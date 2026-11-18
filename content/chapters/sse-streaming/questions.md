<!-- chapter: sse-streaming -->

# When should an AI application use SSE?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: sse-streaming
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**Choose SSE when the browser needs a one-way stream of server events over HTTP**, such as task progress or an answer transcript. Ordinary HTTP can submit/cancel the task; use WebSocket when genuine bidirectional realtime messaging justifies its additional lifecycle. A public SSE contract names the events, payload schema, identity, cursor, terminal states and reconnection policy.

**Streaming is a delivery mode, not evidence of completion.** HTTP byte chunks are arbitrary transport pieces: one UTF-8 character or JSON event may span several chunks, and one chunk may contain several events. A correct client uses an incremental decoder and the declared framing grammar. Server-sent events (SSE) end an event at a blank line and combine data fields; the workbench project instead uses newline-delimited JSON and deliberately documents that difference.

A useful application contract distinguishes accepted, running, partial, completed, failed and cancelled. Bind every frame to a task/request identity and monotonic sequence; accept an identical replay at most once and reject a conflicting replay. Only a valid terminal frame permits Complete. EOF after plausible text is an incomplete answer. Expose that state to sighted and assistive-technology users rather than making an interrupted paragraph look authoritative.

**Walk a boundary failure.** The server sends half a JSON line, the network disconnects, and the UI already shows 'Returns are allowed'. The parser must retain the fragment until a delimiter, then reject the unfinished stream; it must not manufacture the missing citation or terminal event. On identity switch, abort the fetch, advance a generation ID and discard queued callbacks with the old identity/generation. Abort alone cannot recall a callback already queued, and cancelling presentation cannot undo a committed backend effect.

Use bounded frame and total-output sizes, deadlines and backpressure. A slow browser should not accumulate an unlimited transcript. If resumption is supported, authenticate every reconnect, define retention and cursor gaps, and replay from authoritative history. An SSE id is a cursor, not authorization or business idempotency. Test split multibyte characters, multiple frames per read, stale callbacks, malformed JSON, missing final state and cancellation. `projects/evidence-workbench` compiles the actual React/TypeScript client and exercises these failures over loopback HTTP; `labs/streaming_app.py` supplies a separate optional SSE service. Neither fixture proves a provider's token-generation behavior.

## Why

An old Owner A response arrives after switching to Owner B. Aborting and clearing the screen is insufficient if a queued callback still appends A text; a generation check prevents that stale write.

## Worked Case

An old Owner A response arrives after switching to Owner B. Aborting and clearing the screen is insufficient if a queued callback still appends A text; a generation check prevents that stale write.

## Risk

Rendering partial text as final can turn a network failure into a wrong business decision. Logging raw frames can also retain private material beyond the UI lifetime.

## Trade-off

Buffering reduces UI work but delays first visible text. Announcing every token overwhelms screen readers; announce meaningful status changes and provide a readable final transcript.

## Try This

Build the evidence-workbench, run its browser checker, and preserve a failure trace for disconnect-before-final and identity-switch-during-slow-response. Explain which state is authoritative.

## Follow-ups

### Can a reconnect safely repeat the original request?

Only under an explicit request/effect contract. Resume a retained stream with its cursor where supported; creating a fresh model request may duplicate cost or tools. Reauthorize the task and deduplicate durable effects independently of presentation replay.

## Citations

- https://html.spec.whatwg.org/multipage/server-sent-events.html
- https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Using_readable_streams

# How is an SSE message framed?

## Answer

An event consists of text fields followed by a blank line. Data may span multiple data lines, which the receiver combines according to SSE rules. Network chunks do not align with event boundaries.

## Why

Decode UTF-8 incrementally, accumulate lines, and dispatch only at the event delimiter. Normalize supported line endings and impose limits.

## Risk

Parsing each received chunk as JSON fails when characters or messages split across chunks.

## Trade-off

Correct incremental parsing adds state and avoids intermittent corruption.

## Try This

Split a Unicode event at every byte boundary and verify equivalent decoding.

# How should EventSource and fetch streaming be compared?

## Answer

Browser EventSource handles an SSE GET connection and reconnection behavior. Fetch streaming gives control over methods, headers, and request bodies but requires application parsing and retry logic.

## Why

Choose based on authentication, request semantics, and resume requirements. Do not assume EventSource accepts arbitrary authorization headers.

## Risk

Putting bearer tokens in query parameters can expose them in logs and history.

## Trade-off

Fetch offers flexibility while EventSource supplies useful protocol behavior.

## Try This

Design a cookie-authenticated EventSource flow and a header-authenticated fetch flow.

# What should a public AI event schema contain?

## Answer

Include schema version, task ID, ordered sequence, event type, and typed payload. Distinguish text deltas, tool activity, final results, recoverable notices, and terminal errors.

## Why

