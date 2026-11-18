<!-- chapter: agent-observability -->

# How do logs, metrics, traces, audit records, and evaluations differ?

## Answer

Logs describe events, metrics aggregate measurements, traces connect causal execution spans, audit records document selected authoritative actions, and evaluations assess behavior against expectations. They can correlate through operation IDs but are not substitutes for one another.

## Why

Use metrics for trends, logs for events, traces for causal execution, audit for required accountability, and evaluation for quality. Give each a retention and failure policy suited to its purpose.

## Risk

A successful trace export does not prove a business committed, and an audit row does not explain a model's poor retrieval. Confusing these roles produces incomplete incident diagnosis.

## Trade-off

Multiple signals add operational work and answer different questions. Start with a small coherent schema rather than unrelated dashboards.

## Try This

For a failed confirmation after a successful model turn, state which signal proves the transaction result and which explains the preceding tool choice.

# What should a useful agent trace tree contain?

<!-- meta
reference: https://opentelemetry.io/docs/concepts/signals/traces/
-->

## Answer

One request or turn root should connect relevant model, tool, retrieval, and persistence activity with durations and sanitized outcomes. Include operation and version metadata needed to reproduce the failure, while excluding secrets and unnecessary private content.

## Why

Create a task or request root and connect model, retrieval, tool, and persistence spans. Include safe operation and release references without storing unnecessary user content.

## Risk

Orphan model spans can hide which user-visible turn incurred cost. Copying entire state into attributes creates a privacy problem and a noisy trace.

## Trade-off

Rich trace structure improves diagnosis but adds instrumentation complexity. Keep high-value boundaries stable and avoid tracing every tiny helper.

## Try This

Draw the trace tree for coverage review with two tool calls, retrieval, one retry, and final persistence. Mark parallel versus sequential time honestly.

# Why does the runtime-to-model tracing bridge need explicit context stitching?

## Answer

Different instrumentation layers may not share the same active trace context. A parent turn recorded by one SDK and a completion recorded by another callback can otherwise appear as unrelated runs. Correlation metadata bridges that boundary.

## Why

Propagate trace context through supported async and adapter hooks. Verify parentage and avoid brittle monkey patches unless version-specific tests justify the integration.

## Risk

Patching a framework seam is sensitive to dependency changes. A successful import does not prove nesting remains correct after an upgrade, and duplicate callbacks can double recorded usage.

## Trade-off

A localized bridge preserves business-code independence and needs targeted compatibility tests. Provider-native tracing can be simpler but may not connect all application activity.

## Try This

Assert one root turn with nested tool and model spans before and after repeated startup. Verify parent IDs using synthetic data.

# How do you distinguish tool exceptions from business failures in telemetry?

## Answer

Record transport/runtime success separately from domain outcome. A function that returns error='backend unavailable' has executed without raising but did not satisfy the user task. An empty successful search is another distinct outcome.

## Why

Record function exceptions and returned business failures separately. A successful function invocation may still mean not found, denied, unavailable, or needs confirmation.

## Risk

A dashboard based only on exceptions can report excellent tool reliability while users receive failed searches or validations. Mixing not-found with outages also obscures incident severity.

## Trade-off

Typed outcome categories require consistent tool schemas and provide actionable alerts. Raw exception counts are simple and incomplete.

## Try This

Add outcome dimensions for completed, empty, validation_rejected, unauthorized, backend_failed, and cancelled. Test each without logging private arguments.

# How should token and cost telemetry handle unknown prices?

<!-- meta
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer.** Maintain two distinct facts: **observed usage** from a model/provider response and **priced cost** based on a documented, effective-dated catalog. Unknown usage is not zero. Unknown price is not free. Per business task, correlate each distinct provider attempt to a trusted tenant, task ID, trace ID, model revision and price revision. Keep reserved, settled and unresolved amounts separately; do not double-charge identical webhook deliveries, but do count *different billable retries* even if only one user-facing answer succeeds.

**Token categories.** Input tokens, cached-read tokens, cache-write tokens, output tokens and provider-reported reasoning tokens can have different billing semantics; do not blindly add categories if the provider's fields already include them. Different models and modalities may charge per image, second, characters or other units. Preserve raw provider counters alongside normalized categories, provenance, currency, region, unit and rate version.

