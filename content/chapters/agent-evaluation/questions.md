<!-- chapter: agent-evaluation -->

# Why is answer evaluation insufficient for an agent?

<!-- meta
answer_format: conceptual
domain: agent-systems
subdomain: agent-evaluation
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**An agent trajectory is the ordered sequence of observations, proposals, tool calls and transitions.** Evaluate both its final task artifact and its actual effects. A pleasant answer saying 'ticket created' is not proof of a ticket, and a ticket alone is not proof it was authorized. A valid run needs supported source evidence, policy-compliant dispatch and the independently committed receiver state.

Give a run stable request/owner/operation IDs and record safe step metadata: tool/schema version, argument digest, source revision, approval decision, attempt, stop reason and effect outcome. Redact credentials and unnecessary text. Connect events causally rather than inferring order from wall-clock timestamps alone. Trace collection failures need an explicit policy; regulated effects may require fail-closed durable audit, while a read-only observation can tolerate sampled telemetry.

The support project exports source → proposal → approval → effect-committed → reconciled events. Its local ticket table is an independent outcome oracle. The checker separately counts effects, races two connections, injects acknowledgment loss and aborts audit insertion. The static trace reader renders local JSON using text nodes and never executes a tool. A trace viewer is an inspection aid, not an authorization system or proof that omitted events never occurred.

Build a fixed task suite with supported queries, unsupported cases, malicious connector text, wrong owners, changed payloads and recovery incidents. Score task success, unsupported claims, denied writes, duplicate effects, unnecessary calls and budget use separately. Preserve critical policy failures as release blockers even if aggregate task success improves. A model-planning extension needs adjudicated expected outcomes and replayable tool fixtures; do not evaluate it only on its own explanation of why it succeeded.

## Why

The trace shows two executions after acknowledgment loss, while the ticket table contains one row. Evaluating call count alone would falsely report duplication; evaluating the final prose alone would miss unauthorized effects.

## Worked Case

The trace shows two executions after acknowledgment loss, while the ticket table contains one row. Evaluating call count alone would falsely report duplication; evaluating the final prose alone would miss unauthorized effects.

## Risk

A model-generated rationale is not an audit log. Missing or tampered events can hide failures, so compare traces with durable state and record the telemetry completeness assumption.

## Trade-off

Full traces improve diagnosis but add storage and privacy exposure. Store safe identifiers by default and make any sensitive-content retention explicit and bounded.

## Try This

Export the support report and open agent_trace_reader.html. Independently count ticket effects and match source/operation identities, then explain the rollback behavior when the audit trigger fails.

## Follow-ups

### Can a second model judge certify that a payment was authorized?

No. It can help review language, but authorization and receiver state come from authoritative records. Use deterministic permission/effect checks plus adjudicated semantic assessment rather than replacing service invariants with a judge score.

## Citations

- https://opentelemetry.io/docs/security/handling-sensitive-data/
- https://www.nist.gov/itl/ai-risk-management-framework

# How do reference trajectories and invariant-based trajectories differ?

<!-- meta
domain: agents
subdomain: evaluation
module: agent-evaluation
concept: How do reference trajectories and invariant-based trajectories differ
difficulty: implementation
misconception_target: Agent trajectories must match exactly to pass
reference: https://github.com/google/adk-docs/blob/main/docs/evaluate/criteria.md
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

A reference trajectory compares observed calls with an expected sequence. An invariant checks necessary properties such as owner scoping, no duplicate confirmation, and policy retrieval before an eligibility determination. Different valid tool sequences may satisfy the same task.

## Spoken Summary

A reference trajectory describes one expected route. Invariant-based evaluation accepts several routes that preserve required conditions and partial ordering. Use exact sequences only when sequence itself is part of the contract; inspect actual effects and terminal state independently.

## Why

Use exact reference sequences only for required order. Prefer invariants or partial orders when several legitimate trajectories can complete the task without violating scope or approval.

## Production Case

Two agents retrieve evidence in different safe orders. Both should pass if they review before the same authorized write and produce one effect, while a third path that writes before approval must fail.

## Risk

Exact sequence tests can fail harmless reordering; very loose rubrics can miss a missing critical step. Tool names alone also ignore whether arguments or results were correct.

