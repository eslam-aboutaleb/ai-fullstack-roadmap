<!-- chapter: evaluation-engineering -->

# Why does an agent need evaluation even when its answers look good?

<!-- meta
domain: operations
subdomain: evaluation-engineering
module: evaluation-engineering
concept: Why does an agent need evaluation even when its answers look good
difficulty: implementation
misconception_target: One dataset serves all evaluation purposes
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

An agent can write convincing text while choosing the wrong tool, exposing data, repeating a transaction, or failing to finish. Evaluation checks outcomes and the process that produced them.

## Spoken Summary

An agent can give a good-looking answer after unsafe or unnecessary actions. Evaluate task outcomes, permission and ordering invariants, effect state, latency and spend. Partition development and held-out cases, calibrate semantic judges and inspect failures by slice.

## Why

Define task success and forbidden effects before implementation. Combine deterministic assertions, human review, and calibrated model judging where appropriate.

## Production Case

A prompt change improves a judge score but doubles tool calls and occasionally skips approval. The release must fail the hard trajectory invariant and report the cost regression independently.

## Risk

A style-only score can reward unsafe behavior.

## Trade-off

Broad evaluation costs effort and prevents expensive hidden failures.

## Try This

Create a fluent answer paired with a duplicate write and ensure it fails the suite.

## Execution Timeline

Collect data -> Split into train/validation/test -> Develop on validation -> Calibrate judges -> Final evaluation on test set

## Complexity

Track dataset size, query/model attempts, judged token volume and reviewer effort. Deterministic checks and model-based semantic evaluation have different cost and variance profiles.

## Definitions

- **Train/validation/test split**: Separate datasets for development, tuning, and final evaluation
- **Judge calibration**: Aligning LLM judges with human ratings
- **Overfitting to test set**: Tuning hyperparameters based on test set performance

## Alternatives

- Single dataset for all purposes
- No judge calibration

## Pitfalls

- No train/validation/test split
- Uncalibrated LLM judges
- Evaluating on training data

## Follow-ups

### Can you tune prompts repeatedly on the final test set?

Doing so turns it into development data. Preserve a fresh holdout and report what was used for selection.

## Example

> Explanation: Split data, calibrate judge on validation, evaluate on test.
> Output: Evaluation results on held-out test set

```python
train, val, test = split_dataset(data, [0.7, 0.15, 0.15])
calibrated_judge = calibrate_judge(llm_judge, human_ratings, val)
results = calibrated_judge.evaluate(test)
```

## Citations

- https://arxiv.org/abs/2303.16634

# How should evaluation datasets be partitioned?

## Answer

Separate development examples, prompt-tuning data, held-out release cases, and ongoing production monitoring samples. Keep adversarial and regression sets visible as distinct categories.

## Why

Track provenance and versioning, prevent duplicate leakage across splits, and retain hard cases after fixes.

## Risk

Repeatedly tuning against the release set turns it into training data.

## Trade-off

Larger held-out sets improve confidence and cost more to curate.

## Try This

Deduplicate a dataset by task template and source document, not only exact text.

# What is the difference between outcome and trajectory evaluation?

## Answer

Outcome evaluation checks the final answer or durable business result. Trajectory evaluation checks tool choices, arguments, ordering constraints, permissions, and recovery behavior along the way.

## Why

Use invariants when multiple sequences are valid. Reserve exact sequence matching for workflows whose order is actually required.

## Risk

A correct final record may hide an unauthorized read that happened earlier.

## Trade-off

Trajectory checks improve diagnosis and require richer event capture.

## Try This

Accept two valid search sequences but reject either if it crosses a tenant boundary.

# How should model judges be calibrated?

## Answer

Compare judge labels with reviewed human labels across representative failures. Measure agreement, systematic bias, and sensitivity to irrelevant wording before trusting the score.

## Why

Use an explicit rubric and structured reasons, randomize answer order, and keep judged content untrusted. Recalibrate after judge changes.

## Risk

A judge can favor its own style or follow injected scoring instructions.

## Trade-off

Human calibration is costly and anchors automation.

## Try This

Build a disagreement table and revise the rubric before increasing judge volume.