**Worked calculation (illustrative, not a live provider tariff).** If input costs $2 per million tokens, cache reads $0.50 per million, and output $8 per million, a request with 200 input tokens (50 cached), 80 output tokens costs (150×2 + 50×0.5 + 80×8) microUSD = 965 microUSD = **$0.000965**. If an earlier attempt incurred 200 microUSD before failing, the *task* cost is 1,165 microUSD; billing it only once because the user saw one response loses the retry charge. Do not mistake a model's token **estimate** for actual settled usage.

**Admit versus settle.** A high-concurrency application must reserve a bounded maximum amount before sending calls, using a transactional per-user or tenant budget gate. On completion, settle against provider usage, refund the unused reservation, and reconcile invoice anomalies. Cancellation or missing usage must not automatically erase a possibly charged attempt. Where actual spend exceeds the reservation, flag an exceptional reconciliation path rather than silently dropping the liability.

**Implementation and failure modes.** `labs/finops_budget_ledger.py` demonstrates atomic SQLite holds, idempotent attempt IDs, owner scope, price version and cache rate splits. Negative tests reject concurrent overspending, changed-payload replay and unauthorized settlement. The lab does not call a provider or prove a cloud invoice. Avoid storing raw prompts, user names or sensitive content as metrics labels; use opaque correlation IDs and privacy-aware trace sampling.

**Follow-up — a provider 429 spike causes retries but the application returns HTTP 200.** The HTTP success rate hides a deteriorating dependency. Alert on retry rate, model wait, budget drain, task-level correctness and saturation. Use circuit breakers/backoff and a fallback only after evaluating changes to privacy residency, quality, safety and price.

## Why

Resolve usage and pricing independently, retaining unknown and estimated values explicitly. Compare total cost per completed task, including retries and failed runs, with a known pricing source.

## Risk

A zero-cost metric can hide a new provider or unsupported model price. Retries, embedding, and reranking may also be omitted from a narrow generation-only dashboard.

## Trade-off

Detailed accounting adds metadata and improves budget control. Provider invoices remain a reconciliation source rather than assuming local estimates are exact bills.

## Try This

Send a synthetic unknown-model usage record and verify it is reported as unpriced, not confidently free. Attribute all calls in one successful task.

## Follow-ups

### What happens when an invoice shows a charged retry but the application has no token-usage response?

Keep the attempt unresolved in a reserved or reconciliation state and associate the provider request identifier, model and effective price revision. Never silently record zero cost; reconcile the authoritative provider invoice before releasing reserved funds and preserve retries as separate attempts.

## Citations

- https://opentelemetry.io/docs/specs/semconv/gen-ai/

# Why are in-process metrics different from fleet-wide monitoring?

## Answer

Process-local counters and bounded event buffers describe one process since its start. They do not automatically aggregate across replicas, survive restarts, or provide a durable long-term time series. Fleet monitoring requires collection and identity rules.

## Why

Aggregate across replicas through an external collection system and stable metric definitions. Process-local counters cannot establish a deployment-wide rate or survive restart by themselves.

## Risk

Summing request snapshots repeatedly can double count, and restarting a process can look like a sudden drop in demand. High-cardinality labels such as raw request IDs can overwhelm a metrics backend.

## Trade-off

Local metrics are lightweight and useful for debugging; shared systems add infrastructure and coherent operational visibility.

## Try This

Run two replicas and restart one. Specify how counters, gauges, and histograms should be exported and queried without inventing fleet totals.

# How can trace collection disclose private customer data?

<!-- meta
reference: https://opentelemetry.io/docs/security/handling-sensitive-data/
-->

## Answer

Tool arguments, results, prompts, completions, exception strings, and URLs can contain customer or claim information. Tracing a trusted tool does not make its payload safe to export. Data minimization must apply before or at the instrumentation/export boundary.

## Why

Apply an allowlist before export, redact necessary payloads, and control access and retention. Review embeddings, transcripts, documents, and identifiers as potential disclosure sources.

## Risk

Trace readers or vendors may gain access broader than the product's owner-scoped API permits. Confirmation tokens and source text should not appear by accident in support exports.

## Trade-off