## Trade-off

Reference paths are easy to inspect and brittle under valid variation. Invariants need careful definition and better express safety and business requirements.

## Try This

Evaluate a mixed coverage/status request with two valid call orders, then reject both if the service request lookup lacks the correct owner context.

## Execution Timeline

Define invariants -> Specify partial order -> Add adversarial cases -> Run agent -> Check invariants after full interaction

## Complexity

Simple invariant scans can be linear in trace length with suitable indexed state, while semantic grading, effect queries and model-judge calls add independent cost. Keep the oracle separate from the candidate agent.

## Definitions

- **Partial ordering**: Required sequence constraints that allow valid variations
- **Hard constraint**: Rule that must never be violated, such as review before write
- **Adversarial transition**: Intentional failure scenario to test agent recovery

## Alternatives

- Exact trace matching (too brittle)
- Answer-only evaluation (misses side effects)

## Pitfalls

- Requiring exact tool order
- Missing hard constraints
- Not testing failure recovery

## Follow-ups

### What belongs in a partial-order assertion?

Required dependencies such as approval before dispatch and dispatch before confirmation, while independent read-only steps may vary.

## Example

> Explanation: Check hard constraints regardless of tool sequence variation.
> Output: Pass/fail with constraint details

```python
def evaluate(trajectory):
    assert eligibility_checked(trajectory)  # hard constraint
    assert review_before_write(trajectory)  # hard constraint
    assert no_duplicate_writes(trajectory)  # hard constraint
    return task_success(trajectory)
```

## Citations

- https://langchain-ai.github.io/langgraph/tutorials/introduction/

# What do retrieval-only, context, and end-to-end evaluations measure?

## Answer

Retrieval-only evaluation measures candidate quality. Context evaluation examines the evidence assembled for generation. End-to-end evaluation checks the actual answer, agent actions, and relevant durable outcome. Each localizes a different failure class.

## Why

Record whether an output came from retrieval, context assembly, a baseline, or the live agent. Compare the same path across releases and label synthetic substitutes explicitly.

## Risk

Comparing proxy scores with live-agent scores without checking labels can create a false regression or improvement. Availability fallbacks should never silently change the meaning of the reported metric.

## Trade-off

Offline proxies are cheap and useful for early diagnosis. Actual agent evaluation costs provider calls and measures a different layer.

## Try This

Run or inspect configurations for all modes and assert the reported answer_source. Separate proxy and live results in your report.

# How should a multi-turn request-preparation test be structured?

## Answer

Model the user's progressive facts, corrections, missing fields, preparation, and explicit confirmation boundary. Assert the prepared payload and server effects at each step, not only whether the assistant eventually produces a token.

## Why

Create multi-turn fixtures with missing fields, corrections, stale approvals, cancellation, and repeated submission. Assert both the user interaction and the final business state.

## Risk

A user simulator may accidentally supply hints or accept a fabricated success. Test fixtures should inspect the database and use deterministic assertions for required fields and token state.

## Trade-off

Multi-turn tests take more execution and reveal memory and correction failures absent from isolated prompts. Keep a small high-value regression set alongside larger sampled evaluations.

## Try This

Create a scenario that changes the amount after preparation and attempts the old token. Report both current behavior and the desired contract.

# How should refusal and clarification be evaluated separately?

## Answer

Refusal is appropriate when the task is unsupported or evidence cannot justify an answer. Clarification is appropriate when obtaining missing facts could make the task answerable. Escalation is another outcome requiring truthful operational status.

## Why

Distinguish unavailable evidence, unsupported intent, missing user information, and denied authority. Evaluate whether the response chooses the correct refusal, clarification, or retry behavior.

## Risk

Rewarding all refusals as safe can produce an unusable assistant. Rewarding direct answers to ambiguous eligibility questions can produce unsupported decisions.

## Trade-off

Rich outcome labels cost annotation effort and better match product expectations. A binary correct/incorrect label is simpler and loses diagnostic detail.

## Try This

Label cases as answer, clarify, refuse, retry, or escalate. Require evidence for every final coverage claim and an actual handoff result before claiming transfer.