# How do Ragas, DeepEval, and Promptfoo fit different needs?

## Answer

Ragas provides RAG-oriented evaluation components, DeepEval supplies model-testing abstractions and metrics, and Promptfoo supports configuration-driven comparisons and assertions. Their metrics and defaults are not interchangeable.

## Why

Choose the library that fits your workflow, inputs, privacy requirements, and required assertions. Pin a compatible version and document your judge configuration.

## Risk

A library name or metric label does not establish measurement validity.

## Trade-off

Multiple tools can fill gaps and duplicate infrastructure.

## Try This

Run the same small dataset through two tools and explain score differences from their contracts.

# How do tracing platforms support evaluation?

## Answer

Traces reveal actual inputs, tools, timing, and outcomes so evaluation failures can be diagnosed. Platforms such as LangSmith, Phoenix, and TruLens connect observation with experiment or feedback workflows in different ways.

## Why

Capture safe trace identifiers and attach evaluation labels to immutable run versions. Evaluate retention and data export policies before sending payloads.

## Risk

Rich traces can leak private user or document content.

## Trade-off

Hosted workflows simplify collaboration and add privacy and cost decisions.

## Try This

Diagnose one failed task using metadata-only traces and identify what additional redacted evidence is necessary.

# How should performance and quality be reported together?

## Answer

Report completion, unsupported-answer rate, policy violations, p50 and p95 latency, and total cost per completed task. Include sample sizes and uncertainty rather than one blended score.

## Why

Use paired fixtures when comparing releases and segment by task difficulty and user context. Count retries and failed tasks in cost.

## Risk

Average latency can hide severe tail delays or one vulnerable subgroup.

## Trade-off

Multi-dimensional reporting is harder to summarize and supports honest trade-offs.

## Try This

Build a comparison table where one variant is cheaper but fails more difficult tasks.

# How should side-effecting agents be evaluated safely?

## Answer

Use sandbox services, synthetic users, isolated databases, and explicit effect ledgers. Assert that only permitted writes occur and reset fixtures between runs.

## Why

Separate replayed model decisions from live provider experiments. Never point a benchmark at real payment or notification systems.

## Risk

A mocked success response can conceal real transaction or concurrency failures.

## Trade-off

Realistic isolated tests require infrastructure and establish stronger behavior evidence.

## Try This

Race two confirmation requests against a disposable database and count durable records.

# How should online feedback differ from offline evaluation?

## Answer

Online feedback reflects real user experience but is selective and often incomplete. Offline evaluation provides controlled repeatability but may miss new task distributions. Use both.

## Why

Review sampled failures, add approved examples to datasets, and monitor changes in task mix and rejection rates.

## Risk

Positive feedback is not proof of factual correctness or privacy compliance.

## Trade-off

Production learning improves relevance and requires careful data governance.

## Try This

Define a process for converting a redacted support incident into a reproducible test fixture.

# What should block an agent release?

## Answer

Block on breached safety invariants, unacceptable task failure, degraded recovery, or a measured performance regression beyond the agreed threshold. Define these gates before seeing results.

## Why

Require immutable release manifests and a rollback path. Distinguish critical deterministic failures from noisy judge-score fluctuations.

## Risk

Choosing a threshold after evaluation invites cherry-picking.

## Trade-off

Strict gates slow release and protect known obligations.

## Try This

Write a release policy with one absolute invariant, one statistical quality target, and one latency budget.

# How do you evaluate an inferred proficiency or category without treating a heuristic label as a calibrated probability?

<!-- meta
answer_format: conceptual
domain: data-integrity
subdomain: evaluation-engineering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Define the target before collecting labels.** Years of experience, job title and demonstrated proficiency are related but different quantities. A rule that maps seven years to expert is an explicit heuristic, not a validated measurement of skill. Establish what outcome the label is supposed to predict and how reviewers can independently assess it.

**Separate ranking, classification and confidence.** A system may rank plausible categories without having calibrated probabilities. If it emits a confidence score, evaluate whether predictions near that score are correct at the corresponding frequency on held-out data. A self-reported certainty string does not supply that evidence. Label uncertainty and disagreement may limit the precision of any calibration claim.

