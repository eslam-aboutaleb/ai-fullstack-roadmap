# Source-derived editorial review and release gates (#20)

The report at `questions/editorial-evidence.json` is generated with each static
build. It makes the limits of automated quality visible chapter by chapter:
short primary answers, missing question-level citations, unanswered interview
follow-ups and content not independently approved. Legacy counts are **triage
signals**, not automatic judgments that every short answer is incorrect.

`scripts/editorial_evidence.py` enforces stricter requirements for all newly
appended interview IDs above the frozen October 21, 2026 baseline (1211):
substantial answer, HTTPS source reference, substantive answered follow-up,
honest review state and no obvious placeholder prose.

Unlike a “draft means blocked” model, draft learning content can still publish
with its accurate status; **reviewed/approved** content must satisfy the existing
SHA-256 attestation check from `scripts/editorial.py`. The repository currently
has no independent approvals, and no automated check can certify factual
correctness, dataset representativeness, absence of plagiarism, compliance with
third-party licenses, or semantic duplicates.

### Reviewer acceptance procedure
1. Pick a flagged answer, establish its assumptions and primary source versions.
2. Check the substantive explanation and verify every important term and claim.
3. Execute applicable code with the declared dependencies and check exact output.
4. Trace a counterexample, failure mode, alternative, and answered follow-up.
5. Inspect citation accuracy, original diagram accessibility and security/privacy.
6. Only after independent review, record the matching content digest, reviewer,
   date and review notes in the existing attestation registry.
7. Rebuild, run all checks, inspect Pages subpath output, and publish with known
   limitations. Failing or missing independent checks remain **pending**.

New requirements do not silently rewrite historical study identities, progress,
or the existing single detailed-answer reader. This is an incremental QA factory,
not a declaration that all existing content already meets its final standard.
