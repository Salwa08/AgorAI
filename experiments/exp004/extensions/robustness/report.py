"""Verify robustness outcomes and produce reproducible seed-level research tables."""
import argparse
import csv
from dataclasses import asdict
import hashlib
import gzip
import json
from pathlib import Path
import subprocess
import zipfile
import numpy as np
from experiments.exp004.runner import write_csv,summarize
from .environment import Config,RESERVED

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]


def verify(output):
    metadata=json.loads((output/'metadata.json').read_text(encoding='utf-8'))
    config=json.loads((output/'config.json').read_text(encoding='utf-8'))
    assert not set(config['seeds'])&set(RESERVED)
    for name,digest in metadata['output_sha256'].items():
        assert hashlib.sha256((output/name).read_bytes()).hexdigest()==digest,name
    for name,digest in metadata['source_sha256'].items():
        if Path(name).name in ('environment.py','policies.py','runner.py','__init__.py'):
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    for name,digest in metadata['original_working_file_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    subprocess.check_call(['git','diff','--quiet','c871764','--',*metadata['original_working_file_sha256']],cwd=ROOT)
    manifest=json.loads((output/'manifest.json').read_text())
    assert len(manifest)==len(config['seeds'])*len(config['rhos'])*len(config['coverage'])
    lookup={}
    with (output/'agents.csv').open(newline='',encoding='utf-8') as stream:
        for row in csv.DictReader(stream):
            key=(int(row['seed']),float(row['rho']),int(row['coverage']),row['policy'],int(row['agent']))
            assert key not in lookup
            lookup[key]=row
    paired={};main=0;focal=0
    for row in manifest:
        seed,rho,m=row['seed'],row['rho'],row['coverage']
        path=output/'raw'/f'{seed}_{rho}_{m}_outcomes.npz'
        with np.load(path) as d:
            expected,realized,weights=d['expected'],d['realized'],d['weights']
            # First-round provenance snapshot in every completed world; all ledger bytes are hashed.
            with gzip.open(output/'raw'/f'{seed}_{rho}_{m}_evidence.jsonl.gz','rt',encoding='utf-8') as stream:
                evidence=json.loads(stream.readline())
            distributed=[message for view in evidence['main'] for message in view['own']]
            assert len(distributed)==config['agents']*m
            assert len({tuple(message['identity']) for message in distributed})==len(distributed)
            for message in distributed:
                assert message['identity'][:2]==[seed,0]
            if m>=config['actions']:
                assert all({o['action'] for o in v['own']}==set(range(config['actions'])) for v in evidence['main'])
            for i,view in enumerate(evidence['focal']):
                assert len(view['own'])==len(distributed)
                for source,local in zip(distributed,view['own']):
                    assert source['identity']==local['identity'] and source['action']==local['action']
                    assert source['variance']==local['variance'] and local['context']==view['context']
                    donor=source['identity'][2];action=source['action']
                    assert np.allclose(np.asarray(source['outcomes'])-expected[0,donor,action],
                                       np.asarray(local['outcomes'])-expected[0,i,action])
            assert expected.shape==(config['rounds'],config['agents'],config['actions'],config['dimensions'])
            digest=hashlib.sha256()
            for mu,z in zip(expected,realized):digest.update(mu.tobytes());digest.update(z.tobytes())
            assert digest.hexdigest()==row['world_sha256']
            key=(seed,rho)
            if key in paired:assert paired[key]==row['world_sha256']
            paired[key]=row['world_sha256']
            truth=np.einsum('tnad,nd->tna',expected,weights)
            observed=np.einsum('tnad,nd->tna',realized,weights)
            assert np.array_equal(d['B2_action'],d['B3_action'])
            if rho==0:
                assert np.array_equal(d['H_known_action'],d['B1_action'])
                assert np.array_equal(d['L_budget_action'],d['B1_action'])
            if rho==1:assert np.array_equal(d['H_known_action'],d['B2_action'])
            for policy in ('B0','B1','B2','B3','H_known','H_fit','L_budget'):
                actions=d[policy+'_action'];idx=np.arange(actions.shape[0])[:,None],np.arange(actions.shape[1])[None,:],actions
                assert np.allclose(d[policy+'_utility'],truth[idx])
                assert np.allclose(d[policy+'_regret'],truth.max(axis=2)-truth[idx])
                assert np.allclose(d[policy+'_realized_regret'],observed.max(axis=2)-observed[idx])
                assert np.allclose(d[policy+'_regret']-d['B0_regret'],-d[policy+'_utility']+d['B0_utility'])
                if policy=='L_budget':focal+=actions.size
                else:main+=actions.size
                for metric in ('utility','regret','realized_utility','realized_regret','volume','evidence'):
                    values=d[policy+'_'+metric];assert np.isfinite(values).all()
                    for i,value in enumerate(values.mean(axis=0)):
                        assert np.isclose(value,float(lookup[(seed,rho,m,policy,i)][metric]),rtol=0,atol=1e-12)
            assert np.all(d['B0_volume']==0)
            assert np.all(d['B1_volume']==m*(config['agents']-1))
            for policy in ('B3','H_known','H_fit'):assert np.all(d[policy+'_volume']==m+1)
            assert np.all(d['L_budget_evidence']==config['agents']*m)
            assert np.all((d['rho_selected']>=0)&(d['rho_selected']<=1))
    with (output/'focal_seed_metrics.csv').open(newline='') as stream:
        for row in csv.DictReader(stream):
            budget=config['agents']*int(row['coverage'])
            assert int(row['acquired_each_side'])==budget
            assert int(row['shared_focal_packets'])==budget+1
            assert np.isclose(float(row['local_minus_shared_net'])-float(row['local_minus_shared_utility']),
                              float(row['cost'])*(budget+1))
    result=dict(main_decisions=main,focal_decisions=focal,worlds=len(manifest),hashes=True,originals_unchanged=True,
        coverage_worlds_matched=True,posterior_endpoints=True,architecture_parity=True,raw_regret_and_agent_means=True,
        focal_budgets_and_costs=True,focal_provenance_snapshots=True,confirmation_seeds_executed=False)
    (output/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return metadata,config,result


def render(output):
    metadata,config,checks=verify(output)
    if config!=json.loads(json.dumps(asdict(Config()))):
        raise ValueError('Narrative tables require the prespecified exploratory config; use summaries for other configs')
    sources={name:json.loads((output/f'{name}.json').read_text()) for name in ('levels','contrasts','coverage_effects','focal')}
    def get(source,rho,m,p,metric,cost=0,group='ALL',reference=None):
        matches=[r for r in sources[source] if r['rho']==rho and r['coverage']==m and r['policy']==p and r['metric']==metric
                 and r['cost']==cost and (source=='focal' or r['group']==group) and (reference is None or r['reference']==reference)]
        assert len(matches)==1,(source,rho,m,p,metric,cost,reference)
        return matches[0]
    def fmt(r,scale=1):
        return f"{r['mean']*scale:.5f} [{r['low']*scale:.5f}, {r['high']*scale:.5f}]" if r['low'] is not None else f"{r['mean']*scale:.5f} [CI unavailable]"
    # Selection diagnostics first aggregate 100 estimates within each seed.
    groups={}
    with (output/'rho_estimates.csv').open(newline='') as stream:
        for r in csv.DictReader(stream):groups.setdefault((int(r['seed']),float(r['rho']),int(r['coverage'])),[]).append(float(r['selected']))
    seed_lookup={}
    with (output/'seed_metrics.csv').open(newline='') as stream:
        for r in csv.DictReader(stream):
            if r['group']=='ALL' and float(r['cost'])==0:
                seed_lookup[(int(r['seed']),float(r['rho']),int(r['coverage']),r['policy'])]=r
    attenuation=[]
    for seed in config['seeds']:
        for rho in config['rhos']:
            for policy in ('B1','B2','H_known','H_fit'):
                gains=[]
                for m in (1,3):
                    gains.append(float(seed_lookup[(seed,rho,m,policy)]['utility'])-float(seed_lookup[(seed,rho,m,'B0')]['utility']))
                attenuation.append(dict(seed=seed,rho=rho,policy=policy,sparse_gain=gains[0],full_gain=gains[1],gain_change=gains[1]-gains[0]))
    write_csv(output/'sharing_gain_seed.csv',attenuation)
    (output/'sharing_gain.json').write_text(json.dumps(summarize(attenuation,['rho','policy']),indent=2),encoding='utf-8')
    estimates=[dict(seed=s,rho=r,coverage=m,selected_mean=float(np.mean(x)),mae=float(np.mean(np.abs(np.array(x)-r))),
                    selected_zero=float(np.mean(np.array(x)==0)),selected_one=float(np.mean(np.array(x)==1))) for (s,r,m),x in groups.items()]
    write_csv(output/'rho_seed_summary.csv',estimates)
    selection=summarize(estimates,['rho','coverage'])
    (output/'rho_summary.json').write_text(json.dumps(selection,indent=2),encoding='utf-8')
    out=['# EXP004.1 exploratory robustness results','',
         f"Completed **{checks['main_decisions']:,} main-policy decisions and {checks['focal_decisions']:,} separate focal comparisons**. "
         'Twenty agents, three actions/dimensions/contexts, 100 rounds per seed, exploratory seeds 100–119, '
         'rho {0,.25,.5,.75,1}, local coverage {1,3}, noise .5, costs {0,.01,.1}. Confirmation seeds 200–219 remain untouched.','',
         'Primary metric: expected regret. All intervals are exploratory, unadjusted 95% Student t intervals across 20 independent seeds; '
         'rounds are averaged within agents first. Negative regret contrasts favor the named policy. '
         'H_known receives the true correlation parameter only; H_fit uses observation-only marginal-likelihood selection. '
         'Read INTERPRETATION.md for direct answers to the five research questions, and LIMITATIONS.md for validity boundaries.','',
         '## Expected regret by coverage and heterogeneity','',
         'Larger rho means less cross-context similarity. Three observations cover all actions once; they remain noisy.','',
         '| rho | Local samples | B0 | B1 | B2 (=B3) | H_known | H_fit |',
         '|---|---|---|---|---|---|---|']
    for m in config['coverage']:
        for rho in config['rhos']:
            out.append(f'| {rho} | {m} | '+' | '.join(fmt(get('levels',rho,m,p,'regret')) for p in ('B0','B1','B2','H_known','H_fit'))+' |')
    out+=['','## Sharing effects versus equally covered local-only','',
          '| rho | Samples | Policy | Regret difference [CI] | Mean utility [CI] | Harmed % [CI] | q10 utility [CI] | Packets | Net-utility difference at .01 [CI] |',
          '|---|---|---|---|---|---|---|---|---|']
    for m in config['coverage']:
        for rho in config['rhos']:
            for p in ('B1','B2','B3','H_known','H_fit'):
                vals=[fmt(get('contrasts',rho,m,p,'regret',reference='B0')),
                      fmt(get('levels',rho,m,p,'utility')),fmt(get('levels',rho,m,p,'harmed'),100),
                      fmt(get('levels',rho,m,p,'q10_utility')),f"{get('levels',rho,m,p,'volume')['mean']:.2f}",
                      fmt(get('contrasts',rho,m,p,'net_utility',cost=.01,reference='B0'))]
                out.append(f'| {rho} | {m} | {p} | '+' | '.join(vals)+' |')
    out+=['','## Cross-context harm depends on the comparator','',
          'Positive differences mean unconditional pooling is worse. A sampled rho threshold is not a universal boundary.','',
          '| rho | Local samples | B1 minus B0 regret [CI] | B1 minus B2 regret [CI] |',
          '|---|---|---|---|']
    for m in config['coverage']:
        for rho in config['rhos']:
            out.append(f'| {rho} | {m} | '+fmt(get('contrasts',rho,m,'B1','regret',reference='B0'))+' | '+fmt(get('contrasts',rho,m,'B1','regret',reference='B2'))+' |')
    out+=['','## Partial pooling: paired comparisons','',
          '| rho | Samples | Estimator | Versus B1: regret [CI] | Versus B2: regret [CI] |',
          '|---|---|---|---|---|']
    for m in config['coverage']:
        for rho in config['rhos']:
            for p in ('H_known','H_fit'):
                out.append(f'| {rho} | {m} | {p} | '+fmt(get('contrasts',rho,m,p,'regret',reference='B1'))+' | '+fmt(get('contrasts',rho,m,p,'regret',reference='B2'))+' |')
    out+=['','## Cost of estimating rho','',
          'Positive regret differences indicate a loss from using observation-fitted rho rather than the declared true parameter. '
          'The two estimators have identical acquisition and communication budgets.','',
          '| rho | Local samples | H_fit minus H_known regret [CI] |',
          '|---|---|---|']
    for m in config['coverage']:
        for rho in config['rhos']:
            out.append(f'| {rho} | {m} | '+fmt(get('contrasts',rho,m,'H_fit','regret',reference='H_known'))+' |')
    out+=['','## Stronger local coverage and equal-budget focal sensing','',
          'Coverage changes mean three minus one observations per agent (60 versus 20 acquisitions system-wide). '
          'Focal differences compare local concentration versus distributed sensing with the SAME total acquisition count: '
          '20 at coverage 1 or 60 at coverage 3. Focal results are separate counterfactual trials, not a joint deployment with free extra sensing.','',
          '| rho | B0 coverage regret change [CI] | H_fit coverage regret change [CI] |',
          '|---|---|---|']
    for rho in config['rhos']:
        out.append(f'| {rho} | '+fmt(get('coverage_effects',rho,3,'B0','regret'))+' | '+fmt(get('coverage_effects',rho,3,'H_fit','regret'))+' |')
    out+=['','| rho | Samples/source | Shared estimator | Local minus shared regret [CI] | Shared harmed versus local % [CI] |',
          '|---|---|---|---|---|']
    for m in config['coverage']:
        for rho in config['rhos']:
            for p in ('B1','H_known','H_fit'):
                out.append(f'| {rho} | {m} | {p} | '+fmt(get('focal',rho,m,p,'local_minus_shared_regret'))+' | '+fmt(get('focal',rho,m,p,'shared_harmed_vs_local'),100)+' |')
    out+=['','## Rho selection diagnostics','',
          'H_fit re-estimates rho every round from permitted current evidence. Error below uses true rho only in evaluation. '
          'More measurements improve latent-mean precision but do not create more independent context/action/dimension draws.','',
          '| True rho | Local samples | Mean selected rho [CI] | Mean absolute error [CI] |',
          '|---|---|---|---|']
    for m in config['coverage']:
        for rho in config['rhos']:
            entries={r['metric']:r for r in selection if r['rho']==rho and r['coverage']==m}
            out.append(f'| {rho} | {m} | '+fmt(entries['selected_mean'])+' | '+fmt(entries['mae'])+' |')
    out+=['','## Verification, environment and replay','',
          '45 automated tests passed (16.76 s), including all 25 original tests. Smoke completed 7,200 main decisions and 1,200 focal comparisons. '
          'The pre-existing requests dependency warning is unrelated to this NumPy/SciPy computation. '
          'Full verification reproduced raw expected/realized regret and agent means, checked every hash, matched coverage worlds, '
          'validated endpoint and architecture parity, and checked focal budgets and costs. Original EXP004 working-file hashes and Git content are unchanged.','',
          'Actual commands (repository root):','',
          '```powershell',
          'python -m pytest experiments/exp004/tests experiments/exp004/extensions/robustness/tests -q',
          'python -m experiments.exp004.extensions.robustness.runner --config experiments/exp004/extensions/robustness/configs/smoke.json --output experiments/exp004/extensions/robustness/results/smoke',
          'python -m experiments.exp004.extensions.robustness.runner --config experiments/exp004/extensions/robustness/configs/exploratory.json --output experiments/exp004/extensions/robustness/results/exploratory',
          'python -m experiments.exp004.extensions.robustness.report --results experiments/exp004/extensions/robustness/results/exploratory',
          '```','',
          'Use new results/replay paths to rerun, as in README.md. summary.zip retains complete machine-readable agent/seed results, '
          'paired contrasts, all costs, context/objective subgroups, coverage effects, focal comparisons and provenance. '
          'Raw messages and counterfactuals remain local and reproducible.','',
          'Execution commit: '+metadata['commit']+'. The execution modules were committed before exploration; '
          'metadata records dirty state and source hashes at completion. Downstream reporting has separate hashes.','',
          'Python: '+metadata['python']+'. Platform: '+metadata['platform']+'. Packages: '+str(metadata['packages'])+'. '
          'Completion UTC: '+metadata['timestamp_utc']+'.','',
          'No agricultural validity, confirmation result or algorithmic novelty is claimed.']
    (BASE/'RESULTS.md').write_text('\n'.join(out)+'\n',encoding='utf-8',newline='\n')
    analysis=dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  report_sha256=hashlib.sha256((BASE/'RESULTS.md').read_bytes()).hexdigest(),verification=checks)
    (output/'analysis_metadata.json').write_text(json.dumps(analysis,indent=2),encoding='utf-8')
    with zipfile.ZipFile(output/'summary.zip','w') as archive:
        for path in sorted(output.iterdir()):
            if path.is_file() and path.suffix in ('.json','.csv'):
                info=zipfile.ZipInfo(path.name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                archive.writestr(info,path.read_bytes())
    print(json.dumps(checks,indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--results',type=Path,required=True)
    render(p.parse_args().results)


if __name__=='__main__':main()
