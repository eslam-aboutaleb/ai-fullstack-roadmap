# Build, break and defend the three connected workflows

Read the introduction and ordered questions in Retrieval/Evaluation, Agent Harness,
and Frontend/Data/Deployment. These projects run on your computer; the roadmap
remains a static site. Python 3.11+ is sufficient for the first two projects and
CDC checks. The browser project needs Node 22.12+ and its lockfile. All policy text,
incidents, credentials and expected answers are original synthetic teaching data.
Repository MIT licensing applies. No paid account or model is required.

## 1. Policy assistant: independent evidence before generation

From the repository or extracted local-projects ZIP root:

```sh
python3 labs/policy_assistant_project.py --check --report policy-report.json
# In the source ZIP keep labs/. For files in a built static-site copy, use examples/labs/.
```

The report contains the corpus hash, per-case retrieval/answer results, a deliberately
broken candidate and predictions. The reference gets 8/8 authored cases right. Its
missing-exception mutant must fail the final-sale case. Recall, reciprocal rank and
binary nDCG are independently checked for a relevant hit at rank two: 1, 0.5 and
approximately 0.63093. Recall is null for unanswerable queries, not one.

Build your own predictor from `SOURCES` and `CASES`, without calling `predict`.
Use exactly one JSON object per case: `id`, `answer` (string or null), `citations`
(scoped span IDs), and `ranking` (unique ordered scoped IDs). Save a JSON array:

```sh
python3 labs/policy_assistant_project.py --grade learner-predictions.json --report grade.json
```

A failed grade exits nonzero and identifies per-case errors. Scope is part of each
span ID: `A:returns@2:0` is not `B:returns@1:0`. The gold spans and sentences were
fixed independently of prediction. This narrow exact-answer oracle does not grade
arbitrary paraphrases or prove natural-language entailment; adjudicate changed
phrasing and unseen cases separately. Do not remove difficult cases or copy reference
predictions and call that independent completion.

Required artifacts: learner implementation, corpus/profile hash, predictions,
failed and repaired grades, and a two-page explanation. Add an unseen final-sale
question, a revised policy, a deleted latest revision, an unknown question and an
owner-swapped query. Define expected evidence before running either method.
Explain candidate recall versus reranking, final context versus citation support,
false refusal versus unsupported answers, and approximation versus relevance recall.
Compare lexical and fusion variants on the same cases and report exceptions, not
only an average. A learned embedding extension must pin its model/license/profile,
reindex both query/document spaces and rerun all scope/revision cases. The existing
two-dimensional vectors and coverage ranker are explicitly not learned models.

Optional external-model extension: create a provider adapter behind the same scoped
request/result contract. Pin the chosen SDK/model revision, read its actual schema,
refusal, streaming and usage contracts, and inject a narrowly scoped key through
your local environment only. Set a small explicit maximum output, deadline,
attempt/cost allowance and synthetic-only corpus; log safe IDs and reported usage,
never the key. Pass only the authorized evidence and validate runtime schema,
citation membership and claim support. Run supported, unknown, malformed, rate-limit,
owner-swap and interrupted-stream cases. Record provider execution separately from
mock replay. Revoke the test key and remove local sensitive logs afterwards. A live
call is optional for issue #17 and cannot replace the credential-free baseline.

## 2. Support agent: exact approval and independently counted effects

```sh
python3 labs/research_support_project.py tools
python3 labs/research_support_project.py propose --db support.sqlite --owner A --run case-1
python3 labs/research_support_project.py execute --db support.sqlite --owner A --run case-1
# The previous command must fail: there is no approval yet.
python3 labs/research_support_project.py approve --db support.sqlite --owner A --run case-1
python3 labs/research_support_project.py execute --db support.sqlite --owner A --run case-1
python3 labs/research_support_project.py execute --db support.sqlite --owner A --run case-1
python3 labs/research_support_project.py trace --db support.sqlite --owner A --run case-1 --report trace.json
python3 labs/research_support_project.py check --report support-report.json
```

Approvals last 60 seconds by default. If you pause longer, issue a fresh approval
while the proposal is still pending. The second successful execute reconciles the
same local effect. Do not change operation keys to make failed replays pass.
The CLI owner flag is a trusted single-user fixture input, not authentication.
Anyone controlling this local database can edit its records; no production
cryptographic-approval or tamper-evident audit claim is made.

