# EXP004 measured pilot results

Completed 960,000 matched policy decisions: 20 agents, 3 actions, 3 dimensions, 100 independent-environment rounds per seed, seeds [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]. Scenarios ['S1', 'S2', 'S0'], measurement noise [0.5, 1.5], costs [0, 0.01, 0.1]. Costs are postprocessing, not extra replicates.

All intervals below are exploratory, unadjusted 95% Student t intervals across independent seeds. Round averages are formed within agents first. Harm is the fraction whose mean expected utility is below paired B0. Expected regret is primary; realized regret is a separate hindsight quantity in machine-readable artifacts. Units are abstract utility, not money or agricultural outcomes.

## Main findings

At noise .5, B1 reduces expected regret versus B0 in S1 by 0.3480 [0.3343, 0.3617] utility units. S2 B1 still improves mean utility by 0.0224 [0.0114, 0.0335], but harms 38.5000 [32.8135, 44.1865]% of agents. Thus context mismatch did not reverse the average zero-cost gain against this sparse local baseline; it greatly reduced it and caused individual harm.

S2 B2 improves utility by 0.2889 [0.2801, 0.2976]; B3 makes identical decisions. At cost .01, S2 B1 net utility changes by -0.1676 [-0.1786, -0.1565], while B3 changes by 0.2689 [0.2601, 0.2776]. The B3 cost advantage is assumed topology, not extra information or intelligence.

S0 has exactly zero decision value from sharing, and positive costs make local-only best. No sanity check failed. B1 is best at zero cost in S1; B2/B3 tie in S2; B3 is best at the tested positive costs in S1/S2. These rankings apply only to the prespecified pilot and accounting assumptions.

## Expected outcomes at zero transmission cost

