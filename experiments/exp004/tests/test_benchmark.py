"""Scientific controls, hand calculations, and reproducible pipeline checks."""
from dataclasses import fields, replace
import ast
import json
from pathlib import Path
import numpy as np
import pytest
from experiments.exp004.environment import Config, population, generate, World
from experiments.exp004.policies import Message, View, decide, posterior, central_decisions, payload_volume
from experiments.exp004.evaluation import evaluate, metrics, interval
from experiments.exp004 import runner


def message(origin=0, action=0, outcomes=(1.,0.,0.), context=0, variance=1.):
    return Message((0,0,origin,0),context,action,outcomes,variance)


def view(own=(), peers=(), context=0, weights=(1.,0.,0.)):
    return View(0,0,context,weights,tuple(own),tuple(peers))


def test_conjugate_update_and_provenance():
    a=message();b=message(origin=1)
    means,var,used=posterior([a,a,b],3,3)
    assert means[0,0]==pytest.approx(2/3)
    assert var.tolist()==pytest.approx([1/3,1,1])
    assert len(used)==2
    with pytest.raises(ValueError,match='Conflicting'):
        posterior([a,replace(a,outcomes=(2.,0.,0.))],3,3)


@pytest.mark.parametrize('policy',runner.POLICIES)
def test_zero_observations_and_ties(policy):
    decision=decide(view(),policy)
    assert decision.action==0 and not decision.used
    assert np.array_equal(decision.variances,np.ones(3))


def test_agent_objectives_respected():
    evidence=[message(action=0,outcomes=(5.,0.,0.)),message(origin=1,action=1,outcomes=(0.,5.,0.))]
    assert decide(view(evidence,weights=(1.,0.,0.)),'B1').action==0
    assert decide(view(evidence,weights=(0.,1.,0.)),'B1').action==1
    decisions=central_decisions([view(evidence),view(evidence,weights=(0.,1.,0.))])
    assert [d.action for d in decisions]==[0,1]


def test_information_api_has_no_hidden_state():
    assert {f.name for f in fields(View)}=={'seed','round','context','weights','own','peers'}
    source=Path('experiments/exp004/policies.py').read_text()
    imports=[n.module for n in ast.walk(ast.parse(source)) if isinstance(n,ast.ImportFrom)]
    assert not any(x and ('environment' in x or 'evaluation' in x) for x in imports)
    with pytest.raises(TypeError): View(0,0,0,(1.,0.,0.),(),expected=np.zeros(3))


def test_local_invariant_to_irrelevant_or_invalid_peers():
    own=message()
    invalid=replace(message(1,1,(100.,0.,0.)),identity=(0,99,1,0))
    assert decide(view([own],[invalid]),'B0').action==decide(view([own]),'B0').action
    with pytest.raises(ValueError,match='outside'):
        decide(view([own],[invalid]),'B1')


def test_incompatible_contexts_and_central_parity():
    v0=view([message()],context=0)
    v1=view([message(1,1,(100.,0.,0.),context=1)],context=1)
    assert decide(replace(v0,peers=v1.own),'B1').action==1
    assert decide(replace(v0,peers=v1.own),'B2').action==0
    central=central_decisions([v0,v1])
    assert central[0].action==0 and central[1].action==1
    assert central[0].used==(message().identity,)


def test_cost_hand_calculation_including_duplicate_traffic():
    views=[view([message()]),view([message(1)],context=0),view([message(2,context=1)],context=1)]
    assert payload_volume('B0',views).tolist()==[0,0,0]
    assert payload_volume('B1',views).tolist()==[2,2,2]
    assert payload_volume('B2',views).tolist()==[1,1,0]
    assert payload_volume('B3',views).tolist()==[2,2,2]
    assert payload_volume('B1',[views[0],views[0]]).tolist()==[1,1]
    data=dict(utility=np.array([2.,4.]),volume=np.array([3.,3.]))
    m=metrics(data,dict(utility=np.array([2.,3.])),np.array([True,True]),.5)
    assert m['net_utility']==1.5 and m['communication_cost']==1.5
    assert m['harmed']==0 and m['net_harmed']==1


def test_regret_expected_and_realized_by_hand():
    expected=np.array([[[1,2,3],[3,1,0],[0,0,0]]],dtype=float)
    realized=expected.copy();realized[0,2]=10
    out=evaluate(expected,realized,np.array([[1.,0.,0.]]),[0])
    assert out['utility'][0]==1 and out['regret'][0]==2
    assert out['realized_regret'][0]==9


