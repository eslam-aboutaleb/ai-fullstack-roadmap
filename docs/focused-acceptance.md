# Acceptance evidence: LLM/RAG, agents and full-stack

Reviewed 22 October 2026. Scope in this resolved branch: issues #17, #18.

The user delegated the final technical/content verdict to Codex. Records identify AI-authored/self-reviewed work with content-specific digests; no independent human SME endorsement is claimed. Original issue requirements remain binding. The original projects explicitly allow local/mock connectors and optional external-model/cloud exercises. Real protocol and browser integrations below are additional executed evidence, not mandatory live-vendor dependencies imported from separate advanced issues.

## Learning coverage

The chapter introduction, terminology and flow precede the existing foundation and deeper questions. 20 existing question IDs were expanded rather than copied into new hubs. 5 companion-unit interviews now contain complete explanations. 20 applied changed-assumption scenarios and 2 project rubrics are linked to practice/progress; self-review cannot grant an objective pass.

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
| #18 | agent vs workflow, planning/execution, tool selection, deterministic state machines | [381](../content/chapters/agent-patterns/questions.json), `agent-patterns.html#q381` | `acceptance-18-381` |
| #18 | tool calling protocol, structured schemas, authorization, least privilege | [393](../content/chapters/agent-harness/questions.json), `agent-harness.html#q393` | `acceptance-18-393` |
| #18 | MCP architecture, transports, capability discovery, agent protocols | [341](../content/chapters/mcp-foundations/questions.json), `mcp-foundations.html#q341` | `acceptance-18-341` |
| #18 | stop conditions, budgets, human approvals, state transitions | [392](../content/chapters/agent-harness/questions.json), `agent-harness.html#q392` | `acceptance-18-392` |
| #18 | concurrency, retries/compensation, durable state, failure recovery | [395](../content/chapters/agent-harness/questions.json), `agent-harness.html#q395` | `acceptance-18-395` |
| #18 | context management, memory boundaries, untrusted tool outputs/prompt injection | [301](../content/chapters/context-engineering/questions.json), `context-engineering.html#q301` | `acceptance-18-301` |
| #18 | tracing, trajectory evaluation, task success vs side effects, policy checks | [231](../content/chapters/agent-evaluation/questions.json), `agent-evaluation.html#q231` | `acceptance-18-231` |
| #18 | multi-agent tradeoffs, costs, delegation, recovery ownership | [371](../content/chapters/agent-orchestration/questions.json), `agent-orchestration.html#q371` | `acceptance-18-371` |

The machine-readable matrix is `content/shared/focused-acceptance.json`: source paths, outcome IDs, introduction/reader anchors, question IDs, unit outcomes, labs and assessments. Original instruction in the surrounding chapters remains available. Eight original accessible/printable ordered diagrams illustrate ingestion publication, chunk exceptions, ranking, release gating, approval/recovery, effects, CDC and capacity.

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
