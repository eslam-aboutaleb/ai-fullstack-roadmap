<!-- chapter: evaluation -->

# How are Recall@K, Precision@K, and MRR calculated?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: evaluation
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**Retrieval metrics describe a ranking relative to declared relevance labels.** For top-k unique retrieved IDs R and relevant IDs G, Recall@k=|R intersect G|/|G| and Precision@k=|R intersect G|/|R| when R is the returned top-k set. State whether a fixed-k denominator is used instead; do not switch conventions between systems. Reciprocal rank is 1/r for the first relevant hit at rank r, or zero if none. MRR averages reciprocal rank across a declared query set.

For graded relevance g_i at rank i, one common DCG is sum((2^g_i-1)/log2(i+1)); nDCG divides by the ideal DCG from the same labels. Declare the gain convention. With binary relevance, one relevant item at rank 2 has Recall=1, RR=1/2 and nDCG=1/log2(3), approximately 0.63093. If two gold items exist but only one is retrieved, recall is 1/2 even if that item ranks first. A duplicate relevant ID must not count twice.

**Unanswerable queries need a different oracle.** An empty gold set makes recall undefined rather than automatically perfect. Report it as not applicable and evaluate correct abstention or unsupported-answer rate. Missing labels are not proof of irrelevance: pool candidate results from several methods, adjudicate scope/revision/claim applicability and record disagreement. Keep question IDs stable and group near-duplicates by document/customer/time when splitting data so copied examples do not leak across train, tuning and held-out evaluation.

`policy_assistant_project.py` fixes case IDs and gold answer spans independently of prediction. Its arithmetic test checks rank-two nDCG against a hand-calculated constant, and its deliberate missing-exception regression must fail. The fixture is small and English-only; 8/8 is not an estimate of broad production accuracy. Report counts and per-case outcomes, not a misleading confidence claim. On a larger release set, compare paired old/new outcomes on identical queries, inspect critical regressions and use uncertainty methods appropriate to correlated cases rather than treating every paraphrase as an independent customer.

## Why

For ranking [noise,gold], binary relevance gives Recall=1, RR=0.5 and nDCG approximately 0.63093. The independent arithmetic oracle would catch an implementation that incorrectly uses rank zero or duplicate hits.

## Worked Case

For ranking [noise,gold], binary relevance gives Recall=1, RR=0.5 and nDCG approximately 0.63093. The independent arithmetic oracle would catch an implementation that incorrectly uses rank zero or duplicate hits.

## Risk

A label set that ignores owner or revision can reward a forbidden result. Averaging unanswerable recall as one inflates quality without improving any answer.

## Trade-off

MRR emphasizes the first relevant hit, while nDCG captures position and graded relevance. Neither measures whether the final answer follows the evidence or whether latency is acceptable.

## Try This

Write the three metric formulas before running the capstone. Change a prediction to rank the gold span second, then duplicate the ID and verify that malformed ranking is rejected rather than rewarded.

## Follow-ups

### What if experts disagree whether a passage is relevant?

Record the disagreement, question conditions and adjudication rule. Evaluate sensitivity under plausible labels or graded relevance; do not hide uncertain labels behind a falsely exact benchmark score.

## Citations

- https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html
- https://trec.nist.gov/overview.html

# How should I create a useful evaluation dataset?

## Answer

Include realistic questions, expected sources or spans, answerability, permissions, and failure cases. Cover exact identifiers, paraphrases, ambiguous requests, stale knowledge rules, multi-document synthesis, multilingual inputs, and unanswerable questions. Keep a held-out set separate from tuning examples.

## Why

The evaluation modules accept datasets and injected retrieval or answer functions, so the same cases can compare chunkers, profiles, strategies, and host generation knowledge rules. Record the corpus revision and configuration alongside each run.

## Risk

Synthetic questions can mirror the source wording too closely and overstate quality. Data leakage from tuning into evaluation also produces misleading improvements.

## Trade-off

Human-labeled cases cost effort but reveal product relevance. Synthetic expansion is useful when reviewed and balanced against real user questions.

## Try This

Author 30 questions with source-level gold evidence and five deliberate non-answerable cases. Have another reviewer check labels without seeing your retrieval output.

# Why is retrieval-only evaluation useful before generation exists?

