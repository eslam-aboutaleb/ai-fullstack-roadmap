<!-- chapter: evidence -->

# Why does evidence assembly deserve a separate module?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: evidence
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**A separate evidence-assembly module makes source eligibility, context budgeting and claim provenance explicit before generation.** It accepts permitted ranked passages, preserves their revisions/spans, selects a bounded sufficient set and returns a traceable evidence packet. Retrieval ranking and answer wording can then change without silently changing these invariants.

**Evidence is information supporting a specific claim under a scope and time.** A citation names a source; grounding requires that the cited span actually supports the answer. Correctness asks whether the answer is right for the task. Faithfulness asks whether its claims follow from the supplied evidence. Relevance asks whether it addresses the question. These can disagree: faithfully quoting an obsolete policy can still give a wrong current answer.

Carry a stable document/revision/span identity, content digest and trusted eligibility metadata through retrieval to the answer. At citation resolution, check owner access, active revision and deletion status again when stores or caches may have changed. Compare the generated claim with the span's actual conditions and exceptions. Citation membership is an important structural check, but cannot establish entailment. The capstone's exact sentence comparison is an intentionally narrow independent support oracle for authored policy answers; it is not a general natural-language judge.

**Work the exception.** The general rule permits returns within 30 days; the final-sale clause forbids returns for final-sale items. For a final-sale question, citing the real general-policy sentence is insufficient. Dropping the exception is a critical wrong answer even if retrieval recall across other questions is high. Require decisive conditions in the answer or abstain with a useful explanation of missing evidence. Do not answer 'ineligible' merely because retrieval was empty.

Score supported answer, unsupported answer, correct abstention and false refusal separately. False refusal is abstaining on a genuinely answerable case; unsupported answering is giving a substantive answer without the required evidence. Denominators must be stated: answerable versus unanswerable cases are different populations. Include cross-owner requests, outdated revisions, contradictions and unsupported questions in the gold set. A release gate can reject any owner leak or critical unsupported policy decision while still reporting average quality. Optional generative adapters must use the same scoped evidence and be evaluated against independently adjudicated claims, not just JSON validity.

## Why

A final-sale customer receives the real 30-day general rule with a valid URL. The citation exists but does not support that customer eligibility; the independent expected span makes this an explicit failed case.

## Worked Case

A final-sale customer receives the real 30-day general rule with a valid URL. The citation exists but does not support that customer eligibility; the independent expected span makes this an explicit failed case.

## Risk

A fluent answer can hide unsupported conditions; an overly cautious system can refuse answerable requests. One average accuracy number obscures both failure modes.

## Trade-off

Strict extractive answers are auditable for narrow policies but less conversational and incomplete for multi-source reasoning. Generative synthesis needs additional claim-level evaluation and privacy controls.

## Try This

Run the policy project, then grade a learner prediction with the general rule substituted for the final-sale answer. Explain why source existence, recall and claim support produce different conclusions.

## Follow-ups

### What if two currently authorized sources contradict each other?

Do not silently choose the higher similarity score. Check effective dates and source precedence rules; if no authoritative resolution exists, expose the conflict and abstain from the disputed decision while citing both permitted spans.

## Citations

- https://arxiv.org/abs/2005.11401
- https://www.nist.gov/itl/ai-risk-management-framework

# How is the context budget calculated?

## Answer

Available evidence capacity equals total budget minus reserved instructions, user input, and answer tokens, floored at zero. The assembler must account for rendered framing and citation text, not only passage body tokens. A positive capacity does not imply that even one candidate will fit.

## Why

A context budget exposes reserved_total, available_evidence_tokens, and is_valid. Assembly checks the rendered form as items are added and returns insufficient_budget when no candidate fits.

## Risk

Reserving too little for generation can cause provider truncation; counting with an approximate tokenizer cannot guarantee an actual model limit. The host must include its complete message framing and any tool schema costs.

## Trade-off

Larger answer reservations reduce evidence capacity. Larger evidence budgets increase cost and can include irrelevant or distracting material.

## Try This

For a 16,000-token window, reserve 2,000 instructions, 1,000 user input, and 3,000 answer tokens. Compute evidence room, then explain what additional host framing must be counted.

# Why is an approximate token estimator not a strict context guarantee?

## Answer

It estimates from characters and whitespace-separated words. Actual model tokenization depends on its vocabulary and encoding, so a heuristic can undercount some inputs even when intended to be conservative. The class explicitly marks is_exact as false.

## Why

The retrieval service offers an exact token-counting adapter for a model-specific counter. That adapter is only as exact as the supplied counting function and the host's representation of the final serialized request.

## Risk

A function labeled exact but counting the wrong model or omitting message wrappers still gives unsafe limits. Multilingual text, code, and unusual characters deserve explicit verification.

## Trade-off

Approximation keeps core dependency-free and supports offline use. Exact counting adds a tokenizer dependency or integration step and stronger budget fidelity.

