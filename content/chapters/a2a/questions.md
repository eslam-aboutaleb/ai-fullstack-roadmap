<!-- chapter: a2a -->

# What is A2A, and when should a backend expose a remote agent?

<!-- meta
domain: agents
subdomain: a2a
module: a2a
concept: What is A2A, and when should a backend expose a remote agent
difficulty: design
misconception_target: A2A replaces MCP and REST for all use cases
reference: https://a2a-protocol.org/latest/topics/key-concepts/
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Agent2Agent describes interaction between independently hosted agents, including discovery, messages, tasks, and outputs. Use it when a remote specialist has a genuine service boundary rather than wrapping an ordinary deterministic lookup in another agent.

## Spoken Summary

A2A supports interaction between agent systems with discovery, messages and tasks. MCP standardizes AI-facing capabilities over local or remote connections. REST is commonly used for ordinary domain APIs. Choose based on the interaction contract and independent deployment need, then enforce authority separately.

## Why

A remote agent integration needs explicit client and server adapters, discovery, identity, task state, and a sharing policy. An agent SDK dependency does not create an operational endpoint.

## Production Case

A support workflow delegates research to an independently operated specialist. Validate its Agent Card, allowed destinations, disclosed context, task timeout and who owns each durable effect.

## Risk

Calling two local functions agents is not proof of protocol interoperability. A diagram arrow labeled A2A must correspond to an implemented and version-tested transport contract.

## Trade-off

A2A can support organizational and runtime boundaries while adding network, identity, compatibility, and operational complexity. A local domain service is simpler when independent deployment is unnecessary.

## Try This

Identify one support capability that genuinely needs an independently operated agent and one that should remain an ordinary local tool.

## Execution Timeline

Publish Agent Card -> Discover remote agent -> Create task -> Delegate work -> Monitor task lifecycle -> Receive result

## Complexity

Discovery, credentials and compatibility add network work; total cost depends on delegated tools, data and task lifecycle rather than an O(1) interoperability guarantee.

## Definitions

- **A2A**: Agent-to-Agent protocol for remote agent collaboration
- **Agent Card**: Capability advertisement published by an A2A agent
- **Task lifecycle**: States and transitions for long-running agent tasks

## Alternatives

- MCP for AI-facing local or remote capabilities
- A domain API or deterministic workflow when agent delegation adds no value

## Pitfalls

- Using A2A for local tool access
- No task timeout handling
- Missing Agent Card validation

## Follow-ups

### Does MCP imply a local-only deployment?

No. MCP supports remote HTTP integrations as well as local STDIO processes. Transport selection does not determine whether a capability is authorized.

## Example

> Explanation: Discover agent capabilities, create task, wait for result.
> Output: Task result from remote agent

```python
card = await fetch_agent_card(url)
task = await client.create_task(card, input)
result = await client.wait_for_task(task.id)
```

## Citations

- https://a2a-protocol.org/

# How do A2A, MCP, and ordinary APIs differ?

<!-- meta
reference: https://a2a-protocol.org/latest/topics/key-concepts/
-->

## Answer

A2A concerns agent-to-agent interactions and task-oriented collaboration. MCP commonly exposes tools and resources to model-enabled clients. A normal API can provide deterministic domain operations without claiming to be an autonomous peer. These interfaces can coexist but do not grant authority by themselves.

## Why

Use MCP for AI-facing capability access, ordinary APIs for deterministic service operations, and A2A where remote agent task ownership is useful. Define who owns every durable effect.

## Risk

Treating a peer agent as a trusted internal function can bypass user scope or disclose entire conversations. Capability discovery is not consent to every requested action.

## Trade-off

Protocol choice affects interoperability and lifecycle semantics. Use the narrowest interface that meets the integration need rather than wrapping every endpoint in an agent protocol.

## Try This

Map policy search, request confirmation, long-running specialist review, and metrics export to appropriate interfaces and explain the decision.

# What is an Agent Card, and why is it not an authorization token?

<!-- meta
reference: https://a2a-protocol.org/latest/topics/agent-discovery/
-->

## Answer

An Agent Card describes an agent's identity, capabilities, skills, endpoint, and security requirements. Discovery helps a client select a compatible service. Credentials and authorization are separately validated when invoking protected operations.

## Why

Treat published capability metadata as untrusted service input. Review the endpoint and supported contracts before sending scoped customer context or delegating a task.

## Risk

A malicious or stale card can point at an unintended endpoint or overstate capabilities. Do not send credentials or private claim data to arbitrary discovered destinations without trust and network policy.

## Trade-off

Dynamic discovery improves flexibility and adds authenticity, caching, and allowlist requirements. Explicitly configured peers are simpler for a small controlled deployment.

## Try This

Draft a secret-free capability description for a review-only specialist. List information that belongs in deployment configuration rather than its public card.

# How do messages, tasks, and artifacts differ in A2A?

<!-- meta
reference: https://a2a-protocol.org/latest/topics/life-of-a-task/
-->

## Answer

