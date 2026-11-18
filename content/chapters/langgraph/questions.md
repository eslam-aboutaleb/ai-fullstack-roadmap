<!-- chapter: langgraph -->

# What problem would LangGraph solve that a basic agent loop does not?

<!-- meta
reference: https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph
-->

## Answer

LangGraph expresses a workflow as state, nodes, and transitions, with explicit branching and persistence options. It is useful when retries, human review, resumability, and bounded stages should be visible in the orchestration design rather than left entirely to a model loop.

## Why

Represent explicit state transitions when the workflow needs branching, checkpoints, review, or recovery. Keep a simple agent loop when those requirements do not justify a graph.

## Risk

A graph diagram can suggest stronger guarantees than its nodes implement. Domain writes still need their own transaction and permission boundaries.

## Trade-off

Explicit control improves inspectability while adding state schema and orchestration code. A simple tool-calling loop can remain sufficient for narrow conversational tasks.

## Try This

Draw a proposed eligibility-review graph with answerable, missing-facts, unavailable-backend, and escalation branches before writing nodes.

# How do StateGraph state, nodes, and conditional edges work together?

<!-- meta
reference: https://docs.langchain.com/oss/python/langgraph/graph-api
-->

## Answer

State is the workflow's shared data contract; nodes compute updates; edges choose what executes next. A node can be deterministic code or a model call. Conditional routing should use validated state rather than treating arbitrary generated text as an unrestricted next-node name.

## Why

Define typed state with clear ownership, transient fields, durable references, and terminal outcomes. Store large artifacts separately and keep versioned IDs inside graph state.

## Risk

Overloaded state can retain private text, credentials, or stale authorization. Input schema shape alone does not decide what a stream or trace may disclose.

## Trade-off

Explicit state improves testing and requires careful versioning. A dictionary with unrestricted keys is flexible and harder to migrate or secure.

## Try This

Separate public output fields, internal evidence references, and trusted identity in the proposed graph contract.

# Why do reducers matter when graph nodes run in parallel?

<!-- meta
reference: https://docs.langchain.com/oss/python/langgraph/graph-api
-->

## Answer

A reducer defines how multiple updates to a state field combine. Replacing a value, appending messages, and merging keyed results are different semantics. Parallel branches need a declared merge rule rather than assuming the last writer is correct.

## Why

Give parallel updates explicit merge semantics through compatible reducers. Decide whether lists append, records replace, or conflicts fail; persistence alone does not define a safe merge.

## Risk

An append reducer can duplicate retries, and a merge can combine evidence from incompatible revisions or scopes. A reducer is not a distributed database transaction.

## Trade-off

Explicit merge rules support parallel work and require identity, ordering, and replay discipline. Sequential nodes avoid some conflicts at the cost of latency.

## Try This

Design a reducer for evidence keyed by source, revision, and chunk ID. Show how repeated delivery avoids duplicating the same item.

# What is a checkpoint, and how is it different from a business commit?

<!-- meta
reference: https://docs.langchain.com/oss/python/langgraph/persistence
-->

## Answer

A checkpoint stores workflow state so execution can resume or be inspected. A business commit makes an authoritative business transition durable. A checkpoint can refer to a completed operation, but saving it does not atomically commit another service's database transaction.

## Why

Treat checkpoints as workflow progress records. Reconcile them with authoritative operation status after crashes, because checkpoint persistence and a separate business transaction may not commit together.

## Risk

On resume, a node may retry an already-completed side effect. An in-memory saver demonstrates state handling only within its lifetime and is not a durable production guarantee.

## Trade-off

Durable checkpoints support recovery and require storage, retention, access policy, and schema evolution. Pure in-memory graphs are easier for local experiments.

## Try This

Draw a crash after business commit but before checkpoint save. Specify how an operation ID lets the resumed node discover the existing result.

# How does a human-review interrupt differ from authorization?

<!-- meta
reference: https://docs.langchain.com/oss/python/langgraph/interrupts
-->

## Answer