| Regime | Noise | Policy | Expected regret [CI] | Expected utility [CI] | Harmed % [CI] | Lower-tail utility q10 [CI] | Payloads/agent/round |
|---|---|---|---|---|---|---|---|
| S1 | 0.5 | B0 | 0.3548 [0.3412, 0.3684] | 0.2454 [0.2209, 0.2699] | 0.0000 [0.0000, 0.0000] | 0.1719 [0.1463, 0.1975] | 0.00 |
| S1 | 0.5 | B1 | 0.0068 [0.0061, 0.0074] | 0.5934 [0.5703, 0.6165] | 0.0000 [0.0000, 0.0000] | 0.5090 [0.4877, 0.5302] | 19.00 |
| S1 | 0.5 | B2 | 0.0530 [0.0496, 0.0564] | 0.5472 [0.5248, 0.5696] | 0.0000 [0.0000, 0.0000] | 0.4636 [0.4420, 0.4852] | 5.70 |
| S1 | 0.5 | B3 | 0.0530 [0.0496, 0.0564] | 0.5472 [0.5248, 0.5696] | 0.0000 [0.0000, 0.0000] | 0.4636 [0.4420, 0.4852] | 2.00 |
| S1 | 1.5 | B0 | 0.4313 [0.4178, 0.4448] | 0.1689 [0.1454, 0.1923] | 0.0000 [0.0000, 0.0000] | 0.0656 [0.0404, 0.0908] | 0.00 |
| S1 | 1.5 | B1 | 0.0470 [0.0443, 0.0498] | 0.5531 [0.5295, 0.5768] | 0.0000 [0.0000, 0.0000] | 0.4699 [0.4468, 0.4930] | 19.00 |
| S1 | 1.5 | B2 | 0.1508 [0.1437, 0.1578] | 0.4494 [0.4279, 0.4710] | 0.0000 [0.0000, 0.0000] | 0.3629 [0.3359, 0.3898] | 5.70 |
| S1 | 1.5 | B3 | 0.1508 [0.1437, 0.1578] | 0.4494 [0.4279, 0.4710] | 0.0000 [0.0000, 0.0000] | 0.3629 [0.3359, 0.3898] | 2.00 |
| S2 | 0.5 | B0 | 0.3409 [0.3330, 0.3488] | 0.2540 [0.2414, 0.2667] | 0.0000 [0.0000, 0.0000] | 0.1736 [0.1591, 0.1882] | 0.00 |
| S2 | 0.5 | B1 | 0.3185 [0.3100, 0.3270] | 0.2764 [0.2631, 0.2898] | 38.5000 [32.8135, 44.1865] | 0.1667 [0.1382, 0.1952] | 19.00 |
| S2 | 0.5 | B2 | 0.0521 [0.0489, 0.0552] | 0.5429 [0.5308, 0.5549] | 0.0000 [0.0000, 0.0000] | 0.4557 [0.4407, 0.4706] | 5.70 |
| S2 | 0.5 | B3 | 0.0521 [0.0489, 0.0552] | 0.5429 [0.5308, 0.5549] | 0.0000 [0.0000, 0.0000] | 0.4557 [0.4407, 0.4706] | 2.00 |
| S2 | 1.5 | B0 | 0.4234 [0.4143, 0.4324] | 0.1716 [0.1596, 0.1836] | 0.0000 [0.0000, 0.0000] | 0.0734 [0.0577, 0.0891] | 0.00 |
| S2 | 1.5 | B1 | 0.3547 [0.3475, 0.3618] | 0.2403 [0.2272, 0.2533] | 23.5000 [20.0962, 26.9038] | 0.1386 [0.1176, 0.1596] | 19.00 |
| S2 | 1.5 | B2 | 0.1514 [0.1467, 0.1560] | 0.4436 [0.4314, 0.4557] | 0.0000 [0.0000, 0.0000] | 0.3531 [0.3356, 0.3705] | 5.70 |
| S2 | 1.5 | B3 | 0.1514 [0.1467, 0.1560] | 0.4436 [0.4314, 0.4557] | 0.0000 [0.0000, 0.0000] | 0.3531 [0.3356, 0.3705] | 2.00 |
| S0 | 0.5 | B0 | 0.0629 [0.0601, 0.0657] | 0.5373 [0.5138, 0.5607] | 0.0000 [0.0000, 0.0000] | 0.4600 [0.4371, 0.4829] | 0.00 |
| S0 | 0.5 | B1 | 0.0629 [0.0601, 0.0657] | 0.5373 [0.5138, 0.5607] | 0.0000 [0.0000, 0.0000] | 0.4600 [0.4371, 0.4829] | 57.00 |
| S0 | 0.5 | B2 | 0.0629 [0.0601, 0.0657] | 0.5373 [0.5138, 0.5607] | 0.0000 [0.0000, 0.0000] | 0.4600 [0.4371, 0.4829] | 57.00 |
| S0 | 0.5 | B3 | 0.0629 [0.0601, 0.0657] | 0.5373 [0.5138, 0.5607] | 0.0000 [0.0000, 0.0000] | 0.4600 [0.4371, 0.4829] | 4.00 |
| S0 | 1.5 | B0 | 0.2619 [0.2459, 0.2779] | 0.3383 [0.3171, 0.3594] | 0.0000 [0.0000, 0.0000] | 0.2780 [0.2577, 0.2983] | 0.00 |
| S0 | 1.5 | B1 | 0.2619 [0.2459, 0.2779] | 0.3383 [0.3171, 0.3594] | 0.0000 [0.0000, 0.0000] | 0.2780 [0.2577, 0.2983] | 57.00 |
| S0 | 1.5 | B2 | 0.2619 [0.2459, 0.2779] | 0.3383 [0.3171, 0.3594] | 0.0000 [0.0000, 0.0000] | 0.2780 [0.2577, 0.2983] | 57.00 |
| S0 | 1.5 | B3 | 0.2619 [0.2459, 0.2779] | 0.3383 [0.3171, 0.3594] | 0.0000 [0.0000, 0.0000] | 0.2780 [0.2577, 0.2983] | 4.00 |

## Paired policy effects versus local-only

Negative regret differences favor sharing. Utility differences are their exact negatives under paired evaluation. Intervals are on paired seed differences, not differences between separately estimated intervals.

