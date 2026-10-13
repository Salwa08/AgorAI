# EXP001 results — simulation evidence

Completed 2026-10-13. Primary and separately requested README-economics sensitivity each use **20 independent seeds × 4 conditions × 100 matched farmers × 30 seasons** (240,000 farmer-season records per scenario). Seed list: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19].

All intervals below are paired-seed or condition-seed **95% Student t intervals**, n=20; agents and seasons are not independent replicates. Profit is MAD/farm/season. Median profit means the median of farmer across-season mean profits, then averaged over seeds. See [METHODOLOGY.md](METHODOLOGY.md) for precise definitions and limitations.

## Primary: executable V1 economics

Premium .10; cost factors .80/.90; post-harvest losses .06/.12.

### Outcomes

| Condition | Mean profit [CI] | Median profit [CI] | Mean yield t/ha [CI] | Area-weighted productivity t/ha [CI] |
| --- | --- | --- | --- | --- |
| A | 76,545.35 [70,608.43, 82,482.27] | 9,813.28 [8,224.33, 11,402.22] | 3.42 [3.16, 3.67] | 3.40 [3.16, 3.64] |
| B | 111,784.07 [105,043.99, 118,524.15] | 43,328.87 [29,910.03, 56,747.71] | 8.42 [7.22, 9.62] | 8.33 [7.14, 9.51] |
| C | 100,755.24 [93,596.85, 107,913.63] | 19,997.37 [17,870.28, 22,124.46] | 3.42 [3.16, 3.67] | 3.40 [3.16, 3.64] |
| D | 143,311.11 [135,258.07, 151,364.16] | 60,439.78 [45,490.35, 75,389.21] | 8.53 [7.28, 9.78] | 8.44 [7.21, 9.66] |


### Paired factorial effects

| Contrast | Mean profit [CI] | Median profit [CI] | Mean yield [CI] | Productivity [CI] |
| --- | --- | --- | --- | --- |
| information_only | 35,238.72 [30,564.32, 39,913.12] | 33,515.59 [20,737.79, 46,293.39] | 5.003 [3.923, 6.082] | 4.924 [3.815, 6.033] |
| economics_only | 24,209.89 [22,972.99, 25,446.79] | 10,184.10 [9,365.33, 11,002.86] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| combined | 66,765.76 [61,479.10, 72,052.42] | 50,626.50 [36,346.25, 64,906.75] | 5.113 [3.982, 6.244] | 5.036 [3.886, 6.185] |
| information_given_economics | 42,555.87 [37,157.56, 47,954.18] | 40,442.40 [26,446.17, 54,438.64] | 5.113 [3.982, 6.244] | 5.036 [3.886, 6.185] |
| economics_given_information | 31,527.04 [30,091.11, 32,962.98] | 17,110.91 [15,116.37, 19,105.45] | 0.110 [0.009, 0.211] | 0.112 [0.007, 0.216] |
| information_main | 38,897.29 [33,868.97, 43,925.62] | 36,979.00 [23,612.47, 50,345.52] | 5.058 [3.953, 6.162] | 4.980 [3.852, 6.108] |
| economics_main | 27,868.46 [26,609.85, 29,127.08] | 13,647.50 [12,462.24, 14,832.77] | 0.055 [0.005, 0.105] | 0.056 [0.003, 0.108] |
| interaction | 7,317.15 [6,396.72, 8,237.58] | 6,926.81 [5,009.07, 8,844.55] | 0.110 [0.009, 0.211] | 0.112 [0.007, 0.216] |


### Heterogeneity by zone

Each zone appears in all 20 seeds. These contrasts weight farmers equally within each zone and seed; they do not imply representative Moroccan population weights. Intervals across zones are not multiplicity-adjusted.

| Zone | Seeds | B−A profit [CI] | C−A profit [CI] | Interaction profit [CI] | B−A yield [CI] |
| --- | --- | --- | --- | --- | --- |
| ARID | 20 | -5,911.02 [-7,902.52, -3,919.53] | 9,162.88 [8,423.91, 9,901.86] | 82.00 [-1,097.73, 1,261.73] | 0.065 [0.047, 0.084] |
| IRRIGATED_SOUSS | 20 | -8,370.69 [-17,877.03, 1,135.66] | 60,343.58 [56,895.79, 63,791.37] | 505.71 [-993.78, 2,005.20] | 9.306 [7.356, 11.255] |
| SAHARAN | 20 | 85,104.92 [71,886.58, 98,323.25] | 36,435.89 [31,860.67, 41,011.11] | 16,168.53 [12,740.75, 19,596.30] | 9.953 [8.267, 11.639] |
| SEMI_ARID_COOL | 20 | 820.99 [-1,315.78, 2,957.76] | 8,688.72 [8,244.55, 9,132.90] | -431.61 [-1,724.73, 861.52] | 0.285 [0.228, 0.341] |
| SEMI_ARID_WARM | 20 | 136,227.66 [120,521.53, 151,933.79] | 21,214.15 [18,589.20, 23,839.10] | 25,753.07 [22,383.43, 29,122.71] | 4.106 [3.715, 4.497] |
| SUB_HUMID | 20 | 8,137.75 [1,439.99, 14,835.51] | 9,084.47 [8,493.64, 9,675.31] | 2,412.16 [670.73, 4,153.59] | 5.715 [0.894, 10.537] |


