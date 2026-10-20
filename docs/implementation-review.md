# Implementation review: GitHub issues 1–16

**Historical baseline:** this review predates the subsequent implementation pass.
See [acceptance-progress.md](acceptance-progress.md) for the current review of
issues 1–21 and [current-verification.json](current-verification.json) for current
executed checks. Missing features listed below may since have been implemented.

Reviewed on 20 October 2026 against the issue bodies in
[eslam-aboutaleb/ai-fullstack-roadmap](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues).
The old local remote name `rag-learning-guide-site` redirects to this repository.
The review includes the other agent's uncommitted workspace implementation.

**Verdict: the implementation does not meet the acceptance criteria for all 16
issues.** It extends a useful static course, but several proposed features exist
only as documentation, schemas, short examples, or project descriptions. The issues
were all still open when inspected. No issue was closed or marked complete by this
review. Independent subject-matter review and WCAG conformance are not established
by the automated checks.

## Acceptance matrix

| Issue | Status after review fixes | Evidence and remaining work |
| --- | --- | --- |
| [1](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/1) Static architecture | Substantial; deployment verification outstanding | Static packaging, internal links, asset budgets, root/subpath browser checks, main-only deployment and immutable action pins exist. CI now produces a repository-prefixed artifact. The published URL returned HTTP 200, but these local fixes have not been published or checked in a new Pages release. Downloaded reading works; enhanced controls require JS. |
| [2](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/2) Curriculum audit and DAG | Partial | All 48 chapters appear in seven tracks with 64 prerequisite edges. Validation now rejects duplicate membership, mismatched track IDs, invalid entry points, cycles, and incorrect coverage counts. Pages use the manifest prerequisites. The requested inventory of factual accuracy, overlap, individual outcomes and assessments is not exhaustive. |
| [3](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/3) Rigorous pilots | Partial | Three enriched records exist and are now actually rendered, including local sources, diagrams, glossary and references. They concern a reservation race, request validation and an effect oracle. They do not constitute the requested complete asyncio, authenticated FastAPI/transaction and RAG-evaluation courses. Independent SME approval is pending. |
| [4](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/4) Reader and skill map | Partial | Existing chapter reader, glossary, TOC, progress, diagrams and search retained. Track links are discoverable; nested search URLs, modal keyboard containment/focus restoration and no-JS transcripts are repaired. No comprehensive screen-reader/contrast audit, prerequisite graph UI, or line-annotation system. |
| [5](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/5) Mastery and storage | Partial | localStorage notes/bookmarks/self-reports, JSON export/import, and a simple 1/3/doubling-day review schedule. Import now preserves all fields, null schedules cannot crash initialization, and nested pages preserve IDs. Added explicit re-review and clear controls. IndexedDB, evidence-linked Familiar/Practiced/Independent/Mastered states, attempt evidence and conflict-safe multi-tab migration remain missing. |
| [6](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/6) Browser coding labs | Missing workbench | Downloadable JS/Node files now have meaningful throwing assertions and deterministic clocks. They are not an editor/runner. No Worker execution, timeout/output limits, Pyodide, package allowlist or in-page grading. Documentation now makes this distinction explicit. |
| [7](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/7) Connected capstones | Partial | Capstone guidance and a small local HTTP/streaming sample exist. Four independently buildable starter/reference projects with threat models, fault injection and acceptance suites are absent. Project descriptions are not runnable implementations. |
| [8](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/8) Visualizers | Partial | Chapter step-through diagrams, failure toggles, four overview diagrams and deterministic RAG fixtures exist. Complete no-JS step transcripts are now present. These are not four newly implemented scheduling/locking/retry state machines with tested typed transition fixtures. |
| [9](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/9) Assessments | Missing assessment engine | Reveal controls and confidence ratings are self-reports. No deterministic quiz grading, distractor feedback, seeded assessment ordering, incident tasks or stored assessment attempts. Rating active state is repaired; it is not evidence of mastery. |
| [10](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/10) Quality gates | Partial, strengthened | Content/ID/link/example checks now include recursive schema validation, mutation fixtures, actual rendered source comparisons, JS lab execution, Chromium user flows, local FastAPI tests, and root/Pages subpath checks. Action versions are commit-pinned. Exhaustive external-source freshness, semantic duplicate review, dependency vulnerability scanning and an AA audit remain absent. |
| [11](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/11) Exhaustive blueprint | Partial | Versioned seven-track manifest and four sample syllabus summaries exist. These are not the specified module-by-module blueprint across all math, ML, data, cloud and inference subjects, with stable learning-outcome IDs and assessment mappings. Track migration indicators describe enriched content rather than learner or course completion. |
| [12](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/12) Content schemas | Partial, validation repaired | Three enriched lessons and 16 enriched interview entries now pass recursive schemas; enum, nested object/list, range and date validation works. Removed the accidental 200-character spoken-answer limit. The short answers are honestly labeled concise rather than 60–120 seconds. Schema completeness cannot prove jargon coverage, depth, independent review or technical accuracy. Legacy entries retain their original smaller contract. |
| [13](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/13) 1,000+ question bank | Not delivered | No uniform ten-question quota is enforced and IDs remain stable. But there are no paginated topic shards, per-track lazy search indexes, semantic near-duplicate reports or a 1,200-entry build/navigation fixture. The current global search and full chapter DOM do not meet the scaling specification. |
| [14](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/14) Source fidelity | Fixed and regression-tested locally | The historical placeholder highlighter corrupts simple quoted source (reproduced below). Replaced by a tokenizer that creates DOM text nodes; copying uses captured original source. All 810 catalogued sources are compared against generated HTML. Real Chromium tests exercise 19 fixtures, idempotence, literal tokens, entities, Unicode and clipboard text. Publishing the fix remains outstanding. |
| [15](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/15) Python/CS/backend courses | Not complete | Existing foundation/SQL/API material is retained, and reservation/request pilots are repaired. No complete language/data-model/OS/networking/asyncio/backend syllabus with the requested progressive projects and independently reviewed long-form teaching. |
| [16](https://github.com/eslam-aboutaleb/ai-fullstack-roadmap/issues/16) Math/ML/transformer courses | Not complete | Existing numerical foundation bridge and model explanations remain useful. There is no complete first-principles attention/backprop/tokenization sequence, NumPy-to-PyTorch progression, or complete model training/evaluation capstone. A sample syllabus title is not an implemented course. |

## Defects repaired

- `course_data.load()` previously validated only the last `lessons` group; the
  question-validation branch was unreachable. Its helper ignored array items,
  numeric bounds, enums, boolean/integer distinctions and nested required fields.
  Enriched records now receive recursive validation even without `added: true`.
- Published rich pilot fields were silently discarded by the renderer. They now
  appear as escaped semantic HTML, code, glossary definitions, expected output,
  independent tasks, references and accessible figures. SVG uses an explicit
  tag/attribute allowlist and unique marker IDs. Malformed/clipped pilot SVG was
  corrected. Local lab links now point to the relevant downloadable project.
- The reservation example used one default SQLite connection from other threads,
  producing `ProgrammingError` rather than testing a reservation invariant. The
  replacement uses one connection per thread and a shared temporary database,
  checks both outcomes and the committed row count, and leaves winner identity
  unspecified. SQLite write serialization is clearly distinguished from a
  PostgreSQL transaction-isolation demonstration.
- The effect oracle contained unconditional `True` approval checks. The replacement
  checks event ordering and authorization, exact state, and write count. Negative
  fixtures reject missing approval, duplicate rows and unauthorized reads.
- New example strings contained literal `\\n`, misleading HTTP status `201
  Accepted`, an incorrectly ordered PostgreSQL locking clause with a double-quoted
  string, checkpoint advancement before ingestion, and an incorrect model taxonomy.
  These were corrected; illustrations are not presented as standalone runnable code.
- Import discarded confidence, reviews and focus settings. Null review maps could
  prevent app initialization. Track pages had no ID range; saving there could lose
  known progress. State is now sanitized and preserved, and tested through export,
  import, nested navigation, malformed files and blocked browser storage.
- The rating handler queried attributes absent from buttons. It now refreshes the
  actual controls. Search on nested pages now loads its index and resolves result
  URLs against the application script, not the track directory. Modal search traps
  Tab, makes the background inert and restores focus.
- RRF expected the wrong winner and five unique IDs from a seven-ID union;
  `console.assert` then printed success without failing the process. All JS labs
  now throw on failure. RRF rejects duplicate ranking IDs; the token bucket uses
  an injected clock instead of blocking a browser thread; the agent fixture
  enforces terminal states, tool permissions and a retry budget.
- The base-path checker included fragments in relative filesystem names and the
  main check inherited the deployment base during its local-only phase. Both were
  repaired. CI now tests the exact prefixed artifact that it uploads.
- Removed misleading automated approval/completion labels. Sixteen enriched
  questions remain drafts awaiting independent technical review. Source counts,
  suggested experiments, downloads and chapters with review notes are distinguished.

## Quotation corruption reproduction

The committed pre-review highlighter (`5c243d4:assets/js/app.js`) replaces strings
with `@@@TOK0@@@` and then applies a decorator regex to that placeholder. The
`@TOK0` portion is interpreted as a decorator and replaced again; reinsertion no
longer finds the original string placeholder. This is reproducible in Chromium
with `x = "hello"`, whose rendered text becomes `x = @@@TOK0@@@`; it is not an upstream JSON quote substitution. The reviewed
workspace attempted a regex repair, but its Python test reimplemented the
algorithm instead of running browser JavaScript, so it could not establish DOM
or clipboard fidelity. The replacement uses actual DOM nodes, never reparses code
as HTML, and copies captured original text. The original literal token is valid
source data and must survive unchanged, not be rejected.

## Verification and limits

Commands and exact results are recorded in `docs/review-verification.json` after
completion of local checks. The ordinary content check executes catalogued Python
examples and local JS labs, compares all 810 rendered sources, validates the DAG,
and checks internal files/anchors. Optional Chromium checks cover the repaired
user flows at both root and repository subpath; the optional FastAPI pilot checks
valid, blank, missing, oversized, wrong-type and malformed requests.

The existing live Pages landing page returned HTTP 200. The latest existing remote
Actions run for commit `5c243d4` succeeded. Neither fact verifies unpublished local
changes. This review does not claim live deployment, complete visual accessibility,
complete content correctness, optional provider integrations, external link health,
or completion of unfinished issue acceptance criteria.

## Recommended next implementation order

1. Finish the real asyncio/FastAPI/evaluation pilots and independent review before
   expanding their pattern. Preserve stable study IDs.
2. Implement the evidence and attempt model for mastery and assessments together;
   add versioned IndexedDB persistence and tested migration/recovery.
3. Deliver one Worker-backed JS lab with truthful limits, then optional pinned
   browser Python. Keep server/database exercises downloadable and local.
4. Build sharded/paginated question delivery and a distinct 1,200-record stress
   fixture before expanding content volume.
5. Complete the missing textbook courses and connected capstones, using measured
   outcome coverage rather than a generated question-count target.
