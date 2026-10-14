# EXP004.1 robustness and stronger baselines

This extension is based on EXP004 c871764 and changes only this directory. Original EXP004 results, reports and configuration remain frozen. Protocol commit b1a5fd3 precedes implementation. Read PROTOCOL.md, RESULTS.md and LIMITATIONS.md.

## Reproduce from the repository root

Use Python 3.12.4 and the original EXP004 dependency pins (NumPy 1.26.4, SciPy 1.13.1, pytest 9.0.2).

```powershell
python -m pip install -r experiments/exp004/requirements.txt
python -m pytest experiments/exp004/tests experiments/exp004/extensions/robustness/tests -q
python -m experiments.exp004.extensions.robustness.runner --config experiments/exp004/extensions/robustness/configs/smoke.json --output experiments/exp004/extensions/robustness/results/replay/smoke
python -m experiments.exp004.extensions.robustness.runner --config experiments/exp004/extensions/robustness/configs/exploratory.json --output experiments/exp004/extensions/robustness/results/replay/exploratory
python -m experiments.exp004.extensions.robustness.report --results experiments/exp004/extensions/robustness/results/replay/exploratory
```

Output directories must be new. The full design is 20 agents, three actions/dimensions/contexts, 100 rounds, seeds 100–119, rho 0/.25/.5/.75/1, one or three observations per agent, noise .5, and communication costs 0/.01/.1. Costs do not change actions. Smoke uses seeds 90/91 and three rounds. Confirmation seeds 200–219 are reserved, rejected by the runner, and have not been evaluated.

## Interpretation boundaries

B0/B1/B2/B3 preserve EXP004 estimators. H_known is an oracle-parameter diagnostic with declared true rho, not hidden outcomes. H_fit estimates rho on the fixed 21-point grid using only current observations; it is an empirical-Bayes plug-in estimator, not a new algorithm. Both hierarchical estimators have centralized upload/reply costs. B2 and B3 make identical decisions and differ only in packet accounting.

Main policies all acquire N*m observations system-wide; recipients differ in access. More local coverage changes total acquisition, and is reported as a separate paired contrast. L_budget is a separate focal-agent counterfactual that relocates exactly N*m samples into the focal context while preserving action schedule and measurement precisions. Its equal-budget results must not be interpreted as providing N*m samples to every agent for the original system budget. Focal service costs use N*m+1 packets for one shared-service recipient, separately from main-panel amortized m+1 packets.

## Implementation and evidence

- environment.py generates nested coverage and common random primitives for intermediate rho, with constant marginal variance.
- policies.py implements precision compression, Gaussian conditioning and evidence-only rho selection. It imports no environment or evaluator.
- runner.py evaluates matched worlds, records provenance and raw counterfactuals, and constructs agent/seed summaries and paired contrasts.
- report.py independently verifies saved accounting and hashes, generates the report, and packages compact lossless summaries.

Raw gzip JSONL evidence retains main and separately scoped focal messages. NPZ files retain every action's expected/realized outcome and policy choices. These evaluation arrays must never enter policy fitting. Main seed_metrics, paired_seed_metrics, coverage_effects and focal tables distinguish estimands; rho_estimates records each observation-based selection. Subgroup context and dominant-objective summaries are descriptive and use independent seeds for intervals.

The committed results/exploratory/summary.zip contains every summary, exact configuration, reserved-seed declaration, execution metadata and verification. Inspect it with `python -m zipfile -e experiments/exp004/extensions/robustness/results/exploratory/summary.zip experiments/exp004/extensions/robustness/results/review`. Large raw files remain local and regenerable. Verification/report generation requires a completed run including raw outputs. Container compression timestamps need not match; numerical replay and decompressed contents are deterministic on the recorded stack.

Execution source hashes and original working-file hashes are recorded separately from the downstream report-generator and report hashes. Git verifies original tracked content against c871764. All intervals are exploratory 95% seed-level t intervals without multiplicity adjustment. No confirmation, agricultural validation or algorithmic novelty is claimed.
