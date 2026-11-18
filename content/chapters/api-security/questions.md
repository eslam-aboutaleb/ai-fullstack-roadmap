<!-- chapter: api-security -->

# How are JWTs validated and converted into database ownership?

<!-- meta
domain: backend
subdomain: api-security
module: api-security
concept: How are JWTs validated and converted into database ownership
difficulty: foundations
misconception_target: HTTPS alone secures an API
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Validate the token under an explicit issuer, audience, algorithm, and lifetime profile, resolve the subject to a trusted application principal, and authorize access to each resource. A model-generated owner identifier cannot replace authenticated identity.

## Spoken Summary

Validate JWT signature with an allowed algorithm and trusted keys, then check issuer, audience, expiry and relevant claims. Map the verified subject to a trusted application identity and scope every resource operation by that identity. A user-supplied owner ID is not authority.

## Why

Validate signature, allowed algorithm, issuer, audience, expiry, and required claims under the token profile. Resolve the trusted principal and enforce resource ownership in services, not model arguments.

## Production Case

An attacker submits a real task UUID owned by another customer using their own valid token. The query must combine task ID with trusted owner scope and return no other-owner state.

## Risk

A valid token may remain usable after access should be revoked unless the product checks revocation or session versions. Choose lifetime and refresh behavior from the threat model.

## Trade-off

Stateless token checks scale well, while immediate revocation needs additional state or shorter-lived credentials. Database user lookup already provides one current-state validation point.

## Try This

Test expired, malformed, deleted-user, wrong-signature, and valid tokens. Verify that a known request ID still requires owner authorization.

## Execution Timeline

Request received → Extract credentials → Verify identity → Check ownership → Validate input → Execute business logic → Return response

## Complexity

Authentication may verify a signature or fetch/cache trusted keys; authorization can require membership or object queries. Cache cautiously with expiry/revocation semantics and measure the actual lookup path.

## Definitions

- **Authentication**: Verifying who the caller is
- **Authorization**: Checking what the caller is allowed to do
- **Least privilege**: Granting only the minimum access needed

## Alternatives

- Role-based access control (RBAC)
- Attribute-based access control (ABAC)

## Pitfalls

- Missing ownership check
- Secrets in source code
- Input not validated before use

## Follow-ups

### Does a valid JWT authorize every resource?

No. It establishes verified claims; object permissions, tenant membership and allowed state transitions still require explicit checks.

## Example

> Explanation: Check ownership before executing any business logic.
> Output: Processed result or 403 Forbidden

```python
user = get_current_user(token)
if not owns_resource(user, doc_id):
    raise HTTPException(403)
result = service.process(doc_id, user)
```

## Citations

- https://owasp.org/www-project-top-ten/

# Why are HttpOnly, Secure, SameSite, CORS, and CSRF different controls?

## Answer

HttpOnly limits script access to cookies, Secure limits cookie transport to HTTPS, and SameSite constrains some cross-site sending. CORS controls browser access across origins. CSRF protection addresses unwanted state-changing requests made with ambient credentials. None is interchangeable with user authorization.

## Why

Set cookie and origin policies explicitly for the deployment. Review state-changing routes for CSRF and XSS exposure; CORS, SameSite, HttpOnly, and Secure address different browser behaviors.

## Risk

These settings do not establish a complete CSRF review of all mutations and deployment origins. XSS can still issue authorized actions even when it cannot read an HttpOnly cookie.

## Trade-off

Cookie authentication simplifies browser sessions but requires deliberate origin and state-change policy. Bearer clients have different storage and transport concerns.

## Try This

Build a matrix for sign-in, confirmation, cancellation, and logout across trusted and untrusted origins. State which server-side checks enforce each result.

# How does ContextVar prevent cross-request identity leakage?

## Answer

ContextVar associates a value with an asynchronous execution context rather than one mutable process-global variable. Concurrent requests can therefore carry different identities through await boundaries. It is a context propagation mechanism, not an authorization decision or durable identity store.

## Why

Bind task-local identity at the authenticated boundary and reset it in a finally block. A background task must receive a deliberate identity rather than rely on accidental inherited context.

## Risk

Capturing context for a task that outlives a request can retain stale identity. Failing to reset temporary bindings can also confuse tests or reused execution contexts. Server code must define where identity begins and ends.

## Trade-off

Implicit context reduces parameter threading and can hide dependencies. Explicit identity parameters improve local clarity and require more signatures.

## Try This

Run two concurrent tool calls under separate context bindings. Test missing identity and an outliving background task; verify both fail or receive an explicit service identity as intended.

# Why must case ownership be checked in tools as well as routes?

## Answer

Agent tools may execute through a runner, test harness, or future remote protocol without passing through a particular HTTP route. A protected route cannot be the only place a domain operation learns whose data it may access.

