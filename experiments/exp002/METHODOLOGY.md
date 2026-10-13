# EXP002 methodology

## Scope and isolation

The research plan was committed as d3c5102 before implementation. Base EXP001 commit 9564602 and all V1/EXP001 files are preserved. EXP002 subclasses the existing model for scheduling/instrumentation and imports its farmer, suitability, harvest and economic equations; it does not monkey-patch EXP001. Decisions reproduce the original arithmetic order. Trace-only A–D comparisons are tested for exact numerical equality with the original runner. No changes correct the 500-mm water fallback, static climate, unconstrained budgets, perennial switching or duplicated scoring channels.

Full design: seeds 0–19, 100 farmers, 30 seasons, all 16 arms specified in RESEARCH_PLAN.md; 960,000 farmer-season observations. Smoke: seeds [0,1], six farmers, three seasons, 576 observations. A–D reproduce EXP001. B-based interventions keep economics off. Independent exploration arms start from A; shared information arms have epsilon zero. Complete settings are saved for every seed/arm.

## Intervention semantics

D1 uses epsilon-greedy with rates .02, .05, .10, .20, picked before diagnostic outcomes. Exploration is a uniform draw among available viable crops, including the current greedy crop, so an exploration event need not switch crops. Exploration runs each season, including season one. Extra semantic streams do not advance weather/harvest/suitability RNGs, and the exploration event sets are nested across rates. We report exploratory A minus A and B minus exploratory A. The latter changes the comparison baseline, not B's information mechanism.

D2 uses existing shared_strategy. Zone-only removes neighbor read and propagation; neighbor-only removes zone scoring but retains propagated information in the experience channel. Combined is original B. This is the existing model's channel definition, not independent control of every path.

D3 identifies each harvest by (seed, farmer ID, season). Deduplication retains the first occurrence within each crop's neighbor evidence and within the experience pool before minimum-observation thresholds and normalization. It preserves values/order of remaining entries. The same event may still affect separate zone/neighbor/experience channels; this intervention removes within-pool multiplicity, not cross-channel weighting. Direct broadcasts already carry each own event once; duplicated evidence mainly arises from merging neighbor histories. A separate own_memory_only arm removes received observations from the experience score but does not alter its stored memory, neighbor access or propagation. Comparing these individually distinguishes two components of H3; it does not estimate their interaction.

D4 changes only zone profit aggregation: mean(profit_i/land_i), not mean(profit_i)/mean(land_i). Other score weights, yield component and treatment economics remain identical.

D5 default is same-zone (not unrestricted). Unrestricted permits all graph neighbors and their origins. Ecological mode accepts same-zone transfers or a cross-zone pair with equal dominant soil, absolute mean-temperature difference <=3 C, and absolute annual-precipitation difference <=200 mm. Static input values are known before decisions. The rule is applied both to immediate contacts and to ultimate observation origins to prevent indirect bypass. With current inputs it admits only SEMI_ARID_WARM <-> SEMI_ARID_COOL cross-zone pairs. Different filters change both source composition and evidence volume; outcome changes cannot uniquely identify environmental mismatch.

Additional H1 intervention changes the zone mixture from .6 yield + .4 nonnegative profit to 0 yield + 1 nonnegative profit, preserving normalization and unobserved-crop penalties. It retains neighbor and experience objectives. This tests one objective component; it is not a profit-optimal agent redesign.

## Provenance and timing

V1/EXP001 historical tuples do not retain source IDs or dates. No identities are inferred from equal numbers or invented for old records. In prospective reruns, EXP002 creates an immutable observation immediately after its actual harvest, recording identity, source zone, crop, land, yield, cost, water and profit. Sidecar memory mirrors each original tuple's exact insertion and propagation order. Tests assert numerical tuples equal provenance values, distinct equal-valued harvests remain distinct, and deduplication removes only repeated IDs.

All farmers decide before harvest. Only observations with source season < decision season can enter evidence summaries. Zone evidence is last season; neighbor and experience histories accumulate. Candidate traces record ecological score and incremental zone/neighbor/experience contributions, total score, origin farmers/zones, age range/mean, unique events, appearances, duplicates, received counts and source-land mean. Counts include available pools, including pools below min_neighbor_obs; only pools of at least three enter neighbor scores. Aggregate pool normalization can include crops outside a farmer's available candidates, as in V1. Zero candidate contribution does not necessarily mean no evidence was available.