Content-rich traces help reproduce model failures and increase privacy obligations. Prefer sanitized fixtures and reviewed sampled content when necessary.

## Try This

Inventory actual exported payloads for one synthetic request preparation. Define an allowlist and prove a fake token and private description are absent.

# Should tracing failures be allowed to fail business operations?

## Answer

Optional telemetry often uses best-effort failure containment to preserve availability. Mandatory business audit may require a different policy. Decide per signal rather than declaring that every kind of observation may be dropped harmlessly.

## Why

Keep optional telemetry failure from blocking business work where the product permits it. Required audit may need transactional delivery or a controlled fail-closed policy instead.

## Risk

Silent instrumentation failure can leave an incident undiagnosable. Conversely, blocking every request on a slow telemetry vendor can create an avoidable outage.

## Trade-off

Fail-open telemetry improves availability and needs health signals for lost coverage. Transactional audit or a durable audit outbox increases assurance and operational coupling.

## Try This

Simulate unavailable tracing and unavailable audit storage separately. Define the expected request, readiness, and alert behavior for each.

# What SLOs and alerts are useful for a support assistant?

<!-- meta
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Define service-level indicators around the customer task**, not only the web server's health. Useful signals include task-success fraction over independent samples, grounding/citation validity, unsupported-answer behavior, false refusal, tool-denial and effect integrity, and request availability. Track latency distributions by *task type and concurrency*: p50, p95 and p99 end-to-end; model first-token latency (TTFT), inter-token time, retrieval duration, tool queue and external operation waits. Averages hide tail latency and failures.

**Set measurable objectives.** Example policy, not an existing production result: "At least 99% of supported owner-scoped requests complete correctly within 8 seconds over a rolling 28-day window, while critical cross-tenant disclosures must be zero." Correctness must be independently checked, so not every unlabeled production response can claim success. Track invalid/unknown outcomes separately. Use an error budget for release and paging decisions rather than treating any single slow task as an incident.

**Alerts.** Watch sustained dependency 429/5xx, reserve-budget failures, anomalous retries/cost-per-task, stale retrieval, message queue age, p99 token latency and mandatory data-owner controls. An exhausted error budget or critical disclosure triggers a release gate, irrespective of healthy mean latency. Prefer burn-rate alerts over one-off thresholds; use trace exemplars for diagnosis but avoid sensitive high-cardinality metric labels.

**Production scenario.** The gateway returns 200 after a failover, but the fallback misses citations and increases output tokens per answer. Provider uptime looks green while grounding and tenant budget outcomes worsen. Correlate task spans, model attempt IDs, effective price catalog and reviewer-labeled outcomes. A sampled trace can explain a specific failure, but cannot by itself prove fleet-wide prevalence.

**Follow-up — tracing is unavailable during a provider incident.** Preserve the business operation and authoritative effect ledger; degrade sampling/export safely with privacy limits. But fail closed for essential authorization/audit controls whose absence would make the action unsafe. Distinguish task telemetry from the mandatory write audit.

## Why

Define SLOs around useful outcomes, response delay, evidence freshness, and recovery. Alert on sustained user impact and preserve a path from aggregate metrics to safe trace identifiers.

## Risk

Alerting only on average HTTP latency misses stuck jobs and quality failures. Sampling can also miss rare severe authorization incidents, which need deterministic denial monitoring and tests.

## Trade-off

More nuanced SLOs require definitions and ownership. A small set linked to concrete user impact is more maintainable than dozens of disconnected thresholds.

## Try This

Define a stream-success SLO and an indexing-lag SLO, including numerator, denominator, window, and corrective action.

## Follow-ups

### Would a successful HTTP response justify counting a task as a successful user outcome?

No. HTTP 200 measures an API transport outcome, not citation accuracy, authorization, refusal appropriateness or successful side effects. Attribute task-level status from independently evaluated outcomes, then monitor latency/error-budget and quality slices with a known denominator.

## Citations

- https://sre.google/workbook/alerting-on-slos/

# How should observability produce better evaluation cases?

## Answer

Triage a failure trace, minimize and sanitize it, establish the correct outcome with a reviewer, and add a versioned regression case. Keep raw production data access restricted and preserve which failure the new case is intended to catch.

