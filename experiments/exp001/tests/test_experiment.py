import json
import os
from dataclasses import replace
from pathlib import Path
import random
import subprocess
import sys
import numpy as np
import pandas as pd
import pytest
from experiments.exp001 import model as m
from experiments.exp001.analysis import METRICS, factorial, interval, summarize, paired_harm
from experiments.exp001.runner import CONDITIONS, execute


def cfg(**kwargs):
    return m.SIM_CONFIG(**dict(n_agents=12,n_seasons=4,**kwargs))


@pytest.mark.parametrize('information,economics', CONDITIONS.values())
def test_economic_equations(information,economics):
    config=cfg(social_information_enabled=information,cooperative_economics_enabled=economics)
    model=m.FarmModel(config)
    farmer=model.farmers[0]
    farmer.chosen_crop=farmer.zone.viable_crops[0]
    farmer.land_size=3
    farmer.cost_noise_factor=.1
    farmer.irrigation_level=.9
    crop=m.crops_data['crops'][farmer.chosen_crop]
    cost=m.crops_data['cost_model']; cat=crop['cost_category']
    # Independent formula, including the preserved V1 fallback water need.
    raw=(crop['labor_days_per_ha']*cost['smag_mad_per_day']+
         cost['fertilizer_npk_mad_per_ha'][cat]+cost['seeds_mad_per_ha'][cat]+
         cost['mechanization_mad_per_ha'][cat]+500*farmer.zone.raw_zone_data['water_price']*10)*1.1
    farmer.harvest({farmer.zone.id:'normal'},config)
    factor=.8 if economics else .9
    price=crop['faostat_price_mad_per_ton']*(1.1 if economics else 1)
    loss=.06 if economics else .12
    assert farmer.cost_per_ha == pytest.approx(raw*factor)
    assert farmer.profit == pytest.approx((farmer.yield_t_ha*(1-loss)*price-raw*factor)*3)
    assert farmer.water_use_mm == 450


@pytest.mark.parametrize('economics',[False,True])
def test_control_never_receives_or_publishes(economics):
    model, frame=m.run_sim(cfg(cooperative_economics_enabled=economics))
    assert all(not z.shared_crop_yield and not z.shared_crop_profit for z in model.zones.values())
    assert all(sum(map(len,f.knowledge_base.values()))==4 for f in model.farmers)
    a,b=model.farmers[:2]
    a.neighbor_agents=[b]
    before=repr(b.knowledge_base)
    m.propagate_knowledge(a,'poison',999,0,0,filter_mode='none')
    assert repr(b.knowledge_base)==before


@pytest.mark.parametrize('economics',[False,True])
def test_control_does_not_read_social_signals(economics):
    class Forbidden:
        def __getattribute__(self,name):
            raise AssertionError('Social source read: '+name)
        def __bool__(self):
            raise AssertionError('Social source accessed')
    config=cfg(cooperative_economics_enabled=economics)
    model=m.FarmModel(config)
    f=model.farmers[0]
    f.decide_crop(config); expected=f.chosen_crop
    f.zone.shared_crop_yield=Forbidden()
    f.zone.shared_crop_profit=Forbidden()
    f.neighbor_agents=Forbidden()
    f.decide_crop(config)
    assert f.chosen_crop==expected


def test_social_information_changes_decision_when_enabled():
    config=cfg(social_information_enabled=True,shared_strategy='zone')
    model=m.FarmModel(config); f=model.farmers[0]
    available=f.zone.viable_crops
    f.compute_suitability=lambda crop,cfg: 1.0
    f.zone.shared_crop_yield={available[-1]:10}
    f.zone.shared_crop_profit={available[-1]:1000}
    f.decide_crop(config)
    assert f.chosen_crop==available[-1]
    f.decide_crop(replace(config,social_information_enabled=False))
    assert f.chosen_crop==available[0]


def test_first_season_information_cannot_change_economics_or_crop():
    runs={label:m.run_sim(replace(cfg(),n_seasons=1,social_information_enabled=i,
                                cooperative_economics_enabled=e))[1]
          for label,(i,e) in CONDITIONS.items()}
    pd.testing.assert_frame_equal(runs['A'],runs['B'])
    pd.testing.assert_frame_equal(runs['C'],runs['D'])
    assert runs['A'].crop.equals(runs['C'].crop)
    assert runs['A'].yield_t_ha.equals(runs['C'].yield_t_ha)
    assert not runs['A'].profit_mad.equals(runs['C'].profit_mad)


