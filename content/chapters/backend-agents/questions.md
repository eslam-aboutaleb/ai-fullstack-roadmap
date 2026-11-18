<!-- chapter: backend-agents -->

# Where should an agent sit in a backend architecture?

## Answer

Place the agent behind authenticated API boundaries and in front of narrowly scoped application services. The model proposes decisions while the services own validation and state changes.

## Why

Share domain services across web routes, background workers, and tool adapters. Keep framework-specific event objects out of domain models.

## Risk

Allowing a model to access persistence directly bypasses consistent policy.

## Trade-off

Adapters add code and allow the runtime to evolve independently.

## Try This

Draw a dependency graph that prevents a tool from importing the web framework's request object.

# How should authenticated identity reach a tool?

## Answer

Derive identity from verified backend authentication and pass it through trusted runtime context or explicit service arguments. Never ask the model to supply its own tenant authority.

## Why

Bind a principal at the run boundary, reset task-local context reliably, and authorize each resource inside the service.

## Risk

A shared global variable can leak identity across concurrent requests.

## Trade-off

Explicit identity arguments are verbose and make ownership visible.

## Try This

Run two users concurrently and assert that each tool sees only its own scope.

# How do tools reuse business services without duplicating rules?

## Answer

A tool adapter parses model arguments, calls a domain service with trusted identity, and translates a typed result. The service performs business validation and transaction ownership.

## Why

Keep the same service contract for HTTP and agent callers. Test permissions once at the service boundary and adapter behavior separately.

## Risk

Independent validation copies can diverge after a business rule changes.

## Trade-off

Reuse constrains adapter flexibility and preserves consistent outcomes.

## Try This

Implement one request-preparation service with both an API route and a tool wrapper.

# How should long-running agent work be exposed over HTTP?

## Answer

Accept a task, return a durable task ID, process it under worker supervision, and expose status plus an optional event stream. Completion should survive a disconnected browser.

## Why

Persist task state and use owner-scoped status and cancellation endpoints. Distinguish acceptance from completion in response codes and UI text.

## Risk

Holding one request open is not durable task storage.

## Trade-off

Jobs add infrastructure and support recoverable long operations.

## Try This

Submit a task, close the browser, and retrieve its final status later.

# How do transaction boundaries interact with model calls?

## Answer

Keep slow model and network work outside database lock windows. Revalidate current state inside the short transaction that applies a business change.

## Why

Prepare intent first, then lock or compare versions during commit and record downstream jobs atomically.

## Risk

Data can change between preparation and commit, so an earlier validation is insufficient.

## Trade-off

Revalidation adds complexity and avoids prolonged locks.

## Try This

Change a record after planning and verify commit rejects the stale revision.

# How should agent-side idempotency work?

## Answer

Use a durable operation identity tied to the intended business effect. Repeated requests should return or recover the same authoritative result when the contract permits.

## Why

Enforce a uniqueness constraint or conditional transition in the database and keep request-level model-call deduplication separate.

## Risk

A short-lived in-memory lock cannot establish exactly-once business effects.

## Trade-off

Durable ledgers cost storage and enable safe retries.

## Try This

Retry after a simulated response loss and verify only one business record exists.

# What should a typed tool result contain?

## Answer

Include operation ID, outcome category, safe data, retryability, and next permitted action. For writes, include the authoritative record or task reference when completed.

## Why

Translate exceptions into stable categories while retaining private diagnostic details only in protected logs.

## Risk

Returning success true after merely scheduling work can mislead the UI.

## Trade-off

Explicit result types require more branches and prevent ambiguous completion.

## Try This

Model prepared, accepted, completed, rejected, unavailable, and uncertain outcomes separately.

# How should rate limits be applied to agent workloads?

## Answer

Limit requests, concurrent runs, model tokens, tool calls, and downstream operations according to tenant and service capacity. A single HTTP request can initiate substantial work.

## Why

Use shared fleet-wide quotas where needed and propagate an absolute deadline across retries and child tasks.

## Risk

Local process counters multiply when workers scale.

## Trade-off

Shared accounting adds latency and coordinates real capacity.

## Try This

Calculate the worst-case tool load from ten requests with nested agent loops.

# How should provider adapters be designed?

## Answer

Normalize model invocation, cancellation, usage, errors, and public event projections behind an interface, while preserving provider-specific limitations.

## Why

