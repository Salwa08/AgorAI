"""Seed-level paired factorial estimands; no agent-level significance tests."""
import numpy as np
import pandas as pd
from scipy.stats import t

METRICS = ['mean_profit_mad', 'median_profit_mad', 'mean_yield_t_ha',
           'productivity_t_ha', 'mean_profit_mad_ha', 'water_proxy_mm']


def interval(values):
    x = np.asarray(values, dtype=float)
    if not len(x) or not np.isfinite(x).all():
        raise ValueError('Finite nonempty replicates required')
    mean = float(x.mean())
    sd = float(x.std(ddof=1)) if len(x) > 1 else None
    se = sd / np.sqrt(len(x)) if sd is not None else None
    width = float(t.ppf(.975, len(x)-1) * se) if se is not None else None
    return {'n_seeds': len(x), 'estimate': mean, 'seed_sd': sd, 'standard_error': se,
            'ci_low': mean-width if width is not None else None,
            'ci_high': mean+width if width is not None else None}


def summarize(raw, by_zone=False):
    keys = ['seed', 'condition'] + (['zone'] if by_zone else [])
    # Equal weight to farmers: first average each farmer's seasons.
    agents = raw.groupby(keys + ['agent'], sort=True).agg(
        profit=('profit_mad', 'mean'), yield_=('yield_t_ha', 'mean'),
        profit_ha=('profit_mad_ha', 'mean'), water=('water_proxy_mm', 'mean'),
        production=('production_t', 'mean'), land=('land_ha', 'first')).reset_index()
    rows = []
    for labels, frame in agents.groupby(keys, sort=True):
        rows.append(dict(zip(keys, labels), n_agents=len(frame),
            mean_profit_mad=frame.profit.mean(), median_profit_mad=frame.profit.median(),
            mean_yield_t_ha=frame.yield_.mean(),
            productivity_t_ha=frame.production.sum()/frame.land.sum(),
            mean_profit_mad_ha=frame.profit_ha.mean(), water_proxy_mm=frame.water.mean()))
    return agents, pd.DataFrame(rows)


def factorial(summary):
    strata = ['zone'] if 'zone' in summary else []
    estimates, contrasts = [], []
    groups = summary.groupby('zone') if strata else [('ALL', summary)]
    for zone, group in groups:
        for metric in METRICS:
            p = group.pivot(index='seed', columns='condition', values=metric)
            if set(p.columns) != set('ABCD') or p.isna().any().any():
                raise ValueError('Complete paired A–D results required')
            a,b,c,d = (p[x] for x in 'ABCD')
            effects = {'information_only': b-a, 'economics_only': c-a,
                       'combined': d-a, 'information_given_economics': d-c,
                       'economics_given_information': d-b,
                       'information_main': (b-a+d-c)/2,
                       'economics_main': (c-a+d-b)/2,
                       'interaction': d-b-c+a}
            for effect, values in effects.items():
                estimates.append(dict(zone=zone, metric=metric, effect=effect, **interval(values)))
                contrasts.extend(dict(zone=zone, metric=metric, effect=effect, seed=int(seed),
                                      value=float(value)) for seed,value in values.items())
    return pd.DataFrame(estimates), pd.DataFrame(contrasts)


def paired_harm(agents):
    keys = ['seed', 'agent'] + (['zone'] if 'zone' in agents else [])
    p = agents.pivot(index=keys, columns='condition', values='profit')
    if p.isna().any().any():
        raise ValueError('Unpaired farmer results')
    records=[]
    for cond in 'BCD':
        delta=p[cond]-p.A
        for labels, values in delta.groupby(['seed'] + (['zone'] if 'zone' in agents else [])):
            labels = labels if isinstance(labels, tuple) else (labels,)
            records.append(dict(seed=int(labels[0]), zone=labels[1] if len(labels)>1 else 'ALL',
                condition=cond, n_agents=len(values), harmed=float((values < -1e-8).mean()),
                benefited=float((values > 1e-8).mean()), unchanged=float((values.abs() <= 1e-8).mean())))
    return pd.DataFrame(records)