### Farmers harmed or benefited versus paired A

| Condition | Harmed [CI] | Benefited [CI] | Unchanged [CI] |
| --- | --- | --- | --- |
| B | 26.50 [24.69, 28.31]% | 47.05 [44.12, 49.98]% | 26.45 [24.18, 28.72]% |
| C | 0.00 [0.00, 0.00]% | 100.00 [100.00, 100.00]% | 0.00 [0.00, 0.00]% |
| D | 16.10 [14.61, 17.59]% | 83.90 [82.41, 85.39]% | 0.00 [0.00, 0.00]% |


Fractions are computed per seed from the 100 paired farmer identities, then averaged. Equality tolerance is 1e−8 MAD in across-season mean profit. Zone fractions are retained in harm_summary.csv.

### Variation and diagnostics

| Profit contrast | Seed SD | Minimum seed effect | Maximum seed effect | Negative seeds |
| --- | --- | --- | --- | --- |
| information_only | 9,987.72 | 14,022.51 | 51,032.42 | 0 |
| economics_only | 2,642.86 | 19,121.82 | 29,293.36 | 0 |
| interaction | 1,966.67 | 4,190.88 | 11,935.48 | 0 |


Verified 240,000 unique, finite outcome rows; complete 3,000-row seed-condition panels; identical initial choices/gross yields and exogenous population/graph/weather within each seed; all saved source, input and output hashes match. A/C crop disagreements over all seasons: 0; B/D disagreements: 3150 of 60,000 paired farmer-seasons.

Execution metadata: [metadata.json](results/primary/metadata.json); full resolved settings: [resolved_configs.json](results/primary/resolved_configs.json); all metric contrasts: [effects.csv](results/primary/effects.csv). UTC completion: 2026-10-13T09:55:48.809771+00:00.

## Sensitivity: README economics

Premium .20; cost factors .63/.90; losses .05/.15. The .63 factor is 30% below .90. This changes the baseline loss, so comparisons use this scenario's own A.

### Outcomes

| Condition | Mean profit [CI] | Median profit [CI] | Mean yield t/ha [CI] | Area-weighted productivity t/ha [CI] |
| --- | --- | --- | --- | --- |
| A | 72,647.28 [66,934.07, 78,360.49] | 8,461.76 [6,980.56, 9,942.96] | 3.42 [3.16, 3.67] | 3.40 [3.16, 3.64] |
| B | 106,481.18 [99,973.79, 112,988.58] | 40,692.85 [27,742.46, 53,643.25] | 8.41 [7.21, 9.60] | 8.32 [7.13, 9.50] |
| C | 121,668.06 [113,591.59, 129,744.54] | 31,578.31 [28,994.18, 34,162.44] | 3.42 [3.16, 3.67] | 3.40 [3.16, 3.64] |
| D | 170,486.52 [161,514.91, 179,458.13] | 76,204.25 [60,287.64, 92,120.86] | 8.50 [7.30, 9.69] | 8.42 [7.24, 9.61] |


### Paired factorial effects

