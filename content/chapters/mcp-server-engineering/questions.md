<!-- chapter: mcp-server-engineering -->

# How should an MCP server be layered?

<!-- meta
domain: agents
subdomain: mcp
module: mcp-server-engineering
concept: How should an MCP server be layered
difficulty: implementation
misconception_target: MCP servers pass parameters through without validation
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Keep transport handling, tool schemas, application services, and persistence adapters separate. The MCP handler should translate requests rather than embed the entire business workflow.

## Spoken Summary

Keep transport/protocol adaptation separate from schema validation, identity policy and domain operations. Return actionable structured failures without leaking internals. Bind required approval to material operation parameters and enforce authorization/state checks again at execution.

## Why

Inject a service with a narrow interface and derive the principal from request authentication. Reuse the same application service from HTTP and MCP adapters.

## Production Case

A tool request has valid JSON but names another customer’s order. The server rejects object access before executing the domain action, without disclosing the order’s private state.

## Risk

Duplicated business logic can enforce different permissions through different protocols.

## Trade-off

Layering adds interfaces while keeping behavior consistent.

## Try This

Implement one search service behind both an HTTP route and an MCP tool.

## Execution Timeline

Tool invocation received -> Validate parameters -> Check authorization -> Human confirmation if destructive -> Execute -> Return result or structured error

## Complexity

Validation depends on payload size/schema structure; transport, authentication, authorization and domain effects add separate latency and state costs. Bound request sizes and execution deadlines.

## Definitions

- **Input validation**: Checking tool parameters against a schema before execution
- **Human confirmation**: Explicit approval required before destructive operations
- **Structured error**: Error response that helps the agent recover

## Alternatives

- No validation (unsafe)
- Client-side validation only

## Pitfalls

- Missing parameter validation
- No authorization check
- Raw exception exposure

## Follow-ups

### Should every write require a human click?

Choose approval based on explicit risk and product policy. Regardless of approval, writes still need scope checks, stable identity and recovery semantics.

## Example

> Explanation: Validate, authorize, confirm, then execute.
> Output: Tool result or structured error

```python
async def handle_delete(tool_call):
    schema.validate(tool_call.arguments)
    if not await check_auth(tool_call):
        return error(403)
    if tool_call.destructive:
        return await request_human_approval(tool_call)
    return await execute(tool_call)
```

## Citations

- https://modelcontextprotocol.io/

# How do you create a minimal Python MCP tool?

## Answer

Use a supported official SDK interface, define a typed function, and expose it through a server with an explicitly selected transport. Keep the first example read-only.

## Why

The accompanying SDK example uses the v1 FastMCP style and synthetic data. Pin a compatible v1 SDK; evaluate migration separately for another major version.

## Risk

A minimal decorator example omits production authentication, quotas, and shutdown handling.

## Trade-off

SDK convenience reduces boilerplate and introduces version coupling.

## Try This

Run the example locally with a compatible client and inspect the advertised schema.

# How should tool argument validation work?

## Answer

Validate shape, length, allowed identifiers, numeric bounds, and application invariants before contacting downstream services. Derive tenant and user scope outside model arguments.

## Why

Reject arbitrary SQL, paths, or URLs unless the capability is explicitly designed and constrained for them. Use allowlisted operations and parameter binding.

## Risk

A well-typed string can still contain a dangerous destination or a cross-tenant identifier.

## Trade-off

Narrow inputs reduce flexibility and improve control.

## Try This

Try oversized queries, unexpected properties, and unauthorized resource IDs.

# How do you secure a remote MCP deployment?

<!-- meta
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**MCP is not an authorization system by itself.** A remote Model Context Protocol server exposes tools, resources and prompts over its negotiated transport/protocol revision. A *host* controls a client instance and decides whether discovered tools are available to the assistant. A server must still authenticate and authorize every remote request at its own data boundary. A model choosing a tool, or a schema validating JSON arguments, does not confer permission to run that tool.

**Remote OAuth sequence.** Discover the appropriate protected-resource metadata and authorization server; register/use a permitted client and correct OAuth flow (including PKCE for public authorization-code clients). Obtain a token intended for the target resource with narrowly scoped delegation. At the resource server, cryptographically verify token format/signature and trusted issuer/key metadata, then validate audience/resource, subject, expiry, intended scopes and tool/object authorization. Handle redirect URI and state against CSRF; never send a bearer token issued for Server A to an unrelated Server B. Re-check ownership of each document and deny writes until a separate approval/policy gate permits them.

