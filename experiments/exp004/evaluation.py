"""Evaluation-only counterfactual accounting and seed-level inference."""
import numpy as np
from scipy.stats import t


def evaluate(expected, realized, weights, actions):
    expected_u = np.einsum('nad,nd->na', expected, weights)
    realized_u = np.einsum('nad,nd->na', realized, weights)
    index = np.arange(len(actions)), np.asarray(actions)
    return dict(utility=expected_u[index], realized_utility=realized_u[index],
                regret=expected_u.max(axis=1)-expected_u[index],
                realized_regret=realized_u.max(axis=1)-realized_u[index])


def interval(values):
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if not n:
        return dict(n=0, mean=None, low=None, high=None)
    mean = float(x.mean())
    margin = float(t.ppf(.975,n-1)*x.std(ddof=1)/np.sqrt(n)) if n>1 else None
    return dict(n=n, mean=mean, low=mean-margin if margin is not None else None,
                high=mean+margin if margin is not None else None)


def metrics(agent_arrays, baseline, selected, cost):
    u = agent_arrays['utility'][selected]
    net = u - cost * agent_arrays['volume'][selected]
    base = baseline['utility'][selected]
    result = {name: float(values[selected].mean()) for name, values in agent_arrays.items()}
    result.update(net_utility=float(net.mean()), harmed=float(np.mean(u < base-1e-12)),
                  net_harmed=float(np.mean(net < base-1e-12)),
                  q10_utility=float(np.quantile(u,.1)),
                  q10_net_utility=float(np.quantile(net,.1)),
                  communication_cost=float(cost*agent_arrays['volume'][selected].mean()))
    return result
