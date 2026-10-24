# Remaining-gap implementation and source-context review

Current chapter ordering and inventory are recorded in the [learning journey review](learning-journey-review.md). This report describes the preceding enrichment pass.

Updated 21 October 2026. This follow-up adds eight practicum units to the prior
32-unit edition: **seven courses, 40 units, 40 worked cases and 40 interview
defenses**, with 29 graded scenarios. Original study identities 1–842 are
preserved; the eight additions use 843–850. The sequence is prerequisite driven,
so numeric identity order is not necessarily presentation order.

## What is now implemented

| Earlier gap | New implementation | Executed evidence and limits |
| --- | --- | --- |
| A cumulative typed browser/API application | [Evidence workbench](../projects/evidence-workbench/README.md): strict TypeScript, React, unknown-value parsing, scoped Python HTTP API, bounded NDJSON, cancellation/deadline, stale identity invalidation, abstention and inert text | Compiled production assets and actual HTTP/Chromium flows passed, including mobile/keyboard and an axe scan. The two public demo credentials are fixtures; production login and admission control remain extensions. |
| More substantial model evaluation | [model_selection.py](../labs/model_selection.py): real bundled digits data, training-only preprocessing, validation-only selection, held-out baseline, error indices/confusion matrix, Wilson and paired-bootstrap intervals, corruption slice and CPU timings | 1,797 rows; split 1,078/359/360. Observed held-out accuracy 96.67%, baseline 10.28%, Wilson interval approximately 94.26–98.08%. Corruption accuracy was 51.67%. Row sampling is not writer-independent; these results are not production quality estimates. |
| Training/adaptation and measurement | [adapter_training.py](../labs/adapter_training.py): a tiny causal character LM, frozen base, low-rank output-head optimization, base/vocabulary/data manifests, reload, incompatible-base rejection and causal-prefix checks | CPU path passed. 296 of 12,594 parameters are trainable. Training/validation losses, elapsed time and parameter bytes are recorded. Authored miniature corpus and output-head-only adaptation do not establish foundation-model SFT quality. CUDA is opt-in and unmeasured locally. |
| Versioned protocol interoperability | [protocol_interop.py](../labs/protocol_interop.py): official MCP 2.3.0 and A2A 1.2.3 clients, actual subprocess STDIO and loopback HTTP, discovery, input/denial errors, streamed task status and authoritative readback | MCP profile 2026-07-28 asserted on both transports; A2A 1.0 JSON-RPC/SSE and unsupported-version rejection passed. OAuth, tenant policy, durable task restart and cross-vendor conformance are separate acceptance work. |
| Actual streaming execution | [beam_event_time.py](../labs/beam_event_time.py): Beam DirectRunner, timestamped windows, watermarks, late triggers and accumulating panes | Actual emitted totals 5 then 12 passed; a beyond-lateness event did not yield 112. This exercises runner semantics under TestStream, not a distributed checkpoint or real source watermark. |
| Actual broker and worker recovery | [kafka_recovery.py](../labs/kafka_recovery.py) and [native harness](../scripts/test_kafka_recovery.py): official Kafka 4.3.1 distribution verified with SHA-512, real topic, killed worker, durable destination and restart | Exit 73 after destination commit/before acknowledgment, one replay, final checkpoint 6, revision-4 tombstone and one quarantine passed. One partition/worker/local replica; no multi-partition rebalance, connector or HA claim. |
| Restore and rollout practice | [restore_drill.py](../labs/restore_drill.py), plus a non-root Dockerfile and Kubernetes rollout/undo instructions in the cumulative project | A real SQLite snapshot restore passed integrity and visible-row checks, detected a lost insert and reapplied newer deletion intent. Container and cluster execution remain pending because the local Docker daemon did not respond. |
| Independent semantic, multilingual and accessibility review | [Review packet](../projects/review-packet/README.md): artifact identity, changed-assumption interview defenses, risk slices, claim/source adjudication, manual interaction tasks and release decisions | Packet is downloadable. Automated workbench accessibility/keyboard checks passed. Fluent language review, independent technical approval and screen-reader observations are not fabricated or marked passed. |

The downloadable all-project ZIP now includes both project directories, source
locks, optional dependency requirements and native Kafka harness. It excludes
node_modules, compiled dist directories, Python caches and private runtime files.
The static roadmap still has no hosted backend or runtime provider credentials.

