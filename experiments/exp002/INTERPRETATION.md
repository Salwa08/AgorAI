# EXP002 interpretation and EXP003 recommendation

## Answer to the research question

Some farmers choose higher-scoring, higher-tonnage crops with lower economic value. The strongest tested population-level contributor is the zone yield/profit scoring mixture. Information-induced harm is not synonymous with cross-zone negative transfer: default B has no foreign-zone observations. Received observations entering the experience score can cause particular harmful switches, but removing that pathway does not reliably improve average outcomes. The experiments do not uniquely assign every loss to one mechanism.

All numbers below are conditional on this simulator, 20 seeds, fixed primary economics and 30 seasons. Profit units are MAD per farmer-season. Reported confidence intervals are seed-level and unadjusted; cited Holm p-values belong to the prespecified 48-test family. Other subgroup/case/transition findings are exploratory.

## H1 — objective mismatch: strongest supported contributor

Changing only the zone mixture from 60% normalized yield / 40% nonnegative normalized profit to profit-only increases overall mean profit by **21,364 [17,697, 25,031]** relative to B (Holm p=7.91e-9). Harm falls **16.7 percentage points [14.5, 18.9]**, from 26.5% to 9.8% (Holm p=8.12e-11). In ARID, the change is **+13,374 [10,524, 16,225]** (Holm p=2.61e-7), taking B−A from −5,911 to **+7,463 [5,076, 9,851]**. ARID harm falls from 39.12% to 13.21%. This is a controlled effect of that scoring component, not a proof that every non-profit goal is irrational or that profit should replace all objectives.

Of B farmer-season losses, 94.44% on average across seeds also have higher gross yield; in ARID it is 99.96%. Every losing B choice scores above the contemporaneously evaluated A crop. The latter is partly mechanical because B chooses an argmax, so it is a consistency check, not independent hypothesis confirmation. The controlled mixture intervention provides the stronger evidence.

ARID's mean profit loss decomposes into **+3,690 yield-related revenue, −9,761 price-related revenue, +160 cost savings = −5,911**. This symmetric accounting decomposition is not causal mediation. The substitution from A's almonds to B's barley contributes **−8,465 [−10,107, −6,822]** to ARID's total mean effect, offset by beneficial substitutions. Tonnage and price matter together; more tonnes alone can lower profit.

The intervention does not eliminate harm or make agents optimal. It also changes gross yield and explores different endogenous histories; interactions with other objectives remain unresolved. Descriptively, it rescues 66.0% [59.6%,72.4%] of originally harmed identities on a seed-average basis and newly harms 0.7% of all identities. These are outcome-selected subgroup summaries, not separately prespecified tests.

## H2 — environmental context mismatch: not the explanation for default harm

Default B contains **zero cross-zone observations**. Farms within a zone have identical modeled soil/climate, although land, goals, cost noise and suitability noise differ. Cross-zone environmental mismatch therefore cannot explain the reproduced default losses. Unmodeled microclimate mismatch is untestable here.

Removing same-zone filtering reduces overall harm by **3.30 pp [1.74,4.86]** (Holm p=.0082) and ARID harm by **12.44 pp [7.36,17.52]** (Holm p=.0019). Its overall mean-profit change is only +108 [−2,070,2,286], Holm p=1. ARID's larger mean gain is uncertain after the family correction (Holm p=.623). Thus unrestricted information is not uniformly harmful in this model.

The prespecified ecological filter admits only WARM↔COOL semi-arid cross-zone links. It reduces overall mean profit by **3,588 [2,058,5,118]** (Holm p=.0030), while its ARID effect is exactly zero because ARID eligibility is unchanged. This contradicts any assumption that a plausible context filter must improve outcomes. Filter interventions change information quantity, composition and dynamics as well as context; they do not uniquely isolate environmental mismatch.

## H3 — mixed memory and duplication: local pathways, weak average-remedy evidence

Default B decisions see about 2.76 duplicated neighbor appearances and 9.51 received experience observations on average; counting reuse across channels gives 21.42 duplicate appearances. This establishes multiplicity, not its harmfulness.

Deduplication changes mean profit by **+433 [−215,1,080]**, Holm p=1, and changes the mean harmed fraction by **0 pp [−0.30,0.30]**. Restricting the experience score to actual own harvests gives **+522 [−1,206,2,249]**, Holm p=1, while harm changes by +1.05 pp [−0.06,2.16], Holm p=1. Neither intervention is supported as a broad remedy. Deduplication is within scoring pools and leaves cross-channel amplification intact; its null average result does not test all forms of contamination.

