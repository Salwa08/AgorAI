# EXP004 validity limits and interpretation

## What this benchmark can establish

A policy intervention changes which already-collected raw observations are aggregated, how context is conditioned on, and how message deliveries are charged. Every policy is evaluated on the same full set of potential outcomes. Expected regret therefore isolates decision quality within the stated synthetic model; realized regret also contains hindsight selection on independent evaluation noise. Neither is agricultural profit or a field outcome.

Correct raw evidence from a different context need not be useful for the recipient. B1 deliberately ignores context labels, so its S2 likelihood is misspecified. That is an interpretation error involving environmental mismatch. It is not corruption of the raw observation, a biased sensor, or a preference mismatch. Every policy uses the recipient's own utility weights. The benchmark therefore does not yet test transfer of a sender's recommendation under incompatible preferences. Different preferences alone cannot invalidate an accurate vector-valued observation under the correct likelihood.

## Strong controls and remaining benchmark artifacts

B2 and B3 use identical unique evidence and the same posterior estimator. Their decisions must be identical; an intelligence advantage for centralization would be a bug here. Their net-utility difference is entirely imposed by the declared packet accounting: per-recipient deliveries versus uploads and replies. This is a transparent topology sensitivity, not an observed cost advantage of real servers. Routing metadata and computation are free, bandwidth and congestion absent, each central reply charged as one observation-equivalent, and central cost is shared equally. Broadcast, multicast, caching and compact sufficient statistics could change these comparisons.

S1 and S2 hold marginal outcome distributions, population, observation budgets, measurement noise and evaluation noise fixed. They change latent dependence between contexts. S1 makes categorical labels irrelevant; B2/B3 consequently discard usable evidence. S2 makes contexts independent; B1 consequently treats nonexchangeable observations as exchangeable. These deliberately simple endpoints reveal mechanisms but do not estimate how frequently either occurs in practice. Intermediate correlations, imperfect labels, continuous similarity, unequal context sizes and correctly specified hierarchical pooling remain untested.

The S0 control supplies identical public measurements to everyone before communication. Provenance deduplication must remove every redundant copy. It proves that the implementation does not manufacture information from repetition. It does not establish that real communication normally has no value; acquisition costs of public data are excluded equally across policies.

Reported uncertainty is the posterior variance of the chosen action's weighted expected outcome under the policy's assumed likelihood. It excludes evaluation noise; in S2, B1's variance can be falsely small because its cross-context pooling likelihood is wrong. A larger evidence count is therefore not a calibrated guarantee of decision accuracy.

All sensors are unbiased and their variances are perfectly calibrated. Noise sensitivity changes uncertainty, not dishonesty or bias. Independent Gaussian dimensions and a correct public N(0,1) marginal prior make Bayesian updates unusually tractable. A linear objective has no risk aversion, thresholds or hard constraints. Utilities are normalized abstract benefits and can be negative. Equal-weight mean utility across agents assumes interpersonal comparability on that normalization; it is a reporting convention, not an established welfare measure. Communication thresholds depend on this arbitrary scale. Contexts, quality, objectives and feasible actions are exogenous; no strategic reporting, competition, scarce resources, environmental feedback, delayed learning, policy-dependent sampling or nonstationarity is modeled.

The one-observation local baseline has severe action-coverage limits by design. This creates a genuine information-access opportunity, not proof that distributed computation is intrinsically better. Shared baselines see a larger total evidence pool and must be interpreted with that budget difference. Stronger local sensing and equal-total-acquisition-budget comparisons are needed before a new selector's superiority claim. B2 and B3 are the only evidence/estimator-matched architecture comparison here.

## Statistical scope

The 20 seeds are exploratory replicates, not held-out confirmation. Each seed redraws population and all round worlds; rounds are independent conditional on the fixed seed population. Within-seed agents share latent environments. Confidence intervals use seed-level quantities, not thousands of correlated agent-round records. Many metrics, costs, subgroups and scenarios are reported with unadjusted intervals; they do not supply familywise significance guarantees. Harm is defined by round-average expected utility, while round_harmed separately describes individual decisions. A favorable overall mean can coexist with harmed agents. Lower-tail utility is the within-seed q10 of agent round means, not a tail quantile of individual realized shocks.

Deterministic replay is expected on the recorded numerical stack; different numerical libraries may change ties at floating-point precision. The evidence-only API makes accidental leakage testable but is not a security boundary against malicious code. Latent arrays are deliberately saved for independent evaluation and must stay out of future policy fitting. A new method should use separate development/validation worlds and untouched final evaluation seeds.

## Readiness

This is a minimal controlled testbed for a later information-selection mechanism once the documented controls pass. It is not yet a sufficient suite for a broad claim of goal-aware superiority. Before such a comparison, prespecify the new selector, its acquisition/transmission budget, stronger local and hierarchical baselines, and held-out seeds; add intermediate context similarity and miscalibrated or biased evidence. Keep sender preference mismatch distinct from environmental relevance. Do not tune a method on the pilot and present the same seeds as confirmation.

No reinforcement learning, novel goal-aware method, EXP003 implementation, agricultural data changes or water-model corrections are included.

## Measured pilot assessment and unexpected findings

At noise .5, S1 always-sharing reduces mean expected regret by 0.34799 [0.33426, 0.36171]. The same aggregation in S2 improves utility only 0.02243 [0.01140, 0.03346] and harms 38.5% [32.81%, 44.19%] of agents in round-average expected utility. Context-filtered sharing improves S2 utility by 0.28886 [0.28008, 0.29764], with no agents harmed by the round-average criterion in these 20 seeds. This zero observed harm is not a guarantee for every individual decision or future seed.

The prespecified context mismatch did **not** make naive pooling worse on average than the sparse local baseline at zero cost. It caused substantial individual harm and a large loss relative to compatible pooling. This is a substantive limit on the negative-transfer conclusion, not a reason to retune the pilot. The one-observation local baseline remains weak; there is no demonstrated aggregate zero-cost local-only victory in S1/S2. Local-only is strictly best in S0 at positive costs, and beats naive pooling in S2 at cost .01. All sanity checks passed; no generative parameter was changed after observing results.

At noise 1.5, the mean S1 B1 utility gain is larger, 0.38427 [0.37117, 0.39737], than at noise .5. More noise does not mechanically remove the value of sharing: it also weakens the local baseline, while independent evidence can average noise. This is a relative gain, not evidence that high noise improves absolute decision quality. The corresponding S2 B1 gain is 0.06868 [0.05882, 0.07853], with 23.5% [20.10%, 26.90%] harmed. The pilot thus tests interactions of uncertainty and coverage, not a universal monotone noise rule.

At noise .5 and cost .01, S2 B1 net gain becomes -0.16757 [-0.17860, -0.15654]; B3 net gain is +0.26886 [0.26008, 0.27764]. B3 is favored by its declared upload/reply cost model, while its decisions exactly match B2. S0 gives zero utility gain for all sharing policies at both noise levels, and all positive costs are pure losses. These help/harm/no-gain cases are attributable to stated evidence and accounting mechanisms, but their prevalence and cost magnitudes are synthetic.

The benchmark is ready for **development and controlled testing** of a later selector, subject to the broader validity work above. It is not sufficient on its own to claim that such a selector is superior or useful in agriculture.
