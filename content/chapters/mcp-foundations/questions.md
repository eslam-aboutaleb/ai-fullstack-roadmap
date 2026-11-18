<!-- chapter: mcp-foundations -->

# What is MCP and which problem does it solve?

<!-- meta
answer_format: conceptual
domain: agent-systems
subdomain: mcp-foundations
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**MCP separates the host application, its client connections and capability servers.** The host owns the user experience, model interaction and policy decisions. A client implements a connection to a server; a server exposes supported primitives such as tools and resources. MCP is a protocol for context/capability exchange, not an agent planner, a complete identity system or a guarantee that a tool is safe.

Negotiate a supported wire profile and discover capabilities before relying on them. Tool listing exposes names, descriptions and argument schemas; tool execution returns structured/content results or errors. Keep protocol/transport errors distinct from application-level tool failures. Version-pinned SDKs reduce ambiguity, but a package version is not proof that two peers negotiated the same protocol profile.

STDIO connects a local child process through streams; keep diagnostics off its protocol stdout and control the executable/environment. Streamable HTTP uses a remote HTTP boundary with its own session, origin, authentication and authorization requirements. A process launched locally is not automatically trustworthy, and a remote tool description is not permission to transmit confidential evidence. The broader OAuth interoperability issue adds requirements beyond this introductory course.

`labs/protocol_interop.py` uses actual pinned Python MCP clients over STDIO and loopback HTTP, discovers read_policy, executes a public request and rejects private/malformed requests. It also exercises a separate A2A public agent interaction; A2A task delegation and MCP tool invocation are different contracts. The support project's in-process registry is deliberately not labeled MCP wire execution. Keep those evidence types distinct when designing an adapter. Test peer version, discovery, schema errors, cancellation and denial rather than treating a successful connection as conformance or production authorization.

## Why

A host discovers read_policy over actual STDIO and HTTP, then tries an invalid source ID. Discovery succeeds while execution is denied, demonstrating that advertised capability and allowed resource access are separate decisions.

## Worked Case

A host discovers read_policy over actual STDIO and HTTP, then tries an invalid source ID. Discovery succeeds while execution is denied, demonstrating that advertised capability and allowed resource access are separate decisions.

## Risk

An untrusted local executable can read its inherited environment. Remote transport adds token/resource boundaries; neither transport makes a server safe by itself.

## Trade-off

Local STDIO simplifies deployment for one host but couples process lifecycle. HTTP can support remote peers while adding service identity, network failure and operational complexity.

## Try This

Install requirements-advanced.txt in an isolated environment and run protocol_interop.py. Record negotiated profiles and separate valid execution, tool denial and malformed arguments in the trace.

## Follow-ups

### Does using A2A instead of MCP remove the need for tool authorization?

No. A delegated agent still acts under an explicit identity, data-sharing and effect policy. Task lifecycle interoperability cannot grant access to a document or approve a payment.

## Citations

- https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture
- https://a2a-protocol.org/latest/specification/

# How do tools, resources, and prompts differ?

<!-- meta
domain: agents
subdomain: mcp
module: mcp-foundations
concept: How do tools, resources, and prompts differ
difficulty: foundations
misconception_target: MCP is only for connecting to LLMs
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Tools perform requested operations; resources expose addressable context; prompts expose reusable interaction templates. Their selection and use are coordinated by the host.

## Spoken Summary

Tools expose callable operations with defined schemas. Resources expose addressable context/data, and prompts expose reusable prompt templates/workflows. Their discovery and use differ, but all require appropriate trust and access controls. Tool metadata is not proof that an effect is safe.

## Why

Keep side-effecting business operations in narrowly scoped tools and use resources for read-oriented artifacts with explicit authorization.

## Production Case

A service offers a read-only policy resource, a draft-response prompt and a confirm-refund tool. The write tool needs a separate operation and authorization contract even if the other two are permitted.

## Risk

A resource URI can reveal private data if access checks are omitted.

## Trade-off

Rich capability modeling improves clarity while increasing implementation work.

## Try This

Classify a search function, document URI, and review template using these three concepts.

## Execution Timeline

Client connects -> Server lists capabilities -> Client invokes tool/resource -> Server returns result -> Client uses result

## Complexity

Discovery can require multiple paginated network requests and authorization checks. Schema/context size affects model cost; tool execution has its own bounded resource and effect contract.

## Definitions

