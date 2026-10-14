# EXP004.1 validity and interpretation limits

## Which comparison answers which question?

The main panel holds system-wide acquisition at 20*m observations for all policies. Local-only recipients access their own m; sharing makes other acquired evidence accessible. A gain therefore establishes decision value from access and inference in this model, not extra system acquisition or superior multi-agent architecture. The m=3 versus m=1 contrast adds acquisition equally across all main policies. Three samples guarantee action coverage, not low uncertainty or optimal local decisions.

B2 and B3 have identical evidence and estimators, hence identical actions. Their decision-value architecture effect is exactly zero by design; any net-utility difference is packet accounting. H_known and H_fit use B3's same central cost model. Compare expected regret to assess estimators without topology costs. B1's distributed packet cost can make its net comparison with a centralized hierarchy partly architectural even when the expected-regret comparison is clean.

L_budget is a single-focal-agent reallocation diagnostic. Its total sample count, action schedule, variances and standardized noise match the distributed collection, but all samples are acquired in the focal context. Separate counterfactual trials are constructed for each recipient and averaged only for evaluation. Providing this much local evidence to everyone simultaneously would cost 20 times the original system acquisition budget. Free sensor relocation is a strong assumption; physical locations, acquisition prices, travel and sensing constraints are absent. Focal net utilities use a one-recipient service cost, not the main panel's amortized costs. Do not combine the two as a single deployment ranking.

## Model correctness versus practicality

All latent means have variance one, and cross-context correlation is 1-rho^2. Large rho means less similarity. The five tested values are a coarse grid, not an identified universal threshold. Different contexts are exchangeable with one common nonnegative off-diagonal correlation; pair-specific and negatively correlated relationships are not tested. Action/measurement primitives match across rho, while the latent outcome functions intentionally change. Within each rho, coverage and policies share identical evaluation outcomes.

H_known conditions on a correctly declared rho. It has no outcome oracle, but knowing the true hyperparameter is not a practical achievement. H_fit selects rho from current observations only on a fixed 21-point grid. It is a standard empirical-Bayes plug-in approximation: it ignores parameter uncertainty and can overfit. Three contexts and nine action/dimension combinations provide few independent covariance draws even with many repeated measurements. No history is accumulated; learning one stable rho over multiple past rounds could strengthen this baseline and remains untested.

The Gaussian family, zero prior mean, unit marginal scale, sensor variances, exact context labels, independent outcome dimensions and linear recipient utilities are public assumptions. Their correctness is favorable to Bayesian inference. There is no biased evidence, calibration failure, misreported provenance, context-label error, strategic reporting, nonstationarity, competition or policy-dependent sampling. Incorrect raw evidence and sender-preference transfer are not modeled. Different preferences only reweight vector-valued evidence; they do not make valid raw observations intrinsically harmful.

Communication costs use arbitrary utility units per payload, count metadata and computation as free, assume perfect routing and exclude broadcast compression and congestion. Policies do not adapt message volume to cost. Equal-weight averaging of normalized individual utilities is an assumed reporting convention, not validated interpersonal welfare. There is no agricultural production, water process or field calibration in this independent benchmark.

## Statistical and reproducibility limits

Seeds 100–119 are exploratory. Seeds 200–219 are reserved and protected from execution. Reports use independent seed summaries, not agent-round pseudoreplication. Intervals are unadjusted 95% t intervals over many contrasts; isolated interval exclusions do not imply familywise-confirmed discoveries. Subgroups may have fewer seed contributions when an objective group is absent. Harm refers to round-average expected utility; individual rounds can be harmed even when no averaged agent is harmed. Lower-tail utility is q10 across agent round averages, not the tail of realized shock outcomes.

Bayesian optimality is an expectation under the assumed prior/likelihood, not per-realization dominance or guaranteed finite-sample rankings. Equal performance at endpoints and a near-zero contrast must not be called uniform superiority. Threshold statements are restricted to sampled rho, coverage, noise and cost settings. Confirmation seeds must remain untouched until a separately prespecified evaluation.

Evidence-only interfaces and perturbation tests guard against accidental leakage but are not a hostile-code sandbox. Source/output hashes identify the executed implementation; cross-platform compression and floating-point behavior can differ. Raw ledgers contain separately scoped focal identities; equal numeric IDs from different rho, coverage or focal worlds must not be merged. Original EXP004 content and working-file hashes are independently checked.

## Before an adaptive selector

Prespecify the selector and its information/acquisition budget before using confirmation seeds. Add stronger estimation of rho from a separate observation-only calibration history, hyperparameter uncertainty, intermediate/noisy context descriptions, miscalibrated evidence and explicit sensing geography/cost. Compare decision estimators under matched communication topology and acquisition budgets. The present extension is a controlled baseline study, not a novel algorithm or evidence of agricultural validity.

Untransformed seed-level t intervals for bounded harm fractions may extend outside [0, 100] percent; the tables retain the prespecified approximation without clipping. Zero observed harm does not establish zero population risk.
