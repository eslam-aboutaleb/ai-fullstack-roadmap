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

## Stable IDs and edited-record validation

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
Instead review older unverified answers incrementally, preserving all IDs. Review is recorded per content digest; delegated Codex review is identified as AI review. Learner research and independent human review are not inferred from that attestation.

## Review states for conceptual answers

Conceptual answers support draft, reviewed and approved states. Every claimed
reviewed/approved state is checked against a content-digest-specific attestation,
including conceptual records without the legacy `spoken` field. Changing the
schema enum alone must never grant approval. Record the actual reviewer and
review method; an AI review must say so and must not be represented as an
independent human SME review. The maintainer has delegated technical acceptance
to Codex in this implementation session; that does not invent GPU/vendor results.

## Issue #12 acceptance evidence — 23 October 2026

`content/shared/authoring-acceptance.json` identifies three representative full-schema
lessons and ten varied reviewed interviews by stable study ID, source, same-page
reader anchor and primary references. The lessons cover request validation,
concurrent database writes and an independent agent-effect oracle. Their downloadable
labs execute positive and adverse cases; code/source identity is checked by the
existing structure/source-fidelity suite. Review notes and exact digests are in
`content/reviews.json`. Codex performed the technical review under the maintainer's
explicit delegation; this is not independent human review.

The authoring schema and `interview_contract.py` check chapter introductions,
terms, foundation lessons and complete interview fields. The immutable 1211 baseline
only identifies adoption-era records: **scripts/revised_content_gate.py** separately
checks every new or edited record, including older IDs, renamed/moved records,
lessons and companion units. PR and release CI both require matching review.

`make check` validates source, expected outputs, schema negative cases, literal
quotes, glossary/reference links, IDs, one detailed answer and static root/subpath
links. Browser CI checks mobile/no-JS, keyboard, notes, search, focus/sidebar defaults
and print controls at both paths. Existing `content/shared/focused-acceptance.json`
and the chapter practice sections map the ten sample questions to assessed tasks;
the sample lessons additionally contain independent tasks and answer keys.

The reservation sample is explicitly insert contention in one file-backed SQLite
database, not a forced stale-read transaction. The HTTP sample is validation through
TestClient, not authenticated durable queue acceptance. The oracle assumes a trusted
complete fixture ledger. These limits are part of each lesson and its review.
