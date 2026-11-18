<!-- chapter: context-optimization -->

# How do you calculate a safe context budget?

<!-- meta
domain: ai-rag
subdomain: context-optimization
module: context-optimization
concept: How do you calculate a safe context budget
difficulty: implementation
misconception_target: Truncation and compression are interchangeable
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Reserve space for instructions, tool schemas, conversation, retrieved evidence, and expected output before adding optional material. Use the provider's tokenizer or conservative model-specific accounting.

## Spoken Summary

Count instructions, history, tool definitions, evidence and reserved output using the model-specific contract. Leave a documented margin, then choose evidence selection, truncation or compression while preserving source identity and critical exceptions. Re-evaluate quality after changing the packing policy.

## Why

Compute remaining input allowance from the model limit and output reservation, then apply per-section caps. Multimodal inputs and hidden protocol overhead may require separate estimates.

## Production Case

A growing tool catalog consumes the remaining context even though user messages stay short. Break token usage down by category and reject overflow before invoking the provider.

## Risk

A character-based guess can exceed the limit or remove important content unpredictably.

## Trade-off

Large reservations reduce available evidence but improve completion reliability.

## Try This

Calculate budgets for two models with different context windows and output limits.

## Execution Timeline

Calculate token count → If over budget → Rank items by relevance → Truncate lowest priority → Or compress via summarization → Send to model

## Complexity

Token counting, candidate selection, sorting and model-based compression have distinct costs. Track input sizes, selected tokens, added model calls and quality impact rather than claiming all optimization is linear.

## Definitions

- **Context budget**: Maximum tokens available for prompt context
- **Truncation**: Dropping least relevant items to fit budget
- **Compression**: Summarizing content to fit more meaning in budget

## Alternatives

- Map-reduce over chunks
- Hierarchical context

## Pitfalls

- Truncating key evidence
- Compression losing critical details
- No budget monitoring

## Follow-ups

### Is four characters per token a safe hard limit?

No. Tokenization varies by model, language and representation. Use a compatible tokenizer or counting interface for hard budgeting.

## Example

> Explanation: Choose truncation or compression based on whether exact wording matters.
> Output: Prompt within token budget

```python
if token_count(prompt) > budget:
    evidence = evidence[:budget_items]  # truncate
    evidence = summarize(evidence, target_tokens=budget)  # compress
```

## Citations

- https://arxiv.org/abs/2305.14818

# How should evidence be selected under a token budget?

## Answer

Select passages for relevance, novelty, applicability, and source coverage rather than filling the window with the first ranked hits. A second near-duplicate passage often adds less value than a missing condition.

## Why

Deduplicate by document span, group related chunks, and reserve room for contradictory or qualifying passages. Track why a candidate was included or dropped.

## Risk

Greedy selection can omit a long decisive clause. Evaluate answerable cases that require multiple passages.

## Trade-off

Sophisticated selection adds latency; simple baselines remain useful.

## Try This

Compare top-k selection with diversity-aware selection on a fixture containing repeated FAQs.

# What is the difference between truncation and compression?

## Answer

Truncation discards material according to a rule; compression rewrites or extracts a smaller representation. Compression can preserve more useful information, but generated summaries can introduce errors.

## Why

Prefer extractive spans for authoritative numbers and conditions. If a model summarizes, retain the raw source and evaluate factual preservation before using the summary.

## Risk

A summary may drop a negation, exception, or unit while remaining fluent.

## Trade-off

Compression uses extra inference and can be reused across turns.

## Try This

Compress a rule with an exception and verify every condition against the original.

# How should conversation compaction work?

## Answer

Preserve the task goal, confirmed facts, unresolved questions, operation IDs, authorization boundaries, and recent state changes. Keep recent turns verbatim when their exact wording affects intent.

## Why

Generate a structured checkpoint, validate required fields, then continue with the checkpoint plus recent messages. Durable actions must be read from backend state.

## Risk

A summary is not a substitute for an audit log or a completed transaction record.

## Trade-off

Frequent compaction saves context but introduces recurring summarization error.

## Try This

Resume a long conversation from a checkpoint and check whether any completed action is repeated.

# What is lost-in-the-middle behavior?

## Answer

Models may use evidence differently depending on where it appears in a long context. The existence and size of the effect depend on the model, task, and data.

## Why

Evaluate important evidence placed at the beginning, middle, and end, with realistic distractors. Adjust context structure only after observing the failure.

## Risk

Treating a published positional effect as a universal ordering rule can worsen a different workload.

## Trade-off

Reordering is cheap but cannot recover missing evidence.

## Try This

Rotate one decisive passage through a long fixture and measure supported-answer rate.

# How do prompt caching and semantic caching differ?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: context-optimization
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**Prompt caching and answer caching reuse different things.** A provider prompt cache may reuse computation for an exact eligible prefix under provider-specific rules; it does not mean the final answer is cached. An application answer cache stores a previous output and its evidence. A semantic cache matches similar inputs, which can reuse an answer for a materially different scope, time or condition if its policy is too broad.

