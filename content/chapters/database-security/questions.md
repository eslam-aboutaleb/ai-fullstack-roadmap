<!-- chapter: database-security -->

# What does least privilege mean for application, migration, and reporting database roles?

## Answer

Use separate credentials for runtime queries, schema migration, and analysis. The application role should have only the tables and operations its workload needs; it should not need unrestricted DDL or superuser access. Read-only reporting still needs row and data-disclosure controls.

## Why

Provision separate application, migration, reporting, and worker roles. Verify actual grants and keep credentials outside model context; sharing one connection string does not establish least privilege.

## Risk

A single powerful credential turns a query injection, tool bug, or compromised worker into a broader database incident. A model must never receive that credential or arbitrary SQL authority.

## Trade-off

Separate roles require grants and migration coordination but reduce blast radius. One admin credential is convenient locally and inappropriate as evidence of production isolation.

## Try This

Design a grant matrix for API, embedding worker, notification worker, migrator, and analyst. Include which sensitive tables each must never read.

# How could PostgreSQL Row-Level Security complement owner-scoped queries?

<!-- meta
reference: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
-->

## Answer

RLS applies database policies to rows readable or writable through a role. It can add a second barrier when an application query forgets owner filtering. Its protection depends on actual role grants, bypass behavior, identity propagation, and tested policies.

## Why

Enable and test RLS under the actual non-bypass role. Bind identity transaction-locally, verify pooled connection reuse, and understand owner or administrative bypass behavior.

## Risk

Table owners or privileged roles can bypass knowledge rules under documented conditions. Connection reuse can leak session-level identity if it is not reset; transaction-local settings and pool tests matter.

## Trade-off

Database enforcement strengthens defense in depth but complicates jobs, migrations, tests, and administrative workflows. It does not replace server authentication.

## Try This

In a disposable schema, create a transaction-local owner setting and policy. Test two users through reused pooled connections and verify writes as well as reads.

# Why are parameterized values insufficient for arbitrary query generation?

## Answer

Binding values prevents them from being interpreted as SQL syntax in the intended parameter position. It does not make arbitrary table names, operators, SQL fragments, or model-generated statements safe. Query structure needs a trusted construction path and an allowlisted operation surface.

## Why

Parameterize values and allowlist identifiers, operators, and query shapes. Arbitrary generated SQL remains a privilege boundary even when some values use bound parameters.

## Risk

An LLM-generated SELECT can still disclose unauthorized rows, invoke expensive functions, or exploit permissions even if it contains no classic string-concatenation injection.

## Trade-off

Narrow domain tools limit exploratory flexibility and support predictable authorization. A natural-language analytics feature needs an independently constrained read model and query policy.

## Try This

Design an exact aggregate tool for a user's service requests using typed inputs. Explain why it is safer than giving the model a raw database connection.

# How do database credentials and TLS fit into the trust model?

## Answer

Credentials authenticate a process to the database; TLS protects transport and can verify server identity. Neither automatically limits which rows the process may read. Rotate credentials, use appropriate secret storage, and validate certificate settings in the actual deployment.

## Why

Verify server identity through the configured TLS policy, rotate credentials, and restrict network access. A reachable encrypted connection still needs resource authorization and least privilege.

## Risk

Printing URLs or raw driver errors can expose passwords or infrastructure details. Copying secrets into model context, traces, sample files, or shell arguments creates additional disclosure paths.

## Trade-off

Managed identities or short-lived credentials reduce secret lifetime where supported, while adding integration requirements. Static credentials are simpler and need deliberate rotation and incident response.

## Try This

Create a secret-free deployment evidence record showing connection identity, TLS verification mode, role grants, and rotation ownership. Do not include the secret value.

# Which timeouts protect database availability?

## Answer

Bound pool checkout, connection establishment, statement execution, lock waits, and idle transactions according to the workload. These limits solve different problems. An HTTP timeout alone may leave server-side queries or open transactions consuming resources.

## Why

Set connection, statement, lock, and transaction-duration limits according to workload. Cancel abandoned work and keep application deadlines shorter than an uncontrolled sequence of downstream waits.

## Risk

