<!-- chapter: portfolio-capstone -->

# What should a complete capstone include?

<!-- meta
domain: system-design
subdomain: capstone
module: portfolio-capstone
concept: What should a complete capstone include
difficulty: implementation
misconception_target: A capstone is just a working demo
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Build one scoped assistant with a UI, authenticated API, retrieval, a limited agent, durable business operations, evaluation, tracing, and recovery. Add voice or document AI only when the use case needs it.

## Spoken Summary

A strong capstone includes a scoped use case, requirements and threat model, reproducible setup, tested code, versioned data/evaluation, architecture decisions and demonstrated failure recovery. Separate implemented behavior from proposals and leave a clear list of known limitations.

## Why

Define a small set of useful tasks and publish synthetic fixtures, architecture decisions, and a reproducible local setup.

## Production Case

Another engineer starts from a clean environment, reproduces an unauthorized-access negative case and a lost-ack retry, inspects durable effects and reads the measured quality/latency trade-offs.

## Risk

Adding many features can hide weak core guarantees.

## Trade-off

Narrow scope is easier to evaluate and may look less broad.

## Try This

Choose three user journeys and one explicit out-of-scope request before coding.

## Execution Timeline

Plan phases -> Build local deterministic slice -> Add persistence -> Add evaluation -> Add deployment -> Document -> Review with second person

## Complexity

Estimate development and runtime resources from concrete workload and delivery requirements. Counting project phases is not a meaningful algorithmic complexity analysis.

## Definitions

- **Synthetic fixtures**: Test data that simulates real data without using actual user data
- **Evaluation report**: Documented quality metrics for the built system
- **Implemented vs proposed**: Honest distinction between built and planned features

## Alternatives

- Simple demo without documentation
- Project without failure handling

## Pitfalls

- No synthetic fixtures
- No evaluation report
- No failure demo
- Not runnable from clean environment

## Follow-ups

### What makes a capstone stronger than a polished chat demo?

Independent evidence of correctness, permissions and recovery under failure, plus an explanation of assumptions and trade-offs.

## Example

> Explanation: Four-phase capstone delivery plan.
> Output: Complete capstone project

```python
# Phase 1: Local deterministic slice\n# Phase 2: Persistent authenticated workflow\n# Phase 3: Evaluated retrieval/generation\n# Phase 4: Release with recovery evidence
```

## Citations

- https://sre.google/sre-book/

# How should the learning journey be sequenced?

## Answer

Learn backend and data fundamentals, retrieval and evidence, agent tool use, context and prompts, durable orchestration, evaluation, then multimodal and live delivery. Revisit earlier layers as failures emerge.

## Why

Build a working increment at each stage and defend its design trade-offs. The roadmap is a dependency path, not a fixed calendar guarantee.

## Risk

Reading all chapters without implementing leaves integration gaps undiscovered.

## Trade-off

Incremental projects take more setup and produce stronger understanding.

## Try This

Map each chapter to one artifact or demonstrated behavior.

# What should a public portfolio say about AI assistance?

## Answer

Explain your role in design, implementation, review, and validation, including where AI helped. Claims of competence should be supported by decisions and working evidence.

## Why

Publish a short engineering log describing a failure you found, how you diagnosed it, and how you verified the fix.

## Risk

Presenting generated explanations as verified production results undermines trust.

## Trade-off

Transparency may reveal limits and makes your work easier to assess.

## Try This

Write a project description separating demonstrated behavior from planned extensions.

# How should project documentation be structured?

## Answer

Lead with the user problem, supported tasks, architecture, setup, operating constraints, evaluation results, and known limitations. Link deeper explanations from this overview.

## Why

Keep commands reproducible with synthetic data and clearly scoped dependency versions. Show one success and one failure walkthrough.

## Risk

A large README without a runnable path can make a strong project hard to assess.

## Trade-off

Concise onboarding requires separate detail pages and improves accessibility.

## Try This

Ask a new reader to run one task without verbal guidance.

# Which measurements belong in a portfolio report?

## Answer

Report task completion, unsupported-answer rate, authorization invariants, recovery outcomes, p95 latency, and cost under a described workload. Include dataset size and environment.

## Why

Distinguish measured numbers from targets and estimates. Retain configuration and release IDs so a comparison can be reproduced.

## Risk

Benchmark claims without task mix or hardware context are difficult to interpret.

## Trade-off

Honest limitations may look less impressive and provide credible evidence.

## Try This

Publish a small result table with a baseline, one improvement, and one regression.

# How should an architecture decision record be written?

## Answer

Describe the concrete problem, constraints, considered options, chosen approach, consequences, and conditions that would trigger reconsideration. Keep it tied to evidence.

## Why

For example, justify SSE over WebSockets through message direction and reconnect needs rather than popularity.

## Risk

A retrospective justification can conceal alternatives that were never evaluated.

## Trade-off

Decision records cost time and preserve engineering context.

## Try This

Write one record for transaction ownership and one for agent orchestration.

# How should a capstone release be secured?

## Answer

Remove secrets and customer data, constrain tools and outbound access, validate identity and ownership, and isolate evaluation side effects. Include dependency and artifact provenance.

## Why

Use a reviewed deployment manifest and a rollback path. Keep administrative actions separate from ordinary agent capabilities.

## Risk

A public demo can expose backend endpoints even if the repository is private.

## Trade-off

Hardened deployment adds friction and supports credible public access.

## Try This

Threat-model the demo as an anonymous user and an authenticated malicious user.

# How should interviews use the roadmap?

## Answer