Keep capability flags and compatible configuration explicit. Evaluate the same task contract when switching providers.

## Risk

A common API can hide differences in tool calls, structured outputs, or streaming semantics.

## Trade-off

Portability reduces coupling and may limit access to specialized features.

## Try This

Switch between two stub providers with different event sequences without changing the UI contract.

# How should backend integration be demonstrated in a portfolio?

## Answer

Show one complete journey with verified identity, tool use, durable writes, streaming updates, cancellation, and recovery. Include the failure path and measured evaluation results.

## Why

Provide architecture diagrams, synthetic fixtures, a release manifest, and a recorded restart demonstration.

## Risk

A chat screenshot does not prove authorization or transactional correctness.

## Trade-off

A narrow robust scenario is less flashy and stronger engineering evidence.

## Try This

Demonstrate the same operation through HTTP and an agent, then explain the shared service boundary.

# Where should a delegated agent’s authority stop when its task crosses services?

<!-- meta
domain: ai-rag
subdomain: backend-agents
module: backend-agents
concept: Where should a delegated agent’s authority stop when its task crosses services?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: An orchestrator forwards an entire conversation and administrator token to a remote summarizer that only needs one permitted paragraph.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Delegate the minimum data and capability required, carry a verifiable caller or delegation context and enforce resource scope at the receiving service. Keep a stable task/effect identity and an explicit reconciliation path. A local chat role or an agent name is not a transitive authorization credential.

Concrete engineering case: An orchestrator forwards an entire conversation and administrator token to a remote summarizer that only needs one permitted paragraph.

Boundary defense: No. Transport protection does not reduce the authority or data delivered to the receiving service.

## Spoken Summary

Delegate the minimum data and capability required, carry a verifiable caller or delegation context and enforce resource scope at the receiving service. Keep a stable task/effect identity and an explicit reconciliation path. A local chat role or an agent name is not a transitive authorization credential.

## Why

Delegate the minimum data and capability required, carry a verifiable caller or delegation context and enforce resource scope at the receiving service. Keep a stable task/effect identity and an explicit reconciliation path. A local chat role or an agent name is not a transitive authorization credential.

## Production Case

An orchestrator forwards an entire conversation and administrator token to a remote summarizer that only needs one permitted paragraph.

## Risk

An orchestrator forwards an entire conversation and administrator token to a remote summarizer that only needs one permitted paragraph.

## Trade-off

No. Transport protection does not reduce the authority or data delivered to the receiving service.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: backend agents**: Delegate the minimum data and capability required, carry a verifiable caller or delegation context and enforce resource scope at the receiving service.

## Alternatives

- No. Transport protection does not reduce the authority or data delivered to the receiving service.

## Pitfalls

- An orchestrator forwards an entire conversation and administrator token to a remote summarizer that only needs one permitted paragraph.

## Follow-ups

### Can encryption alone make overbroad delegation acceptable?

No. Transport protection does not reduce the authority or data delivered to the receiving service.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "An orchestrator forwards an entire conversation and administrator token to a remote summarizer that only needs one permitted paragraph.",
  "required_decision": "Delegate the minimum data and capability required, carry a verifiable caller or delegation context and enforce resource scope at the receiving service"
}
```

## Citations

- https://docs.python.org/3/tutorial/
- https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

# How can tool proposals be validated without letting the model choose its own permissions?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: backend-agents
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A tool proposal is untrusted input to a trusted application boundary. Parse its schema, resolve the authenticated principal from application context, load current authoritative state and enforce the action's policy. A model-supplied owner field must not override that identity. Use stable operation identities for effects, record accepted state durably and map unknown outcomes separately from failures. Return only data permitted for the caller, including error paths and lookup results. A correct language answer cannot substitute for these checks.

## Why

The model proposes updating request R2 and includes owner_id B while the caller is A. The service must reject the cross-owner action even if all fields have valid types and the model gives a persuasive explanation.

## Worked Case

The model proposes updating request R2 and includes owner_id B while the caller is A. The service must reject the cross-owner action even if all fields have valid types and the model gives a persuasive explanation.

## Risk

Allowing the model to populate trusted identity makes schema validation insufficient.

## Trade-off

Central domain services let agents and ordinary APIs reuse the same enforceable rules.

## Try This

Attempt the same forbidden action through a direct API and a model tool proposal.

## Citations

- https://docs.python.org/3/tutorial/
- https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
