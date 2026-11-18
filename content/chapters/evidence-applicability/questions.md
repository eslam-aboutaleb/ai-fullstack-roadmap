<!-- chapter: evidence-applicability -->

# How does explaining eligibility differ from authorizing a business outcome?

## Answer

An assistant can explain documented eligibility rules and identify missing facts. A binding business outcome requires the authorized process, applicable evidence, and an authoritative recorded decision. Clearly communicate which responsibility the product is performing.

## Why

Separate explanation from authority. An assistant can summarize applicable rules; a deterministic service and authorized actor own the actual business transition and approval.

## Risk

A fluent answer can sound like approval despite missing personal applicability evidence. Distinguish general rules, verified customer-specific facts, and actual recorded decisions.

## Trade-off

Careful conditional explanations may feel less decisive and preserve the actual authority boundary. Automated adjudication is a separate product requiring substantially stronger domain and governance evidence.

## Try This

Rewrite three coverage answers to state the supporting clause, material conditions, unresolved facts, and whether an authorized decision has actually occurred.

# How should event date, submission date, and rule effective date be handled?

## Answer

Event date concerns when something happened, submission date records when a request was filed, and rule effective dates define version applicability. These are separate facts; do not infer one from another merely to fill a required field.

## Why

Store event time, submission time, and rule effective intervals separately. Select the applicable revision explicitly and evaluate timezone and boundary cases rather than guessing a missing date.

## Risk

Applying today's policy to an earlier incident can produce an inaccurate answer. Time zones and inclusive/exclusive boundary rules also matter for exact applicability.

## Trade-off

Explicit temporal modeling adds query and validation work. A current-only general FAQ is simpler if the UI honestly limits its scope.

## Try This

Create incidents before, at, and after a policy-version boundary. Specify the applicable interval rule and the evidence required for each answer.

# Why must exclusions and conditions be retrieved alongside a positive coverage clause?

## Answer

A positive clause can be limited by exclusions, definitions, sublimits, deductibles, and factual conditions elsewhere. Retrieving one semantically similar paragraph is not necessarily sufficient to explain applicability.

## Why

Retrieve linked exceptions and required conditions alongside a positive clause. Group evidence by applicable revision before answering and abstain when a material qualification is unavailable.

## Risk

A faithful summary of an isolated clause can still mislead by omitting a controlling exception. More top-k hits may not solve the problem if the corpus lacks structured relationships.

## Trade-off

Targeted follow-up retrieval or structured links improve completeness and add calls and complexity. Large indiscriminate context increases noise and cost.

## Try This

Build a case where the positive clause ranks highly but its exclusion is elsewhere. Evaluate whether a follow-up query or section expansion retrieves the missing condition.

# Why is a section citation weaker than a revision-aware evidence reference?

## Answer

A section label identifies a human-readable location, but may not uniquely identify source, revision, or exact supporting span. A reproducible reference needs enough identity to retrieve what the user originally saw.

## Why

Carry source ID, revision, span, and applicability metadata through assembly and citation. Recheck access when opening a historical source instead of treating an identifier as a permission token.

## Risk

A later policy edit can make an old answer unverifiable, and section-only deduplication can collapse distinct sources. A fallback source filename is not evidence of the original document's identity.

## Trade-off

Rich citations add metadata and snapshot retention while enabling verification. Simple labels work for a small sample corpus and should not be overstated.

## Try This

Create two sources with an identically named section and different terms. Design a stable citation key and bounded source-opening API.

# How should OCR, tables, photographs, and attachments extend the support pipeline?

## Answer

Treat each modality as a separate extraction and evidence problem. OCR converts visible text, tables need row-column relationships, and photographs may require a vision model or human review. A file upload alone does not create reliable multimodal reasoning.

## Why

Preserve original artifacts, OCR text, layout, and region provenance. Validate fields and tables before indexing, and treat extracted instructions as untrusted source content.

## Risk

OCR errors in amounts, dates, or negations can change meaning. Attachments can also contain malware, private third-party data, prompt injection, and oversized payloads.

## Trade-off

Richer inputs improve user access and require scanning, extraction confidence, provenance, storage policy, and review states. Text-only support is narrower and easier to validate.

## Try This

Design an attachment intake state machine with quarantine, extraction, review, indexing, and rejection. Keep source bytes separate from generated interpretations.

# Why should fraud or risk signals not be treated as automatic truth?

## Answer