| Regime | Noise | Policy | Expected regret difference [CI] | Net utility difference, cost .01 [CI] | Net utility difference, cost .1 [CI] |
|---|---|---|---|---|---|
| S1 | 0.5 | B1 | -0.3480 [-0.3617, -0.3343] | 0.1580 [0.1443, 0.1717] | -1.5520 [-1.5657, -1.5383] |
| S1 | 0.5 | B2 | -0.3018 [-0.3152, -0.2883] | 0.2448 [0.2313, 0.2582] | -0.2682 [-0.2817, -0.2548] |
| S1 | 0.5 | B3 | -0.3018 [-0.3152, -0.2883] | 0.2818 [0.2683, 0.2952] | 0.1018 [0.0883, 0.1152] |
| S1 | 1.5 | B1 | -0.3843 [-0.3974, -0.3712] | 0.1943 [0.1812, 0.2074] | -1.5157 [-1.5288, -1.5026] |
| S1 | 1.5 | B2 | -0.2806 [-0.2940, -0.2671] | 0.2236 [0.2101, 0.2370] | -0.2894 [-0.3029, -0.2760] |
| S1 | 1.5 | B3 | -0.2806 [-0.2940, -0.2671] | 0.2606 [0.2471, 0.2740] | 0.0806 [0.0671, 0.0940] |
| S2 | 0.5 | B1 | -0.0224 [-0.0335, -0.0114] | -0.1676 [-0.1786, -0.1565] | -1.8776 [-1.8886, -1.8665] |
| S2 | 0.5 | B2 | -0.2889 [-0.2976, -0.2801] | 0.2319 [0.2231, 0.2406] | -0.2811 [-0.2899, -0.2724] |
| S2 | 0.5 | B3 | -0.2889 [-0.2976, -0.2801] | 0.2689 [0.2601, 0.2776] | 0.0889 [0.0801, 0.0976] |
| S2 | 1.5 | B1 | -0.0687 [-0.0785, -0.0588] | -0.1213 [-0.1312, -0.1115] | -1.8313 [-1.8412, -1.8215] |
| S2 | 1.5 | B2 | -0.2720 [-0.2827, -0.2613] | 0.2150 [0.2043, 0.2257] | -0.2980 [-0.3087, -0.2873] |
| S2 | 1.5 | B3 | -0.2720 [-0.2827, -0.2613] | 0.2520 [0.2413, 0.2627] | 0.0720 [0.0613, 0.0827] |
| S0 | 0.5 | B1 | 0.0000 [0.0000, 0.0000] | -0.5700 [-0.5700, -0.5700] | -5.7000 [-5.7000, -5.7000] |
| S0 | 0.5 | B2 | 0.0000 [0.0000, 0.0000] | -0.5700 [-0.5700, -0.5700] | -5.7000 [-5.7000, -5.7000] |
| S0 | 0.5 | B3 | 0.0000 [0.0000, 0.0000] | -0.0400 [-0.0400, -0.0400] | -0.4000 [-0.4000, -0.4000] |
| S0 | 1.5 | B1 | 0.0000 [0.0000, 0.0000] | -0.5700 [-0.5700, -0.5700] | -5.7000 [-5.7000, -5.7000] |
| S0 | 1.5 | B2 | 0.0000 [0.0000, 0.0000] | -0.5700 [-0.5700, -0.5700] | -5.7000 [-5.7000, -5.7000] |
| S0 | 1.5 | B3 | 0.0000 [0.0000, 0.0000] | -0.0400 [-0.0400, -0.0400] | -0.4000 [-0.4000, -0.4000] |

## Context and objective heterogeneity

S2 at measurement noise .5, cost .01; subgroup labels refer to fixed context or largest utility weight. All scenarios/subgroups and subgroup seed counts are retained in levels.json and contrasts.json.