## References visited and changes they informed

The catalog now has **99 destinations**. Every destination has a recorded HTTP 200
check and a content use; [the audit](reference-link-audit.json) preserves per-link
check times and retrieved identities. This is availability evidence. The following
source reads informed specific teaching and implementation changes, with inline
source-context notes in each new unit:

- [React Effects](https://react.dev/learn/synchronizing-with-effects) and
  [TypeScript narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html):
  submission events versus cleanup, obsolete asynchronous results and runtime
  contract checks. The cumulative project applies those boundaries in a compiled app.
- [Vite](https://vite.dev/guide/): a separate local application build contract and
  supported Node environment, without adding React runtime dependencies to the reader.
- [Data leakage](https://scikit-learn.org/stable/common_pitfalls.html),
  [cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html),
  [calibration](https://scikit-learn.org/stable/modules/calibration.html) and
  [NIST proportion intervals](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm):
  train-only transformations, split assumptions, validation selection and uncertainty.
  Lower log loss is not described as proof of improved calibration alone.
- [LoRA](https://arxiv.org/abs/2106.09685),
  [PyTorch profiling](https://docs.pytorch.org/tutorials/recipes/recipes/profiler_recipe.html)
  and [allocated memory](https://docs.pytorch.org/docs/2.14/generated/torch.cuda.memory.max_memory_allocated.html):
  explicit matrix shapes, frozen-weight proof and measurement scope. The miniature
  output-head experiment is distinguished from large-model results in the paper.
- [MCP SDK v2](https://py.sdk.modelcontextprotocol.io/get-started/first-steps/),
  [versioned tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools),
  [authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization),
  [A2A 1.0](https://a2a-protocol.org/v1.0.0/specification/) and the
  [official A2A SDK](https://github.com/a2aproject/a2a-python): actual profile assertions,
  SDK-major distinctions, artifact/task separation and explicit compatibility limits.
- [Beam](https://beam.apache.org/documentation/programming-guide/),
  [Kafka quickstart](https://kafka.apache.org/quickstart/) and the
  [client API](https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html):
  lateness/accumulation, producer delivery callbacks and explicit consumer offset commits.
  Separate broker and database commits are not mislabeled as a distributed transaction.
- [SQLite backup](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup),
  [PostgreSQL recovery](https://www.postgresql.org/docs/current/backup.html) and
  [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/):
  observed restore scope, database-specific recovery boundaries and the fact that a
  progress deadline reports a stalled rollout rather than performing automatic rollback.
- [WAI review](https://www.w3.org/WAI/test-evaluate/preliminary/) and
  [OpenTelemetry privacy](https://opentelemetry.io/docs/security/handling-sensitive-data/):
  manual task evidence, data minimization and the limits of both preliminary
  accessibility scans and hashing predictable identifiers.

The source-context notes state the source's role and the local exercise's limit.
Neither a fetched page nor this targeted review certifies every legacy assertion
across all 480 interview records and 330 guided lessons.

## Verification and CI

[Observed integration results](../content/advanced-results.json) include the exact
local outputs and environments. [Current verification](current-verification.json)
records the broader build/browser checks and pending work. Dedicated CI now runs
the real-dataset, Beam, official-client and checksum-pinned native Kafka exercises;
the existing CPU model job also runs adapter training. The browser job compiles
and exercises the React/API project. A non-root container smoke check is required
in CI, with hosted execution still unobserved. Shared CI inheritance and its
reviewed commit pin remain intact.

The model requirement now matches the CPU-wheel version already explicitly
installed by CI (PyTorch 2.14.1), avoiding a subsequent downgrade. The updated
NumPy/autograd bridge passed locally with NumPy 2.0.2 and PyTorch 2.14.1.

## Still requires real completion evidence

- Target GPU/foundation-model experiments and larger independently labeled datasets.
- Replicated broker failure, multi-partition rebalance, real CDC/schema-registry
  connectors and distributed runner checkpoint/restart acceptance.
- Executed container/cluster rollout recovery and application-level PostgreSQL PITR.
- Authenticated, durable and cross-implementation MCP/A2A acceptance.
- Independent technical, fluent-language, capstone-defense and assistive-technology review.

These are explicit project/review requirements, not hidden qualifications to a
claim of universal completeness. The roadmap is an expanded core that still needs
implementation practice, primary documentation and independent feedback.
