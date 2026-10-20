# Architecture decision: GitHub Pages-only static application

## Decision

The published AI Full-Stack Engineering Roadmap is a **static site only**, served exclusively by GitHub Pages. The public artifact contains HTML, CSS, JavaScript, JSON, SVG, and optional browser-side WebAssembly. Build-time tooling (Python scripts, GitHub Actions, local CLI) is permitted, but the deployed site must never depend on:

- A production backend or application server
- A database server or managed data store
- Serverless functions or API endpoints
- Runtime credentials, secrets, or environment-bound tokens
- A hosted code runner or execution sandbox
- A mandatory third-party service or paid external API

Exercises that require real servers, containers, or databases are shipped as **downloadable local-first labs** with explicit setup instructions. Learners run them on their own machines, never on Pages.

## Scope

This decision applies to everything under `docs/`, `content/`, `assets/`, `labs/`, `scripts/`, and `tests/`, and to every file published in the `_site/` Pages artifact.

## Rationale

- Zero infrastructure cost and zero operational burden
- No attack surface from runtime services or secrets
- Content remains readable and linkable indefinitely, even if the repository is archived
- Learners can study offline from a cloned repository or a saved `_site/` copy
- Build-time validation covers links, examples, accessibility and size budgets; no hosted monitoring service is needed

## Base path

GitHub Pages serves user/organization sites at `https://<user>.github.io/<repository>/`. Chapter assets and navigation use flat relative URLs; nested track pages use relative paths to the same artifact. The browser resolves these under the Pages repository path or a downloaded folder. PAGES_BASE_PATH is recorded in the build metadata and exercised by the subpath browser checks; no origin-root assumption is required.

The builder honors `PAGES_BASE_PATH`:

- Local preview: unset (or empty) → site works from `_site/` at `http://127.0.0.1:8765/`
- Pages deploy: `/ai-fullstack-roadmap/` → all `href`/`src` values resolve under that path

Example:

```sh
# Local preview (root-relative)
make serve

# Verify the site behaves as it will on Pages
PAGES_BASE_PATH=/ai-fullstack-roadmap/ python3 scripts/build.py
python3 -B scripts/package.py
python3 tests/check_browser.py --base-path /ai-fullstack-roadmap/
```

The browser check mounts the artifact under the repository path. The same relative-URL artifact is also usable from a root-mounted local preview. Downloaded core HTML/CSS reading works directly from a folder; search and Workers need a local HTTP server because browsers restrict file-URL fetches.

## What is not allowed in the public artifact

| Category | Prohibited | Allowed alternative |
|---|---|---|
| Backend | API server, web framework runtime, worker queue | Downloadable local labs |
| Data | Database, cache, object storage bucket | Browser-local IndexedDB / localStorage |
| Auth | Login server, OAuth provider, session store | None; no accounts, no sync |
| Secrets | Runtime API keys, credentials, tokens | None; examples use synthetic fixtures |
| Execution | Hosted code runner, container runtime, WASM host service | Browser-side Pyodide/WebAssembly in a Worker (opt-in labs only) |
| External mandatory service | Required third-party API for core reading | Optional references only; core content works offline |

Browser-side WebAssembly (e.g. Pyodide) is permitted only as an optional, clearly labeled teaching tool. It is never required to read a chapter, and the site never claims worker isolation is a hardened security boundary.

## Offline and degraded behavior

Core reading, navigation, glossary definitions, static diagrams, walkthrough transcripts, and code examples work without JavaScript. Search, diagram step controls, and study controls require JavaScript. JavaScript enhances the experience (theme, bookmarks, notes, spaced review, interactive walkthroughs, labs) but is never required.

Browser-local study state (mastery, bookmarks, notes) uses a version-3 IndexedDB event journal with per-event localStorage fallback. Notes, bookmarks, settings, attempts, review schedules and reset events merge by stable event identity and logical timestamp. Existing v1 records are migrated without deleting their backup keys. It never leaves the browser. There is no server sync, no account, and no cross-device continuity beyond an explicit export/import JSON file the learner controls.

## Browser storage limitations

- Data is bound to one browser profile and device
- Clearing site data or using private mode discards stored progress
- Export/import JSON is the only recovery and portability mechanism
- No personal data is transmitted to any server

## Build output

The generated site is flat and self-contained:

- `_site/*.html` — chapter, stage, glossary, reference, lab, and redirect pages
- `_site/*.css`, `_site/*.js` — versioned assets (cache-busted by content hash)
- `_site/examples/` — runnable teaching code
- `_site/diagrams/` — interactive diagram sources
- `_site/manifest.json` — build-time content counts and metadata
- `_site/.nojekyll` — disables Jekyll processing

`_build/` and `_site/` are disposable outputs, excluded from git. Only source under `content/`, `assets/`, `labs/`, `scripts/`, `tests/`, and `docs/` is committed.

## Continuous integration

Pull requests run `make check` (build, package, verify). Only the verified `main`-branch artifact is deployed to GitHub Pages. PRs never publish. Actions use commit-pinned action versions and pinned direct browser/integration test dependencies, minimal permissions, concurrency handling, and no runtime secrets.

## Compatibility

Existing published URLs (flat chapter HTML such as `foundations.html`, flat example files, anchors such as `#q481`) are preserved. Moved chapters get HTML redirect pages that preserve deep links and query strings. No existing study ID, bookmark anchor, or lesson URL is retired without an explicit redirect.

## Practice and local execution

Assessments, attempt history and estimated mastery run entirely in the browser.
Familiar can come from a self-check; higher stages require graded evidence.
Subjective design answers receive a self-review rubric, not an automatic expert grade.
Review intervals are documented in [study-records.md](study-records.md).

JavaScript labs run in fresh Workers with 3-second execution limits. Python labs
use self-hosted Pyodide 0.29.2, installed by an integrity-checked authoring script.
Python startup has a 30-second allowance; execution is bounded after readiness.
Source is capped at 64,000 characters and output at 12,000 characters. Workers are
not hardened sandboxes and cannot guarantee a per-program memory ceiling.

The optional runtime is never fetched from a CDN during learner execution. Its
12 MB of runtime assets are served by Pages or a local preview, loaded on demand.
Browser imports use a declared small standard-library allowlist; server libraries,
databases, Docker and real network integrations stay local-only.

Question banks publish at most 40 expanded answers per page and JSON source shards.
Search fetches per-track static shards on demand, instead of loading the full
course on every page. Old chapter anchors and study IDs remain valid.
