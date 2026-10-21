# Interview-first chapter authoring contract (Issue #12)

The **reader begins with the chapter introduction**, not a quiz. Source order is:
`chapter.json` goal/motivation/terms/flow/case → `lessons.json` guided explanations
→ `questions.json` (and shards) for the deeper interview questions.

## One detailed answer, not two competing answers

The question opens with **View answer**, exposing the complete `A` field.
Explain the direct answer, internal mechanism, assumptions, a worked scenario,
a failure boundary, a trade-off and a changed-assumption follow-up. Use Markdown
headings, bold, tables and code only where they **add explanatory value**. Code
should have a meaningful test or declared illustration status, and diagrams
must show concrete processes or calculations with accessible text alternatives.

The historical `spoken` field remains accepted for compatibility with existing
records and authoring schemas; the renderer no longer prints it separately.
New deep questions use `answer_format: conceptual` and contain `A`, `Why`,
`Risk`, `Trade`, `Try`, `worked_case`, `follow_ups`, `citations` and
honest `reviewer_status`. A conceptual answer without useful executable code
must not invent a useless snippet. When code is genuinely useful, use the
existing catalog and test expected output before claiming it ran.

## Append-only migration

`scripts/interview_contract.py` enforces more detailed minimum source fields
for newly registered chapter IDs **above 1211** (the immutable adoption baseline
on 21 October 2026). It does not rewrite IDs, historical notes or old questions.
New foundation lessons require a substantial explanation, specific example and
takeaway. New interview answers require explanatory paragraphs, an answered
follow-up and a primary-source citation. These are **minimum structural gates**,
not a numeric substitute for correctness, expert review or learning depth.
To author a new question, append it then run
`python3 -B scripts/course_data.py --assign-ids`, `make check`, and inspect
the chapter in a browser at root and the Pages subpath.

Do **not** raise the baseline or add empty padding to satisfy a length rule.
Instead review older unverified answers incrementally, preserving all IDs. Human
technical review and learner research remain outstanding until independently done.