An interrupt pauses workflow progress and exposes a question or proposed action for review. Authorization determines whether the identity resuming it is permitted to approve that exact action. A resume payload saying approved is untrusted unless the server validates its actor and scope.

## Why

Pause execution for input or review, then validate the resumed principal and approval against current business state. A resume command is control flow, not authorization.

## Risk

Guessable or cross-user thread access can resume another person's workflow. Material edits after review can invalidate what was approved even if the resume token is technically valid.

## Trade-off

Human pauses reduce accidental actions while adding persistence and expiry management. For low-risk reads they may be unnecessary.

## Try This

Bind a proposed review to user, payload hash, operation ID, and expiry. Test an unauthorized resume and a changed amount.

# Why must code before an interrupt or retry be safe to execute again?

<!-- meta
reference: https://docs.langchain.com/oss/python/langgraph/interrupts
-->

## Answer

Resuming or recovering a workflow may re-enter node code. Work performed before the pause can therefore repeat. Deterministic computation is usually safe; sending a notification or creating a service request needs a durable idempotent operation boundary.

## Why

Put nondeterministic and side-effecting work behind replay-safe boundaries. Use durable operation keys and test the crash window after an effect but before checkpoint completion.

## Risk

Repeating a preparation can leave multiple live tokens; repeating an external notification can confuse the user. A cached Python return value is not enough across process crashes.

## Trade-off

Smaller nodes with explicit side-effect tasks improve replay reasoning and add orchestration detail. One large node is shorter and harder to recover safely.

## Try This

Put a harmless counter and a mock external action before a teaching interrupt. Observe replay, then move the action behind an idempotent service contract.

# How should graph retries and timeouts be layered?

## Answer

Retry only failures likely to recover, with bounded attempts and an overall deadline. A node retry, provider retry, database retry, and client retry can multiply each other. Track the full operation budget and avoid retrying invalid authorization or schema errors.

## Why

Layer node retries, provider retries, and task deadlines deliberately. Count all attempts in one budget and classify business rejection separately from transient infrastructure failure.

## Risk

Nested retries amplify load and can execute write nodes repeatedly. A model timeout also does not prove the provider or remote agent stopped processing.

## Trade-off

Local resilience helps transient failures, while a simpler centralized budget is easier to reason about. Use stage-specific policy with one overall ceiling.

## Try This

Calculate worst-case attempts for two client retries, three node attempts, and four provider attempts. Replace that accidental multiplier with an explicit budget.

# Can graph private state be streamed safely by default?

<!-- meta
reference: https://docs.langchain.com/oss/python/langgraph/streaming
-->

## Answer

Do not assume a private schema is a redaction policy. A framework may stream internal state or custom events depending on mode. Define an application event projection that allowlists public fields and removes private evidence, identity, and credentials.

## Why

Project only approved fields into public events. State needed for internal coordination can include private evidence, tool arguments, or identifiers that should not be streamed.

## Risk

Forwarding raw values or updates can expose claim details or internal analysis. A UI that hides a field visually has still received it over the network.

## Trade-off

Allowlisted projections take adapter work and preserve privacy across framework updates. Raw graph streaming is convenient for development diagnostics only under controlled access.

## Try This

Insert a synthetic private field into graph state and inspect every chosen stream mode. Verify the public SSE adapter never emits it.

# How should graph state and checkpoints evolve across deployments?

## Answer

Version state schemas and maintain readers or migrations for active checkpoints. A suspended service workflow may resume after code changes, so renamed fields, changed node semantics, and new authorization requirements need compatibility handling.

## Why

Version checkpoint schemas and migrate or isolate old threads deliberately. Test resume with old artifacts after deployment, and prevent incompatible readers from silently interpreting changed state fields.

## Risk

A resumed old workflow can invoke a new write path with stale assumptions. Authorization should be re-evaluated at action time rather than frozen indefinitely in a checkpoint.

## Trade-off

Compatibility readers increase maintenance and preserve resumability. Expiring old workflows simplifies migration but must communicate how users restart safely.

## Try This