A message is an exchange of content, a task represents tracked work with lifecycle state, and an artifact is an output produced by that work. A reply being delivered does not necessarily mean the task completed or its output is authorized for all users.

## Why

Map remote lifecycle states into a versioned internal task model. Preserve remote identifiers, required user input, cancellation state, and authoritative completion references.

## Risk

Treating progress text as a final approved decision can trigger premature downstream action. Artifact references also need ownership, integrity, revision, and retrieval limits.

## Trade-off

Explicit tasks support long-running work and require durable tracking. One synchronous response is easier when the operation is genuinely short.

## Try This

Design an internal task record for a review request with owner, remote ID, status, result reference, deadline, and idempotency key.

# How should remote-agent authentication and user delegation work?

<!-- meta
reference: https://a2a-protocol.org/latest/topics/enterprise-ready/
-->

## Answer

Authenticate the service peer and separately authorize the delegated action for the originating user or case. A service identity should receive only the evidence and actions needed for its task. Do not forward a browser cookie indiscriminately across organizational boundaries.

## Why

Authenticate the remote service and delegate only the minimum user authority required. Verify token audience and avoid sending a broad application credential as a convenience.

## Risk

A powerful remote agent can become a confused deputy, using its own privileges for a caller who lacks them. Agent-card metadata does not enforce resource authorization.

## Trade-off

Narrow delegated capabilities reduce disclosure and require identity integration. Broad shared credentials simplify demos and make accountability difficult.

## Try This

Define which identity approves a review, which identity reads evidence, and which identity may confirm a service request. Keep final write authority local unless explicitly delegated.

# How do remote retries avoid duplicate work?

## Answer

Give one logical request a stable operation identity, persist its relationship to the remote task, and query or reconcile before creating another task after an ambiguous timeout. Transport request IDs and business idempotency keys may serve different purposes.

## Why

Propagate deadlines and durable operation identity across retries. After an uncertain response, query task status rather than automatically restarting a side-effecting remote task.

## Risk

A timeout can mean the remote service accepted the task but the acknowledgment was lost. Blind retries can create duplicate cases, charges, or conflicting recommendations.

## Trade-off

Reconciliation adds storage and latency but avoids assuming failure from missing acknowledgment. Fire-and-forget messaging is smaller and unsuitable for untracked consequential work.

## Try This

Simulate remote acceptance followed by a dropped response. Show how the client discovers or reuses the original task without submitting twice.

# What does cancellation mean for a remote agent task?

<!-- meta
reference: https://a2a-protocol.org/latest/topics/life-of-a-task/
-->

## Answer

Cancellation is a request to stop eligible work, not proof that every side effect has been undone. A task may have completed or crossed an irreversible boundary before the cancellation arrives. The host must interpret the remote result and reconcile its own state.

## Why

Specify what cancellation can stop and what already completed. A remote cancelled state does not reverse an external effect, so expose authoritative status and compensation where appropriate.

## Risk

Closing the browser stream does not establish task cancellation. A user may otherwise believe a case was abandoned while remote work continues or a notification is delivered.

## Trade-off

Explicit cancellation acknowledgment improves user expectations and adds race handling. Letting tasks finish is operationally simpler for read-only work if clearly communicated.

## Try This

Draw cancellation before acceptance, during review, and after completion. Define the displayed state and permissible follow-up action for each race.

# How can A2A artifacts become a prompt-injection or disclosure channel?

## Answer

A remote result can contain untrusted text, URLs, attachments, or instructions. Treat it as data from a service with a specific trust level, validate its schema, and allowlist any subsequent action. Remote output must not inherit system-instruction authority.

## Why

Constrain outputs by schema, scope, size, provenance, and retention. Validate artifacts before using them as facts or displaying them through a privileged renderer.

## Risk

An artifact can ask the model to retrieve another customer's claim or fetch an internal URL. Authentication of the sender does not make every returned instruction safe or every referenced document authorized.

## Trade-off

Rich artifacts support useful collaboration and need validation, size limits, safe fetching, and provenance. Minimal structured references are easier to govern than entire conversations and attachments.

## Try This

Return a mock artifact containing a cross-tenant reference and an instruction to bypass confirmation. Verify neither is executed.

# How should one trace span cross an A2A boundary?

<!-- meta
reference: https://opentelemetry.io/docs/concepts/signals/traces/
-->

## Answer

Propagate an approved trace context and stable operation identifiers while keeping credentials and private content separate. Each service records its own spans and outcome; the host correlates the remote task with the originating operation.

## Why

Pass safe trace context under a reviewed policy and retain task correlation across services. Distributed spans aid diagnosis but do not establish who authorized an operation.

## Risk

A trace ID is not authentication, and untrusted inbound trace metadata needs validation. Copying full claim text into span attributes can leak it to both organizations' telemetry systems.

## Trade-off

Distributed traces speed diagnosis but require shared conventions and retention policy. Correlation by sanitized operation IDs is a simpler fallback.

## Try This

