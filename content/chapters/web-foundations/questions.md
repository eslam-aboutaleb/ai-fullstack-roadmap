<!-- chapter: web-foundations -->

# Trace an HTTPS request from a browser address to an application response.

<!-- meta
domain: backend
subdomain: web-foundations
module: web-foundations
concept: Trace an HTTPS request from a browser address to an application response.
difficulty: interview
misconception_target: Missing the stated request lifecycle boundary: A slow request spends most of its time establishing a connection, while the application handler’s timing is short. Server-only telemetry misses the user-visible wait.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

The browser resolves an address, establishes transport, authenticates the server through TLS, and sends an HTTP request for an origin and target. Intermediaries may route or cache it before the application validates identity, input and authorization. Separate network establishment, server processing and response consumption when measuring latency; their failures imply different recovery decisions.

Engineering case: A slow request spends most of its time establishing a connection, while the application handler’s timing is short. Server-only telemetry misses the user-visible wait.

Reasoning under a changed assumption: No. TLS protects and authenticates the transport endpoint. Application identity and object-level permission checks remain independent.

## Spoken Summary

The browser resolves an address, establishes transport, authenticates the server through TLS, and sends an HTTP request for an origin and target. Intermediaries may route or cache it before the application validates identity, input and authorization. Separate network establishment, server processing and response consumption when measuring latency; their failures imply different recovery decisions.

## Why

The browser resolves an address, establishes transport, authenticates the server through TLS, and sends an HTTP request for an origin and target. Intermediaries may route or cache it before the application validates identity, input and authorization. Separate network establishment, server processing and response consumption when measuring latency; their failures imply different recovery decisions.

## Production Case

A slow request spends most of its time establishing a connection, while the application handler’s timing is short. Server-only telemetry misses the user-visible wait.

## Risk

A slow request spends most of its time establishing a connection, while the application handler’s timing is short. Server-only telemetry misses the user-visible wait.

## Trade-off

No. TLS protects and authenticates the transport endpoint. Application identity and object-level permission checks remain independent.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Request lifecycle**: The browser resolves an address, establishes transport, authenticates the server through TLS, and sends an HTTP request for an origin and target.

## Alternatives

- No. TLS protects and authenticates the transport endpoint. Application identity and object-level permission checks remain independent.

## Pitfalls

- A slow request spends most of its time establishing a connection, while the application handler’s timing is short. Server-only telemetry misses the user-visible wait.

## Follow-ups

### Does TLS authorize access to an individual record?