Design a v1-to-v2 checkpoint migration that adds rule revision and payload hash before confirmation. Specify what happens if the old evidence no longer exists.

# When is LangGraph a better choice than ADK or a plain function?

## Answer

Choose it when explicit state transitions, branching, durable pause/resume, or inspectable parallel work solve a real product requirement. Keep a plain function for deterministic small operations and consider retaining ADK when flexible tool routing already meets the need.

## Why

Evaluate transitions, terminal outcomes, approvals, replay, and cost under realistic failures. A passing graph visualization or one happy-path invocation does not establish business reliability.

## Risk

Introducing a graph solely to draw a more impressive architecture can add persistence and deployment obligations without improving outcomes. More orchestration layers can also fragment traces and ownership.

## Trade-off

Explicit workflow control is valuable when recovery and review dominate. Simpler code is preferable when the path is short and has no durable pauses.

## Try This

Write a decision record for one proposed graph workflow and one operation you deliberately keep as a normal function. Defend both choices.

# How does LangGraph implement cyclical state machines using StateGraph, and how do conditional edges control agent looping versus termination?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: agent-orchestration
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**LangGraph implements agent workflows as directed cyclical graphs where nodes represent computation steps and edges define deterministic or conditional control flow.** Traditional DAG (Directed Acyclic Graph) workflow engines (like Airflow) forbid cycles by design. However, autonomous agents inherently require cyclical loops: reasoning -> tool execution -> observing results -> re-evaluating until the goal is achieved or a termination condition is reached.\n\n**State schema and reducer semantics.** In LangGraph, the central data contract is the `State` dictionary or Pydantic model. When multiple nodes execute or return updates, LangGraph applies explicit reducer functions (such as `operator.add` for message arrays or custom merge logic) to evolve the state immutably: `class AgentState(TypedDict): messages: Annotated[list[BaseMessage], operator.add]`.

Nodes are pure functions accepting the current state and returning a dictionary of partial updates.\n\n**Conditional edges as decision routers.** Control flow branching is governed by conditional edges: `workflow.add_conditional_edges("planner", route_decision, {"tools": "tools_node", "end": END})`. The routing function inspects the state (e.g. checking whether the last message contains tool calls) and returns the string identifier of the next target node. Termination is strictly guarded by routing to `END` or enforcing a maximum recursion limit (`recursion_limit=25`), preventing runaway infinite loops when an agent encounters persistent tool errors.

## Why

An agent calls a calculator tool that fails with a division-by-zero error. Without conditional edge routing and recursion limits, the agent repeatedly retries the identical tool call forever, exhausting API budgets. LangGraph conditional edges catch the error state and route to a fallback explanation node.

## Worked Case

An agent calls a calculator tool that fails with a division-by-zero error. Without conditional edge routing and recursion limits, the agent repeatedly retries the identical tool call forever, exhausting API budgets. LangGraph conditional edges catch the error state and route to a fallback explanation node.

## Risk

Defining incorrect reducer functions on state fields can accidentally overwrite past conversation history instead of appending to it, wiping out agent context.

## Trade-off

StateGraph requires explicit state schema design and node decoupling, trading the quick setup of linear chains for robust cyclic control and debuggability.

## Try This

Build a LangGraph StateGraph with a planner node, a tool node, and a conditional edge. Enforce a recursion limit of 5 and assert that the graph halts when the limit is breached.

## Follow-ups

### What happens when two parallel nodes write to the same state key?

If a key has an associative reducer like operator.add, both updates are merged; if no reducer is defined, LangGraph raises an InvalidUpdateError.

## Citations

- https://langchain-ai.github.io/langgraph/concepts/low_level/
- https://langchain-ai.github.io/langgraph/reference/graphs/

