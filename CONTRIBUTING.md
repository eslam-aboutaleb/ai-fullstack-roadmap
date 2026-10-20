# Contributing

Use Python 3.11+ and Node.js. The site builder uses the Python standard library;
there is no required pip or npm install for ordinary content contributions.
Optional integration labs document their own dependencies in [labs/README.md](labs/README.md).

## Static architecture

This is a **GitHub Pages-only static application**. The published site contains only
HTML, CSS, JavaScript, JSON, SVG, and optional browser-side WebAssembly. There is no
production backend, database, serverless function, auth server, or mandatory external
API. Build-time tooling (Python scripts, GitHub Actions) is allowed; runtime secrets
and hosted services are prohibited.

The generated site works both at the repository root during local preview and under
`/ai-fullstack-roadmap/` on GitHub Pages. All internal asset and navigation URLs are
base-path safe. Verify with:

```sh
# Local preview (root-relative, no base path)
make serve

# Verify the site behaves exactly as it will on GitHub Pages
PAGES_BASE_PATH=/ai-fullstack-roadmap/ python3 scripts/build.py
python3 -B scripts/package.py
python3 tests/check_browser.py --base-path /ai-fullstack-roadmap/
```

The browser smoke test mounts the artifact at that path. Relative asset URLs also support a root-mounted `make serve`. Browser checks require the optional test tools below.

`_build/` and `_site/` are disposable generated outputs, excluded from git. Only source
under `content/`, `assets/`, `labs/`, `scripts/`, `tests/`, and `docs/` is committed.

From the repository root:

```sh
make check
make serve
```

If your `python3` is older than 3.11, select a compatible installed interpreter:

```sh
make check PYTHON=python3.11
make serve PYTHON=python3.11 PORT=8767
```

Open the printed localhost address. Stop the preview with Ctrl+C. `make serve`
builds before starting; stop and rerun it after editing source files.

## Find the right source

| Change | Edit |
| --- | --- |
| Chapter title, introduction, terms, flow, or case | `content/chapters/<slug>/chapter.json` |
| Guided explanations | `content/chapters/<slug>/lessons.json` |
| Deeper practice questions and answers | `content/chapters/<slug>/questions.json` |
| Review notes and extension/completion checks | `content/chapters/<slug>/review.json` |
| Chapter code walkthrough | `content/chapters/<slug>/code-notes.json` |
| Chapter example code and its scope | `content/examples/chapters/<slug>.*` and `catalog.json` |
| Inline question code | `content/examples/questions/<topic>/<name>.*` |
| Inline explanation, expected output, and assigned questions | That topic's `catalog.json` |
| Learning-stage order | `content/course.json` |
| Stable study identities | `content/shared/study_ids.json` |
| Glossary or primary references | `content/shared/glossary.json`, `references.json` |
| Styling and browser interactions | `assets/css/`, `assets/js/` |
| Integration labs | `labs/` |
| Page rendering and source loading | `scripts/` |
| Verification | `tests/` |

Generated `_build/` and `_site/` are ignored. They are recreated by the tools;
edit the source directories instead. Published URLs remain flat, such as
`foundations.html` and `examples/questions/gradient.py`, even though source files
are grouped into folders.

## Edit an existing question

1. Find its chapter in `content/chapters/` and edit its JSON record. Keep the
   question's existing `Q` title when changing only its answer; titles are part
   of the study-identity key.
2. Find the question ID in `content/shared/study_ids.json`. Search for that ID
   in `content/examples/questions/**/catalog.json` to find its inline example.
   For example, `rg -n '"gradient"' content/examples/questions` finds the
   gradient recipe and its source filename.
3. Update code, explanation, walkthrough, and expected output together. Related
   questions can share a focused example; review all IDs in its `questions` list.
4. Run `make check` and inspect the affected chapter with `make serve`.

If you reword an existing `Q` title, move its matching key in `study_ids.json`
to the new title while keeping the same numeric ID. Do not allocate a new ID
for a wording-only correction, renumber existing IDs, or reuse a retired ID.

## Add a lesson or question

1. Append a record to a chapter's `lessons.json` or `questions.json`, matching
   the neighboring fields. Lessons use `Q`, `explain`, `example`, and `takeaway`.
   Questions use `Q`, `A`, `Why`, `Risk`, `Trade`, and `Try`.
2. Register the new identity explicitly:

   ```sh
   python3 -B scripts/course_data.py --assign-ids
   ```

   This appends IDs after the current maximum and preserves existing mappings.
   Normal builds read the identity file without rewriting it.
3. Assign that ID to a relevant inline example or add a new one. Every question
   must have exactly one explicit example assignment; no keyword fallback is used.
4. Run `make check` and review the generated question and study controls.

## Add or change an inline example

Place the source in its owning topic folder, then add an entry to that folder's
`catalog.json`. The same example may support questions in other chapters.
Here is a minimal entry for a new hypothetical question ID 826:

```json
{
  "name": "validate-input",
  "language": "python",
  "filename": "validate-input.py",
  "questions": [826],
  "explain": "Reject a blank question before starting expensive work.",
  "steps": "Read the input. || Check that it contains non-whitespace text.",
  "expect": "False"
}
```

The matching source file is:

```python
question = "   "
print(bool(question.strip()))
```

Use a registered ID from your change instead of copying 826 blindly. Names are
unique across all topic catalogs. Filenames must match the recipe name and
language extension. Explanations should describe the specific code, not repeat
the question. `steps` contains at least two parts separated by ` || `.

