<!-- chapter: application-architecture -->

# What does a full support application add beyond a retrieval subsystem?

## Answer

A complete application adds authenticated APIs, customer-owned service requests, versioned knowledge, an agent runtime, confirmation workflows, persistent conversation history, background jobs, evaluation, and observability. Retrieval remains one service within that product.

## Why

Bind authenticated APIs, domain repositories, retrieval, model execution, and a client through typed contracts. Each layer should expose failures without pretending another layer has completed its work.

## Risk

Do not infer that every newer the retrieval service feature is integrated. The knowledge tool concatenates retrieved context directly; it does not automatically use the library's full an evidence assembler and revision-lookup contract.

## Trade-off

A narrow host binding is easier to ship, while richer evidence contracts add explicit statuses and provenance. Adoption requires wiring and migration rather than only upgrading a dependency.

## Try This

Trace a question from the browser through authentication, tool selection, scoped retrieval, evidence assembly, generation, and source opening.

# How should the orchestration framework be distinguished from model and retrieval adapters?

<!-- meta
domain: system-design
subdomain: api-lifecycle
concept: How should the orchestration framework be distinguished from model and retrieval adapters
difficulty: foundations
misconception_target: Confusing orchestration, evidence, eligibility and committed operation state
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

The orchestration runtime controls the agent loop. A model adapter normalizes provider access, a retrieval service supplies evidence, and a tracing backend records execution. A product may use ADK, LangChain, or another runtime without changing these responsibilities.

## Spoken Summary

The orchestration layer owns workflow state, budgets, policy and ordering. A model adapter translates provider contracts; a retrieval adapter exposes scoped evidence candidates. Keep business invariants in authoritative services so replacing the model or orchestration framework cannot bypass them.

## Why

Draw separate boxes for the runtime, model adapter, retrieval service, business services, and telemetry. Evaluate a replacement at its contract boundary rather than inferring responsibilities from package names.

## Production Case

Replacing a model provider changes response and retry formats. Adapter contract tests should catch the change while the same task state machine and authorization service remain responsible for effects.

## Risk

Framework confusion leads to examples that cannot run against the reference design's dependencies. The later LangChain, LangGraph, and A2A chapters explicitly describe alternatives or additions rather than pretending those frameworks are already installed.

## Trade-off

Staying with one orchestrator reduces state-model overlap. Adding another can solve a measured workflow need but introduces serialization, tracing, error, and deployment boundaries.

## Try This

Make a dependency-layer table with web framework, agent runtime, model adapter, retrieval library, persistence layer, and tracing service. Name their concrete constructors.

## Execution Timeline

Validated task -> scoped retrieval -> model proposal -> domain validation -> authorized effect -> durable result

## Complexity

Workflow cost depends on the selected model, retrieval and tool operations; interface separation adds a testable boundary rather than a universal speed improvement.

## Definitions

- **Orchestrator**: Owns workflow transitions, budgets and ordering around adapters.
- **Model adapter**: Translates a provider interface into the application-owned model contract.
- **Retrieval adapter**: Returns scoped versioned evidence through a defined retrieval contract.

## Alternatives

- GraphQL for flexible queries
- WebSocket for bidirectional streaming

## Pitfalls

- Blank input reaches business layer
- Malformed JSON crashes handler
- Authentication bypassed

## Follow-ups

### What should an adapter avoid owning?

Global workflow authority or hidden business writes. Its contract should expose results and failures for the caller to handle explicitly.

## Example

> Explanation: The deterministic decision owns ordering; an adapter call does not grant business authority.
> Output: validate_proposal

```python
def choose_next(state):
    if not state['has_evidence']:
        return 'retrieve'
    if not state['proposal_valid']:
        return 'validate_proposal'
    return 'domain_authorization'

print(choose_next({'has_evidence': True, 'proposal_valid': False}))
```

## Citations

- https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph
- https://docs.langchain.com/oss/python/langchain/models
- https://docs.langchain.com/oss/python/langchain/tools

# How does an eligibility question differ from a request-status question?

<!-- meta
domain: system-design
subdomain: javascript-typescript
module: application-architecture
concept: How does an eligibility question differ from a request-status question
difficulty: foundations
misconception_target: Confusing orchestration, evidence, eligibility and committed operation state
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Coverage requires retrieving knowledge rules and applying a reviewed procedure to the user's facts. Claim status is a lookup of structured application state under the authenticated owner's scope. An answer about a policy is evidence-based interpretation; an answer about an existing request must reflect the actual recorded claim.

## Spoken Summary

An eligibility question asks what current evidence and business rules permit. A request-status question asks what a durable operation has actually reached. Use applicable policies for eligibility and authoritative operational state for status; generated text or retrieved prose cannot prove a request committed.