# How does Checkpointing in LangGraph enable persistent conversational memory and human-in-the-loop interrupt-and-resume workflows?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: agent-orchestration
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**LangGraph checkpointers save atomic snapshots of graph state at every super-step, enabling durable multi-turn execution, state recovery, and human-in-the-loop approval.** In production applications, agent interactions span minutes, hours, or days. If an application worker crashes mid-trajectory, or if a high-impact financial mutation requires human authorization, in-memory state is lost unless backed by durable persistence.\n\n**Checkpointing architecture.** Checkpointers (such as `MemorySaver`, `SqliteSaver`, or `PostgresSaver`) serialize the entire state dictionary, next node pointers, and execution metadata after every node transition, indexed by `thread_id` and monotonic `checkpoint_id`. Resuming a conversation requires simply passing the identical `thread_id` in configuration: `graph.invoke(input, config={"configurable": {"thread_id": "session_123"}})`. The graph automatically rehydrates state from the last committed checkpoint without re-executing completed nodes.\n\n**Human-in-the-Loop (HITL) interrupt patterns.** LangGraph provides native breakpoint interrupts: `workflow.compile(checkpointer=checkpointer, interrupt_before=["execute_transfer"])`.

When execution reaches `execute_transfer`, the engine halts and yields control back to the caller, leaving the graph in a paused state. The user or supervisor reviews the pending state (e.g. transfer recipient and amount) via an administrative UI. Upon approval, the application invokes the graph with `graph.invoke(None, config)`, which resumes execution seamlessly from the exact breakpoint.

## Why

An agent prepares an international wire transfer. The checkpointer halts execution immediately before the transfer node. The manager inspects the pending transaction, approves it via web portal, and the graph resumes and executes the wire transfer with zero state loss.

## Worked Case

An agent prepares an international wire transfer. The checkpointer halts execution immediately before the transfer node. The manager inspects the pending transaction, approves it via web portal, and the graph resumes and executes the wire transfer with zero state loss.

## Risk

Using in-memory MemorySaver in production leads to complete state loss whenever container pods restart or autoscale.

## Trade-off

Durable PostgreSQL checkpointing requires managing database connection overhead and snapshot storage, in exchange for crash resilience and interactive approval gates.

## Try This

Compile a graph with `interrupt_before=["action_node"]`. Run the graph, observe that it stops before `action_node`, inspect `graph.get_state(config)`, and resume it with `graph.invoke(None, config)`.

## Follow-ups

### Can a human modify the state while a graph is paused at an interrupt?

Yes. `graph.update_state(config, {"amount": 50})` allows a human to edit parameters before resuming execution, forking or updating the trajectory.

## Citations

- https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/
- https://langchain-ai.github.io/langgraph/concepts/persistence/

# What is Time-Travel debugging in LangGraph, and how does state fork branching work during incident investigation?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: agent-orchestration
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Time-Travel debugging in LangGraph allows developers and operators to replay, inspect, and fork an agent's execution trajectory from any historical state checkpoint.** When an autonomous agent makes a catastrophic reasoning mistake or hallucinates a bad tool argument in turn 8 of a 10-turn interaction, standard debugging requires restarting the conversation from scratch and hoping the non-deterministic LLM reproduces the error.\n\n**Linear state lineage and checkpoint indexing.** Because LangGraph checkpointers persist an immutable append-only ledger of state snapshots tagged with unique `checkpoint_id` and parent pointer hashes, the entire execution history forms a directed acyclic version tree. An engineer can query the historical trajectory: `history = list(graph.get_state_history(config))`. Each entry contains the complete state snapshot, the node that executed, and the exact tool outputs received at that specific point in time.\n\n**Forking execution from historical states.** To test alternative prompt instructions or fix an erroneous tool payload, the developer selects a historical checkpoint: `config = {"configurable": {"thread_id": "session_123", "checkpoint_id": "chk_04"}}`.

The developer calls `graph.update_state(config, {"corrected_data": "valid_value"})`. LangGraph creates a new branch in the checkpoint tree, branching off from step 4 without mutating the original historical timeline. When `graph.invoke(None, config)` is called, the agent executes from step 4 forward under the corrected state. This transforms debugging from guesswork into deterministic, replayable scientific analysis.

## Why

