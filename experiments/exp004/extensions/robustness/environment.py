"""Nested sensing panels and evaluation-only latent worlds."""
from dataclasses import dataclass
import numpy as np
from experiments.exp004.environment import rng, population, Population
from experiments.exp004.policies import Message, View

RESERVED = tuple(range(200,220))


@dataclass(frozen=True)
class Config:
    agents: int = 20
    actions: int = 3
    dimensions: int = 3
    contexts: int = 3
    rounds: int = 100
    seeds: tuple[int,...] = tuple(range(100,120))
    rhos: tuple[float,...] = (0.,.25,.5,.75,1.)
    coverage: tuple[int,...] = (1,3)
    noise: float = .5
    evaluation_noise: float = .2
    costs: tuple[float,...] = (0.,.01,.1)

    def __post_init__(self):
        for key in ('agents','actions','dimensions','contexts','rounds'):
            if type(getattr(self,key)) is not int or getattr(self,key)<1:
                raise ValueError('Positive integer sizes required')
        if not self.seeds or len(set(self.seeds))!=len(self.seeds) or any(type(s) is not int or s<0 for s in self.seeds):
            raise ValueError('Unique nonnegative integer seeds required')
        if set(self.seeds)&set(RESERVED):raise ValueError('Confirmation seeds remain untouched')
        if not self.rhos or any(not np.isfinite(r) or not 0<=r<=1 for r in self.rhos):raise ValueError('Invalid rho')
        if not self.coverage or any(type(m) is not int or m<1 for m in self.coverage):raise ValueError('Invalid coverage')
        if len(set(self.rhos))!=len(self.rhos) or len(set(self.coverage))!=len(self.coverage):raise ValueError('Duplicate conditions')
        if not np.isfinite(self.noise) or self.noise<=0:raise ValueError('Invalid noise')
        if not np.isfinite(self.evaluation_noise) or self.evaluation_noise<0:raise ValueError('Invalid evaluation noise')
        if not self.costs or any(not np.isfinite(c) or c<0 for c in self.costs):raise ValueError('Invalid costs')


def latent(seed: int, round_index: int, rho: float, contexts: int, actions: int, dimensions: int):
    g=rng(seed,10,round_index).normal(size=(actions,dimensions))
    h=rng(seed,11,round_index).normal(size=(contexts,actions,dimensions))
    return np.sqrt(1-rho*rho)*g[None]+rho*h


@dataclass(frozen=True)
class World:
    views: tuple[View,...]
    focal: tuple[View,...]  # separate counterfactual namespace for EACH recipient
    expected: np.ndarray
    realized: np.ndarray


def generate(cfg: Config, seed: int, t: int, rho: float, m: int, pop: Population) -> World:
    means=latent(seed,t,rho,cfg.contexts,cfg.actions,cfg.dimensions)
    expected=means[pop.contexts]
    realized=expected+cfg.evaluation_noise*rng(seed,12,t).normal(size=expected.shape)
    starts=rng(seed,13,t).integers(cfg.actions,size=cfg.agents)
    # Sample-major storage makes the first observation exactly EXP004-compatible.
    errors=np.stack([rng(seed,14+100*s,t).normal(size=(cfg.agents,cfg.dimensions)) for s in range(m)])
    scale=cfg.noise*pop.quality
    views=[];focal=[]
    for i in range(cfg.agents):
        own=tuple(Message((seed,t,i,s),int(pop.contexts[i]),int((starts[i]+s)%cfg.actions),
                 tuple(expected[i,(starts[i]+s)%cfg.actions]+scale[i]*errors[s,i]),float(scale[i]**2)) for s in range(m))
        views.append(View(seed,t,int(pop.contexts[i]),tuple(pop.weights[i]),own))
        local=tuple(Message((seed,t,j,s),int(pop.contexts[i]),int((starts[j]+s)%cfg.actions),
                   tuple(expected[i,(starts[j]+s)%cfg.actions]+scale[j]*errors[s,j]),float(scale[j]**2))
                   for j in range(cfg.agents) for s in range(m))
        focal.append(View(seed,t,int(pop.contexts[i]),tuple(pop.weights[i]),local))
    return World(tuple(views),tuple(focal),expected,realized)
