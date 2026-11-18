# Repository structure

```text
.
├── .github/workflows/             # Pull-request validation and Pages publishing
├── assets/
│   ├── css/style.css              # Editable styles
│   ├── js/                       # Study controls and teaching interactions
│   └── static/.nojekyll
├── content/
│   ├── course.json               # Stage order and chapter slugs
│   ├── chapters/<slug>/          # Structured JSON + canonical questions.md pack per chapter
│   ├── examples/
│   │   ├── chapters/             # 59 editable chapter examples + catalog
│   │   └── questions/<topic>/    # 562 inline examples + topic catalogs
│   ├── diagrams/                 # Editable overview-diagram sources
│   └── shared/                   # Glossary, references, stable study IDs
├── labs/                         # Optional HTTP/streaming, voice, OCR, foundation labs
├── scripts/                      # Build/CLI entrypoints (`questions.py`, `build.py`, `roadmap/`)
├── tests/                        # Site, example, and source-layout verification
├── docs/                         # Contributor architecture and verification record
├── CONTRIBUTING.md
├── LICENSE                       # MIT terms, also shipped in the public artifact
├── Makefile
├── README.md
├── _build/                       # Ignored intermediate generated site
└── _site/                        # Ignored allowlisted public deployment artifact
```

## Static architecture

The site is a **GitHub Pages-only static application** (`docs/architecture.md`). The builder
honors `PAGES_BASE_PATH` so all internal asset and navigation URLs work both at the local
preview root and under `/ai-fullstack-roadmap/` on GitHub Pages. The generated artifact
includes `.nojekyll` to disable Jekyll processing.

## Data flow

`content/ + assets/ + labs/ + LICENSE` → `scripts/build.py` → `_build/`
→ `scripts/package.py` → `_site/` → `tests/check.py`.

`make check` runs this sequence. `make serve` builds and serves `_site/`.
The two output folders are disposable, and source paths are resolved from the
script location rather than the caller's current directory.

The builder flattens selected assets and example paths to preserve published
URLs. Grouping a source recipe under a topic does not change its public filename
or question anchor. Only public static files and the generated example/lab
folders are packaged; contributor documents, source chapter JSON/Markdown, tests, and Git metadata
are excluded.

## Chapter ownership

Each chapter has:

- `chapter.json`: title, introduction, terms, concrete case, and diagram flow.
- `lessons.json`: guided explanations, preserving their existing reading order.
- `questions.md`: single canonical Markdown pack containing all deeper interview questions (`scripts/roadmap/question_markdown.py`, authored/validated via `scripts/questions.py`).
- `review.json`: additions, recommended work, completion checks, reference keys.
- `code-notes.json`: the chapter-level code walkthrough.

Examples live under the shared example folders because a focused example may support multiple chapters.

## Script architecture (`scripts/` & `scripts/roadmap/`)

Reusable build, content loading, prose rendering, course builders, and editorial gates live in
`scripts/roadmap/` (`config.py`, `question_markdown.py`, `examples.py`, `editorial.py`,
`content.py`, `prose.py`, `courses.py`, `practice.py`, `audit_pages.py`, `site_builder.py`).
Top-level `scripts/*.py` files provide lightweight CLI entrypoints (`questions.py`, `build.py`,
`package.py`, `course_data.py`, `interview_contract.py`) and compatibility facades so existing
checks continue working with zero import-time side effects.

## Code-example ownership

Chapter example filenames and scope/language metadata are declared in
`content/examples/chapters/catalog.json`. Inline examples have ordinary source
files and a topic-local `catalog.json` holding their explanation, walkthrough,
expected outcome, limitations, and explicit question-ID assignments.

A recipe is stored once and may be assigned to several related questions. Its
topic is its source home, not an instruction to attach it to every question in
that topic. The loader rejects duplicate assignments, missing coverage, unknown
IDs, mismatched filenames, and unregistered source files.

## Identity and compatibility

Browser notes, bookmarks, and learned flags use numeric IDs from
`content/shared/study_ids.json`. Moving content between source folders does not
change those IDs. New question titles must be registered with
`python3 scripts/course_data.py --assign-ids`; ordinary builds do not mutate
source identity files.

All 1,163 question records live in 59 canonical per-chapter `questions.md` files
verified losslessly against content digests, paired with 562 inline examples and
59 chapter examples. Existing root HTML and example copies belong only in ignored output folders.
