# Content enrichment and technical-context review

Current chapter ordering and inventory are recorded in the [learning journey review](learning-journey-review.md). This report describes the preceding enrichment pass.

Updated 21 October 2026 after the reference/coverage audit. The project is a useful
learning base, but it is not yet a sufficient sole source for becoming a production
AI engineer. This pass expands the actual teaching and exercises, and corrects
misleading interview context. It does not claim universal topic coverage or
independent technical approval.

## What the learner now gets

| Course | Units | Main progression | Source |
| --- | ---: | --- | --- |
| Python/backend | 7 | Values and protocols → resources/types → OS/network/concurrency → authenticated transactional services → independent checks | [python-backend.json](../content/courses/python-backend.json) |
| Mathematics/models | 8 | Vectors/probability → derivatives → leakage/splits → backprop → NumPy/autograd → tokenization/attention → inference/adaptation | [math-models.json](../content/courses/math-models.json) |
| Frontend engineering | 4 | Semantic accessible UI → JS/TypeScript/React state → streaming framing/replay → browser security/performance | [frontend-engineering.json](../content/courses/frontend-engineering.json) |
| Data engineering | 4 | Data contracts/schema evolution → atomic CDC/checkpoints → event time/late data/backpressure → lineage/deletion/rebuild | [data-engineering.json](../content/courses/data-engineering.json) |
| LLM applications | 5 | Provider/output contracts → context/security budgets → lexical/hybrid retrieval and metrics → citation/abstention evaluation → safe agent/protocol effects | [llm-application-engineering.json](../content/courses/llm-application-engineering.json) |
| Production AI | 4 | Immutable releases/IaC → capacity/SLO/cost → telemetry/privacy/triage → restore drills/governance/release gates | [production-ai-engineering.json](../content/courses/production-ai-engineering.json) |
| Engineering practicum | 8 | Typed cumulative app → real-dataset evaluation → causal-model adapter → protocol clients → Beam/Kafka recovery → restore → independent review | [engineering-practicum.json](../content/courses/engineering-practicum.json) |

The seven courses contain **40 units**, about **11,800 words of mechanism narrative**,
40 worked cases and 40 interview defenses with detailed reasoning, follow-up
answers and review rubrics. Those counts exclude the older 330 guided chapter
lessons and 480 interview-bank questions; course units are counted separately.
Four units include explicit production incident walkthroughs. These quantities
measure authored material, not mastery or factual certification.

Each unit has measurable outcomes, prerequisites, defined terms, an actual local
reference exercise, independent work, debugging guidance, cost/alternative
analysis and primary references. Worked cases and interview defenses are now
required by the course schema. All units are in global lazy search and can be
filtered by course. Public counts come from source rather than a hardcoded total.

The first enrichment added ten graded scenarios, bringing the assessment set to 23;
the practicum follow-up adds six more for a current total of 29. They cover stale
responses, missing terminal events, atomic checkpoint rollback, late events,
retry-budget exhaustion, metric denominators, unsupported citations, capacity
assumptions, privacy release gates and tombstone replay. They point to actual
course topics and contribute local attempt evidence; subjective defenses remain
self-reviewed. Existing study IDs 1–825 are preserved; the first 17 additions use 826–842 and
the practicum additions use 843–850.

## Runnable boundary examples

- [streaming_reader.html](../labs/streaming_reader.html) is a self-contained browser
  fixture with normal/disconnected/malformed streams, cancellation/restart,
  incremental UTF-8 decoding, newline framing, exact replay deduplication,
  sequence-gap detection and inert rendering of markup. It is synthetic NDJSON,
  not a production SSE server or a React application.
- [data_contract_pipeline.py](../labs/data_contract_pipeline.py) demonstrates one
  source partition, schema adapters, payload-bound identities, atomic projection
  and checkpoints, injected rollback, stale revisions, quarantine and tombstones.
  SQLite is a transaction fixture; distributed destinations still need recovery.
- [llm_contracts.py](../labs/llm_contracts.py) uses a scripted provider to demonstrate
  context preflight, finite retry and conservative reservation, structural output
  checks and caller-scoped citation membership. It deliberately does not equate
  membership with semantic support or claim to reproduce provider billing.