## Answer

It isolates whether the system can locate supporting material. If relevant passages never reach the candidate or evidence set, a better generator cannot reliably repair that failure. Retrieval-only runs are also cheaper and more deterministic than end-to-end model evaluation.

## Why

The runner supports distinct evaluation modes and accepts host callbacks. the retrieval service can be evaluated as a subsystem without pretending it ships a complete production chat application.

## Risk

Strong retrieval metrics can hide poor evidence budgeting, unsupported claims, and an unhelpful UI. They are a stage gate, not the final product score.

## Trade-off

Early isolation speeds diagnosis and reduces API cost, while end-to-end testing is still needed to assess user outcomes. Use both at different stages of development.

## Try This

Establish a retrieval baseline before adding a generator. Record cases where the correct source is retrieved but later excluded from the evidence budget.

# How do heuristic answer scoring and LLM-as-judge differ?

## Answer

Heuristic scoring uses deterministic text-overlap signals and is cheap to run offline. LLM-as-judge asks a configured model to assess qualities such as faithfulness, relevance, completeness, and conciseness. Neither is an infallible measure of truth.

## Why

The corresponding service module implements both strategies with standardized score containers. Heuristics provide a stable baseline; judges can assess richer language relationships but add provider cost and evaluation-model variability.

## Risk

Overlap can reward copying a wrong answer, while judges can exhibit bias, prompt sensitivity, and correlated mistakes. A judge may also be influenced by adversarial content in the answer or evidence.

## Trade-off

Use deterministic metrics for broad regression feedback and calibrated human review for critical cases. Model judging can expand coverage if its agreement with humans is measured.

## Try This

Score a faithful paraphrase, a copied incorrect answer, and a fluent unsupported answer using both approaches. Explain disagreements rather than averaging them away.

# What does a high-value test strategy look like for this reference design?

## Answer

Test behavioral invariants at seams: no mutation after invalid preparation, scope constraints on both stages, explicit backend failure, stale-worker rejection, revision-correct lookup, and safe repeated job processing. Use focused fakes for deterministic races and real adapter tests for actual storage semantics.

## Why

The test suite has targeted modules for ingestion locking, embedding execution, retrieval capabilities, and sync coordination. These boundaries are more consequential than mirroring every helper's internal implementation.

## Risk

Passing fake-based tests cannot prove production rollback, SQL locking, or vendor filter behavior. Conversely, an enormous end-to-end suite can be slow and poor at locating failures.

## Trade-off

A layered mix gives fast feedback and credible integration evidence. Choose the smallest test that can actually falsify the relevant guarantee.

## Try This

For one transaction guarantee and one retrieval filter guarantee, state which test needs a real database and which can use a controlled fake.

# What is the difference between liveness, readiness, and degraded health?

## Answer

Liveness asks whether a process can run. Readiness asks whether it can serve its intended work. Degraded health means some useful behavior remains but a dependency or freshness condition is impaired. One healthy HTTP process does not prove its index is current or its embedding provider works.

## Why

A health collector collects configuration, connectivity, counts, sync, job, and evaluation information. a health report exposes distinctions that a host can map to probes and user-facing status.

## Risk

An expensive consistency scan in every readiness probe can overload the database. A permissive count returning zero after an error can also mask a dependency failure if interpreted carelessly.

## Trade-off

Deeper checks improve diagnosis and cost more I/O. Separate cheap frequent probes from scheduled expensive consistency checks.

## Try This

Define probe behavior when the process is alive, the vector store is down, and the index is stale but readable. Explain whether traffic should continue in each case.

# What operational signals should be monitored?

## Answer

Track ingestion lag, scan authority failures, embedding retries and queue pressure, active-generation age, job backlog and oldest age, search latency, empty and failed retrieval rates, evidence truncation, and quality regressions. Each signal should connect to a user-visible consequence.

## Why

Events and health checks expose stage and lifecycle information. Optional OpenTelemetry integration can connect this information to a host's tracing system without making it a mandatory runtime dependency.

## Risk

Large numbers of document IDs or tenant IDs as metric labels create cardinality and privacy problems. Raw query logging can expose sensitive user intent.

## Trade-off