## Why

Authorize the resource inside the service called by every adapter. A protected chat endpoint cannot make a later model-selected identifier trustworthy.

## Risk

A model-supplied user_id is untrusted even if it is a valid UUID. A future LangChain adapter must not expose that internal parameter as a tool argument the model can freely choose.

## Trade-off

Repeated enforcement at domain boundaries adds code and protects alternate callers. Duplicated policy implementations can drift, so centralize shared service authorization where possible.

## Try This

Invoke the service request-search tool directly without an HTTP request and with the wrong user context. Verify that knowing another user's request ID does not reveal it.

# What is the distinction between RBAC and resource ownership here?

## Answer

Role-Based Access Control determines whether a principal may perform a category of action; ownership determines which records that principal may affect. A support operator role does not automatically justify unrestricted access to every customer's service requests.

## Why

Use roles for permitted categories of action and ownership for access to a particular resource. Check both when a privileged operation also targets tenant-scoped data.

## Risk

Replacing the allowlist with a broad role check without resource policy can overgrant authority. Tests that widen the allowlist for fixtures do not prove production administration is configured.

## Trade-off

Combining role and attribute checks is more expressive and more complex. A deny-by-default seam is safer than silently pretending a missing administrative policy exists.

## Try This

Define reader, customer, handler, and administrator actions with both role and record-scope rules. Map each rule to its actual enforcement point.

# Why does password hashing require more than naming Argon2?

## Answer

A password hash uses intentionally costly computation and salt to resist offline guessing. Operational parameters, input limits, verification errors, rehash policy, and login rate limiting matter too. A hash algorithm name alone does not establish timing-safe user enumeration resistance.

## Why

Use a valid dummy hash with a reviewed work factor for unknown accounts. Compare timing distributions under load and keep authentication errors consistent without suppressing operational diagnostics.

## Risk

Malformed dummy verification can return faster than a real check. Unbounded password input or excessive concurrent hashing can also consume resources before the agent is involved.

## Trade-off

Higher hashing cost protects stolen hashes and increases authentication resource use. Choose measured parameters and a valid equivalent dummy path.

## Try This

Benchmark known-user wrong-password and unknown-user checks with reviewed test data. Verify hash validity and compare distributions without asserting perfect constant time.

# How should confirmation tokens be treated as capabilities?

## Answer

A confirmation token identifies a specific prepared action and should be bound to the user, payload, pending state, and expiry. Possession alone should not bypass authentication. Material edits should produce a new reviewed operation and invalidate or supersede the old one server-side.

## Why

Bind confirmation to owner, exact parameters, revision, expiry, and pending state. Supersede earlier approvals explicitly after material changes and reject reused completed tokens.

## Risk

A model's statement cannot revoke a still-pending token. Some preparation logs also include tokens, increasing the audience that may see them even though owner binding remains required.

## Trade-off

Server-enforced supersession adds lifecycle bookkeeping and prevents stale confirmation. Keeping multiple live preparations is simpler but needs an honest user-visible model.

## Try This

Prepare an amount, correct it, then try both tokens. Document current behavior and specify the desired supersession invariant.

# Why must rate limiting, request-size limits, and tool budgets coexist?

## Answer

Request rate bounds arrival frequency, size limits bound per-request input, and tool or token budgets bound work initiated by one accepted request. An agent can turn one small request into many expensive provider calls, so requests per minute alone do not control cost.

## Why

Apply limits at request, run, model, and tool boundaries. Account for nested calls and retries so one accepted HTTP request cannot expand into unbounded downstream work.

## Risk

Fail-open Redis behavior preserves availability and can weaken fleet-wide limits during an outage. Model-generated loops may also stay within HTTP request limits while exhausting provider budgets.

## Trade-off

Layered budgets increase configuration and improve predictable resource use. Tight limits can interrupt legitimate multi-intent conversations and need explicit completion states.

## Try This

Estimate worst-case cost from maximum turns, tool calls, retries, candidates, and output tokens. Test overload without using real private service requests.

# How can error responses leak information even when access is denied?

## Answer

Different messages, status codes, timings, trace payloads, and raw exception strings can reveal record existence or internal details. A denial response should reveal only what the caller is entitled to learn, while internal diagnostics remain appropriately protected.

## Why

Return appropriately indistinguishable not-found or inaccessible responses when disclosure policy requires it. Keep private diagnostic detail in protected logs rather than client exception text.

## Risk

A model may repeat an internal error returned by a tool. Sanitizing only the final HTTP exception leaves tool results and streaming error events as additional channels.

## Trade-off

Generic external messages reduce detail for users and support; structured internal error categories preserve diagnosis without exposing private values.

## Try This

Compare responses for unknown and foreign-owned request IDs, invalid tokens, provider failures, and database errors. Inspect both the streamed events and final response.