# How can evaluation verify that writes happened exactly as intended?

## Answer

Assert durable rows, ownership, consumed-token state, lifecycle events, and outbox records after the operation. Repeat and race requests to verify logical uniqueness. Evaluate external deliveries separately from database acceptance.

## Why

Run against disposable services with an effect ledger. Count writes, approvals, owners, and operation keys; a convincing success message cannot replace database assertions.

## Risk

A mocked submit function can return success without exercising SQL locks or commits. A judge of answer text cannot establish atomicity or idempotency.

## Trade-off

Real integration tests are slower and necessary for authoritative effects. Cheap fake-model tests remain useful for routing and error mapping around them.

## Try This

Build a failure-injection table for every write in confirmation. For each failure, assert the visible claim, submission, event, and job state.

# How should a judge be calibrated and protected from the answer being judged?

## Answer

Use a precise rubric, trusted references, known positive and negative cases, and human review to measure agreement. Treat candidate answer and retrieved text as untrusted data in the judge prompt. Record judge model, prompt, and sampling settings.

## Why

Calibrate judges against human-reviewed labels, keep answer text untrusted, and version the rubric and model. Track disagreements and test adversarial scoring instructions.

## Risk

A candidate can contain instructions to the judge, and a judge can favor style over factual support. A second model is not independent truth when it shares the same missing evidence.

## Trade-off

Model judging scales nuanced review and costs money and uncertainty. Deterministic checks should handle exact citations, amounts, permissions, and state transitions where possible.

## Try This

Add a fluent unsupported answer and a judge-injection answer to a calibration set. Compare model verdicts with explicit human labels.

# How do uncertainty intervals and category slices improve evaluation?

## Answer

A score from a small sample is an estimate, not a universal property. Report sample counts, uncertainty, and important categories such as exclusions, limits, corrections, unanswerable questions, and authorization failures. Inspect severity as well as frequency.

## Why

Report sample counts, confidence or uncertainty intervals, and meaningful task slices. Avoid claiming a small aggregate score proves equivalent quality across languages or difficult cases.

## Risk

Repeatedly tuning on the same visible cases overfits the benchmark. Averaging a cross-user disclosure with several harmless formatting errors gives a misleading quality summary.

## Trade-off

Category reporting creates more numbers and reveals actionable regressions. Small categories need cautious interpretation rather than overconfident ranking.

## Try This

Split a benchmark by answerability and category, publish counts, and flag critical failures as release blockers instead of averaging them away.

# How should evaluation control cost and side effects?

## Answer

Separate deterministic unit tests, offline retrieval checks, fake-model trajectories, and opt-in live-agent runs. Use synthetic identities and a sandbox, forbid real irreversible actions, and bound tokens, calls, and total spend. Record which execution mode actually ran.

## Why

Use synthetic identities, isolated data, and sandbox endpoints. Bound judge calls and agent retries, and never let an evaluation trigger real payments or customer notifications.

## Risk

A live agent can prepare records or call real services if its test capabilities are not constrained. Test traces may also export fixtures containing private data.

## Trade-off

Offline checks are fast and less realistic; live runs expose provider behavior and require stronger controls. Use both without conflating their scores.

## Try This

Define a CI budget and a nightly live-evaluation budget with safe tool replacements and explicit answer-source assertions.

# What should an agent release gate require?

## Answer

Require critical authorization and write invariants, non-regression on held-out task outcomes, acceptable latency and cost, and a rollback path. Keep quality thresholds distinct from informational efficiency metrics. A release gate should reflect product harm and operational capacity.

## Why

Predeclare release gates for critical invariants, task quality, latency, and cost. Keep immutable run manifests, reviewed failures, and a rollback artifact for the selected release.

## Risk

A changing judge or proxy fallback can move metrics without a real behavior change. A passing average must never excuse a critical cross-user disclosure or duplicate write.

## Trade-off

Strict gates slow some releases and prevent expensive regressions. Narrow deterministic checks should fail quickly before costly live evaluation.

## Try This

Write a gate with hard denials, category quality thresholds, p95 latency, cost per successful task, and explicit metadata compatibility checks.

# How do you evaluate an agent whose final answer is correct but its action trace violated policy?