- **MCP**: Model Context Protocol: standardized interface for AI-accessible tools and resources
- **Capability discovery**: Client queries server for available tools, resources, prompts
- **Transport**: Communication channel between MCP client and server

## Alternatives

- Custom API integration per tool
- OpenAPI-based tool definitions

## Pitfalls

- Over-exposing sensitive resources
- No authorization boundary
- Transport security gaps

## Follow-ups

### Can a read-only annotation replace backend permissions?

No. Validate actual behavior and scope at the authoritative boundary; metadata supplied by a server is not a security guarantee.

## Example

> Explanation: Discover what the server offers, then invoke a tool.
> Output: Tool result data

```python
capabilities = client.list_capabilities()
result = client.invoke_tool(tool_name, args)
```

## Citations

- https://modelcontextprotocol.io/

# What does capability negotiation mean for an MCP integration?

## Answer

Participants communicate supported features for a protocol revision so each side can use only compatible behavior. An application must handle absent capabilities explicitly.

## Why

Test the actual client and server pair, pin compatible SDK versions, and expose feature-dependent paths only when supported.

## Risk

Assuming a newer feature exists can break an otherwise healthy integration.

## Trade-off

Conservative compatibility reduces features but improves interoperability.

## Try This

Define a fallback when a server cannot provide a feature your UI would prefer.

# How should a tool's input and output contracts be designed?

## Answer

Use precise names, small input schemas, typed outcomes, and stable identifiers. Describe side effects and missing-input behavior clearly enough for both models and humans.

## Why

Validate arguments server-side and return minimal structured data plus a useful explanation. Keep protocol errors distinct from normal business failures.

## Risk

Descriptions and annotations are metadata, not a permission system.

## Trade-off

Rich output helps agents reason while consuming context.

## Try This

Design a search tool that distinguishes zero matches from backend failure.

# How does MCP differ from A2A and REST?

## Answer

REST commonly exposes application resources and operations. MCP standardizes AI-facing capability access. A2A coordinates tasks between agent systems. They can wrap the same backend while serving different contracts.

## Why

Choose the smallest boundary that matches the integration. A deterministic lookup rarely needs a remote agent negotiation layer.

## Risk

Adding protocols can obscure which service owns authorization and durable writes.

## Trade-off

Standardization helps interoperability and adds lifecycle overhead.

## Try This

Explain why your account-balance lookup uses a tool while a specialist investigation may use a remote task.

# Which transport should an MCP server use?

## Answer

Local stdio suits supervised local processes; remote HTTP transport suits network services with explicit identity and deployment controls. Supported details depend on the protocol and SDK versions.

## Why

Choose based on process ownership, trust boundary, network reachability, and operational needs. Implement the lifecycle required by the selected revision.

## Risk

Never expose a local development server broadly merely because it starts successfully.

## Trade-off

Local processes simplify access while remote services enable shared operations and require stronger controls.

## Try This

Compare a developer desktop connector with a shared enterprise document connector.

# Why are remote tool descriptions a trust boundary?

## Answer

A server can supply text that the host places in the model's context. Hostile metadata can try to redirect behavior before any tool is called.

## Why

Approve servers, scope available tools, review metadata changes, and keep secrets outside model-visible descriptions. Backend authorization must still apply on execution.

## Risk

A read-only annotation cannot prove that a remote implementation has no side effects.

## Trade-off

Server review slows onboarding and reduces uncontrolled capability exposure.

## Try This

Create a tool description containing a malicious instruction and verify host policy remains effective.

# How should MCP authorization map to backend identity?

## Answer

Authenticate the request and map permitted scopes to an application principal. The server must authorize the requested resource and operation using trusted identity.

## Why

Validate token issuer, audience, expiry, and required scopes according to the selected authorization profile. Do not pass arbitrary caller tokens through to unrelated services.

## Risk

A valid token for one resource may be invalid for another.

## Trade-off

Fine-grained scopes require lifecycle management and reduce blast radius.

## Try This

Write allow and deny cases for two tenants using the same tool name.

# What should cancellation and timeouts mean?

## Answer

Cancellation stops work where possible and communicates the resulting operation state. It does not reverse an already committed side effect.

## Why

Propagate deadlines, retain operation identifiers, and provide a status lookup for uncertain outcomes. Follow the protocol revision's cancellation behavior.

## Risk

A client disconnect can leave a server operation running.

## Trade-off

Durable status adds storage while supporting safe recovery.

## Try This

Disconnect during a simulated write and determine whether retry would duplicate it.