## Try This

Compare heuristic and actual counts for prose, code, Arabic, and long identifiers. Explain why agreement on one example does not establish a global upper bound.

# How do deduplication and span merging differ?

## Answer

Deduplication removes repeated hits representing the same chunk. Span merging combines compatible overlapping or contiguous material from the same source context, preserving a larger coherent excerpt. They solve redundancy at different identity and text-boundary levels.

## Why

An evidence assembler has separate _deduplicate and _merge_spans stages and records counts. Proper merging depends on source and revision information plus usable offsets; arbitrary neighboring ranked hits are not automatically one passage.

## Risk

Merging across revisions or unrelated documents can fabricate a source excerpt that never existed. Missing or inconsistent offsets should not be guessed into a false provenance claim.

## Trade-off

Merging can restore context and save repeated framing, but may create a large item that fails the budget. Keeping chunks separate provides finer selection at the cost of repetition.

## Try This

Construct overlapping spans from the same document revision and one from a different revision. Predict which may merge and verify the emitted provenance.

# Why balance evidence across sources?

## Answer

A single document can occupy the candidate pool with many similar chunks. Source diversity can expose corroborating or contrasting material and reduce redundant context. It is a selection heuristic, not a guarantee that independent sources agree or are trustworthy.

## Why

The assembler ranks within sources and interleaves them before budget selection. This can preserve diversity even when a long source produces many high-scoring chunks.

## Risk

Diversity may demote the only authoritative source in favor of weaker material. Source quality and authority are product knowledge rules that may need explicit weighting or filtering outside the default heuristic.

## Trade-off

Pure relevance order maximizes one ranking signal; diversity spreads context coverage. Evaluate questions requiring one detailed source separately from questions requiring synthesis across sources.

## Try This

Give one source eight high-ranked chunks and another one relevant chunk. Compare evidence selection with the product's expected authority policy.

# What failure states should an evidence consumer handle?

## Answer

An evidence-status type includes success, empty_search, backend_failure, insufficient_budget, stale_index, and revision_unavailable. These represent different next actions: answer, clarify, retry, change capacity, refresh indexing, or explain that a historical source cannot be retrieved.

## Why

The assembler explicitly returns backend and stale-index states rather than assembling ungrounded material. Revision-aware lookup raises a distinct error instead of silently substituting the example document.

## Risk

Flattening every state into no answer hides outages and can trigger unsafe generation fallbacks. Success also means usable selected evidence, not proof of a correct final answer.

## Trade-off

Rich states require more UI and API branches but let users respond appropriately. A single boolean is simpler and loses important operational meaning.

## Try This

Write user-facing messages for each status and specify which states may be retried automatically without changing the user's question.

# What makes a citation reproducible?

## Answer

A reproducible citation identifies a stable source, document, revision, and bounded location or span. A URL pointing only to the latest page may no longer support an old answer after an update. Display labels such as [1] are local presentation, not durable source identities.

## Why

Revision-aware source lookup retrieves retained snapshots and rejects unavailable revisions. Evidence items carry revision and span fields, while source-reference helpers encode identifiers for later verification.

## Risk

Historical snapshots can contain sensitive material even after current content changes. Retention and revocation knowledge rules must apply to lookup as well as search, and a host must provide durable snapshot storage when needed.

## Trade-off

Retention improves auditability and costs storage and policy management. Current-only lookup is lighter but must admit when a historical request cannot be verified.

## Try This

Cite revision A, update the source to B, and attempt lookup. Verify that A is returned if retained and that missing A never silently becomes B.

# What does delimiter escaping mitigate, and what does it leave open?

## Answer

Escaping selected instruction-like tags and code fences reduces the chance that source text visually or syntactically breaks out of an evidence wrapper. It does not recognize every malicious natural-language instruction or make a model incapable of following one.

## Why

Escape_untrusted_delimiters replaces known markers in evidence rendering, and URI sanitization removes embedded credentials or disallowed active schemes. These are narrow input-handling mechanisms within a larger trust model.

## Risk

A passage can say ignore previous instructions without using any special delimiter. Host instructions must classify evidence as untrusted data, and tool permissions must prevent source text from gaining authority.

## Trade-off

Escaping preserves useful text with modest complexity but can alter literal code examples. More aggressive sanitization may damage legitimate content and still cannot solve all prompt injection.

## Try This

Compare a tag-based injection and a plain-language injection. Explain why both should remain untrusted even if only one changes during escaping.

# How can evidence compression preserve usefulness without fabricating support?

## Answer

Compression shortens selected material to fit a budget. Extractive compression selects original spans; abstractive compression generates a shorter restatement. The latter can change meaning or omit conditions, so provenance and faithfulness require explicit checks.

## Why

An evidence assembler accepts an optional compressor, passes a copy of the item, checks selected provenance fields, recounts the rendered result, and falls back when compression fails. No universal learned compressor is installed by default.

