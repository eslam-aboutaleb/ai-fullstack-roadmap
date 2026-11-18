<!-- chapter: product-delivery -->

# What is the public SSE contract, and why should the browser not parse raw ADK internals?

<!-- meta
answer_format: conceptual
domain: fullstack-engineering
subdomain: product-delivery
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**The browser should consume an application-owned event contract**, such as task identity, sequence, progress, bounded text, citations, error and a terminal state. An adapter translates framework-specific events into that stable contract. Raw ADK internals can change version, expose tool arguments or leak private state; the frontend must not infer user success from an undocumented internal event. Define whether the actual wire framing is SSE or NDJSON and parse it accordingly.

**An interface should make system state understandable while the server remains authoritative.** Distinguish pending, partial, completed, unsupported, failed and cancelled results. Show source provenance and limitations alongside fluent prose. A spinner cannot stand in for a task-state contract, and hiding another owner's record in the browser does not undo the disclosure if it already arrived over the network.

Authentication establishes identity; object-level authorization decides access to each task, source and effect. The workbench uses public synthetic fixture identities and is not a real login system. A production cookie session needs a CSRF policy for state-changing requests, secure cookie settings and server-side expiry/revocation. A bearer-token design needs safe storage, transport and issuer/audience validation. Never embed provider secrets in a static build or assume CORS is authentication.

On logout or owner change, clear visible answer/citation state, invalidate client caches and ignore old callbacks. Scope server caches and reads independently. Render model/source text as text, not trusted HTML; a content security policy is additional defense rather than a reason to use unsafe insertion. Do not put tokens in URLs or ordinary logs. Browser-only checks cannot authorize a tool operation.

Measure useful performance: build size, initial interaction, first visible response, final completion, render/update count and long tasks under a stated device/network/fixture. A fast localhost response is not evidence of fleet capacity. Run behavioral browser tests over the actual compiled UI and HTTP server, including malformed stream, unsupported query, cancellation, owner swap and literal HTML-looking text. Keep semantic accessibility review and real authentication integration as explicit extensions with their own evidence, rather than pretending a demo-token selector implements production security.

## Why

A hidden B citation still appears in the network response to A. The correct repair scopes the server query before returning data; clearing the UI or adding a client filter does not repair the confidentiality breach.

## Worked Case

A hidden B citation still appears in the network response to A. The correct repair scopes the server query before returning data; clearing the UI or adding a client filter does not repair the confidentiality breach.

## Risk

Static frontend bundles and source maps are public. Embedding a provider key or treating a demo identity selector as authentication makes every visitor capable of impersonation.

## Trade-off

Rich HTML can improve presentation but increases sanitization and injection complexity. Text rendering plus explicit trusted components is a safer default for untrusted model/source output.

## Try This

Inspect the workbench network response for an owner swap and literal HTML payload. Record first-response and completion separately, then state why the timing cannot predict concurrent production capacity.

## Follow-ups

### Does a disabled Approve button protect a write endpoint?

No. It is a usability control. The server must verify principal, exact operation arguments, business state and approval on every request, including requests sent outside the interface.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS
- https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html

# How should a browser parse streaming chunks correctly?

<!-- meta
domain: frontend
subdomain: streaming-ui
module: product-delivery
concept: How should a browser parse streaming chunks correctly
difficulty: implementation
misconception_target: Streaming UI is just showing text as it arrives
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Buffer bytes across network reads, decode incrementally, split complete SSE frames, parse their JSON, and retain any unfinished suffix. A network chunk may contain half a JSON object or several events; it is not an event boundary.

## Spoken Summary

Decode bytes incrementally, preserve partial UTF-8 state and parse the transport’s actual event framing before parsing JSON. Track operation identity, sequence/replay, partial content and explicit completion separately. Bound buffers and reject malformed or conflicting events.

## Why

Decode UTF-8 incrementally and accumulate SSE fields through the blank-line delimiter. Validate the completed event payload separately and test every relevant network fragmentation boundary.

## Production Case

An accented character and a JSON delimiter arrive in different network chunks. A streaming decoder plus framing buffer reconstructs the event; per-chunk JSON parsing fails.

## Risk

Naive JSON.parse on each read loses events or fails on multibyte characters. Error recovery must also distinguish a malformed event from a clean terminal completion.

## Trade-off

A small parser handles a narrow contract; a mature SSE client can cover more protocol details. Test the actual API framing and reconnection requirements.

## Try This

Feed the same stream split at every possible byte boundary, including inside Unicode text. Verify identical parsed events.

## Execution Timeline

