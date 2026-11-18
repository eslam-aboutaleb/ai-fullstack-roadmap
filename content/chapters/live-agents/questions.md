<!-- chapter: live-agents -->

# What makes an agent live or realtime?

## Answer

A live agent reacts to ongoing inputs and changing state under a latency target. It may process speech, events, sensors, or user interaction rather than one isolated request.

## Why

Define the required response deadline and which state changes can invalidate active work. Use an explicit session and task lifecycle.

## Risk

Calling a system realtime without a measured latency contract hides important product limitations.

## Trade-off

Lower latency can reduce deliberation and increase infrastructure cost.

## Try This

Specify a latency target for interruption handling separately from final task completion.

# How should events trigger agent work?

## Answer

Validate and normalize external events, deduplicate them, check scope, and schedule bounded tasks. The model should not directly subscribe to an unrestricted event firehose.

## Why

Use an event envelope with ID, source, subject, revision, and timestamp. Record why an event created or updated a task.

## Risk

Duplicate or reordered events can repeat actions or restore stale state.

## Trade-off

Event infrastructure adds complexity and supports responsive workflows.

## Try This

Deliver the same update twice and verify only one task effect occurs.

# How do you handle stale work when new events arrive?

## Answer

Associate work with a state version or generation ID. Before publishing a result or committing a write, verify that the assumptions remain applicable.

## Why

Cancel or supersede obsolete generation and use conditional writes for authoritative state.

## Risk

An old model response can overwrite a newer user instruction if arrival order is treated as authority.

## Trade-off

Version checks can discard useful computation and preserve correctness.

## Try This

Send a correction while the agent is working and reject the earlier draft as stale.

# What is event-time versus processing-time reasoning?

## Answer

Event time describes when something occurred; processing time describes when the system handled it. Delayed delivery makes them different and can change applicability decisions.

## Why

Retain both timestamps and define ordering and lateness policies per event type. Use monotonic clocks for local duration measurement.

## Risk

Sorting only by arrival can misrepresent the user's actual sequence of actions.

## Trade-off

Lateness handling adds state and supports unstable networks.

## Try This

Process a late event and decide whether it updates history, current state, or neither.

# How should long-lived session memory be bounded?

## Answer

Keep a compact working state, recent events, durable operation references, and relevant retrieved memory. Archive detailed history under controlled retention instead of appending forever.

## Why

Periodically checkpoint and compact using validated fields. Rebuild essential facts from authoritative systems after restart.

## Risk

Unbounded histories increase token cost and retain unnecessary private data.

## Trade-off

Compaction reduces detail and controls operational growth.

## Try This

Run a synthetic session through hundreds of events and measure memory and prompt size.

# How should human escalation work for live agents?

## Answer

Create a durable handoff with owner, reason, urgency, safe summary, evidence, completed actions, and unresolved questions. Tell the user the actual handoff state.

## Why

Integrate with a real queue or ticket service and expose acceptance and resolution events.

## Risk

Saying a specialist has been contacted without a recorded handoff is false completion.

## Trade-off

Human review adds delay and handles ambiguity beyond automation scope.

## Try This

Simulate an unavailable escalation service and show an honest fallback.

# How do presence and connection state differ from task state?

## Answer

Presence indicates whether a client is connected or recently active. Task state records accepted work, progress, and outcomes. A disconnected user may still have a running task.

## Why

Keep separate connection, session, and task records with distinct expiry and recovery rules.

## Risk

Tying task lifetime blindly to one socket can lose durable work on a network interruption.

## Trade-off

Separate lifecycles add modeling and improve recovery.

## Try This

Close the client, complete a background task, and reconnect to its result.

# How should live agents handle overload?

## Answer

Use admission control, bounded queues, priority policies, and explicit degraded behavior. Prefer rejecting new work clearly over silently accumulating unbounded delay.

## Why

Reserve capacity for cancellation, status, and safety controls. Track queue age and deadline expiry.

## Risk

Treating every request equally can starve critical controls behind bulk generation.

## Trade-off

Priority policies add fairness decisions and keep the system operable.

## Try This

Flood nonessential events and verify that cancellation remains responsive.

# What should live-agent observability emphasize?

## Answer

Track event lag, queue age, active sessions, stale-result rejection, reconnect rate, cancellation latency, task outcomes, and cost per active period.

