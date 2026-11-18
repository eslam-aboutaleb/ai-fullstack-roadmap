<!-- chapter: agent-patterns -->

# What is the ReAct pattern?

<!-- meta
answer_format: conceptual
domain: agent-systems
subdomain: agent-patterns
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**ReAct interleaves reasoning about the next step, an action such as a tool call, and an observation of the result.** The next action depends on that observation rather than executing a fully fixed plan. Store inspectable tool/state events and concise decision summaries; private chain-of-thought is neither required for an audit nor an authoritative safety check. The executor still validates every proposed action.

**A workflow follows application-defined transitions; an agent chooses some steps from observations.** Both need explicit inputs, completion conditions and authority. A model is useful when the next information-gathering action is not known in advance, not merely because a product has a chat box. A lookup with fixed validation is usually a simpler workflow; an investigation may justify bounded planning over a narrow tool set.

Separate proposal from execution. A planner may suggest search → compare → create ticket. The executor validates tool name, argument schema, permission, remaining budget and current state before each step. Record accepted transitions rather than trusting a prose plan to describe what happened. Define terminal states for completed, awaiting approval, cancelled, failed and unknown effect; unknown is not success and should not trigger a fresh write.

In the support project, the planner is deliberately deterministic. It discovers an application registry, reads owner-scoped policy, records a proposed ticket and waits for an explicit approval command. An injected connector instruction cannot alter the registry or authorize the ticket. This isolates the execution contract so a future model planner can be swapped in and evaluated without changing permission enforcement.

Start with a baseline fixed workflow, then justify additional autonomy by task success under the same effect and cost constraints. Measure unnecessary tool calls, loops, false completion and unsafe proposals separately. Bound elapsed time, steps, output bytes, attempts and concurrent work. A more elaborate planner can reduce user effort while introducing nondeterminism, latency and recovery states; the implementation must make those costs observable.

## Why

A return-policy lookup needs a predictable read, while an ambiguous receipt incident may need investigation. The project holds the execution boundary fixed so adding a planner cannot silently grant new powers.

## Worked Case

A return-policy lookup needs a predictable read, while an ambiguous receipt incident may need investigation. The project holds the execution boundary fixed so adding a planner cannot silently grant new powers.

## Risk

A plan can claim completion without any committed effect. Evaluate receiver state and task evidence independently of the planner transcript.

## Trade-off

Fixed workflows are easier to replay and audit. Agent-selected tools can handle unfamiliar tasks but add uncertainty, cost and evaluation requirements.

## Try This

Run research_support_project.py tools, then propose a ticket without approving it. Draw the state machine and show that planning alone created no ticket.

## Follow-ups

### When should a router choose a deterministic workflow instead?

When the task maps reliably to a known bounded procedure, route to it and preserve its validation. Escalate ambiguous cases explicitly; a routing model must not turn uncertainty into extra authorization.

## Citations

- https://www.anthropic.com/engineering/building-effective-agents
- https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture

# When should you use a router pattern?

## Answer

A router sends a task to a specialized workflow or capability based on intent and required authority. Routing can be deterministic, model-assisted, or hybrid.

## Why

Validate route labels and provide an ambiguous or unsupported path. Evaluate routing independently from specialist quality.

## Risk

A routing error can send sensitive data to the wrong service.

## Trade-off

Specialization improves focus while increasing handoff and monitoring needs.

## Try This

Route billing, product, and unsupported requests with a confidence-independent fallback rule.

# What is a planner-executor pattern?

## Answer

A planner proposes work, while an executor applies validated steps and returns observations. This separates flexible decomposition from constrained action.

## Why

Restrict executable step types, enforce budgets, and revise the plan when an observation invalidates an assumption.

## Risk

A polished plan can still contain impossible or unauthorized steps.

## Trade-off

Planning improves visibility and may be wasteful for short tasks.

## Try This

Reject a plan step that references a tool absent from the permitted registry.

# When does a supervisor-worker pattern help?

## Answer

A supervisor coordinates specialists that solve bounded subproblems with explicit inputs and outputs. It helps when specialist responsibilities genuinely differ.

## Why

Give workers narrow tools, independent budgets, and artifact contracts. The supervisor verifies outputs before aggregating them.

## Risk

The supervisor can become a bottleneck or accept unsupported worker summaries.

## Trade-off

Specialist depth adds calls, latency, and integration complexity.

## Try This

Compare one capable agent with three specialists on the same investigation fixtures.

# How does a handoff differ from delegation?

## Answer