Convert provider events through an adapter. The UI should reduce these events into explicit states rather than concatenate every payload into answer text.

## Risk

Provider-internal messages can leak private arguments or confuse partial output with completion.

## Trade-off

Stable schemas add adapter maintenance and protect the UI from provider churn.

## Try This

Document how a tool error changes state differently from an answer delta.

# How should reconnection and replay work?

## Answer

Give events durable sequence IDs and define a retention window. Resume from the last acknowledged or processed event, and deduplicate repeated sequence numbers.

## Why

If replay history expired, return a snapshot or a clear resume failure. Revalidate ownership on every connection.

## Risk

Reconnecting without a replay contract can lose events or duplicate displayed text.

## Trade-off

Durable event storage adds cost and enables recovery.

## Try This

Disconnect after event seven and resume without repeating the final business operation.

# How do heartbeats and proxy buffering affect streams?

## Answer

Intermediaries may buffer output or close idle connections. Heartbeats can keep an otherwise idle stream active, but infrastructure behavior must be measured.

## Why

Use appropriate content type and cache policy, disable buffering where supported, and send bounded periodic comments. Check actual arrival times through the production proxy.

## Risk

Application flushes alone do not establish that the browser receives each event promptly.

## Trade-off

Frequent heartbeats consume connections and bandwidth.

## Try This

Record server-send and browser-receive timestamps behind your actual ingress.

# How should cancellation work with SSE?

## Answer

Closing a stream should stop unnecessary generation according to product policy, while durable tasks may continue independently. Expose a task cancellation endpoint for explicit control.

## Why

Propagate cancellation to providers when supported and record the final task state. Preserve committed operation IDs for later lookup.

## Risk

A disconnected stream does not prove that external effects were cancelled.

## Trade-off

Separating task and stream lifetimes adds complexity and enables background completion.

## Try This

Close the stream during a pending tool call and inspect the authoritative task status.

# How should backpressure be handled?

## Answer

Bound producer-to-writer queues and prevent slow clients from retaining unlimited memory. Decide which progress events can be coalesced and which terminal events must be retained.

## Why

Await writable capacity where the framework supports it, monitor queue depth, and disconnect consumers that cannot keep up under the contract.

## Risk

Dropping arbitrary text deltas corrupts the answer.

## Trade-off

Strong limits may disconnect slow clients and protect the server.

## Try This

Simulate a client reading one event per second while the producer emits many more.

# What should completion mean in an SSE stream?

## Answer

A completion event should identify the persisted result or authoritative final task state. A finished model token sequence is not necessarily a completed application operation.

## Why

Persist the final record before emitting completion and support owner-scoped result retrieval after disconnect.

## Risk

A crash after sending done but before commit creates a false success.

## Trade-off

Persist-before-complete adds final latency and strengthens recovery.

## Try This

Crash at the completion boundary and verify the UI can recover from the result endpoint.

# How should SSE be tested?

## Answer

Test UTF-8 boundaries, multiline data, line endings, comments, empty data, malformed payloads, replay, authorization, disconnects, and slow consumers. Test through the real proxy as well as in process.

## Why

Keep transport decoding separate from JSON schema validation and UI reduction. Assert both event order and terminal state.

## Risk

A happy-path mock stream misses buffering and network fragmentation.

## Trade-off

Real transport tests cost more and catch difficult intermittent failures.

## Try This

Build a replay fixture containing a duplicate event and an expired resume token.

# What must an SSE parser preserve when an event is split across network chunks?

<!-- meta
domain: frontend
subdomain: sse-streaming
module: sse-streaming
concept: What must an SSE parser preserve when an event is split across network chunks?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A multibyte character and an event boundary are split across two reads. Parsing each read independently corrupts the text or loses the event.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Decode UTF-8 incrementally and apply the SSE field and blank-line grammar independently of fetch chunks. Preserve declared event identity and replay semantics, bound buffers and require application completion evidence where the task needs it. A transport reconnection is not permission to repeat a business effect.

Concrete engineering case: A multibyte character and an event boundary are split across two reads. Parsing each read independently corrupts the text or loses the event.

Boundary defense: No. Bound admitted work, retained history and slow-consumer buffers under an explicit server/client policy.

## Spoken Summary

Decode UTF-8 incrementally and apply the SSE field and blank-line grammar independently of fetch chunks. Preserve declared event identity and replay semantics, bound buffers and require application completion evidence where the task needs it. A transport reconnection is not permission to repeat a business effect.

## Why

Decode UTF-8 incrementally and apply the SSE field and blank-line grammar independently of fetch chunks. Preserve declared event identity and replay semantics, bound buffers and require application completion evidence where the task needs it. A transport reconnection is not permission to repeat a business effect.

## Production Case

A multibyte character and an event boundary are split across two reads. Parsing each read independently corrupts the text or loses the event.

## Risk

A multibyte character and an event boundary are split across two reads. Parsing each read independently corrupts the text or loses the event.