## Risk

Preserving source ID and revision does not prove the compressed words accurately represent the source. The host must evaluate the compressor and decide whether the compressed text is quoteable or should be labeled as a summary.

## Trade-off

Compression increases context coverage but adds cost and potential distortion. Dropping a low-value item is often safer than aggressively rewriting essential evidence.

## Try This

Compress a rule containing an exception. Verify both metadata invariance and semantic preservation; show a failure that passes metadata checks but changes the rule.

# How should the host turn evidence into a safe answer policy?

## Answer

The host should specify when to answer, how to cite, when to ask for clarification, and when to abstain. It should pass authorized evidence as data, preserve status signals, and check that important service requests are supported. This policy is part of the application, not an automatic property of the retrieval service.

## Why

The bridge returns a structured EvidenceBundle that a generator or source-viewing UI can consume. Its explicit status and attribution fields make a disciplined policy feasible without binding the subsystem to one chat model.

## Risk

A host that discards bundle status, regenerates citation identifiers, or allows source text to choose tools can undermine the safeguards upstream. Streaming service requests before evidence selection is settled creates another verification gap.

## Trade-off

Strict evidence-only answering improves traceability but can feel less helpful for general questions. Clearly separated modes can preserve user expectations.

## Try This

Draft a generation policy for answerable, ambiguous, empty, stale, and failed retrieval cases. Create one acceptance example for each branch.

# How do you test that a citation supports a claim rather than merely belonging to the user?

<!-- meta
domain: ai-rag
subdomain: evidence
module: evidence
concept: How do you test that a citation supports a claim rather than merely belonging to the user?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: An answer cites an authorized delivery paragraph as support for a refund decision.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Check caller scope, source identity and revision, then label whether the cited span entails the material claim under the case’s conditions. Membership checks are deterministic boundary evidence; semantic support needs an appropriate oracle or calibrated review. Split compound answers into individual claims and preserve disagreement rationale.

Concrete engineering case: An answer cites an authorized delivery paragraph as support for a refund decision.

Boundary defense: No. It can reject unknown or unauthorized identities, but a permitted source can still be irrelevant, insufficient or contradictory.

## Spoken Summary

Check caller scope, source identity and revision, then label whether the cited span entails the material claim under the case’s conditions. Membership checks are deterministic boundary evidence; semantic support needs an appropriate oracle or calibrated review. Split compound answers into individual claims and preserve disagreement rationale.

## Why

Check caller scope, source identity and revision, then label whether the cited span entails the material claim under the case’s conditions. Membership checks are deterministic boundary evidence; semantic support needs an appropriate oracle or calibrated review. Split compound answers into individual claims and preserve disagreement rationale.

## Production Case

An answer cites an authorized delivery paragraph as support for a refund decision.

## Risk

An answer cites an authorized delivery paragraph as support for a refund decision.

## Trade-off

No. It can reject unknown or unauthorized identities, but a permitted source can still be irrelevant, insufficient or contradictory.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: evidence**: Check caller scope, source identity and revision, then label whether the cited span entails the material claim under the case’s conditions.

## Alternatives

- No. It can reject unknown or unauthorized identities, but a permitted source can still be irrelevant, insufficient or contradictory.

## Pitfalls

- An answer cites an authorized delivery paragraph as support for a refund decision.

## Follow-ups

### Can source-ID validation automatically certify faithfulness?

No. It can reject unknown or unauthorized identities, but a permitted source can still be irrelevant, insufficient or contradictory.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "An answer cites an authorized delivery paragraph as support for a refund decision.",
  "required_decision": "Check caller scope, source identity and revision, then label whether the cited span entails the material claim under the case’s conditions"
}
```

## Citations

- https://arxiv.org/abs/2005.11401

# How do citation spans, source versions and claim coverage make an answer auditable?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: evidence
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A citation should identify inspectable evidence supporting the associated claim, ideally with the source revision and relevant location. Merely listing related documents does not establish entailment. Split a multi-part answer into claims and check whether each supported claim has the necessary evidence and applicability context. Keep extraction and chunk identities linked to their source so a reader can verify the exact text that informed the answer. Unsupported claims need omission, qualification or an explicit request for more information.

## Why

An answer states a 30-day deadline and a fee exemption but cites a passage supporting only the deadline. One valid citation does not support the additional exemption, even when both appear in the same sentence.

## Worked Case

An answer states a 30-day deadline and a fee exemption but cites a passage supporting only the deadline. One valid citation does not support the additional exemption, even when both appear in the same sentence.

## Risk

Citation formatting can make unsupported content appear trustworthy.

## Trade-off

Finer evidence links improve auditability while requiring stable provenance and UI support.

## Try This

Mark the supported span for each claim in a two-clause answer and identify any unsupported clause.

## Citations

- https://arxiv.org/abs/2005.11401