A statistical risk score is evidence for investigation, not proof that a service requestant is dishonest or that a service request should be denied. Training data, false positives, protected proxies, and changing behavior all affect interpretation.

## Why

Treat risk predictions as uncertain inputs with reviewed thresholds and an appeal path. Evaluate false positives and subgroup effects before connecting a signal to consequential decisions.

## Risk

Presenting an opaque score as a decision can create harmful unsupported accusations and unreliable automation. It also introduces sensitive-data and model-governance obligations beyond this guide's engineering examples.

## Trade-off

Assisted triage can prioritize workload while requiring calibration, review, and appeal paths. Simple rule-based routing may be more transparent for a small system.

## Try This

Design a review-only output with supporting observable signals, uncertainty, missing information, and prohibited automatic actions. Do not invent a fraud threshold.

# How should deterministic calculations complement generated explanations?

## Answer

Use reviewed deterministic code for exact arithmetic under explicitly selected policy rules, then let generation explain the result and assumptions. A model should not invent a deductible, round a monetary value arbitrarily, or apply an unverified formula.

## Why

Use deterministic arithmetic with explicit units, currencies, dates, and reviewed formulas. Let the model explain a verified result rather than inventing or silently altering the calculation.

## Risk

Correct arithmetic with the wrong rule or knowledge version is still wrong. Caps, sublimits, depreciation, multiple currencies, and exceptions require domain-approved logic.

## Trade-off

Deterministic calculators improve reproducibility and need versioned business specifications. Free-form arithmetic is convenient and unsuitable as authoritative financial logic.

## Try This

Write a hypothetical deductible calculation with explicit inputs and rounding, then state which real knowledge facts must be verified before using it.

# What should a real human-escalation record contain?

## Answer

Store the originating operation, authorized user or case, reason, minimal evidence, destination, delivery state, and an acknowledgement or failure. Distinguish requested, accepted, in progress, and completed rather than claiming connection from generated prose alone.

## Why

Create a durable handoff record with owner, urgency, evidence, completed actions, and unresolved questions. Report actual acceptance state instead of promising human contact without an integration.

## Risk

Exporting a full conversation can disclose unnecessary personal data, and a failed handoff can leave a user waiting without an actual owner.

## Trade-off

Structured escalation adds integration work and truthful operational status. A clear support-contact instruction is a legitimate simpler fallback.

## Try This

Specify a proposed handoff service and acceptance tests for delivery failure, duplicate requests, revoked access, and a later human response.

# How should fairness and accessibility be evaluated in customer support?

## Answer

Evaluate whether the assistant handles equivalent requests consistently across language, writing style, disability-related interaction needs, and differing levels of domain knowledge. Focus on support outcomes and access, not unsupported automated judgments about protected traits.

## Why

Evaluate realistic language, literacy, disability, and channel variations under reviewed criteria. Report subgroup results and preserve a usable non-voice or human-assisted alternative.

## Risk

Simplified wording can accidentally omit a condition, while multilingual retrieval can fail under ASCII lexical fallback. Voice or OCR inputs introduce another representation gap.

## Trade-off

Broader evaluation and interface support cost effort and improve real usability. Clearly bounded supported languages are preferable to an untested universal claim.

## Try This

Create semantically equivalent questions in plain language, formal wording, and a supported second language. Compare evidence, clarification, and escalation outcomes.

# How should the application explain uncertainty without hiding system failure?

## Answer

Explain whether facts are missing, evidence is absent, the source is inapplicable, or a backend is unavailable. Give the strongest supported statement while preserving a distinct failure status. Uncertainty should guide the next action rather than be a vague disclaimer appended to everything.

## Why

Return typed missing-input, insufficient-evidence, conflict, and unavailable states. Explain the next useful step without presenting an infrastructure failure as proof that no relevant record exists.

## Risk

An outage can be mistaken for proof that the policy says nothing. Reassuring language may also imply a specialist handoff that never happened.

## Trade-off

Explicit statuses require API and UI changes but make retries and support decisions honest. Text-only fallback is simple and ambiguous.

## Try This

Design separate responses for missing incident facts, no matching clause, source outage, stale policy, and completed escalation. Map each to a testable backend status.

# How do you retrieve the document version that applied on a given date, and what is bitemporal retrieval?

<!-- meta
domain: ai-rag
subdomain: evidence-applicability
module: evidence-applicability
concept: temporal and bitemporal retrieval
difficulty: design
misconception_target: Sorting by newest timestamp is the same as selecting the applicable version
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-29
-->

