# Learning journey and topic-context review

Reviewed 21 October 2026. The main reader previously started with RAG even though
programming and web material existed in separate companion courses. The actual
chapter path, home entry point, sidebar, track entry points, previous/next links
and course index now follow prerequisite order.

The subsequent [interview-led chapter pass](interview-led-chapters.md) expands this
inventory and includes all answers on each chapter page. Counts below describe
the earlier journey-reorganization pass.

## Published progression

| Stage | Learning goal | Chapters |
| --- | --- | --- |
| 1 | Write programs and understand the web | Programming/Python/workflow → CS/OS/concurrency → HTTP/APIs → HTML/CSS/JS/TypeScript/React |
| 2 | Build trustworthy backend and data systems | Relational modeling → API/database security → concurrency → source/data contracts → ingestion/recovery |
| 3 | Learn mathematics and models | Linear algebra/probability/statistics/gradients → ML features/splits/baselines → neural networks/autograd/tokenization/attention → model capabilities |
| 4 | Design basic model interactions | Prompt contracts and techniques, after model fundamentals |
| 5 | Build retrieval and evidence-grounded applications | RAG → application boundaries → OCR/chunking/embeddings/storage/retrieval → evidence/applicability/context → evaluation engineering |
| 6 | Deliver interfaces and realtime behavior | Product delivery → SSE → WebSocket → voice |
| 7 | Choose controlled agents and protocols | Harnesses/patterns/orchestration → framework choices → skills → MCP → A2A → delegated backends |
| 8 | Evaluate and operate | Live behavior → agent evaluation/observability → model releases → deployment/recovery |
| 9 | Integrate and defend | Connected full-stack implementation and portfolio capstone |

**RAG is chapter 20**, after 19 prerequisite chapters. Programming foundations is
chapter 1. The main CTA and first four chapter cards lead to programming, computer
science, web and frontend fundamentals. Existing chapter URLs are preserved;
`foundations.html` still contains RAG and its original study identities.

The validator now rejects an acyclic graph whose published chapter order puts a
prerequisite after its dependent. Tracks must preserve this order and begin at
their first listed chapter. Companion courses have an explicit order instead of
alphabetical discovery, and their index points beginners to the main chapter path.
Individual unit prerequisites remain visible because a companion course can span
more than one main-journey stage.

## Content and interview additions

Eight new foundation chapters contain 26 guided lessons. The additions bring the
whole chapter collection to **356 lessons and 590 interview questions**, alongside
**40 companion course units**. All 850 previous study identities remain unchanged;
136 additions use 851–986. New question identities are appended, never renumbered
according to their position in the journey.

The 110 new interview records include:

- 62 questions on Python/value ownership, exceptions, iterators, type boundaries,
  testing/Git, complexity, processes, scheduling, memory, HTTP, browser security,
  pagination, responsive/accessible UI, React state/effects, runtime narrowing,
  linear algebra, probability, statistics, optimization, classical ML, neural
  architectures, tokenization/attention, inference and data pipelines.
- A distinct scenario/design defense for each of the original 48 chapters,
  covering authority/applicability, cache scope, source provenance, extraction,
  indexing/ranking, evidence support, tool effects, protocol profiles, realtime
  interruption, evaluation, observability and deployment/recovery.

Each added question has a direct answer, concrete engineering case, answered
follow-up and primary citations. They remain draft pending independent review.
Question JSON fixtures are explicitly labeled reasoning inputs: parsing their
representation is not presented as execution of the real mechanism. The chapter
examples and linked local projects supply actual runnable references.

There is **no topic question-count cap or fixed authoring target**. Existing
`questions-*.json` shards remain supported. Forty full answers per delivered page
is a browser/HTML pagination budget, not a maximum for a subject. Questions should
be added when they cover a distinct mechanism, failure, implementation decision or
trade-off, rather than to make every chapter reach the same number.

## Context repairs and worked mechanisms

- Programming entry lessons now teach values, ownership, functions/types, ordinary
  tests and a reproducible Git workflow. They no longer require starting with
  model terminology or a transactional API delivery lesson.
- HTTP explains name resolution/connection/TLS, request and representation,
  error contracts, retry identity and browser-origin boundaries before the
  optional framework exercise.
- Probability includes a 10,000-case table: 90 true positives and 99 false alerts
  imply 90/189 alert precision despite 90/100 positive recall. Its executable
  example checks those separate denominators.
- Classical ML explains regression/logistic decisions, tree/ensemble mechanisms,
  K-means assignment/update and PCA limitations, with a four-point centroid
  calculation and a link to the real digits evaluation project.
- Neural architecture teaching compares dense, convolutional, recurrent and
  attention models. A checked calculation derives 448 parameters for a 3-input,
  16-output, 3×3 convolution with bias; parameter count is not confused with peak
  training memory or latency.
- The classical model-selection unit now requires the train/split lesson, rather
  than an unrelated language-model inference/adaptation unit.
- The relational revision example no longer declares UNIQUE(owner_id, revision),
  which would prohibit an owner from having two unrelated revision-one documents.
  Documents and per-document revision identity are modeled separately.

The existing source-linked long-form course explanations are exposed through the
new foundation chapters and companion-unit links. This makes them reachable in
the main path; it does not count the same companion unit as another new course.

## Coverage and verification evidence

The generated `topic-coverage.html` and `questions/topic-coverage.json` enumerate
every chapter in learning order with defined terms, taught lessons, interview
identities, answered follow-ups and companion units. They distinguish an authored
inventory from independent approval; counts alone do not prove semantic completeness.
The curriculum map retains short-legacy-lesson review priorities.

Relevant primary sources were revisited, including Python control flow, HTML
structure, TypeScript narrowing, scikit-learn leakage, tree/ensemble/clustering
mechanisms and PyTorch convolution/recurrent contracts. The catalog has 104
source destinations with recorded successful availability checks and content uses;
see [reference audit](reference-link-audit.json). Availability and targeted reads
are not certification of every legacy assertion.

See [current verification](current-verification.json) for the executed build,
source-fidelity, browser, accessibility and scale checks. The first-card/CTA browser
regression and a prerequisite-inverted-but-acyclic negative fixture protect the
reported journey. Source counts and stable identities are checked automatically.

Independent semantic/editorial, fluent-language and manual assistive-technology
review remain open. The hardware/distributed/runtime limits recorded in the
[practicum report](practicum-progress.md) also remain; the reorder does not turn
unexecuted work into a passed acceptance result.