There is nevertheless a directly observed individual pathway. In the post-hoc illustration seed 0, farmer 83, ARID, season 2, B switches almonds→barley. Almonds' score is 1.32477; barley's is 1.46091, including a **.25 experience bonus based on received observations**. Barley's ecological suitability is actually lower (.94091 vs .99228). The switch raises yield by .33244 t/ha but changes profit from +22,868.50 under A to −11,765.87 under B (−34,634.37). Both the own-memory-only and profit-only-zone interventions retain almonds and avoid this loss. Deduplication and per-ha normalization retain the harmful barley choice. All arms have identical first-season outcomes, so this early case isolates the scoring interventions before divergent histories develop. See case_study.json for complete traces. The case was chosen after observing outcomes and is not a prevalence estimate.

Across all farmers, own-memory separation descriptively rescues 5.45% of originally harmed farmers but newly harms 2.45% of all farmers. A mechanism can cause particular losses without its removal improving aggregate welfare. No claim of zero individual effect follows from a near-zero mean.

## H4 — deficient independent exploration: real baseline limitation, incomplete explanation

Original A never switches. Epsilon-greedy makes alternatives observable and changes the comparison, but no tested rate eliminates B's overall advantage: B minus the exploratory baseline remains about **+32,045 to +34,033** MAD, with positive exploratory 95% intervals at all four rates.

Independent exploration improves overall mean profit by roughly +1,206 to +3,194 MAD; none of these overall mean improvements passes the 48-test Holm correction. In ARID, rates .05, .10 and .20 do improve mean profit after correction. At .20 the ARID A improvement is **+13,426 [9,791,17,061]** (Holm p<.0001). Relative to these stronger independent ARID baselines, B becomes *more* disadvantageous, reaching −19,337 [−23,524,−15,150] at epsilon .20. Exploration also harms 20.35%–41.90% of overall identities versus deterministic A, so it is not uniformly beneficial.

This supports treating no-exploration A as a limited comparator, but does not explain away information harm or the overall sharing benefit. Uniform ongoing exploration is only one diagnostic policy and retains V1's heuristic objective and 30-season horizon.

## H5 — total-profit signal bias: present algebraically, no supported average remedy

The normalization test confirms that mean individual profit/ha replaces mean total profit correctly. Its overall mean effect is **−298 [−1,406,810]**, Holm p=1, and ARID effect **+251 [−849,1,351]**, Holm p=1. Harm changes are likewise not significant after correction. This does not support total-farm-profit weighting as the dominant explanation for average loss. It still changes some trajectories: descriptively, 4.26% of originally harmed farmers are rescued and 1.30% of all farmers become newly harmed. Other contexts or interactions with score objectives remain untested.

## Switching, timing and signal associations

In ARID, harmed B farmers switch in 5.51% of eligible seasons, benefited farmers in 8.92%, and unchanged farmers in 0%. Thus “harmed farmers switch more often” is not supported relative to benefited farmers. Their average land sizes are 5.17 versus 5.44 ha; paired land is identical in A/B, so land imbalance is not a confounder of the within-identity effect. Harmed farmers receive more experience observations (11.58 vs 6.56) and neighbor duplicates (3.01 vs 1.54), but those groups are selected on outcomes and cannot identify a harmful dose effect.

ARID's average B−A profit difference is zero in season 1, +641 in season 2, −4,875 in season 5, −6,863 in season 10, −6,987 in season 20 and −6,237 in season 30. Harm therefore emerges after early sharing and persists despite low later switching. Season-level harmed fraction is distinct from the fraction harmed in across-season mean profit. Crop substitutions and temporal transitions are separately exported.

## Prioritized recommendation for EXP003 — proposal only

1. **Test objective alignment and mixed-memory interaction first.** Prespecify a small factorial study crossing zone yield/profit mixture with separate own/social memory, retaining the same exogenous pairing. Use several fixed mixture weights, explicit farmer goal profiles, profit/ha and gross yield endpoints, and a policy that uses past observations only. Include an independent exploration comparator. This distinguishes the strongly supported zone-objective contribution from the demonstrated local memory pathway and tests whether their joint effects are additive, substitutive or antagonistic. Reserve new seeds for confirmation rather than choosing weights from EXP002 winners.
2. **Evaluate support and selection in information availability.** Compare matched-volume same-zone/unrestricted evidence and stratify by goal/cost similarity to separate context from information quantity. Preserve negative controls; the present ecological filter worsened profit.
3. **Run the water-model correction as a separate sensitivity.** Correct the nested crop-water lookup and specify whether irrigation affects yield and billed costs, with reviewed physical assumptions. Do not combine this with the objective test: current water outcomes cannot validate sustainability. Also examine perennial switching and parameter evidence before agricultural interpretation.

No EXP003 implementation is included. The residual 9.8% harm under profit-only zone scoring, weak aggregate effects for several plausible fixes, and untested interactions prevent a complete attribution of all losses. The defensible conclusion is that objective mismatch and some mixed-memory pathways causally contribute within this simulator, while cross-zone environmental mismatch is not the source of default EXP001 harm.
