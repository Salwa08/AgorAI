"""Seed-replicated paired diagnostics; farmer-season associations remain descriptive."""
import numpy as np
import pandas as pd
from scipy.stats import t

B_ARMS=['zone_only','neighbor_only','dedup','own_memory_only','profit_per_ha',
        'unrestricted','ecological','zone_profit_only']
E_ARMS=['A_e02','A_e05','A_e10','A_e20']
METRICS=['mean_profit','median_profit','mean_yield','productivity','effect_A','median_effect_A',
         'harmed_A','benefited_A','negative_part_loss','conditional_harmed_loss','q10_effect_A',
         'switch_rate','score_profit_conflict','yield_profit_tradeoff','received_experience',
         'neighbor_count','neighbor_duplicates','cross_zone_count','profit_regret']


def interval(values):
    a=np.asarray(values,dtype=float); a=a[np.isfinite(a)]
    n=len(a)
    if not n: return dict(n=0,estimate=np.nan,sd=np.nan,se=np.nan,ci_low=np.nan,ci_high=np.nan,p=np.nan)
    mean=float(a.mean()); sd=float(a.std(ddof=1)) if n>1 else np.nan
    se=sd/np.sqrt(n)
    width=t.ppf(.975,n-1)*se if n>1 else np.nan
    p=float(2*t.sf(abs(mean/se),n-1)) if se>0 else (1. if n>1 and mean==0 else 0. if n>1 else np.nan)
    return dict(n=n,estimate=mean,sd=sd,se=se,ci_low=mean-width,ci_high=mean+width,p=p)


def holm(pvalues):
    p=np.asarray(pvalues,float)
    if not np.isfinite(p).all(): raise ValueError('Finite p-values required')
    order=np.argsort(p); adjusted=np.empty(len(p)); running=0.
    for rank,index in enumerate(order):
        running=max(running,(len(p)-rank)*p[index]);adjusted[index]=min(1.,running)
    return adjusted


def aggregate_seed(frame):
    agents=frame.groupby(['seed','arm','zone','agent'],sort=True).agg(
        profit=('profit_mad','mean'),yield_=('yield_t_ha','mean'),production=('production_t','mean'),
        land=('land_ha','first'),delta=('delta_profit_A','mean'),delta_yield=('delta_yield_A','mean'),
        switches=('switched','sum'),seasons=('season','count'),
        score_profit_conflict=('score_profit_conflict','mean'),yield_profit_tradeoff=('yield_profit_tradeoff','mean'),
        received_experience=('received_experience','mean'),neighbor_count=('neighbor_count','mean'),
        neighbor_duplicates=('neighbor_duplicates','mean'),cross_zone_count=('cross_zone_count','mean'),
        profit_regret=('profit_regret','mean'),yield_component=('yield_revenue_delta','mean'),
        price_component=('price_revenue_delta','mean'),cost_component=('cost_profit_delta','mean')).reset_index()
    agents['switch_rate']=agents.switches/(agents.seasons-1).clip(lower=1)
    agents['harm_group']=np.where(agents.delta < -1e-8,'harmed',np.where(agents.delta>1e-8,'benefited','unchanged'))
    rows=[]
    for arm,a in agents.groupby('arm'):
        for zone,g in [('ALL',a),*list(a.groupby('zone'))]:
            neg=g.delta[g.delta < -1e-8]
            row=dict(seed=int(g.seed.iloc[0]),arm=arm,zone=zone,n_agents=len(g),
                     mean_profit=g.profit.mean(),median_profit=g.profit.median(),mean_yield=g.yield_.mean(),
                     productivity=g.production.sum()/g.land.sum(),effect_A=g.delta.mean(),median_effect_A=g.delta.median(),
                     harmed_A=(g.delta < -1e-8).mean(),benefited_A=(g.delta>1e-8).mean(),
                     negative_part_loss=(-g.delta.clip(upper=0)).mean(),
                     conditional_harmed_loss=-neg.mean() if len(neg) else np.nan,q10_effect_A=g.delta.quantile(.1))
            for metric in METRICS[10:]:
                if metric in g: row[metric]=g[metric].mean()
            rows.append(row)
    return agents,pd.DataFrame(rows)


def contrasts(seed_summary):
    pairs=[(x,'B') for x in B_ARMS]+[(x,'A') for x in E_ARMS]+[('B','A')]+[('B',x) for x in E_ARMS]
    rows=[]
    for zone,group in seed_summary.groupby('zone'):
        for metric in METRICS:
            p=group.pivot(index='seed',columns='arm',values=metric)
            for arm,reference in pairs:
                if arm not in p or reference not in p: continue
                values=p[arm]-p[reference]
                rows.append(dict(zone=zone,metric=metric,arm=arm,reference=reference,**interval(values)))
    effects=pd.DataFrame(rows)
    primary=(effects.zone.isin(['ALL','ARID']) & effects.metric.isin(['mean_profit','harmed_A']) &
             ((effects.arm.isin(B_ARMS)&effects.reference.eq('B')) |
              (effects.arm.isin(E_ARMS)&effects.reference.eq('A'))))
    effects['family']='exploratory';effects.loc[primary,'family']='prespecified_48'
    effects['p_holm']=np.nan
    valid=primary & effects.p.notna()
    if valid.sum(): effects.loc[valid,'p_holm']=holm(effects.loc[valid,'p'])
    return effects