No. TLS protects and authenticates the transport endpoint. Application identity and object-level permission checks remain independent.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A slow request spends most of its time establishing a connection, while the application handler’s timing is short. Server-only telemetry misses the user-visible wait.",
  "decision": "The browser resolves an address, establishes transport, authenticates the server through TLS, and sends an HTTP request for an origin and target"
}
```

## Citations

- https://www.rfc-editor.org/rfc/rfc9110.html
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://api-security.owasp.org/editions/2023/en/0x11-t10

# How do safe methods, idempotent methods and an application operation key differ?

<!-- meta
domain: backend
subdomain: web-foundations
module: web-foundations
concept: How do safe methods, idempotent methods and an application operation key differ?
difficulty: interview
misconception_target: Missing the stated idempotent effect boundary: A POST creates a task but its response is lost. Repeating with the original key and matching payload returns the same logical task.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Safety concerns whether the method is intended to change server state; idempotence concerns the intended effect of repeating a request. An operation key lets an application bind a logical mutation to stable content. HTTP method semantics do not prove that a particular implementation is safe, and a key must reject changed content rather than merge unrelated requests.

Engineering case: A POST creates a task but its response is lost. Repeating with the original key and matching payload returns the same logical task.

Reasoning under a changed assumption: That violates the expected safe-method contract and exposes the action to caches, prefetching and automated traversal. Use an explicit authorized mutation contract.

## Spoken Summary

Safety concerns whether the method is intended to change server state; idempotence concerns the intended effect of repeating a request. An operation key lets an application bind a logical mutation to stable content. HTTP method semantics do not prove that a particular implementation is safe, and a key must reject changed content rather than merge unrelated requests.

## Why

Safety concerns whether the method is intended to change server state; idempotence concerns the intended effect of repeating a request. An operation key lets an application bind a logical mutation to stable content. HTTP method semantics do not prove that a particular implementation is safe, and a key must reject changed content rather than merge unrelated requests.

## Production Case

A POST creates a task but its response is lost. Repeating with the original key and matching payload returns the same logical task.

## Risk

A POST creates a task but its response is lost. Repeating with the original key and matching payload returns the same logical task.

## Trade-off

That violates the expected safe-method contract and exposes the action to caches, prefetching and automated traversal. Use an explicit authorized mutation contract.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Idempotent effect**: Safety concerns whether the method is intended to change server state; idempotence concerns the intended effect of repeating a request.

## Alternatives

- That violates the expected safe-method contract and exposes the action to caches, prefetching and automated traversal. Use an explicit authorized mutation contract.

## Pitfalls

- A POST creates a task but its response is lost. Repeating with the original key and matching payload returns the same logical task.

## Follow-ups

### Can GET perform a payment because it is easier to call?

That violates the expected safe-method contract and exposes the action to caches, prefetching and automated traversal. Use an explicit authorized mutation contract.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A POST creates a task but its response is lost. Repeating with the original key and matching payload returns the same logical task.",
  "decision": "Safety concerns whether the method is intended to change server state; idempotence concerns the intended effect of repeating a request"
}
```

## Citations

- https://www.rfc-editor.org/rfc/rfc9110.html
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://api-security.owasp.org/editions/2023/en/0x11-t10

# When should an API distinguish invalid input, unauthenticated access and missing records?

<!-- meta
domain: backend
subdomain: web-foundations
module: web-foundations
concept: When should an API distinguish invalid input, unauthenticated access and missing records?
difficulty: interview
misconception_target: Missing the stated http error contract boundary: An API reports every problem as 200 with a message string. The browser treats an authentication failure as a successful empty answer.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Use a documented error contract separating malformed input, absent or invalid authentication, authorization failure and unavailable dependencies. The exact status choices must match the API policy, including whether to conceal cross-owner record existence. Stable machine-readable error codes let the client react without scraping prose or exposing internal diagnostics.

Engineering case: An API reports every problem as 200 with a message string. The browser treats an authentication failure as a successful empty answer.

Reasoning under a changed assumption: No. Preserve useful internal correlation and diagnostics without returning secrets, private values or unnecessary implementation details.

## Spoken Summary

Use a documented error contract separating malformed input, absent or invalid authentication, authorization failure and unavailable dependencies. The exact status choices must match the API policy, including whether to conceal cross-owner record existence. Stable machine-readable error codes let the client react without scraping prose or exposing internal diagnostics.

## Why

Use a documented error contract separating malformed input, absent or invalid authentication, authorization failure and unavailable dependencies. The exact status choices must match the API policy, including whether to conceal cross-owner record existence. Stable machine-readable error codes let the client react without scraping prose or exposing internal diagnostics.

## Production Case

An API reports every problem as 200 with a message string. The browser treats an authentication failure as a successful empty answer.

## Risk

An API reports every problem as 200 with a message string. The browser treats an authentication failure as a successful empty answer.

## Trade-off

No. Preserve useful internal correlation and diagnostics without returning secrets, private values or unnecessary implementation details.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **HTTP error contract**: Use a documented error contract separating malformed input, absent or invalid authentication, authorization failure and unavailable dependencies.

## Alternatives

- No. Preserve useful internal correlation and diagnostics without returning secrets, private values or unnecessary implementation details.

## Pitfalls

- An API reports every problem as 200 with a message string. The browser treats an authentication failure as a successful empty answer.

## Follow-ups

### Should an error response include the full database query?

