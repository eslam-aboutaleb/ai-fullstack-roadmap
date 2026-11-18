<!-- chapter: evaluation-libraries -->

# How do you choose an evaluation library without turning the stack into a collection of dashboards?

## Answer

Start from the question to measure: retrieval relevance, grounded answers, tool trajectories, task completion, adversarial behavior, or production drift. Choose one durable experiment record and connect additional metrics only where they add diagnostic value.

## Why

Choose tools by the question they can measure, required input data, workflow fit, privacy, and cost. A growing collection of dashboards is not an evaluation strategy.

## Risk

Different tools may use the same metric name for different inputs, judges, and aggregation rules. Comparing their numeric outputs without recording definitions is invalid.

## Trade-off

One harness is easier to operate; specialized libraries can deepen particular checks. Prefer a small adapter around a shared dataset and result schema.

## Try This

Create a selection matrix for ADK evaluation, LangSmith, Ragas, DeepEval, TruLens, Phoenix, and Promptfoo. State one justified use and one limitation for each.

# What does ADK evaluation add for this example ADK agent?

<!-- meta
reference: https://github.com/google/adk-docs/blob/main/docs/evaluate/criteria.md
-->

## Answer

ADK evaluation can test tool-use trajectories and final responses using reference or rubric-based criteria. Its fit is strongest when you want evaluation close to the runtime's sessions and events, including reviewed multi-turn cases.

## Why

Use compatible ADK evaluation interfaces for agent-specific criteria where they fit the runtime. Verify which criteria actually ran and retain application-level transaction and authorization tests separately.

## Risk

Exact trajectory matching can reject valid alternative orders, and judge-based criteria add model dependencies and cost. Some criteria require additional services; the dependency's broad lower bound does not guarantee every current documentation feature exists locally.

## Trade-off

Runtime-native evaluation reduces event translation and may couple fixtures to the framework. A framework-neutral contract suite survives migration more easily.

## Try This

Define one exact confirmation-preparation trajectory and one rubric for flexible coverage review. Pin versions before running the documented criterion configuration.

# What is LangSmith evaluation useful for if the agent uses ADK?

<!-- meta
reference: https://docs.langchain.com/langsmith/evaluation
-->

## Answer

LangSmith supports datasets, experiments, evaluators, and review workflows that need not require LangChain as the agent runtime. The application can submit its own target function and measured outputs while retaining ADK execution.

## Why

Use dataset, experiment, and trace workflows independently of a particular orchestrator where supported. Integrate through a narrow adapter and review what payloads leave the application.

## Risk

Uploading examples, outputs, or traces can disclose claim data. Experiment identity must distinguish model output from an offline context proxy and preserve prompt, corpus, and evaluator revisions.

## Trade-off

A shared experiment service improves collaboration and adds data-governance and service-dependency considerations. Local JSON reports are easier to keep isolated and less convenient for team review.

## Try This

Design a target function returning answer, evidence IDs, tool trace, and answer_source for one synthetic case. Specify which fields may be exported.

# How does Ragas help evaluate retrieval-augmented answers?

<!-- meta
reference: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/
-->

## Answer

Ragas provides metrics for relationships among questions, retrieved contexts, answers, and references. Faithfulness asks whether answer service requests are supported by context; other metrics address relevance and retrieval behavior. Each metric has required inputs and may use a model judge.

## Why

Match each Ragas metric to its required context, answer, reference, and judge inputs. Pin the implementation and do not assume every metric is reference-free or comparable across versions.

## Risk

Faithfulness to the wrong rule revision can still score well. Missing references, synthetic contexts, and judge changes can alter meaning or cost.

## Trade-off

Specialized RAG diagnostics help isolate failure layers and do not establish authorization, exact-money calculations, or correct claim writes. Keep those deterministic tests separate.

## Try This

Compare an answer faithful to stale evidence with an answer correct for the active policy. Explain why both evidence applicability and faithfulness must be evaluated.