Explain a complete journey, then zoom into one failure boundary and defend a trade-off. Use diagrams and actual measurements to distinguish understanding from terminology recall.

## Why

Practice concise answers first, then expand into transaction scope, context design, permissions, and evaluation when asked.

## Risk

Memorized framework definitions do not demonstrate reasoning under changed constraints.

## Trade-off

Deep specialization reduces breadth and produces stronger technical discussions.

## Try This

Answer how your design changes when traffic grows tenfold or a provider fails.

# What should completion of a chapter mean?

## Answer

You can explain the mechanism, implement a small example, reproduce a relevant failure, and justify a trade-off. A learned checkbox is a personal study signal.

## Why

Use the chapter lab acceptance criteria and write your own explanation before revealing the detailed answer.

## Risk

Marking everything complete without independent work gives misleading progress.

## Trade-off

Higher standards slow apparent progress and deepen practical competence.

## Try This

Revisit one learned topic and solve its exercise without viewing the answer.

# How should the roadmap continue after the capstone?

## Answer

Choose a real weakness revealed by evaluation: retrieval quality, multilingual behavior, privacy, latency, model serving, accessibility, or operational recovery. Deepen that area with a controlled experiment.

## Why

Keep a baseline and compare one intervention at a time. Add a new framework only when it solves a defined problem.

## Risk

Collecting technologies can fragment the system without improving user outcomes.

## Trade-off

Focused depth limits feature count and builds durable engineering judgment.

## Try This

Propose your next experiment with a hypothesis, dataset, metric, budget, and stopping rule.

# What evidence distinguishes an independently built AI capstone from a copied happy-path demo?

<!-- meta
domain: system-design
subdomain: portfolio-capstone
module: portfolio-capstone
concept: What evidence distinguishes an independently built AI capstone from a copied happy-path demo?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A demo works once but cannot explain a missing final stream event, cross-owner cache hit or replay after receiver commit.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Require a clean-start build, explicit scope and threat model, artifact identities, independent fixtures, reproduced failures and durable-state checks. Ask the learner to diagnose an unfamiliar changed assumption and show a regression that fails on the defect. Reading a reference or reporting a self-rating is not equivalent evidence.

Concrete engineering case: A demo works once but cannot explain a missing final stream event, cross-owner cache hit or replay after receiver commit.

Boundary defense: Mark the scope and evidence honestly, require an extension when acceptance needs it, and avoid inventing a pass from a diagram or checklist alone.

## Spoken Summary

Require a clean-start build, explicit scope and threat model, artifact identities, independent fixtures, reproduced failures and durable-state checks. Ask the learner to diagnose an unfamiliar changed assumption and show a regression that fails on the defect. Reading a reference or reporting a self-rating is not equivalent evidence.

## Why

Require a clean-start build, explicit scope and threat model, artifact identities, independent fixtures, reproduced failures and durable-state checks. Ask the learner to diagnose an unfamiliar changed assumption and show a regression that fails on the defect. Reading a reference or reporting a self-rating is not equivalent evidence.

## Production Case

A demo works once but cannot explain a missing final stream event, cross-owner cache hit or replay after receiver commit.

## Risk

A demo works once but cannot explain a missing final stream event, cross-owner cache hit or replay after receiver commit.

## Trade-off

Mark the scope and evidence honestly, require an extension when acceptance needs it, and avoid inventing a pass from a diagram or checklist alone.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: portfolio capstone**: Require a clean-start build, explicit scope and threat model, artifact identities, independent fixtures, reproduced failures and durable-state checks.

## Alternatives

- Mark the scope and evidence honestly, require an extension when acceptance needs it, and avoid inventing a pass from a diagram or checklist alone.

## Pitfalls

- A demo works once but cannot explain a missing final stream event, cross-owner cache hit or replay after receiver commit.

## Follow-ups

### How should a reviewer score a boundary the reference does not implement?

Mark the scope and evidence honestly, require an extension when acceptance needs it, and avoid inventing a pass from a diagram or checklist alone.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A demo works once but cannot explain a missing final stream event, cross-owner cache hit or replay after receiver commit.",
  "required_decision": "Require a clean-start build, explicit scope and threat model, artifact identities, independent fixtures, reproduced failures and durable-state checks"
}
```

## Citations

- https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control
- https://developer.mozilla.org/en-US/curriculum/core/

# How should an interview portfolio distinguish implemented behavior, measured evidence and remaining assumptions?

<!-- meta
answer_format: conceptual
domain: system-design
subdomain: portfolio-capstone
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Present a concrete user problem, system boundaries, a runnable path and observed failure/recovery behavior. Link claims to reproducible commands, source versions and results under stated conditions. Distinguish a local fixture from an authenticated integration, a single-worker test from distributed recovery and an automated accessibility scan from human approval. Explain a decision you changed after evidence contradicted it. A strong portfolio helps an interviewer inspect reasoning and limits, rather than requiring belief in a broad 'production ready' label.

## Why

A local Kafka replay test can demonstrate one commit-before-ack failure boundary. It does not establish multi-broker availability or rebalance correctness unless those conditions were also executed and recorded.

## Worked Case

A local Kafka replay test can demonstrate one commit-before-ack failure boundary. It does not establish multi-broker availability or rebalance correctness unless those conditions were also executed and recorded.

## Risk

Overstated claims make genuine implementation evidence harder to trust.

## Trade-off

A scoped, reproducible result is more defensible than an unsupported coverage checklist.

## Try This

Prepare a five-minute demo with normal behavior, one injected failure and an honest evidence ledger.

## Citations

- https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control
- https://developer.mozilla.org/en-US/curriculum/core/
