<!-- chapter: langchain -->

# What would LangChain replace or add in this application?

<!-- meta
reference: https://docs.langchain.com/oss/python/langchain/agents
-->

## Answer

LangChain can supply model, message, tool, middleware, structured-output, and agent-building abstractions. Adopting its agent factory would replace part of the example ADK orchestration, not PostgreSQL, the retrieval service, domain validation, or the confirmation transaction.

## Why

Wrap existing services through compatible tool interfaces and retain business ownership and transactions. Compare the runtime with the baseline using identical application tasks and measured integration cost.

## Risk

Installing a framework without deciding who owns sessions, tool errors, and streaming can create two overlapping runtimes. A dependency change alone does not migrate behavioral contracts.

## Trade-off

LangChain offers a broad integration surface; staying with ADK avoids migration cost. Choose based on a demonstrated need and an equivalent behavioral benchmark.

## Try This

Map each current ADK constructor argument to the proposed LangChain composition. Identify the contracts that should remain unchanged.

# What are messages, chat models, and invocation methods?

<!-- meta
reference: https://docs.langchain.com/oss/python/langchain/models
-->

## Answer

Messages represent roles, text, tool calls, and tool results. A chat model consumes a message sequence and produces model output. Invocation, streaming, and batch methods are execution interfaces, not different authorization knowledge rules or independent guarantees of model quality.

## Why

Inject a compatible model interface and record provider-specific capabilities. A common constructor does not guarantee identical tool, streaming, or structured-output behavior.

## Risk

Dropping a tool result, role boundary, or corrected user value can change behavior. A model supporting text may not support the tool or structured-output features the application requires.

## Trade-off

Standard interfaces ease experimentation while provider capabilities still require testing. A single-provider direct adapter can be smaller for a narrow workload.

## Try This

Translate a user question, tool call, tool result, and assistant answer into an explicit message sequence and verify the pairing identifiers.

# How can an existing domain service become a LangChain tool?

<!-- meta
reference: https://docs.langchain.com/oss/python/langchain/tools
-->

## Answer

Wrap the existing async domain function with a narrow typed tool whose arguments contain only user-searchable input. Resolve trusted identity in server context and retain the domain function's validation and owner filters. The wrapper should not expose internal session or owner parameters to the model.

## Why

Expose a narrow model-facing function that calls an authorized service with trusted runtime context. Keep internal owner and tenant arguments out of user-editable tool schemas.

## Risk

A convenient wrapper accepting user_id from the model defeats the example scoping boundary. Context setup and reset must be defined for HTTP, evaluation, and background execution.

## Trade-off

Thin adapters reuse tested business logic and add a small compatibility surface. Rewriting tools inside each framework risks policy drift.

## Try This

Inspect the proposed read-only policy wrapper in the worked examples. Add a service requests wrapper that obtains identity from a trusted service context.

# How do runnable composition and an agent loop differ?

## Answer

A composed chain follows a known sequence such as retrieve, assemble, and answer. An agent loop lets a model choose tools and continuation. Both can use the same model and retriever interfaces, but they create different testing and cost requirements.

## Why

Use fixed composition when stage order is known; use an agent loop when tool selection depends on observations. Evaluate the extra flexibility against latency and failure complexity.

## Risk

Calling a fixed chain an agent can hide the absence of planning; calling an agent a simple chain can hide repeated calls and nondeterministic routing. Name the actual control flow.

## Trade-off

Fixed composition is easier to bound and diagnose; flexible routing handles ambiguity. Start from the least flexible flow that meets the requirement.

## Try This

Build a deterministic retrieval-and-answer baseline and compare it with agent orchestration on single-intent and multi-intent cases.

# What does structured output validate, and what does it not validate?

<!-- meta
reference: https://docs.langchain.com/oss/python/langchain/structured-output
-->

## Answer

A structured schema constrains the form and types of a model result, such as an answer with citation IDs and a status. It does not prove the citations exist, the amounts match policy text, or the caller may execute a proposed action.

## Why

Choose a compatible structured-output strategy, parse the result, and run domain validation. Schema compliance does not establish factual correctness or action authority.

## Risk

A valid JSON decision saying approved is still not an authorized claim transition. Schema conformance can otherwise create a false impression of factual or business correctness.

## Trade-off

Typed outputs simplify UI integration and require explicit parse, retry, and semantic-validation branches. Free-form prose is flexible and harder to validate reliably.

## Try This

Define a recommendation schema with status, cited evidence IDs, missing facts, and explanation. Reject unknown citations before presentation.

# What belongs in middleware instead of a business tool?

<!-- meta
reference: https://docs.langchain.com/oss/python/langchain/middleware/overview
-->

## Answer

Cross-cutting knowledge rules such as call budgets, model selection, standardized error mapping, and context preparation can sit around execution. Business tools should still own their domain authorization, validation, and transaction behavior.

## Why

Use middleware for cross-cutting policy, budget, logging, and context transformations. Keep business validation in application services so non-agent callers enforce the same invariants.

## Risk