Design cache identity from trusted tenant/permissions, question/task, source/index revision, prompt/tool schema, model/profile and relevant settings. Similar wording is not enough. Bind cached citations to source revisions and reauthorize at read time; invalidate on deletion, policy change or permission epoch. Never use a caller-supplied owner label as authority. Negative caching also needs a lifetime: an earlier 'no evidence' result can become wrong after ingestion succeeds.

**Walk a stale policy.** Owner A asks about returns before a policy update and the answer cache stores 60 days. Revision 2 changes the rule to 30 days. Reusing the old output based only on query similarity yields a fluent stale answer with a real but obsolete citation. A versioned key prevents that hit, and final citation resolution catches a missed invalidation. If Owner B asks the same words, a cache hit must never reveal A's source or text. Clearing the current screen does not clear a shared server cache.

Measure cache hit rate alongside supported-answer rate, stale-hit rate, false refusals, latency and reported token usage. Do not claim provider savings from a local string match or toy token estimate. A cache stampede needs bounded single-flight or admission control so expiry does not create a burst of expensive attempts; cancellation and failure must release waiters safely. Cache only material allowed by retention/privacy policy and document deletion propagation into cache layers, logs and backups separately. The context packet fixture exercises scope/version logic; real provider prefix caching remains an optional adapter-specific experiment, not an inferred result.

## Why

Owner A caches a 60-day return answer, then revision 2 changes it to 30 days. A query-only cache returns stale guidance; including the source generation and revalidating citations prevents the incorrect reuse.

## Worked Case

Owner A caches a 60-day return answer, then revision 2 changes it to 30 days. A query-only cache returns stale guidance; including the source generation and revalidating citations prevents the incorrect reuse.

## Risk

Semantic similarity can ignore negation, tenant scope or an effective date. One high hit-rate graph can therefore hide both private-data leaks and wrong policy decisions.

## Trade-off

Exact versioned caching sacrifices some hit rate for clear validity. Semantic caching can help repetitive workloads but needs scoped thresholds, independent quality labels and a safe miss path.

## Try This

Run context_packet_policy.py. Add a policy-generation change and owner swap to a cache design, then predict hit/miss and citation eligibility independently of the implementation.

## Follow-ups

### Can a correct cached answer remain valid after permission revocation?

The text may remain factually correct but no longer authorized. Treat access validity independently of answer correctness, invalidate permission-scoped entries and recheck eligibility before returning cached text or citations.

## Citations

- https://www.rfc-editor.org/rfc/rfc9111.html
- https://opentelemetry.io/docs/security/handling-sensitive-data/

# How should memory retrieval avoid overwhelming the prompt?

## Answer

Retrieve a small set of task-relevant memory entries using ownership, recency, applicability, and confidence constraints. Long-term memory should remain selective.

## Why

Separate user-declared preferences from inferred observations and verified system facts. Rank within the authorized scope, then apply a token budget and expiry checks.

## Risk

Stale inferred preferences can override a new explicit user request if presented as privileged context.

## Trade-off

Narrow retrieval reduces noise but may repeat questions when recall misses a useful fact.

## Try This

Introduce an expired preference and verify that the current user instruction wins.

# When should you compress tool results instead of retrieving fewer records?

## Answer

Compress when the selected records are necessary but their representation is verbose. Retrieve fewer records when the extras do not contribute to the task. These solve different causes of context growth.

## Why

Keep authoritative identifiers and outcome fields, remove repeated schema descriptions, and store detailed payloads behind access-controlled artifact references.

## Risk

Dropping row-level provenance can make aggregates impossible to verify.

## Trade-off

Compact schemas improve efficiency while requiring schema version discipline.

## Try This

Replace a verbose 50-record tool response with an aggregate and scoped drill-down IDs.

# What is token efficiency, and how do you avoid optimizing the wrong metric?

## Answer

Token efficiency is useful work per cost under a quality and safety constraint. Reducing input tokens while increasing failed turns is not a product improvement.

## Why

Compare total task cost, completion rate, supported-answer rate, p95 latency, and repeat calls. Count summarization and cache misses in the same experiment.

## Risk

A cheaper model call can produce more retries and a more expensive complete journey.

## Trade-off

Multi-metric evaluation complicates ranking alternatives but reflects real users.

## Try This

Run a paired comparison where both context policies face the same task fixtures.

# How should context policies be rolled out?

## Answer

Version the assembly policy, evaluate it offline, compare it on a limited traffic slice, and retain rollback. Include permission and long-conversation cases in release gates.

## Why

Record the selected policy version in traces and experiment outputs. Change one dominant factor at a time so regressions can be attributed.

## Risk

A silent tokenizer or model revision change can invalidate an old budget assumption.

## Trade-off

Controlled rollout delays broad savings while reducing unknown failure exposure.

## Try This

Write a rollout plan with a regression threshold and an explicit rollback trigger.

# How do you prove that context compression did not remove a decisive exception?

<!-- meta
domain: ai-rag
subdomain: context-optimization
module: context-optimization
concept: How do you prove that context compression did not remove a decisive exception?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: Compression keeps the general refund rule but drops the sentence excluding sale items.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Compare compressed and original evidence on labeled cases that require conditions, units, dates and exceptions. Record the compressor/version and preserve source traceability. Token savings are useful only under a quality and permission gate. A fluent summary can erase the very detail that changes the correct answer.