<!-- meta
domain: agents
subdomain: agent-evaluation
module: agent-evaluation
concept: How do you evaluate an agent whose final answer is correct but its action trace violated policy?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: An agent returns the requested summary after also reading another tenant’s document that its final answer never cites.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Score final task quality and the action/effect trace separately. Check denied calls, authority, redundant effects, recovery and budget violations with independent oracles. A correct final sentence cannot compensate for private data disclosure or an unauthorized committed action. Freeze fixtures and inspect judge limitations.

Concrete engineering case: An agent returns the requested summary after also reading another tenant’s document that its final answer never cites.

Boundary defense: No. It does not necessarily observe or judge the action trace. Add explicit scope and effect-state checks.

## Spoken Summary

Score final task quality and the action/effect trace separately. Check denied calls, authority, redundant effects, recovery and budget violations with independent oracles. A correct final sentence cannot compensate for private data disclosure or an unauthorized committed action. Freeze fixtures and inspect judge limitations.

## Why

Score final task quality and the action/effect trace separately. Check denied calls, authority, redundant effects, recovery and budget violations with independent oracles. A correct final sentence cannot compensate for private data disclosure or an unauthorized committed action. Freeze fixtures and inspect judge limitations.

## Production Case

An agent returns the requested summary after also reading another tenant’s document that its final answer never cites.

## Risk

An agent returns the requested summary after also reading another tenant’s document that its final answer never cites.

## Trade-off

No. It does not necessarily observe or judge the action trace. Add explicit scope and effect-state checks.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: agent evaluation**: Score final task quality and the action/effect trace separately.

## Alternatives

- No. It does not necessarily observe or judge the action trace. Add explicit scope and effect-state checks.

## Pitfalls

- An agent returns the requested summary after also reading another tenant’s document that its final answer never cites.

## Follow-ups

### Can a final-answer faithfulness metric detect every such violation?

