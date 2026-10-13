from dataclasses import replace
import json
from pathlib import Path
import pandas as pd
import pytest
from experiments.exp001 import model as v1
from experiments.exp002.model import Config, DiagnosticModel, Observation, unique, compatible, run_sim

@pytest.mark.parametrize('information,economics',[(False,False),(True,False),(False,True),(True,True)])
def test_instrumentation_equivalence(information,economics):
    config=Config(n_agents=12,n_seasons=5,random_seed=8,social_information_enabled=information,
                  cooperative_economics_enabled=economics)
    vconfig=v1.SIM_CONFIG(**{k:getattr(config,k) for k in v1.SIM_CONFIG.__dataclass_fields__})
    _,expected=v1.run_sim(vconfig)
    off,actual=run_sim(config,False)
    on,traced=run_sim(config,True)
    pd.testing.assert_frame_equal(actual,expected,check_exact=True)
    pd.testing.assert_frame_equal(traced,expected,check_exact=True)
    assert off.traces==[]
    assert len(on.traces)==60
    for row in on.traces:
        for c in row['candidates'].values():
            assert sum(c[k] for k in ['suitability','zone','neighbor','experience'])==pytest.approx(c['total_score'])
            for pool in ['experience_info','zone_info','neighbor_info']:
                assert c[pool]['age_min'] is None or c[pool]['age_min']>=1
        assert row['candidates'][row['crop']]['analyst_only_same_shock_profit']==row['profit_mad']
        assert row['chosen_score']==max(c['total_score'] for c in row['candidates'].values())


def test_no_future_leakage_and_provenance():
    config=Config(n_agents=12,n_seasons=4,social_information_enabled=True)
    model,_=run_sim(config)
    assert len({o.identity for o in model.ledger})==48
    for t in model.traces:
        if t['season']==1: assert t['all_channels_info']['count']==0
        assert t['all_channels_info']['cross_zone']==0
    for f in model.farmers:
        assert {c:[o.values for o in obs] for c,obs in f.provenance.items()}==f.knowledge_base
    future=Observation(42,0,4,'ARID','barley',1,1,1,1,1)
    with pytest.raises(AssertionError): model.pool_stats([future],model.farmers[0])


def test_dedup_is_identity_not_numeric_equality():
    a=Observation(0,0,1,'ARID','barley',1,1,2,3,4)
    b=replace(a,farmer=1)
    assert unique([a,a,b,a])==[a,b]
    config=Config(n_agents=6,social_information_enabled=True)
    model=DiagnosticModel(config)
    f,n1,n2=model.farmers[:3]
    n1.zone=n2.zone=f.zone
    a=replace(a,zone=f.zone.id)
    n1.provenance={'barley':[a]}; n2.provenance={'barley':[a]}
    f.neighbor_agents=[n1,n2]
    assert model.pools(f)[1]['barley']==[a,a]
    model.cfg.deduplicate=True
    assert model.pools(f)[1]['barley']==[a]


def test_context_filter_and_ultimate_source():
    model=DiagnosticModel(Config(n_agents=6))
    a,b=list(model.zones.values())[:2]
    assert compatible(a,a,'same_zone')
    assert not compatible(a,b,'same_zone')
    assert compatible(a,b,'unrestricted')
    from copy import deepcopy
    b=deepcopy(a); b.id='OTHER'
    assert compatible(a,b,'ecological')
    b.climate_profile['annual_summary']['T2M_annual_mean']['mean']+=3.01
    assert not compatible(a,b,'ecological')
    with pytest.raises(ValueError): compatible(a,b,'invalid')


def test_profit_normalization_only():
    a=DiagnosticModel(Config(n_agents=12,social_information_enabled=True))
    b=DiagnosticModel(Config(n_agents=12,social_information_enabled=True,profit_per_ha=True))
    a.step();b.step()
    assert a.records==b.records
    for zid,z in b.zones.items():
        for crop,obs in b.zone_observations[zid].items():
            assert z.shared_crop_profit[crop]==sum(o.profit/o.land for o in obs)/len(obs)
            assert a.zones[zid].shared_crop_profit[crop]==sum(o.profit for o in obs)/len(obs)


@pytest.mark.parametrize('changes',[{'deduplicate':True},{'own_memory_only':True},{'profit_per_ha':True},
    {'context_filter':'unrestricted'},{'context_filter':'ecological'},{'zone_yield_fraction':0},
    {'shared_strategy':'zone'},{'shared_strategy':'neighbor'}])
def test_intervention_first_season_and_exogenous_pairing(changes):
    cfg=Config(n_agents=12,n_seasons=3,social_information_enabled=True)
    a,da=run_sim(cfg);b,db=run_sim(replace(cfg,**changes))
    pd.testing.assert_frame_equal(da[da.season==1],db[db.season==1],check_exact=True)
    assert a.weather_history==b.weather_history
    assert list(a.graph.edges)==list(b.graph.edges)
    assert [f.cost_noise_factor for f in a.farmers]==[f.cost_noise_factor for f in b.farmers]


def test_exploration_streams_and_replay():
    cfg=Config(n_agents=12,n_seasons=4,epsilon=.2)
    a,da=run_sim(cfg);b,db=run_sim(cfg)
    pd.testing.assert_frame_equal(da,db,check_exact=True)
    assert a.traces==b.traces
    c,_=run_sim(replace(cfg,epsilon=.05))
    high={(t['agent'],t['season']) for t in a.traces if t['explored']}
    low={(t['agent'],t['season']) for t in c.traces if t['explored']}
    assert low<=high
    assert a.weather_history==c.weather_history
    with pytest.raises(ValueError): DiagnosticModel(replace(cfg,social_information_enabled=True))

@pytest.mark.parametrize('arm,information,economics',[('A',False,False),('B',True,False),('C',False,True),('D',True,True)])
def test_committed_exp001_seed_zero_reproduction(arm,information,economics):
    from experiments.exp001.analysis import summarize
    cfg=Config(n_agents=100,n_seasons=30,random_seed=0,social_information_enabled=information,
               cooperative_economics_enabled=economics)
    _,raw=run_sim(cfg,False);raw.insert(1,'condition',arm)
    _,actual=summarize(raw)
    path=Path(__file__).resolve().parents[2]/'exp001/results/primary/seed_summary.csv'
    expected=pd.read_csv(path,float_precision='round_trip')
    expected=expected[(expected.seed==0)&(expected.condition==arm)].reset_index(drop=True)
    pd.testing.assert_frame_equal(actual,expected,check_exact=True)