User submits -> Loading state -> Stream begins -> Handle chunks -> Complete or error -> Reconnect if needed

## Complexity

Decoder/reducer work depends on bytes, events and retained history; immutable copies and rendering can add growing cost. Bound buffers and batch visible updates after measuring responsiveness.

## Definitions

- **UI state machine**: Tracks request state across loading, streaming, complete, and error
- **Citation rendering**: Displaying source passages alongside generated answers
- **Reconnection**: Resuming a stream after a connection drop

## Alternatives

- Polling for updates
- Server-sent events without state machine

## Pitfalls

- Losing state on reconnect
- No error state handling
- Citations not matched to text

## Follow-ups

### Does a fetch chunk correspond to one SSE event?

No. Network chunk boundaries are arbitrary. SSE fields and blank-line framing need a compatible parser.

## Example

> Explanation: Track state transitions for streaming UI.
> Output: UI state transitions correctly

```python
const states = { LOADING, STREAMING, COMPLETE, ERROR };\nlet current = states.LOADING;\nfunction onChunk(text) { current = states.STREAMING; append(text); }\nfunction onError(err) { current = states.ERROR; showError(err); }
```

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/EventSource

# Why do persisted message IDs matter for feedback?

## Answer

Feedback should reference an actual assistant message owned by the user, not a temporary browser-generated ID. The backend can then authorize the record and connect a rating to its conversation, evidence, model configuration, and trace.

## Why

Bind feedback to an owner-scoped persisted answer or operation. A client-supplied message ID must not allow another user to label or retrieve private conversation data.

## Risk

Rating an optimistic local ID can fail or attach feedback to the wrong turn. A persistence failure may leave partial text visible but no authoritative message to rate.

## Trade-off

Waiting for server identity adds a final synchronization step and preserves referential integrity. Client-only messages are easy to render and weak as durable references.

## Try This

Simulate a stream that generates text but fails persistence. Define whether feedback is disabled and how retry behaves without duplicating the displayed answer.

# What should the UI state machine distinguish during a turn?

## Answer

Distinguish draft, accepted, searching or tooling, generating, completed, failed, cancelled, and disconnected. Track evidence and persistence status separately where needed. A spinner stopping is not proof that the model completed successfully.

## Why

Use explicit waiting, running, streaming, review, complete, incomplete, failed, and cancelled states. Transitions should follow typed outcomes rather than the presence of some generated text.

## Risk

Treating every closed connection as completion can show truncated service requests as final. Late responses from a prior conversation or signed-out user can also contaminate current state.

## Trade-off

Explicit states add frontend logic and improve recovery. A single loading boolean is compact and cannot represent the important distinctions.

## Try This

Create a reducer for stream events and test disconnect before completion, tool failure, persistence failure, cancellation, and a late event after tenant or conversation change.

# How should request confirmation be presented and protected in the UI?

## Answer

Display the exact prepared fields, identify that no claim is yet submitted, and send the token through the authenticated confirmation route only after the user's action. Disable duplicate controls for usability while retaining server-side race protection.

## Why

Present exact parameters, operation identity, expiry, and revision. Disable misleading repeated actions in the UI, but rely on server-side approval validation and transactional idempotency for correctness.

## Risk

Corrections can leave old pending tokens valid unless the server supersedes them. The UI must not promise revocation that only exists in prompt text.

## Trade-off

A review screen adds friction and supports consent to material fields. The authoritative check must remain on the server because browsers can retry or be bypassed.

## Try This

Test double click, refresh, expired token, cancellation race, and correction after preparation. Compare displayed state with the actual submission record.

# How should browser caching respond to sign-out, role changes, and archived conversations?

## Answer

Partition cached results by trusted user and relevant resource identity, cancel or ignore obsolete in-flight responses, and clear private state at sign-out. Revalidate permissions for source opening and mutation even if a cached view once allowed access.

## Why

Invalidate or partition client caches by authenticated identity and permission revision. Cancel streams and clear private view state on sign-out, while retaining server-side ownership checks on every fetch.

## Risk

Reusing query keys across users can show private content without making a new unauthorized request. Hidden or archived messages can also remain in model context unless their lifecycle is mapped deliberately.

## Trade-off

Aggressive invalidation costs network requests and preserves clear session boundaries. Long-lived caches improve responsiveness and need stronger partitioning and freshness rules.

## Try This

Switch users during a slow stream and verify no old message, source, or confirmation token appears in the new user's interface.

# How should citations and tool activity be rendered accessibly and safely?

## Answer