def test_paired_exogenous_population_graph_weather_shocks():
    models=[m.run_sim(replace(cfg(),social_information_enabled=i,cooperative_economics_enabled=e))[0]
            for i,e in CONDITIONS.values()]
    for model in models[1:]:
        assert model.weather_history==models[0].weather_history
        assert sorted(model.graph.edges)==sorted(models[0].graph.edges)
        for a,b in zip(model.farmers,models[0].farmers):
            for name in ['unique_id','land_size','cost_noise_factor','goal_profile','budget','irrigation_type']:
                assert getattr(a,name)==getattr(b,name)
            assert a.zone.id==b.zone.id
            for crop in m.CROP_IDS:
                assert a.compute_suitability(crop,model.cfg)==b.compute_suitability(crop,models[0].cfg)
            for season in range(1,5):
                assert model.stream('harvest',season,a.unique_id).random()==models[0].stream('harvest',season,a.unique_id).random()


def test_replay_interleaving_and_no_global_random_mutation():
    config=cfg(social_information_enabled=True,cooperative_economics_enabled=True)
    state=random.getstate()
    _,expected=m.run_sim(config)
    a=m.FarmModel(config); b=m.FarmModel(replace(config,random_seed=72))
    for _ in range(4):
        a.step(); b.step()
    actual=pd.DataFrame(a.records).sort_values(['season','agent']).reset_index(drop=True)
    pd.testing.assert_frame_equal(expected,actual)
    assert random.getstate()==state
    assert a.zones['ARID'] is not b.zones['ARID']
    assert a.farmers[0].knowledge_base is not b.farmers[0].knowledge_base
    config.shared_weight=999
    assert a.cfg.shared_weight!=999


def test_cross_process_hash_independence():
    code="from experiments.exp001.model import *; import hashlib; _,d=run_sim(SIM_CONFIG(n_agents=6,n_seasons=2,social_information_enabled=True)); print(hashlib.sha256(d.to_csv(index=False).encode()).hexdigest())"
    outputs=[subprocess.check_output([sys.executable,'-c',code],env=dict(os.environ,PYTHONHASHSEED=s),text=True)
             for s in ['1','987']]
    assert outputs[0]==outputs[1]


def test_factorial_and_seed_uncertainty():
    rows=[]
    for seed,i in enumerate([1.,2.,3.]):
        for cond,value in zip('ABCD',[10,10+i,14,14+3*i]):
            rows.append(dict(seed=seed,condition=cond,**{metric:value for metric in METRICS}))
    effects,_=factorial(pd.DataFrame(rows))
    e=effects[effects.metric==METRICS[0]].set_index('effect')
    assert e.loc['information_only','estimate']==2
    assert e.loc['economics_only','estimate']==4
    assert e.loc['interaction','estimate']==4
    assert e.loc['information_main','estimate']==4
    assert e.loc['economics_main','estimate']==6
    assert e.loc['information_only','standard_error']==pytest.approx(1/np.sqrt(3))
    assert e.loc['information_only','ci_low']==pytest.approx(2-4.302652729911275/np.sqrt(3))
    assert interval([2])['ci_low'] is None
    with pytest.raises(ValueError):
        factorial(pd.DataFrame(rows[:-1]))


def test_aggregation_weights_harm_and_replication():
    rows=[]
    for condition in 'ABCD':
        for agent in [0,1]:
            for season in [1,2]:
                profit=10+agent*10
                if condition!='A': profit += -1 if agent==0 else 3
                rows.append(dict(seed=1,condition=condition,agent=agent,season=season,
                                 profit_mad=profit,yield_t_ha=2+agent,profit_mad_ha=profit/(1+agent),
                                 water_proxy_mm=450,production_t=(2+agent)*(1+agent),land_ha=1+agent))
    agents,s=summarize(pd.DataFrame(rows))
    assert s.iloc[0].mean_profit_mad==15
    assert s.iloc[0].median_profit_mad==15
    assert s.iloc[0].productivity_t_ha==pytest.approx(8/3)
    assert (paired_harm(agents).harmed==.5).all()
    effects,_=factorial(s)
    assert (effects.n_seeds==1).all()
    assert effects.ci_low.isna().all()


