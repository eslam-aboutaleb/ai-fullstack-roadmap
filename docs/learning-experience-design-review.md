# Learning experience and advanced design review

Reviewed 21 October 2026. Changes extend the existing interview-led learning journey and preserve earlier study identifiers.

## Findings and changes

- Long chapters had a desktop table of contents, but it disappeared at narrower widths. Every chapter now includes a compact question directory that works on mobile and without JavaScript. JavaScript adds title search, Foundation/Deeper/Advanced scenario filters, counts, a clear empty state and reset. Filtering affects the directory only; answers and notes stay available.
- The deeper-section bulk answer control only opened answers. Both bulk controls now toggle open/closed with consistent labels and pressed state.
- Initial direct links could be closed again when asynchronous study-state initialization finished. A ready event now restores the requested answer after initialization.
- Re-selecting the same question fragment after closing its answer did not trigger a hash-change event. Directory links now reopen that answer, while explicit practice mode still keeps answers hidden.
- A new Design scenarios page, linked in the course navigation and each chapter directory, connects the advanced cases without duplicating answers or bypassing chapter prerequisites.
- Removed obsolete design-showcase prose describing separate concise and deep answers.

## New content

15 detailed advanced questions across 13 chapters cover:

1. Evidence exceeding a model context window: token ledger, retrieval versus exhaustive aggregation, source verification and unsupported scope.
2. Long-running context compaction: corrected constraints, untrusted summaries, durable task state and effect reconciliation.
3. A 100 GB upload with 2 GB RAM: external storage, direct multipart transfer, per-stage memory budgets and checkpoints.
4. Upload resume: ownership, expiration, integrity, completion/cancellation races and honest progress states.
5. Streaming chunking: incremental decoding, record and decompression limits, semantic boundaries, provenance and replay cursors.
6. Embedding backlog: token/request quotas, bounded queues, per-chunk retries, fairness and compatible index publication.
7. Ingestion recovery: deterministic identities, stale-worker fencing, tombstones and cross-store reconciliation.
8. Metadata filtering: eligibility versus relevance, candidate starvation, exact eligible-set baselines and authorization rechecks.
9. Metadata schema evolution: trusted versus inferred fields, effective time, indexes and deciding when re-embedding is needed.
10. Revocation: cached answers, resumed tasks, derived artifacts and streaming disclosure.
11. Choosing workflows, one agent or multiple agents from task structure and measured outcomes.
12. Bounded research: coverage, stopping rules, shared budgets and partial results.
13. Multi-agent research: task contracts, independent work, conflicting evidence, synthesis and root cancellation.
14. Concurrent agent effects: shared operation identities, conditional commitment, approval scope and unknown outcomes.
15. Architecture evaluation: equal-budget comparisons, independent outcome checks, ablations and uncertainty.

Every new question has a four-stage diagram and a failure exercise. Three executable standard-library examples illustrate token capacity, upload capacity and post-filter candidate starvation. Numerical scenarios are original illustrative assumptions, not provider benchmarks or claims of measured production capacity. All new answers retain the project's independent-review-pending status.

## Primary references visited

These pages were opened during this review to check mechanisms. Citations are attached to the relevant answers. Provider-specific APIs and limits still require checking against the implementation version.

- [S3 multipart upload](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)
- [S3 presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
- [Azure vector filtering](https://learn.microsoft.com/en-us/azure/search/vector-search-filters)
- [Qdrant filtering](https://qdrant.tech/documentation/search/filtering/)
- [PostgreSQL row security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Python incremental codecs](https://docs.python.org/3/library/codecs.html)
- [Python bounded asynchronous queues](https://docs.python.org/3/library/asyncio-queue.html)
- [Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [Context engineering](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)
- [Multi-agent research systems](https://www.anthropic.com/research/multi-agent-research-system)

## Validation scope

The browser regression covers scenario-to-answer navigation, combined directory filters, empty/reset behavior, keeping the complete lesson available, bulk toggles, reopening the current fragment and mobile overflow. Accessibility checks include the new scenario page and expanded chapter directory. Existing build checks cover stable identities, diagrams, literal source fidelity and executable examples. No real 100 GB transfer, provider embedding job or production agent run is claimed.

Validation results: `make check` passed (202 pages, 22,512 internal links, 1,103 chapter questions, 966 code associations). Root Chromium checks and 30 automated accessibility checks passed. Desktop (1440px) and mobile (390px) directory screenshots were inspected.
GitHub Pages subpath Chromium checks also passed; the default root preview was rebuilt afterward.