Concrete engineering case: Compression keeps the general refund rule but drops the sentence excluding sale items.

Boundary defense: Inspect critical failure slices and denominators. A decisive permission or applicability regression should not be traded away for a better mean.

## Spoken Summary

Compare compressed and original evidence on labeled cases that require conditions, units, dates and exceptions. Record the compressor/version and preserve source traceability. Token savings are useful only under a quality and permission gate. A fluent summary can erase the very detail that changes the correct answer.

## Why

Compare compressed and original evidence on labeled cases that require conditions, units, dates and exceptions. Record the compressor/version and preserve source traceability. Token savings are useful only under a quality and permission gate. A fluent summary can erase the very detail that changes the correct answer.

## Production Case

Compression keeps the general refund rule but drops the sentence excluding sale items.

## Risk

Compression keeps the general refund rule but drops the sentence excluding sale items.

## Trade-off

Inspect critical failure slices and denominators. A decisive permission or applicability regression should not be traded away for a better mean.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: context optimization**: Compare compressed and original evidence on labeled cases that require conditions, units, dates and exceptions.

## Alternatives

- Inspect critical failure slices and denominators. A decisive permission or applicability regression should not be traded away for a better mean.

## Pitfalls

- Compression keeps the general refund rule but drops the sentence excluding sale items.

## Follow-ups

### Can a smaller prompt with the same average score be accepted automatically?

Inspect critical failure slices and denominators. A decisive permission or applicability regression should not be traded away for a better mean.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "Compression keeps the general refund rule but drops the sentence excluding sale items.",
  "required_decision": "Compare compressed and original evidence on labeled cases that require conditions, units, dates and exceptions"
}
```

## Citations

- https://arxiv.org/abs/1706.03762

# How do you compact a long-running agent without forgetting constraints or trusting a poisoned summary?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: context-optimization
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Separate durable task state from the model transcript.** Store the user objective, permissions, approved actions, unresolved questions, artifact identifiers and verified results as typed application state. A compressed transcript is a navigation aid; it is not an authority record. Preserve evidence references and versions so the agent can reopen the original source when needed.

**Compact at a measured boundary.** Before the next request, count the full context and predict the maximum next tool result. Keep recent exchanges needed for the immediate decision, replace older exploration with a bounded progress summary, and save bulky artifacts externally. Summaries should distinguish observations, hypotheses and failed attempts. Mark instructions found inside documents as untrusted data rather than promoting them into system instructions.

**Keep effects outside the summary.** A statement such as 'the refund probably succeeded' cannot decide whether to retry. Reconcile the operation identifier with the authoritative service. Preserve pending approval scope and expiration separately; a summary must not widen it. Record the compaction version and which original messages it covers, allowing an audit to reconstruct a decision.

**Test information survival.** Seed a long run with an early constraint, a later correction, a failed action and a malicious document. After repeated compactions, test whether the next action respects the correction and whether the system can recover the original evidence. Track task success and incorrect actions, not just the compression ratio. Use an explicit escalation when reconstruction fails.

## Why

At turn 80, a travel assistant must remember a corrected spending limit of 600 rather than the original 900. The typed budget is 600; neither a stale summary nor a retrieved hotel advertisement can override it.

## Worked Case

At turn 80, a travel assistant must remember a corrected spending limit of 600 rather than the original 900. The typed budget is 600; neither a stale summary nor a retrieved hotel advertisement can override it.

## Risk

Summarizing repeatedly can amplify an early mistake and erase provenance.

## Trade-off

Retain immutable artifacts for recoverability while limiting sensitive transcript retention according to the application policy.

## Try This

Build a compaction fixture with a corrected limit and a pending side effect. Demonstrate that replay neither restores the old limit nor repeats the effect.

## Citations

- https://www.anthropic.com/research/effective-context-engineering-for-ai-agents

# How do you optimize context cost without discarding rare but decisive evidence?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: context-optimization
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Context optimization should preserve task-critical support under a measured token and latency budget. Deduplicate repeated material, retain decisive exceptions and track source identities through compression. Estimate with the target tokenizer and include instructions, tool schemas, history and output reserve. Greedy selection by relevance alone can discard an expensive but essential qualifying clause. Evaluate answer support and failure slices after truncation or summarization; a smaller prompt is not automatically a better prompt.

## Why

Three repeated positive clauses can outrank one longer exclusion. Keeping all three repetitions wastes budget and can produce an incorrect answer even though the selected text has high average relevance.

## Worked Case

Three repeated positive clauses can outrank one longer exclusion. Keeping all three repetitions wastes budget and can produce an incorrect answer even though the selected text has high average relevance.

## Risk

Summaries can omit negation, dates, units or attribution that changes the answer.

## Trade-off

Optimize useful evidence per budget rather than only total token reduction.

## Try This

Compare full and compressed contexts on a case whose answer depends on one exception.

## Citations

- https://arxiv.org/abs/1706.03762
