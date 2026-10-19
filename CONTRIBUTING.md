# Contributing

Use Python 3.10+ and Node.js. The site builder uses the Python standard library;
there is no required pip or npm install for ordinary content contributions.
Optional integration labs document their own dependencies in [labs/README.md](labs/README.md).

From the repository root:

```sh
make check
make serve
```

If your `python3` is older than 3.10, select a compatible installed interpreter:

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
Here is a minimal entry for a new hypothetical question ID 811:

```json
{
  "name": "validate-input",
  "language": "python",
  "filename": "validate-input.py",
  "questions": [811],
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

Use a registered ID from your change instead of copying 811 blindly. Names are
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
- Preserve existing explanations and IDs unless a correction is intentional.
- Include the user-visible change, why it helps learning, and what you verified.
- Distinguish offline models and proposed exercises from executed integrations.
- Commit source, docs, and any intentionally assigned IDs; omit generated output.

Pull requests run the same checks as local contributions. Publishing occurs only
from the main branch through the Pages workflow; opening a pull request does not
publish the site.

## Contribution license

Contributions to this project are provided under the same [MIT License](LICENSE)
as the existing code and original learning content. You retain copyright in your
contributions. Submit material you have the right to contribute, and preserve any
applicable third-party attribution and license notices. No separate contributor
license agreement or copyright assignment is required.
