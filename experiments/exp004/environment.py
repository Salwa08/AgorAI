"""Inspectable synthetic worlds; latent arrays are evaluation-only."""
from dataclasses import dataclass
import numpy as np
from .policies import Message, View


@dataclass(frozen=True)
class Config:
    agents: int = 20
    actions: int = 3
    dimensions: int = 3
    contexts: int = 3
    rounds: int = 100
    seeds: tuple[int, ...] = tuple(range(20))
    scenarios: tuple[str, ...] = ('S1', 'S2', 'S0')
    noise: tuple[float, ...] = (.5, 1.5)
    costs: tuple[float, ...] = (0., .01, .1)
    evaluation_noise: float = .2

    def __post_init__(self):
        for name in ('agents', 'actions', 'dimensions', 'contexts', 'rounds'):
            if not isinstance(getattr(self, name), int) or getattr(self, name) < 1:
                raise ValueError('Positive integer sizes required')
        if not self.seeds or len(set(self.seeds)) != len(self.seeds) or any(s < 0 for s in self.seeds):
            raise ValueError('Unique nonnegative seeds required')
        if not self.scenarios or len(set(self.scenarios)) != len(self.scenarios) or set(self.scenarios) - {'S0','S1','S2'}:
            raise ValueError('Unknown or duplicate scenarios')
        if not self.noise or any(not np.isfinite(x) or x <= 0 for x in self.noise):
            raise ValueError('Positive noise required')
        if not self.costs or any(not np.isfinite(x) or x < 0 for x in self.costs):
            raise ValueError('Nonnegative costs required')
        if not np.isfinite(self.evaluation_noise) or self.evaluation_noise < 0:
            raise ValueError('Invalid evaluation noise')


def rng(seed: int, stream: int, round_index: int = 0):
    return np.random.default_rng(np.random.SeedSequence([seed, stream, round_index]))


@dataclass(frozen=True)
class Population:
    contexts: np.ndarray
    weights: np.ndarray
    quality: np.ndarray


def population(config: Config, seed: int) -> Population:
    return Population(rng(seed, 1).permutation(np.arange(config.agents) % config.contexts),
                      rng(seed, 2).dirichlet(np.ones(config.dimensions), config.agents),
                      rng(seed, 3).permutation(np.resize([.5, 1.5], config.agents)))


@dataclass(frozen=True)
class World:
    views: tuple[View, ...]
    expected: np.ndarray  # agent, action, dimension -- NEVER sent to policy
    realized: np.ndarray


def generate(config: Config, seed: int, t: int, scenario: str, noise: float,
             pop: Population) -> World:
    if scenario not in ('S0','S1','S2'):
        raise ValueError('Unknown scenario')
    common = rng(seed, 10, t).normal(size=(config.actions, config.dimensions))
    contextual = rng(seed, 11, t).normal(size=(config.contexts, config.actions, config.dimensions))
    expected = contextual[pop.contexts] if scenario == 'S2' else np.repeat(common[None], config.agents, axis=0)
    realized = expected + config.evaluation_noise * rng(seed, 12, t).normal(size=expected.shape)
    choices = rng(seed, 13, t).integers(config.actions, size=config.agents)
    errors = rng(seed, 14, t).normal(size=(config.agents, config.dimensions))
    public_errors = rng(seed, 15, t).normal(size=common.shape)
    public = tuple(Message((seed,t,-1,a), -1, a, tuple(common[a] + noise*public_errors[a]), noise**2)
                   for a in range(config.actions))
    views = []
    for i in range(config.agents):
        a = int(choices[i]); scale = noise * pop.quality[i]
        own = public if scenario == 'S0' else (Message((seed,t,i,0), int(pop.contexts[i]), a,
                tuple(expected[i,a] + scale*errors[i]), float(scale**2)),)
        views.append(View(seed, t, int(pop.contexts[i]), tuple(pop.weights[i]), own))
    return World(tuple(views), expected, realized)