- [retrieval_scorecard.py](../labs/retrieval_scorecard.py) supplies a scoped lexical
  BM25 baseline, deterministic RRF and hand-checked Recall/MRR/binary nDCG. Empty
  gold sets are kept separate from ordinary retrieval recall.
- [production_scorecard.py](../labs/production_scorecard.py) calculates a capacity
  estimate and error-budget burn under explicit assumptions, rejects critical
  disclosure/latency regressions and demonstrates telemetry attribute allowlisting.

The four Python references run with Python 3.11+ and the standard library.
Their deterministic verification routines are included in the normal content CI
contract. The browser suite exercises the actual HTML fixture and course evidence
flow. No provider account or hosted backend is required by these additions.

## Corrections to current interview context

All 40 enriched interview responses were rewritten to answer their own question,
with a concrete production case and an answered follow-up. This includes:

- MCP is not limited to local tools; remote HTTP capability access and its
  authorization contract must be distinguished from local STDIO operation.
- An eligibility decision and an operation-status lookup use different evidence.
  The previous enriched explanation incorrectly discussed JavaScript promises.
- Orchestration versus model/retrieval adapters now discusses responsibility and
  authority boundaries instead of an unrelated HTTP/DNS walkthrough.
- Mathematics prerequisites now contain a verified derivative example rather than
  an unrelated model-lineage object.
- Candidate-pool versus final-result limits now explains upstream recall, reranking
  and cost instead of answering a different RRF question.
- Migration-at-startup advice now covers serialized ownership, mixed-version
  compatibility, locking and rollback limits instead of generic health checks.
- AI/ML/DL/NLP/GenAI are no longer described as one universally nested hierarchy.
  Generated content is not contrasted with prediction as if they were exclusive.
- SSE does not automatically provide application backpressure, and WebSocket
  authentication is not universally restricted to a first-message pattern.
- Delimiters do not guarantee protection from prompt injection; source-ID
  membership does not prove citation support; a valid token/schema does not prove
  permission to act.
- Unsupported blanket asymptotic claims were replaced with explicit cost drivers:
  database index/query plans and contention, ANN settings and worst-case behavior,
  payload bytes, model tokens, downstream limits, queue age and effect recovery.

The corrected records remain draft. The review did not independently certify all
480 questions or all 330 legacy lessons. Where applicable, misleading definitions,
examples, outputs, citations and metadata were repaired as well as spoken answers.

## Remaining-gap implementation

The follow-up [practicum progress report](practicum-progress.md) records the actual
React/API application, digits experiment, low-rank causal-model adaptation,
official MCP/A2A clients, real Beam runner, real Kafka worker crash/replay and
snapshot recovery. The downloadable review packet supplies multilingual,
semantic, permission and manual accessibility tasks. Six more scenarios bring
the graded assessment set to 29, and the eight new units use IDs 843–850.

## Remaining work before claiming a sole learning source

1. Actual target GPU and foundation-model training/serving measurements, larger
   independently labeled datasets, and reviewed cumulative project work. CPU and
   miniature adapter results are deliberately scoped.
2. Real schema-registry/CDC connectors, multi-partition rebalancing, replicated
   broker failures and a distributed Beam runner. One local broker/partition and
   DirectRunner do not establish those properties.
3. Execute container and cluster rollout/undo drills and PostgreSQL PITR under a
   full application recovery oracle. Native Kafka and SQLite restore are verified;
   the container/cluster path remains pending in this Docker-unavailable environment.
4. Authenticated remote OAuth, durable restart/cancellation/continuation and
   cross-implementation MCP/A2A acceptance. The current public read-only paths have
   real client/transport evidence for the declared profiles.
5. Fluent multilingual claim/source adjudication, independent SME/editorial
   review, capstone defenses and manual assistive-technology observations. The
   packet supplies tasks, not fabricated reviewer approvals.
6. Continued source/version maintenance. Availability and a matching page identity
   do not prove completeness or support for every claim.

Use this as a structured core plus primary documentation, deliberate project work
and review feedback. Course depth, real practice and independently checked
reasoning are the acceptance standard; reaching a word/question count is not.

## Verification

See [current-verification.json](current-verification.json) for executed checks,
carried-forward baseline results and remaining limitations. Root and Pages-subpath
browser suites passed in isolated runs. Concurrent runs intermittently exceeded
the startup timeout; diagnostic navigation cycles showed no JavaScript error,
but the cause has not been established.
