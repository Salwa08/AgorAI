# EXP002 — mechanisms of harmful social information

Completed simulation diagnostics: **20 seeds (0–19), 100 matched farmers, 30 seasons, 16 arms; 960,000 farmer-season outcomes**. The research plan was committed before implementation. EXP001 A–D seed summaries reproduce exactly, including the +35,238.72 MAD information-only mean effect, 26.5% harmed, and ARID mean effect −5,911.02 MAD with a small positive gross-yield effect.

**Interpretation rule:** these are interventions within FarmSwarm, not empirical causal evidence. Negative profit differences alone do not establish environmental negative transfer. All intervals are 95% seed-level t intervals, with seasons averaged within farmers first. Intervals are unadjusted; the 48 prespecified endpoint/contrast/stratum tests receive Holm-adjusted p-values separately.

## Absolute outcomes and harm versus original A

Profit is MAD/farmer/season; median profit is the median across farmer mean profits within each seed, then averaged over seeds. Harm compares each matched identity with A. Negative-part loss averages losses over everyone (zero for unhurt farmers). Switching excludes season one. All rows below have 20 seed replicates.

| Arm | Mean profit [CI] | Median profit [CI] | Harmed % [CI] | Negative-part loss [CI] | Switch % [CI] |
| --- | --- | --- | --- | --- | --- |
| A | 76,545.4 [70,608.4, 82,482.3] | 9,813.3 [8,224.3, 11,402.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| B | 111,784.1 [105,044.0, 118,524.2] | 43,328.9 [29,910.0, 56,747.7] | 26.5 [24.7, 28.3] | 10,754.7 [9,113.2, 12,396.2] | 4.5 [4.1, 4.9] |
| C | 100,755.2 [93,596.8, 107,913.6] | 19,997.4 [17,870.3, 22,124.5] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| D | 143,311.1 [135,258.1, 151,364.2] | 60,439.8 [45,490.3, 75,389.2] | 16.1 [14.6, 17.6] | 5,170.7 [4,168.9, 6,172.6] | 4.4 [4.0, 4.7] |
| A_e02 | 77,751.4 [72,089.1, 83,413.6] | 10,721.0 [8,823.9, 12,618.0] | 20.3 [18.7, 22.0] | 3,032.9 [2,108.7, 3,957.1] | 3.0 [2.8, 3.3] |
| A_e05 | 78,454.2 [73,389.0, 83,519.3] | 11,648.2 [9,335.7, 13,960.8] | 34.5 [32.3, 36.8] | 6,251.8 [4,933.7, 7,569.9] | 7.7 [7.3, 8.0] |
| A_e10 | 79,739.3 [74,363.8, 85,114.8] | 14,716.8 [10,405.5, 19,028.0] | 41.9 [40.0, 43.8] | 9,888.7 [8,351.8, 11,425.6] | 15.3 [14.9, 15.7] |
| A_e20 | 79,492.5 [74,011.7, 84,973.2] | 18,901.4 [13,609.7, 24,193.0] | 41.1 [39.6, 42.7] | 14,386.0 [12,661.6, 16,110.4] | 29.6 [29.0, 30.2] |
| zone_only | 113,162.7 [106,861.9, 119,463.5] | 48,356.9 [34,103.6, 62,610.1] | 25.9 [23.8, 27.9] | 9,657.7 [8,127.8, 11,187.7] | 4.0 [3.7, 4.3] |
| neighbor_only | 80,576.0 [73,935.3, 87,216.6] | 9,540.7 [7,475.7, 11,605.7] | 11.1 [9.8, 12.4] | 6,318.3 [4,594.6, 8,042.0] | 1.6 [1.3, 1.8] |
| dedup | 112,216.6 [105,529.3, 118,904.0] | 44,040.0 [30,738.9, 57,341.0] | 26.5 [24.7, 28.3] | 10,589.7 [9,178.2, 12,001.2] | 4.6 [4.2, 5.0] |
| own_memory_only | 112,305.7 [105,965.4, 118,646.0] | 46,517.0 [32,915.6, 60,118.4] | 27.5 [25.4, 29.7] | 10,612.6 [9,056.2, 12,169.0] | 4.4 [4.1, 4.7] |
| profit_per_ha | 111,486.2 [105,064.9, 117,907.6] | 43,616.5 [29,755.1, 57,477.9] | 26.7 [24.9, 28.5] | 10,934.2 [9,359.2, 12,509.2] | 4.6 [4.2, 5.0] |
| unrestricted | 111,892.0 [104,270.5, 119,513.6] | 47,176.8 [32,568.2, 61,785.4] | 23.2 [21.7, 24.7] | 9,021.1 [7,477.1, 10,565.1] | 9.4 [8.5, 10.3] |
| ecological | 108,196.0 [101,389.9, 115,002.1] | 37,958.7 [25,617.2, 50,300.3] | 26.9 [25.1, 28.7] | 11,053.6 [9,410.7, 12,696.5] | 5.2 [4.8, 5.6] |
| zone_profit_only | 133,148.1 [126,115.1, 140,181.1] | 48,449.6 [34,392.3, 62,507.0] | 9.8 [7.9, 11.7] | 3,783.2 [2,411.6, 5,154.8] | 8.9 [8.2, 9.6] |


## Controlled intervention contrasts

Each intervention changes one mechanism. B-based rows compare against B; epsilon rows compare against A. Harm differences are percentage-point changes in the fraction harmed relative to original A. Holm p-values cover the complete family of 48 tests (12 contrasts × 2 endpoints × ALL/ARID).

### ALL

| Contrast | Profit change [CI] | Holm p | Harm change, pp [CI] | Holm p |
| --- | --- | --- | --- | --- |
| zone_only − B | 1,378.7 [-620.9, 3,378.2] | 1 | -0.7 [-2.1, 0.8] | 1 |
| neighbor_only − B | -31,208.1 [-36,084.2, -26,332.0] | 1.621e-09 | -15.4 [-17.5, -13.3] | 1.906e-10 |
| dedup − B | 432.6 [-214.8, 1,080.0] | 1 | 0.0 [-0.3, 0.3] | 1 |
| own_memory_only − B | 521.6 [-1,205.6, 2,248.8] | 1 | 1.0 [-0.1, 2.2] | 1 |
| profit_per_ha − B | -297.9 [-1,405.8, 810.1] | 1 | 0.2 [-0.7, 1.1] | 1 |
| unrestricted − B | 108.0 [-2,069.7, 2,285.7] | 1 | -3.3 [-4.9, -1.7] | 0.008204 |
| ecological − B | -3,588.0 [-5,117.7, -2,058.4] | 0.003018 | 0.4 [-0.4, 1.2] | 1 |
| zone_profit_only − B | 21,364.1 [17,696.8, 25,031.4] | 7.911e-09 | -16.7 [-18.9, -14.5] | 8.118e-11 |
| A_e02 − A | 1,206.0 [-328.9, 2,741.0] | 1 | 20.3 [18.7, 22.0] | 1.455e-14 |
| A_e05 − A | 1,908.8 [-275.8, 4,093.4] | 1 | 34.5 [32.3, 36.8] | 1.85e-16 |
| A_e10 − A | 3,194.0 [962.4, 5,425.5] | 0.1933 | 41.9 [40.0, 43.8] | 3.035e-19 |
| A_e20 − A | 2,947.1 [50.3, 5,844.0] | 0.9769 | 41.1 [39.6, 42.7] | 5.153e-21 |


### ARID

| Contrast | Profit change [CI] | Holm p | Harm change, pp [CI] | Holm p |
| --- | --- | --- | --- | --- |
| zone_only − B | 2,022.0 [221.5, 3,822.5] | 0.6534 | -5.3 [-8.0, -2.7] | 0.01395 |
| neighbor_only − B | 3,053.1 [579.9, 5,526.4] | 0.4551 | -25.3 [-32.6, -18.0] | 2.44e-05 |
| dedup − B | 50.3 [-64.8, 165.4] | 1 | 0.0 [0.0, 0.0] | 1 |
| own_memory_only − B | 658.7 [-186.0, 1,503.4] | 1 | 0.1 [-1.4, 1.6] | 1 |
| profit_per_ha − B | 250.9 [-849.0, 1,350.7] | 1 | 0.2 [-1.6, 1.9] | 1 |
| unrestricted − B | 17,893.3 [2,261.0, 33,525.5] | 0.6228 | -12.4 [-17.5, -7.4] | 0.001934 |
| ecological − B | 0.0 [0.0, 0.0] | 1 | 0.0 [0.0, 0.0] | 1 |
| zone_profit_only − B | 13,374.5 [10,523.7, 16,225.3] | 2.61e-07 | -25.9 [-32.8, -19.0] | 7.528e-06 |
| A_e02 − A | 2,654.5 [354.5, 4,954.5] | 0.6228 | 15.9 [10.6, 21.2] | 0.0001711 |
| A_e05 − A | 5,149.0 [2,395.9, 7,902.1] | 0.02515 | 28.7 [22.9, 34.5] | 1.135e-07 |
| A_e10 − A | 8,686.4 [4,770.0, 12,602.8] | 0.00533 | 32.3 [27.7, 36.9] | 3.23e-10 |
| A_e20 − A | 13,425.9 [9,790.9, 17,060.9] | 9.719e-06 | 25.9 [21.0, 30.8] | 4.067e-08 |


## Exploration changes the comparison baseline

B is held fixed. The following compares B with the contemporaneous exploratory A, including newly paired harm fractions computed against that exploratory baseline (not differences between two A-relative harm rates). These comparisons are exploratory.

| Stratum | Comparison | Mean profit effect [CI] | B harmed % [CI] | Negative-part loss [CI] |
| --- | --- | --- | --- | --- |
| ALL | B − A_e02 | 34,032.7 [29,413.9, 38,651.5] | 30.8 [28.5, 33.0] | 10,519.8 [8,975.9, 12,063.6] |
| ALL | B − A_e05 | 33,329.9 [28,706.9, 37,952.9] | 36.4 [33.7, 39.1] | 10,172.6 [8,638.3, 11,706.8] |
| ALL | B − A_e10 | 32,044.8 [27,139.0, 36,950.5] | 40.4 [37.2, 43.6] | 9,478.3 [7,864.3, 11,092.2] |
| ALL | B − A_e20 | 32,291.6 [27,521.1, 37,062.1] | 42.4 [38.9, 45.9] | 8,790.7 [7,418.1, 10,163.3] |
| ARID | B − A_e02 | -8,565.5 [-10,351.7, -6,779.3] | 48.9 [44.0, 53.7] | 11,076.8 [8,798.3, 13,355.3] |
| ARID | B − A_e05 | -11,060.0 [-13,824.9, -8,295.1] | 61.3 [56.5, 66.0] | 13,561.8 [10,888.4, 16,235.3] |
| ARID | B − A_e10 | -14,597.4 [-18,697.6, -10,497.2] | 72.2 [66.9, 77.6] | 16,666.3 [12,790.5, 20,542.2] |
| ARID | B − A_e20 | -19,336.9 [-23,524.0, -15,149.9] | 79.3 [75.1, 83.5] | 21,158.1 [17,152.2, 25,164.0] |


Exploration can improve average independent performance while harming some identities. Uniform exploration continues throughout the horizon and is not a learning-optimal policy. No epsilon was selected for favorable results.

## Zone heterogeneity and severity

These additional zone/endpoints are exploratory; all six zones occur in all 20 seeds.

| Zone | B−A mean profit [CI] | Harmed % [CI] | Loss among harmed [CI] | Severity seeds | 10th percentile effect [CI] |
| --- | --- | --- | --- | --- | --- |
| ARID | -5,911.0 [-7,902.5, -3,919.5] | 39.1 [34.1, 44.1] | 21,542.4 [18,422.8, 24,662.0] | 20 | -30,467.0 [-36,974.3, -23,959.7] |
| IRRIGATED_SOUSS | -8,370.7 [-17,877.0, 1,135.7] | 40.8 [35.2, 46.3] | 77,375.1 [64,995.2, 89,755.1] | 20 | -105,084.6 [-130,290.7, -79,878.6] |
| SAHARAN | 85,104.9 [71,886.6, 98,323.3] | 26.8 [21.4, 32.2] | 59,965.0 [48,092.3, 71,837.6] | 19 | -51,502.8 [-67,407.3, -35,598.3] |
| SEMI_ARID_COOL | 821.0 [-1,315.8, 2,957.8] | 36.8 [31.6, 42.0] | 12,173.0 [9,065.3, 15,280.6] | 20 | -14,085.6 [-17,393.6, -10,777.7] |
| SEMI_ARID_WARM | 136,227.7 [120,521.5, 151,933.8] | 1.0 [-0.6, 2.6] | 204,595.1 [-931,574.1, 1,340,764.2] | 2 | 10,226.3 [-3,195.0, 23,647.6] |
| SUB_HUMID | 8,137.7 [1,440.0, 14,835.5] | 15.5 [8.6, 22.4] | 14,656.4 [8,676.6, 20,636.2] | 15 | -5,040.7 [-8,216.5, -1,864.8] |


## Decision evidence and accounting decomposition

All source observations in default B originate within the receiver's zone. Source ages are at least one season in decision traces. Current-season candidate potential profit is computed only after every decision and is labeled analyst-only. The decomposition below is an accounting identity, not causal mediation.

| Metric | ALL [CI] | ARID [CI] |
| --- | --- | --- |
| score_conflict_among_losses | 1.0 [1.0, 1.0] | 1.0 [1.0, 1.0] |
| yield_gain_among_losses | 0.9 [0.9, 1.0] | 1.0 [1.0, 1.0] |
| mean_yield_component | 219,071.7 [188,865.7, 249,277.6] | 3,689.7 [2,382.3, 4,997.0] |
| mean_price_component | -178,683.2 [-207,440.3, -149,926.2] | -9,760.7 [-12,924.7, -6,596.7] |
| mean_cost_component | -5,149.7 [-5,818.0, -4,481.4] | 160.0 [94.6, 225.5] |
| mean_neighbor_duplicates | 2.8 [2.2, 3.3] | 2.1 [1.0, 3.3] |
| neighbor_duplicate_fraction | 0.1 [0.1, 0.1] | 0.0 [0.0, 0.1] |
| received_experience | 9.5 [8.9, 10.1] | 8.6 [6.7, 10.5] |
| cross_channel_duplicates | 21.4 [20.0, 22.8] | 19.2 [14.9, 23.6] |
| mean_age | 5.8 [5.7, 5.8] | 5.8 [5.7, 5.9] |


Conflict and tradeoff quantities are fractions, not percentages. Duplication counts are appearances of immutable harvest IDs, not equality of numeric values; cross-channel duplication intentionally includes an event used by different weighted channels. Experience received counts refer to observations originating at another farmer. Neighbor duplicate fraction conditions on a nonempty neighbor pool.

### Harmed versus benefited farmers (descriptive)

Groups are defined by their realized 30-season average B−A effect. These associations are outcome-selected and not causal tests. Numbers are means of seed-specific group summaries; missing groups are omitted and n is reported.

| Zone | Group | Seeds | Land ha | Switch % | Profit delta | Received experience | Neighbor duplicates |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ARID | harmed | 20 | 5.17 | 5.51 | -21,542.4 | 11.6 | 3.0 |
| ARID | benefited | 20 | 5.44 | 8.92 | 8,191.2 | 6.6 | 1.5 |
| ARID | unchanged | 20 | 5.38 | 0.00 | 0.0 | 7.2 | 1.7 |
| IRRIGATED_SOUSS | harmed | 20 | 5.55 | 5.50 | -77,375.1 | 9.1 | 3.1 |
| IRRIGATED_SOUSS | benefited | 20 | 5.74 | 5.52 | 80,992.0 | 8.5 | 3.0 |
| IRRIGATED_SOUSS | unchanged | 19 | 5.91 | 0.00 | 0.0 | 10.7 | 3.0 |
| SEMI_ARID_WARM | harmed | 2 | 7.04 | 4.31 | -204,595.1 | 25.4 | 18.1 |
| SEMI_ARID_WARM | benefited | 20 | 5.70 | 3.68 | 184,485.4 | 7.6 | 1.8 |
| SEMI_ARID_WARM | unchanged | 20 | 5.44 | 0.00 | 0.0 | 12.7 | 4.5 |


### ARID crop substitutions contributing to paired profit loss

Each seed/zone contribution divides the substitution's total profit difference by all farmer-season observations in that zone. Absent substitutions receive zero before averaging seeds; contributions therefore sum to the zone effect. These are A-crop versus B-crop substitutions, distinct from actual temporal switches recorded in switch_transitions.csv.

| A crop → B crop | Farmer-season rows | Mean contribution, MAD [CI] |
| --- | --- | --- |
| almonds → barley | 2450 | -8,464.6 [-10,107.0, -6,822.3] |
| cumin → barley | 26 | -27.3 [-84.4, 29.8] |
| barley → sorghum | 1 | -0.7 [-2.1, 0.8] |
| almonds → almonds | 2290 | 0.0 [0.0, 0.0] |
| barley → barley | 3973 | 0.0 [0.0, 0.0] |
| cumin → cumin | 2 | 0.0 [0.0, 0.0] |
| sorghum → sorghum | 11 | 0.0 [0.0, 0.0] |
| cumin → almonds | 32 | 109.5 [-91.9, 310.8] |


Actual transitions and their distributions, season-by-zone harm profiles, source statistics, paired rescue rates and all non-primary zone contrasts are retained in the machine-readable evidence. No farmer-season counts are used as independent replicates.

## Competing hypotheses and EXP003 recommendation

The strongest controlled contribution is the zone scoring mixture: profit-only zone scoring raises mean profit by 21,364 MAD and reduces harm from 26.5% to 9.8%. Default cross-zone exposure is zero. Deduplication and per-hectare profit normalization show no clear average benefit; mixed-memory scoring can cause individual losses even though its removal does not clearly improve the mean. Exploration strengthens some baselines but does not remove the overall information advantage. These conclusions concern the modeled environment only.

See [INTERPRETATION.md](INTERPRETATION.md) for hypothesis-by-hypothesis evidence, a post-hoc causal decision case, contradictory findings, and a prioritized EXP003 proposal. The priority is a prespecified objective-mixture × memory-separation factorial with an exploration comparator; the water correction belongs in a separate sensitivity. No EXP003 implementation is included.

## Validation and reproducibility

Tests: **52 passed**, 0 failed; command `python -m pytest experiments/exp001/tests experiments/exp002/tests -q`. Coverage includes tracing-on/off exact parity, all four committed EXP001 seed-zero regressions, prospective identity/deduplication, past-only evidence, context rules including ultimate-source bypass prevention, normalization, intervention independence, pairing, accounting, seed-level inference and the 48-test Holm family. EXP001's tests also pass unchanged.

The complete 20-seed A–D reproduction table matches EXP001 committed seed summaries exactly. All 320 seed/arm environment hashes pair; 960,000 outcome rows passed count, identity uniqueness, finite-value and accounting checks. Default B has zero cross-zone observations. Saved execution-source, input and output hashes were verified. The test environment emits a Requests dependency warning; no test or simulation failed.

Software: 3.12.4 | packaged by Anaconda, Inc. | (main, Jun 18 2024, 15:03:56) [MSC v.1929 64 bit (AMD64)]. Platform: Windows-11-10.0.26200-SP0. Packages: {'mesa': '3.4.2', 'numpy': '1.26.4', 'pandas': '2.2.2', 'scipy': '1.13.1', 'networkx': '3.2.1', 'pytest': '9.0.2'}.
The execution metadata records the pre-implementation plan commit and uncommitted implementation state plus exact source hashes; this is not presented as execution from a later commit. Metadata UTC completion: 2026-10-13T14:48:20.509755+00:00.

Actual commands (repository root):

```powershell
python -m experiments.exp002.runner --config experiments/exp002/configs/smoke.json --output experiments/exp002/results/smoke
python -m experiments.exp002.runner --config experiments/exp002/configs/full.json --output experiments/exp002/results/full
python -m pytest experiments/exp001/tests experiments/exp002/tests -q
python -m experiments.exp002.diagnose --results experiments/exp002/results/full
python -m experiments.exp002.report --results experiments/exp002/results/full
```

For reproduction in a fresh clone use new results/replay directories as documented in README.md. Raw compressed decisions, observations and outcomes remain local; compact summaries and provenance are committed. Existing V1 notebook, EXP001 implementation and agricultural data remain unchanged.

## Scientific limits

Seed uncertainty excludes parameter, observational and structural uncertainty. Holm correction covers only the designated 48 tests. Other results are explicitly exploratory. Within-zone farmers share environmental parameters, so same-zone filtering cannot test unmodeled microclimates. Ecological filtering changes only one cross-zone pair under current inputs. Deduplication leaves cross-channel reuse and cannot identify all contamination mechanisms. Exploration and profit-only zone weighting are narrow diagnostics, not policy recommendations. The 500-mm fallback, uncoupled irrigation/yield, static prices and climate, non-profit agent goals, unconstrained budgets and immediate perennial switching remain limitations. No sustainability benefit or real-world agricultural improvement is claimed.