# How does DeepEval fit into a pytest-oriented workflow?

<!-- meta
reference: https://deepeval.com/docs/metrics-faithfulness
-->

## Answer

DeepEval provides test-case and metric abstractions for language-model systems, including faithfulness evaluation over retrieval context. It can make selected behavioral quality checks part of an existing test workflow while still depending on judge configuration for relevant metrics.

## Why

Represent a task with the required test-case fields and choose a DeepEval metric suited to the rubric. Record judge configuration and retain deterministic business-invariant checks alongside it.

## Risk

A unit-test appearance can conceal network calls, nondeterminism, and cost. A passing metric does not prove server-side authorization or transaction atomicity.

## Trade-off

Developer-friendly tests improve feedback locality; broad judge-heavy CI can become slow and flaky. Run exact contract tests frequently and sampled model judging under a controlled budget.

## Try This

Add one faithful and one unsupported answer to an optional evaluation suite, pin the judge configuration, and record raw verdicts alongside thresholds.

# What does the TruLens RAG triad measure?

<!-- meta
reference: https://www.trulens.org/getting_started/core_concepts/rag_triad/
-->

## Answer

The RAG triad distinguishes context relevance, groundedness of the response in context, and answer relevance to the question. Separating these relationships helps identify whether retrieval or generation deserves investigation.

## Why

Treat context relevance, groundedness, and answer relevance as distinct questions. Define feedback inputs and calibrate scores before using any RAG triad as a release decision.

## Risk

Good triad scores do not establish that the policy applies to this user or that a submitted claim exists. Domain and permission checks remain outside those semantic relationships.

## Trade-off

Structured feedback improves diagnosis while adding instrumentation and evaluator configuration. Use it when the team will act on the distinctions rather than only collect more scores.

## Try This

Create three failures: irrelevant context, unsupported answer, and grounded but off-topic answer. Map each to the relationship that should fail.

# How can Phoenix combine tracing and evaluation?

<!-- meta
reference: https://arize.com/docs/phoenix
-->

## Answer

Phoenix supports inspecting model-system traces and evaluating behavior using recorded inputs and outputs. It can help connect a quality failure to a particular retrieval, tool, or model span. It is a proposed observability/evaluation alternative here, not an existing backend integration.

## Why

Use safe trace recording to connect failures with evaluation feedback. Review deployment, exporters, retention, and dataset identity rather than adopting a platform for its interface alone.

## Risk

Automatic instrumentation may capture sensitive arguments or create duplicate spans alongside LangSmith. Local hosting alone does not guarantee safe access control or retention.

## Trade-off

Correlated traces and evaluation improve diagnosis but require export policy, span conventions, and service operation. One well-configured backend is often enough.

## Try This

Define the minimum trace fields needed to explain a wrong policy answer, then compare that allowlist with an automatic export's actual payload.

# Where does Promptfoo fit compared with a Python evaluation harness?

<!-- meta
reference: https://www.promptfoo.dev/docs/configuration/expected-outputs/
-->

## Answer

Promptfoo provides configuration-driven evaluations and assertions over model or application outputs, useful for comparing prompts, providers, and adversarial cases. A Python harness is often more natural for inspecting internal service and database state.

## Why

Use configuration-driven providers and assertions for repeatable comparisons. Separate deterministic schema or policy checks from model-judged language criteria and control live side effects.

## Risk

A contains assertion can pass on quoted or negated text, and a model-graded assertion still depends on judge quality. End-to-end outputs alone cannot reveal every unsafe intermediate tool call.

## Trade-off

Declarative matrices make broad experiments convenient; custom Python gives finer control over stateful workflows and failure injection.

## Try This

Define deterministic assertions for an empty result and missing confirmation, then add a reviewed rubric for coverage faithfulness. Explain which checks need backend instrumentation.

# How do you make evaluation results comparable across libraries?