A middleware-only authorization check can be bypassed by direct service calls. Overly broad retry middleware can also repeat side effects whose business idempotency is not established.

## Trade-off

Central hooks reduce repetition while increasing execution-order and wrapper-compatibility complexity. Keep critical invariants enforceable independently of orchestration hooks.

## Try This

Classify budget checking, owner filtering, signature preservation, and pending-token consumption by the layer that must enforce each one.

# How should short-term memory map to support conversations?

<!-- meta
reference: https://docs.langchain.com/oss/python/langchain/short-term-memory
-->

## Answer

Short-term memory stores a thread's evolving conversational context. It needs a stable thread identity and a persistence policy. Long-term customer facts, authoritative service requests, and pending confirmation state should remain in domain storage rather than only in a message buffer.

## Why

Map conversation and thread ownership explicitly, define retention and compaction, and test concurrent updates. Framework memory is neither a business ledger nor a universal persistence contract.

## Risk

Reusing thread IDs across users or forgetting ownership checks can disclose history. Memory summaries can also retain obsolete tokens or knowledge facts after a correction.

## Trade-off

Persistent memory improves continuity and increases retention obligations. Stateless turns simplify privacy and require more explicit context from the user.

## Try This

Design a user-and-conversation thread key and a migration test for archived history, corrected facts, and sign-out followed by another user.

# How should LangChain streams be adapted to the existing UI contract?

<!-- meta
reference: https://docs.langchain.com/oss/python/langchain/streaming
-->

## Answer

Translate framework-specific chunks into the application's typed events rather than exposing raw runtime objects. Preserve text deltas, tool activity, errors, persisted message IDs, and a truthful terminal status.

## Why

Translate framework events into a stable user-safe schema. Preserve task identity, event order, cancellation, errors, and persistence-before-completion semantics across adapters.

## Risk

A tool error or cancelled stream can otherwise be mislabeled complete. Forwarding arbitrary runtime state may leak internal or private fields.

## Trade-off

A stable application event layer costs adapter code and decouples UI releases from framework changes. Raw framework streams are faster to demo and fragile to evolve.

## Try This

Feed equivalent synthetic ADK and LangChain event sequences into two adapters and compare the resulting public events.

# Are framework guardrails a replacement for deterministic permissions?

<!-- meta
reference: https://docs.langchain.com/oss/python/langchain/guardrails
-->

## Answer

No. Guardrails can classify inputs, validate outputs, or interrupt unsafe model behavior, but backend authorization must still deny prohibited reads and writes. A classifier can be wrong or unavailable, and a prompt can be ignored.

## Why

Validate both proposed arguments and actual service outcomes. A tool description improves selection but cannot prevent a model from proposing unauthorized or invalid operations.

## Risk

A content-safety pass does not certify that a customer may access another claim or approve a payout. Combining unrelated notions of safety into one boolean hides authority errors.

## Trade-off

Guardrails add useful signals and latency. Deploy them as complementary checks with explicit error behavior, not as the sole permission system.

## Try This

Make a simulated model issue an unauthorized operation after a guardrail reports safe text. Verify the service still denies it.

# How would you decide whether a runtime-to-LangChain migration is worthwhile?

<!-- meta
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Start from a task contract, not a framework popularity contest.** A direct provider SDK focuses on model I/O and streaming. LangChain provides composable model/tool/retrieval components; LlamaIndex focuses on data ingestion/index/query abstractions; LangGraph models explicit stateful execution and checkpoints; Google ADK and OpenAI Agents SDK supply their own agent lifecycle abstractions. These layers are not interchangeable: an SDK can call a model without guaranteeing workflow persistence, and an orchestration framework does not prove safe business effects.

**Fair comparison method.** Keep the same synthetic input documents, authenticated user, initial context, tool schemas, deterministic mock response or pinned real provider configuration, output schema, budget, data retention policy and failure schedule. Measure comparable outputs—authorized citations, refusal cases, schema validity, tool dispatch and side effects—before wall-clock latency. Log separate initialization, first token and total task latency distributions, memory/dependency footprint, traces and retry/cost behavior. Do not compare a warmed-up framework against a cold-start SDK and claim the SDK is slower.

**Worked case.** Implement a policy assistant whose single allowed action is owner-scoped read-only search. With the same gold return-policy document, the direct reference, graph reference and retrieval reference must produce the same answer and source ID. Remove search permission: all must refuse without reading any private data. Add a malicious adapter that claims to call a write tool: the harness must reject it independently of how nice its generated text looks.

**Local implementation.** `labs/framework_contract_compare.py` creates three small reference execution strategies under a shared Task/Outcome schema, verifies paired results, owner scope, denied tools and forbidden effects. It records fixture timing only; it does **not** import or measure LangChain, LlamaIndex, LangGraph, ADK or the OpenAI Agents SDK. Real pinned adapter implementations, tracing exporters, semantic retrieval and normalized provider cost measurements are future integration acceptance items.

**Senior trade-off.** Choose a framework only after you identify a needed capability that you cannot implement cheaply and safely with direct SDK plus ordinary application code. More orchestration can improve complex interrupt/recovery semantics but adds dependency maintenance, implicit retries, serializer/version compatibility and debugging load. Keep authorization, owner-scoped durable state, evaluation and effect ownership outside the model framework.

