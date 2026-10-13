# EXP004: independent collective-knowledge benchmark

This experiment branches from main and imports no V1, EXP001 or EXP002 code/data. Read PROTOCOL.md (committed before implementation), RESULTS.md and LIMITATIONS.md. EXP003 is not required or implemented.

## Reproduce from repository root

Tested on Python 3.12.4; only NumPy/SciPy are runtime dependencies. Use a dedicated environment if desired.

```powershell
python -m pip install -r experiments/exp004/requirements.txt
python -m pytest experiments/exp004/tests -q
python -m experiments.exp004.runner --config experiments/exp004/configs/smoke.json --output experiments/exp004/results/replay/smoke
python -m experiments.exp004.runner --config experiments/exp004/configs/pilot.json --output experiments/exp004/results/replay/pilot
python -m experiments.exp004.report --results experiments/exp004/results/replay/pilot
```

Use fresh output directories: the runner refuses to overwrite an existing experiment. Pilot defaults are 20 agents, three actions/dimensions/contexts, 100 rounds, seeds 0–19, three scenarios and two noise levels. Four policies share every evaluation world; three cost levels are postprocessing, not additional independent simulations. Configuration can change these counts, seeds, scenarios and noise/cost settings. No policy optimization uses pilot outcomes.

## Modules and artifacts

- environment.py generates inspectable worlds with separate semantic random streams.
- policies.py accepts immutable evidence-only views, defines all four fixed baselines and transmission accounting; it has no access to latent outcome arrays.
- evaluation.py computes expected/realized utility and regret and seed-level uncertainty.
- runner.py executes the config, saves raw audit evidence, agent/seed summaries and paired contrasts.
- report.py verifies recorded hashes and numerical controls before regenerating RESULTS.md.

Raw compressed message ledgers retain every observation's origin, round, context, action and measurement variance. Raw counterfactual NPZ files retain all action outcomes and choices, enabling paired comparisons. These evaluation arrays must never be passed to deployable policies. Large raw files are ignored by Git. Committed machine-readable summaries include config.json, metadata.json, manifest.json, levels.json, contrasts.json, seed_metrics.csv, paired_seed_metrics.csv and agents.csv. metadata.json records source/output hashes, exact environment, commit and dirty state. Compression headers are not guaranteed byte-identical; decompressed evidence and numerical results are deterministic on the recorded stack.

B3 uses exactly B2's evidence/estimator, so equal decisions are required. Its lower cost in some regimes comes from upload-and-reply topology, not a proven architectural intelligence advantage. Costs are abstract utility units per payload-equivalent; all policies ignore costs when choosing actions because they are fixed communication baselines.

Inference uses independent seed summaries. Agents and rounds are not independent replicates. All intervals are exploratory and unadjusted. Public S0 duplicate evidence deliberately gives no information gain; it is not a realistic universal communication model. No agricultural outcome is modeled.