# What does an effective threat-model review produce?

## Answer

It produces a concrete asset and actor map, trust boundaries, abuse cases, enforcement points, and tests. For this product, include private claim text, confirmation tokens, knowledge versions, prompt data, provider keys, session history, and traces.

## Why

List assets, actors, entry points, trust boundaries, and forbidden effects. Convert identified threats into owners, controls, and observable acceptance tests rather than a generic security checklist.

## Risk

A checklist detached from actual call sites can certify controls that are merely configured or documented. Threat modeling should include alternate paths such as evaluation, administration, scripts, and workers.

## Trade-off

A focused model tied to major workflows is maintainable. An exhaustive speculative catalog can consume time without improving concrete denial behavior.

## Try This

Pick cross-user disclosure, duplicate submission, and malicious-source instructions. For each, identify the earliest reliable enforcement point and a test proving denial.

# What must a signed bearer token prove before an owned resource can be returned?

<!-- meta
domain: backend
subdomain: api-security
module: api-security
concept: What must a signed bearer token prove before an owned resource can be returned?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A correctly signed token for another service is accepted because the API never checks audience.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Verify the declared token profile: trusted issuer and keys, permitted algorithm, audience, validity period and relevant claims. Map that authenticated identity to server-side authorization and scope the authoritative resource query. A valid signature alone does not prove that a token was issued for this API or that its subject owns the requested record.

Concrete engineering case: A correctly signed token for another service is accepted because the API never checks audience.

Boundary defense: No. Audience identifies an intended recipient. Ownership, role and lifecycle permissions remain resource-specific decisions.

## Spoken Summary

Verify the declared token profile: trusted issuer and keys, permitted algorithm, audience, validity period and relevant claims. Map that authenticated identity to server-side authorization and scope the authoritative resource query. A valid signature alone does not prove that a token was issued for this API or that its subject owns the requested record.

## Why

Verify the declared token profile: trusted issuer and keys, permitted algorithm, audience, validity period and relevant claims. Map that authenticated identity to server-side authorization and scope the authoritative resource query. A valid signature alone does not prove that a token was issued for this API or that its subject owns the requested record.

## Production Case

A correctly signed token for another service is accepted because the API never checks audience.

## Risk

A correctly signed token for another service is accepted because the API never checks audience.

## Trade-off

No. Audience identifies an intended recipient. Ownership, role and lifecycle permissions remain resource-specific decisions.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: api security**: Verify the declared token profile: trusted issuer and keys, permitted algorithm, audience, validity period and relevant claims.

## Alternatives

- No. Audience identifies an intended recipient. Ownership, role and lifecycle permissions remain resource-specific decisions.

## Pitfalls

- A correctly signed token for another service is accepted because the API never checks audience.

## Follow-ups

### Does checking audience remove the need for object authorization?

No. Audience identifies an intended recipient. Ownership, role and lifecycle permissions remain resource-specific decisions.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A correctly signed token for another service is accepted because the API never checks audience.",
  "required_decision": "Verify the declared token profile: trusted issuer and keys, permitted algorithm, audience, validity period and relevant claims"
}
```

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://www.rfc-editor.org/rfc/rfc9110.html
- https://www.rfc-editor.org/rfc/rfc9700.html
- https://spec.openapis.org/oas/latest.html
- https://json-schema.org/draft/2020-12/json-schema-validation
- https://api-security.owasp.org/editions/2023/en/0x11-t10

# How should token expiry, key rotation and logout work together?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: api-security
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Signature verification proves a token was signed by an accepted key under the selected algorithm; it does not alone prove issuer, audience, validity interval or current permission. Key rotation needs a controlled overlap and refresh policy. Logout of a browser session is different from immediate invalidation of every copied bearer token. Choose short validity, server-side revocation or another explicit session policy according to the threat and latency requirements. Never let a client select arbitrary verification algorithms or trusted keys.

## Why

Removing a token from local browser storage does not invalidate an attacker-held copy. If immediate revocation is required, the backend needs a revocation or session-state check rather than relying only on expiration.

## Worked Case

Removing a token from local browser storage does not invalidate an attacker-held copy. If immediate revocation is required, the backend needs a revocation or session-state check rather than relying only on expiration.

## Risk

Cached key or permission state can extend an unintended acceptance window.

## Trade-off

Stateless validation reduces lookups but complicates immediate revocation.

## Try This

Trace a stolen token through logout, permission removal, key rotation and expiry.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://www.rfc-editor.org/rfc/rfc9110.html
- https://www.rfc-editor.org/rfc/rfc9700.html
- https://spec.openapis.org/oas/latest.html
- https://json-schema.org/draft/2020-12/json-schema-validation
- https://api-security.owasp.org/editions/2023/en/0x11-t10
