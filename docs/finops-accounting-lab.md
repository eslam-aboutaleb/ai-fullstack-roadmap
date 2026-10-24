# Production observability and FinOps — taught through failures (#48)

**Introduction.** Models expose different token and modality usage fields.
A user's business task can trigger more than one model call, retry, tool use
and provider. A successful HTTP response does not prove the task succeeded
or that its bill is reconciled.

**Core mechanism.** Track `task_id` separately from `attempt_id` and
assign each provider call a price-catalog revision. The offline ledger in
`labs/finops_budget_ledger.py` uses integer **microUSD**: if a rate is quoted
in USD per million tokens, multiplying by the token count produces microUSD.
Its example rates are invented *teaching fixtures*, not live prices.

Reserve a maximum before admitting an attempt, under an atomic SQLite
transaction. A settlement with actual usage releases unused reservation.
If provider usage is missing, **hold the reservation** and reconcile later.
Each retry is a distinct billable attempt even if there is only one logical
task result. Concurrent users cannot spend the same remaining budget.

Run `python3 -B labs/finops_budget_ledger.py`. Tests cover cache price
subtotals, duplicate attempt IDs, unknown usage, owner scope, refunds,
over-limit admission and concurrent write contention.

**Interview study map.** Calculate a multi-attempt task cost, defend a
per-tenant budget gate, distinguish TTFT vs first-byte HTTP latency, explain
why trace IDs cannot become high-cardinality metric dimensions and separate
provider failure/quality degradation from a healthy web endpoint. What
changes with different cached-token rates, privacy-restricted traces and
provider failover? Explain where usage field reconciliation, external
invoices, model drift monitoring and dashboard alert evaluation still need
real provider/production data.

A local SQLite fixture is not a distributed spend-control service, and the
included limits must not be advertised as cloud billing accuracy.