# What is a good first MCP project?

## Answer

Build a read-only knowledge-search server with synthetic documents, an authenticated service adapter, structured results, and clear empty versus failure outcomes.

## Why

Start with one tool, test compatible clients, and add access-control and injection cases before write tools. Keep provider secrets in server configuration.

## Risk

A toy search demo is not proof of production readiness.

## Trade-off

Narrow scope makes the protocol learnable before distributed security complexity.

## Try This

Deliver a client transcript, authorization matrix, and failure-recovery demonstration.

# How do MCP package versions and negotiated wire profiles differ on STDIO and HTTP?

<!-- meta
domain: agents
subdomain: mcp-foundations
module: mcp-foundations
concept: How do MCP package versions and negotiated wire profiles differ on STDIO and HTTP?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A client silently falls back to an older lifecycle while the application assumes metadata required by a newer profile.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

An SDK release can support several wire profiles or compatibility paths. Record and assert the profile actually used, then check required capabilities. STDIO inherits a local subprocess boundary, while HTTP additionally needs its declared remote authentication and transport policy. Neither discovery nor valid schemas alone authorizes a resource read.

Concrete engineering case: A client silently falls back to an older lifecycle while the application assumes metadata required by a newer profile.

Boundary defense: No. Pin the dependency and execute an actual client/server exchange on the relevant transport, including unsupported-version and denied-input cases.

## Spoken Summary

An SDK release can support several wire profiles or compatibility paths. Record and assert the profile actually used, then check required capabilities. STDIO inherits a local subprocess boundary, while HTTP additionally needs its declared remote authentication and transport policy. Neither discovery nor valid schemas alone authorizes a resource read.

## Why

An SDK release can support several wire profiles or compatibility paths. Record and assert the profile actually used, then check required capabilities. STDIO inherits a local subprocess boundary, while HTTP additionally needs its declared remote authentication and transport policy. Neither discovery nor valid schemas alone authorizes a resource read.

## Production Case

A client silently falls back to an older lifecycle while the application assumes metadata required by a newer profile.

## Risk

A client silently falls back to an older lifecycle while the application assumes metadata required by a newer profile.

## Trade-off

No. Pin the dependency and execute an actual client/server exchange on the relevant transport, including unsupported-version and denied-input cases.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: mcp foundations**: An SDK release can support several wire profiles or compatibility paths.

## Alternatives

- No. Pin the dependency and execute an actual client/server exchange on the relevant transport, including unsupported-version and denied-input cases.

## Pitfalls

- A client silently falls back to an older lifecycle while the application assumes metadata required by a newer profile.

## Follow-ups

### Can you infer current interoperability from a copied SDK snippet?

No. Pin the dependency and execute an actual client/server exchange on the relevant transport, including unsupported-version and denied-input cases.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A client silently falls back to an older lifecycle while the application assumes metadata required by a newer profile.",
  "required_decision": "An SDK release can support several wire profiles or compatibility paths"
}
```

## Citations

- https://modelcontextprotocol.io/specification/2026-07-28/server/tools
- https://github.com/modelcontextprotocol/python-sdk
- https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization

# How do protocol versions, negotiated capabilities and transport choices constrain MCP interoperability?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: mcp-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

MCP interoperability depends on a shared protocol profile, supported capabilities and the chosen transport's lifecycle, not only a successful connection. Negotiate or verify the applicable version and expose unsupported operations clearly. Standard input/output is a local process transport, while remote HTTP introduces network, identity and authorization concerns. Tools, resources and prompts retain distinct semantics. A public read-only demonstration establishes a smaller contract than authenticated remote tool access, so state the tested profile and avoid inferring security properties from a client library name.

## Why

A client can connect and list tools while not supporting an extension needed by one operation. Treat the operation as unsupported or adapt it deliberately instead of sending a request the peer cannot interpret safely.

## Worked Case

A client can connect and list tools while not supporting an extension needed by one operation. Treat the operation as unsupported or adapt it deliberately instead of sending a request the peer cannot interpret safely.

## Risk

Transport connectivity can be mistaken for complete protocol conformance.

## Trade-off

Pin and test representative profiles while planning compatible version evolution.

## Try This

Test one negotiated capability and one explicitly unsupported operation across two transports.

## Citations

- https://modelcontextprotocol.io/specification/2026-07-28/server/tools
- https://github.com/modelcontextprotocol/python-sdk
- https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization
