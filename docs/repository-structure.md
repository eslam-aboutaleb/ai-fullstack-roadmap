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
│   ├── chapters/<slug>/          # Five JSON files per chapter
│   ├── examples/
│   │   ├── chapters/             # 48 editable chapter examples + catalog
│   │   └── questions/<topic>/    # 298 inline examples + topic catalogs
│   ├── diagrams/                 # Editable overview-diagram sources
│   └── shared/                   # Glossary, references, stable study IDs
├── labs/                         # Optional HTTP/streaming, voice, OCR, foundation labs
├── scripts/                      # Build, package, and content loaders
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
folders are packaged; contributor documents, chapter JSON, tests, and Git metadata
are excluded.

## Chapter ownership

Each chapter has:

- `chapter.json`: title, introduction, terms, concrete case, and diagram flow.
- `lessons.json`: guided explanations, preserving their existing reading order.
- `questions.json`: deeper practice material, preserving the existing answers.
- `review.json`: additions, recommended work, completion checks, reference keys.
- `code-notes.json`: the chapter-level code walkthrough.

Examples live under the shared example folders because a focused example may support multiple chapters.

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

The migration from `authoring/` split the existing large lesson/question files
into chapter folders and extracted embedded example strings into editable code
files. All 810 question records, 298 inline examples, and 48 chapter examples
were compared with the pre-migration data. Existing root HTML and example copies
were generated artifacts and now belong only in ignored output folders.