## Why

Turn reviewed incidents into redacted reproducible fixtures. Keep task category, configuration lineage, observed failure, and expected invariant while avoiding unnecessary customer-data retention.

## Risk

Automatically adding model answers as gold labels reinforces errors. Copying production conversations into broad datasets can violate data-minimization policy.

## Trade-off

Reviewed case creation costs human time and improves relevance. Fully synthetic tests scale cheaply and may miss real ambiguity.

## Try This

Turn one synthetic wrong-policy trace into a case with expected revision, required tool steps, allowed final outcomes, and a clear privacy review.

# How do OpenTelemetry semantic conventions for Generative AI capture agent spans without violating data privacy or leaking customer PII?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: agent-observability
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**OpenTelemetry semantic conventions for Generative AI define standardized telemetry attributes for traces, metrics, and logs while enforcing strict privacy-by-design boundaries.** When autonomous agents execute multi-step planning loops, naively serializing prompts and tool payloads into span attributes sends proprietary intellectual property, confidential user chats, and unredacted PII to third-party APM SaaS vendors (Datadog, Honeycomb, New Relic).

**Standardized GenAI attributes.** The OpenTelemetry GenAI specification defines standardized span attributes: (1) Model and provider identity: `gen_ai.system` (e.g. `"openai"`, `"anthropic"`), `gen_ai.request.model`, `gen_ai.response.model`; (2) Token accounting: `gen_ai.usage.prompt_tokens`, `gen_ai.usage.completion_tokens`, `gen_ai.usage.total_tokens`; (3) Execution hyperparameters: `gen_ai.request.temperature`, `gen_ai.request.top_p`, `gen_ai.response.finish_reasons`; and (4) Tool and Agent spans: wrapping each tool invocation in a dedicated span with `gen_ai.operation.name: "tool"` and `gen_ai.tool.name`.

**Privacy-by-design redaction policy.** To prevent telemetry from becoming a secondary breach vector, organizations enforce strict capture controls: (1) Default exclusion of prompt and completion payloads: `gen_ai.prompt` and `gen_ai.completion` must be disabled in production, capturing only token counts and latency metrics; (2) In-line PII sanitization: if payload capture is explicitly enabled for audit compliance, an OpenTelemetry Span Processor runs regex and Named Entity Recognition (NER) scrubbers to mask credit cards, API keys (`sk-...`), and personal identifiers before spans leave the process; and (3) Ephemeral, encrypted trace sinks with strict retention TTLs.

## Why

A medical assistant agent processes patient records. An unredacted OpenTelemetry exporter sends full patient medical histories as trace attributes to a third-party monitoring dashboard, causing an immediate HIPAA compliance violation. Enabling GenAI privacy-by-design masks patient data while retaining token and latency metrics.

## Worked Case

A medical assistant agent processes patient records. An unredacted OpenTelemetry exporter sends full patient medical histories as trace attributes to a third-party monitoring dashboard, causing an immediate HIPAA compliance violation. Enabling GenAI privacy-by-design masks patient data while retaining token and latency metrics.

## Risk

Sending unmasked user queries and retrieved document chunks into APM trace aggregators violates compliance standards including GDPR, HIPAA, and SOC 2.

## Trade-off

Redacting raw text from spans increases debugging difficulty during hallucination investigations, requiring developers to reproduce bugs in dedicated, synthetic staging sandboxes.

## Try This

Configure an OpenTelemetry Tracer in Python using the `opentelemetry-semantic-conventions` package. Emit a GenAI span with standard token attributes and verify that raw prompts are excluded.

## Follow-ups

### How do you trace tool call arguments under OpenTelemetry GenAI conventions?

Tool calls are recorded as child spans under the model invocation span, recording the tool name and execution status while sanitizing sensitive argument values.

## Citations

- https://opentelemetry.io/docs/specs/semconv/gen-ai/
- https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/

# How do you maintain distributed trace context across asynchronous message queues, background workers, and long-running agent workflows?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: agent-observability
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Maintaining distributed trace context across asynchronous boundaries requires explicit W3C Trace Context propagation across thread pools, message queues, and async tasks.** In autonomous agent systems, a single user request can trigger a cascading, long-running workflow: a FastAPI gateway receives the request, publishes an event to Kafka or RabbitMQ, a background Celery worker picks up the job, invokes an LLM, schedules two parallel sub-agents, and writes results to PostgreSQL. If trace context is lost at any hop, the workflow shatters into disconnected trace fragments, making debugging impossible.

