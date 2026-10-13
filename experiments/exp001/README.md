# FarmSwarm Experiment 001

Four independent worlds isolate social information (I) and cooperative economics (E): A off/off, B on/off, C off/on, D on/on. See [AUDIT.md](AUDIT.md) for discrepancies with V1, [METHODOLOGY.md](METHODOLOGY.md) for estimands and [RESULTS.md](RESULTS.md) for completed-run evidence. Original notebook and datasets are unchanged.

## Reproduce

From the repository root, using Python 3.12 (tested version is recorded in output metadata):

```powershell
python -m pip install -r experiments/exp001/requirements-lock.txt
python -m pytest experiments/exp001/tests -q
python -m experiments.exp001.runner --config experiments/exp001/configs/smoke.json --output experiments/exp001/results/replay/smoke
python -m experiments.exp001.runner --config experiments/exp001/configs/primary.json --output experiments/exp001/results/replay/primary
python -m experiments.exp001.runner --config experiments/exp001/configs/readme_economics.json --output experiments/exp001/results/replay/readme_economics
```

The commands above write to a new `results/replay/` tree so the committed evidence is preserved. To regenerate the report after both full runs, execute `python -m experiments.exp001.report --results-root experiments/exp001/results/replay`. The report verifies all raw-output and execution-source hashes before writing RESULTS.md.

Use a **new output directory** on another replay (e.g. results/primary_replay). Existing directories are refused to prevent mixing runs. No network/data download or notebook execution is required. The runner loads four committed data JSON files relative to its module path. NetworkX is required when the graph is enabled; failure cannot silently remove the treatment. The experiment's direct dependency pins avoid the original requirements' incompatible historical Mesa versions. environment-freeze.txt records all installed distribution versions for provenance, not a recommended environment to install wholesale.

## Configuration and importable API

Config JSON has exactly scenario, seeds and model. Edit n_agents, n_seasons, the explicit unique integer seed list, or any other SIM_CONFIG field under model. Runner owns random_seed and treatment switches and rejects their presence under model, ensuring A–D are always run for each seed. Full defaults are recorded in resolved_configs.json. n_agents means farmers **per condition**, all matched across worlds, not V1's combined count across two strategies. At least two farmers and one season are required.

```python
from experiments.exp001.model import SIM_CONFIG, run_sim
model, agent_seasons = run_sim(SIM_CONFIG(
    n_agents=100, n_seasons=30, random_seed=42,
    social_information_enabled=True,
    cooperative_economics_enabled=False,
))
```

Primary config: 100 agents/condition, 30 seasons, seeds [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]. V1 economics: premium .10, shared cost .80, individual cost .90, shared loss .06, individual loss .12. README sensitivity: premium .20, shared cost .63, individual cost .90, losses .05/.15. “30% reduction” is explicitly relative to individual cost (.90 × .70 = .63). All other parameters and seed identities match. Each scenario uses its own A baseline because the individual loss differs.

## Outputs

All files live below the requested results directory. agent_season.csv stores raw farmer outcomes (before aggregation), identity, zone, season, crop, weather, land, gross/effective yield, production, realized costs/price, profit and diagnostic water proxy. agents.csv averages seasons per identity; seasons.csv and zone_seasons.csv summarize temporal outcomes; seed_summary.csv and zone_seed_summary.csv feed inference. effects.csv and zone_effects.csv contain additive paired contrasts, seed SD, SE and 95% t intervals; paired_seed_contrasts.csv retains individual replicates. paired_harm.csv contains seed-level harmed/benefited/unchanged fractions against paired A; harm_summary.csv estimates uncertainty across seeds. condition_summary.csv gives seed-level outcome intervals.

config.json and resolved_configs.json describe every run; exogenous.json records populations, graphs, weather and pairing hashes; metadata.json records UTC execution time, exact command, Python/packages/platform, git state, source/input/output SHA-256 hashes and replication counts. Output CSVs replay deterministically in the recorded environment; timestamps, absolute command paths and git status metadata may differ. Compare output hashes or CSV contents rather than requiring metadata bytes to match.

Large raw outputs and exogenous manifests remain locally generated and are ignored by git. Selected small configs, metadata and summary CSVs are explicitly retained as review evidence. Their metadata includes hashes of the omitted reproducible raw files. No claims of empirical validation or sustainability are made.