## Why

Route an exact request identifier to an authorized structured lookup. Route a knowledge question to applicable evidence. Evaluate both the intent decision and the resulting resource scope.

## Production Case

A user asks whether a refund is allowed and then whether it was sent. The first needs current policy and case attributes; the second needs the owned operation and receiver-confirmed effect state.

## Risk

Semantic similarity cannot establish that an arbitrary request ID belongs to the user or that a versioned rule applies to their contract. Tool-side identity checks remain necessary even when prompting selects the right tool.

## Trade-off

Separate tools make intent and authority clearer but require route-selection evaluation. One universal search tool is simpler and can blur exact facts with approximate matches.

## Try This

Write expected tool sequences for an exact request ID, a remembered incident without an ID, and an eligibility question with missing facts.

## Execution Timeline

Classify question -> validate identity -> policy/evidence lookup OR owned operation lookup -> report scoped conclusion

## Complexity

Eligibility may involve evidence/rule evaluation; status uses authoritative operation lookup. Neither should be inferred from fluent generated text.

## Definitions

- **Eligibility**: What applicable evidence and current rules permit for this case.
- **Operation status**: The durable state reached by a specific owned task or effect.
- **Authoritative state**: The system of record whose committed result determines the operation outcome.

## Alternatives

- XMLHttpRequest
- Third-party HTTP libraries

## Pitfalls

- Not checking response.ok
- Trusting TypeScript types at runtime
- No error handling

## Follow-ups

### Can a retrieved policy confirm a completed refund?

No. Policy supports a permission/eligibility decision, while execution status requires durable operation and effect evidence.

## Example

> Explanation: Route by the kind of fact being requested; a policy passage cannot confirm a completed external effect.
> Output: owned_durable_operation

```python
def answer_source(question_type):
    return {'eligibility': 'applicable_policy_and_case',
            'status': 'owned_durable_operation'}[question_type]

print(answer_source('status'))
```

## Citations

- https://arxiv.org/abs/2005.11401
- https://www.postgresql.org/docs/current/tutorial.html

# What is the difference between an agent session and a conversation record?

## Answer

Agent sessions hold runtime state and events used by ADK. Conversation records hold application-visible messages, ownership, archival state, and IDs used by feedback and history APIs. They overlap in content but serve different contracts and lifecycle requirements.

## Why

Give runtime sessions and user-visible conversations separate identities and retention rules. Rehydrate only authorized history and reconcile message IDs with durable task and operation state.

## Risk

Divergence can replay a turn twice, omit tool results, or show UI messages that the agent cannot recall. Switching storage modes also needs a deliberate migration and restart story.

## Trade-off

Separate stores decouple product history from runtime implementation but require clear reconciliation and retention ownership. A single store reduces duplication and can bind the product tightly to one framework.

## Try This

Trace which IDs identify the user, conversation, ADK session, invocation, user message, and assistant message. Explain which remain stable after a restart.

# What is the real prepare-and-confirm boundary for request creation?

## Answer

Preparation validates fields and stores a pending submission with a confirmation token and expiry. Confirmation is an authenticated API operation that locks the pending submission, creates the service request and associated records, marks completion, and commits. Agent prose does not itself complete the financial workflow.

## Why

Prepare validated intent, present exact parameters for review, then verify approval inside a short transaction. Persist the authoritative result before claiming the action completed.

## Risk

The prompt's phrase that a tool call is the confirmation action can be misunderstood. The actual database submission still requires the separate route. A textual yes from the model is not proof that the API operation succeeded.

## Trade-off

Two steps add user interaction and pending-state management while reducing accidental writes. A one-step workflow is faster but gives less opportunity to review material fields.

## Try This

Follow one token from preparation to a locked confirmation transaction. Identify which operation first makes the service request durable.

# Why separate policy procedures from knowledge facts?

## Answer

A procedure describes how to investigate a question or route an unclear request. A knowledge source supplies actual limits, deductibles, exclusions, and conditions. The procedure should not become an alternative authority for contractual facts merely because it is easier to retrieve.

## Why

Store playbooks as workflow guidance and knowledge articles as factual authority. Version both and evaluate whether a current procedure can still select an inapplicable source.

## Risk

A stale procedure can direct an incomplete investigation, while a current procedure can still be combined with the wrong rule revision. Both source identities need to be visible in evaluation and operational diagnosis.

## Trade-off

Separating reasoning guidance from factual material supports independent review but adds retrieval calls and version combinations. Hardcoding all instructions in one prompt is easier to start and harder to govern.

## Try This

Label every sentence in the eligibility-review playbook as a workflow rule or factual claim. Move any unsupported numeric policy claim back to the authoritative source layer.