**Measure selective performance.** Report the number of accepted predictions, accuracy or task-specific error among those predictions, and the fraction abstained. Set thresholds on a validation split and measure the frozen rule on a test split. Reject empty accepted subsets as unmeasured rather than calling them perfect. Inspect slices such as language, source format, missing context and ambiguous short terms where appropriate to the task.

**Keep consequential decisions reviewable.** An inferred label should carry provenance, rule/model version and a correction path. Do not confuse profile completeness with competence, or seniority with authorization to perform a task. The local example computes selective accuracy and coverage for synthetic labeled cases; its numeric score is a fixture rather than evidence that any real model is calibrated.

## Why

A classifier accepts two high-confidence cases and abstains on one ambiguous case. Reporting only its accuracy hides the lost coverage; reporting only coverage hides whether the accepted labels were correct.

## Worked Case

A classifier accepts two high-confidence cases and abstains on one ambiguous case. Reporting only its accuracy hides the lost coverage; reporting only coverage hides whether the accepted labels were correct.

## Risk

An unvalidated heuristic can look objective once it is serialized as a numeric score and reused downstream.

## Trade-off

Abstention improves accepted-case quality only if evaluated; aggressive abstention can make a system unhelpful.

## Try This

Compare title-based, years-based and evidence-based labels against independently reviewed cases. Report disagreement, coverage and error rather than assuming one proxy is ground truth.

## Follow-ups

### Is a years-of-experience field useless?

No. It may be a relevant observed feature when accurately collected, but it is not interchangeable with demonstrated proficiency. Evaluate its contribution and preserve the difference between feature and target.

### Can user corrections go straight into a test set?

Use a reviewed labeling and split policy. Corrections may be noisy or selected from difficult cases, and reusing tuning feedback as held-out evaluation can inflate results.

## Citations

- https://scikit-learn.org/stable/modules/model_evaluation.html

# What makes an evaluation set invalid after repeated prompt and model selection?

<!-- meta
domain: operations
subdomain: evaluation-engineering
module: evaluation-engineering
concept: What makes an evaluation set invalid after repeated prompt and model selection?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A team tries dozens of prompts against the same published test questions and reports the maximum as unbiased progress.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

If the team repeatedly inspects its outcomes and changes the system accordingly, it has become selection data. Keep decision-making in validation and reserve an appropriately sampled holdout for the frozen candidate. Preserve case provenance, group structure and label adjudication, then report uncertainty under the sampling design.

Concrete engineering case: A team tries dozens of prompts against the same published test questions and reports the maximum as unbiased progress.

Boundary defense: No. Keep regression cases for known defects while distinguishing them from a fresh generalization estimate and recording the selection history.

## Spoken Summary

If the team repeatedly inspects its outcomes and changes the system accordingly, it has become selection data. Keep decision-making in validation and reserve an appropriately sampled holdout for the frozen candidate. Preserve case provenance, group structure and label adjudication, then report uncertainty under the sampling design.

## Why

If the team repeatedly inspects its outcomes and changes the system accordingly, it has become selection data. Keep decision-making in validation and reserve an appropriately sampled holdout for the frozen candidate. Preserve case provenance, group structure and label adjudication, then report uncertainty under the sampling design.

## Production Case

A team tries dozens of prompts against the same published test questions and reports the maximum as unbiased progress.

## Risk

A team tries dozens of prompts against the same published test questions and reports the maximum as unbiased progress.

## Trade-off

No. Keep regression cases for known defects while distinguishing them from a fresh generalization estimate and recording the selection history.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: evaluation engineering**: If the team repeatedly inspects its outcomes and changes the system accordingly, it has become selection data.

## Alternatives

- No. Keep regression cases for known defects while distinguishing them from a fresh generalization estimate and recording the selection history.

## Pitfalls

- A team tries dozens of prompts against the same published test questions and reports the maximum as unbiased progress.

## Follow-ups

### Should it discard every older regression case?