Delegation keeps coordination with the original agent while a worker performs a subtask. A handoff transfers responsibility or interaction control to another participant under a defined protocol.

## Why

Preserve task identity, user-visible ownership, and authorization context across the boundary. Define who communicates completion and failure.

## Risk

Ambiguous ownership can leave a user waiting while both agents assume the other will respond.

## Trade-off

Handoffs improve specialization and complicate continuity.

## Try This

Design a handoff record with the next owner, reason, evidence, and pending action.

# What is an evaluator-optimizer pattern?

## Answer

A generator proposes output and an evaluator checks it against an explicit rubric, producing targeted revision feedback. The loop stops when acceptance criteria or a budget is reached.

## Why

Use a critic with appropriate evidence and calibrate it against known results. Keep the final gate independent when possible.

## Risk

Correlated generator and critic errors can create false confidence.

## Trade-off

Iteration can improve quality while increasing cost and over-editing risk.

## Try This

Measure factual correctness before and after revision instead of measuring stylistic change.

# When is a parallel ensemble appropriate?

## Answer

Use an ensemble when independent approaches provide useful diversity and you have a reliable aggregation or verification method. More agents alone do not guarantee better reasoning.

## Why

Vary evidence or method deliberately and compare outputs under a shared factual rubric. Count total cost and disagreement.

## Risk

Identical models with identical context may repeat the same mistake.

## Trade-off

Diversity improves robustness in some workloads and adds latency or cost.

## Try This

Compare one solver against two independent approaches on ambiguous cases.

# What is a tool-first deterministic pattern?

## Answer

Resolve exact facts and validated operations through deterministic services before asking a model to explain them. The model handles language while the backend remains the authority.

## Why

Route known identifiers to owner-scoped lookups and use generation only after receiving a typed result.

## Risk

A tool can still return stale or incorrectly scoped data if its backend contract is weak.

## Trade-off

Deterministic paths reduce flexibility and support strong guarantees.

## Try This

Answer a request-status question without semantic search or model-selected resource IDs.

# What are saga and outbox patterns useful for in agent systems?

## Answer

A saga coordinates multi-step business changes with compensating actions; an outbox records durable downstream work in the same transaction as a business change. They solve different distributed consistency problems.

## Why

Keep model decisions separate from the transaction. Make workers idempotent and compensation semantics explicit.

## Risk

Compensation may not fully reverse real-world effects such as a sent email.

## Trade-off

Eventual consistency improves availability and requires recovery tooling.

## Try This

Model a reservation plus notification workflow and identify which failures can be compensated.

# How should you choose an agent pattern?

## Answer

Start from the task's uncertainty, authority, state, latency budget, and recovery needs. Choose the simplest structure that meets measured requirements.

## Why

Compare candidates on the same fixtures and document why added coordination improves outcomes. Patterns can be combined at clear boundaries.

## Risk

Architecture diagrams can look sophisticated without improving completion rate.

## Trade-off

Simplicity limits flexibility and reduces operational burden.

## Try This

Defend one fixed workflow and one agent pattern using failure and cost evidence.

# When is a deterministic workflow preferable to a planner or multi-agent pattern?

<!-- meta
domain: agents
subdomain: agent-patterns
module: agent-patterns
concept: When is a deterministic workflow preferable to a planner or multi-agent pattern?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A three-step policy lookup becomes a five-agent debate with more latency but no measurable quality improvement.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Choose a fixed workflow when the permitted steps and recovery conditions are known and dynamic selection adds little value. A planner can help when task decomposition or capability choice genuinely varies, but requires evaluation of authority, loop limits and uncertainty. Compare the simplest baseline under the same task and operational budget.

Concrete engineering case: A three-step policy lookup becomes a five-agent debate with more latency but no measurable quality improvement.

Boundary defense: A representative task set where adaptive choices improve meaningful outcomes enough to justify additional cost, failure paths and review burden.

## Spoken Summary

Choose a fixed workflow when the permitted steps and recovery conditions are known and dynamic selection adds little value. A planner can help when task decomposition or capability choice genuinely varies, but requires evaluation of authority, loop limits and uncertainty. Compare the simplest baseline under the same task and operational budget.

## Why

Choose a fixed workflow when the permitted steps and recovery conditions are known and dynamic selection adds little value. A planner can help when task decomposition or capability choice genuinely varies, but requires evaluation of authority, loop limits and uncertainty. Compare the simplest baseline under the same task and operational budget.

## Production Case

A three-step policy lookup becomes a five-agent debate with more latency but no measurable quality improvement.