<!-- meta
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Define a shared evaluation contract before choosing a platform.** Every tool must receive the same immutable case IDs, dataset split, user/tenant constraints, expected source IDs, answer/reference rubric, model configuration and policy version. Persist the run ID, trace ID, prompt/model/index fingerprints, metric definitions, scorer revision, outcomes and reason for each failure. If tools see different golden cases, averages cannot be compared, regardless of how polished the dashboards look.

**Separate metrics by the layer they measure.** Retrieval recall@k asks whether gold evidence appears among eligible candidates. Citation precision asks whether cited passages actually support the answer. A grounded answer can still refuse an answerable case (false refusal), and high retrieval recall does not guarantee safe tool decisions. Latency, tokens, provider errors, unsupported answers and owner-scope violations need distinct fields. Report per-slice results and sample counts; do not average incomparable rubric scales.

**Calibrate model judges.** A language-model judge is itself a stochastic, potentially biased model. Label a representative adjudicated set with humans, run the judge on exactly the same examples, compute TP/TN/FP/FN, inspect prompt sensitivity and discordant slices, and maintain a holdout not used for prompt tuning. Agreement is not a correctness proof: two judges can share the same failure. Human adjudication is required for ambiguous or high-severity decisions.

**Worked regression.** A candidate retriever improves overall mean recall but loses the only eligible citation for a high-risk question. A release gate must reject this specific regression despite the higher average. The local `labs/eval_platform_contract.py` pairs baseline/candidate runs by case ID, records trace IDs, checks unsupported answers and prevents a previously perfect retrieval case from silently regressing; it has no real LangSmith/Langfuse/Phoenix/DeepEval/Ragas/Promptfoo network calls.

**Cross-platform engineering.** LangSmith/Langfuse/Phoenix commonly center traces and annotated datasets; Ragas and DeepEval provide evaluator abstractions and metric workflows; Promptfoo supports prompt/config/test matrices. Each vendor has version-sensitive semantics, export and retention behavior, cost/tracing privacy trade-offs. Keep a portable canonical run record, then build optional pinned adapters and verify the actual emitted trace/evaluation results. Do not claim tool interoperability from a mock.

**Follow-up.** If the judge labels 20% of the ground-truth supported answers unsupported, inspect the false-negative slice and revise rubric/adjudication, then rerun on a sealed test set. A numerical threshold without judge calibration is a fragile release gate.

## Why

Align task fixtures, inputs, rubric, judge, sampling, thresholds, and versions before comparing scores. Identical metric names can represent different scales and decision rules.

## Risk

Averaging one library's probability-like score with another's binary verdict produces an uninterpretable number. Silent skipping of failed cases can also inflate averages.

## Trade-off

Rich records cost storage and support reproducibility. A compact dashboard is useful only when links expose the underlying definitions and examples.

## Try This

Execute the paired release gate and change one case to an unsupported answer or foreign citation; explain why the candidate must fail.

## Follow-ups

### How do you distinguish a genuine evaluator improvement from a judge prompt overfit?

Freeze a sealed, independently adjudicated holdout before optimizing rubrics or judge prompts. Compare paired case IDs, disagreement and calibration by slice and inspect false positives/negatives; retesting the exact tuning examples does not independently validate the evaluator.

## Citations

- https://docs.ragas.io/

# What evaluation stack is a sensible starting point for this reference design?

## Answer

Retain deterministic pytest contracts for security and writes, use the existing the retrieval service harness for retrieval diagnosis, and add a small opt-in agent trajectory suite. Choose one experiment and tracing workflow, then add one specialized evaluator only for a demonstrated gap.

## Why

Start with service invariants, a small agent trajectory suite, and one coherent experiment workflow. Add a new evaluator only for a specific unanswered measurement need.

## Risk

Tool proliferation fragments datasets, duplicates provider spend, and increases private-data copies. A simpler stack with reviewed gold cases can produce more reliable engineering decisions.

## Trade-off