**Version and discovery.** Initialization/capability negotiation, tool lists, transport errors and versioned input schemas are separate from application authority. A client supporting two MCP specification versions should select an intersection, not assume the newest protocol from a marketing page. Remote HTTP has different origin, session, timeout and cancellation risks from local STDIO; the tool result remains untrusted content, even from a properly authenticated server.

**Execution example.** `labs/mcp_remote_policy.py` uses already-verified synthetic identities (it does NOT parse or cryptographically verify JWTs) and checks issuer, audience, expiry, scopes, declared tools, effect approval and replay identity. It rejects cross-resource bearer token forwarding, read-only-to-write escalation and unsupported versions. The effect-ID set is process-local teaching state, not a durable cross-replica idempotency ledger. Real OAuth integration must use a cryptographic library, a live issuer, discovery, consent, token exchange and negative redirect/PKCE tests.

**Production failure.** A user authorizes an innocuous document-search tool. A compromised server description then asks the client to submit a payment and forward its token. Descriptions are lower-trust data; the host rejects tool/policy escalation, the wrong-audience token is unusable by the second server, and effectful operations require authenticated owner plus explicit approval and durable idempotent business handling.

**Trade-off and follow-up.** Stateless HTTP simplifies horizontal scaling but requires an explicit continuation/effect ledger for long-running tasks; session transports add lifetime/cleanup complexity. **What changes when the HTTP result is lost after commit?** Replay using a stable owner-scoped operation ID and consult the durable effect store; a transport retry alone cannot guarantee exactly-once side effects.

## Why

Follow the selected protocol security guidance and deploy behind an explicit ingress policy. Log security outcomes without storing credentials.

## Risk

A reverse proxy does not automatically validate application-level permissions or block server-side request forgery.

## Trade-off

More controls add operational work and reduce exposure.

## Try This

Run MCP remote policy tests; change audience, scope, expiry and approval to confirm rejection; distinguish verified-claims policy from actual signature verification.

## Follow-ups

### Can a tool's advertised JSON input schema prove that an MCP client is authorized to invoke it?

No. JSON validation checks arguments, while authentication establishes a principal and authorization checks the exact resource and action. Validate issuer, signature, audience, expiration, scope, per-object policy and separate user approval before irreversible effects; remote tool descriptions cannot grant privileges.

## Citations

- https://modelcontextprotocol.io/specification/2026-07-28

# How should tool errors be modeled?

## Answer

Separate transport or protocol failures from expected application outcomes such as not found, permission denied, unavailable, and needs confirmation. Return stable machine-readable categories.

## Why

Map internal exceptions to a controlled envelope and preserve a trace or operation ID for support. Do not expose stack traces or query strings containing private data.

## Risk

Returning an empty list for every failure causes an agent to misreport outages as no matches.

## Trade-off

Typed outcomes require client handling and support reliable decisions.

## Try This

Simulate one normal empty result and one timeout and compare agent behavior.

# How should write tools require human confirmation?

## Answer

Preparation should produce a reviewable operation with exact parameters, owner, expiry, and revision. Execution should validate an approval bound to that operation.

## Why

Keep approval verification and the business transaction server-side. A natural-language yes or model-provided approved flag is insufficient.

## Risk

Reusing approval after parameters change can authorize a different action.

## Trade-off

Two-step operations add interaction and reduce accidental changes.

## Try This

Change the amount after approval and verify execution rejects the stale approval.

# How do you control concurrency and retries for tools?

## Answer

Apply per-tenant quotas, bounded execution concurrency, downstream deadlines, and an idempotency policy for side effects. Retries must depend on outcome and operation semantics.

## Why

Keep the same durable operation key across retry attempts, and query status after an ambiguous failure. Avoid holding database locks during remote model calls.

## Risk

Retrying a timeout can repeat a committed write.

## Trade-off

Conservative retry limits may surface more transient failures while protecting correctness.

## Try This

Inject a timeout immediately after commit and recover through the operation ledger.

# What should MCP observability record?

## Answer

