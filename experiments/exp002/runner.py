"""Run all prespecified EXP002 arms; raw traces stay local and compressed."""
import argparse
from dataclasses import asdict,replace
import gzip
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime,timezone
import pandas as pd
from .model import Config,run_sim
from .analysis import aggregate_seed,contrasts,interval
from experiments.exp001.analysis import summarize

ROOT=Path(__file__).resolve().parents[2]
ARMS={
 'A':{},'B':{'social_information_enabled':True},
 'C':{'cooperative_economics_enabled':True},
 'D':{'social_information_enabled':True,'cooperative_economics_enabled':True},
 'A_e02':{'epsilon':.02},'A_e05':{'epsilon':.05},'A_e10':{'epsilon':.10},'A_e20':{'epsilon':.20},
 'zone_only':{'social_information_enabled':True,'shared_strategy':'zone'},
 'neighbor_only':{'social_information_enabled':True,'shared_strategy':'neighbor'},
 'dedup':{'social_information_enabled':True,'deduplicate':True},
 'own_memory_only':{'social_information_enabled':True,'own_memory_only':True},
 'profit_per_ha':{'social_information_enabled':True,'profit_per_ha':True},
 'unrestricted':{'social_information_enabled':True,'context_filter':'unrestricted'},
 'ecological':{'social_information_enabled':True,'context_filter':'ecological'},
 'zone_profit_only':{'social_information_enabled':True,'zone_yield_fraction':0.},
}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def flatten(model,baseline):
    rows=[]
    for trace in model.traces:
        t=trace
        a=baseline[(t['agent'],t['season'])]
        delta=t['profit_mad']-a['profit_mad']
        t['paired_A']=dict(crop=a['crop'],profit_mad=a['profit_mad'],delta_profit_mad=delta,
                          delta_yield_t_ha=t['yield_t_ha']-a['yield_t_ha'])
        selected=t['candidates'][t['crop']]
        score_gain=t['chosen_score']-t['candidates'][a['crop']]['total_score']
        yield_revenue=(t['effective_yield_t_ha']-a['effective_yield_t_ha'])*(t['price_mad_t']+a['price_mad_t'])/2*t['land_ha']
        price_revenue=(t['price_mad_t']-a['price_mad_t'])*(t['effective_yield_t_ha']+a['effective_yield_t_ha'])/2*t['land_ha']
        cost_delta=-(t['cost_mad_ha']-a['cost_mad_ha'])*t['land_ha']
        assert abs(delta-yield_revenue-price_revenue-cost_delta)<1e-7
        row={k:t[k] for k in model.records[0]}
        row.update(previous_crop=t['previous_crop'],switched=t['switched'],explored=t['explored'],baseline_crop=a['crop'],
            delta_profit_A=delta,delta_yield_A=t['yield_t_ha']-a['yield_t_ha'],score_gain_vs_A=score_gain,
            score_profit_conflict=int(score_gain>1e-12 and delta < -1e-8),
            yield_profit_tradeoff=int(t['yield_t_ha']>a['yield_t_ha'] and delta < -1e-8),
            yield_revenue_delta=yield_revenue,price_revenue_delta=price_revenue,cost_profit_delta=cost_delta,
            received_experience=t['experience_info']['received'],neighbor_count=t['neighbor_info']['count'],
            neighbor_duplicates=t['neighbor_info']['duplicates'],cross_zone_count=t['all_channels_info']['cross_zone'],
            unique_observations=t['all_channels_info']['unique'],observation_appearances=t['all_channels_info']['count'],
            cross_channel_duplicates=t['all_channels_info']['duplicates'],
            age_mean=t['all_channels_info']['age_mean'],profit_regret=t['analyst_only_profit_regret'],
            source_land_mean=t['zone_info']['source_land_mean'],goal=json.dumps(t['goal'],sort_keys=True),
            chosen_suitability=selected['suitability'],chosen_experience=selected['experience'],
            chosen_zone=selected['zone'],chosen_neighbor=selected['neighbor'],chosen_score=t['chosen_score'])
        rows.append(row)
    frame=pd.DataFrame(rows).sort_values(['season','agent']).reset_index(drop=True)
    for col in ['age_mean','source_land_mean']:
        frame[col]=pd.to_numeric(frame[col],errors='raise').astype(float)
    return frame