Incremental adoption delays some advanced features and keeps failure attribution manageable. Expand when the team can name the question the example tools cannot answer.

## Try This

Write a one-page evaluation architecture with test tiers, dataset owner, judge budget, privacy policy, and release blockers. Limit the first implementation to three layers.

# How do you verify that two evaluation libraries measure the same notion of faithfulness?

<!-- meta
domain: ai-rag
subdomain: evaluation-libraries
module: evaluation-libraries
concept: How do you verify that two evaluation libraries measure the same notion of faithfulness?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A library upgrade changes how unsupported claims are segmented and the dashboard improves without an application change.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Compare their input contracts, claim extraction, source treatment, judge model, aggregation, handling of abstention and version. Calibrate against independently labeled cases, including contradictions and insufficient evidence. Similar metric names do not prove identical semantics or comparable numerical scales.

Concrete engineering case: A library upgrade changes how unsupported claims are segmented and the dashboard improves without an application change.

Boundary defense: Only with a demonstrated calibration or rerun under a common contract. Treat grader identity as part of the evaluation artifact.

## Spoken Summary

Compare their input contracts, claim extraction, source treatment, judge model, aggregation, handling of abstention and version. Calibrate against independently labeled cases, including contradictions and insufficient evidence. Similar metric names do not prove identical semantics or comparable numerical scales.

## Why

Compare their input contracts, claim extraction, source treatment, judge model, aggregation, handling of abstention and version. Calibrate against independently labeled cases, including contradictions and insufficient evidence. Similar metric names do not prove identical semantics or comparable numerical scales.

## Production Case

A library upgrade changes how unsupported claims are segmented and the dashboard improves without an application change.

## Risk

A library upgrade changes how unsupported claims are segmented and the dashboard improves without an application change.

## Trade-off

Only with a demonstrated calibration or rerun under a common contract. Treat grader identity as part of the evaluation artifact.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: evaluation libraries**: Compare their input contracts, claim extraction, source treatment, judge model, aggregation, handling of abstention and version.

## Alternatives

- Only with a demonstrated calibration or rerun under a common contract. Treat grader identity as part of the evaluation artifact.

## Pitfalls

- A library upgrade changes how unsupported claims are segmented and the dashboard improves without an application change.

## Follow-ups

### Can you compare scores across judge versions without qualification?

Only with a demonstrated calibration or rerun under a common contract. Treat grader identity as part of the evaluation artifact.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A library upgrade changes how unsupported claims are segmented and the dashboard improves without an application change.",
  "required_decision": "Compare their input contracts, claim extraction, source treatment, judge model, aggregation, handling of abstention and version"
}
```

## Citations

- https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/
- https://deepeval.com/docs/metrics-faithfulness
- https://www.promptfoo.dev/docs/configuration/expected-outputs/

# How do you keep evaluation semantics stable when changing libraries or dashboards?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: evaluation-libraries
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A library provides collection, execution and reporting mechanisms; your evaluation contract defines dataset identity, metric meaning, aggregation and failure policy. Export raw per-case outcomes and version configuration so a dashboard change does not silently change acceptance. Check how missing results, judge errors, retries and skipped cases enter the denominator. Run a small shared fixture through both implementations before comparing their totals. Provider integration convenience does not establish that two similarly named metrics measure the same quantity.

## Why

One runner excludes timed-out cases and another counts them as failures. Their reported success rates cannot be compared directly even if both dashboards call the metric 'pass rate'.

## Worked Case

One runner excludes timed-out cases and another counts them as failures. Their reported success rates cannot be compared directly even if both dashboards call the metric 'pass rate'.

## Risk

A changed denominator can look like a quality improvement.

## Trade-off

Separate portable metric definitions from provider-specific collection adapters.

## Try This

Reconcile per-case results and denominators across two evaluation reports.

## Citations

- https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/
- https://deepeval.com/docs/metrics-faithfulness
- https://www.promptfoo.dev/docs/configuration/expected-outputs/
