"""Run matched independent rounds, save evidence and aggregate by seed."""
import argparse
import csv
from dataclasses import asdict
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone
import numpy as np
import scipy
from .environment import Config, population, generate
from .policies import View, decide, central_decisions, payload_volume
from .evaluation import evaluate, metrics, interval

POLICIES = ('B0','B1','B2','B3')
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def run_world(config, seed, scenario, noise, output=None):
    pop = population(config, seed)
    collected = {p: defaultdict(list) for p in POLICIES}
    digest = hashlib.sha256()
    latent, realized = [], []
    ledger = gzip.open(output / f'{seed}_{scenario}_{noise}_messages.jsonl.gz','wt',encoding='utf-8') if output else None
    try:
        for round_index in range(config.rounds):
            world = generate(config, seed, round_index, scenario, noise, pop)
            digest.update(world.expected.tobytes()); digest.update(world.realized.tobytes())
            digest.update(pop.weights.tobytes()); digest.update(pop.contexts.tobytes())
            views = world.views
            if ledger:
                ledger.write(json.dumps([asdict(v) for v in views])+'\n')
                latent.append(world.expected); realized.append(world.realized)
            central = central_decisions(views, config.actions)
            for policy in POLICIES:
                decisions = []
                for i, view in enumerate(views):
                    # B0 receives no peer objects. Filtering is source-side for B2.
                    peers = () if policy == 'B0' else tuple(m for j, source in enumerate(views) if i != j
                        for m in source.own if policy != 'B2' or m.context in (view.context, -1))
                    decisions.append(central[i] if policy == 'B3' else decide(
                        View(view.seed, view.round, view.context, view.weights, view.own, peers), policy, config.actions))
                actions = np.array([d.action for d in decisions])
                values = evaluate(world.expected, world.realized, pop.weights, actions)
                values.update(volume=payload_volume(policy, views),
                              uncertainty=np.array([np.dot(pop.weights[i]**2,d.variances[d.action]*np.ones(config.dimensions))
                                                    for i,d in enumerate(decisions)]),
                              unique_evidence=np.array([len(d.used) for d in decisions]), action=actions)
                for name, value in values.items(): collected[policy][name].append(value)
            assert np.array_equal(collected['B2']['action'][-1],collected['B3']['action'][-1])
    finally:
        if ledger: ledger.close()
    arrays = {p:{k:np.asarray(v) for k,v in data.items()} for p,data in collected.items()}
    if scenario == 'S0':
        assert all(np.array_equal(arrays[p]['action'],arrays['B0']['action']) for p in POLICIES)
    if output:
        np.savez_compressed(output/f'{seed}_{scenario}_{noise}_counterfactuals.npz',
            expected=np.asarray(latent), realized=np.asarray(realized), weights=pop.weights, contexts=pop.contexts,
            **{p+'_'+k:v for p,data in arrays.items() for k,v in data.items()})
    return pop, arrays, digest.hexdigest()


def write_csv(path, rows):
    with path.open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def summarize(rows, keys):
    groups=defaultdict(list)
    for row in rows: groups[tuple(row[k] for k in keys)].append(row)
    result=[]
    for key, group in groups.items():
        for metric in group[0]:
            if metric not in keys+['seed']:
                result.append(dict(zip(keys,key),metric=metric,**interval([r[metric] for r in group])))
    return result


def execute(config: Config, output: Path):
    output.mkdir(parents=True,exist_ok=False); raw=output/'raw';raw.mkdir()
    rows=[]; agent_rows=[]; manifest=[]
    for seed in config.seeds:
        for scenario in config.scenarios:
            for noise in config.noise:
                pop, arrays, world_hash=run_world(config,seed,scenario,noise,raw)
                means={p:{k:v.mean(axis=0) for k,v in data.items() if k!='action'} for p,data in arrays.items()}
                groups={'ALL':np.ones(config.agents,dtype=bool)}
                groups.update({f'context_{c}':pop.contexts==c for c in range(config.contexts)})
                groups.update({f'objective_{d}':pop.weights.argmax(axis=1)==d for d in range(config.dimensions)})
                for policy in POLICIES:
                    means[policy]['round_harmed']=(arrays[policy]['utility'] < arrays['B0']['utility']-1e-12).mean(axis=0)
                    for i in range(config.agents):
                        agent_rows.append(dict(seed=seed,scenario=scenario,noise=noise,policy=policy,agent=i,
                            context=int(pop.contexts[i]),objective=int(pop.weights[i].argmax()),
                            **{f'w_{d}':float(pop.weights[i,d]) for d in range(config.dimensions)},
                            **{k:float(v[i]) for k,v in means[policy].items()}))
                    for cost in config.costs:
                        for group, selected in groups.items():
                            if selected.any():
                                rows.append(dict(seed=seed,scenario=scenario,noise=noise,policy=policy,cost=cost,group=group,
                                    **metrics(means[policy],means['B0'],selected,cost)))
                manifest.append(dict(seed=seed,scenario=scenario,noise=noise,world_sha256=world_hash,
                                     policies=list(POLICIES),decisions=config.agents*config.rounds*len(POLICIES)))
        print(f'Completed seed {seed}',flush=True)
    write_csv(output/'agents.csv',agent_rows);write_csv(output/'seed_metrics.csv',rows)
    keys=['scenario','noise','policy','cost','group']
    levels=summarize(rows,keys)
    lookup={(r['seed'],r['scenario'],r['noise'],r['cost'],r['group'],r['policy']):r for r in rows}
    paired=[]
    for row in rows:
        references=['B0'] if row['policy']!='B0' else []
        if row['policy']=='B2':references.append('B1')
        if row['policy']=='B3':references.append('B2')
        for ref in references:
            base=lookup[tuple(row[k] for k in ['seed','scenario','noise','cost','group'])+(ref,)]
            paired.append(dict(seed=row['seed'],**{k:row[k] for k in keys},reference=ref,
                **{k:row[k]-base[k] for k in row if k not in keys+['seed']}))
    contrasts=summarize(paired,keys+['reference'])
    write_csv(output/'paired_seed_metrics.csv',paired)
    for name,data in [('levels',levels),('contrasts',contrasts),('manifest',manifest),('config',asdict(config))]:
        (output/f'{name}.json').write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf-8')
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    metadata=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),python=sys.version,platform=platform.platform(),
                  packages=dict(numpy=np.__version__,scipy=scipy.__version__),commit=git('rev-parse','HEAD'),
                  git_status=git('status','--short'),command=sys.argv,
                  source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(BASE.glob('*.py'))},
                  output_sha256={p.relative_to(output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(output.rglob('*')) if p.is_file()})
    (output/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print(f'Completed {sum(m["decisions"] for m in manifest):,} matched policy decisions',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    execute(Config(**json.loads(args.config.read_text(encoding='utf-8-sig'))),args.output)


if __name__=='__main__':main()
