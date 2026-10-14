# EXP004.1 interpretation

These are exploratory synthetic-model findings from seeds 100-119, with 20 independent seed replicates. All quoted intervals are paired, unadjusted 95% seed-level t intervals. The frozen protocol preceded implementation and execution. Confirmation seeds 200-219 were not run. Full metrics, subgroup results and provenance are in RESULTS.md and results/exploratory/summary.zip.

## 1. Does sharing help with adequate local evidence?

Yes for context-aware sharing in this tested model, with a substantially smaller gain. Covering all three actions once reduces local-only expected regret from approximately .34 to .067-.068. Fitted partial pooling (H_fit) still reduces regret by .0621-.0657 across the five rho settings. At rho=.5 its reduction is .06210 [.05943, .06476], versus .30970 [.30010, .31930] with sparse local coverage. The paired reduction in the sharing gain is .24760 [.23826, .25694]. One noisy observation per action is full coverage, not unlimited or fully adequate evidence.

Costs change the answer. At .01 per packet, H_fit retains a net utility advantage of about .022-.026 with full coverage under the assumed central upload/reply topology. Distributed unconditional sharing and exact-context filtering have negative net advantages at that coverage because their assumed packet volumes are higher. These are accounting assumptions, not measured network costs. All three prespecified costs are retained in the machine-readable results.

## 2. Does partial pooling beat both extremes?

With sparse coverage, observation-fitted H_fit beats unconditional pooling (B1) and strict context filtering (B2) at rho=.25, .5 and .75. At rho=.5, regret contrasts are -.03847 [-.04056, -.03638] versus B1 and -.02053 [-.02318, -.01789] versus B2.

With full coverage, the advantage over filtering is small: -.00061 [-.00092, -.00029] at rho=.25 and -.00022 [-.00033, -.00010] at rho=.5. At rho=.75 and 1 the H_fit-versus-B2 intervals include zero. There is no uniform superiority: H_fit is slightly worse than B1 at rho=0, and with sparse coverage is worse than B2 at rho=1 by .00230 [.00105, .00355]. Known-parameter H_known exactly matches B1 at rho=0 and B2 at rho=1. Its occasional tiny finite-sample disadvantage at other settings is retained, not tuned away. The practical fitted estimator and the parameter-oracle diagnostic are separate results.

## 3. When does cross-context transfer become harmful?

The answer depends on the comparator and coverage. Distinct-context latent correlation is 1-rho^2, so increasing rho decreases similarity. Against strict filtering, unconditional pooling becomes worse at the sampled rho=.5 with sparse coverage and already at rho=.25 with full coverage. Against local-only, its mean regret remains lower throughout the sparse grid, but with full coverage becomes worse at rho=.75 and 1. At rho=.75 the excess regret is .06462 [.05810, .07113]; 82.25% [78.42%, 86.08%] of agents have lower round-average expected utility than their paired local baseline. At rho=1, 98.5% are harmed under full coverage.

Mean gains can hide individual harm: at rho=.5 with full coverage, unconditional pooling still improves mean regret by .01160 [.00810, .01510], yet harms 52.75% [50.29%, 55.21%] of agents. These are sampled settings, not universal thresholds or evidence that correctly modeled raw information intrinsically harms a Bayesian decision maker.

## 4. Evidence quantity versus multi-agent architecture

The main panel has the same total acquisition budget across policies; sharing expands each recipient's access to evidence already collected. Increasing local coverage substantially shrinks its benefit. B2 and centralized B3 have exactly identical decisions across every saved world: there is zero decision-value architecture effect in that controlled comparison. Their net difference comes solely from stipulated communication accounting.

In the separate equal-acquisition focal diagnostic, relocating all observations into the recipient's context exactly matches B1 and H_known when rho=0 and outperforms both hierarchical policies at every tested positive rho. For example, at rho=.5 with full coverage, local minus H_fit regret is -.00349 [-.00392, -.00305]. This supports an evidence-access and relevance explanation, not an inherent multi-agent advantage. It does not identify a single universal percentage attributable to architecture or quantity. The relocation assumes free local sensing, and cannot supply every agent this budget simultaneously: doing so would multiply acquisition by 20. Distributed collection may remain useful when sensing locations are constrained, which this model does not test.

## 5. What remains before an adaptive selector?

Prespecify a selector, its information and communication budgets, and confirmation analysis before unlocking the reserved seeds. Strengthen the deployable baseline with observation-only calibration history and hyperparameter uncertainty. Test noisy context labels, misspecified covariance and sensor variances, nonstationarity, realistic acquisition geography, and comparisons under the same communication topology. Current rho estimation uses only nine independent action/dimension covariance draws per round and no accumulated history. No winner should be selected from this exploration and presented as confirmed without fresh evaluation.

## Validation and limits

All 45 automated tests passed, including the 25 original tests. Full output verification passed for 200 worlds, 2,400,000 main decisions and 400,000 separate focal decisions: hashes, frozen EXP004 content, matched worlds, endpoint and architecture parity, raw regret/agent means, and acquisition/communication accounting. Provenance snapshots check the first round of every world; all ledger bytes are hashed. Raw outputs remain local and reproducible; the compact archive retains all summaries and metadata.

The experiment has a correctly specified Gaussian observation model, public exact context labels and sensor variances, and linear utilities. Unadjusted intervals over many comparisons are exploratory. T intervals for bounded harm fractions can extend below 0% or above 100%; these are approximation artifacts, not possible fractions. Zero observed harm is not proof of zero population risk. No agricultural validity or algorithmic novelty is claimed. See LIMITATIONS.md for the full scope of these conclusions.