Record tool name, schema version, permitted principal category, latency, outcome, retry count, and trace linkage. Store arguments only under a reviewed privacy policy.

## Why

Use an allowlist of safe attributes and attach task or operation IDs across adapters. Separate user-visible outcomes from instrumentation success.

## Risk

A tool returning a domain failure may still look like a successful function call.

## Trade-off

Detailed payload logging improves diagnosis and increases disclosure risk.

## Try This

Show metrics that distinguish validation rejection, denied access, empty search, and provider outage.

# How should MCP contract tests be organized?

## Answer

Test schema discovery, normal execution, denied access, malformed inputs, cancellation, timeouts, and client-version compatibility. Add backend invariants separately.

## Why

Use synthetic data and a sandbox service. Assert what actions occurred, not only what text the agent returned.

## Risk

Mock-only tests cannot establish behavior of real transport framing or token validation.

## Trade-off

End-to-end tests cost more and catch boundary failures unit tests miss.

## Try This

Publish a small compatibility matrix for the clients and protocol revisions you actually ran.

# How should tool changes be released?

## Answer

Treat schema, semantic, permission, and outcome changes as API changes. Version incompatible contracts and evaluate tool selection after description edits.

## Why

Pin the deployed artifact, announce deprecations, retain rollback, and compare tool trajectories before expanding traffic.

## Risk

Renaming a field can break stored plans or cached tool metadata.

## Trade-off

Backward compatibility costs maintenance and prevents abrupt client failure.

## Try This

Design a migration from one search field to a structured query without silently changing behavior.

# How do standard I/O and HTTP Server-Sent Events transports differ in Model Context Protocol server engineering, and when is each appropriate?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: mcp-server-engineering
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**The Model Context Protocol (MCP) defines a client-server architecture communicating via JSON-RPC 2.0 messages over two standardized transports: standard I/O (stdio) and HTTP with Server-Sent Events (SSE).** Choosing between them dictates the process lifecycle, security boundary, network latency, and deployment model of the integration.

**Standard I/O (stdio) transport: local process execution.** In stdio transport, the host client (e.g., Claude Desktop or an AI IDE) directly spawns the MCP server as a local child process, communicating over standard input and output streams (`stdin` and `stdout`). Key characteristics: (1) Zero network overhead: message transmission is pure inter-process communication (IPC) via pipe buffers; (2) Tightly coupled process lifecycle: the server starts and dies with the host client session; and (3) Local security perimeter: the server operates within the user's local machine environment, accessing local files and environment variables. Ideal for developer desktop tools, local database inspectors, and command-line execution.

**HTTP with Server-Sent Events (SSE) transport: distributed remote services.** In SSE transport, the MCP server runs as an independent, persistent remote web service (e.g., built on FastAPI or Starlette). The client opens an HTTP GET connection to `/sse` to receive real-time streaming JSON-RPC server events, and sends client requests via HTTP POST to `/messages`. Key characteristics: (1) Decoupled remote lifecycle: the server runs in Kubernetes or cloud containers, scaling independently; (2) Multi-tenant enterprise access: serves multiple concurrent agent sessions over TLS; and (3) Hard network perimeter: requires mutual TLS, API keys, or OAuth 2.0 authentication, and network firewalls. Ideal for centralized enterprise knowledge stores, shared microservice tools, and multi-tenant cloud agent systems.

## Why

An enterprise wants all developer AI tools to query an internal security database. Using stdio requires distributing database credentials to every employee machine. Deploying an MCP server over SSE centralizes authentication, auditing, and credential management behind an authenticated gateway.

## Worked Case

An enterprise wants all developer AI tools to query an internal security database. Using stdio requires distributing database credentials to every employee machine. Deploying an MCP server over SSE centralizes authentication, auditing, and credential management behind an authenticated gateway.

## Risk

Deploying an MCP server over SSE without authentication exposes internal tool execution capabilities to unauthorized network exploitation.

## Trade-off

Stdio provides zero-latency local setup with zero network configuration; SSE requires running and securing persistent cloud web infrastructure, but enables centralized multi-tenant tool sharing.

## Try This

Build a minimal MCP server in Python with FastMCP. Run it locally via stdio, and reconfigure it to serve over SSE on localhost:8000. Inspect the SSE stream with curl.

## Follow-ups