# Where does eventual consistency appear to a customer?

## Answer

A request can be durably submitted before its embedding job completes, so exact structured lookup and semantic search may temporarily disagree. Notification delivery can also lag the request transaction. These are different read and delivery projections of one business operation.

## Why

Commit the request and its downstream jobs together. Serve exact status from authoritative records while exposing indexing or notification lag as separate projection states.

## Risk

A search miss immediately after filing must not be reported as proof that no claim exists. An authoritative exact lookup can confirm persistence while the index catches up.

## Trade-off

Asynchronous processing keeps submission independent of provider latency but introduces lag and recovery work. Synchronous indexing is simpler conceptually and couples business availability to model services.

## Try This

Pause the embedding worker, file a service request, and compare exact lookup with semantic search. Define the appropriate user-visible status for each result.

# What are the main trust boundaries in this application?

## Answer

Boundaries include browser-to-API identity, model-to-tool authority, source-to-prompt content, application-to-database privileges, application-to-model disclosure, and application-to-observability export. Each boundary has a different actor and failure mode.

## Why

Annotate every edge with identity, allowed data, and permitted effects. Model output, retrieved text, remote metadata, and observability exports cross different trust boundaries.

## Risk

A protected chat endpoint is insufficient if a tool trusts model-supplied owner IDs or a trace exports private claim text. Read and write paths require separate evidence of enforcement.

## Trade-off

Explicit boundaries add policy and testing effort but make failures diagnosable. Combining all access behind a powerful agent credential simplifies integration and magnifies mistakes.

## Try This

Draw the support runtime diagram and annotate every edge with identity, permitted data, and whether the receiver can initiate authoritative writes.

# Which application guarantees must be established end to end?

## Answer

Implemented mechanisms include owner-scoped case retrieval, a locked confirmation row, caller-owned submission transactions, typed streaming events, optional shared idempotency, and trace instrumentation. Their deployment guarantees depend on real database behavior, chosen storage settings, provider configuration, and complete use of the intended paths.

## Why

Define tool availability, ownership checks, approval validation, persistence, and stream outcomes as independently testable contracts. A framework swap should preserve or explicitly revise those contracts.

## Risk

Reading a comment about deployment defaults or a role model as proof of configured behavior creates false confidence. Follow defaults and call sites rather than naming available classes.

## Trade-off

Conservative defaults support local development but may require production gates. Rejecting startup on missing critical state is stricter than silently falling back to local state.

## Try This

Create a deployment evidence checklist showing the selected session, idempotency, rate-limit, and tracing backends without printing secrets.

# How should you trace a request across the complete application?

## Answer

Start at user intent and verified identity, follow tool selection and scoped services, inspect evidence and model output, then confirm persisted results and client state. Trace the actual path, including failures and recovery.

## Why

Turn architectural guarantees into acceptance tests. A diagram describes intended responsibilities; concurrent workers, deployment settings, provider errors, and bypass paths determine whether the implementation actually meets them.

## Risk

A diagram can describe an ideal design while a bypass path violates it. Verify each critical boundary through observable behavior rather than relying only on intended structure.

## Trade-off

Cross-project tracing takes more effort than a single overview but teaches integration judgment, the central skill in full-stack AI engineering.

## Try This

Trace three synthetic tasks: a factual answer, an approved write, and a provider failure. Record the invariant checked at every boundary.

# Where should a shared application decide whether an operation is permitted?

<!-- meta
domain: system-design
subdomain: application-architecture
module: application-architecture
concept: Where should a shared application decide whether an operation is permitted?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: The chat path checks document ownership, but a background task calls the same repository without that scope.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Keep the authoritative authorization and business-state transition in a service boundary used by every caller. UI code and model prompts can guide interaction but cannot grant authority. Model and retrieval adapters should expose bounded capabilities without owning unrelated domain rules. Validate the caller and target again at the consequential read or write boundary.

Concrete engineering case: The chat path checks document ownership, but a background task calls the same repository without that scope.

Boundary defense: Not for object-level decisions requiring actual resource and lifecycle state. Middleware can authenticate and apply common limits; the domain boundary must enforce its own invariant.

## Spoken Summary

Keep the authoritative authorization and business-state transition in a service boundary used by every caller. UI code and model prompts can guide interaction but cannot grant authority. Model and retrieval adapters should expose bounded capabilities without owning unrelated domain rules. Validate the caller and target again at the consequential read or write boundary.

## Why

Keep the authoritative authorization and business-state transition in a service boundary used by every caller. UI code and model prompts can guide interaction but cannot grant authority. Model and retrieval adapters should expose bounded capabilities without owning unrelated domain rules. Validate the caller and target again at the consequential read or write boundary.

## Production Case