An expensive permitted query can be a denial-of-service vector. Very short timeouts can also cause retry amplification or repeatedly abort useful work.

## Trade-off

Tighter limits improve isolation and can reduce completion rates. Use separate knowledge rules for interactive search, migrations, and backfills instead of one global number.

## Try This

Propose settings for pool wait, lock wait, and statement time with a measured request budget. Simulate a blocked transaction and observe rollback and connection reuse.

# What is the difference between secure deletion, logical revocation, and retention?

## Answer

Revocation stops authorized disclosure. Logical deletion changes application visibility. Physical deletion removes stored copies, subject to backups and retention. Service records, embeddings, pending payloads, conversations, traces, and notifications can each retain different copies of the same private facts.

## Why

Distinguish removing search visibility from deleting retained originals, embeddings, caches, logs, and backups. Define which lifecycle obligation applies to every derived artifact.

## Risk

Deleting a relational row may leave vectors, trace payloads, exports, or historical messages accessible. Conversely, deleting everything indiscriminately can violate a required evidence-retention policy; the applicable policy must be established outside this engineering guide.

## Trade-off

Purpose-specific retention minimizes unnecessary copies while preserving required records. One indefinite retention setting is easy and accumulates disclosure risk.

## Try This

Draw a data inventory for a single claim description and specify revocation, retention, deletion, and verification owners for every copy.

# Is an append-only audit table automatically tamper-proof and complete?

## Answer

No. Append-only is an application behavior unless database privileges and external retention enforce it. Completeness depends on what is recorded and what happens when recording fails. Trace data and business audit records also have different reliability requirements.

## Why

Give required audit events transactional or explicitly durable delivery semantics. Append-only application behavior does not prevent privileged database changes, and a failed transaction needs rollback or a savepoint.

## Risk

A missing trail can matter during an investigation. Also, swallowing a failed SQL statement does not by itself restore a PostgreSQL transaction; savepoint and rollback behavior require testing.

## Trade-off

Best-effort audit favors availability. Mandatory audit or a transactional audit outbox provides stronger completeness at the cost of possible business-operation failure or more infrastructure.

## Try This

Inject an audit insertion failure and inspect the surrounding transaction. Define which actions must fail closed if audit cannot be guaranteed.

# How should backup and point-in-time recovery be tested for an AI application?

## Answer

Restore the relational database and verify business records, ownership, migrations, outbox state, and knowledge versions. Then decide whether vector projections should be restored or rebuilt. The recovery objective concerns a coherent application state, not only a successful backup command.

## Why

Restore a known fixture into an isolated environment and verify authoritative records, outbox work, derived indexes, credentials, and access policy. Measure recovery time and actual recoverable data loss.

## Risk

Replaying old notification or submission jobs can duplicate effects. A backup also contains private data and requires its own encryption, access, and retention policy.

## Trade-off

Rebuilding vectors reduces backup coupling and takes time and provider cost. Snapshotting every projection can accelerate recovery while making consistency coordination harder.

## Try This

Write a restore drill with a known claim, pending job, rule revision, and revoked user. Verify exact reads, search visibility, and safe job resumption.

# Why separate operational metrics from database content exports?

## Answer

Counts, durations, and sanitized error categories support capacity and health without automatically exporting claim text, customer identifiers, or confirmation tokens. Content exports need an explicit purpose and access policy rather than being a side effect of debugging.

## Why

Export allowlisted operational metadata instead of whole records. Separate observability access from business-data access and review whether identifiers themselves reveal sensitive relationships.

## Risk

A credential-safe SQL logger can still expose PII through parameter values. Traces may be readable by a broader audience than the application database.

## Trade-off

Minimal telemetry reduces diagnosis detail; controlled replay fixtures and opt-in redacted samples can provide useful debugging with less disclosure.

## Try This

Trace one claim description and token through logs, tool spans, model callbacks, and telemetry endpoints. Record exactly what leaves the process.

# How should database security be verified before adding agent autonomy?

## Answer

Prove owner filtering, least-privilege credentials, constrained tools, input validation, timeout behavior, audit policy, and recovery using the actual storage setup. A more autonomous planner increases the number and variety of operations, so it should inherit a secure capability surface rather than broadening it.