### Why must stdout be kept strictly clean of debug prints in an stdio MCP server?

In stdio mode, stdout is the dedicated JSON-RPC message channel; any stray print() statement emits non-JSON text that breaks the client's JSON parser, crashing the connection.

## Citations

- https://modelcontextprotocol.io/docs/concepts/transports
- https://spec.modelcontextprotocol.io/specification/basic/transports/

# How should MCP servers handle high-concurrency tool execution, backpressure, and asynchronous cancellation signals?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: mcp-server-engineering
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Production MCP servers must manage concurrent asynchronous tasks, apply rate-limiting backpressure, and honor JSON-RPC cancellation notifications.** When an autonomous agent coordinates complex workflows, it can issue multiple parallel tool invocations simultaneously (e.g., analyzing 20 source code files or querying multiple databases concurrently). Without robust concurrency governance, worker memory exhausts and event loops block.

**Asynchronous concurrency control with asyncio semaphores.** An MCP server implemented in Python (using FastMCP or the official MCP Python SDK) must decouple transport receiving from tool execution using an asynchronous worker pool. A global or per-session semaphore (`asyncio.Semaphore(max_concurrency)`) bounds simultaneous tool runs. When incoming request rates exceed capacity, the server returns structured JSON-RPC error codes (`-32000 Server overloaded`) with `Retry-After` headers rather than buffering unbounded tasks in memory.

**Handling notifications/cancelled signals.** The Model Context Protocol specification supports cancellation: if an agent times out or the end-user halts generation, the client transmits a `notifications/cancelled` JSON-RPC message containing the `requestId`. A production MCP server must track active `asyncio.Task` instances in an in-memory dictionary. Upon receiving the cancellation notification, the server calls `task.cancel()`, properly cleaning up open database transactions, terminating child subprocesses, and releasing semaphore slots. Ignoring cancellation causes orphaned background tasks to consume CPU and database connections long after the user has abandoned the request.

## Why

A user cancels a slow codebase search. Without cancellation handling, the MCP server continues running ripgrep across 100,000 files for 45 seconds, blocking the next user request and consuming 100% CPU.

## Worked Case

A user cancels a slow codebase search. Without cancellation handling, the MCP server continues running ripgrep across 100,000 files for 45 seconds, blocking the next user request and consuming 100% CPU.

## Risk

Failing to handle task cancellation leaves zombie subprocesses and leaked database locks running in the background after client disconnects.

## Trade-off

Tracking task futures and implementing cancellation hooks adds state management complexity, but prevents severe server resource exhaustion under high concurrency.

## Try This

Implement an MCP tool that sleeps for 10 seconds. Issue a cancellation notification from the client after 2 seconds, and verify that the server cancels the underlying asyncio task immediately.

## Follow-ups

### Can an MCP tool return streaming progress updates while executing?

Yes. MCP supports notifications/progress messages, allowing a long-running tool to emit percentage completion updates back to the client before returning the final result.

## Citations

- https://spec.modelcontextprotocol.io/specification/basic/utilities/cancellation/
- https://docs.python.org/3/library/asyncio-task.html

# How do MCP Resources, Tools, and Prompts differ in protocol lifecycle and security boundaries?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: mcp-server-engineering
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**The Model Context Protocol organizes data and capabilities into three core architectural primitives—Resources, Tools, and Prompts—each with distinct lifecycles, user-interaction patterns, and security guarantees.** Conflating these primitives creates poor agent UX and dangerous security boundaries.

**1. Resources (Passive, Read-Only Context).** Resources represent readable data and documents exposed by the server under standardized URI schemes (e.g., `postgres://db/schema` or `file:///logs/app.log`). Resources are passive: reading a resource has zero side effects. Clients can subscribe to resource updates (`resources/subscribe`), allowing the server to push real-time cache invalidations when data changes. Security boundary: strictly read-only; exposed to model context as reference data.

**2. Tools (Active, Executable Capabilities).** Tools are executable functions (e.g., `execute_sql`, `send_email`, `fetch_metrics`) invoked with model-generated arguments. Tools have active operational consequences and can mutate external system state. Security boundary: Tools require strict JSON Schema validation, capability checks, and explicit client-side approval (human-in-the-loop authorization) before execution.