No. Preserve useful internal correlation and diagnostics without returning secrets, private values or unnecessary implementation details.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "An API reports every problem as 200 with a message string. The browser treats an authentication failure as a successful empty answer.",
  "decision": "Use a documented error contract separating malformed input, absent or invalid authentication, authorization failure and unavailable dependencies"
}
```

## Citations

- https://www.rfc-editor.org/rfc/rfc9110.html
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://api-security.owasp.org/editions/2023/en/0x11-t10

# Why is CORS not authentication or a server-to-server access control system?

<!-- meta
domain: backend
subdomain: web-foundations
module: web-foundations
concept: Why is CORS not authentication or a server-to-server access control system?
difficulty: interview
misconception_target: Missing the stated browser origin policy boundary: A backend accepts any bearerless request because its CORS allowlist includes only the official website. A command-line client can still call it directly.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

CORS is a browser policy governing which origins may read certain cross-origin responses. Non-browser clients do not enforce it. Authenticate and authorize the request on the server regardless of Origin. A preflight is a browser permission check for a request shape, not proof that its eventual caller owns the target object.

Engineering case: A backend accepts any bearerless request because its CORS allowlist includes only the official website. A command-line client can still call it directly.

Reasoning under a changed assumption: No. Cookies can be attached automatically under their rules and some cross-origin requests can be sent without a preflight. Apply an explicit cookie and CSRF threat model.

## Spoken Summary

CORS is a browser policy governing which origins may read certain cross-origin responses. Non-browser clients do not enforce it. Authenticate and authorize the request on the server regardless of Origin. A preflight is a browser permission check for a request shape, not proof that its eventual caller owns the target object.

## Why

CORS is a browser policy governing which origins may read certain cross-origin responses. Non-browser clients do not enforce it. Authenticate and authorize the request on the server regardless of Origin. A preflight is a browser permission check for a request shape, not proof that its eventual caller owns the target object.

## Production Case

A backend accepts any bearerless request because its CORS allowlist includes only the official website. A command-line client can still call it directly.

## Risk

A backend accepts any bearerless request because its CORS allowlist includes only the official website. A command-line client can still call it directly.

## Trade-off

No. Cookies can be attached automatically under their rules and some cross-origin requests can be sent without a preflight. Apply an explicit cookie and CSRF threat model.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Browser origin policy**: CORS is a browser policy governing which origins may read certain cross-origin responses.

## Alternatives

- No. Cookies can be attached automatically under their rules and some cross-origin requests can be sent without a preflight. Apply an explicit cookie and CSRF threat model.

## Pitfalls

- A backend accepts any bearerless request because its CORS allowlist includes only the official website. A command-line client can still call it directly.

## Follow-ups

### Does CORS alone prevent CSRF?

No. Cookies can be attached automatically under their rules and some cross-origin requests can be sent without a preflight. Apply an explicit cookie and CSRF threat model.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A backend accepts any bearerless request because its CORS allowlist includes only the official website. A command-line client can still call it directly.",
  "decision": "CORS is a browser policy governing which origins may read certain cross-origin responses"
}
```

## Citations

- https://www.rfc-editor.org/rfc/rfc9110.html
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://api-security.owasp.org/editions/2023/en/0x11-t10

# How do cookie sessions and browser-held bearer tokens create different risks?

<!-- meta
domain: backend
subdomain: web-foundations
module: web-foundations
concept: How do cookie sessions and browser-held bearer tokens create different risks?
difficulty: interview
misconception_target: Missing the stated session authority boundary: After logout, a pending request from the previous user writes private text into the newly signed-in user’s screen.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

A session cookie can be HttpOnly so ordinary JavaScript cannot read its value, but browser-attached credentials require a CSRF policy and appropriate cookie attributes. JavaScript-held bearer tokens can be stolen by successful script injection. Both approaches need expiry, server verification, object authorization and invalidation of user-scoped caches on identity changes.

Engineering case: After logout, a pending request from the previous user writes private text into the newly signed-in user’s screen.