def execute(config,output):
    if set(config)!={'seeds','n_agents','n_seasons','arms'}: raise ValueError('Invalid config fields')
    if config['arms']!=list(ARMS): raise ValueError('Prespecified complete arm list required')
    seeds=config['seeds']
    if not seeds or len(set(seeds))!=len(seeds) or any(type(s)!=int or s<0 for s in seeds):
        raise ValueError('Unique nonnegative integer seeds required')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    rawdir=output/'raw';rawdir.mkdir()
    agents_out=[];seeds_out=[];reproduction=[];transition=[];switch_transitions=[];temporal=[];subgroups=[];manifests=[]
    resolved={}
    for seed in seeds:
        base=Config(n_agents=config['n_agents'],n_seasons=config['n_seasons'],random_seed=seed)
        baseline=None;env_ref=None;frames=[];v1frames=[]
        for arm,changes in ARMS.items():
            cfg=replace(base,**changes);resolved[f'{seed}/{arm}']=asdict(cfg)
            model,raw=run_sim(cfg,True)
            if baseline is None: baseline={(r['agent'],r['season']):r for r in model.records}
            env=dict(weather=model.weather_history,edges=list(model.graph.edges),
                agents=[dict(agent=f.unique_id,zone=f.zone.id,land=f.land_size,budget=f.budget,
                             goal=f.goal_profile,cost=f.cost_noise_factor) for f in model.farmers])
            envhash=hashlib.sha256(json.dumps(env,sort_keys=True).encode()).hexdigest()
            if env_ref is None: env_ref=envhash
            assert envhash==env_ref
            if arm=='A':
                (rawdir/f'{seed:02}_environment.json').write_text(json.dumps(env),encoding='utf-8')
            flat=flatten(model,baseline);flat.insert(1,'arm',arm);frames.append(flat)
            stem=f'{seed:02}_{arm}'
            flat.to_csv(rawdir/f'{stem}_outcomes.csv.gz',index=False,compression='gzip')
            with gzip.open(rawdir/f'{stem}_decisions.jsonl.gz','wt',encoding='utf-8',compresslevel=1) as f:
                for row in model.traces: f.write(json.dumps(row,separators=(',',':'))+'\n')
            with gzip.open(rawdir/f'{stem}_observations.jsonl.gz','wt',encoding='utf-8',compresslevel=1) as f:
                for obs in model.ledger: f.write(json.dumps(asdict(obs),separators=(',',':'))+'\n')
            manifests.append(dict(seed=seed,arm=arm,n_rows=len(flat),exogenous_sha256=envhash,
                                  outcomes_sha256=sha(rawdir/f'{stem}_outcomes.csv.gz')))
            if arm in 'ABCD' and len(arm)==1:
                raw.insert(1,'condition',arm);v1frames.append(raw)
            print(f'seed {seed:02} {arm} complete',flush=True)
        frame=pd.concat(frames,ignore_index=True)
        agents,summary=aggregate_seed(frame);agents_out.append(agents);seeds_out.append(summary)
        _,vs=summarize(pd.concat(v1frames,ignore_index=True));reproduction.append(vs)
        merged=frame.merge(agents[['arm','agent','harm_group']],on=['arm','agent'],validate='many_to_one')
        for (arm,zone,status),g in merged.groupby(['arm','zone','harm_group']):
            subgroups.append(dict(seed=seed,arm=arm,zone=zone,group=status,n_agents=g.agent.nunique(),
                mean_land=g.land_ha.mean(),switch_rate=g[g.season>1].switched.mean(),mean_delta=g.delta_profit_A.mean(),
                mean_yield_delta=g.delta_yield_A.mean(),yield_component=g.yield_revenue_delta.mean(),
                price_component=g.price_revenue_delta.mean(),cost_component=g.cost_profit_delta.mean(),
                received_experience=g.received_experience.mean(),neighbor_duplicates=g.neighbor_duplicates.mean(),
                neighbor_count=g.neighbor_count.mean(),cross_zone_count=g.cross_zone_count.mean(),
                score_profit_conflict=g.score_profit_conflict.mean(),yield_profit_tradeoff=g.yield_profit_tradeoff.mean(),
                profit_regret=g.profit_regret.mean(),source_land_mean=g.source_land_mean.mean()))
        # Crop-pair attribution covers ALL rows, not only switches; decomposes the total paired effect.
        for keys,g in frame.groupby(['arm','zone','baseline_crop','crop']):
            arm,zone,acrop,crop=keys
            transition.append(dict(seed=seed,arm=arm,zone=zone,baseline_crop=acrop,crop=crop,
                n=len(g),sum_profit_delta=g.delta_profit_A.sum(),mean_profit_delta=g.delta_profit_A.mean(),
                sum_yield_component=g.yield_revenue_delta.sum(),sum_price_component=g.price_revenue_delta.sum(),
                sum_cost_component=g.cost_profit_delta.sum(),yield_delta=g.delta_yield_A.mean()))
        for keys,g in frame[frame.switched].groupby(['arm','zone','previous_crop','crop']):
            arm,zone,previous,crop=keys
            switch_transitions.append(dict(seed=seed,arm=arm,zone=zone,previous_crop=previous,crop=crop,
                n=len(g),mean_profit_delta=g.delta_profit_A.mean(),sum_profit_delta=g.delta_profit_A.sum(),
                yield_delta=g.delta_yield_A.mean(),score_gain=g.score_gain_vs_A.mean()))
        for keys,g in frame.groupby(['arm','zone','season']):
            arm,zone,season=keys
            temporal.append(dict(seed=seed,arm=arm,zone=zone,season=season,n=len(g),
                mean_profit_delta=g.delta_profit_A.mean(),harmed_fraction=(g.delta_profit_A < -1e-8).mean(),
                switch_fraction=g.switched.mean(),yield_delta=g.delta_yield_A.mean()))
    agents=pd.concat(agents_out,ignore_index=True);summary=pd.concat(seeds_out,ignore_index=True)
    agents.to_csv(output/'agents.csv',index=False);summary.to_csv(output/'seed_summary.csv',index=False)
    pd.concat(reproduction,ignore_index=True).to_csv(output/'exp001_reproduction.csv',index=False)
    effects=contrasts(summary);effects.to_csv(output/'contrasts.csv',index=False)
    level=[]
    for (arm,zone),g in summary.groupby(['arm','zone']):
        for metric in ['mean_profit','median_profit','mean_yield','productivity','effect_A','harmed_A',
                       'negative_part_loss','conditional_harmed_loss','q10_effect_A','switch_rate','profit_regret']:
            level.append(dict(arm=arm,zone=zone,metric=metric,**interval(g[metric])))
    pd.DataFrame(level).to_csv(output/'levels.csv',index=False)
    pd.DataFrame(transition).to_csv(output/'crop_pairs.csv',index=False)
    pd.DataFrame(switch_transitions).to_csv(output/'switch_transitions.csv',index=False)
    pd.DataFrame(temporal).to_csv(output/'season_zone.csv',index=False)
    pd.DataFrame(subgroups).to_csv(output/'harm_groups.csv',index=False)
    (output/'config.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
    (output/'resolved_configs.json').write_text(json.dumps(resolved,indent=2),encoding='utf-8')
    (output/'run_manifest.json').write_text(json.dumps(manifests,indent=2),encoding='utf-8')
    source_paths=list((ROOT/'experiments/exp002').glob('*.py'))+list((ROOT/'experiments/exp001').glob('*.py'))
    metadata=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),command=sys.argv,python=sys.version,
        platform=platform.platform(),packages={x:importlib.metadata.version(x) for x in ['mesa','numpy','pandas','scipy','networkx','pytest']},
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        git_status=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'data').glob('*.json')},
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in source_paths},
        output_sha256={p.name:sha(p) for p in output.iterdir() if p.is_file()},
        n_seeds=len(seeds),n_arms=len(ARMS),n_records=sum(m['n_rows'] for m in manifests))
    (output/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    execute(json.loads(args.config.read_text(encoding='utf-8-sig')),args.output)

if __name__=='__main__':main()