def test_seed_interval_not_pseudoreplication():
    result=interval([1,2,3])
    assert result['n']==3 and result['mean']==2
    assert result['low']==pytest.approx(2-4.3026527299/np.sqrt(3))
    assert interval([1])['low'] is None
    rows=[dict(seed=s,policy='B',utility=x) for s,x in enumerate([1,2,3])]
    assert runner.summarize(rows,['policy'])[0]['n']==3


@pytest.mark.parametrize('scenario',['S0','S1','S2'])
def test_replay_pairing_and_exact_architecture_control(scenario):
    cfg=Config(agents=6,rounds=4,seeds=(0,))
    p,a,h=runner.run_world(cfg,0,scenario,.5)
    _,b,h2=runner.run_world(cfg,0,scenario,.5)
    assert h==h2
    for policy in runner.POLICIES:
        for key in a[policy]: assert np.array_equal(a[policy][key],b[policy][key])
    assert np.array_equal(a['B2']['action'],a['B3']['action'])
    # Paired regret difference equals negative utility difference, same oracle.
    assert np.allclose(a['B1']['regret']-a['B0']['regret'],-a['B1']['utility']+a['B0']['utility'])
    if scenario=='S0':
        for policy in runner.POLICIES:
            assert np.array_equal(a[policy]['utility'],a['B0']['utility'])
            assert np.array_equal(a[policy]['unique_evidence'],np.full((4,6),3))


def test_no_test_outcomes_in_policy_fit(monkeypatch):
    cfg=Config(agents=6,rounds=3,seeds=(0,))
    _,original,_=runner.run_world(cfg,0,'S2',.5)
    generate_original=runner.generate
    def perturb(*args):
        world=generate_original(*args)
        return World(world.views,world.expected+100,world.realized-100)
    monkeypatch.setattr(runner,'generate',perturb)
    _,changed,_=runner.run_world(cfg,0,'S2',.5)
    for policy in runner.POLICIES:
        assert np.array_equal(original[policy]['action'],changed[policy]['action'])
        assert np.allclose(changed[policy]['utility'],original[policy]['utility']+100)


def test_observation_scope_and_matching_across_sensitivities():
    cfg=Config();pop=population(cfg,3)
    a=generate(cfg,3,2,'S1',.5,pop);b=generate(cfg,3,2,'S1',1.5,pop)
    assert np.array_equal(a.expected,b.expected) and np.array_equal(a.realized,b.realized)
    for i,(v,w) in enumerate(zip(a.views,b.views)):
        m,n=v.own[0],w.own[0]
        assert m.identity==n.identity==(3,2,i,0) and m.action==n.action
        assert np.allclose(np.asarray(n.outcomes)-b.expected[i,n.action],3*(np.asarray(m.outcomes)-a.expected[i,m.action]))


def test_high_noise_reverts_toward_prior_and_identical_agents_agree():
    m=message(variance=1e12)
    d=decide(view([m]),'B0')
    assert np.max(np.abs(d.means))<1e-10 and np.allclose(d.variances,1)
    a,b=central_decisions([view([m]),view([m])])
    assert a.action==b.action and np.array_equal(a.means,b.means)


def test_correct_information_value_with_different_preferences():
    # Integrated Gaussian-prior experiment, not per-realization dominance.
    rng=np.random.default_rng(93711);n=30000
    mu=rng.normal(size=(n,3,3));e1=rng.normal(size=mu.shape);e2=rng.normal(size=mu.shape)
    local=(mu+e1)/2;pooled=(2*mu+e1+e2)/3
    for weights in ([1.,0.,0.],[0.,1.,0.],[.1,.2,.7]):
        truth=mu@weights
        a=(local@weights).argmax(axis=1);b=(pooled@weights).argmax(axis=1)
        gain=truth[np.arange(n),b]-truth[np.arange(n),a]
        assert gain.mean() > -3*gain.std(ddof=1)/np.sqrt(n)
        assert gain.mean()>0  # large deterministic Monte Carlo check


@pytest.mark.parametrize('kwargs',[dict(agents=0),dict(noise=[0]),dict(costs=[-1]),dict(seeds=[1,1]),dict(scenarios=['bad'])])
def test_invalid_configs(kwargs):
    with pytest.raises(ValueError):Config(**kwargs)


def test_runner_artifacts(tmp_path):
    cfg=Config(agents=3,rounds=2,seeds=(0,1),scenarios=('S0',),noise=(.5,),costs=(0.,))
    output=tmp_path/'run';runner.execute(cfg,output)
    metadata=json.loads((output/'metadata.json').read_text())
    assert metadata['source_sha256'] and metadata['output_sha256']
    rows=json.loads((output/'levels.json').read_text())
    assert all(r['n']<=2 for r in rows)
    with pytest.raises(FileExistsError):runner.execute(cfg,output)