**Follow-up.** If the application requires human approval and crash recovery across replicas, the plain direct SDK example becomes insufficient unless you add a durable workflow engine and effect journal. Compare that *complete* architecture fairly against a graph/agent framework, not against a one-function demo.

## Why

Compare routing, scope enforcement, approval, memory, streaming, recovery, and trace privacy on the same fixtures. Preserve product contracts or explicitly redesign them with migration and rollback evidence.

## Risk

Benchmarking only a successful coverage response misses multi-turn correction, tool failure, and duplicate writes. New abstractions can also change trace payload disclosure.

## Trade-off

A better-fit ecosystem can justify the cost; keeping the example stack may be more valuable when problems are domain contracts rather than orchestration limitations.

## Try This

Execute the framework task contract, deny search, then insert a tool-calling adapter and inspect its rejection; repeat with pinned real frameworks before making performance claims.

## Follow-ups

### What evidence makes a graph agent worth replacing a direct SDK call in a production workflow?

Demonstrate a requirement such as durable crash recovery, supervised interrupts or multi-step resumable state under equal data/tool contracts. Measure the complete direct-SDK implementation including its own ledger and retries, compare traces and failure oracles, and account for framework upgrade and operational complexity.

## Citations

- https://docs.langchain.com/oss/python/langchain/overview

# When does a LangChain abstraction need to be replaced with a smaller explicit boundary?

<!-- meta
domain: ai-rag
subdomain: langchain
module: langchain
concept: When does a LangChain abstraction need to be replaced with a smaller explicit boundary?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A chain retries a mutation-bearing tool automatically after a transport error and the receiver commits twice.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Use an abstraction while it makes the required data flow, retries, callbacks and authority observable. If hidden behavior makes lifecycle or error handling ambiguous, inspect and configure it or isolate a smaller explicit adapter. Do not let a convenience wrapper own business authorization simply because it already calls the model.

Concrete engineering case: A chain retries a mutation-bearing tool automatically after a transport error and the receiver commits twice.

Boundary defense: No. The receiver’s commit and deduplication contract remain application concerns across every framework.

## Spoken Summary

Use an abstraction while it makes the required data flow, retries, callbacks and authority observable. If hidden behavior makes lifecycle or error handling ambiguous, inspect and configure it or isolate a smaller explicit adapter. Do not let a convenience wrapper own business authorization simply because it already calls the model.

## Why

Use an abstraction while it makes the required data flow, retries, callbacks and authority observable. If hidden behavior makes lifecycle or error handling ambiguous, inspect and configure it or isolate a smaller explicit adapter. Do not let a convenience wrapper own business authorization simply because it already calls the model.

## Production Case

A chain retries a mutation-bearing tool automatically after a transport error and the receiver commits twice.

## Risk

A chain retries a mutation-bearing tool automatically after a transport error and the receiver commits twice.

## Trade-off

No. The receiver’s commit and deduplication contract remain application concerns across every framework.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: langchain**: Use an abstraction while it makes the required data flow, retries, callbacks and authority observable.

## Alternatives

- No. The receiver’s commit and deduplication contract remain application concerns across every framework.

## Pitfalls

- A chain retries a mutation-bearing tool automatically after a transport error and the receiver commits twice.

## Follow-ups

### Does switching frameworks remove the need for an effect identity?

No. The receiver’s commit and deduplication contract remain application concerns across every framework.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A chain retries a mutation-bearing tool automatically after a transport error and the receiver commits twice.",
  "required_decision": "Use an abstraction while it makes the required data flow, retries, callbacks and authority observable"
}
```

## Citations

- https://docs.langchain.com/oss/python/langchain/tools
- https://docs.langchain.com/oss/python/langchain/streaming

# How should callback instrumentation and framework wrappers preserve tool semantics?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: langchain
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A tool wrapper must preserve input validation, identity propagation, error categories and the meaning of its return value. Instrumentation should observe the call without swallowing exceptions, leaking arguments or changing an async function into blocking behavior. A framework-generated schema needs inspection, especially after decorators alter signatures or annotations. Keep domain authorization outside model-editable arguments and test the wrapped tool against the same contract as a direct call. Framework convenience does not establish effect durability or safe replay.

## Why

A decorator hides a required keyword argument and the framework exposes an incorrect tool schema. The agent then supplies incomplete calls even though direct unit calls to the original function work correctly.

## Worked Case

A decorator hides a required keyword argument and the framework exposes an incorrect tool schema. The agent then supplies incomplete calls even though direct unit calls to the original function work correctly.

## Risk

An observability wrapper can become a behavioral bug at the tool boundary.

## Trade-off

Thin adapters reduce duplicated rules while keeping framework-specific details replaceable.

## Try This

Compare direct and wrapped tool validation, exceptions and schema output.

## Citations

- https://docs.langchain.com/oss/python/langchain/tools
- https://docs.langchain.com/oss/python/langchain/streaming