| Group | Policy | Regret difference from B0 [CI] | Harmed % [CI] | Net utility difference from B0 [CI] |
|---|---|---|---|---|
| context_0 | B1 | -0.0591 [-0.0912, -0.0269] | 27.1429 [13.9660, 40.3197] | -0.1309 [-0.1631, -0.0988] |
| context_0 | B2 | -0.2921 [-0.3047, -0.2795] | 0.0000 [0.0000, 0.0000] | 0.2321 [0.2195, 0.2447] |
| context_0 | B3 | -0.2921 [-0.3047, -0.2795] | 0.0000 [0.0000, 0.0000] | 0.2721 [0.2595, 0.2847] |
| context_1 | B1 | -0.0254 [-0.0566, 0.0057] | 32.8571 [17.8128, 47.9014] | -0.1646 [-0.1957, -0.1334] |
| context_1 | B2 | -0.2898 [-0.3042, -0.2755] | 0.0000 [0.0000, 0.0000] | 0.2298 [0.2155, 0.2442] |
| context_1 | B3 | -0.2898 [-0.3042, -0.2755] | 0.0000 [0.0000, 0.0000] | 0.2698 [0.2555, 0.2842] |
| context_2 | B1 | 0.0238 [-0.0111, 0.0587] | 58.3333 [42.6306, 74.0361] | -0.2138 [-0.2487, -0.1789] |
| context_2 | B2 | -0.2839 [-0.3054, -0.2625] | 0.0000 [0.0000, 0.0000] | 0.2339 [0.2125, 0.2554] |
| context_2 | B3 | -0.2839 [-0.3054, -0.2625] | 0.0000 [0.0000, 0.0000] | 0.2639 [0.2425, 0.2854] |
| objective_0 | B1 | -0.0270 [-0.0477, -0.0063] | 34.2956 [24.9937, 43.5976] | -0.1630 [-0.1837, -0.1423] |
| objective_0 | B2 | -0.2866 [-0.2994, -0.2738] | 0.0000 [0.0000, 0.0000] | 0.2294 [0.2166, 0.2421] |
| objective_0 | B3 | -0.2866 [-0.2994, -0.2738] | 0.0000 [0.0000, 0.0000] | 0.2666 [0.2538, 0.2794] |
| objective_1 | B1 | -0.0159 [-0.0338, 0.0020] | 44.6939 [33.9725, 55.4153] | -0.1741 [-0.1920, -0.1562] |
| objective_1 | B2 | -0.2942 [-0.3090, -0.2794] | 0.0000 [0.0000, 0.0000] | 0.2372 [0.2222, 0.2521] |
| objective_1 | B3 | -0.2942 [-0.3090, -0.2794] | 0.0000 [0.0000, 0.0000] | 0.2742 [0.2594, 0.2890] |
| objective_2 | B1 | -0.0203 [-0.0371, -0.0035] | 39.2262 [31.3940, 47.0583] | -0.1697 [-0.1865, -0.1529] |
| objective_2 | B2 | -0.2862 [-0.2985, -0.2739] | 0.0000 [0.0000, 0.0000] | 0.2294 [0.2170, 0.2419] |
| objective_2 | B3 | -0.2862 [-0.2985, -0.2739] | 0.0000 [0.0000, 0.0000] | 0.2662 [0.2539, 0.2785] |

## Controls, execution and interpretation

All raw world/output/source hashes checked; expected and realized regret recomputed from stored counterfactuals; every agent mean reproduced from raw arrays. Measurement-noise sensitivities have identical evaluation worlds. B2 and B3 make identical decisions in every world. All policies make identical decisions in S0. S0 sharing therefore has exactly zero expected-utility gain at zero cost and strictly loses net utility at positive cost.

B3 versus B2 isolates the stated communication topology only: identical intelligence, different uploads/deliveries/replies. The central service has no ground-truth access. Naive pooling in S2 discards relevant context labels; this is estimator misspecification, not inherently harmful true evidence or a mismatch in sender preferences. Different preferences act only on raw outcome predictions. All evidence is unbiased with calibrated variance.

Read LIMITATIONS.md for the post-pilot assessment, unexpected findings and readiness for a new selector. No p-value selection, hyperparameter tuning or goal-aware method was performed.

Actual test command: `python -m pytest experiments/exp004/tests -q` â€” 25 passed in 9.98 s. A pre-existing Anaconda requests dependency warning did not affect these NumPy/SciPy computations. Smoke completed 2,880 decisions before the pilot.

Actual run commands (repository root):

```powershell
python -m experiments.exp004.runner --config experiments/exp004/configs/smoke.json --output experiments/exp004/results/smoke
python -m experiments.exp004.runner --config experiments/exp004/configs/pilot.json --output experiments/exp004/results/pilot
python -m experiments.exp004.report --results experiments/exp004/results/pilot
```

Use fresh results/replay paths for reruns as in README.md. Raw outputs remain local and regenerable; compact summaries are committed.

Execution commit: 12a2062aec3b0cca67fbe38bf88903416fd29b4b. Source hashes and dirty state at metadata capture are recorded in metadata.json. The execution modules were committed before the pilot; downstream reporting was prepared while it ran.

Python: 3.12.4 | packaged by Anaconda, Inc. | (main, Jun 18 2024, 15:03:56) [MSC v.1929 64 bit (AMD64)]. Platform: Windows-11-10.0.26200-SP0. Packages: {'numpy': '1.26.4', 'scipy': '1.13.1'}. Completion UTC: 2026-10-13T15:57:01.393241+00:00.