Reasoning under a changed assumption: No. Consider server session or token revocation policy, in-flight operations, shared caches and every retained representation of the old user’s data.

## Spoken Summary

A session cookie can be HttpOnly so ordinary JavaScript cannot read its value, but browser-attached credentials require a CSRF policy and appropriate cookie attributes. JavaScript-held bearer tokens can be stolen by successful script injection. Both approaches need expiry, server verification, object authorization and invalidation of user-scoped caches on identity changes.

## Why

A session cookie can be HttpOnly so ordinary JavaScript cannot read its value, but browser-attached credentials require a CSRF policy and appropriate cookie attributes. JavaScript-held bearer tokens can be stolen by successful script injection. Both approaches need expiry, server verification, object authorization and invalidation of user-scoped caches on identity changes.

## Production Case

After logout, a pending request from the previous user writes private text into the newly signed-in user’s screen.

## Risk

After logout, a pending request from the previous user writes private text into the newly signed-in user’s screen.

## Trade-off

No. Consider server session or token revocation policy, in-flight operations, shared caches and every retained representation of the old user’s data.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Session authority**: A session cookie can be HttpOnly so ordinary JavaScript cannot read its value, but browser-attached credentials require a CSRF policy and appropriate cookie attributes.

## Alternatives

- No. Consider server session or token revocation policy, in-flight operations, shared caches and every retained representation of the old user’s data.

## Pitfalls

- After logout, a pending request from the previous user writes private text into the newly signed-in user’s screen.

## Follow-ups

### Is clearing local storage a complete logout design?

No. Consider server session or token revocation policy, in-flight operations, shared caches and every retained representation of the old user’s data.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "After logout, a pending request from the previous user writes private text into the newly signed-in user’s screen.",
  "decision": "A session cookie can be HttpOnly so ordinary JavaScript cannot read its value, but browser-attached credentials require a CSRF policy and appropriate cookie attributes"
}
```

## Citations

- https://www.rfc-editor.org/rfc/rfc9110.html
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://api-security.owasp.org/editions/2023/en/0x11-t10

# What makes API pagination stable while records are being inserted?

<!-- meta
domain: backend
subdomain: web-foundations
module: web-foundations
concept: What makes API pagination stable while records are being inserted?
difficulty: interview
misconception_target: Missing the stated cursor ordering boundary: An infinite-scroll page uses timestamp alone. Two rows share the same timestamp and one disappears between pages.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Offset pagination can shift under concurrent inserts and deletes. A cursor can encode a stable ordering boundary such as created_at plus a unique ID, but still needs declared consistency and filtering semantics. Apply caller scope before selecting the page and bind cursors to their query contract. Avoid treating an opaque cursor as permission.

Engineering case: An infinite-scroll page uses timestamp alone. Two rows share the same timestamp and one disappears between pages.

Reasoning under a changed assumption: No. A cursor identifies a continuation boundary. Snapshot consistency requires additional storage or transaction semantics and a defined lifetime.

## Spoken Summary

Offset pagination can shift under concurrent inserts and deletes. A cursor can encode a stable ordering boundary such as created_at plus a unique ID, but still needs declared consistency and filtering semantics. Apply caller scope before selecting the page and bind cursors to their query contract. Avoid treating an opaque cursor as permission.

## Why

Offset pagination can shift under concurrent inserts and deletes. A cursor can encode a stable ordering boundary such as created_at plus a unique ID, but still needs declared consistency and filtering semantics. Apply caller scope before selecting the page and bind cursors to their query contract. Avoid treating an opaque cursor as permission.

## Production Case

An infinite-scroll page uses timestamp alone. Two rows share the same timestamp and one disappears between pages.

## Risk

An infinite-scroll page uses timestamp alone. Two rows share the same timestamp and one disappears between pages.

## Trade-off

No. A cursor identifies a continuation boundary. Snapshot consistency requires additional storage or transaction semantics and a defined lifetime.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Cursor ordering**: Offset pagination can shift under concurrent inserts and deletes.

## Alternatives

- No. A cursor identifies a continuation boundary. Snapshot consistency requires additional storage or transaction semantics and a defined lifetime.

## Pitfalls

- An infinite-scroll page uses timestamp alone. Two rows share the same timestamp and one disappears between pages.

## Follow-ups

### Can a cursor guarantee a snapshot without a snapshot mechanism?

No. A cursor identifies a continuation boundary. Snapshot consistency requires additional storage or transaction semantics and a defined lifetime.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "An infinite-scroll page uses timestamp alone. Two rows share the same timestamp and one disappears between pages.",
  "decision": "Offset pagination can shift under concurrent inserts and deletes"
}
```

