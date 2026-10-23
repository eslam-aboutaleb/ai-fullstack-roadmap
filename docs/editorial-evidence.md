# Source-derived editorial evidence and release acceptance (#20)

Every build emits `questions/editorial-evidence.json`. Version 2 inventories every
chapter lesson, interview and companion unit, including source path, stable ID,
content digest, primary references, lab, assessment IDs, review status, reviewer
and date. A claimed review is verified against the content-specific registry;
missing or stale attestations fail the build. `verified_review_records` counts
only matching reviewed/approved records. Legacy and draft content remains clearly
itemized; the report does not convert structural checks into semantic approval.

The existing editorial report and same-page chapter practice sections provide
navigation. Removed question-bank/course/coverage dashboards are not restored.
`content/shared/authoring-acceptance.json` supplies three representative reviewed
lessons and ten reviewed questions; `content/shared/focused-acceptance.json` maps
the previously completed LLM/RAG, agent and full-stack outcomes to reviewed
answers/units, code, diagrams and assessments.

## Required checks

- `make check`: schemas, malformed fields, literal quotes, executable expected
  outputs, source/example identity, local artifact links, assessment mapping,
  duplicate/near-duplicate prompts, stable IDs, root/subpath builds and source
  equality of the published report.
- `scripts/revised_content_gate.py --base <base> --require-review`: every authored
  or revised record, including legacy stable IDs, lesson edits, question
  moves/renames and companion units, needs matching review. PR and release jobs
  use the pinned event base and fail closed without it.
- Claimed reviewed units are validated in preview builds too; this PR preserves
  main's stricter implementation, rather than reverting it to release-only checks.
- Browser CI covers mobile/no-JS, keyboard, search, progress/notes, single answers,
  sidebar defaults and root/subpath links. Static content needs no secrets/backend.

## Review evidence and limits

The maintainer explicitly delegated technical acceptance to Codex. Each resulting
attestation identifies AI review; no independent human review, learner research,
exhaustive link freshness or semantic plagiarism certification is inferred.
Primary sources, code mechanics, negative cases, limitations and worked examples
are assessed before that record's digest is attested. A changed record invalidates
the old attestation. Reviewed is a content-specific claim, not a global statement
that the entire historical curriculum is complete. Unchanged legacy content remains
an honestly inventoried backlog; its presence does not bypass new/edited gates.

## Acceptance mapping

Malformed/uncited content and missing/stale reviews → revised-record negative
fixtures and source schema tests. Verified versus draft coverage → version-2
per-record report and source equality/counter assertions. Practice/source/quote
fidelity → existing assessment, example, rich lesson and quote suites. Accessible
static reading → browser CI at both paths. Delegated technical verdict → matching
attestations for every changed lesson/question/unit; report-only changes introduce
no unreviewed teaching record. No runtime service or paid account is introduced.
