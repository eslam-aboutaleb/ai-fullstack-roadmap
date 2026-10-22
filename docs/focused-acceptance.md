# Acceptance evidence: LLM/RAG, agents and full-stack

Reviewed 22 October 2026. This branch verifies issues #19. Related project sources are shared so every downloaded guide command is available; other issue acceptance remains separate until its own reviewed content and matrix merge.

The user delegated the final technical/content verdict to Codex. Records identify AI-authored/self-reviewed work with content-specific digests; no independent human SME endorsement is claimed. Original issue requirements remain binding. The original projects explicitly allow local/mock connectors and optional external-model/cloud exercises. Real protocol and browser integrations below are additional executed evidence, not mandatory live-vendor dependencies imported from separate advanced issues.

## Learning coverage

The chapter introduction, terminology and flow precede the existing foundation and deeper questions. 10 existing question IDs were expanded rather than copied into new hubs. 12 companion-unit interviews now contain complete explanations. 10 applied changed-assumption scenarios and 1 project rubrics are linked to practice/progress; self-review cannot grant an objective pass.

| Issue | Syllabus concepts | Stable topic / learner page | Assessment |
|---|---|---|---|
| #19 | semantic HTML/CSS layout, accessible forms, responsive design | [910](../content/chapters/frontend-foundations/questions.json), `frontend-foundations.html#q910` | `acceptance-19-910` |
| #19 | JS event loop, TypeScript, React rendering/state/effects, fetch/streaming | [912](../content/chapters/frontend-foundations/questions.json), `frontend-foundations.html#q912` | `acceptance-19-912` |
| #19 | auth UX, testing, performance, browser trust boundaries | [271](../content/chapters/product-delivery/questions.json), `product-delivery.html#q271` | `acceptance-19-271` |
| #19 | ETL/ELT, batch/stream, schema evolution, validation, storage/SQL | [875](../content/chapters/data-engineering-foundations/questions.json), `data-engineering-foundations.html#q875` | `acceptance-19-875` |
| #19 | CDC, lineage, data quality, deletion, checkpoint recovery | [877](../content/chapters/data-engineering-foundations/questions.json), `data-engineering-foundations.html#q877` | `acceptance-19-877` |
| #19 | Docker, IaC, CI/CD, AWS concepts, Kubernetes, secrets management | [286](../content/chapters/deployment-reliability/questions.json), `deployment-reliability.html#q286` | `acceptance-19-286` |
| #19 | model registries, serving, MLOps, release artifacts | [299](../content/chapters/model-engineering/questions.json), `model-engineering.html#q299` | `acceptance-19-299` |
| #19 | queues, caching, partitioning, rate limiting, capacity estimates, AI latency/cost/correctness tradeoffs | [138](../content/chapters/fullstack/questions.json), `fullstack.html#q138` | `acceptance-19-138` |
| #19 | consistency, transactions, security, typed APIs, idempotency | [161](../content/chapters/database-concurrency/questions.json), `database-concurrency.html#q161` | `acceptance-19-161` |
| #19 | telemetry, cost, reliability, incident response, system design | [289](../content/chapters/deployment-reliability/questions.json), `deployment-reliability.html#q289` | `acceptance-19-289` |

The machine-readable matrix is `content/shared/focused-acceptance.json`: source paths, outcome IDs, introduction/reader anchors, question IDs, unit outcomes, labs and assessments. Original instruction in the surrounding chapters remains available. Original accessible/printable ordered diagrams illustrate ingestion publication, chunk exceptions, ranking, release gating, approval/recovery, effects, CDC and capacity.

## Reproducible projects and expected behavior

- `python3 labs/policy_assistant_project.py --check`: fixed authored spans; 8/8 reference cases; removing the exception must fail. Separate answer/citation correctness, false refusal, unsupported answers, Recall/MRR/nDCG and null unanswerable recall. `--grade` checks learner predictions against fixed gold and exits nonzero on failure. Evidence: `docs/evidence/policy-assistant-project.json`.
- `python3 labs/research_support_project.py check`: exact owner/payload/source approval, expiry, restart after lost acknowledgment, two-connection race, cancellation and cross-owner denial. An audit trigger failure rolls back effect/state. Evidence: `docs/evidence/research-support-project.json`; static reader: `examples/labs/agent_trace_reader.html`.
- `python3 labs/data_rollout_contract.py`: exact material replay, gaps, revision/tombstone and checkpoint-rollback tests. `data_contract_pipeline.py`, `restore_drill.py`, `production_scorecard.py` and the Node stream reducer cover schema/quarantine, deletion replay, analytic capacity/release policy and stale callbacks.
- Compile `projects/evidence-workbench`, then run its actual HTTP/Chromium checker. It exercises normal/unsupported output, malformed/incomplete stream, cancellation, owner switching, literal text, keyboard/mobile and automated axe when installed. Recorded output: `docs/evidence/focused-workbench-run.json`.
- `python3 labs/protocol_interop.py` in the pinned `requirements-advanced.txt` environment: genuine MCP 2.3.0 STDIO/HTTP profile 2026-07-28 discovery/call/denial/schema checks and A2A 1.2.3 profile 1.0 discovery/task stream/readback/unsupported-version rejection. Evidence: `docs/evidence/focused-protocol-run.json`.

`labs/focused-project-guide.md` supplies exact commands, independent implementation milestones, expected artifacts, fault oracles, grading limits, optional provider setup and teardown. The source ZIP includes the guide and project files.

## Evidence boundaries

The corpus and incidents are original synthetic data. Policy ranking is lexical/coverage plus rank fusion and deterministic extractive answers; the separate cosine fixture uses hand-authored vectors. Neither is an embedding/LLM quality benchmark. The support effect and audit share SQLite, so local atomicity does not prove remote exactly-once. CLI owners/public demo tokens are fixture inputs, not production authentication. Capacity calculations are analytic, not measured throughput.

No usable Docker daemon is available here. The workbench includes a non-root image, two-replica manifest and disposable-kind unavailable-image/explicit-undo exercise, but container/cluster/cloud execution remains an optional learner activity, as the original issue allows. Full manual assistive-technology conformance is not claimed.

## Final verification

Local content/package and root/subpath browser checks, exact per-PR revision gates, hosted CI and resolved-merge verification must pass before an issue is closed. The draft combined audit PR #70 remains separate; it is not a release artifact or a substitute for reviewing each focused PR.