## Citations

- https://www.rfc-editor.org/rfc/rfc9110.html
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://api-security.owasp.org/editions/2023/en/0x11-t10

# Which API failures can be retried safely and within what budget?

<!-- meta
domain: backend
subdomain: web-foundations
module: web-foundations
concept: Which API failures can be retried safely and within what budget?
difficulty: interview
misconception_target: Missing the stated retry eligibility boundary: A client retries an unauthorized write five times, spending resources while never changing the credential or ownership condition.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Retry only under a policy that considers method/effect identity, failure class, remaining deadline and attempt budget. A rate-limit response may supply retry guidance, while invalid input or permission denial usually requires a changed decision. Backoff and jitter reduce synchronized retry pressure but do not resolve uncertain commits.

Engineering case: A client retries an unauthorized write five times, spending resources while never changing the credential or ownership condition.

Reasoning under a changed assumption: Use the original operation key and an authoritative status or receipt. A timeout alone cannot identify whether the effect happened.

## Spoken Summary

Retry only under a policy that considers method/effect identity, failure class, remaining deadline and attempt budget. A rate-limit response may supply retry guidance, while invalid input or permission denial usually requires a changed decision. Backoff and jitter reduce synchronized retry pressure but do not resolve uncertain commits.

## Why

Retry only under a policy that considers method/effect identity, failure class, remaining deadline and attempt budget. A rate-limit response may supply retry guidance, while invalid input or permission denial usually requires a changed decision. Backoff and jitter reduce synchronized retry pressure but do not resolve uncertain commits.

## Production Case

A client retries an unauthorized write five times, spending resources while never changing the credential or ownership condition.

## Risk

A client retries an unauthorized write five times, spending resources while never changing the credential or ownership condition.

## Trade-off

Use the original operation key and an authoritative status or receipt. A timeout alone cannot identify whether the effect happened.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Retry eligibility**: Retry only under a policy that considers method/effect identity, failure class, remaining deadline and attempt budget.

## Alternatives

- Use the original operation key and an authoritative status or receipt. A timeout alone cannot identify whether the effect happened.

## Pitfalls

- A client retries an unauthorized write five times, spending resources while never changing the credential or ownership condition.

## Follow-ups

### What if the server timed out after committing?

