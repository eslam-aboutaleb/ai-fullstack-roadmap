# AI Full-Stack Engineering Roadmap

A learning journey through 48 chapters, from core programming and web foundations to AI systems, evaluation, and deployment. It includes 810 guided explanations and practice questions with code examples and walkthroughs.

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

The expanded site adds **Foundations courses**, **Capstones**, **Assessments**,
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
