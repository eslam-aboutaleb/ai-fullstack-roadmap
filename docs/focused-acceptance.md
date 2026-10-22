# Acceptance evidence: LLM/RAG, agents and full-stack

Reviewed 22 October 2026. This branch verifies issues #18. Related project sources are shared so every downloaded guide command is available; other issue acceptance remains separate until its own reviewed content and matrix merge.

The user delegated the final technical/content verdict to Codex. Records identify AI-authored/self-reviewed work with content-specific digests; no independent human SME endorsement is claimed. Original issue requirements remain binding. The original projects explicitly allow local/mock connectors and optional external-model/cloud exercises. Real protocol and browser integrations below are additional executed evidence, not mandatory live-vendor dependencies imported from separate advanced issues.

## Learning coverage

The chapter introduction, terminology and flow precede the existing foundation and deeper questions. 8 existing question IDs were expanded rather than copied into new hubs. 1 companion-unit interviews now contain complete explanations. 8 applied changed-assumption scenarios and 1 project rubrics are linked to practice/progress; self-review cannot grant an objective pass.

| Issue | Syllabus concepts | Stable topic / learner page | Assessment |
|---|---|---|---|
| #18 | agent vs workflow, planning/execution, tool selection, deterministic state machines | [381](../content/chapters/agent-patterns/questions.json), `agent-patterns.html#q381` | `acceptance-18-381` |
| #18 | tool calling protocol, structured schemas, authorization, least privilege | [393](../content/chapters/agent-harness/questions.json), `agent-harness.html#q393` | `acceptance-18-393` |
| #18 | MCP architecture, transports, capability discovery, agent protocols | [341](../content/chapters/mcp-foundations/questions.json), `mcp-foundations.html#q341` | `acceptance-18-341` |
| #18 | stop conditions, budgets, human approvals, state transitions | [392](../content/chapters/agent-harness/questions.json), `agent-harness.html#q392` | `acceptance-18-392` |
| #18 | concurrency, retries/compensation, durable state, failure recovery | [395](../content/chapters/agent-harness/questions.json), `agent-harness.html#q395` | `acceptance-18-395` |
| #18 | context management, memory boundaries, untrusted tool outputs/prompt injection | [301](../content/chapters/context-engineering/questions.json), `context-engineering.html#q301` | `acceptance-18-301` |
| #18 | tracing, trajectory evaluation, task success vs side effects, policy checks | [231](../content/chapters/agent-evaluation/questions.json), `agent-evaluation.html#q231` | `acceptance-18-231` |
| #18 | multi-agent tradeoffs, costs, delegation, recovery ownership | [371](../content/chapters/agent-orchestration/questions.json), `agent-orchestration.html#q371` | `acceptance-18-371` |

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