def test_output_manifest_and_config_validation(tmp_path):
    config={'scenario':'test','seeds':[2],'model':{'n_agents':6,'n_seasons':1}}
    out=execute(config,tmp_path/'run')
    metadata=json.loads((out/'metadata.json').read_text())
    assert metadata['n_agent_season_records']==24
    assert metadata['exogenous_pairing_verified']
    assert len(metadata['input_sha256'])==4
    with pytest.raises(FileExistsError): execute(config,out)
    with pytest.raises(ValueError): execute(dict(config,seeds=[2,2]),tmp_path/'bad')


def test_extracted_equations_match_v1(monkeypatch):
    # Execute definitions only: no notebook experiments or output cells.
    root=Path(m.__file__).resolve().parents[2]
    monkeypatch.chdir(root)
    notebook=json.loads((root/'simulation.ipynb').read_text(encoding='utf-8'))
    ns={}
    exec(''.join(notebook['cells'][0]['source'])+'\n'+''.join(notebook['cells'][1]['source']),ns)
    config=cfg()
    for zid,zone in m.zones_data['zones'].items():
        cp=m.climate_data['zones'][zid]['climate_profile']
        for cid,crop in m.crops_data['crops'].items():
            assert m._get_cost_per_ha(crop,zone,config,.12)==ns['_get_cost_per_ha'](crop,zone,config,.12)
            assert m._get_water_use_mm(crop,.6,config)==ns['_get_water_use_mm'](crop,.6,config)
            for weather in ['normal','drought','wet']:
                monkeypatch.setitem(ns,'random',random.Random(18))
                actual=m.calculate_yield(cid,crop,zone,cp,{'weather_type':weather},rng=random.Random(18))
                expected=ns['calculate_yield'](cid,crop,zone,cp,{'weather_type':weather})
                assert actual==expected

@pytest.mark.parametrize('mode',['zone','neighbor','both'])
def test_neutral_economics_does_not_change_information_paths(mode):
    config=cfg(social_information_enabled=True,shared_strategy=mode,
               shared_price_premium=0,shared_cost_efficiency=.9,shared_post_harvest_loss=.12)
    a,df_a=m.run_sim(config)
    b,df_b=m.run_sim(replace(config,cooperative_economics_enabled=True))
    pd.testing.assert_frame_equal(df_a,df_b,check_dtype=False,check_exact=True)
    assert [f.knowledge_base for f in a.farmers]==[f.knowledge_base for f in b.farmers]


@pytest.mark.parametrize('mode',['zone','neighbor','both'])
def test_control_ignores_graph_and_social_configuration(mode):
    config=cfg(shared_strategy=mode,shared_weight=100,neighbor_weight=100)
    _,a=m.run_sim(config)
    _,b=m.run_sim(replace(config,use_neighbor_graph=False))
    pd.testing.assert_frame_equal(a,b)


def test_labels_do_not_control_treatments():
    config=cfg(social_information_enabled=True,cooperative_economics_enabled=True)
    a=m.FarmModel(config); b=m.FarmModel(config)
    for farmer in b.farmers: farmer.strategy_type='INDIVIDUAL'
    for _ in range(config.n_seasons): a.step(); b.step()
    assert a.records==b.records


def test_readme_sensitivity_economics():
    path=Path(m.__file__).parent/'configs/readme_economics.json'
    spec=json.loads(path.read_text())
    config=m.SIM_CONFIG(**spec['model'])
    assert config.shared_cost_efficiency/config.indiv_cost_efficiency==pytest.approx(.7)
    for economics in [False,True]:
        model=m.FarmModel(replace(config,cooperative_economics_enabled=economics))
        f=model.farmers[0]; f.chosen_crop=f.zone.viable_crops[0]
        f.harvest({f.zone.id:'normal'},model.cfg)
        crop=m.crops_data['crops'][f.chosen_crop]
        raw=m._get_cost_per_ha(crop,f.zone.raw_zone_data,config,f.cost_noise_factor)
        assert f.cost_per_ha==pytest.approx(raw*(.63 if economics else .9))
        assert f.price==pytest.approx(crop['faostat_price_mad_per_ton']*(1.2 if economics else 1))
        assert f.effective_yield==pytest.approx(f.yield_t_ha*(.95 if economics else .85))