After all decisions, analysts evaluate each candidate's potential profit under that farmer-season's same harvest shock. These counterfactuals are never exposed to scoring, memory or sharing. They measure realized model regret, not ex-ante expected profit. Expected score is the heuristic score at decision time; it is not calibrated expected economic utility. Tracing off omits this diagnostic calculation and yields identical outcomes.

## Pairing and outcome decomposition

All original semantic streams and farmer identities match across arms. Each seed's population, graph and complete weather trajectory are hashed and checked equal. Exploration alone uses additional independent keyed streams. Consequences of changed crop choices are endogenous.

Every raw row includes a paired A comparison at identical seed/identity/season. Profit difference is exactly decomposed symmetrically into yield-revenue, price-revenue and cost components:

Delta profit = land × [(effective_yield_t − effective_yield_A) × (price_t + price_A)/2 + (price_t − price_A) × (effective_yield_t + effective_yield_A)/2 − (cost_t − cost_A)].

This is an accounting identity, not mediation identification. It handles changed crops and the revenue cross-term without arbitrary ordering. Land is identical within a pair, so population land differences cannot mechanically confound paired effects. Correlation of harm with land or signal source land is descriptive. Yield-profit tradeoff counts higher gross yield with negative paired profit; score-profit conflict counts a chosen score above the A crop's score while paired profit is lower.

## Statistical analysis

Farmers' seasons are averaged first, then equally weighted within each seed (or within seed/zone). Median profit is the within-seed median of farmer mean profits. Harm means average profit difference from A < -1e-8 MAD. Negative-part loss averages max(-delta,0) over all farmers; conditional severity averages loss only over harmed farmers and is missing for zero-harm seeds. q10 is the within-seed 10th percentile of individual average effects. Switching frequency excludes season one. All CIs use independent seed summaries, never individual farmer-season rows.

Paired effect intervals: mean seed contrast ± t(.975,n−1) × sample SD/sqrt(n). Missing conditional-severity seeds are explicitly counted; one seed yields no interval. These intervals quantify simulator Monte Carlo variation, not real-world uncertainty. The primary family is 48 tests: 12 controlled contrasts (eight B-based, four A-exploration), two endpoints (mean profit, harm fraction relative to original A), two strata (ALL, ARID). Two-sided seed t p-values receive Holm correction over the entire family. Zero-variance contrasts use p=1 when zero and p=0 when deterministically nonzero. CI columns remain unadjusted and are not simultaneous confidence bounds. Other endpoints, zones and B-versus-exploratory-A contrasts are exploratory.

Harmed/benefited groups are selected on realized outcomes. Their switching, evidence-volume and decomposition differences cannot independently establish causal mechanisms. Transition tables distinguish baseline-versus-chosen crop substitutions (which sum to the paired effect) from actual previous-to-next crop switches (which describe temporal behavior). Counts pool descriptive observations and do not supply independent-sample inferential tests.

## Reproduction and limitations

Compressed decision JSONL and provenance ledgers plus outcome CSVs are saved per seed/arm. Gzip headers can contain times; deterministic replay refers to decompressed contents and model outcomes, not compressed-container bytes. Execution metadata records config, environment, source/input hashes, output hashes and git state. EXP001 A–D seed summaries are checked against committed primary evidence after the full run.

The diagnostic interventions may give contradictory answers. A filter effect bundles source quantity/composition changes; within-pool deduplication leaves cross-channel amplification; changing one profit mixture leaves other non-profit objectives. Nonlinear trajectories and interactions mean separate ablations do not uniquely allocate all harm to mechanisms. No field validation, welfare optimality or sustainability claim follows. A separate EXP003 sensitivity should consider the water lookup only after this diagnostic evidence is assessed; it is not implemented here.

Observation IDs are local to an arm/world; the arm is recorded in the containing file name. When combining ledgers, use (arm, seed, farmer, season), since a matched identity-season can have different potential outcomes in different arms. Evidence never crosses those worlds.
