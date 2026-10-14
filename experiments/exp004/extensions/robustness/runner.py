"""Reproducible robustness panel; focal budget trials are labeled separately."""
import argparse
from dataclasses import asdict
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime,timezone
import numpy as np
import scipy
from experiments.exp004.evaluation import evaluate,metrics
from experiments.exp004.runner import write_csv,summarize
from .environment import Config,RESERVED,population,generate
from .policies import POLICIES,decide_panel

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]


def run_world(cfg,seed,rho,m,output=None):
    pop=population(cfg,seed);collected={p:defaultdict(list) for p in POLICIES}
    means=[];realized=[];selected=[];digest=hashlib.sha256()
    ledger=gzip.open(output/f'{seed}_{rho}_{m}_evidence.jsonl.gz','wt',encoding='utf-8') if output else None
    try:
        for t in range(cfg.rounds):
            world=generate(cfg,seed,t,rho,m,pop)
            digest.update(world.expected.tobytes());digest.update(world.realized.tobytes())
            result=decide_panel(world.views,world.focal,cfg.contexts,cfg.actions,rho)
            if ledger:
                ledger.write(json.dumps(dict(main=[asdict(v) for v in world.views],
                    focal=[asdict(v) for v in world.focal]))+'\n')
                means.append(world.expected);realized.append(world.realized)
            selected.append(result.rho_selected)
            for policy in POLICIES:
                values=evaluate(world.expected,world.realized,pop.weights,result.actions[policy])
                values.update(action=result.actions[policy],volume=result.volumes[policy],
                              evidence=result.evidence_counts[policy])
                for key,value in values.items():collected[policy][key].append(value)
            assert np.array_equal(result.actions['B2'],result.actions['B3'])
    finally:
        if ledger:ledger.close()
    arrays={p:{k:np.asarray(v) for k,v in fields.items()} for p,fields in collected.items()}
    if output:
        np.savez_compressed(output/f'{seed}_{rho}_{m}_outcomes.npz',expected=means,realized=realized,
            weights=pop.weights,contexts=pop.contexts,rho_selected=selected,
            **{p+'_'+k:v for p,fields in arrays.items() for k,v in fields.items()})
    return pop,arrays,np.array(selected),digest.hexdigest()


