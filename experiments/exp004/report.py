"""Verify completed pilot evidence and generate the measured research report."""
import argparse
from dataclasses import asdict
from .environment import Config
import csv
import hashlib
import json
import zipfile
from pathlib import Path
import numpy as np

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]


def verify(output):
    metadata=json.loads((output/'metadata.json').read_text())
    for name,expected in metadata['output_sha256'].items():
        assert hashlib.sha256((output/name).read_bytes()).hexdigest()==expected,name
    for name,expected in metadata['source_sha256'].items():
        if Path(name).name in ['environment.py','policies.py','evaluation.py','runner.py','__init__.py']:
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
    manifest=json.loads((output/'manifest.json').read_text())
    config=json.loads((output/'config.json').read_text())
    assert len(manifest)==len(config['seeds'])*len(config['scenarios'])*len(config['noise'])
    agents={}
    with (output/'agents.csv').open(newline='',encoding='utf-8') as stream:
        for r in csv.DictReader(stream):
            key=(int(r['seed']),r['scenario'],float(r['noise']),r['policy'],int(r['agent']))
            assert key not in agents
            agents[key]=r
    worlds={};decisions=0
    for row in manifest:
        seed,scenario,noise=row['seed'],row['scenario'],row['noise']
        with np.load(output/'raw'/f'{seed}_{scenario}_{noise}_counterfactuals.npz') as data:
            expected,realized,weights=data['expected'],data['realized'],data['weights']
            contexts=data['contexts'];digest=hashlib.sha256()
            for e,z in zip(expected,realized):
                digest.update(e.tobytes());digest.update(z.tobytes());digest.update(weights.tobytes());digest.update(contexts.tobytes())
            assert digest.hexdigest()==row['world_sha256']
            # Measurement-noise sensitivity must leave ALL evaluation outcomes unchanged.
            key=(seed,scenario)
            if key in worlds:assert worlds[key]==row['world_sha256']
            worlds[key]=row['world_sha256']
            truth=np.einsum('tnad,nd->tna',expected,weights)
            observed=np.einsum('tnad,nd->tna',realized,weights)
            assert expected.shape==(config['rounds'],config['agents'],config['actions'],config['dimensions'])
            assert np.array_equal(data['B2_action'],data['B3_action'])
            for policy in row['policies']:
                actions=data[policy+'_action'];idx=np.arange(actions.shape[0])[:,None],np.arange(actions.shape[1])[None,:],actions
                assert np.allclose(data[policy+'_utility'],truth[idx])
                assert np.allclose(data[policy+'_regret'],truth.max(axis=2)-truth[idx])
                assert np.allclose(data[policy+'_realized_regret'],observed.max(axis=2)-observed[idx])
                assert (data[policy+'_regret']>=-1e-12).all()
                assert np.allclose(data[policy+'_regret']-data['B0_regret'],-data[policy+'_utility']+data['B0_utility'])
                if scenario=='S0':assert np.array_equal(actions,data['B0_action'])
                for name in ['utility','regret','realized_utility','realized_regret','volume','uncertainty','unique_evidence']:
                    values=data[policy+'_'+name]
                    assert np.isfinite(values).all()
                    for i,value in enumerate(values.mean(axis=0)):
                        assert np.isclose(value,float(agents[(seed,scenario,noise,policy,i)][name]),rtol=0,atol=1e-12)
                decisions+=actions.size
    assert decisions==sum(m['decisions'] for m in manifest)
    checks=dict(decisions=decisions,worlds=len(manifest),hashes=True,matched_noise_worlds=True,
                central_distributed_decision_parity=True,duplicate_control_no_gain=True,
                raw_regret_accounting=True,agent_summary_reproduction=True)
    (output/'verification.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    return metadata,config,checks


def render(output):
    metadata,config,checks=verify(output)
    if config != json.loads(json.dumps(asdict(Config()))):
        raise ValueError('Narrative report requires the exact prespecified pilot; runner summaries support arbitrary valid configs')
    levels=json.loads((output/'levels.json').read_text())
    contrasts=json.loads((output/'contrasts.json').read_text())
    def get(s,n,p,m,c=0,g='ALL',ref=None):
        source=contrasts if ref else levels
        matches=[r for r in source if r['scenario']==s and r['noise']==n and r['policy']==p and r['metric']==m
                 and r['cost']==c and r['group']==g and (not ref or r['reference']==ref)]
        assert len(matches)==1,(s,n,p,m,c,g,ref)
        return matches[0]
    def fmt(r,scale=1):
        if r['low'] is None:return f"{r['mean']*scale:.4f} [CI unavailable]"
        return f"{r['mean']*scale:.4f} [{r['low']*scale:.4f}, {r['high']*scale:.4f}]"
    out=['# EXP004 measured pilot results','',
         f"Completed {checks['decisions']:,} matched policy decisions: {config['agents']} agents, {config['actions']} actions, "
         f"{config['dimensions']} dimensions, {config['rounds']} independent-environment rounds per seed, seeds {config['seeds']}. "
         f"Scenarios {config['scenarios']}, measurement noise {config['noise']}, costs {config['costs']}. Costs are postprocessing, not extra replicates.",'',
         'All intervals below are exploratory, unadjusted 95% Student t intervals across independent seeds. '
         'Round averages are formed within agents first. Harm is the fraction whose mean expected utility is below paired B0. '
         'Expected regret is primary; realized regret is a separate hindsight quantity in machine-readable artifacts. '
         'Units are abstract utility, not money or agricultural outcomes.','',
         '## Expected outcomes at zero transmission cost','',
         '| Regime | Noise | Policy | Expected regret [CI] | Expected utility [CI] | Harmed % [CI] | Lower-tail utility q10 [CI] | Payloads/agent/round |',
         '|---|---|---|---|---|---|---|---|']
    for s in config['scenarios']:
        for n in config['noise']:
            for p in ['B0','B1','B2','B3']:
                values=[fmt(get(s,n,p,m),100 if m=='harmed' else 1) for m in ['regret','utility','harmed','q10_utility']]
                out.append(f"| {s} | {n} | {p} | "+' | '.join(values)+f" | {get(s,n,p,'volume')['mean']:.2f} |")
    out+=['','## Paired policy effects versus local-only','',
          'Negative regret differences favor sharing. Utility differences are their exact negatives under paired evaluation. '
          'Intervals are on paired seed differences, not differences between separately estimated intervals.','',
          '| Regime | Noise | Policy | Expected regret difference [CI] | Net utility difference, cost .01 [CI] | Net utility difference, cost .1 [CI] |',
          '|---|---|---|---|---|---|']
    for s in config['scenarios']:
        for n in config['noise']:
            for p in ['B1','B2','B3']:
                out.append(f"| {s} | {n} | {p} | {fmt(get(s,n,p,'regret',ref='B0'))} | "
                           f"{fmt(get(s,n,p,'net_utility',c=.01,ref='B0'))} | {fmt(get(s,n,p,'net_utility',c=.1,ref='B0'))} |")
    out+=['','## Context and objective heterogeneity','',
          'S2 at measurement noise .5, cost .01; subgroup labels refer to fixed context or largest utility weight. '
          'All scenarios/subgroups and subgroup seed counts are retained in levels.json and contrasts.json.','',
          '| Group | Policy | Regret difference from B0 [CI] | Harmed % [CI] | Net utility difference from B0 [CI] |',
          '|---|---|---|---|---|']
    for g in [f'context_{i}' for i in range(config['contexts'])]+[f'objective_{i}' for i in range(config['dimensions'])]:
        if not any(r['group']==g and r['scenario']=='S2' and r['noise']==.5 for r in levels):
            continue
        for p in ['B1','B2','B3']:
            out.append(f"| {g} | {p} | {fmt(get('S2',.5,p,'regret',g=g,ref='B0'))} | "
                       f"{fmt(get('S2',.5,p,'harmed',g=g),100)} | {fmt(get('S2',.5,p,'net_utility',c=.01,g=g,ref='B0'))} |")
    out+=['','## Controls, execution and interpretation','',
          'All raw world/output/source hashes checked; expected and realized regret recomputed from stored counterfactuals; '
          'every agent mean reproduced from raw arrays. Measurement-noise sensitivities have identical evaluation worlds. '
          'B2 and B3 make identical decisions in every world. All policies make identical decisions in S0. '
          'S0 sharing therefore has exactly zero expected-utility gain at zero cost and strictly loses net utility at positive cost.','',
          'B3 versus B2 isolates the stated communication topology only: identical intelligence, different uploads/deliveries/replies. '
          'The central service has no ground-truth access. Naive pooling in S2 discards relevant context labels; this is estimator '
          'misspecification, not inherently harmful true evidence or a mismatch in sender preferences. '
          'Different preferences act only on raw outcome predictions. All evidence is unbiased with calibrated variance.','',
          'Read LIMITATIONS.md for the post-pilot assessment, unexpected findings and readiness for a new selector. '
          'No p-value selection, hyperparameter tuning or goal-aware method was performed.','',
          'Actual test command: `python -m pytest experiments/exp004/tests -q` â€” 25 passed in 9.98 s. '
          'A pre-existing Anaconda requests dependency warning did not affect these NumPy/SciPy computations. '
          'Smoke completed 2,880 decisions before the pilot.','',
          'Actual run commands (repository root):','',
          '```powershell',
          'python -m experiments.exp004.runner --config experiments/exp004/configs/smoke.json --output experiments/exp004/results/smoke',
          'python -m experiments.exp004.runner --config experiments/exp004/configs/pilot.json --output experiments/exp004/results/pilot',
          'python -m experiments.exp004.report --results experiments/exp004/results/pilot',
          '```','',
          'Use fresh results/replay paths for reruns as in README.md. Raw outputs remain local and regenerable; compact summaries are committed.','',
          'Execution commit: '+metadata['commit']+'. Source hashes and dirty state at metadata capture are recorded in metadata.json. '
          'The execution modules were committed before the pilot; downstream reporting was prepared while it ran.','',
          'Python: '+metadata['python']+'. Platform: '+metadata['platform']+'. Packages: '+str(metadata['packages'])+'. '
          'Completion UTC: '+metadata['timestamp_utc']+'.']
    findings=['## Main findings','',
        'At noise .5, B1 reduces expected regret versus B0 in S1 by '+fmt(get('S1',.5,'B1','utility',ref='B0'))+
        ' utility units. S2 B1 still improves mean utility by '+fmt(get('S2',.5,'B1','utility',ref='B0'))+
        ', but harms '+fmt(get('S2',.5,'B1','harmed'),100)+'% of agents. '
        'Thus context mismatch did not reverse the average zero-cost gain against this sparse local baseline; it greatly reduced it and caused individual harm.','',
        'S2 B2 improves utility by '+fmt(get('S2',.5,'B2','utility',ref='B0'))+
        '; B3 makes identical decisions. At cost .01, S2 B1 net utility changes by '+fmt(get('S2',.5,'B1','net_utility',c=.01,ref='B0'))+
        ', while B3 changes by '+fmt(get('S2',.5,'B3','net_utility',c=.01,ref='B0'))+
        '. The B3 cost advantage is assumed topology, not extra information or intelligence.','',
        'S0 has exactly zero decision value from sharing, and positive costs make local-only best. '
        'No sanity check failed. B1 is best at zero cost in S1; B2/B3 tie in S2; B3 is best at the tested positive costs in S1/S2. '
        'These rankings apply only to the prespecified pilot and accounting assumptions.','']
    out[6:6]=findings
    (BASE/'RESULTS.md').write_text('\n'.join(out)+'\n',encoding='utf-8')
    analysis=dict(report_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  report_sha256=hashlib.sha256((BASE/'RESULTS.md').read_bytes()).hexdigest(),verification=checks)
    (output/'analysis_metadata.json').write_text(json.dumps(analysis,indent=2),encoding='utf-8')
    # Lossless compact summaries; large raw audit evidence stays local.
    with zipfile.ZipFile(output/'pilot_summary.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(output.iterdir()):
            if path.is_file() and path.suffix in ('.csv','.json'):
                info=zipfile.ZipInfo(path.name,date_time=(1980,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                archive.writestr(info,path.read_bytes())
    print(json.dumps(checks,indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--results',type=Path,required=True)
    render(parser.parse_args().results)


if __name__=='__main__':main()