Design a trace tree for one remote review with a retry and later artifact delivery. Show which spans represent waiting versus remote execution.

# When is a multi-agent architecture justified for service work?

<!-- meta
reference: https://adk.dev/a2a/
-->

## Answer

Use independently scoped agents when capabilities have distinct ownership, data access, deployment, or specialist review responsibilities. A local planner calling five functions does not need networked peers simply to look sophisticated.

## Why

Use multiple agents when ownership, capabilities, trust, or deployment boundaries justify them. Compare with one local agent and deterministic services before accepting the coordination overhead.

## Risk

More peers increase routing errors, coordination cost, inconsistent evidence, and cascading failures. Agreement between agents is not independent verification if they share the same wrong source or model.

## Trade-off

Specialization and organizational boundaries can justify distributed collaboration; a single orchestrator with narrow tools is cheaper and easier to test.

## Try This

Write an A2A architecture decision record with a task lifecycle, delegation policy, data-minimization plan, failure budget, and a simpler alternative.

# How do you reconcile an A2A artifact received before the task reaches a terminal state?

<!-- meta
domain: agents
subdomain: a2a
module: a2a
concept: How do you reconcile an A2A artifact received before the task reaches a terminal state?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A remote agent sends a draft artifact, the connection closes and the caller marks the overall operation successful without checking the task.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

An artifact can represent partial output. Preserve task identity and inspect status under the declared protocol profile. On interruption, read authoritative task state and apply the receiver’s continuation or cancellation semantics. Do not convert a closed stream or useful-looking artifact into proof of completed or reversed business work.

Concrete engineering case: A remote agent sends a draft artifact, the connection closes and the caller marks the overall operation successful without checking the task.

Boundary defense: No. It advertises capabilities and interfaces. Authentication, delegation scope and object permissions remain separate checks.

## Spoken Summary

An artifact can represent partial output. Preserve task identity and inspect status under the declared protocol profile. On interruption, read authoritative task state and apply the receiver’s continuation or cancellation semantics. Do not convert a closed stream or useful-looking artifact into proof of completed or reversed business work.

## Why

An artifact can represent partial output. Preserve task identity and inspect status under the declared protocol profile. On interruption, read authoritative task state and apply the receiver’s continuation or cancellation semantics. Do not convert a closed stream or useful-looking artifact into proof of completed or reversed business work.

## Production Case

A remote agent sends a draft artifact, the connection closes and the caller marks the overall operation successful without checking the task.

## Risk

A remote agent sends a draft artifact, the connection closes and the caller marks the overall operation successful without checking the task.

## Trade-off

No. It advertises capabilities and interfaces. Authentication, delegation scope and object permissions remain separate checks.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: a2a**: An artifact can represent partial output.

## Alternatives

- No. It advertises capabilities and interfaces. Authentication, delegation scope and object permissions remain separate checks.

## Pitfalls

- A remote agent sends a draft artifact, the connection closes and the caller marks the overall operation successful without checking the task.

## Follow-ups

### Does an Agent Card authorize the caller to run every advertised skill?

No. It advertises capabilities and interfaces. Authentication, delegation scope and object permissions remain separate checks.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A remote agent sends a draft artifact, the connection closes and the caller marks the overall operation successful without checking the task.",
  "required_decision": "An artifact can represent partial output"
}
```

## Citations

- https://a2a-protocol.org/latest/specification/
- https://a2a-protocol.org/latest/topics/life-of-a-task/
- https://a2a-protocol.org/latest/topics/enterprise-ready/
- https://a2a-protocol.org/v1.0.0/specification/
- https://github.com/a2aproject/a2a-python

# How should remote-agent tasks reconcile streaming status, reconnects and cancellation races?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: a2a
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

An A2A task has an identity and lifecycle under the negotiated profile. Streamed updates help responsiveness but may be interrupted, so authoritative task readback and allowed transitions matter. Cancellation is a request whose effect depends on task state and remote support; it need not undo a completed external operation. Authenticate task access and scope continuation to the intended principal. Persist mapping between local and remote task identities, and distinguish unknown connectivity from a confirmed terminal result.

## Why

A client disconnects after receiving 'working'. The remote task completes before cancellation arrives. On reconnect, read its actual terminal status instead of displaying 'cancelled' merely because a local cancel button was clicked.

## Worked Case

A client disconnects after receiving 'working'. The remote task completes before cancellation arrives. On reconnect, read its actual terminal status instead of displaying 'cancelled' merely because a local cancel button was clicked.

## Risk

A lost stream can cause duplicate task creation if identity mapping is discarded.

## Trade-off

Durable remote task identity supports recovery at additional coordination cost.

## Try This

Interrupt the stream, request cancellation and reconcile the task through authoritative readback.

## Citations

- https://a2a-protocol.org/latest/specification/
- https://a2a-protocol.org/latest/topics/life-of-a-task/
- https://a2a-protocol.org/latest/topics/enterprise-ready/
- https://a2a-protocol.org/v1.0.0/specification/
- https://github.com/a2aproject/a2a-python
