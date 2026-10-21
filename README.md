# AI Full-Stack Engineering Roadmap

**Live site:** [AI Full-Stack Engineering Roadmap](https://eslam-aboutaleb.github.io/ai-fullstack-roadmap/)

A prerequisite-ordered learning journey through 56 chapters: programming and the web first, then backend/data, mathematics, ML/deep learning, model applications, RAG, agents and production. It teaches through 1,103 question-and-answer entries on the chapter pages (356 foundation explanations and 747 deeper interview questions), plus 40 companion course units. Answers include worked examples and in-answer acronym definitions; chapters have no question-count limit.

## Static architecture

The published site is a **GitHub Pages-only static application**: HTML, CSS, JavaScript, JSON, SVG, and optional browser-side WebAssembly. There is no production backend, database, serverless function, auth server, or mandatory external API. Build-time tooling is allowed; runtime secrets and hosted services are prohibited. Exercises needing real servers ship as downloadable local-first labs. See [docs/architecture.md](docs/architecture.md) for the full decision and constraints.

## Contents

- `content/chapters/` — chapter lessons, questions, and review notes
- `content/examples/` — chapter and question code examples
- `content/shared/` — study IDs, glossary, and references
- `content/diagrams/` — learning journey diagrams
- `assets/` — site styles and browser scripts
- `labs/` — optional hands-on integration labs
- `scripts/` — site build and packaging tools
- `tests/` — content and build checks
- `docs/` — repository structure and verification notes

For setup, editing content, adding questions, and running checks, see the [contribution guide](CONTRIBUTING.md).

The [implementation review of issues 1–16](docs/implementation-review.md) records
verified fixes and outstanding acceptance requirements. Several requested platform
features and full courses remain incomplete.

The expanded site adds **Engineering courses**, **Capstones**, **Assessments**,
**Coding labs**, **My study record**, a **Question bank**, and a **Curriculum map**
to the course navigation. Notes and practice evidence use browser-local IndexedDB
with a recoverable export; no account or backend is required.

Use `make check` and `make serve` to verify and preview. `make runtime` installs the
optional pinned browser Python assets for local previews; CI includes those assets
in the static Pages artifact. Backend and model-training projects remain local-only.

Current acceptance review for issues 1–21: [implementation progress and remaining criteria](docs/acceptance-progress.md). Executed checks: [verification evidence](docs/current-verification.json).

CI inherits SHA-pinned project, workflow-lint and security checks from
[`ci-workflows`](https://github.com/eslam-aboutaleb/ci-workflows).
See [the inheritance contract](docs/ci-inheritance.md) for selected checks and release gates.

Content coverage and reference audit: [full-stack gap analysis](docs/fullstack-coverage-audit.md),
[Live reference status and source mapping](docs/reference-link-audit.md), and the
[machine-readable link results](docs/reference-link-audit.json). Rerun live links
with `python3 scripts/audit_references.py`; network results are intentionally not a CI gate.

The expanded engineering courses now include frontend, data pipelines, LLM/retrieval
and production operations, with worked cases and interview defenses. See the
[content enrichment review](docs/content-enrichment-review.md) for the current
40-unit scope, new local exercises and remaining learning-source limitations.

The [engineering practicum](content/courses/engineering-practicum.json) adds a
compiled React/API project, real-dataset selection and uncertainty, a measured
causal-model adapter, official MCP/A2A clients, Beam late panes, actual Kafka worker
crash/replay and restore drills. See [remaining-gap progress](docs/practicum-progress.md)
for executed evidence and the boundaries still needing independent work.

See the [learning journey and topic review](docs/learning-journey-review.md) for
chapter order, context repairs, uncapped interview authoring and verification.

See the [interview-led chapter review](docs/interview-led-chapters.md) for same-page answers, content additions and verification.

The [answer formatting review](docs/answer-format-review.md) documents the single detailed answer layout, diagrams, code and duplicate suppression.

The [learning experience and design review](docs/learning-experience-design-review.md) covers chapter question finding and advanced scenarios for context limits, huge uploads, metadata and agent architecture choices.