Render untrusted text safely, expose expandable source details by keyboard, use meaningful labels, and avoid announcing every token to assistive technology. Show user-relevant activity without exposing internal prompts, private tool arguments, or raw exception data.

## Why

Render model text as text or a sanitized approved subset. Validate links and avoid treating returned HTML or tool output as trusted application markup.

## Risk

Raw HTML or unsafe URLs can create XSS, and a busy live region can make streaming unusable. A similarity distance should not be displayed as percent certainty.

## Trade-off

Progressive disclosure reduces overload but must keep verification discoverable. Detailed internal traces belong in authorized operator tools, not the customer screen.

## Try This

Review a synthetic answer using only the keyboard and a screen reader. Include malicious markup and long source titles in the fixture.

# How should client retries preserve operation identity?

## Answer

Reuse one idempotency key for retries of the same logical request, but create a new operation for a genuinely changed request. Record whether the server accepted or completed it. Claim confirmation should rely on its own token and durable state, not a generic chat response cache.

## Why

Preserve a durable operation key across retries and distinguish request deduplication from business idempotency. After an uncertain outcome, query status rather than restarting a write blindly.

## Risk

Reusing a key with a changed body should fail rather than replay another answer. Retrying a long-running request after a best-effort Redis wait can still duplicate model calls.

## Trade-off

Explicit operation identity requires lifecycle handling and supports predictable retries. Automatically retrying all failures is easy and can repeat expensive work.

## Try This

Test same key/same body, same key/changed body, new key/same body, and an ambiguous timeout. Document behavior for chat versus confirmation.

# How should frontend, API, and agent contracts be tested together?

## Answer

Use a small set of full user journeys plus focused contract tests for events, ownership, persistence IDs, and confirmation effects. Fake providers make UI tests deterministic; separate live-provider tests assess actual model behavior.

## Why

Expose a stable API error and outcome schema across frontend and backend. Version incompatible changes and test clients against missing, delayed, duplicate, and unknown event types.

## Risk

A mocked stream that always ends successfully cannot reveal cancellation or malformed-event behavior. Live model tests alone are too variable for every UI assertion.

## Trade-off

Layered tests provide fast diagnosis and credible integration coverage. Excessive end-to-end duplication raises cost without necessarily testing new behavior.

## Try This

Define five journeys: cited answer, corrected preparation, denied foreign claim, failed stream, and post-restart history. State the provider and database realism each needs.

# What should the completed portfolio demonstration show?

## Answer

Show one coherent user journey across authentication, evidence retrieval, streaming, source verification, request preparation, confirmation, background indexing, and feedback. Then demonstrate a denial and a recovery case with supporting traces and tests.

## Why

Demonstrate identity, evidence, approved effects, cancellation, restart recovery, and quality measurement in one coherent journey. Use synthetic data and show a failure as well as success.

## Risk

A polished recording can hide unimplemented handoff, current-only policy scope, or in-memory deployment state. State those limitations and show the effective configuration.

## Trade-off

A narrow reliable application is more persuasive than many unverified agent features. Add remote agents or model adaptation only when the measured problem justifies them.

## Try This

Prepare a ten-minute demo with architecture, one successful task, one adversarial denial, one crash recovery, and a held-out quality/cost report.

# How should an AI product explain partial output, retry and session expiry to a user?

<!-- meta
domain: frontend
subdomain: product-delivery
module: product-delivery
concept: How should an AI product explain partial output, retry and session expiry to a user?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A timeout after task acceptance produces a Try again button that silently creates a second task under a new key.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Model operation, transport connection and visible draft text are different states. Preserve useful partial work under a truthful incomplete label, expose a bounded recovery action and clear user-scoped data when identity changes. Do not tell the user a write failed merely because its acknowledgment was lost; reconcile the authoritative operation.

Concrete engineering case: A timeout after task acceptance produces a Try again button that silently creates a second task under a new key.

Boundary defense: The logical operation identity and compatible payload, with an authoritative status or reconciliation result rather than a second independent request.

## Spoken Summary

Model operation, transport connection and visible draft text are different states. Preserve useful partial work under a truthful incomplete label, expose a bounded recovery action and clear user-scoped data when identity changes. Do not tell the user a write failed merely because its acknowledgment was lost; reconcile the authoritative operation.

## Why

Model operation, transport connection and visible draft text are different states. Preserve useful partial work under a truthful incomplete label, expose a bounded recovery action and clear user-scoped data when identity changes. Do not tell the user a write failed merely because its acknowledgment was lost; reconcile the authoritative operation.

## Production Case

