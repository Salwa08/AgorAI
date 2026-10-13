"""Verify completed runs and summarize diagnostic evidence without agent-level inference."""
import argparse
import hashlib
import gzip
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .analysis import interval,B_ARMS,E_ARMS

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]


def summarize_groups(frame,keys,metrics):
    rows=[]
    for labels,g in frame.groupby(keys):
        labels=labels if isinstance(labels,tuple) else (labels,)
        for metric in metrics:
            rows.append(dict(zip(keys,labels),metric=metric,**interval(g[metric])))
    return pd.DataFrame(rows)


def execute(output):
    output=Path(output)
    metadata=json.loads((output/'metadata.json').read_text())
    for name,expected in metadata['output_sha256'].items():
        assert hashlib.sha256((output/name).read_bytes()).hexdigest()==expected,name
    for name,expected in metadata['input_sha256'].items():
        assert hashlib.sha256((ROOT/name.replace('\\','/')).read_bytes()).hexdigest()==expected,name
    for name,expected in metadata['source_sha256'].items():
        # Execution modules are immutable while running; report/diagnostic scripts are downstream.
        if name.replace('\\','/') in ['experiments/exp002/model.py','experiments/exp002/runner.py','experiments/exp002/analysis.py']:
            assert hashlib.sha256((ROOT/name.replace('\\','/')).read_bytes()).hexdigest()==expected,name
    config=json.loads((output/'config.json').read_text())
    assert config['n_agents']==100 and config['n_seasons']==30 and config['seeds']==list(range(20))
    reproduction=pd.read_csv(output/'exp001_reproduction.csv',float_precision='round_trip').sort_values(['seed','condition']).reset_index(drop=True)
    golden=pd.read_csv(BASE.parent/'exp001/results/primary/seed_summary.csv',float_precision='round_trip').sort_values(['seed','condition']).reset_index(drop=True)
    pd.testing.assert_frame_equal(reproduction,golden,check_exact=True)
    manifest=pd.DataFrame(json.loads((output/'run_manifest.json').read_text()))
    assert manifest.groupby('seed').arm.nunique().eq(16).all()
    assert manifest.groupby('seed').exogenous_sha256.nunique().eq(1).all()
    assert manifest.n_rows.eq(3000).all()
    agents=pd.read_csv(output/'agents.csv')
    assert not agents.duplicated(['seed','arm','agent']).any()
    exploratory=[];rescues=[]
    for seed,a in agents.groupby('seed'):
        for zone,g in [('ALL',a),*list(a.groupby('zone'))]:
            p=g.pivot(index='agent',columns='arm',values='profit')
            assert not p.isna().any().any()
            for ref in E_ARMS:
                d=p.B-p[ref]
                exploratory.append(dict(seed=seed,zone=zone,reference=ref,n_agents=len(d),
                    mean_profit_effect=d.mean(),median_effect=d.median(),harmed=(d < -1e-8).mean(),
                    negative_part_loss=-d.clip(upper=0).mean()))
            harmed=p.B-p.A < -1e-8
            for arm in B_ARMS:
                d=p[arm]-p.A
                rescues.append(dict(seed=seed,zone=zone,arm=arm,originally_harmed=int(harmed.sum()),
                    rescue_fraction=((d>=-1e-8)&harmed).sum()/harmed.sum() if harmed.any() else np.nan,
                    newly_harmed_fraction=((d < -1e-8)&~harmed).mean()))
    exploration=pd.DataFrame(exploratory)
    exploration.to_csv(output/'exploration_seed_comparisons.csv',index=False)
    summarize_groups(exploration,['zone','reference'],['mean_profit_effect','median_effect','harmed','negative_part_loss']).to_csv(output/'exploration_comparisons.csv',index=False)
    rescue=pd.DataFrame(rescues)
    rescue.to_csv(output/'rescue_seed.csv',index=False)
    summarize_groups(rescue,['zone','arm'],['rescue_fraction','newly_harmed_fraction']).to_csv(output/'rescue_summary.csv',index=False)
    diagnostic=[];records=0
    for row in manifest.itertuples():
        path=output/'raw'/f'{row.seed:02}_{row.arm}_outcomes.csv.gz'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row.outcomes_sha256
        f=pd.read_csv(path,float_precision='round_trip')
        assert len(f)==3000 and not f.duplicated(['agent','season']).any()
        assert np.isfinite(f[['profit_mad','yield_t_ha','delta_profit_A','chosen_score']]).all().all()
        assert np.allclose(f.delta_profit_A,f.yield_revenue_delta+f.price_revenue_delta+f.cost_profit_delta,atol=1e-7)
        records+=len(f)
        if row.arm=='B':
            assert f.cross_zone_count.eq(0).all()
            for zone,g in [('ALL',f),*list(f.groupby('zone'))]:
                lost=g.delta_profit_A < -1e-8
                diagnostic.append(dict(seed=row.seed,zone=zone,
                    loss_row_fraction=lost.mean(),
                    score_conflict_among_losses=g.loc[lost,'score_profit_conflict'].mean(),
                    yield_gain_among_losses=g.loc[lost,'yield_profit_tradeoff'].mean(),
                    mean_yield_component=g.yield_revenue_delta.mean(),
                    mean_price_component=g.price_revenue_delta.mean(),
                    mean_cost_component=g.cost_profit_delta.mean(),
                    mean_neighbor_duplicates=g.neighbor_duplicates.mean(),
                    neighbor_duplicate_fraction=(g.neighbor_duplicates/g.neighbor_count.replace(0,np.nan)).mean(),
                    received_experience=g.received_experience.mean(),
                    cross_channel_duplicates=g.cross_channel_duplicates.mean(),
                    mean_age=g.age_mean.mean()))
    diag=pd.DataFrame(diagnostic)
    diag.to_csv(output/'B_diagnostic_seeds.csv',index=False)
    summarize_groups(diag,['zone'],[c for c in diag.columns if c not in ['seed','zone']]).to_csv(output/'B_diagnostics.csv',index=False)
    # Pad absent crop substitutions with zero before averaging seed contributions.
    pairs=pd.read_csv(output/'crop_pairs.csv');pairs=pairs[pairs.arm=='B'].copy()
    pairs['denom']=pairs.groupby(['seed','zone']).n.transform('sum')
    pairs['contribution']=pairs.sum_profit_delta/pairs.denom
    pairrows=[]
    for (zone,baseline,crop),g in pairs.groupby(['zone','baseline_crop','crop']):
        values=g.set_index('seed').contribution.reindex(config['seeds'],fill_value=0)
        pairrows.append(dict(zone=zone,baseline_crop=baseline,crop=crop,n_rows=int(g.n.sum()),
                             **interval(values)))
    pd.DataFrame(pairrows).to_csv(output/'B_crop_contributions.csv',index=False)
    effects=pd.read_csv(output/'contrasts.csv')
    assert (effects.family=='prespecified_48').sum()==48
    assert effects[effects.family=='prespecified_48'].p_holm.notna().all()
    verification=dict(exp001_seed_summaries_exact=True,matched_seed_arms=320,
        verified_outcome_rows=records,exogenous_pairing=True,B_cross_zone_observations=0,
        primary_holm_tests=48,source_input_output_hashes=True)
    (output/'verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
    # Explicitly post-hoc illustration, selected by a reproducible rule.
    rows=pd.read_csv(output/'raw/00_B_outcomes.csv.gz')
    selected=rows[(rows.zone=='ARID') & (rows.delta_profit_A < 0) &
                  (rows.baseline_crop=='almonds')].sort_values(['season','agent']).iloc[0]
    case=dict(selection="Post-hoc illustration: first negative ARID B row in seed 0 with A crop almonds, ordered by season then agent. Not representative or a statistical test.",
              seed=0,agent=int(selected.agent),season=int(selected.season),arms={})
    for arm in ['A','B','dedup','own_memory_only','profit_per_ha','zone_profit_only']:
        with gzip.open(output/f'raw/00_{arm}_decisions.jsonl.gz','rt',encoding='utf-8') as stream:
            for line in stream:
                trace=json.loads(line)
                if trace['agent']==case['agent'] and trace['season']==case['season']:
                    case['arms'][arm]=trace
                    break
        assert arm in case['arms']
    (output/'case_study.json').write_text(json.dumps(case,indent=2),encoding='utf-8')
    analysis_files=['exploration_seed_comparisons.csv','exploration_comparisons.csv',
                    'rescue_seed.csv','rescue_summary.csv','B_diagnostic_seeds.csv',
                    'B_diagnostics.csv','B_crop_contributions.csv','verification.json','case_study.json']
    analysis_metadata=dict(stage='Post-execution diagnostics; separate from simulation execution metadata',
        source_sha256={name:hashlib.sha256((BASE/name).read_bytes()).hexdigest()
                       for name in ['diagnose.py','report.py']},
        output_sha256={name:hashlib.sha256((output/name).read_bytes()).hexdigest() for name in analysis_files})
    (output/'analysis_metadata.json').write_text(json.dumps(analysis_metadata,indent=2),encoding='utf-8')
    print(json.dumps(verification,indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--results',type=Path,required=True)
    execute(p.parse_args().results)

if __name__=='__main__':main()
