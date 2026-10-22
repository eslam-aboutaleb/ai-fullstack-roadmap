# Acceptance evidence: LLM/RAG, agents and full-stack

Reviewed 22 October 2026. This branch verifies issues #17. Related project sources are shared so every downloaded guide command is available; other issue acceptance remains separate until its own reviewed content and matrix merge.

The user delegated the final technical/content verdict to Codex. Records identify AI-authored/self-reviewed work with content-specific digests; no independent human SME endorsement is claimed. Original issue requirements remain binding. The original projects explicitly allow local/mock connectors and optional external-model/cloud exercises. Real protocol and browser integrations below are additional executed evidence, not mandatory live-vendor dependencies imported from separate advanced issues.

## Learning coverage

The chapter introduction, terminology and flow precede the existing foundation and deeper questions. 12 existing question IDs were expanded rather than copied into new hubs. 4 companion-unit interviews now contain complete explanations. 12 applied changed-assumption scenarios and 1 project rubrics are linked to practice/progress; self-review cannot grant an objective pass.

| Issue | Syllabus concepts | Stable topic / learner page | Assessment |
|---|---|---|---|
| #17 | LLM APIs, token budgets, structured outputs, rate limits, retry/cost controls | [128](../content/chapters/models/questions.json), `models.html#q128` | `acceptance-17-128` |
| #17 | streaming, LLM lifecycle, cancellation | [421](../content/chapters/sse-streaming/questions.json), `sse-streaming.html#q421` | `acceptance-17-421` |
| #17 | ingestion/parsing/OCR, document provenance, revision publication | [81](../content/chapters/ingestion/questions.json), `ingestion.html#q81` | `acceptance-17-81` |
| #17 | chunking, context packing, provenance boundaries | [31](../content/chapters/chunking/questions.json), `chunking.html#q31` | `acceptance-17-31` |
| #17 | embeddings, dense retrieval, similarity profiles | [41](../content/chapters/embeddings/questions.json), `embeddings.html#q41` | `acceptance-17-41` |
| #17 | BM25, hybrid retrieval/RRF, ranking arithmetic | [63](../content/chapters/retrieval/questions.json), `retrieval.html#q63` | `acceptance-17-63` |
| #17 | ANN/HNSW, reranking, candidate/final limits | [65](../content/chapters/retrieval/questions.json), `retrieval.html#q65` | `acceptance-17-65` |
| #17 | citation fidelity, abstention, faithfulness, answer relevance, false refusal | [71](../content/chapters/evidence/questions.json), `evidence.html#q71` | `acceptance-17-71` |
| #17 | Recall@k, MRR, nDCG, gold datasets, metric oracles | [111](../content/chapters/evaluation/questions.json), `evaluation.html#q111` | `acceptance-17-111` |
| #17 | offline/online eval, trace analysis, regression release, latency, observability | [119](../content/chapters/evaluation/questions.json), `evaluation.html#q119` | `acceptance-17-119` |
| #17 | caching, tenant isolation, cache invalidation, token efficiency | [316](../content/chapters/context-optimization/questions.json), `context-optimization.html#q316` | `acceptance-17-316` |
| #17 | prompt injection, prompt contracts, tool interface design, security | [321](../content/chapters/prompt-foundations/questions.json), `prompt-foundations.html#q321` | `acceptance-17-321` |

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