A timeout after task acceptance produces a Try again button that silently creates a second task under a new key.

## Risk

A timeout after task acceptance produces a Try again button that silently creates a second task under a new key.

## Trade-off

The logical operation identity and compatible payload, with an authoritative status or reconciliation result rather than a second independent request.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: product delivery**: Model operation, transport connection and visible draft text are different states.

## Alternatives

- The logical operation identity and compatible payload, with an authoritative status or reconciliation result rather than a second independent request.

## Pitfalls

- A timeout after task acceptance produces a Try again button that silently creates a second task under a new key.

## Follow-ups

### What should the interface reuse for a safe retry?

The logical operation identity and compatible payload, with an authoritative status or reconciliation result rather than a second independent request.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A timeout after task acceptance produces a Try again button that silently creates a second task under a new key.",
  "required_decision": "Model operation, transport connection and visible draft text are different states"
}
```

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://react.dev/learn
- https://www.typescriptlang.org/docs/handbook/intro.html

# How do you bind user feedback to the exact persisted answer and its evidence version?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: product-delivery
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Feedback needs an authoritative target.** Persist a distinct assistant-message identifier and return it after commit. Bind that message to its authenticated conversation owner, task or operation identifier, answer revision, model configuration and source/index generation. A client-generated display key can help render a draft but must not be mistaken for the database's answer identity.

**Authorize the target on every submission.** The feedback endpoint should verify that the message exists, belongs to an accessible conversation and is an assistant answer eligible for feedback. A valid identifier alone is not authorization. Avoid revealing whether another user's private message exists through unnecessarily different errors. Validate rating bounds and treat free-text comments as untrusted input.

**Choose duplicate and revision semantics.** A unique constraint such as principal plus message plus feedback kind can implement one current rating with explicit updates. Alternatively, preserve append-only revisions with an active pointer for analysis. Regenerating an answer should produce a new revision or message identity; otherwise old negative feedback may silently attach to new text.

**Preserve evaluation provenance.** Analyze feedback by the actual answer and evidence version, not just the question text. Separate user satisfaction from factual correctness and avoid treating sparse voluntary ratings as an unbiased evaluation dataset. In an unsaved-stream state, disable durable feedback until a real message identity is reconciled. The example enforces ownership and idempotent current-rating updates in a small local store.

## Why

A user sees two regenerated answers to the same question and rates only the second. Separate answer identities let analysts attribute that rating to its model and evidence version instead of blaming the first answer.

## Worked Case

A user sees two regenerated answers to the same question and rates only the second. Separate answer identities let analysts attribute that rating to its model and evidence version instead of blaming the first answer.

## Risk

Accepting arbitrary message IDs enables cross-user feedback manipulation. Reusing an ID after regeneration corrupts evaluation provenance.

## Trade-off

Append-only feedback gives a better audit trail but needs revision handling; one current rating is simpler for the UI.

## Try This

Rate a saved answer, update its rating, attempt to rate another owner's message and try submitting feedback for an unsaved draft.

## Follow-ups

### Can negative ratings become training labels automatically?

Not safely. Ratings can reflect latency, tone or an unwanted but correct refusal. Review provenance, sampling bias, privacy and label quality before using them for model updates.

### What if the client times out submitting feedback?

Retry with a stable feedback operation identity or use an idempotent current-rating update. Avoid appending duplicate votes on every transport retry.

## Citations

- https://www.sqlite.org/lang_transaction.html

# How should loading, partial answers, abstention and committed outcomes appear in an AI interface?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: product-delivery
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

The interface should represent what the system actually knows: waiting, partial generated text, supported completion, insufficient evidence, failure and authoritative operation state. Streamed text is provisional content, not proof that a domain effect committed. Preserve focus, readable status and a recoverable user action when a request fails. Feedback should attach to stable message or operation identities, not a transient screen position. Invalidate obsolete responses after account or conversation changes and avoid leaving private stale content visible.

## Why

A user cancels while text is streaming. The interface can stop showing new text immediately but must separately check whether any requested backend effect was already accepted before describing the entire operation as cancelled.

## Worked Case

A user cancels while text is streaming. The interface can stop showing new text immediately but must separately check whether any requested backend effect was already accepted before describing the entire operation as cancelled.

## Risk

An optimistic success label can contradict authoritative state.

## Trade-off

Immediate feedback improves responsiveness when provisional and final states are clearly distinguished.

## Try This

Test every visible state, including a late old response after an identity switch.

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://react.dev/learn
- https://www.typescriptlang.org/docs/handbook/intro.html