**3. Prompts (Reusable Interactive Templates).** Prompts are server-defined prompt templates and conversational workflows with parameterized arguments (e.g., `git_commit_review(branch: str)`). They allow servers to supply standardized system instructions and few-shot examples directly to client UIs, guiding model behavior without embedding instructions in client application code.

## Why

An engineer exposes a database query as a Tool when it should be a Resource. The model invokes the tool multiple times during planning, causing unnecessary round trips. Exposing the schema as a static Resource allows the client to inject it directly into context upfront.

## Worked Case

An engineer exposes a database query as a Tool when it should be a Resource. The model invokes the tool multiple times during planning, causing unnecessary round trips. Exposing the schema as a static Resource allows the client to inject it directly into context upfront.

## Risk

Treating a state-mutating operation as a Resource bypasses user-approval safety gates, allowing models to alter data during passive context gathering.

## Trade-off

Structuring capabilities cleanly across Resources, Tools, and Prompts requires deeper protocol design upfront, but creates modular, secure, and highly predictable agent integrations.

## Try This

Author an MCP server exposing one Resource (`file://config.json`), one Tool (`update_setting`), and one Prompt (`review_config`). Verify how each appears in client capabilities discovery.

## Follow-ups

### Can an MCP resource return binary data like images or PDFs?

Yes. Resource contents can be serialized as UTF-8 text or Base64-encoded binary blobs with explicit MIME types.

## Citations

- https://modelcontextprotocol.io/docs/concepts/resources
- https://modelcontextprotocol.io/docs/concepts/tools

# How do you build production sandboxing for MCP servers executing code or shell commands to prevent container breakout?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: mcp-server-engineering
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**MCP servers that execute shell commands or user/agent-generated code (such as Python or Bash interpreters) represent critical remote code execution (RCE) vectors requiring multi-layered kernel and container sandboxing.** In autonomous agent environments, an agent can be persuaded via prompt injection to run destructive commands (`rm -rf /`, downloading cryptominers, or scanning the internal cloud VPC).

**Defense-in-depth sandboxing architecture.** Relying on basic Python `subprocess.run()` or Docker alone is insufficient because standard Docker containers share the host Linux kernel and are vulnerable to container breakout exploits. A production sandboxing architecture enforces four strict isolation tiers: (1) Kernel Isolation via MicroVMs: Execute code inside microVMs (such as AWS Firecracker, gVisor, or Kata Containers) that implement an isolated guest kernel, preventing host kernel privilege escalation; (2) Linux Namespace & cgroup Restrictions: Bind execution to ephemeral namespaces with non-root UID/GID, drop all Linux capabilities (`cap_drop: ["ALL"]`), and enforce hard cgroup limits on CPU time, RAM (e.g. max 512MB), and disk I/O; (3) Ephemeral Read-Only Root Filesystem: Mount the root filesystem as read-only, providing only an in-memory `tmpfs` volume for scratch files that is destroyed immediately upon process exit; and (4) Strict Network Egress Filtering: Deny all outbound internet and local network access (`--network none`) except to explicitly whitelisted API endpoints, completely neutralizing data exfiltration and SSRF attacks.

## Why

An agent executes a Python snippet containing a kernel exploit. In a standard Docker container, the exploit escalates to host root and compromises other customer containers. In a gVisor/Firecracker microVM sandbox, the exploit fails because the intercepted syscall is isolated to an unprivileged user-space virtual kernel.

## Worked Case

An agent executes a Python snippet containing a kernel exploit. In a standard Docker container, the exploit escalates to host root and compromises other customer containers. In a gVisor/Firecracker microVM sandbox, the exploit fails because the intercepted syscall is isolated to an unprivileged user-space virtual kernel.

## Risk

Executing un-sandboxed shell tools in an MCP server gives prompt injection payloads immediate arbitrary remote execution authority on your infrastructure.

## Trade-off

MicroVM sandboxing introduces a tiny startup latency overhead (5–20ms per execution), but provides indispensable protection against catastrophic host compromise.

## Try This

Configure an unprivileged gVisor `runsc` runtime in Docker. Attempt to read `/proc` or access host network interfaces from inside the container, confirming that access is strictly denied.

## Follow-ups

### Why is running code as an unprivileged user inside Docker not enough?