No. Keep regression cases for known defects while distinguishing them from a fresh generalization estimate and recording the selection history.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A team tries dozens of prompts against the same published test questions and reports the maximum as unbiased progress.",
  "required_decision": "If the team repeatedly inspects its outcomes and changes the system accordingly, it has become selection data"
}
```

## Citations

- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/common_pitfalls.html

# How do you prevent a deterministic evaluation proxy from being reported as live agent quality?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: evaluation-engineering
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Label what produced the evaluated answer.** Retrieval-only scoring, a deterministic answer stub, a context-only generator and a full agent trajectory measure different systems. Store the execution mode and answer source in every result alongside dataset version, configuration, code revision and tool access. A familiar metric name does not make these modes interchangeable.

**Gate only claims the run can support.** A retrieval fixture can verify whether required evidence was surfaced. It cannot establish that a live agent cites it correctly, uses tools safely or stops under uncertainty. A deterministic refusal stub can test evaluator wiring without proving that the deployed model refuses the same inputs. Live runs need explicit provider/model identities and independent checks on actual outputs and effects.

**Protect evaluation against accidental shortcuts.** Keep ground-truth answers and expected labels outside the model input. Pin the dataset split and distinguish tuning data from a held-out release set. A gate should reject a mode mismatch rather than silently accept whichever artifact happens to have a high score. Missing provenance is a failed validation, not a default live mode.

**Report comparable results.** Compare runs with compatible datasets, budgets, tool environments and scoring rules. Track stochastic variation over repeated live runs and preserve failed trajectories. A fast offline proxy remains useful for development feedback, but its report must state its narrower scope. The executable check below rejects a high proxy score when the release gate requires live-agent evidence.

## Why

A deterministic context proxy scores 0.98 and a live agent scores 0.84. Reporting the proxy as the deployed assistant's quality hides tool selection, provider failures and unsupported claims that only the live run can expose.

## Worked Case

A deterministic context proxy scores 0.98 and a live agent scores 0.84. Reporting the proxy as the deployed assistant's quality hides tool selection, provider failures and unsupported claims that only the live run can expose.

## Risk

An excellent score from the wrong execution mode can approve a release without testing the product behavior.

## Trade-off

Offline fixtures are cheap and reproducible; live evaluation adds realism, cost and variance. Use both with distinct gates.

## Try This

Create a report with a deliberately mislabeled answer source and verify that the release gate rejects it even when every numeric score passes.

## Follow-ups

### Can a live label alone prove the run was live?

No. Preserve execution records and enforce mode selection in the runner. A metadata validator checks consistency, while trusted run provenance establishes where the artifact came from.

### Should the live gate replace deterministic tests?

No. Deterministic checks catch contracts cheaply; live checks address model and integration behavior. A useful pipeline keeps their evidence and failure meanings distinct.

## Citations

- https://scikit-learn.org/stable/modules/model_evaluation.html

# How should an LLM judge be calibrated and protected against evaluation leakage?

<!-- meta
answer_format: conceptual
domain: operations
subdomain: evaluation-engineering
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A model judge implements a fallible measurement procedure. Define a rubric with concrete anchors, compare its judgments against qualified human review and inspect disagreement by important slice. The judge can be sensitive to wording, answer order, verbosity and adversarial instructions inside the evaluated content. Keep reference labels and held-out cases out of the tested system's tuning path. Version the judge model, prompt and parsing policy, and report uncertainty instead of treating an unexplained numeric score as objective truth.

## Why

A verbose unsupported answer can receive a higher helpfulness score than a concise supported answer if the rubric rewards style indirectly. Human-reviewed counterexamples reveal the mismatch between the judge and the intended standard.

## Worked Case

A verbose unsupported answer can receive a higher helpfulness score than a concise supported answer if the rubric rewards style indirectly. Human-reviewed counterexamples reveal the mismatch between the judge and the intended standard.

## Risk

Optimizing directly against one judge can overfit its preferences.

## Trade-off

Automated judges scale review but need calibration, sampling and explicit limitations.

## Try This

Blindly review judge disagreements and refine the rubric before using it as a release gate.

## Citations

- https://scikit-learn.org/stable/modules/cross_validation.html
- https://scikit-learn.org/stable/common_pitfalls.html
