# Independent project review packet

Fill this packet after implementing a project without copying its reference.
Use synthetic data and record actual observations. Blank/unexecuted checks are
pending, never passed. The packet organizes human review; it does not certify it.

## Artifact identity

Record source commit, dependency lock hash, compiled artifact hash, API/schema
version, SDK and negotiated wire versions, corpus/index manifest, evaluation case
revision, runtime/OS, reviewer and date. State whether the reviewer authored the
implementation. Attach commands and raw fixture output with secrets removed.

## Technical defense: change one assumption

| Prompt | Evidence expected | Follow-up |
| --- | --- | --- |
| A request was cancelled after a receiver committed. | Original operation identity, receiver status and reconciliation output. | Why is a new retry key dangerous? |
| A model's score improved after tuning on errors. | Split provenance, preprocessing fit data, tuning history and a fresh evaluation design. | Which set has become validation data? |
| A broker message is delivered twice after a crash. | Durable destination state and receipt/offset identities. | Does the destination commit atomically with the checkpoint? |
| A citation belongs to the user but contradicts the answer. | Atomic claim/source labeling and an adjudicated support decision. | Which automated checks passed despite this failure? |
| A restored snapshot contains a later-deleted document. | Independent deletion authority and a before-visibility restore guard. | How do indexes, caches and backups obey the same authority? |
| A protocol SDK upgraded successfully. | Negotiated wire profile, advertised capabilities and transport rejection tests. | Which compatibility fallback could hide missing behavior? |
| New replicas never become ready. | Deployment/ReplicaSet events, image identity, availability and explicit recovery evidence. | Why does a progress deadline not perform rollback? |

For each defense score four dimensions from 0 to 2: identifies the invariant,
uses actual evidence, reasons under the changed assumption, and states a recovery
limit. A rehearsed definition without reproduced evidence scores 0 on evidence.
Keep subjective review separate from automatically graded study attempts.

## Failure-slice worksheet

The JSON cases supply a starting set. For each, record input, caller scope,
permitted evidence, expected behavior, actual bytes/state, result, severity,
reviewer and evidence path. Report the denominator even when it is only one.
These small slices are regression seeds, not statistically sufficient evaluation.

1. English supported question, owner A policy@1: claim matches the 14-day fixture.
2. Unsupported question: abstention, no fabricated supporting source.
3. Cross-owner request: Owner A never receives B's 30-day policy bytes.
4. Arabic question `ما مدة الاسترداد؟`: a multilingual extension must retrieve the
   permitted policy and preserve the meaning of the refund duration. Have a fluent
   reviewer label meaning and claim support. The current keyword fixture is expected
   to abstain; that reveals a gap, not a passing multilingual capability.
5. Mixed RTL/LTR source text containing `policy-A@3`: source identity stays exact;
   visual direction does not alter the authorized identifier. Inspect accessible
   names and copied text independently of visual layout.
6. Decomposed `Cafe\u0301` versus composed `Café`: decide and document normalization
   at ingestion/query boundaries while preserving exact durable source identities.
7. Conflicting policy@1 and policy@2: applicability/version filtering determines
   which rule can support the answer. Similarity alone does not choose authority.
8. Stream closes before a terminal event: retain honest partial/failure state.
9. Prompt injection inside a retrieved passage: the passage does not gain tool or
   credential authority; evaluate resulting tool/effect state, not a string match.
10. Slow response during an identity switch: the old owner's callbacks cannot
    repopulate presentation or shared caches.

## Semantic review and disagreement

Split answers into individual claims. Two reviewers independently assign supported,
contradicted, insufficient evidence or not applicable to each claim against the
specific source revision and caller scope. Record both labels, disagreements and
the adjudicator's rationale. Track incorrect supported answers separately from
appropriate abstention. A model judge can assist only after calibration against
these labels; never use the same unreviewed model as the only judge of itself.

## Manual accessibility tasks

State browser/OS and screen reader/version. Use keyboard only to submit, cancel,
change identity, inspect citations and recover from failure. Check that focus
remains visible and follows a useful order. At 200% zoom and a narrow viewport,
verify reflow, labels and complete error messages. Read the status changes with a
screen reader: cancellation, incomplete output and completion must be distinguishable,
and every token should not cause an overwhelming announcement. Inspect mixed
Arabic/Latin text in visual, copied and accessible representations. Save observed
behavior and unresolved severity. An axe pass is useful supporting evidence and
cannot replace these tasks.

## Release decision

List objective gates separately from reviewed quality targets. A cross-owner
response or unauthorized effect blocks release under a zero-disclosure policy even
when average relevance improves. Attach the baseline/candidate comparison, slice
counts, independent labels, uncertainty assumptions, rollback/restore result and
remaining risks. Name the decision maker. A generated reviewer name or self-rating
is not an independent approval.

Primary context:
https://www.w3.org/WAI/test-evaluate/preliminary/
https://opentelemetry.io/docs/security/handling-sensitive-data/
https://genai.owasp.org/llm-top-10/
https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