## Answer

**Two different questions.** 'Is this passage about cancellation?' is relevance. 'Did this version of the policy apply on 15 June 2025 for this customer?' is applicability. A superseded policy can be highly relevant and still wrong to cite for a current question; a historical question explicitly needs the old version.

**Model time explicitly.** Keep distinct fields: `valid_from` and `valid_to` define when the rules apply in the world; `published_at` records when the document became available; `known_at` (or transaction time) records when your system ingested it. A bitemporal model uses valid time and transaction time together, so you can answer both 'what applied on date X' and 'what did we believe applied on date X when we answered on date Y', which matters for audits and disputes.

**Retrieval design.** (1) Parse or request the as-of date from the user or application context; default to today for 'current' questions using the server clock, not the model's guess. (2) Apply the temporal predicate, tenant filter and authorization before or during search so superseded versions cannot compete in ranking. (3) Keep version relationships such as `supersedes` and `superseded_by`. (4) If the question spans versions ('what changed'), retrieve both explicitly and label them.

**Reading the example.** The as-of query for 15 June 2025 returns only the 2025 version, 15 June 2026 returns only the 2026 version, and the same 2026 date as known on 1 June 2025 returns nothing because that version was not yet known. Deterministic rules decide applicability; embeddings only rank within the eligible set.

**Pitfalls.** Open-ended ranges need a sentinel or null handling, inclusive versus exclusive end dates must be consistent, time zones matter at boundaries, and sorting by updated_at conflates edits to old documents with new applicable versions. Do not tell the LLM to 'use the latest document'; give it only the applicable evidence.

## Spoken Summary

Relevance and applicability are different. I store valid_from and valid_to for when a document's rules apply, plus published or known_at for when the system learned it, and apply an as-of filter before ranking. A question about June 2025 gets the 2025 version even if the 2026 text is more similar. Bitemporal retrieval adds a second axis so you can answer what we believed on a past date. Sorting by newest timestamp is not version-aware retrieval.

## Why

The example stores two policy versions with valid ranges and known_at dates, then selects by as_of and optionally by what was known at a past time, demonstrating the two time axes.

## Production Case

A customer asks what cancellation notice applied when they cancelled in June 2025. Similarity ranks the 2026 policy first. The as-of filter excludes it, the 2025 version is cited, and the audit record stores both the as-of date and the index state used.

## Risk

Citing a superseded policy because it ranks highest, or silently using the newest version for a historical question. Both produce confident, wrong answers.

## Trade-off

Temporal metadata requires reliable ingestion of effective dates and more complex queries, but it removes a class of high-severity errors and supports audits.

## Try This

Add a policy with valid_to = None (still active) and handle the open range, then add a time-zone-aware boundary test for 2025-12-31 23:30 in two zones.

## Execution Timeline

Resolve as-of date -> apply temporal, tenant and authorization filters -> retrieve and rank eligible versions -> label versions in evidence -> answer with applicability note

## Complexity

Temporal predicates add range checks that are cheap with an index on valid_from and valid_to; pre-filtering reduces the vector search candidate set.

## Definitions

- **Valid time**: The period during which a fact or rule applies in the real world.
- **Transaction time**: When the system recorded or learned a fact.
- **Bitemporal**: A model that tracks both valid time and transaction time.
- **As-of query**: A query evaluated against the state applicable at a chosen date.

## Alternatives

- Version tags with explicit user selection
- Separate indexes per version for small corpora
- Event-sourced document store with time-travel queries

## Pitfalls

- Using newest-first sorting
- Letting the model infer the as-of date
- Mixing valid time and publication time
- Inconsistent inclusive and exclusive range ends

## Follow-ups

### What is the difference between published_at and valid_from?

published_at is when the document became available; valid_from is when its rules start to apply. A policy can be published in December to apply from January, and retrospective corrections can be published after their valid period.

### How do you answer 'what changed between versions'?

Retrieve both versions explicitly by ID or date, align their sections by stable identifiers, and present differences with citations to each version rather than letting similarity choose.

### Where does this fit relative to authorization?

Both are eligibility filters applied before ranking. Authorization decides who may see a document; applicability decides whether it governs the question.

## Example

> Explanation: Select the policy version applicable at a business date, optionally as known at a past time.
> Output: verified

