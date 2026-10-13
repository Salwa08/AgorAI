"""Deployable evidence-only policies. No environment/evaluation imports."""
from dataclasses import dataclass
from typing import Sequence
import numpy as np


@dataclass(frozen=True)
class Message:
    identity: tuple[int, int, int, int]  # seed, round, origin, sample
    context: int  # -1 public measurement
    action: int
    outcomes: tuple[float, ...]
    variance: float


@dataclass(frozen=True)
class View:
    seed: int
    round: int
    context: int
    weights: tuple[float, ...]
    own: tuple[Message, ...]
    peers: tuple[Message, ...] = ()


@dataclass(frozen=True)
class Decision:
    action: int
    means: np.ndarray
    variances: np.ndarray
    used: tuple[tuple[int, int, int, int], ...]


def unique(messages: Sequence[Message]) -> tuple[Message, ...]:
    seen = {}
    for message in messages:
        if message.identity in seen and seen[message.identity] != message:
            raise ValueError('Conflicting provenance payload')
        seen[message.identity] = message
    return tuple(seen.values())


def posterior(messages: Sequence[Message], actions: int, dimensions: int):
    precision = np.ones(actions)
    weighted = np.zeros((actions, dimensions))
    evidence = unique(messages)
    for m in evidence:
        if not (0 <= m.action < actions and len(m.outcomes) == dimensions
                and np.isfinite(m.variance) and m.variance > 0
                and np.isfinite(m.outcomes).all()):
            raise ValueError('Invalid observation')
        precision[m.action] += 1 / m.variance
        weighted[m.action] += np.asarray(m.outcomes) / m.variance
    return weighted / precision[:, None], 1 / precision, evidence


def decide(view: View, policy: str, actions: int = 3) -> Decision:
    weights = np.asarray(view.weights)
    if not (np.isfinite(weights).all() and (weights >= 0).all()
            and np.isclose(weights.sum(), 1)):
        raise ValueError('Invalid utility weights')
    if policy == 'B0':
        messages = view.own  # peers deliberately never inspected
    elif policy == 'B1':
        messages = view.own + view.peers
    elif policy in ('B2', 'B3'):
        messages = tuple(m for m in view.own + view.peers
                         if m.context in (view.context, -1))
    else:
        raise ValueError('Unknown policy')
    if any(m.identity[:2] != (view.seed, view.round) for m in messages):
        raise ValueError('Evidence outside decision round')
    means, variances, evidence = posterior(messages, actions, len(weights))
    return Decision(int(np.argmax(means @ weights)), means, variances,
                    tuple(m.identity for m in evidence))


def central_decisions(views: Sequence[View], actions: int = 3) -> tuple[Decision, ...]:
    # Uploads only; no caller-supplied peer channel or hidden world.
    uploads = tuple(m for view in views for m in view.own)
    return tuple(decide(View(v.seed, v.round, v.context, v.weights, uploads),
                        'B3', actions) for v in views)


def payload_volume(policy: str, views: Sequence[View]) -> np.ndarray:
    n = len(views)
    if not n:
        return np.array([], dtype=float)
    if policy == 'B0':
        return np.zeros(n)
    if policy == 'B3':
        return np.full(n, sum(len(v.own) for v in views) / n + 1)
    if policy not in ('B1', 'B2'):
        raise ValueError('Unknown policy')
    return np.array([sum(sum(policy == 'B1' or m.context in (v.context, -1)
                              for m in source.own)
                        for j, source in enumerate(views) if i != j)
                     for i, v in enumerate(views)], dtype=float)