The chat path checks document ownership, but a background task calls the same repository without that scope.

## Risk

The chat path checks document ownership, but a background task calls the same repository without that scope.

## Trade-off

Not for object-level decisions requiring actual resource and lifecycle state. Middleware can authenticate and apply common limits; the domain boundary must enforce its own invariant.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: application architecture**: Keep the authoritative authorization and business-state transition in a service boundary used by every caller.

## Alternatives

- Not for object-level decisions requiring actual resource and lifecycle state. Middleware can authenticate and apply common limits; the domain boundary must enforce its own invariant.

## Pitfalls

- The chat path checks document ownership, but a background task calls the same repository without that scope.

## Follow-ups

### Would moving all checks into one generic middleware be sufficient?

Not for object-level decisions requiring actual resource and lifecycle state. Middleware can authenticate and apply common limits; the domain boundary must enforce its own invariant.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "The chat path checks document ownership, but a background task calls the same repository without that scope.",
  "required_decision": "Keep the authoritative authorization and business-state transition in a service boundary used by every caller"
}
```

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://docs.python.org/3/tutorial/

# How do you guarantee a retrieved procedure contains every required step before an agent follows it?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: application-architecture
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Procedure discovery and procedure execution need different completeness contracts.** Semantic search can help identify which approved procedure matches a task. Once selected, load that exact immutable version using its manifest and ordered step identifiers. A top-k result set is ranked evidence, not an enumeration of every required instruction.

**Validate structure, not only the number of hits.** A manifest can specify version, expected step identifiers, order, content digests and mandatory branches. Verify all required steps are present exactly once, from the same version, with matching digests. A matching count can still hide one duplicate and one missing step. If procedures form a graph, validate required nodes and edges rather than assuming a linear sequence is sufficient.

**Treat truncation as an execution boundary.** If the complete approved procedure cannot fit the request, use a typed workflow state machine that loads the next permitted step and preserves durable progress. Do not let the model freely skip unseen steps. Missing prerequisites, unreadable content or unknown versions should block actions that depend on those steps, with an explicit escalation or an approved alternative.

**Keep facts and procedure authority separate.** A runbook describes how to gather evidence and make decisions; current limits or product facts come from their authoritative sources. Retrieved text must not grant tool permissions. Procedures need controlled publication, review and rollback just like code. The executable manifest validator below rejects a missing middle step even when the remaining steps look plausible.

## Why

A retrieval query returns steps 1, 2 and 4 of a four-step access-review runbook. Step 3 contains mandatory approval. The agent must not proceed because the text reads smoothly without it.

## Worked Case

A retrieval query returns steps 1, 2 and 4 of a four-step access-review runbook. Step 3 contains mandatory approval. The agent must not proceed because the text reads smoothly without it.

## Risk

Logging a truncation warning while returning a runnable-looking partial procedure leaves the safety decision to the model.

## Trade-off

Exact versioned loading improves completeness; controlled stepwise execution supports larger procedures with more application state.

## Try This

Create a procedure with a mandatory branch, then remove a step, duplicate a step and mix versions. Verify that each invalid load blocks execution.

## Follow-ups

### Can a count equal to the retrieval limit prove truncation?

No. It signals that truncation is possible, not certain. Compare against an authoritative manifest or exhaust an exact bounded enumeration to prove completeness.

### Is a retrieved procedure trusted because it is in the index?

Index membership does not confer execution authority. Validate its publication provenance, approval and version, and keep application tool policy outside the document.

## Citations

- https://www.postgresql.org/docs/current/transaction-iso.html

# How should transactional application state be separated from conversation and retrieval state?

<!-- meta
answer_format: conceptual
domain: system-design
subdomain: application-architecture
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Conversation messages, retrieved evidence and business records have different authority, retention and consistency requirements. A transcript can record that a user asked for a cancellation without proving that a cancellation transaction committed. Keep domain operations behind explicit services and return authoritative operation identities and statuses. Link messages to those records for explanation, but do not reconstruct current truth from a model's narrative. Apply ownership checks when loading each state type, including historical conversations and retrieved attachments.

## Why

A chat answer says 'cancelled' but the provider request timed out after an uncertain commit. The UI should display the authoritative operation as pending verification and query its status instead of trusting the generated wording.

## Worked Case

A chat answer says 'cancelled' but the provider request timed out after an uncertain commit. The UI should display the authoritative operation as pending verification and query its status instead of trusting the generated wording.

## Risk

A convincing transcript can hide an unconfirmed or failed domain effect.

## Trade-off

Separate stores or modules according to contracts, not merely framework terminology.

## Try This

Model a conversation turn, a retrieval result and an accepted cancellation as distinct records.

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://docs.python.org/3/tutorial/