If a Linux kernel vulnerability (like Dirty COW) exists, an unprivileged user inside a standard container can exploit shared host kernel memory to gain root access on the physical host.

## Citations

- https://gvisor.dev/docs/architecture_guide/
- https://firecracker-microvm.github.io/

# How should an MCP write tool defend against a forged target and a repeated effect?

<!-- meta
domain: agents
subdomain: mcp-server-engineering
module: mcp-server-engineering
concept: How should an MCP write tool defend against a forged target and a repeated effect?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A model changes the owner field in an otherwise valid tool call and retries it after a lost acknowledgment.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Validate structured arguments, authenticate the caller through the transport’s contract and authorize the specific target at the service boundary. Bind approval, payload and owner to a durable operation identity and use a receiver-safe retry policy. Tool annotations and a descriptive name are not permission enforcement.

Concrete engineering case: A model changes the owner field in an otherwise valid tool call and retries it after a lost acknowledgment.

Boundary defense: No. Approval authority must come from a trusted interaction or policy record, bound to the intended action and protected from arbitrary model input.

## Spoken Summary

Validate structured arguments, authenticate the caller through the transport’s contract and authorize the specific target at the service boundary. Bind approval, payload and owner to a durable operation identity and use a receiver-safe retry policy. Tool annotations and a descriptive name are not permission enforcement.

## Why

Validate structured arguments, authenticate the caller through the transport’s contract and authorize the specific target at the service boundary. Bind approval, payload and owner to a durable operation identity and use a receiver-safe retry policy. Tool annotations and a descriptive name are not permission enforcement.

## Production Case

A model changes the owner field in an otherwise valid tool call and retries it after a lost acknowledgment.

## Risk

A model changes the owner field in an otherwise valid tool call and retries it after a lost acknowledgment.

## Trade-off

No. Approval authority must come from a trusted interaction or policy record, bound to the intended action and protected from arbitrary model input.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: mcp server engineering**: Validate structured arguments, authenticate the caller through the transport’s contract and authorize the specific target at the service boundary.

## Alternatives

- No. Approval authority must come from a trusted interaction or policy record, bound to the intended action and protected from arbitrary model input.

## Pitfalls

- A model changes the owner field in an otherwise valid tool call and retries it after a lost acknowledgment.

## Follow-ups

### Is a boolean approved argument supplied by the model adequate approval evidence?

No. Approval authority must come from a trusted interaction or policy record, bound to the intended action and protected from arbitrary model input.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A model changes the owner field in an otherwise valid tool call and retries it after a lost acknowledgment.",
  "required_decision": "Validate structured arguments, authenticate the caller through the transport’s contract and authorize the specific target at the service boundary"
}
```

## Citations

- https://github.com/modelcontextprotocol/python-sdk
- https://modelcontextprotocol.io/specification/2026-07-28/server/tools
- https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization
- https://py.sdk.modelcontextprotocol.io/get-started/first-steps/

# How do confused-deputy risks and token audience checks affect a remote MCP server?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: mcp-server-engineering
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A server that can call powerful downstream services must not let an untrusted caller borrow those privileges merely by proposing tool arguments. Validate the caller's identity, requested resource, token audience and action permissions at the correct boundary. Follow the protocol profile's authorization requirements and do not pass arbitrary inbound tokens through to unrelated services. Sessions are transport/application state, not substitutes for authorization. Audit safe identifiers and decisions without exposing bearer credentials or private argument payloads.

## Why

A caller supplies a token intended for service A and asks an MCP server to use its privileged connection to service B. The server must enforce the intended audience and delegated scope rather than treat any valid-looking token as universal authority.

## Worked Case

A caller supplies a token intended for service A and asks an MCP server to use its privileged connection to service B. The server must enforce the intended audience and delegated scope rather than treat any valid-looking token as universal authority.

## Risk

Shared backend credentials can turn a narrow tool into a privilege-escalation path.

## Trade-off

Remote interoperability needs explicit identity and resource boundaries beyond local tool schemas.

## Try This

Test wrong audience, missing scope and access to another principal's resource.

## Citations

- https://github.com/modelcontextprotocol/python-sdk
- https://modelcontextprotocol.io/specification/2026-07-28/server/tools
- https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization
- https://py.sdk.modelcontextprotocol.io/get-started/first-steps/