| Contrast | Mean profit [CI] | Median profit [CI] | Mean yield [CI] | Productivity [CI] |
| --- | --- | --- | --- | --- |
| information_only | 33,833.90 [29,291.89, 38,375.92] | 32,231.09 [19,880.80, 44,581.39] | 4.990 [3.915, 6.066] | 4.914 [3.810, 6.018] |
| economics_only | 49,020.78 [46,623.13, 51,418.44] | 23,116.55 [21,741.26, 24,491.84] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| combined | 97,839.24 [91,915.61, 103,762.88] | 67,742.49 [52,506.86, 82,978.13] | 5.079 [4.009, 6.150] | 5.023 [3.917, 6.129] |
| information_given_economics | 48,818.46 [42,875.50, 54,761.42] | 44,625.94 [29,884.90, 59,366.98] | 5.079 [4.009, 6.150] | 5.023 [3.917, 6.129] |
| economics_given_information | 64,005.34 [61,371.35, 66,639.32] | 35,511.40 [31,723.35, 39,299.44] | 0.089 [-0.005, 0.183] | 0.109 [0.004, 0.214] |
| information_main | 41,326.18 [36,099.46, 46,552.90] | 38,428.52 [24,928.09, 51,928.95] | 5.035 [3.963, 6.107] | 4.968 [3.865, 6.072] |
| economics_main | 56,513.06 [54,128.20, 58,897.92] | 29,313.97 [26,975.62, 31,652.33] | 0.045 [-0.002, 0.092] | 0.055 [0.002, 0.107] |
| interaction | 14,984.56 [13,365.00, 16,604.11] | 12,394.85 [9,137.59, 15,652.10] | 0.089 [-0.005, 0.183] | 0.109 [0.004, 0.214] |


### Heterogeneity by zone

Each zone appears in all 20 seeds. These contrasts weight farmers equally within each zone and seed; they do not imply representative Moroccan population weights. Intervals across zones are not multiplicity-adjusted.

| Zone | Seeds | B−A profit [CI] | C−A profit [CI] | Interaction profit [CI] | B−A yield [CI] |
| --- | --- | --- | --- | --- | --- |
| ARID | 20 | -5,962.54 [-7,777.35, -4,147.73] | 20,353.73 [18,731.70, 21,975.76] | 3,015.94 [1,352.49, 4,679.39] | 0.067 [0.050, 0.085] |
| IRRIGATED_SOUSS | 20 | -8,217.32 [-17,516.03, 1,081.39] | 118,244.58 [111,587.34, 124,901.83] | 1,079.43 [-1,736.22, 3,895.08] | 9.269 [7.312, 11.227] |
| SAHARAN | 20 | 81,842.55 [69,080.85, 94,604.26] | 72,545.66 [63,711.58, 81,379.74] | 32,498.09 [27,077.52, 37,918.66] | 9.953 [8.267, 11.639] |
| SEMI_ARID_COOL | 20 | 601.21 [-1,436.31, 2,638.73] | 19,382.59 [18,432.82, 20,332.36] | 1,535.40 [-338.46, 3,409.27] | 0.287 [0.232, 0.342] |
| SEMI_ARID_WARM | 20 | 131,316.75 [116,178.31, 146,455.20] | 43,164.97 [38,082.77, 48,247.18] | 49,229.36 [42,923.79, 55,534.92] | 4.106 [3.715, 4.497] |
| SUB_HUMID | 20 | 7,797.47 [1,401.83, 14,193.11] | 19,841.07 [18,613.89, 21,068.25] | 4,770.65 [1,844.07, 7,697.22] | 5.684 [0.882, 10.486] |


### Farmers harmed or benefited versus paired A

| Condition | Harmed [CI] | Benefited [CI] | Unchanged [CI] |
| --- | --- | --- | --- |
| B | 26.55 [24.75, 28.35]% | 46.40 [43.35, 49.45]% | 27.05 [24.67, 29.43]% |
| C | 0.00 [0.00, 0.00]% | 100.00 [100.00, 100.00]% | 0.00 [0.00, 0.00]% |
| D | 7.05 [5.97, 8.13]% | 92.95 [91.87, 94.03]% | 0.00 [0.00, 0.00]% |


Fractions are computed per seed from the 100 paired farmer identities, then averaged. Equality tolerance is 1e−8 MAD in across-season mean profit. Zone fractions are retained in harm_summary.csv.

### Variation and diagnostics

| Profit contrast | Seed SD | Minimum seed effect | Maximum seed effect | Negative seeds |
| --- | --- | --- | --- | --- |
| information_only | 9,704.86 | 12,930.88 | 49,054.56 | 0 |
| economics_only | 5,123.03 | 39,234.34 | 58,753.37 | 0 |
| interaction | 3,460.48 | 10,904.70 | 22,238.42 | 0 |


Verified 240,000 unique, finite outcome rows; complete 3,000-row seed-condition panels; identical initial choices/gross yields and exogenous population/graph/weather within each seed; all saved source, input and output hashes match. A/C crop disagreements over all seasons: 0; B/D disagreements: 5637 of 60,000 paired farmer-seasons.

