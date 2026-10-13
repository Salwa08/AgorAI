import numpy as np
import pandas as pd
import pytest
from dataclasses import replace
from experiments.exp002.analysis import interval,holm,aggregate_seed,contrasts,B_ARMS,E_ARMS
from experiments.exp002.runner import flatten,ARMS
from experiments.exp002.model import Config,run_sim,DiagnosticModel,Observation


def test_holm_and_seed_interval():
    assert holm([.01,.04,.03])==pytest.approx([.03,.06,.06])
    i=interval([1,2,3])
    assert i['se']==pytest.approx(1/np.sqrt(3))
    assert i['ci_low']==pytest.approx(2-4.302652729911275/np.sqrt(3))
    assert np.isnan(interval([1])['ci_low'])


def test_pairing_decomposition_and_aggregation():
    cfg=Config(n_agents=12,n_seasons=3)
    a,_=run_sim(cfg);b,_=run_sim(replace(cfg,social_information_enabled=True))
    base={(r['agent'],r['season']):r for r in a.records}
    frames=[]
    for arm,model in [('A',a),('B',b)]:
        f=flatten(model,base);f['arm']=arm;frames.append(f)
        assert np.allclose(f.delta_profit_A,f.yield_revenue_delta+f.price_revenue_delta+f.cost_profit_delta)
    agents,summary=aggregate_seed(pd.concat(frames))
    row=summary[(summary.arm=='B')&(summary.zone=='ALL')].iloc[0]
    ag=agents[agents.arm=='B']
    assert row.effect_A==pytest.approx(ag.delta.mean())
    assert row.harmed_A==pytest.approx((ag.delta < -1e-8).mean())
    assert row.negative_part_loss==pytest.approx((-ag.delta.clip(upper=0)).mean())
    assert len(ag)==12


def test_prespecified_family_has_48_tests():
    from experiments.exp002.analysis import METRICS
    rows=[]
    for seed in range(3):
        for zone in ['ALL','ARID','OTHER']:
            for index,arm in enumerate(ARMS):
                rows.append(dict(seed=seed,arm=arm,zone=zone,**{m:index*(seed+1) for m in METRICS}))
    e=contrasts(pd.DataFrame(rows))
    assert (e.family=='prespecified_48').sum()==48
    assert e[e.family=='prespecified_48'].p_holm.notna().all()
    assert e[e.family=='exploratory'].p_holm.isna().all()
    assert (e.n==3).all()


def test_own_memory_separation_does_not_change_neighbor_pool():
    model=DiagnosticModel(Config(n_agents=6,social_information_enabled=True))
    a,b=model.farmers[:2]; b.zone=a.zone;a.neighbor_agents=[b]
    own=Observation(42,a.unique_id,1,a.zone.id,'barley',1,1,1,1,1)
    other=replace(own,farmer=b.unique_id)
    a.provenance={'barley':[own,other]};b.provenance={'barley':[other,other]}
    before=model.pools(a)
    model.cfg.own_memory_only=True
    after=model.pools(a)
    assert before[1]==after[1]
    assert after[0]['barley']==[own]
    assert len(after[1]['barley'])==2


def test_context_ultimate_source_cannot_bypass_filter():
    model=DiagnosticModel(Config(n_agents=6,social_information_enabled=True))
    a,b=model.farmers[:2];b.zone=a.zone;a.neighbor_agents=[b]
    foreign=next(z for z in model.zones if z!=a.zone.id)
    b.provenance={'barley':[Observation(42,b.unique_id,1,foreign,'barley',1,1,1,1,1)]}
    assert model.pools(a)[1]['barley']==[]
    model.cfg.context_filter='unrestricted'
    assert len(model.pools(a)[1]['barley'])==1


def test_single_factor_config_independence():
    baseline=ARMS['B']
    for arm in B_ARMS:
        assert sum(ARMS[arm].get(k)!=baseline.get(k) for k in set(ARMS[arm])|set(baseline))==1
    for arm in E_ARMS: assert set(ARMS[arm])=={'epsilon'}