The check uses separate connections to race two executions, loses an acknowledgment
after commit, reopens state, tests changed payload/expiry/owner/cancellation, and
aborts audit insertion. That last fault must roll back the ticket and completed
state. Inspect `tickets`, `runs`, `approvals` and `trace` independently using SQLite:

```sh
sqlite3 support.sqlite 'SELECT owner,operation,payload,source FROM tickets;'
```

Open the published `agent_trace_reader.html` and choose the exported trace/report.
It uses text rendering and sends no file data to a server. Compare source → proposal
→ approval → committed effect → reconciliation against the ticket count. A tool-call
trace or generated success sentence alone is insufficient evidence.

Build your own implementation against these invariants, then add a new incident
with a material argument change and an approval that expires while queued. Supply
source, negative outputs, reopened database rows, safe trace and an architecture
sequence. Explain why a local same-database effect can be atomic while an external
payment needs receiver idempotency/reconciliation and possibly compensation.

The application registry is not MCP. For actual protocol execution, use the pinned
optional `requirements-advanced.txt` environment and run `labs/protocol_interop.py`.
It exercises real MCP SDK STDIO/HTTP discovery, public execution and denied/malformed
arguments, plus an A2A task interaction. Its public fixture is not production auth.
Do not merge that evidence with the mock connector or claim cross-vendor conformance.

## 3. Full-stack: browser, data contract and recovery

The existing `projects/evidence-workbench/README.md` contains exact build/server
commands and a blank-component implementation milestone. Compile with its lockfile,
run its real browser/API acceptance checker, and keep owner-switch, malformed-stream,
missing-terminal, cancellation, literal HTML text, keyboard and mobile evidence.
Its wire format is NDJSON; implement SSE separately if taking that extension.

```sh
python3 labs/data_contract_pipeline.py
python3 labs/data_rollout_contract.py
python3 labs/restore_drill.py
python3 labs/production_scorecard.py
node labs/stream_session_reducer.cjs
```

The CDC routine rejects same-key/same-offset changed payload, gaps and unapproved
tombstone restoration. A checkpoint-write fault must leave neither projection nor
consumed-event changes. Old databases lacking material digests retain history but
cannot silently accept an unverifiable replay. For your own implementation, predict
row contents before executing each fault and compare reopened state afterwards.

Deliver a schema expand/contract plan with old/new readers and writers, quarantined
invalid input, source/transformation lineage, and a safe rebuild/deletion policy.
Connect it to your browser/API project; do not send source secrets or other-owner
rows to the browser and rely on hiding them later.

For the system-design defense, calculate 20 requests/s * 2 s = 40 mean occupied
slots, then explain why five eight-slot replicas is only an arithmetic minimum.
Specify burst, retry, N-1 headroom, bounded admission and quality constraints. Record
assumptions separately from observed timing. Include an incident timeline and a
restore check that replays deletions newer than the snapshot before traffic.

Docker/kind/cloud execution is an optional learner activity under issue #19.
The workbench includes non-root container and deployment manifests plus a disposable
cluster unavailable-image/explicit-undo exercise and teardown. A valid manifest is
not an executed rollout. This authoring environment has no usable Docker daemon;
container/GPU/cloud results are not claimed. Record actual execution when available,
including image digest, context, events, readiness and explicit cleanup. Never run
these exercises against a shared cluster by default.

## Grading and progress

Each major mechanism has a linked applied scenario in the chapter practice UI.
The three capstone self-review rubrics require source, independently expected
results, failure/repair evidence and changed-assumption interview defense. They
record self-review evidence; they do not automatically grant an objective pass or
certify professional mastery. Reject critical owner leakage, unauthorized/duplicate
effects, unsupported policy decisions or silent data loss even when averages improve.

## Technical review attribution

The technical acceptance verdict was verified under maintainer review. The content records identify
Technical curriculum review and bind the review to content digests. This is authored
and self-reviewed AI work, not an independent human SME endorsement. Executed local
checks, analytic calculations, optional unexecuted infrastructure and any future
provider/model measurements remain distinct. Automated accessibility checks do not
claim full manual assistive-technology conformance.