Aggregated metrics are scalable but less detailed; controlled traces aid diagnosis. Correlate with sanitized operation identifiers and use retention knowledge rules appropriate to the data.

## Try This

Define an alert for rising stale-index age and another for rising backend-failure rate. Explain why their remediation differs even if both reduce answer quality.

# How should a system meet an end-to-end latency target?

## Answer

Allocate a request deadline across stages, measure tail latency, and propagate cancellation and remaining time. Per-call timeouts and retry ceilings are ingredients, not an end-to-end deadline. Query variants, sequential stages, reranking, and generation can each consume the budget.

## Why

A bounded embedding executor and query transformation expose local bounds; telemetry gives stage durations. The host must compose them into a product-level deadline and decide which optional stages can be skipped safely.

## Risk

Summing independent p95 measurements does not yield an exact request p95, and a timeout can leave remote work running. Retry storms can worsen the same overload they attempt to recover from.

## Trade-off

Tight deadlines improve responsiveness while reducing recovery and ranking opportunities. A slower asynchronous ingestion path can tolerate different retry policy from an interactive search.

## Try This

Trace a request with one retry and two query variants. Compare actual elapsed time with your budget and identify which optional stage should be shed first.

# How do you roll out a retrieval change safely?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: evaluation
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**A retrieval rollout is a controlled change to a measurable evidence path.** Offline evaluation compares candidate and baseline on the same frozen corpus, scope rules and labeled questions before traffic exposure. Online evaluation observes real product outcomes under an explicit allocation and privacy policy. A click or thumbs-up is not automatically a correctness label, and live experimentation cannot justify knowingly exposing private data or unsafe policy decisions.

Create a run manifest with code/configuration, source snapshot, embedding/reranker profiles, gold-set version and threshold policy. Report paired per-case changes: which supported answers improved, which became false refusals, which lost decisive evidence and whether any forbidden source appeared. Keep critical owner/citation failures as hard blockers independently of average relevance. Tune on development data; reserve a held-out release set so repeated threshold adjustments cannot memorize the acceptance answers.

**Trace the failure before changing the model.** A request timeline should distinguish queue wait, source search, reranking, context preparation, model first token and completion. Propagate request/attempt IDs and record safe source revision IDs, counts, stop reason and usage categories. Avoid raw prompts, document bodies and credentials in ordinary telemetry. Stage p95 values do not add into an end-to-end p95; measure the complete request distribution as well. A faster answer that omits the policy exception is a quality regression.

Deploy a reversible configuration/index version, shadow where appropriate without effects, then a limited canary with scope-aware quality, latency, cost and error budgets. Define sample requirements and rollback triggers in advance. Keep old artifacts compatible long enough for rollback; a schema migration or deleted-source restoration can make a naive rollback unsafe. The local capstone's missing-exception mutant demonstrates a regression gate: baseline passes, the candidate fails and the repaired candidate restores the required span. It proves that bounded fixture behavior, not actual customer success or production latency.

## Why

A candidate returns faster because it excludes the final-sale exception. Baseline and candidate are scored on identical gold cases; the unsupported answer blocks release despite the latency improvement.

## Worked Case

A candidate returns faster because it excludes the final-sale exception. Baseline and candidate are scored on identical gold cases; the unsupported answer blocks release despite the latency improvement.

## Risk

A mean quality gain can hide a severe minority or permission regression. Logging sensitive text to diagnose that regression can itself create another disclosure.

## Trade-off

Shadow traffic avoids user-visible answers but still incurs cost and may send private data to a model. Canary exposure requires a safe task, explicit gates and a tested rollback path.

## Try This

Run the capstone baseline, deliberate regression and repair. Produce a release note listing changed cases, critical blockers, manifest hashes and a rollback decision; keep measured and proposed latency evidence separate.

## Follow-ups

### What if online success improves while the held-out policy cases regress?

Investigate metric mismatch and slice differences before promotion. Business engagement cannot overrule unauthorized disclosure or unsupported critical decisions; preserve the hard gate and obtain better representative labels.

## Citations

- https://sre.google/sre-book/monitoring-distributed-systems/
- https://opentelemetry.io/docs/security/handling-sensitive-data/

# How should you investigate quality drift over time?

## Answer