Optional `change`, `limit`, and `reference` fields add a targeted experiment,
setup/limitations, and a primary documentation link. Use `python-sketch` for
optional Python integrations, and state compatible dependencies in `limit`.
Other supported languages are `javascript`, `html`, `sql`, `bash`, `json`, and
`dockerfile`. Execution/syntax checks vary by language; see
[tests/check_question_examples.py](tests/check_question_examples.py).

Python examples are executed in fresh processes with a timeout and their stdout
must match `expect`. Use only synthetic fixtures; do not add live credentials,
provider calls, uncontrolled downloads, or writes outside disposable fixtures.
SQL-specific integration requirements and browser/SDK setup must be explicit.

## Add a chapter

Create a folder containing the same five JSON files as an existing chapter.
Register its slug in `content/course.json`, add its chapter example and catalog
entry, register its study IDs, and provide inline examples for its questions.
Keep prerequisites and the case understandable before introducing deeper detail.

## Before opening a pull request

- Run `make check` and verify the affected pages at desktop and mobile widths.
- Verify base-path behavior with `PAGES_BASE_PATH=/ai-fullstack-roadmap/ make check`.
- Preserve existing explanations and IDs unless a correction is intentional.
- Include the user-visible change, why it helps learning, and what you verified.
- Distinguish offline models and proposed exercises from executed integrations.
- Commit source, docs, and any intentionally assigned IDs; omit generated output.

Pull requests run the same checks as local contributions, including base-path safety,
broken-link detection, example execution, and accessibility structure. Publishing occurs
only from the main branch through the Pages workflow; opening a pull request does not
publish the site. The architectural constraint (static only, no runtime services) is
documented in [docs/architecture.md](docs/architecture.md).

## Contribution license

Contributions to this project are provided under the same [MIT License](LICENSE)
as the existing code and original learning content. You retain copyright in your
contributions. Submit material you have the right to contribute, and preserve any
applicable third-party attribution and license notices. No separate contributor
license agreement or copyright assignment is required.

## Browser and pilot integration checks

Ordinary `make check` uses Python 3.11+ and Node.js. To run the Chromium checks
and the optional FastAPI pilot in an isolated environment:

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m playwright install chromium
make check PYTHON=.venv/bin/python
.venv/bin/python tests/check_browser.py
.venv/bin/python labs/request_lifecycle.py
```

CI also rebuilds with `PAGES_BASE_PATH=/ai-fullstack-roadmap/` and checks that
artifact through `tests/check_browser.py --base-path /ai-fullstack-roadmap/`.
No browser or Python test dependency is a hosted runtime service.

Enriched lessons and questions must satisfy the recursive schemas in
`content/shared/`. Existing legacy entries retain their smaller contract.
Do not label content approved without independent technical review. Self-report
confidence and learned flags do not certify mastery. See the
[issues 1–16 implementation review](docs/implementation-review.md) for the
current acceptance gaps.

## Practice, scale, courses and integration checks

Edit `content/assessments.json` for graded quizzes/debugging cases and subjective
rubrics, and `content/browser-labs.json` for starters, reference solutions and
input/output cases. Keep stable IDs and explicit learning outcomes. Do not make a
subjective answer an automatic pass. `content/courses/` contains structured units,
prerequisites, definitions, independent exercises and primary references.

Question source can be split into `questions-<name>.json` beside `questions.json`.
All records still require registered study IDs and explicit example assignments.
The generated bank uses 40 full answers per page; search uses static per-track
shards. `tests/check_question_bank.py` and `tests/check_scale_browser.py` build and
navigate 1,200 test records without adding filler to public content.

```sh
make runtime                    # optional, pinned self-hosted browser Python
make check                      # Python 3.11+ and Node; no npm/pip needed here
npm ci --ignore-scripts          # pinned test-only axe-core
npm audit --audit-level=high
.venv/bin/python tests/check_browser.py
.venv/bin/python tests/check_learning_browser.py
.venv/bin/python tests/check_accessibility.py
.venv/bin/python tests/check_scale_browser.py
```

For local backend pilots, install `requirements-labs.txt` in an isolated Python
3.11+ environment and install PostgreSQL 16+ locally. Then run
`python scripts/test_postgres_pilot.py`. It creates its own temporary loopback
cluster, tests the API and connected app, stops it, and removes it. It does not
reuse an existing database or accept a production DSN.

The optional NumPy/autograd bridge uses a separate Python 3.14+ environment and
`requirements-models.txt`. On Linux, install the pinned torch version from the
[official CPU wheel index](https://download.pytorch.org/whl/cpu) first to avoid a
GPU dependency download; then install the requirements and run
`python -m labs.numpy_torch_bridge`. No trained weights or provider are downloaded.

Automated accessibility checks are a release gate; manual keyboard/screen-reader,
zoom and content review remain separate review work. Never describe a green axe
result as full WCAG conformance. See [study-records.md](docs/study-records.md) for
storage, migration and mastery semantics.

## Recording technical review

Enriched interview entries remain `draft` until a reviewer has checked the claims,
citations and examples. To mark a question `reviewed` or `approved`, add a matching
entry to `content/reviews.json`, keyed by its stable registry identity
(`interview/<chapter>/<exact question text>`). Record `reviewer`, `reviewed_at`,
`review_notes` and `sha256`. Compute the digest with
`scripts.editorial.content_digest(record)` after finishing the content changes.
The digest excludes the generated numeric ID and review status. CI rejects missing
or stale attestations; editing reviewed content requires renewed review. These
records document a review; automation cannot authenticate reviewer identity or
establish expertise. Never invent a reviewer or claim approval from a passing test.

Draft material is published with its pending status. The editorial report displays
source-derived review counts separately from test results. Legacy content has not
been retroactively certified. The course-unit review label is also explicitly
pending; it does not imply the question attestation gate covers every content type.