**W3C Trace Context headers (traceparent and tracestate).** OpenTelemetry standards define the `traceparent` HTTP/message header: `traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`, encoding version, 16-byte `trace_id`, 8-byte `parent_span_id`, and trace flags. When publishing a job to a message queue or background task runner, the publisher must inject active context into message headers: `inject(carrier=message.headers)`. When the background worker consumes the message, it extracts context: `context = extract(carrier=message.headers)` and starts child spans linked to the extracted context.

**Python asyncio contextvars preservation.** In Python async workflows, trace context is held in `contextvars`. A frequent bug occurs when dispatching work via `asyncio.to_thread()` or `concurrent.futures.ThreadPoolExecutor`: thread boundaries do NOT automatically inherit contextvars unless explicitly copied using `contextvars.copy_context().run(func)`. Proper instrumentation ensures that child spans accurately reflect the parent span across threads and async tasks.

## Why

An agent task fails in a background Celery worker. In the APM dashboard, the Celery execution appears as an isolated root trace with a new trace_id, making it impossible to correlate with the user's original HTTP request. W3C trace injection links the frontend request, Kafka message, and worker execution into a single unified trace waterfall.

## Worked Case

An agent task fails in a background Celery worker. In the APM dashboard, the Celery execution appears as an isolated root trace with a new trace_id, making it impossible to correlate with the user's original HTTP request. W3C trace injection links the frontend request, Kafka message, and worker execution into a single unified trace waterfall.

## Risk

Dropping trace headers during message queue serialization breaks causal correlation, leaving engineers blind to distributed agent latencies and failure cascades.

## Trade-off

Injecting and extracting W3C headers adds minor serialization logic to message producers and consumers, but provides end-to-end operational visibility across distributed workers.

## Try This

Use OpenTelemetry Python SDK to inject `traceparent` into a dictionary, simulate sending it across a network boundary, extract the context, and verify the child span shares the identical `trace_id`.

## Follow-ups

### What is the difference between Span Links and Parent-Child Spans in asynchronous queues?

Parent-Child spans represent direct synchronous blocking dependencies; Span Links represent causal relationships where a batch worker processes multiple independent message traces simultaneously without blocking the parent.

## Citations

- https://www.w3.org/TR/trace-context/
- https://opentelemetry.io/docs/languages/python/instrumentation/#context-propagation

# What is the difference between latency profiling, token attribution accounting, and cost tracking across multi-turn agent decision graphs?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: agent-observability
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Production agent observability requires a three-dimensional accounting model that separates performance latency, resource consumption, and financial unit economics.** Monitoring basic HTTP request latency alone fails to explain why an agentic workflow was slow or expensive, because a single user turn can trigger five tool calls and three recursive LLM reasoning steps.

**1. Latency Profiling (Time-to-First-Token vs Inter-Tool Delays).** Latency profiling decomposes execution time across: (a) Time-To-First-Token (TTFT): the time taken by the LLM provider to process the prompt prefix and emit the first streaming token (dominated by prompt token count and prefill compute); (b) Inter-Token Latency (ITL): generation speed per output token; (c) Tool Execution Time: wall-clock time spent inside database queries or external API requests; and (d) Client Network Overhead. Profiling reveals whether delays stem from large prompt prefill, slow third-party tool APIs, or queue scheduling.

**2. Token Attribution Accounting (Prompt Bloat & Tool Footprint).** Token accounting disaggregates token spend by category: System Instructions, Tool JSON Schemas, Conversation History, Retrieved Evidence, and Generated Output. Attribution metrics pinpoint which subsystem is causing token bloat (e.g. an oversized 4,000-token tool catalog or a bloated 50-turn chat history).

**3. Financial Cost Tracking (Unit Economics per User Journey).** Cost tracking maps token consumption and infrastructure compute to financial currency ($ USD) based on model pricing tiers (input vs output tokens, cached prefix discounts, image/audio token multipliers). Metrics compute: Cost per Completed Task, Cost per User Session, and Gross Margin per Tenant.