Separate source drift, query-distribution drift, model or provider changes, extraction changes, index freshness, and application-policy changes. Re-run a stable benchmark and inspect newly failing real-world cases. A single aggregate score rarely identifies the cause.

## Why

Profiles and ingestion snapshots record important configuration identity, while telemetry and evaluation capture operational and quality observations. A host should retain run metadata tying them together.

## Risk

Silent provider updates or hidden preprocessing changes may not be visible unless a model revision and adapter configuration are recorded. Privacy limits also constrain how production questions can be retained for analysis.

## Trade-off

Stable benchmarks preserve comparability but can become unrepresentative. Add reviewed new cases while keeping a fixed core set for historical comparison.

## Try This

Simulate an unchanged corpus with a changed query mix, then a changed extractor with the old query mix. Show how you would distinguish the resulting metric changes.

# Why must retrieval relevance, answer support and correct abstention be scored separately?

<!-- meta
domain: ai-rag
subdomain: evaluation
module: evaluation
concept: Why must retrieval relevance, answer support and correct abstention be scored separately?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A system receives credit for citing a relevant document even though its actual answer contradicts that document.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

They represent different failure boundaries. A retriever may return relevant text that a model misuses, while a model may abstain correctly when no answer exists. Define ground truth, denominators and empty-gold behavior explicitly. Keep critical authority failures outside a compensating average and compare candidate and baseline on matched cases.

Concrete engineering case: A system receives credit for citing a relevant document even though its actual answer contradicts that document.

Boundary defense: Usually not. Inspect stage-specific outcomes and error slices to locate whether retrieval, applicability, generation or the grader failed.

## Spoken Summary

They represent different failure boundaries. A retriever may return relevant text that a model misuses, while a model may abstain correctly when no answer exists. Define ground truth, denominators and empty-gold behavior explicitly. Keep critical authority failures outside a compensating average and compare candidate and baseline on matched cases.

## Why

They represent different failure boundaries. A retriever may return relevant text that a model misuses, while a model may abstain correctly when no answer exists. Define ground truth, denominators and empty-gold behavior explicitly. Keep critical authority failures outside a compensating average and compare candidate and baseline on matched cases.

## Production Case

A system receives credit for citing a relevant document even though its actual answer contradicts that document.

## Risk

A system receives credit for citing a relevant document even though its actual answer contradicts that document.

## Trade-off

Usually not. Inspect stage-specific outcomes and error slices to locate whether retrieval, applicability, generation or the grader failed.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: evaluation**: They represent different failure boundaries.

## Alternatives

- Usually not. Inspect stage-specific outcomes and error slices to locate whether retrieval, applicability, generation or the grader failed.

## Pitfalls

- A system receives credit for citing a relevant document even though its actual answer contradicts that document.

## Follow-ups

### Does one composite score explain the repair?

Usually not. Inspect stage-specific outcomes and error slices to locate whether retrieval, applicability, generation or the grader failed.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A system receives credit for citing a relevant document even though its actual answer contradicts that document.",
  "required_decision": "They represent different failure boundaries"
}
```

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html

# How do incomplete relevance labels and unanswerable questions distort retrieval metrics?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: evaluation
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Retrieval metrics assume a relevance definition and a judged candidate population. If a useful document is unjudged, treating it as irrelevant can penalize a legitimate result. Conversely, weak labels can reward a related passage that does not answer the question. Include unanswerable, conflicting and permission-denied cases with their proper expected behavior. Report candidate depth and ranking cutoffs, inspect disagreements and distinguish missing labels from actual failures. A single aggregate score cannot describe every operational risk.

## Why

A query has two valid supporting documents but only one is labeled. A new retriever returns the other document and appears worse until the judgment set is reviewed against the same relevance criteria.

## Worked Case

A query has two valid supporting documents but only one is labeled. A new retriever returns the other document and appears worse until the judgment set is reviewed against the same relevance criteria.

## Risk

Unjudged data can be mistaken for negative ground truth.

## Trade-off

Broader judgment improves validity at review cost; report uncertainty and sampling scope.

## Try This

Review a metric regression and separate true misses from incomplete labels.

## Citations

- https://scikit-learn.org/stable/common_pitfalls.html
- https://scikit-learn.org/stable/modules/cross_validation.html