An agent failed at step 7 because an API returned an unexpected date format. A developer loads checkpoint 6, patches the state with the normalized date format, and resumes the run. The agent succeeds, proving the root cause without re-running steps 1 through 5.

## Worked Case

An agent failed at step 7 because an API returned an unexpected date format. A developer loads checkpoint 6, patches the state with the normalized date format, and resumes the run. The agent succeeds, proving the root cause without re-running steps 1 through 5.

## Risk

Allowing arbitrary state updates without schema validation during production replay can introduce invalid domain types into running sessions.

## Trade-off

Retaining complete checkpoint histories consumes database storage over time, requiring automated snapshot retention and compaction policies.

## Try This

Run an agent graph for 5 steps with PostgresSaver. Retrieve the state history, pick step 2, update a state field, and resume execution to observe the branched trajectory.

## Follow-ups

### Does forking a state checkpoint delete subsequent checkpoints in the original thread?

No. Checkpointers maintain an append-only DAG of state revisions, preserving both the original execution branch and the new forked branch.

## Citations

- https://langchain-ai.github.io/langgraph/concepts/time-travel/
- https://langchain-ai.github.io/langgraph/reference/checkpoints/

# How do Multi-Agent architectures coordinate state sharing and avoid infinite delegation loops in LangGraph?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: agent-orchestration
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Multi-agent coordination in LangGraph requires explicit topological communication patterns to prevent coordination deadlock and delegation thrashing.** When decomposing complex enterprise systems into specialized autonomous agents (e.g., a Research Agent, a Coding Agent, and a Reviewer Agent), naive implementations allow agents to delegate freely to one another.

Without centralized governance, agents easily become trapped in infinite ping-pong loops: Agent A asks Agent B for clarification, Agent B delegates back to Agent A, burning tokens indefinitely.\n\n**Three primary Multi-Agent topologies.** LangGraph structures multi-agent collaboration across three architectural patterns: (1) Supervisor Architecture: A centralized router agent evaluates user intent, delegates work to specialized sub-agents, aggregates their structured outputs, and decides when the task is complete. Sub-agents communicate strictly with the supervisor, never directly with each other; (2) Hierarchical Teams: Nested sub-graphs where each specialized domain (e.g., Software Engineering team) has its own internal supervisor managing child workers (Coder, Tester), reporting consolidated summaries up to a root orchestrator; and (3) Peer-to-Peer State Collaboration: Agents share a unified `AgentState` containing a shared message ledger, with conditional edges enforcing strict sequential handoffs (e.g., Coder -> Linter -> Reviewer -> End).\n\n**Anti-loop governance.** Production systems enforce loop guards: (1) Monotonic turn counters embedded in state: incrementing `delegation_count` and routing to an Escalation node if `count > max_turns`; and (2) Structured task status envelopes: requiring sub-agents to emit explicit status flags (`DONE`, `BLOCKED`, `NEED_INFO`) rather than open-ended natural language banter.

## Why

A Researcher agent and a Writer agent pass draft versions back and forth 30 times critiquing minor phrasing. A Supervisor topology limits critique to 2 rounds, forcing the Writer to output the final draft once the revision budget is exhausted.

## Worked Case

A Researcher agent and a Writer agent pass draft versions back and forth 30 times critiquing minor phrasing. A Supervisor topology limits critique to 2 rounds, forcing the Writer to output the final draft once the revision budget is exhausted.

## Risk

Allowing unrestricted peer-to-peer agent delegation leads to exponential token consumption and non-deterministic completion times.

## Trade-off

A centralized supervisor agent adds an extra model invocation per handoff, trading minor routing latency for deterministic coordination and strict budget control.

## Try This

Implement a Supervisor LangGraph with two worker sub-agents (MathAgent, SearchAgent). Set `max_turns=3` in state, and assert that the graph halts and returns a summary when the budget is reached.

## Follow-ups

### How do sub-agents keep their private context from polluting the global state?

Use isolated sub-graphs: the sub-graph executes internally with a private detailed state and maps only its final distilled answer to the parent graph's global state.