## Why

An agent response takes 18 seconds. Monitoring reveals: TTFT was only 400ms, but a custom SQL tool took 14 seconds due to a missing database index, and the LLM generated 1,200 tokens because the prompt lacked a conciseness constraint. The breakdown immediately isolates the database index as the primary bottleneck.

## Worked Case

An agent response takes 18 seconds. Monitoring reveals: TTFT was only 400ms, but a custom SQL tool took 14 seconds due to a missing database index, and the LLM generated 1,200 tokens because the prompt lacked a conciseness constraint. The breakdown immediately isolates the database index as the primary bottleneck.

## Risk

Tracking only global monthly LLM API bills conceals runaway token consumption by specific abusive users or inefficient agent looping paths.

## Trade-off

Multi-dimensional accounting requires annotating spans with token counts and pricing matrices, trading minor telemetry instrumentation for precise financial unit economics.

## Try This

Write an OpenTelemetry span processor that computes dollar cost from prompt and completion token counts based on published model price rates, attaching `app.cost_usd` to each span.

## Follow-ups

### How does prompt caching affect token cost tracking?

Providers offer 50%–75% discounts on cached prompt tokens; telemetry must record `cached_prompt_tokens` separately to calculate accurate financial costs.

## Citations

- https://opentelemetry.io/docs/specs/semconv/gen-ai/
- https://www.datadoghq.com/blog/llm-observability/

# How do you instrument automated anomaly detection for agent death loops, runaway tool recursion, and context window bloat?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: agent-observability
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Autonomous agents running open-ended decision loops are vulnerable to catastrophic failure modes including death loops, recursive delegation thrashing, and context window bloat.** A death loop occurs when an agent encounters an unhandled tool error, reformulates the query with minor variations, and re-invokes the failing tool repeatedly until it exhausts tokens or API rate limits.

**Real-time anomaly detection heuristics.** Production observability platforms deploy real-time stream processing rules on span streams to catch agent anomalies before they exhaust financial budgets: (1) Levenshtein distance on consecutive tool arguments: if an agent invokes the same tool 3 times consecutively with argument strings having >90% textual similarity, a death loop detector triggers; (2) Semantic loop detection: embedding the model's reasoning thoughts and computing cosine similarity against the prior two turns; if similarity exceeds 0.95, the agent is repeating thoughts; (3) Tool call frequency ceilings: alerting if an agent executes > 8 tool calls within a single user turn; and (4) Context bloat velocity: tracking the rate of token growth per turn; if input tokens increase by >5,000 tokens across consecutive turns, an alert fires for context leakage.

**Automated circuit breaking and recovery.** Upon detecting an anomaly, the telemetry system triggers automated circuit breakers: (1) Force-terminating the active agent loop; (2) Injecting an explicit system correction message: `'[System Warning: You have repeated tool X three times without success. Halt tool calling and explain the failure to the user]'`; or (3) Gracefully escalating to a human operator.

## Why

An agent queries a weather API with an invalid zip code. The API returns an error. The agent retries 45 times in a loop, burning $15.00 in LLM tokens and locking up worker concurrency. A death loop detector intercepts the execution on attempt 3, halting the run and saving the budget.

## Worked Case

An agent queries a weather API with an invalid zip code. The API returns an error. The agent retries 45 times in a loop, burning $15.00 in LLM tokens and locking up worker concurrency. A death loop detector intercepts the execution on attempt 3, halting the run and saving the budget.

## Risk

Allowing autonomous agents to run without real-time recursion and death-loop circuit breakers exposes the organization to massive unbounded cloud billing spikes.

## Trade-off

Real-time anomaly detection requires stateful monitoring of active agent spans, trading minor telemetry overhead for guaranteed containment of runaway agent costs.

## Try This

Write an agent guard wrapper that tracks the history of tool calls in state. If the same tool is called with the same arguments twice consecutively, raise an AgentDeathLoopException.

## Follow-ups

### Can an LLM judge detect its own death loop?

Rarely. Models trapped in death loops exhibit fixation bias; deterministic external heuristics (argument hashing and repetition counters) are far more reliable than model self-reflection.

## Citations

