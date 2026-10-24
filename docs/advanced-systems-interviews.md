# Advanced systems interview additions

Added 16 standalone questions, 32 detailed follow-ups, 16 answer diagrams and 16 executable Python examples. The public learning material uses generic tasks, jobs, procedures, answers and notifications. It contains no references to another application or its repository.

## Coverage and chapter placement

| Topic | Chapter | Main questions |
| --- | --- | --- |
| Atomic index publication and representation fingerprints | Ingestion | Replacement-generation visibility; source versus representation changes |
| Job claiming and stale-worker completion | Coordination | Durable ownership after row selection; destination and completion fencing |
| Distributed idempotency | Database concurrency | Publication/release ordering; coordination-outage admission |
| Complete procedures | Application architecture; Skills layers | Manifest completeness; pinned-version migration and revocation |
| Durable answers and feedback | SSE streaming; Product delivery | Generation versus persistence versus domain outcomes; ownership and answer revisions |
| Evaluation validity and abstention | Evaluation engineering; Agent evaluation | Proxy versus live evidence; refusal and false-refusal denominators |
| Hybrid retrieval correctness | Retrieval | Missing versus zero distances; invariant-based regression matrices |
| Notification intent and delivery | Coordination; Deployment reliability | Business/outbox atomicity; destination deduplication after lost acknowledgment |

Every main answer explains the invariant, failure sequence, implementation boundary, recovery rule and tradeoff. Each includes a worked case, a learner exercise, two follow-up answers, a diagram and primary documentation links.

## Example evidence

All examples use Python standard-library code and synthetic data. The authoring pass executed every example and compared stdout against an independently declared expected output. Assertions cover negative paths as well as useful behavior.

Five examples execute real SQLite statements for transaction rollback, guarded transitions, stale-attempt rejection or uniqueness. They are local database demonstrations; they do not claim PostgreSQL concurrency, distributed transactions or external provider delivery. The remaining examples isolate deterministic schedules, state contracts, metrics, manifests, fingerprints and result serialization. Their displayed explanations state these boundaries.

Primary references checked during authoring: PostgreSQL transaction isolation and SELECT locking, Redis distributed-lock ownership guidance, WHATWG Server-Sent Events, SQLite transaction semantics and scikit-learn evaluation documentation. The application-level failure scenarios and numerical fixtures are original worked exercises rather than production benchmark claims.

Independent technical review remains pending under the existing content-review contract. Live Redis, PostgreSQL multi-worker and notification-provider behavior are exercises to implement, not execution results asserted by these examples.

Validation: `make check` passed with 202 pages, 22,592 internal links, 1,119 chapter questions, 65 answer diagrams and 982 rendered code associations. All 763 deeper-question titles passed lexical duplicate checks. Existing root/subpath packaging and stable identity checks passed.
Root Chromium checks passed, including discovery of all 31 advanced scenarios and the new stale-worker answer with code. All 30 automated accessibility template/theme checks passed.