## Citations

- https://langchain-ai.github.io/langgraph/concepts/multi_agent/
- https://langchain-ai.github.io/langgraph/tutorials/multi_agent/hierarchical_agent_teams/

# What can a durable LangGraph checkpoint fail to tell you about an interrupted node?

<!-- meta
domain: ai-rag
subdomain: langgraph
module: langgraph
concept: What can a durable LangGraph checkpoint fail to tell you about an interrupted node?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: The checkpoint says a tool node is incomplete, while the tool’s receiver has already applied its mutation.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

A checkpoint describes the persisted workflow state at its boundary. Work performed after that checkpoint, especially an external receiver commit, can remain uncertain. Bind effects to stable identities, inspect actual resume semantics for the pinned runtime and test a crash between provider commit and local acknowledgment.

Concrete engineering case: The checkpoint says a tool node is incomplete, while the tool’s receiver has already applied its mutation.

Boundary defense: No. The function may have external effects, random choices or time-dependent inputs. Preserve their identity and recovery contract.

## Spoken Summary

A checkpoint describes the persisted workflow state at its boundary. Work performed after that checkpoint, especially an external receiver commit, can remain uncertain. Bind effects to stable identities, inspect actual resume semantics for the pinned runtime and test a crash between provider commit and local acknowledgment.

## Why

A checkpoint describes the persisted workflow state at its boundary. Work performed after that checkpoint, especially an external receiver commit, can remain uncertain. Bind effects to stable identities, inspect actual resume semantics for the pinned runtime and test a crash between provider commit and local acknowledgment.

## Production Case

The checkpoint says a tool node is incomplete, while the tool’s receiver has already applied its mutation.

## Risk

The checkpoint says a tool node is incomplete, while the tool’s receiver has already applied its mutation.

## Trade-off

No. The function may have external effects, random choices or time-dependent inputs. Preserve their identity and recovery contract.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: langgraph**: A checkpoint describes the persisted workflow state at its boundary.

## Alternatives

- No. The function may have external effects, random choices or time-dependent inputs. Preserve their identity and recovery contract.

## Pitfalls

- The checkpoint says a tool node is incomplete, while the tool’s receiver has already applied its mutation.

## Follow-ups

### Does replaying the same Python function imply a safe replay?

No. The function may have external effects, random choices or time-dependent inputs. Preserve their identity and recovery contract.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "The checkpoint says a tool node is incomplete, while the tool’s receiver has already applied its mutation.",
  "required_decision": "A checkpoint describes the persisted workflow state at its boundary"
}
```

## Citations

- https://docs.langchain.com/oss/python/langgraph/persistence
- https://docs.langchain.com/oss/python/langgraph/interrupts
- https://docs.langchain.com/oss/python/langgraph/graph-api

# How do durable checkpoints, node replay and external effect identity interact?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: langgraph
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A checkpoint preserves graph execution state under its storage contract; it does not atomically include every external service effect. A node may be replayed after failure or resumption, depending on the execution boundary. Isolate nondeterministic and effectful operations according to the framework's durable-execution guidance and give consequential external operations stable identities. Version graph state and test migration or rejection of incompatible checkpoints. Reauthorization on resume matters because the user's permissions may have changed while the graph was paused.

## Why

A node sends an email and crashes before its next persisted boundary. Resuming from the prior checkpoint can call it again unless the email operation has an independently enforced replay policy.

## Worked Case

A node sends an email and crashes before its next persisted boundary. Resuming from the prior checkpoint can call it again unless the email operation has an independently enforced replay policy.

## Risk

Persistence is often mistaken for universal exactly-once execution.

## Trade-off

Durable graphs improve recovery when state and effect boundaries are designed explicitly.

## Try This

Crash after an external acceptance and resume the graph without duplicating the effect.

## Citations

- https://docs.langchain.com/oss/python/langgraph/persistence
- https://docs.langchain.com/oss/python/langgraph/interrupts
- https://docs.langchain.com/oss/python/langgraph/graph-api