- https://opentelemetry.io/docs/specs/semconv/gen-ai/
- https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/

# How do you debug a tool timeout without retaining complete private prompts in traces?

<!-- meta
domain: ai-rag
subdomain: agent-observability
module: agent-observability
concept: How do you debug a tool timeout without retaining complete private prompts in traces?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A retry storm is visible only as generic failures, so engineers enable full request logging and create a second private document store.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Record appropriate stage timing, operation identity, bounded outcome codes, retry count and safe resource-generation metadata. Prefer allowlisted attributes and restricted diagnostic workflows. Correlate model/tool/receiver spans without putting tokens, document bodies or uncontrolled high-cardinality input into ordinary telemetry.

Concrete engineering case: A retry storm is visible only as generic failures, so engineers enable full request logging and create a second private document store.

Boundary defense: Not necessarily. Small predictable input spaces can be guessed. Minimize collection and apply the actual privacy and access policy.

## Spoken Summary

Record appropriate stage timing, operation identity, bounded outcome codes, retry count and safe resource-generation metadata. Prefer allowlisted attributes and restricted diagnostic workflows. Correlate model/tool/receiver spans without putting tokens, document bodies or uncontrolled high-cardinality input into ordinary telemetry.

## Why

Record appropriate stage timing, operation identity, bounded outcome codes, retry count and safe resource-generation metadata. Prefer allowlisted attributes and restricted diagnostic workflows. Correlate model/tool/receiver spans without putting tokens, document bodies or uncontrolled high-cardinality input into ordinary telemetry.

## Production Case

A retry storm is visible only as generic failures, so engineers enable full request logging and create a second private document store.

## Risk

A retry storm is visible only as generic failures, so engineers enable full request logging and create a second private document store.

## Trade-off

Not necessarily. Small predictable input spaces can be guessed. Minimize collection and apply the actual privacy and access policy.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: agent observability**: Record appropriate stage timing, operation identity, bounded outcome codes, retry count and safe resource-generation metadata.

## Alternatives

- Not necessarily. Small predictable input spaces can be guessed. Minimize collection and apply the actual privacy and access policy.

## Pitfalls

- A retry storm is visible only as generic failures, so engineers enable full request logging and create a second private document store.

## Follow-ups

### Does hashing a predictable user identifier make it anonymous?

Not necessarily. Small predictable input spaces can be guessed. Minimize collection and apply the actual privacy and access policy.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A retry storm is visible only as generic failures, so engineers enable full request logging and create a second private document store.",
  "required_decision": "Record appropriate stage timing, operation identity, bounded outcome codes, retry count and safe resource-generation metadata"
}
```

## Citations

- https://opentelemetry.io/docs/concepts/signals/
- https://opentelemetry.io/docs/concepts/signals/traces/
- https://opentelemetry.io/docs/security/handling-sensitive-data/
- https://docs.langchain.com/langsmith/observability

# How do trace context, sampling and data redaction change what operators can conclude?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: agent-observability
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Trace context connects related spans across asynchronous and remote boundaries; missing propagation can split one operation into unrelated observations. Sampling decides which traces are retained and can bias visible failures or latency. Redaction must apply before sensitive fields enter logs, events or exports. Use bounded metric labels rather than raw user or prompt values, and keep authoritative audit records distinct from sampled telemetry. An absent trace may indicate sampling or propagation loss, not that no action happened.

## Why

A provider span lacks its parent because context was not propagated into a worker. The dashboard shows two short traces rather than the real long request, so operators may misdiagnose latency until correlation is repaired.

## Worked Case

A provider span lacks its parent because context was not propagated into a worker. The dashboard shows two short traces rather than the real long request, so operators may misdiagnose latency until correlation is repaired.

## Risk

High-cardinality labels can create excessive telemetry cost and expose identity.

## Trade-off

Sampled traces aid diagnosis; durable audit state supports required accountability.

## Try This

Follow one request across a worker and verify safe identifiers without raw private content.

## Citations

- https://opentelemetry.io/docs/concepts/signals/
- https://opentelemetry.io/docs/concepts/signals/traces/
- https://opentelemetry.io/docs/security/handling-sensitive-data/
- https://docs.langchain.com/langsmith/observability