## Risk

A three-step policy lookup becomes a five-agent debate with more latency but no measurable quality improvement.

## Trade-off

A representative task set where adaptive choices improve meaningful outcomes enough to justify additional cost, failure paths and review burden.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: agent patterns**: Choose a fixed workflow when the permitted steps and recovery conditions are known and dynamic selection adds little value.

## Alternatives

- A representative task set where adaptive choices improve meaningful outcomes enough to justify additional cost, failure paths and review burden.

## Pitfalls

- A three-step policy lookup becomes a five-agent debate with more latency but no measurable quality improvement.

## Follow-ups

### What evidence would justify the more dynamic pattern?

A representative task set where adaptive choices improve meaningful outcomes enough to justify additional cost, failure paths and review burden.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A three-step policy lookup becomes a five-agent debate with more latency but no measurable quality improvement.",
  "required_decision": "Choose a fixed workflow when the permitted steps and recovery conditions are known and dynamic selection adds little value"
}
```

## Citations

- https://adk.dev/evaluate/

# When should you use a deterministic workflow, a single agent or multiple agents?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: agent-patterns
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Choose from task structure, not a desire to use agents.** A workflow follows application-defined transitions. An agent chooses its next action dynamically from observations. Multiple agents introduce separate reasoning contexts and coordination. A queue of identical embedding workers is parallel processing, not necessarily a multi-agent system.

| Situation | Starting design | Evidence needed before adding autonomy |
| --- | --- | --- |
| Upload, scan, parse, embed and publish documents | Durable deterministic workflow | Usually none: transitions and retry rules are known |
| Answer a policy question from authorized sources | Retrieval plus one generation step | Demonstrate failures requiring iterative search |
| Diagnose an unfamiliar repository bug | Bounded single agent in a sandbox | Show dynamic inspection improves verified fixes |
| Research independent markets with distinct source sets | Parallel workers or specialist agents | Show useful independence and affordable synthesis |
| Approve a refund or change permissions | Deterministic policy and approval boundary | An agent may propose; authority remains in code |

**Specify an evaluation gate.** Compare each candidate on held-out tasks using verified outcomes, unauthorized actions, latency percentiles and cost per successful task. Include ambiguous inputs, missing evidence, tool errors and cancellation. A more complex system should earn its coordination cost through a measured improvement.

**Bound the chosen autonomy.** Limit steps, elapsed time, tokens, money and tool scope. Require structured outputs that the application validates. Keep irreversible effects behind explicit policy checks and idempotent service operations. If a task has a known procedure, an agent that invents the procedure adds uncertainty without a demonstrated benefit.

## Why

A document ingestion product needs robust retries and accurate indexing. It starts with a state machine. A separate research feature may need adaptive queries, so it can use a bounded agent without turning file upload into an agent task.

## Worked Case

A document ingestion product needs robust retries and accurate indexing. It starts with a state machine. A separate research feature may need adaptive queries, so it can use a bounded agent without turning file upload into an agent task.

## Risk

Adding agents to a fixed pipeline can make retries and completion criteria harder to reason about.

## Trade-off

Autonomy is useful when the next useful action depends on observations; deterministic paths are easier to test when the sequence is known.

## Try This

Choose designs for invoice extraction, repository repair and market research. Define one measurable condition under which you would change each design.

## Citations

- https://www.anthropic.com/research/building-effective-agents

# How do reflection and multi-agent debate differ from independently verified evidence?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: agent-patterns
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Reflection asks a model to critique or revise an answer; debate asks multiple roles or agents to propose and challenge alternatives. These may expose mistakes but remain correlated when they share a model, prompt assumptions or source material. Agreement is not the same as an independent measurement or an authorized decision. Use verifiable intermediate outputs, independent sources where available and a bounded arbitration policy. Prefer a simpler deterministic workflow when roles add tokens without improving measured outcomes.

## Why

Three specialist agents agree that a policy permits an action because all read the same incomplete excerpt. A fourth debate round cannot supply the missing exclusion; checking the complete governing source can.

## Worked Case

Three specialist agents agree that a policy permits an action because all read the same incomplete excerpt. A fourth debate round cannot supply the missing exclusion; checking the complete governing source can.

## Risk

More agent roles can amplify one unsupported assumption and diffuse accountability.

## Trade-off

Add roles for distinct capabilities or evidence, not simulated consensus alone.

## Try This

Compare debate with a single-agent baseline on a shared-source failure case.

## Citations

- https://adk.dev/evaluate/
