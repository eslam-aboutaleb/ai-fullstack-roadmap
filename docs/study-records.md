# Local study records

The website has no account, analytics service, server sync or background reminders.
Browser storage is tied to one origin/profile/device; private browsing and clearing
site data can discard it. Export a backup to move devices.

## Persistence and migration

`study-model.js` defines validation, merging, scheduling and estimates.
`study-store.js` stores a version-3 IndexedDB journal in `ai-fullstack-study`.
Every note edit, bookmark change, setting, attempt, review and reset is its own
record. Two tabs changing different fields do not replace a shared full snapshot.
Timestamps plus stable record IDs define deterministic ordering; identical IDs are
deduplicated. Same-field conflicts use that order, not a semantic text merge.

If IndexedDB is unavailable, individual localStorage journal keys provide a
fallback. Storage denial or quota errors keep the in-memory record usable and show
an export warning. Corrupt legacy JSON is skipped while valid records are recovered.
The old `ai-fullstack-roadmap-v1` and predecessor keys are retained as backups and
migrate at logical time zero, so they cannot override newer journal changes.

Exports contain the validated event journal. Version-1 exports are accepted and
converted; version-3 imports preserve identities, attempts and review history.
Imports merge rather than replace the current journal. Clear deletes old journal entries and migration backup keys, then retains a reset barrier,
so an old tab cannot resurrect older events merely by reconnecting. Exports after reset contain no cleared notes or attempts. An explicit
import of old records with timestamps before a later reset remains cleared; a v1
import is a deliberate new merge at import time. Browser/device clock skew and
conflicting edits to the same note still require judgment; no server resolves them.

## Evidence and review

- Familiar: self-check or an attempt.
- Practiced: at least one passed deterministic quiz, debugging or coding check.
- Independent: passed independent debugging/coding evidence without hints, with a
  passing latest graded result.
- Estimated Mastered: distinct independent checks passed at least 24 hours apart,
  with a passing latest graded result.

These estimates are study aids, not secure certification or comprehensive proof of
competence. Self-review of a design response never grants an automatic pass. Seeing
hints or a reference solution marks subsequent attempts on that page as assisted.
The assistance flag describes that browser-page session, not a claim to measure
whether a learner has ever seen an answer.

A graded failure schedules review in one day. Successful review intervals are 1,
3, then doubled days capped at 90. Time is supplied explicitly to the pure scheduler
for reproducible tests. There are no promised background notifications.
