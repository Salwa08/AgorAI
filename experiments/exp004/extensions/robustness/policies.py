"""Gaussian partial pooling from evidence only; no environment/evaluator imports."""
from dataclasses import dataclass
from typing import Sequence
import numpy as np
from experiments.exp004.policies import Message, View, unique, posterior, payload_volume

RHO_GRID=np.linspace(0.,1.,21)
POLICIES=('B0','B1','B2','B3','H_known','H_fit','L_budget')


def compress(messages: Sequence[Message], seed: int, round_index: int,
             contexts: int, actions: int, dimensions: int):
    evidence=unique(messages)
    precision=np.zeros((contexts,actions)); weighted=np.zeros((contexts,actions,dimensions))
    for m in evidence:
        if m.identity[:2]!=(seed,round_index):raise ValueError('Evidence outside decision round')
        if not (0<=m.context<contexts and 0<=m.action<actions and len(m.outcomes)==dimensions
                and np.isfinite(m.variance) and m.variance>0 and np.isfinite(m.outcomes).all()):
            raise ValueError('Invalid evidence')
        precision[m.context,m.action]+=1/m.variance
        weighted[m.context,m.action]+=np.asarray(m.outcomes)/m.variance
    return precision,weighted,evidence


def gaussian_grid(precision: np.ndarray, weighted: np.ndarray, rhos: Sequence[float]):
    """Exact posterior and marginal log likelihood, batched over declared rho values."""
    c,k=precision.shape;d=weighted.shape[-1]
    rhos=np.asarray(rhos,dtype=float)
    if not np.isfinite(rhos).all() or ((rhos<0)|(rhos>1)).any():raise ValueError('Invalid model rho')
    r2=rhos**2
    cov=r2[:,None,None]*np.eye(c)[None]+(1-r2[:,None,None])*np.ones((1,c,c))
    means=np.zeros((len(rhos),c,k,d));variances=np.ones((len(rhos),c,k));loglik=np.zeros(len(rhos))
    for action in range(k):
        obs=np.flatnonzero(precision[:,action]>0)
        if not len(obs):continue
        z=weighted[obs,action]/precision[obs,action,None]
        cross=cov[:,:,obs]
        s=cov[:,obs[:,None],obs]+np.diag(1/precision[obs,action])[None]
        sign,logdet=np.linalg.slogdet(s)
        if not (sign>0).all():raise ValueError('Non-positive evidence covariance')
        solved=np.linalg.solve(s,np.broadcast_to(z,(len(rhos),*z.shape)))
        means[:,:,action]=cross@solved
        reduction=cross@np.linalg.solve(s,cross.transpose(0,2,1))
        variances[:,:,action]=np.diagonal(cov-reduction,axis1=1,axis2=2)
        loglik-=.5*(d*logdet+np.einsum('od,god->g',z,solved))
    return means,variances,loglik


@dataclass(frozen=True)
class Decisions:
    actions: dict[str,np.ndarray]
    volumes: dict[str,np.ndarray]
    evidence_counts: dict[str,np.ndarray]
    rho_selected: float


def choose(means: np.ndarray, weights: np.ndarray) -> np.ndarray:
    return np.einsum('nkd,nd->nk',means,weights).argmax(axis=1)


def deployable(views: Sequence[View], contexts: int, actions: int):
    """No true rho or latent/evaluation inputs. Returns predictions and sufficient evidence."""
    n=len(views);d=len(views[0].weights)
    weights=np.asarray([v.weights for v in views]);cs=np.array([v.context for v in views])
    if not (np.isfinite(weights).all() and (weights>=0).all() and np.allclose(weights.sum(axis=1),1)):
        raise ValueError('Invalid preferences')
    if any((v.seed,v.round)!=(views[0].seed,views[0].round) for v in views):raise ValueError('Mixed rounds')
    all_messages=tuple(m for v in views for m in v.own)
    precision,weighted,evidence=compress(all_messages,views[0].seed,views[0].round,contexts,actions,d)
    local=np.stack([posterior(v.own,actions,d)[0] for v in views])
    pooled=np.repeat(posterior(evidence,actions,d)[0][None],n,axis=0)
    by_context=np.stack([posterior(tuple(m for m in evidence if m.context==c),actions,d)[0] for c in range(contexts)])
    grid_means,_,ll=gaussian_grid(precision,weighted,RHO_GRID)
    selected=int(np.argmax(ll))
    predictions={'B0':local,'B1':pooled,'B2':by_context[cs],
                 'B3':by_context[cs].copy(),'H_fit':grid_means[selected,cs]}
    decisions={name:choose(pred,weights) for name,pred in predictions.items()}
    counts={'B0':np.array([len(unique(v.own)) for v in views]),'B1':np.full(n,len(evidence)),
            'B2':np.array([sum(m.context==v.context for m in evidence) for v in views])}
    counts['B3']=counts['B2'].copy();counts['H_fit']=counts['B1'].copy()
    return decisions,counts,float(RHO_GRID[selected]),precision,weighted


def decide_panel(views: Sequence[View], focal_views: Sequence[View], contexts: int,
                 actions: int, declared_rho: float) -> Decisions:
    # Only the diagnostic receives declared_rho; all practical decisions are already made.
    decisions,counts,selected,precision,weighted=deployable(views,contexts,actions)
    weights=np.asarray([v.weights for v in views]);cs=np.array([v.context for v in views])
    known,_,_=gaussian_grid(precision,weighted,[declared_rho])
    decisions['H_known']=choose(known[0,cs],weights)
    local_budget=np.stack([posterior(v.own,actions,len(v.weights))[0] for v in focal_views])
    decisions['L_budget']=choose(local_budget,weights)
    counts['H_known']=counts['B1'].copy();counts['L_budget']=np.array([len(unique(v.own)) for v in focal_views])
    volumes={p:payload_volume(p,views) for p in ('B0','B1','B2','B3')}
    volumes.update(H_known=volumes['B3'].copy(),H_fit=volumes['B3'].copy(),L_budget=np.zeros(len(views)))
    return Decisions(decisions,volumes,counts,selected)
