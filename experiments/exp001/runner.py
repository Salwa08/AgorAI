"""Run from repository root: python -m experiments.exp001.runner --config PATH."""
import argparse
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
import pandas as pd
from .model import SIM_CONFIG, DATA_DIR, run_sim
from .analysis import summarize, factorial, paired_harm, interval

CONDITIONS = {'A': (False, False), 'B': (True, False), 'C': (False, True), 'D': (True, True)}
ROOT = Path(__file__).resolve().parents[2]


def git(*args):
    result = subprocess.run(['git', *args], cwd=ROOT, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else 'unavailable'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(config, output):
    if set(config) != {'model', 'seeds', 'scenario'}:
        raise ValueError('Config requires exactly model, seeds, scenario')
    seeds = config['seeds']
    if not seeds or len(set(seeds)) != len(seeds) or any(type(s) is not int or s < 0 for s in seeds):
        raise ValueError('Seeds must be unique nonnegative integers')
    if any(k in config['model'] for k in ['social_information_enabled','cooperative_economics_enabled','random_seed']):
        raise ValueError('Runner controls treatment flags and random_seed')
    base = SIM_CONFIG(**config['model'])
    if type(base.n_agents) is not int or type(base.n_seasons) is not int:
        raise ValueError('Agent and season counts must be integers')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    rows, environments = [], []
    configs = {}
    for seed in seeds:
        for condition, (information, economics) in CONDITIONS.items():
            cfg = replace(base, random_seed=seed, social_information_enabled=information,
                          cooperative_economics_enabled=economics)
            configs[f'{seed}/{condition}'] = asdict(cfg)
            model, frame = run_sim(cfg)
            frame.insert(1, 'condition', condition)
            rows.append(frame)
            environment = dict(weather=model.weather_history,
                agents=[dict(id=f.unique_id, zone=f.zone.id, land=f.land_size, budget=f.budget,
                             goal=f.goal_profile, irrigation=f.irrigation_type, cost=f.cost_noise_factor)
                        for f in model.farmers],
                edges=sorted([sorted(e) for e in model.graph.edges]) if model.graph is not None else [])
            environments.append(dict(seed=seed,condition=condition,environment=environment,
                sha256=hashlib.sha256(json.dumps(environment,sort_keys=True).encode()).hexdigest()))
        print(f'Completed seed {seed}: A B C D', flush=True)
    raw=pd.concat(rows,ignore_index=True)
    raw.to_csv(output/'agent_season.csv',index=False)
    # Save observations before any aggregate computation.
    (output/'exogenous.json').write_text(json.dumps(environments,indent=2),encoding='utf-8')
    for seed in seeds:
        if len({x['sha256'] for x in environments if x['seed']==seed}) != 1:
            raise AssertionError('Exogenous pairing failed')
    agents, summaries=summarize(raw)
    zone_agents, zones=summarize(raw,by_zone=True)
    agents.to_csv(output/'agents.csv',index=False)
    summaries.to_csv(output/'seed_summary.csv',index=False)
    zones.to_csv(output/'zone_seed_summary.csv',index=False)
    raw.groupby(['seed','condition','season']).agg(
        mean_profit_mad=('profit_mad','mean'),median_profit_mad=('profit_mad','median'),
        mean_yield_t_ha=('yield_t_ha','mean'),production_t=('production_t','sum'),
        land_ha=('land_ha','sum')).to_csv(output/'seasons.csv')
    raw.groupby(['seed','condition','zone','season']).agg(
        n_agents=('agent','count'),mean_profit_mad=('profit_mad','mean'),
        mean_yield_t_ha=('yield_t_ha','mean')).to_csv(output/'zone_seasons.csv')
    effects, contrasts=factorial(summaries)
    zone_effects, zone_contrasts=factorial(zones)
    effects.to_csv(output/'effects.csv',index=False)
    contrasts.to_csv(output/'paired_seed_contrasts.csv',index=False)
    zone_effects.to_csv(output/'zone_effects.csv',index=False)
    zone_contrasts.to_csv(output/'zone_paired_seed_contrasts.csv',index=False)
    harms=pd.concat([paired_harm(agents),paired_harm(zone_agents)],ignore_index=True)
    harms.to_csv(output/'paired_harm.csv',index=False)
    harm_summary=[]
    for (zone,condition), g in harms.groupby(['zone','condition']):
        for metric in ['harmed','benefited','unchanged']:
            harm_summary.append(dict(zone=zone,condition=condition,metric=metric,**interval(g[metric])))
    pd.DataFrame(harm_summary).to_csv(output/'harm_summary.csv',index=False)
    condition_summary=[]
    for condition, g in summaries.groupby('condition'):
        for metric in ['mean_profit_mad','median_profit_mad','mean_yield_t_ha','productivity_t_ha']:
            condition_summary.append(dict(condition=condition,metric=metric,**interval(g[metric])))
    pd.DataFrame(condition_summary).to_csv(output/'condition_summary.csv',index=False)
    (output/'config.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
    (output/'resolved_configs.json').write_text(json.dumps(configs,indent=2),encoding='utf-8')
    metadata=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),python=sys.version,
        platform=platform.platform(), executable=sys.executable,command=sys.argv,
        git_commit=git('rev-parse','HEAD'),git_status=git('status','--short'),
        packages={name:importlib.metadata.version(name) for name in ['mesa','numpy','pandas','scipy','networkx','pytest']},
        input_sha256={p.name:digest(p) for p in sorted(DATA_DIR.glob('*.json'))},
        source_sha256={str(p.relative_to(ROOT)):digest(p) for p in sorted(Path(__file__).parent.glob('*.py'))},
        notebook_sha256=digest(ROOT/'simulation.ipynb'),exogenous_pairing_verified=True,
        n_seed_replicates=len(seeds),n_agent_season_records=len(raw),
        output_sha256={p.name:digest(p) for p in sorted(output.iterdir()) if p.is_file()})
    (output/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    execute(json.loads(args.config.read_text(encoding='utf-8-sig')),args.output)

if __name__ == '__main__':
    main()