Execution metadata: [metadata.json](results/readme_economics/metadata.json); full resolved settings: [resolved_configs.json](results/readme_economics/resolved_configs.json); all metric contrasts: [effects.csv](results/readme_economics/effects.csv). UTC completion: 2026-10-13T09:55:49.411344+00:00.

## Interpretation

Information access raises average simulated profit in both parameter scenarios, but does not benefit everyone. Under primary economics, the arid-zone information-only profit interval is wholly negative; the irrigated Souss estimate is negative with an interval crossing zero, and semi-arid cool is near zero with an interval crossing zero. Large positive effects in semi-arid warm and Saharan zones contribute strongly to the overall mean. The large gap between mean and median profits also cautions against treating the mean as a typical farmer outcome.

Economics-only changes profit but produces exactly zero gross-yield and productivity contrast in these runs. With empty initial memory and deterministic maximum-score decisions, a control farmer repeatedly observes only its chosen crop. A single observed crop has zero range-normalized own-experience bonus, so there is no exploration to initiate a switch. The imposed economic improvements then benefit every economics-only farmer. This is a structural result of the rules, not observed cooperative effectiveness.

The positive profit interaction includes mechanical amplification: premiums and smaller losses increase returns to information-induced output, and lower costs affect its profitability. It also permits changed decisions through realized social profit/cost signals. It is not a separate validation of social intelligence. The primary gross-yield interaction is small and positive; the sensitivity gross-yield interaction interval crosses zero.

The water proxy has exactly zero treatment contrasts in both scenarios because V1 falls back to 500 mm for every crop and paired weather determines irrigation. This cannot establish environmental neutrality or efficiency. No sustainability indicator beyond this diagnostic proxy is inferred.

## Verification and provenance

Final test command: `python -m pytest experiments/exp001/tests -q`. Outcome: **25 passed**, 0 failed (18.94 seconds). Coverage includes all four economic settings, information-off read/receive/publish isolation, first-season treatment independence, neutral-economics equivalence in all three information modes, independence from strategy labels, paired exogenous and latent shocks, fixed-seed/cross-process/interleaved replay, V1 yield/cost/water equation parity, seed-level factorial CIs and harm aggregation, output manifests and README sensitivity calculations.

Initial 17-test suite passed. Expanded suite initially had three failures because identical neutral-economics prices had int/float pandas dtype differences; exact numeric comparisons with dtype ignored resolved those test assertions. Simulation values were unchanged. The environment emitted a Requests dependency-version warning at pytest startup; tests and simulations completed, and the model does not use Requests.

Software: Python 3.12.4 (Anaconda), Windows 11; Mesa 3.4.2, NumPy 1.26.4, pandas 2.2.2, SciPy 1.13.1, NetworkX 3.2.1, pytest 9.0.2. Direct pins are in requirements-lock.txt and installed distribution inventory in environment-freeze.txt. Runs occurred on protocol commit 51ef5fa3bc52d8feec49cd8de93d4efb9010e0ac with implementation files then uncommitted; metadata records that state honestly and includes exact execution-source SHA-256 hashes. Notebook/data have not been changed.

Exact experiment commands (run from repository root):

```powershell
python -m experiments.exp001.runner --config experiments/exp001/configs/smoke.json --output experiments/exp001/results/smoke
python -m experiments.exp001.runner --config experiments/exp001/configs/primary.json --output experiments/exp001/results/primary
python -m experiments.exp001.runner --config experiments/exp001/configs/readme_economics.json --output experiments/exp001/results/readme_economics
python -m pytest experiments/exp001/tests -q
python -m experiments.exp001.report
```

The report command checks hashes and raw-data diagnostics before writing this report. Reproducing it requires the full generated primary and sensitivity outputs, not just the small committed evidence subset. Use new run directories for replay; original directory names above are the actual completed runs. Raw records and exogenous manifests remain locally available and reproducible but are not committed.

## Limits and open scientific questions

These are causal contrasts within the implemented simulator and its specified homogeneous treatment worlds, not field estimates for Morocco. Uncertainty covers random seeds only, not parameter uncertainty, data quality, model structure or economic equilibrium. Twenty seeds, unadjusted multiple comparisons, hypothetical graph/population assignment, static climate, unconstrained budgets and annual perennial switching limit interpretation. The network population differs from V1 mixed SHARED/INDIVIDUAL cohorts. See AUDIT.md for every deliberate design change.

Future reviewed experiments should address crop-specific water lookup and yield coupling, validated economics, total-profit versus per-hectare social signals, deduplication of repeated neighbor observations, separate own/social memory, and cooperative eligibility. Adaptive trust, partner selection and reinforcement learning remain out of scope.
