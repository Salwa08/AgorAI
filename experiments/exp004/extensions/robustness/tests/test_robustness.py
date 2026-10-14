from dataclasses import replace
import inspect
import csv
import json
import numpy as np
import pytest
from scipy.stats import multivariate_normal
from experiments.exp004.environment import Config as OriginalConfig,generate as original_generate
from experiments.exp004.policies import Message,decide,central_decisions
from experiments.exp004.extensions.robustness import environment as e,policies as p,runner


def fixture(m=3,rho=.5):
    cfg=e.Config(agents=6,rounds=3,seeds=(90,))
    pop=e.population(cfg,90)
    return cfg,pop,e.generate(cfg,90,0,rho,m,pop)


@pytest.mark.parametrize('rho',[0,.25,.5,.75,1])
def test_marginal_covariance_and_latent_stream_formula(rho):
    g=e.rng(90,10,0).normal(size=(3,3));h=e.rng(90,11,0).normal(size=(3,3,3))
    assert np.array_equal(e.latent(90,0,rho,3,3,3),np.sqrt(1-rho**2)*g[None]+rho*h)
    r=np.random.default_rng(918273);g=r.normal(size=(100000,1));h=r.normal(size=(100000,3))
    x=np.sqrt(1-rho**2)*g+rho*h
    assert np.allclose(x.var(axis=0),1,atol=.02)
    assert np.cov(x.T)[0,1]==pytest.approx(1-rho**2,abs=.02)


@pytest.mark.parametrize('rho',[0,.25,.5,.75,1])
def test_posterior_against_observation_level_conditioning(rho):
    cfg,pop,w=fixture()
    messages=[v.own[0] for v in w.views]
    prec,weighted,_=p.compress(messages,90,0,3,3,3)
    means,var,ll=p.gaussian_grid(prec,weighted,[rho])
    cov=rho**2*np.eye(3)+(1-rho**2)*np.ones((3,3))
    for a in range(3):
        selected=[m for m in messages if m.action==a]
        if not selected:
            assert np.array_equal(means[0,:,a],np.zeros((3,3)))
            continue
        cs=np.array([m.context for m in selected]);y=np.array([m.outcomes for m in selected])
        s=cov[np.ix_(cs,cs)]+np.diag([m.variance for m in selected])
        cross=cov[:,cs]
        direct=cross@np.linalg.inv(s)@y
        variance=np.diag(cov-cross@np.linalg.inv(s)@cross.T)
        assert np.allclose(means[0,:,a],direct,atol=1e-11)
        assert np.allclose(var[0,:,a],variance,atol=1e-11)


def test_compressed_likelihood_differences_match_full_gaussian():
    cfg,pop,w=fixture()
    messages=[m for v in w.views for m in v.own]
    prec,weighted,_=p.compress(messages,90,0,3,3,3)
    rhos=[0,.4,1];_,_,ll=p.gaussian_grid(prec,weighted,rhos)
    direct=[]
    for rho in rhos:
        cov=rho**2*np.eye(3)+(1-rho**2)*np.ones((3,3));value=0.
        for a in range(3):
            ms=[m for m in messages if m.action==a];cs=[m.context for m in ms]
            s=cov[np.ix_(cs,cs)]+np.diag([m.variance for m in ms])
            y=np.array([m.outcomes for m in ms])
            value+=sum(multivariate_normal.logpdf(y[:,d],mean=np.zeros(len(ms)),cov=s) for d in range(3))
        direct.append(value)
    assert np.allclose(ll-ll[0],np.array(direct)-direct[0],atol=1e-10)


@pytest.mark.parametrize('rho',[0,1])
def test_limits_and_original_sparse_parity(rho):
    cfg,pop,w=fixture(m=1,rho=rho)
    orig=original_generate(OriginalConfig(agents=6),90,0,'S1' if rho==0 else 'S2',.5,pop)
    assert w.views==orig.views and np.array_equal(w.expected,orig.expected)
    result=p.decide_panel(w.views,w.focal,3,3,rho)
    target='B1' if rho==0 else 'B2'
    assert np.array_equal(result.actions['H_known'],result.actions[target])
    for i,v in enumerate(w.views):
        peer=tuple(m for j,other in enumerate(w.views) if j!=i for m in other.own)
        for name in ('B0','B1','B2'):
            assert result.actions[name][i]==decide(replace(v,peers=peer),name).action
    assert result.actions['B3'].tolist()==[d.action for d in central_decisions(w.views)]