Use the original operation key and an authoritative status or receipt. A timeout alone cannot identify whether the effect happened.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A client retries an unauthorized write five times, spending resources while never changing the credential or ownership condition.",
  "decision": "Retry only under a policy that considers method/effect identity, failure class, remaining deadline and attempt budget"
}
```

## Citations

- https://www.rfc-editor.org/rfc/rfc9110.html
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://api-security.owasp.org/editions/2023/en/0x11-t10

# How do you evolve a JSON API when producers and consumers run different schema versions?

<!-- meta
answer_format: conceptual
domain: data-integrity
subdomain: web-foundations
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Assume deployments overlap.** A producer may emit a new field while an older consumer still runs, or a stored event may be replayed years later. Define compatibility rules for required fields, optional fields, enum values and type changes. A field addition is only compatible if actual consumers tolerate it and its absence has a truthful meaning.

**Dispatch by an explicit schema version.** Validate an incoming version before translating it to the internal domain model. Use a controlled decoder or upcaster for each supported old version. Reject unsupported future versions rather than interpreting them with yesterday's defaults. Keep data revision, which tracks edits, separate from schema version, which identifies structure.

**Be precise about missing and null.** A missing field can mean not supplied, while null can mean explicitly empty or unknown. Defaults should preserve documented semantics. Renaming or changing the type of a required field may need an expand-and-contract rollout: introduce compatible reads, write the new form, backfill and remove old support only after consumers and retained data permit it.

**Test both directions and stored history.** Check old producer to new consumer, new producer to supported older consumer where promised, and replay of persisted payloads. Record decoder failures and avoid dropping unknown fields during a read-modify-write path when preservation is part of the contract. The example supports two explicitly defined versions and rejects a future version instead of silently guessing its structure.

## Why

A consumer knows schemas 1 and 2. It receives schema 3 from a newer producer. Treating missing familiar fields as empty strings would turn an incompatibility into apparently valid but wrong data.

## Worked Case

A consumer knows schemas 1 and 2. It receives schema 3 from a newer producer. Treating missing familiar fields as empty strings would turn an incompatibility into apparently valid but wrong data.

## Risk

A permissive default can make incompatible events pass validation and contaminate downstream state.

## Trade-off

Long compatibility windows ease rolling upgrades but increase codec and migration maintenance.

## Try This

Create a compatibility matrix for a renamed field, a new optional field, a new enum value and a missing-versus-null distinction.

## Follow-ups

### Can a server ignore every unknown field safely?

Not universally. Ignoring optional forward-compatible metadata may be fine; ignoring a misspelled authorization or money field can be dangerous. Apply explicit policy by endpoint and field semantics.

### How long should an old decoder remain?

Base removal on supported clients, stored payload retention and replay requirements. Observing no recent live traffic does not prove that historical events no longer need decoding.

## Citations

- https://docs.python.org/3/library/json.html

# What belongs in a URL, request header and request body?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: web-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A URL locates a resource and may carry query parameters; headers carry protocol metadata such as accepted representations, authorization and caching conditions; the body carries the request representation where the method contract supports it. Avoid placing secrets in URLs because they can appear in history, logs and referrer data. Validate all three as untrusted input. Choosing a transport location does not change authorization requirements, and a large JSON body still needs size limits and a schema.

## Why

A list endpoint can accept a bounded page size in its query string and a bearer credential in a header. It must not trust an owner query parameter as proof of the caller's identity.

## Worked Case

A list endpoint can accept a bounded page size in its query string and a bearer credential in a header. It must not trust an owner query parameter as proof of the caller's identity.

## Risk

Sensitive query parameters can be retained outside the application's intended storage.

## Trade-off

Use explicit resource and representation contracts rather than arbitrary placement.

## Try This

Design a list request and identify where identity, pagination and filtering belong.

## Citations

- https://www.rfc-editor.org/rfc/rfc9110.html
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://api-security.owasp.org/editions/2023/en/0x11-t10

# How do HTTP status codes and error bodies form a usable API contract?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: web-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Use the **HTTP status** for the broad protocol outcome and a **stable application error code** for client recovery. Human-readable messages can change or be translated; clients should not parse their English wording.

| Situation | Typical status | Client decision |
| --- | --- | --- |
| Malformed request | 400 | Correct the representation |
| Missing or invalid authentication | 401 | Obtain valid credentials under the authentication contract |
| Authenticated but forbidden | 403 | Stop or request the necessary permission |
| Missing resource | 404 | Handle absence under the privacy policy |
| Current-state conflict | 409 | Refresh or reconcile the operation |
| Semantically invalid content | 422 when chosen by the API contract | Correct the invalid fields |
| Rate or capacity policy exceeded | 429 | Follow the bounded retry policy and any valid retry hint |
| Temporary service unavailability | 503 | Retry only when the operation and deadline allow it |

These are **contract choices, not substitutes for domain reasoning**. A service may deliberately avoid exposing whether another user's resource exists. It must not expose internal traces or credentials through error details.

Return a safe request/operation identifier and a documented error category where useful. Do not return an apparently successful response when a required operation failed, and do not blindly retry a stale version conflict as if it were a dropped connection.

## Why

An optimistic version conflict can return 409 with a safe conflict category. A client should refresh authoritative state instead of endlessly resending the same stale version as if it were a transient connection error.

## Worked Case

An optimistic version conflict can return 409 with a safe conflict category. A client should refresh authoritative state instead of endlessly resending the same stale version as if it were a transient connection error.

## Risk

An undifferentiated 500 response makes safe client recovery difficult.

## Trade-off

Rich errors improve recovery but must preserve privacy and avoid internal implementation leakage.

## Try This

Define error bodies for invalid input, stale version and temporary overload.

## Citations

- https://www.rfc-editor.org/rfc/rfc9110.html
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://api-security.owasp.org/editions/2023/en/0x11-t10

# How do cookies, sessions and bearer tokens establish different trust boundaries?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: web-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A cookie is browser-managed storage attached according to domain, path and security attributes. A server session commonly stores authoritative login state keyed by a cookie value. A bearer token grants access to whoever possesses it within its validity and scope. Storage location, automatic attachment and revocation determine different risks. Protect secrets in transit and at rest, rotate session identity at appropriate authentication boundaries, and authorize the current action server-side. A client-side decoded claim is not verification.

## Why

A stolen bearer token can be replayed until expiry or revocation policy stops it. An HttpOnly cookie reduces script access to the cookie but does not stop an injected script from making actions in the victim's browser context.

## Worked Case

A stolen bearer token can be replayed until expiry or revocation policy stops it. An HttpOnly cookie reduces script access to the cookie but does not stop an injected script from making actions in the victim's browser context.

## Risk

Treating one token storage option as solving all browser attacks leaves other controls missing.

## Trade-off

Session and token choices depend on clients, revocation and trust boundaries.

## Try This

Trace credential creation, storage, automatic attachment, validation and logout for one design.

## Citations

- https://www.rfc-editor.org/rfc/rfc9110.html
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://api-security.owasp.org/editions/2023/en/0x11-t10

# How do browser origins, sites and preflight requests differ?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: web-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

An origin is the scheme, host and port tuple used by important browser isolation rules. A site is a different grouping used by mechanisms such as SameSite cookies. Cross-origin requests may require a CORS preflight that asks the server about permitted methods and headers. A permitted response is not an authorization decision, and some cross-origin requests can be sent even when scripts cannot read their responses. Specify credentials behavior and allowed origins deliberately rather than reflecting arbitrary request origins.

## Why

A development UI on one port and API on another are different origins even on the same host. An allow-origin policy can permit reading the response without deciding which account's rows the API may return.

## Worked Case

A development UI on one port and API on another are different origins even on the same host. An allow-origin policy can permit reading the response without deciding which account's rows the API may return.

## Risk

Confusing origins with sites leads to incorrect cookie and CORS assumptions.

## Trade-off

Narrow policies reduce accidental exposure while development proxies can simplify local setup.

## Try This

Compare two URLs by scheme, host and port, then predict credential and preflight behavior.

## Citations

- https://www.rfc-editor.org/rfc/rfc9110.html
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://api-security.owasp.org/editions/2023/en/0x11-t10

# How do HTTP caching, ETags and conditional requests avoid stale or leaked data?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: web-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A cache stores a representation under a key and freshness policy. An ETag identifies a representation version and can support conditional validation or guarded updates. Cache keys and Vary behavior must include all relevant representation inputs. Private user data should not enter a shared cache under an identity-blind key. A 304 response reuses an existing representation under the cache contract; it does not re-run every business authorization policy by magic. Coordinate expiry and permission revocation requirements explicitly.

## Why

A public product description can be cached differently from an owner-specific account balance. Reusing the same URL alone as a shared key for both users can disclose one user's balance to another.

## Worked Case

A public product description can be cached differently from an owner-specific account balance. Reusing the same URL alone as a shared key for both users can disclose one user's balance to another.

## Risk

A correct freshness interval does not establish correct tenant isolation.

## Trade-off

Caching reduces work but adds invalidation, versioning and privacy obligations.

## Try This

Design cache policies and conditional responses for a public document and a private account view.

## Citations

- https://www.rfc-editor.org/rfc/rfc9110.html
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://api-security.owasp.org/editions/2023/en/0x11-t10

# How do cursor pagination and offset pagination behave under concurrent updates?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: web-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Offset pagination skips a count in an ordered result, which is simple but can become expensive and unstable when rows are inserted or deleted before the next page. Cursor pagination resumes from an explicit ordering boundary, usually including a unique tie-breaker. It still needs stable filters, ordering and an authority or snapshot contract if a complete consistent scan is required. Validate opaque cursors and scope them to the caller and query instead of treating them as trusted arbitrary database instructions.

## Why

Paging by created_at alone can skip rows sharing the same timestamp. A compound boundary using created_at and a unique identifier gives a deterministic next position under the chosen ordering.

## Worked Case

Paging by created_at alone can skip rows sharing the same timestamp. A compound boundary using created_at and a unique identifier gives a deterministic next position under the chosen ordering.

## Risk

A cursor is not automatically a snapshot of a changing source.

## Trade-off

Offsets suit small stable views; cursors suit larger or changing ordered streams.

## Try This

Page records with equal timestamps while inserting one new row between requests.

## Citations

- https://www.rfc-editor.org/rfc/rfc9110.html
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://api-security.owasp.org/editions/2023/en/0x11-t10

# How should webhooks be authenticated, deduplicated and acknowledged?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: web-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A webhook is an inbound event delivery, often retried by the sender. Verify the sender's documented signature over the exact required bytes, apply replay controls appropriate to its contract, and validate the event type and payload. Persist a deduplication identity and accepted work before acknowledging when processing is asynchronous. A quick success response says the event was accepted under that contract, not that every downstream action completed. Keep authoritative event status and a repair path for later failures.

## Why

A sender retries event E9 after a lost acknowledgement. The receiver should recognize the same event and avoid charging or notifying twice, while retaining a clear record of its original acceptance and processing state.

## Worked Case

A sender retries event E9 after a lost acknowledgement. The receiver should recognize the same event and avoid charging or notifying twice, while retaining a clear record of its original acceptance and processing state.

## Risk

Parsing and reserializing before signature verification can change the bytes being verified.

## Trade-off

Asynchronous handling improves response time but requires durable ownership and operational visibility.

## Try This

Simulate duplicate delivery and a crash after acceptance but before processing.

## Citations

- https://www.rfc-editor.org/rfc/rfc9110.html
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://api-security.owasp.org/editions/2023/en/0x11-t10

# How do reverse proxies, load balancers and timeouts change an API deployment?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: web-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A reverse proxy accepts client requests and forwards them to application workers; a load balancer chooses among backends. They can terminate TLS, buffer bodies, enforce size limits and impose their own timeouts. An application deadline longer than an upstream proxy timeout may leave expensive work running after the client is gone. Trust forwarded identity or address headers only from configured trusted infrastructure. Verify streaming, cancellation and connection lifetimes through the actual deployed path, not only a direct localhost connection.

## Why

A stream that works directly can appear in one burst through a buffering proxy. An idle timeout can terminate a quiet stream even though the application believes its connection is still active.

## Worked Case

A stream that works directly can appear in one burst through a buffering proxy. An idle timeout can terminate a quiet stream even though the application believes its connection is still active.

## Risk

Trusting arbitrary forwarded headers can let clients spoof network context.

## Trade-off

Proxies centralize controls while adding configuration and timeout interactions.

## Try This

Trace every hop's body limit, buffering policy and timeout for a streaming request.

## Citations

- https://www.rfc-editor.org/rfc/rfc9110.html
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://api-security.owasp.org/editions/2023/en/0x11-t10
