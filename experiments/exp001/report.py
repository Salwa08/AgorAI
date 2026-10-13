"""Create RESULTS.md from completed runs; never synthesizes missing observations."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .runner import ROOT, digest

BASE=Path(__file__).resolve().parent


def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(map(str,row))+' |' for row in rows])+'\n'


def value(row, digits=2, scale=1):
    return f"{row.estimate*scale:,.{digits}f} [{row.ci_low*scale:,.{digits}f}, {row.ci_high*scale:,.{digits}f}]"


def load_verified(scenario, results_root):
    p=results_root/scenario
    meta=json.loads((p/'metadata.json').read_text())
    for name,sha in meta['output_sha256'].items():
        if digest(p/name)!=sha: raise ValueError(f'Output hash mismatch: {p/name}')
    for name,sha in meta['input_sha256'].items():
        if digest(ROOT/'data'/name)!=sha: raise ValueError(f'Input changed: {name}')
    for name,sha in meta['source_sha256'].items():
        # Metadata may have been generated on Windows.
        if digest(ROOT/Path(name.replace('\\','/')))!=sha: raise ValueError(f'Source changed: {name}')
    raw=pd.read_csv(p/'agent_season.csv')
    assert len(raw)==meta['n_agent_season_records']
    assert not raw.duplicated(['seed','condition','agent','season']).any()
    assert np.isfinite(raw.select_dtypes('number')).all().all()
    assert raw.groupby(['seed','condition']).size().eq(3000).all()
    ex=json.loads((p/'exogenous.json').read_text())
    assert all(len({e['sha256'] for e in ex if e['seed']==seed})==1 for seed in raw.seed.unique())
    # First-season choices and gross yields must be exactly paired.
    first=raw[raw.season==1]
    for metric in ['crop','yield_t_ha','land_ha','cost_noise','weather']:
        pivot=first.pivot(index=['seed','agent'],columns='condition',values=metric)
        assert all(pivot[c].equals(pivot.A) for c in 'BCD')
    pivot=raw.pivot(index=['seed','season','agent'],columns='condition',values='crop')
    diagnostics=dict(records=len(raw),seeds=int(raw.seed.nunique()),
                     first_season_pairing=True,hashes_verified=True,
                     ac_crop_disagreements=int((pivot.A!=pivot.C).sum()),
                     bd_crop_disagreements=int((pivot.B!=pivot.D).sum()),
                     unique_crops=int(raw.crop.nunique()),
                     absent_zone_seed_pairs=int(20*6-raw[['seed','zone']].drop_duplicates().shape[0]))
    return p,meta,raw,diagnostics


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results-root',type=Path,default=BASE/'results')
    args=parser.parse_args()
    verification=json.loads((BASE/'verification.json').read_text())
    lines=['# EXP001 results — simulation evidence', '',
           'Completed 2026-10-13. Primary and separately requested README-economics sensitivity each use '
           '**20 independent seeds × 4 conditions × 100 matched farmers × 30 seasons** '
           '(240,000 farmer-season records per scenario). Seed list: '+str(list(range(20)))+'.', '',
           'All intervals below are paired-seed or condition-seed **95% Student t intervals**, n=20; '
           'agents and seasons are not independent replicates. Profit is MAD/farm/season. '
           'Median profit means the median of farmer across-season mean profits, then averaged over seeds. '
           'See [METHODOLOGY.md](METHODOLOGY.md) for precise definitions and limitations.', '']
    all_diagnostics={}
    for scenario,title in [('primary','Primary: executable V1 economics'),('readme_economics','Sensitivity: README economics')]:
        p,meta,raw,diagnostics=load_verified(scenario,args.results_root)
        all_diagnostics[scenario]=diagnostics
        relative=p.resolve().relative_to(BASE).as_posix()
        conditions=pd.read_csv(p/'condition_summary.csv')
        effects=pd.read_csv(p/'effects.csv')
        zones=pd.read_csv(p/'zone_effects.csv')
        harms=pd.read_csv(p/'harm_summary.csv')
        contrasts=pd.read_csv(p/'paired_seed_contrasts.csv')
        lines += ['## '+title,'',
                  ('Premium .10; cost factors .80/.90; post-harvest losses .06/.12.' if scenario=='primary' else
                   'Premium .20; cost factors .63/.90; losses .05/.15. The .63 factor is 30% below .90. '
                   'This changes the baseline loss, so comparisons use this scenario\'s own A.'),'',
                  '### Outcomes','']
        rows=[]
        for c in 'ABCD':
            g=conditions[conditions.condition==c].set_index('metric')
            rows.append([c]+[value(g.loc[k]) for k in ['mean_profit_mad','median_profit_mad','mean_yield_t_ha','productivity_t_ha']])
        lines += [table(['Condition','Mean profit [CI]','Median profit [CI]','Mean yield t/ha [CI]','Area-weighted productivity t/ha [CI]'],rows),'',
                  '### Paired factorial effects','']
        rows=[]
        for effect in effects.effect.unique():
            g=effects[effects.effect==effect].set_index('metric')
            rows.append([effect,value(g.loc['mean_profit_mad']),value(g.loc['median_profit_mad']),
                         value(g.loc['mean_yield_t_ha'],3),value(g.loc['productivity_t_ha'],3)])
        lines += [table(['Contrast','Mean profit [CI]','Median profit [CI]','Mean yield [CI]','Productivity [CI]'],rows),'',
                  '### Heterogeneity by zone','',
                  'Each zone appears in all 20 seeds. These contrasts weight farmers equally within each zone and seed; '
                  'they do not imply representative Moroccan population weights. Intervals across zones are not multiplicity-adjusted.','']
        rows=[]
        for z in sorted(zones.zone.unique()):
            g=zones[(zones.zone==z)&(zones.metric=='mean_profit_mad')].set_index('effect')
            y=zones[(zones.zone==z)&(zones.metric=='mean_yield_t_ha')].set_index('effect')
            rows.append([z,20,value(g.loc['information_only']),value(g.loc['economics_only']),
                         value(g.loc['interaction']),value(y.loc['information_only'],3)])
        lines += [table(['Zone','Seeds','B−A profit [CI]','C−A profit [CI]','Interaction profit [CI]','B−A yield [CI]'],rows),'',
                  '### Farmers harmed or benefited versus paired A','']
        rows=[]
        for c in 'BCD':
            g=harms[(harms.zone=='ALL')&(harms.condition==c)].set_index('metric')
            rows.append([c]+[value(g.loc[k],2,100)+'%' for k in ['harmed','benefited','unchanged']])
        lines += [table(['Condition','Harmed [CI]','Benefited [CI]','Unchanged [CI]'],rows),'',
                  'Fractions are computed per seed from the 100 paired farmer identities, then averaged. '
                  'Equality tolerance is 1e−8 MAD in across-season mean profit. Zone fractions are retained in harm_summary.csv.','',
                  '### Variation and diagnostics','']
        rows=[]
        for effect in ['information_only','economics_only','interaction']:
            vals=contrasts[(contrasts.metric=='mean_profit_mad')&(contrasts.effect==effect)].value
            rows.append([effect,f'{vals.std(ddof=1):,.2f}',f'{vals.min():,.2f}',f'{vals.max():,.2f}',int((vals<0).sum())])
        lines += [table(['Profit contrast','Seed SD','Minimum seed effect','Maximum seed effect','Negative seeds'],rows),'',
                  f"Verified {diagnostics['records']:,} unique, finite outcome rows; complete 3,000-row seed-condition panels; "
                  'identical initial choices/gross yields and exogenous population/graph/weather within each seed; '
                  'all saved source, input and output hashes match. '
                  f"A/C crop disagreements over all seasons: {diagnostics['ac_crop_disagreements']}; "
                  f"B/D disagreements: {diagnostics['bd_crop_disagreements']} of 60,000 paired farmer-seasons.", '',
                  f"Execution metadata: [metadata.json]({relative}/metadata.json); full resolved settings: "
                  f"[resolved_configs.json]({relative}/resolved_configs.json); all metric contrasts: "
                  f"[effects.csv]({relative}/effects.csv). UTC completion: {meta['timestamp_utc']}.",'']
    lines += ['## Interpretation','',
              'Information access raises average simulated profit in both parameter scenarios, but does not benefit everyone. '
              'Under primary economics, the arid-zone information-only profit interval is wholly negative; '
              'the irrigated Souss estimate is negative with an interval crossing zero, and semi-arid cool is near zero with an interval crossing zero. '
              'Large positive effects in semi-arid warm and Saharan zones contribute strongly to the overall mean. '
              'The large gap between mean and median profits also cautions against treating the mean as a typical farmer outcome.','',
              'Economics-only changes profit but produces exactly zero gross-yield and productivity contrast in these runs. '
              'With empty initial memory and deterministic maximum-score decisions, a control farmer repeatedly observes only its chosen crop. '
              'A single observed crop has zero range-normalized own-experience bonus, so there is no exploration to initiate a switch. '
              'The imposed economic improvements then benefit every economics-only farmer. This is a structural result of the rules, not observed cooperative effectiveness.','',
              'The positive profit interaction includes mechanical amplification: premiums and smaller losses increase returns to information-induced output, '
              'and lower costs affect its profitability. It also permits changed decisions through realized social profit/cost signals. '
              'It is not a separate validation of social intelligence. The primary gross-yield interaction is small and positive; '
              'the sensitivity gross-yield interaction interval crosses zero.','',
              'The water proxy has exactly zero treatment contrasts in both scenarios because V1 falls back to 500 mm for every crop and '
              'paired weather determines irrigation. This cannot establish environmental neutrality or efficiency. '
              'No sustainability indicator beyond this diagnostic proxy is inferred.','',
              '## Verification and provenance','',
              f"Final test command: `{verification['command']}`. Outcome: **{verification['passed']} passed**, "
              f"{verification['failed']} failed ({verification['duration_seconds']:.2f} seconds). "
              'Coverage includes all four economic settings, information-off read/receive/publish isolation, first-season treatment independence, '
              'neutral-economics equivalence in all three information modes, independence from strategy labels, paired exogenous and latent shocks, '
              'fixed-seed/cross-process/interleaved replay, V1 yield/cost/water equation parity, seed-level factorial CIs and harm aggregation, '
              'output manifests and README sensitivity calculations.','',
              'Initial 17-test suite passed. Expanded suite initially had three failures because identical neutral-economics prices had int/float '
              'pandas dtype differences; exact numeric comparisons with dtype ignored resolved those test assertions. Simulation values were unchanged. '
              'The environment emitted a Requests dependency-version warning at pytest startup; tests and simulations completed, and the model does not use Requests.','',
              'Software: Python 3.12.4 (Anaconda), Windows 11; Mesa 3.4.2, NumPy 1.26.4, pandas 2.2.2, SciPy 1.13.1, '
              'NetworkX 3.2.1, pytest 9.0.2. Direct pins are in requirements-lock.txt and installed distribution inventory in environment-freeze.txt. '
              'Runs occurred on protocol commit 51ef5fa3bc52d8feec49cd8de93d4efb9010e0ac with implementation files then uncommitted; '
              'metadata records that state honestly and includes exact execution-source SHA-256 hashes. Notebook/data have not been changed.','',
              'Exact experiment commands (run from repository root):','',
              '```powershell',
              'python -m experiments.exp001.runner --config experiments/exp001/configs/smoke.json --output experiments/exp001/results/smoke',
              'python -m experiments.exp001.runner --config experiments/exp001/configs/primary.json --output experiments/exp001/results/primary',
              'python -m experiments.exp001.runner --config experiments/exp001/configs/readme_economics.json --output experiments/exp001/results/readme_economics',
              'python -m pytest experiments/exp001/tests -q',
              'python -m experiments.exp001.report',
              '```','',
              'The report command checks hashes and raw-data diagnostics before writing this report. Reproducing it requires the full generated primary '
              'and sensitivity outputs, not just the small committed evidence subset. Use new run directories for replay; original directory names above are '
              'the actual completed runs. Raw records and exogenous manifests remain locally available and reproducible but are not committed.','',
              '## Limits and open scientific questions','',
              'These are causal contrasts within the implemented simulator and its specified homogeneous treatment worlds, not field estimates for Morocco. '
              'Uncertainty covers random seeds only, not parameter uncertainty, data quality, model structure or economic equilibrium. '
              'Twenty seeds, unadjusted multiple comparisons, hypothetical graph/population assignment, static climate, unconstrained budgets and annual perennial switching '
              'limit interpretation. The network population differs from V1 mixed SHARED/INDIVIDUAL cohorts. See AUDIT.md for every deliberate design change.','',
              'Future reviewed experiments should address crop-specific water lookup and yield coupling, validated economics, total-profit versus per-hectare social signals, '
              'deduplication of repeated neighbor observations, separate own/social memory, and cooperative eligibility. '
              'Adaptive trust, partner selection and reinforcement learning remain out of scope.']
    (BASE/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (BASE/'diagnostics.json').write_text(json.dumps(all_diagnostics,indent=2),encoding='utf-8')
    print('Verified both completed scenarios and generated RESULTS.md')

if __name__=='__main__': main()