```python
"""Select the policy version applicable at a business date, optionally as known at a past time."""
from datetime import date

VERSIONS = [
    {"id": "policy-2025", "valid_from": date(2025, 1, 1), "valid_to": date(2025, 12, 31), "known_at": date(2024, 12, 20), "notice_days": 15},
    {"id": "policy-2026", "valid_from": date(2026, 1, 1), "valid_to": date(2026, 12, 31), "known_at": date(2025, 11, 30), "notice_days": 30},
]


def applicable(as_of, known_at=None):
    return [v["id"] for v in VERSIONS
            if v["valid_from"] <= as_of <= v["valid_to"]
            and (known_at is None or v["known_at"] <= known_at)]


assert applicable(date(2025, 6, 15)) == ["policy-2025"]
assert applicable(date(2026, 6, 15)) == ["policy-2026"]
assert applicable(date(2026, 6, 15), known_at=date(2025, 6, 1)) == []
print(applicable(date(2025, 6, 15)), applicable(date(2026, 6, 15)), applicable(date(2026, 6, 15), date(2025, 6, 1)))
```

## Citations

- https://martinfowler.com/articles/bitemporal-history.html
- https://www.postgresql.org/docs/current/rangetypes.html

# How should conflicting policy versions be resolved before an eligibility answer?

<!-- meta
domain: ai-rag
subdomain: evidence-applicability
module: evidence-applicability
concept: How should conflicting policy versions be resolved before an eligibility answer?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A current policy and a historical exception both appear in context, but the user has not supplied the relevant transaction date.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Determine the authoritative version and its effective conditions for the specific case. Retrieval rank does not decide legal or business applicability, and a general rule can have an overriding exception. If essential facts such as purchase date or product class are missing, ask a targeted clarification or abstain under the declared policy.

Concrete engineering case: A current policy and a historical exception both appear in context, but the user has not supplied the relevant transaction date.

Boundary defense: No. Indexing time and policy effective time are different. Use explicit authority and applicability metadata.

## Spoken Summary

Determine the authoritative version and its effective conditions for the specific case. Retrieval rank does not decide legal or business applicability, and a general rule can have an overriding exception. If essential facts such as purchase date or product class are missing, ask a targeted clarification or abstain under the declared policy.

## Why

Determine the authoritative version and its effective conditions for the specific case. Retrieval rank does not decide legal or business applicability, and a general rule can have an overriding exception. If essential facts such as purchase date or product class are missing, ask a targeted clarification or abstain under the declared policy.

## Production Case

A current policy and a historical exception both appear in context, but the user has not supplied the relevant transaction date.

## Risk

A current policy and a historical exception both appear in context, but the user has not supplied the relevant transaction date.

## Trade-off

No. Indexing time and policy effective time are different. Use explicit authority and applicability metadata.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: evidence applicability**: Determine the authoritative version and its effective conditions for the specific case.

## Alternatives

- No. Indexing time and policy effective time are different. Use explicit authority and applicability metadata.

## Pitfalls

- A current policy and a historical exception both appear in context, but the user has not supplied the relevant transaction date.

## Follow-ups

### Should the model simply choose the most recently indexed passage?

No. Indexing time and policy effective time are different. Use explicit authority and applicability metadata.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A current policy and a historical exception both appear in context, but the user has not supplied the relevant transaction date.",
  "required_decision": "Determine the authoritative version and its effective conditions for the specific case"
}
```

## Citations

- https://arxiv.org/abs/2005.11401

# How do conflicting rule versions, precedence and effective dates affect an eligibility explanation?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: evidence-applicability
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Relevance identifies material about the subject; applicability determines which rule governs the case. Compare jurisdiction, product, customer category, event date and effective interval, then apply an explicit precedence policy for conflicts. Publication time is not necessarily effective time, and a newer page may describe a future rule. Preserve superseded versions when historical cases need them. If necessary facts or precedence are missing, explain that uncertainty rather than allowing the generator to silently choose the most convenient passage.

## Why

A claim filed in June may concern an event in April under a rule replaced in May. Selecting only the newest document can apply the wrong eligibility conditions if event date controls the policy.

## Worked Case

A claim filed in June may concern an event in April under a rule replaced in May. Selecting only the newest document can apply the wrong eligibility conditions if event date controls the policy.

## Risk

Ranking score cannot settle a legal or business precedence rule.

## Trade-off

Retrieve alternatives and resolve applicability with declared domain policy.

## Try This

Build a timeline with two rule versions and show which facts select the governing version.

## Citations

- https://arxiv.org/abs/2005.11401