def execute(cfg,output):
    output.mkdir(parents=True,exist_ok=False);raw=output/'raw';raw.mkdir()
    rows=[];agents=[];manifest=[];rho_estimates=[];focal_rows=[]
    for seed in cfg.seeds:
        for rho in cfg.rhos:
            paired_hash=None
            for m in cfg.coverage:
                pop,arrays,selected,digest=run_world(cfg,seed,rho,m,raw)
                if paired_hash is not None:assert paired_hash==digest
                paired_hash=digest
                averages={p:{k:v.mean(axis=0) for k,v in fields.items() if k!='action'} for p,fields in arrays.items()}
                groups={'ALL':np.ones(cfg.agents,dtype=bool)}
                groups.update({f'context_{c}':pop.contexts==c for c in range(cfg.contexts)})
                groups.update({f'objective_{d}':pop.weights.argmax(axis=1)==d for d in range(cfg.dimensions)})
                for p in POLICIES:
                    averages[p]['round_harmed']=(arrays[p]['utility']<arrays['B0']['utility']-1e-12).mean(axis=0)
                    for i in range(cfg.agents):
                        agents.append(dict(seed=seed,rho=rho,coverage=m,policy=p,agent=i,context=int(pop.contexts[i]),
                            objective=int(pop.weights[i].argmax()),**{k:float(v[i]) for k,v in averages[p].items()}))
                    # L_budget is deliberately excluded from jointly feasible net-utility tables.
                    if p=='L_budget':continue
                    for cost in cfg.costs:
                        for group,mask in groups.items():
                            if mask.any():rows.append(dict(seed=seed,rho=rho,coverage=m,policy=p,cost=cost,group=group,
                                **metrics(averages[p],averages['B0'],mask,cost)))
                for p in ('B1','H_known','H_fit'):
                    for cost in cfg.costs:
                        # One service recipient: N*m observations + one reply (including B1 estimator).
                        shared=averages[p]['utility'];local=averages['L_budget']['utility']
                        focal_rows.append(dict(seed=seed,rho=rho,coverage=m,policy=p,cost=cost,
                            acquired_each_side=cfg.agents*m,shared_focal_packets=cfg.agents*m+1,
                            local_regret=float(averages['L_budget']['regret'].mean()),
                            shared_regret=float(averages[p]['regret'].mean()),
                            local_minus_shared_regret=float((averages['L_budget']['regret']-averages[p]['regret']).mean()),
                            local_minus_shared_utility=float((local-shared).mean()),
                            local_minus_shared_net=float((local-shared).mean()+cost*(cfg.agents*m+1)),
                            shared_harmed_vs_local=float((shared<local-1e-12).mean())))
                for t,estimate in enumerate(selected):rho_estimates.append(dict(seed=seed,rho=rho,coverage=m,round=t,
                    selected=float(estimate),absolute_error=float(abs(estimate-rho))))
                manifest.append(dict(seed=seed,rho=rho,coverage=m,world_sha256=digest,
                    main_decisions=cfg.rounds*cfg.agents*6,focal_decisions=cfg.rounds*cfg.agents,
                    main_total_acquired_per_round=cfg.agents*m,focal_total_acquired_per_trial=cfg.agents*m))
        print(f'Completed exploratory seed {seed}',flush=True)
    keys=['rho','coverage','policy','cost','group']
    lookup={tuple(r[k] for k in ['seed',*keys]):r for r in rows}
    paired=[]
    for r in rows:
        refs=[] if r['policy']=='B0' else ['B0']
        if r['policy'] in ('H_known','H_fit'):refs+=['B1','B2']
        if r['policy']=='H_fit':refs+=['H_known']
        if r['policy']=='B3':refs+=['B2']
        if r['policy']=='B1':refs+=['B2']
        for ref in refs:
            key=(r['seed'],r['rho'],r['coverage'],ref,r['cost'],r['group'])
            base=lookup[key]
            paired.append(dict(seed=r['seed'],**{k:r[k] for k in keys},reference=ref,
                               **{k:r[k]-base[k] for k in r if k not in ['seed',*keys]}))
    coverage_rows=[]
    if 1 in cfg.coverage:
        for r in rows:
            if r['coverage']==1:continue
            b=lookup[(r['seed'],r['rho'],1,r['policy'],r['cost'],r['group'])]
            coverage_rows.append(dict(seed=r['seed'],**{k:r[k] for k in keys},
                **{k:r[k]-b[k] for k in r if k not in ['seed',*keys]}))
    tables={'agents':agents,'seed_metrics':rows,'paired_seed_metrics':paired,'focal_seed_metrics':focal_rows,
            'rho_estimates':rho_estimates}
    if coverage_rows:tables['coverage_seed_metrics']=coverage_rows
    for name,data in tables.items():write_csv(output/f'{name}.csv',data)
    summaries={'levels':summarize(rows,keys),'contrasts':summarize(paired,keys+['reference']),
               'focal':summarize(focal_rows,['rho','coverage','policy','cost']),
               'config':asdict(cfg),'manifest':manifest,
               'confirmation':dict(status='RESERVED_NOT_EXECUTED',seeds=RESERVED)}
    if coverage_rows:summaries['coverage_effects']=summarize(coverage_rows,keys)
    for name,data in summaries.items():(output/f'{name}.json').write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf-8')
    def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    originals=git('ls-tree','-r','--name-only','c871764','experiments/exp004').splitlines()
    original_hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in originals}
    subprocess.check_call(['git','diff','--quiet','c871764','--',*originals],cwd=ROOT)
    metadata=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),python=sys.version,platform=platform.platform(),
        packages=dict(numpy=np.__version__,scipy=scipy.__version__),command=sys.argv,commit=git('rev-parse','HEAD'),
        git_status=git('status','--short'),original_working_file_sha256=original_hashes,
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(BASE.glob('*.py'))},
        output_sha256={p.relative_to(output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.rglob('*')) if p.is_file()})
    (output/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print('Completed main decisions:',sum(m['main_decisions'] for m in manifest),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();execute(Config(**json.loads(args.config.read_text(encoding='utf-8-sig'))),args.output)


if __name__=='__main__':main()