No. It does not necessarily observe or judge the action trace. Add explicit scope and effect-state checks.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "An agent returns the requested summary after also reading another tenant’s document that its final answer never cites.",
  "required_decision": "Score final task quality and the action/effect trace separately"
}
```

## Citations

- https://adk.dev/evaluate/
- https://github.com/google/adk-docs/blob/main/docs/evaluate/criteria.md
- https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf

# How do you prove an agentic or multi-agent design is better than a simpler baseline?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: agent-evaluation
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Freeze the task contract before comparing architectures.** Use the same inputs, permissions, accessible tools and success criteria. Hold out tasks from prompt tuning. Include ordinary successes, ambiguous requests, unavailable tools, adversarial documents, cancellation and tasks that should be refused or escalated. Compare against a deterministic or retrieval-only baseline where it can solve the task.

**Score actual outcomes.** For a code repair, run independent tests and inspect unauthorized changes. For research, check claim support and coverage rather than prose length. For a business action, inspect durable state and duplicate effects. Separate answer quality from process violations: a correct final answer can still have used an unauthorized source.

**Normalize resource comparisons.** Report token/tool budgets, cost per completed task, p50 and p95 latency, cancellation behavior and the proportion requiring human intervention. A multi-agent system allowed ten times the tokens is not an isolated test of architecture. Compare both equal-budget performance and an explicit cost-quality curve. Repeat stochastic runs and report uncertainty rather than celebrating one favorable seed.

**Run ablations.** Remove delegation, reviewer agents, extra searches or memory compression one at a time. If performance stays the same, the removed component may not justify its complexity. Investigate failure clusters, then confirm improvements on a fresh evaluation slice. Use staged release with rollback criteria after offline checks pass.

## Why

A three-agent system raises supported-answer success from 78 to 82 out of 100 tasks but triples cost and exceeds the latency target. Those counts alone do not establish a win; inspect uncertainty, task value and whether a larger single-agent budget achieves the same gain.

## Worked Case

A three-agent system raises supported-answer success from 78 to 82 out of 100 tasks but triples cost and exceeds the latency target. Those counts alone do not establish a win; inspect uncertainty, task value and whether a larger single-agent budget achieves the same gain.

## Risk

An evaluator that rewards verbosity or shares the same unsupported assumptions can favor the more elaborate system unfairly.

## Trade-off

Choose the simplest system that meets the actual quality, risk, cost and latency constraints.

## Try This

Write a comparison table for workflow, single agent and multi-agent designs, including one ablation and independent checks for side effects.

## Citations

- https://www.anthropic.com/research/multi-agent-research-system
- https://www.anthropic.com/research/building-effective-agents

# How do you evaluate abstention without rewarding an assistant that refuses every question?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: agent-evaluation
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Use at least two labeled populations.** Answerable cases test whether the assistant provides correct supported answers. Unanswerable cases test whether it avoids unsupported claims and takes the correct alternative action. Keep refusal, clarification and tool-unavailable outcomes distinct when the product requires different behavior; a generic refusal may be safe but still fail the task.

**State each denominator.** For expected-unanswerable cases, measure correct abstentions divided by the number of such cases. For answerable cases, measure unnecessary abstentions divided by the number of answerable cases. An always-refuse system has perfect abstention on the first population and a 100% false-refusal rate on the second. Aggregate accuracy can conceal this when the dataset is imbalanced.

**Evaluate the answer path as well.** Non-refusal is not success: score correctness, evidence support and unauthorized actions independently. Report coverage, meaning the fraction of requests answered, together with quality among answered requests. Plot a risk-coverage curve when tuning an abstention threshold; a higher threshold can reduce unsupported answers while declining more useful tasks.

**Stratify and stress the gate.** Separate missing evidence, conflicting sources, expired documents, ambiguous user intent and tool outages. Set minimum sample sizes and report uncertainty. A category with no samples is unmeasured, not a perfect score. The example calculates both abstention and false-refusal rates and explicitly handles empty subsets rather than dividing by zero.

## Why

A release set contains 20 answerable and 80 unanswerable questions. An assistant that refuses all 100 looks strong under some aggregate scores, yet fails every opportunity to help on the 20 answerable questions.

## Worked Case

A release set contains 20 answerable and 80 unanswerable questions. An assistant that refuses all 100 looks strong under some aggregate scores, yet fails every opportunity to help on the 20 answerable questions.

## Risk

Scoring only correct refusals creates a perverse incentive to avoid answering. Treating a zero-sized subset as perfect hides missing coverage.

## Trade-off

A stricter threshold can reduce unsupported answers but also reduce useful coverage; select it using actual task risk and measured tradeoffs.

## Try This

Compare always-answer, always-refuse and a calibrated policy. Report subset denominators, supported-answer quality and behavior on an empty evaluation subset.

## Follow-ups

### Can a keyword detector establish correct refusal?

Only for limited fixtures. A response can include refusal words and still make unsupported assertions. Evaluate meaning and downstream actions with independent checks and reviewed samples.

### Is clarification equivalent to refusal?

No. If one missing user fact can make the request answerable, asking for it may be the correct action. Preserve this category in labels and scoring.

## Citations

- https://scikit-learn.org/stable/modules/model_evaluation.html

# How do invariant checks test agents when many trajectories can be valid?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: agent-evaluation
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A task may allow several correct tool sequences, so exact trace matching can reject safe alternatives and reward brittle imitation. Invariants express required properties such as no cross-owner reads, no duplicate accepted effects, bounded work and truthful final status. Pair them with task outcome and evidence checks. Retain traces for diagnosis and compare efficiency separately from correctness. Test denied, ambiguous, cancelled and partially failed paths as well as successful examples, and keep evaluation credentials and fixtures scoped.

## Why

One agent fetches policy before account state and another does the reverse. Both can be correct if authorization holds, necessary evidence is available and no effect occurs before required approval.

## Worked Case

One agent fetches policy before account state and another does the reverse. Both can be correct if authorization holds, necessary evidence is available and no effect occurs before required approval.

## Risk

A reference trace can encode incidental order as a false correctness requirement.

## Trade-off

Use invariants for safety and outcomes while reviewing trajectories for causal diagnosis.

## Try This

Write checks accepting two valid traces and rejecting one unauthorized shortcut.

## Citations

- https://adk.dev/evaluate/
- https://github.com/google/adk-docs/blob/main/docs/evaluate/criteria.md
- https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