def test_nested_coverage_and_equal_focal_budgets():
    cfg,pop,sparse=fixture(1);full=e.generate(cfg,90,0,.5,3,pop)
    assert np.array_equal(sparse.expected,full.expected) and np.array_equal(sparse.realized,full.realized)
    distributed=[m for v in full.views for m in v.own]
    for i,v in enumerate(full.views):
        assert v.own[:1]==sparse.views[i].own
        assert {m.action for m in v.own}=={0,1,2}
        focal=full.focal[i].own
        assert len(focal)==len(distributed)==cfg.agents*3
        for d,l in zip(distributed,focal):
            assert d.identity==l.identity and d.action==l.action and d.variance==l.variance
            assert l.context==v.context
            donor=d.identity[2]
            assert np.allclose(np.asarray(d.outcomes)-full.expected[donor,d.action],
                               np.asarray(l.outcomes)-full.expected[i,l.action])
        assert all(m in focal for m in v.own)


def test_known_parameter_only_affects_known_diagnostic():
    cfg,pop,w=fixture()
    a=p.decide_panel(w.views,w.focal,3,3,0)
    b=p.decide_panel(w.views,w.focal,3,3,1)
    for name in ('B0','B1','B2','B3','H_fit','L_budget'):
        assert np.array_equal(a.actions[name],b.actions[name])
    assert a.rho_selected==b.rho_selected
    assert set(inspect.signature(p.deployable).parameters)=={'views','contexts','actions'}
    assert 'from .environment' not in inspect.getsource(p)


def test_hidden_outcome_perturbation_no_fit_leakage(monkeypatch):
    cfg=e.Config(agents=6,rounds=2,seeds=(90,))
    _,a,estimate,_=runner.run_world(cfg,90,.5,3)
    original=runner.generate
    def changed(*args):
        w=original(*args);return replace(w,expected=w.expected+100,realized=w.realized-100)
    monkeypatch.setattr(runner,'generate',changed)
    _,b,estimate2,_=runner.run_world(cfg,90,.5,3)
    assert np.array_equal(estimate,estimate2)
    for name in p.POLICIES:
        assert np.array_equal(a[name]['action'],b[name]['action'])
        assert np.allclose(a[name]['utility']+100,b[name]['utility'])


def test_replay_and_packet_costs():
    cfg=e.Config(agents=6,rounds=2,seeds=(90,))
    _,a,est,h=runner.run_world(cfg,90,.75,3)
    _,b,est2,h2=runner.run_world(cfg,90,.75,3)
    assert h==h2 and np.array_equal(est,est2)
    for name in p.POLICIES:
        for key in a[name]:assert np.array_equal(a[name][key],b[name][key])
    assert np.all(a['B0']['volume']==0)
    assert np.all(a['B1']['volume']==15)
    assert np.all(a['B2']['volume']==3)
    assert np.all(a['B3']['volume']==4)
    assert np.all(a['H_fit']['volume']==4)
    assert np.all(a['H_known']['volume']==4)
    assert np.all(a['L_budget']['evidence']==18)
    assert np.allclose(a['H_fit']['regret']-a['B0']['regret'],-a['H_fit']['utility']+a['B0']['utility'])


def test_deduplication_scope_conflicts_and_no_observations():
    m=Message((90,0,0,0),0,0,(1.,2.,3.),1.)
    a,b,used=p.compress([m,m],90,0,3,3,3)
    assert len(used)==1 and a.sum()==1
    with pytest.raises(ValueError):p.compress([m,replace(m,outcomes=(0.,0.,0.))],90,0,3,3,3)
    with pytest.raises(ValueError):p.compress([m],90,1,3,3,3)
    means,var,ll=p.gaussian_grid(np.zeros((3,3)),np.zeros((3,3,3)),[0,.5,1])
    assert np.all(means==0) and np.all(var==1) and np.all(ll==0)
    means,_,_=p.gaussian_grid(a,b,[0,1])
    assert means[0,1,0,0]>0 and means[1,1,0,0]==0


def test_confirmation_set_cannot_be_executed():
    with pytest.raises(ValueError,match='untouched'):e.Config(seeds=(200,))
    assert not set(e.Config().seeds)&set(range(20))
    assert not set(e.Config().seeds)&set(e.RESERVED)


def test_small_pipeline(tmp_path):
    output=tmp_path/'smoke'
    runner.execute(e.Config(agents=3,rounds=2,seeds=(90,91),rhos=(0.,1.),coverage=(1,3)),output)
    meta=json.loads((output/'metadata.json').read_text())
    assert meta['source_sha256'] and meta['original_working_file_sha256']
    focal=json.loads((output/'focal.json').read_text())
    assert all(r['n']==2 for r in focal)
    with (output/'focal_seed_metrics.csv').open(newline='') as stream:
        for row in csv.DictReader(stream):
            budget=3*int(row['coverage'])
            assert int(row['acquired_each_side'])==budget
            assert int(row['shared_focal_packets'])==budget+1
            assert float(row['local_minus_shared_net'])-float(row['local_minus_shared_utility'])==pytest.approx(float(row['cost'])*(budget+1))
    assert json.loads((output/'confirmation.json').read_text())['status']=='RESERVED_NOT_EXECUTED'
