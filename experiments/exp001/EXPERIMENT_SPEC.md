# EXP001 — Social-information × cooperative-economics factorial ablation

Status: **protocol / implementation pending**. No findings claimed.

## Aim
Disentangle the effects of social information from cooperative economic benefits in the original FarmSwarm comparison (SHARED vs INDIVIDUAL). Preserve the V1 implementation on `main`.

## Initial code audit
- Source of truth: `simulation.ipynb` (Mesa model / `SIM_CONFIG` / `run_sim`).
- `dashboard_solara.py` is presentation, not experiment orchestration.
- `data/` holds fixed crop, zone, climate and moisture inputs.
- README documents current SHARED economics: +20% price premium, 30% cost reduction and 5% vs 15% post-harvest loss. These are scenario assumptions and must not be conflated with information effects.
- Investigate the notebook implementation, not only README descriptions, for hidden SHARED flags and agent initialization differences.

## Treatment matrix
| Condition | Social information (I) | Cooperative economics (E) |
|---|---:|---:|
| A baseline | off | off |
| B information only | on | off |
| C economics only | off | on |
| D combined | on | on |

The same agent population, zones, crop catalog, climate observations and decision rules must apply across conditions, varying **only** the two specified mechanisms. Define clearly how agents get own experience when social information is off and how zone aggregates / neighbor messages are withheld. Economic effects should be explicit switches, not keyed to a SHARED label.

## Implementation work for Codex
1. Audit the complete notebook and config, documenting where SHARED affects knowledge, pricing, costs, losses, social networks and initialization. Flag assumptions that prevent clean manipulation.
2. Extract model execution into importable Python modules as needed; keep the notebook functional and original outputs reproducible. Avoid large unrelated refactors and edits to real data.
3. Add an experiment runner CLI that produces all four conditions for each seed using common random numbers where legitimate; document where stochastic paths cannot be aligned. Do not mix observations between independent treatment runs.
4. Provide config manifest and environment metadata for each run; retain individual/zone/season outcomes. Log outcomes prior to aggregating. Fix experimental seeds in configuration.
5. Implement correctness tests: treatment switches independent, economics equality when E=off, information isolation when I=off, identical exogenous environments for paired comparisons, deterministic replay, no inter-condition leakage.
6. Analysis: report profits, yields, environmental metrics **where actually modeled**, per-zone heterogeneity, harmed-agent fraction, seed-level paired contrasts and uncertainty intervals. Estimate factorial information effect, economic effect, and I×E interaction on the explicitly documented scale; avoid treating correlated seasons and agents as independent replicate experiments.
7. Produce methods/results templates and run instructions. Label generated results as simulation-based; distinguish empirical inputs from calibrated and assumed quantities.
8. Submit as a draft PR for review. Do not merge into main.

## Scientific constraints
- Do **not** tune the model to guarantee positive sharing effects.
- Do not label the V1 profit gain a causal effect of social information.
- Define treatment eligibility: if incentives require cooperative participation, model that dimension explicitly and describe the counterfactual interpretation.
- Start with the smallest verifiable test run before scaling to 100 paired agents × 30 seasons and repeated seeds.
- Keep adaptive partner selection, trust learning and reinforcement learning **out of scope** until this ablation works.
- If source code contradicts README, preserve code evidence, document deviation and request scientific review rather than silently choosing one.

## Acceptance criteria
- One documented command reproduces four-condition outputs for each seed.
- Unit/integration tests pass and no control condition receives unintended social information or cooperative advantages.
- Tables/plots have sample sizes, uncertainties, limitations and complete configuration provenance.
- No V1 source or dataset is overwritten on `main`.