## Why

Test with the real application role and cross-tenant fixtures. Exercise denied reads and writes, pooled reuse, arbitrary-input rejection, backup access, and every non-agent administrative path.

## Risk

A framework demo may call internal functions directly and skip route dependencies. The same tool needs an identity context or service principal appropriate to its execution path.

## Trade-off

A capability-oriented service layer takes design work and supports safe reuse across orchestration frameworks. Direct ORM access inside every agent is fast to prototype and hard to govern.

## Try This

Build a deny-first test matrix for interactive users, background workers, and remote agents. Include actions each principal may read, prepare, confirm, or never perform.

# What can PostgreSQL row-level security fail to protect if connection roles are chosen incorrectly?

<!-- meta
domain: ai-rag
subdomain: database-security
module: database-security
concept: What can PostgreSQL row-level security fail to protect if connection roles are chosen incorrectly?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: The application always connects as the table owner and assumes its row policy is restricting every read.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Row policies operate within database role and session semantics. Owners or privileged roles may bypass ordinary policies unless configured appropriately; pooled connections can also retain stale caller context. Use the intended restricted role, bind and reset caller context safely, and test actual application queries with two identities rather than inspecting policy text alone.

Concrete engineering case: The application always connects as the table owner and assumes its row policy is restricting every read.

Boundary defense: Only under a deliberately verified authorization design. Defense in depth and correct role/session behavior still need tests, especially across pools and background workers.

## Spoken Summary

Row policies operate within database role and session semantics. Owners or privileged roles may bypass ordinary policies unless configured appropriately; pooled connections can also retain stale caller context. Use the intended restricted role, bind and reset caller context safely, and test actual application queries with two identities rather than inspecting policy text alone.

## Why

Row policies operate within database role and session semantics. Owners or privileged roles may bypass ordinary policies unless configured appropriately; pooled connections can also retain stale caller context. Use the intended restricted role, bind and reset caller context safely, and test actual application queries with two identities rather than inspecting policy text alone.

## Production Case

The application always connects as the table owner and assumes its row policy is restricting every read.

## Risk

The application always connects as the table owner and assumes its row policy is restricting every read.

## Trade-off

Only under a deliberately verified authorization design. Defense in depth and correct role/session behavior still need tests, especially across pools and background workers.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: database security**: Row policies operate within database role and session semantics.

## Alternatives

- Only under a deliberately verified authorization design. Defense in depth and correct role/session behavior still need tests, especially across pools and background workers.

## Pitfalls

- The application always connects as the table owner and assumes its row policy is restricting every read.

## Follow-ups

### Can application filters be removed after enabling RLS?

Only under a deliberately verified authorization design. Defense in depth and correct role/session behavior still need tests, especially across pools and background workers.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "The application always connects as the table owner and assumes its row policy is restricting every read.",
  "required_decision": "Row policies operate within database role and session semantics"
}
```

## Citations

- https://www.postgresql.org/docs/current/ddl-rowsecurity.html

# How can connection pooling undermine session-based tenant isolation?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: database-security
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A pool reuses physical database connections among logical requests. Session settings can therefore outlive the request that created them unless reset or scoped correctly. A tenant filter or row-level policy depending on such state must use a trustworthy assignment and lifecycle contract, including errors and rollback. Keep migration/administrative roles separate from application roles that should be constrained. Test reuse of the same connection across two principals rather than assuming a fresh connection for every operation.

## Why

Request A sets a tenant session value and fails before cleanup. Request B reuses that connection and must not inherit A's tenant visibility. Transaction-scoped assignment and verified reset behavior can constrain this boundary.

## Worked Case

Request A sets a tenant session value and fails before cleanup. Request B reuses that connection and must not inherit A's tenant visibility. Transaction-scoped assignment and verified reset behavior can constrain this boundary.

## Risk

Superuser or owner privileges can bypass protections expected from ordinary application queries.

## Trade-off

Pooling saves setup cost while making connection-state ownership an explicit requirement.

## Try This

Force one pooled connection through success, rollback and two different tenant requests.

## Citations

- https://www.postgresql.org/docs/current/ddl-rowsecurity.html
