# Evaluation platforms: provider-neutral quality evidence (issue #42)

Introduction: production evaluation is an independently defined experiment,
not the existence of a trace dashboard. A canonical record contains a stable
case ID/split, owner scope, source evidence, answer, model/index/prompt version,
trace ID, scorer version, human adjudication and measured latency/usage.

Local offline exercise: python3 -B labs/eval_platform_contract.py
It tests recall, unsupported answer refusal, tenant-negative evidence,
pairwise release regressions, dataset fingerprint and 2x2 binary judge
disagreement. Results come from synthetic fixtures, not live LLM judges.

Actual platform implementation plan:
- LangSmith and Langfuse: compare run/trace span export, dataset IDs and feedback.
- Arize Phoenix: compare OpenTelemetry span IDs and annotated eval trace.
- DeepEval/Ragas: pin score definitions and evaluator model versions.
- Promptfoo: pin provider config, test case IDs and rubric/threshold mapping.
- Human review: calibrate judges against independently adjudicated cases and
  preserve disagreements, never silently mark a machine label as gold.

These are outstanding real integration tasks requiring pinned SDKs, real
service instances and possibly credentials. Static Pages uses no secrets.