## Why

Correlate events, tasks, model runs, and operations with stable IDs and safe metadata.

## Risk

A healthy socket count can conceal a stalled worker or outdated responses.

## Trade-off

Fine-grained metrics increase instrumentation effort and reveal real responsiveness.

## Try This

Create an alert for rising event lag while HTTP health remains green.

# How should live-agent reliability be demonstrated?

## Answer

Show duplicate delivery, out-of-order events, network loss, user interruption, process restart, provider outage, and overload recovery under a declared contract.

## Why

Use synthetic scenarios with expected final states and record timing evidence. Review both user-visible behavior and durable effects.

## Risk

A short low-load demo cannot establish long-running reliability.

## Trade-off

Failure demonstrations take time and provide strong engineering evidence.

## Try This

Record a session that survives a restart without duplicating an approved action.

# How should a live assistant handle a perception update that invalidates its pending plan?

<!-- meta
domain: ai-rag
subdomain: live-agents
module: live-agents
concept: How should a live assistant handle a perception update that invalidates its pending plan?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A screen changes while a live agent prepares a click. The delayed action targets the old location and activates another control.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Bind observations and plans to revisioned context, cancel obsolete local work where appropriate and reject actions whose prerequisites no longer hold. Separate a new observation from evidence that a previous effect was undone. Bound update frequency and queue age so the assistant does not act on a backlog of stale state.

Concrete engineering case: A screen changes while a live agent prepares a click. The delayed action targets the old location and activates another control.

Boundary defense: No. Validate current state and action preconditions at dispatch, and use a recovery policy when effects become uncertain.

## Spoken Summary

Bind observations and plans to revisioned context, cancel obsolete local work where appropriate and reject actions whose prerequisites no longer hold. Separate a new observation from evidence that a previous effect was undone. Bound update frequency and queue age so the assistant does not act on a backlog of stale state.

## Why

Bind observations and plans to revisioned context, cancel obsolete local work where appropriate and reject actions whose prerequisites no longer hold. Separate a new observation from evidence that a previous effect was undone. Bound update frequency and queue age so the assistant does not act on a backlog of stale state.

## Production Case

A screen changes while a live agent prepares a click. The delayed action targets the old location and activates another control.

## Risk

A screen changes while a live agent prepares a click. The delayed action targets the old location and activates another control.

## Trade-off

No. Validate current state and action preconditions at dispatch, and use a recovery policy when effects become uncertain.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: live agents**: Bind observations and plans to revisioned context, cancel obsolete local work where appropriate and reject actions whose prerequisites no longer hold.

## Alternatives

- No. Validate current state and action preconditions at dispatch, and use a recovery policy when effects become uncertain.

## Pitfalls

- A screen changes while a live agent prepares a click. The delayed action targets the old location and activates another control.

## Follow-ups

### Is a faster perception loop alone enough?

No. Validate current state and action preconditions at dispatch, and use a recovery policy when effects become uncertain.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A screen changes while a live agent prepares a click. The delayed action targets the old location and activates another control.",
  "required_decision": "Bind observations and plans to revisioned context, cancel obsolete local work where appropriate and reject actions whose prerequisites no longer hold"
}
```

## Citations

- https://opentelemetry.io/docs/concepts/signals/

# How do event generations and invalidation prevent stale live-agent results?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: live-agents
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A live agent can receive a new event while earlier work is still running. Assign generation or version identities to inputs, propagate them through work and verify result ownership before publishing or committing. Cancellation reduces wasted work but may arrive too late, so invalidation at the publication boundary is still required. Define whether events replace prior intent, accumulate or require ordered processing. Effects accepted under an older generation need explicit reconciliation rather than silent abandonment.

## Why

A location update makes an earlier recommendation obsolete. A slow earlier lookup may finish last, but the UI must reject that result instead of replacing the newer recommendation solely because it arrived most recently.

## Worked Case

A location update makes an earlier recommendation obsolete. A slow earlier lookup may finish last, but the UI must reject that result instead of replacing the newer recommendation solely because it arrived most recently.

## Risk

Completion order is not intent order.

## Trade-off

Latest-value processing saves work when replacement semantics are valid; ordered events need a different policy.

## Try This

Delay the first of two events and prove only the current generation can publish.

## Citations

- https://opentelemetry.io/docs/concepts/signals/
