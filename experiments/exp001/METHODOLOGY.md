# EXP001 methodology

## Design and treatment interpretation

This is a simulation experiment conditional on V1 equations and four versioned JSON inputs, not empirical agricultural validation. The primary scenario preserves executable V1 parameters. A user-requested separate sensitivity uses the README economic claims, interpreting the 30% reduction relative to individual cost (0.63 vs 0.90). Neither scenario is calibrated to its outcomes.

A=(I off,E off), B=(I on,E off), C=(I off,E on), D=(I on,E on). Every run has 100 farmer identities and 30 simulated seasons. Each seed defines a fresh population, graph and environmental trajectory. Twenty independent seed replicates, seeds 0 through 19, were selected before the larger runs, following a 6-agent × 2-season × 2-seed smoke test. All 100 identities match across the four conditions, giving 400 simulated farmers per seed across separate worlds. This differs intentionally from V1's 50 partially matched pairs in one 100-agent mixed population.

Cooperative economics is an externally assigned intervention available to all farmers in E-on worlds. Participation costs and incentives are not modeled. Information-on farmers use the same zone and neighbor rules as V1, including repeated observations and mixed own/received memory; off farmers can only use their own outcomes and fixed ecological inputs. E changes observed costs and profits, which can affect own learning and shared signal values. This is a causal feedback pathway, not a change in who can access information. Consequently economics-only can eventually affect crop choices through experience. First-season crop choices and gross yields must match across all four worlds.

## Pairing and random numbers

SHA-256 keyed streams use seed plus semantic identifiers: population/agent; cost/agent; suitability/agent/crop; weather/season/zone; order/season; harvest/season/agent. Graphs use NetworkX with the seed. Harvest uniform and Gaussian shocks are shared across crops at a farmer-season, preserving V1 marginals and making alternative choices face the same shocks. Seeds are the independent replication units. Fixed identities share all exogenous attributes and latent suitability across conditions; world-specific endogenous decisions, costs and memories can differ. All decisions precede harvest, and social updates become available next season.

No global RNG state or mutable zones/memories/config is shared between runs. The runner verifies equal population/graph/weather hashes across A–D for every seed, and tests inspect latent suitability and harvest streams. Replay is exact in the recorded software environment, including across different Python hash salts; future library versions need revalidation. This stream scheme intentionally does not reproduce V1's nonportable global RNG path.

## Outcomes, estimands and inference

For each seed and condition, first average each farmer over all 30 seasons (including the initial season). Mean profit is the equal-farmer mean of those averages in MAD/farm/season; median profit is the median across those farmer averages. Mean yield is similarly t/ha, while productivity is total gross tonnes divided by total hectares, averaged over seasons (fixed land). Profit/ha is also reported. Crop tonnage aggregates commodities with different composition/value, so productivity is not a nutrition or welfare index. Gross yield is before loss; effective yield and production are retained in raw outputs.

Let A_s,B_s,C_s,D_s be a seed's condition outcome on its original additive scale. Information-only=B−A; economics-only=C−A; combined=D−A; information given economics=D−C; economics given information=D−B. Factorial information main effect=[(B−A)+(D−C)]/2; economics main effect=[(C−A)+(D−B)]/2; interaction=D−B−C+A. For every metric and zone, form seed-level contrasts first, then average. No ratios or percent-profit advantages are used as primary effects.

Uncertainty is the two-sided Student t 95% interval: mean ± t(.975,n−1) × sample SD/sqrt(n). SD uses ddof=1. One seed yields no estimated interval, not zero uncertainty. Seed-level SD and SE are exported. These intervals describe Monte Carlo variation of this simulator, not uncertainty about real-world parameters. Twenty seeds offer limited tail precision; intervals are descriptive and not adjusted for multiple outcomes/zones. Zone analyses include only seeds where that zone has agents (all four conditions must be paired); their n is reported explicitly.

Harm/benefit compares each identity's across-season mean profit with its matched A value, with absolute tolerance 1e−8 MAD for numerical equality. Compute fractions within each seed, then mean and t interval over seeds. Fractions do not treat farmers as independent replicates; t intervals can extend outside [0,1] near bounds and are not clipped. Shared weather and social interactions induce within-run dependence, including across zones and seasons.

## Limitations and unresolved scientific choices

The model has fixed prices with no market clearing, no resource or budget constraints, static soils/climate, independent weather categories, and immediate annual crop switching even for perennials. Cooperative premiums and reductions are imposed assumptions. Land/goal/zone sampling and network links are hypothetical, not a sampled Moroccan farming population. Social yield and total-profit normalization, self-inclusion in zone signals, duplicate messages and mixed memory are preserved rather than redesigned. Treatment effects are conditional on these choices and on information availability across an entirely treated population.

The V1 water lookup uses 500 mm for every crop despite category values in the JSON. Irrigation reduces the reported water proxy but does not modify production or billed water. Thus water_proxy_mm is diagnostic only; there is no modeled sustainability endpoint. No inference about emissions, soil conservation or environmental benefit is supported.

Scientific review remains appropriate for the water lookup, total-profit versus per-hectare social signals, repeated observations, network population/eligibility, parameter evidence, perennial dynamics and the sensitivity interpretation. Correcting these would define additional experiments; this ablation keeps them visible and preserves V1 assumptions.

## Completed replay check

After source whitespace/line-ending normalization, all three configurations were re-executed. Every generated CSV and each exogenous manifest was byte-identical to its first-pass counterpart. Final tests: 25 passed in 18.94 seconds. verification.json records per-file replay checks. Final run metadata hashes identify the normalized reviewed source. Initial raw evidence is retained locally under results/pre_formatting and excluded from version control. Saharan weather uses V1 fallback probabilities .20 drought/.15 wet because that input profile lacks those fields.