## Trade-off

No. Bound admitted work, retained history and slow-consumer buffers under an explicit server/client policy.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: sse streaming**: Decode UTF-8 incrementally and apply the SSE field and blank-line grammar independently of fetch chunks.

## Alternatives

- No. Bound admitted work, retained history and slow-consumer buffers under an explicit server/client policy.

## Pitfalls

- A multibyte character and an event boundary are split across two reads. Parsing each read independently corrupts the text or loses the event.

## Follow-ups

### Does SSE automatically give the application backpressure?

No. Bound admitted work, retained history and slow-consumer buffers under an explicit server/client policy.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A multibyte character and an event boundary are split across two reads. Parsing each read independently corrupts the text or loses the event.",
  "required_decision": "Decode UTF-8 incrementally and apply the SSE field and blank-line grammar independently of fetch chunks"
}
```

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch

# How should a streaming API distinguish generated text, persisted answers and successful task completion?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: sse-streaming
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**These are separate facts.** A model can generate text before the application saves it. A saved message can describe a failed business operation. A connection can close without a terminal application event. Define explicit fields for generation outcome, persistence outcome and domain-operation outcome instead of overloading one success boolean.

**Make terminal semantics part of the application protocol.** Server-Sent Events (SSE) define an event framing and reconnection transport, not what your product considers a completed answer. Use a typed final event with task identity, status, persisted message identifier when available, source references and safe error information. If the product promises a durable answer at completion, commit the answer before emitting a successful terminal event.

**Represent persistence failures honestly.** If text was generated but storage failed, the UI may keep a clearly marked unsaved draft and offer an appropriate retry or reconciliation path. Do not enable feedback with a fabricated message identifier. Avoid regenerating the entire answer just to retry persistence; preserve the generated artifact under a task identity when the architecture permits safe recovery.

**Handle transport loss independently.** A server can emit one terminal event and the client can still miss it. Clients need a status lookup or replay contract where continuity matters. Treat end-of-file without terminal evidence as interrupted or unknown, not successful. Exactly one logical terminal state is an application invariant; its delivery may be at least once, so clients must deduplicate. The example models server-side completion fields without pretending to run an HTTP server.

## Why

A browser displays a complete paragraph, then the database write fails. The terminal event reports generated text with failed persistence and no message ID; the UI retains an unsaved draft and disables persisted-message feedback.

## Worked Case

A browser displays a complete paragraph, then the database write fails. The terminal event reports generated text with failed persistence and no message ID; the UI retains an unsaved draft and disables persisted-message feedback.

## Risk

Equating a closed socket with a completed operation causes false success and feedback against nonexistent records.

## Trade-off

Commit-before-terminal adds storage latency but makes durable-completion promises meaningful.

## Try This

Test generated-but-unsaved, saved-but-terminal-lost and failed-domain-action cases. Define the UI state and retry action for each.

## Follow-ups

### Should persistence failure always discard visible text?

That is a product decision. Keeping it as an explicitly unsaved draft can preserve user work, but the client must not present it as durable history or invent feedback references.

### Does a terminal event guarantee the client received it?

No. Durable status and replay are needed to reconcile lost delivery. A successful send call does not prove the browser processed the event.

## Citations

- https://html.spec.whatwg.org/multipage/server-sent-events.html
- https://www.sqlite.org/lang_transaction.html

# How do event IDs, replay retention and truncated frames affect SSE recovery?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: sse-streaming
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**A network read is not an SSE message.** Server-sent events are UTF-8 text framed by lines and a blank-line delimiter; a read can split a character, line or entire event.

1. Decode bytes with an **incremental decoder**, retaining incomplete character bytes.
2. Preserve unfinished text until a complete line is available.
3. Assemble an event from its fields and dispatch only when its frame is complete.
4. Track the completed application event identity under the server's replay contract.
5. On reconnect, deduplicate any replay and handle an expired retention cursor explicitly.

An event ID supports recovery only when the server defines its **scope, ordering, retention and resume behavior**. An automatic EventSource reconnect does not create an end-to-end exactly-once guarantee for business effects.

If a connection closes halfway through a frame, do not apply that partial event as a successful completion. Distinguish an explicit terminal application event from an unexpected disconnect, and reconcile authoritative task state when the stream alone cannot establish the result.

## Why

The connection closes after half an event, then reconnects with the last completed ID. The client must not apply the truncated event or duplicate a completed event replayed by the server.

## Worked Case

The connection closes after half an event, then reconnects with the last completed ID. The client must not apply the truncated event or duplicate a completed event replayed by the server.

## Risk

Treating every received byte chunk as a complete event corrupts framing.

## Trade-off

Replay improves continuity while requiring bounded storage and an explicit expired-cursor policy.

## Try This

Split a UTF-8 character and frame across reads, then test duplicate replay after reconnect.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
