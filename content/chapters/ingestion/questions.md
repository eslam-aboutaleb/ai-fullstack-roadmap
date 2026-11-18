<!-- chapter: ingestion -->

# What are the phases of the ingestion workflow?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: ingestion
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**Preparation creates candidate knowledge; activation makes it searchable.** Model ingestion as discover/fetch → extract → normalize → chunk → embed → validate → activate. A document identity is different from its revision, content digest and transformation profile. Store all of them with page/character or bounding-box provenance so a citation can be resolved back to the actual input. Hash bytes before transformation; record the parser/OCR/chunker version and parameters rather than pretending equal filenames imply equal content.

For born-digital documents, extract the text and layout you need. For scanned pages, optical character recognition (OCR) estimates characters from pixels; it can confuse digits, omit negation or mix columns. Preserve page dimensions, coordinate convention and recognition confidence, then assess text and region accuracy on labeled permitted pages. Low confidence is not a calibrated correctness probability. Never turn a fabricated transcript into an alleged OCR measurement. The optional OCR lab requires a local engine and synthetic approved image; the policy capstone uses authored text and labels that boundary explicitly.

**Publish atomically.** Suppose revision 2 needs 100 chunks and a worker crashes after 90 embeddings. Keep revision 1 active until revision 2 is complete and validated. Reuse prepared artifacts only when their source digest and profiles match. At activation, compare the expected generation again: another worker may already have published revision 3. A short transaction or compare-and-swap controls that race; a preliminary check before remote work does not.

Treat malformed files, incomplete scans and confirmed deletions differently. Quarantine a poison item with a bounded error record; an unavailable folder is not proof its documents were deleted. Confirmed revocation should exclude results promptly even if physical cleanup lags. Impose file/page/CPU limits and isolate untrusted parsers; extension checks alone are not a sandbox. Test a failed replacement, stale activation, duplicate source revision and latest-revision tombstone. The policy project's sentence offsets and byte digests provide a small inspectable lineage oracle, not a production PDF parser.

## Why

A replacement policy crashes before all chunks exist. Keeping the prior active generation avoids publishing partial knowledge; a confirmed tombstone must nevertheless prevent a backfill from reviving an older policy.

## Worked Case

A replacement policy crashes before all chunks exist. Keeping the prior active generation avoids publishing partial knowledge; a confirmed tombstone must nevertheless prevent a backfill from reviving an older policy.

## Risk

An OCR error changing 30 to 90 or losing the word not can invert an answer while every downstream schema remains valid. Source validation and claim review must precede activation.

## Trade-off

Atomic full-generation replacement simplifies reads but temporarily duplicates storage. Incremental publication reduces work but requires explicit completeness, deletion and snapshot semantics.

## Try This

Run policy_assistant_project.py --check; inspect each offset against its original sentence. Design a failed 90/100-chunk replacement and show the active revision before, during and after recovery.

## Follow-ups

### What if an empty scan is actually an access outage?

Mark the scan incomplete and retain the previous publication according to the stale-data policy. Only an authoritative complete scan or explicit deletion event can authorize removal; emit an alert rather than interpreting an exception as empty truth.

## Citations

- https://www.postgresql.org/docs/current/mvcc-intro.html
- https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html

# Why is there a second snapshot check under the lock?

## Answer

Two workers can both read an old snapshot, prepare identical new vectors, and then reach the write phase. The second check detects that another worker already activated the intended snapshot and avoids duplicate version mutation.

## Why

_commit_ingestion reads the active version again before retiring anything. This is double-checked coordination: the early check avoids unnecessary work in the common case; the protected check handles races during preparation.

## Risk

The recheck is only serialized when the relevant locking and transaction semantics are actually enforced. Without a supplied lock key or equivalent host coordination, concurrent writes may still race.

## Trade-off

A second read costs a small amount of database work and does not prevent duplicate provider calls. It protects the authoritative mutation rather than promising exactly-once preparation.

## Try This

Pause two workers after their initial checks, let one commit, then release the second. Verify only one new active version appears when the lock contract is honored.

# What belongs in an ingestion snapshot?

## Answer

The snapshot should represent the inputs that determine indexed content: source manifest hash, extractor behavior, chunker identity and configuration, and embedding configuration or profile. A change to any of these can make existing vectors stale despite unchanged source text.

## Why

Read the active revision again inside the protected activation transaction. If it changed while preparation ran, compare the new state and either discard redundant work or retry under a defined conflict policy.

## Risk

Omitting hidden preprocessing or a model revision can cause false unchanged matches. Including unstable or secret-bearing fields can trigger needless rebuilds or expose credentials.

## Trade-off

Comprehensive snapshots improve repeatability while requiring disciplined adapter metadata. A simple content hash is easier but cannot detect pipeline changes.

## Try This

List every transformation between source bytes and stored vectors in your host. Identify which are represented in the snapshot and add a documented version for any custom transformation.

# What is idempotency, and what is idempotent in a reference design?

## Answer

An idempotent operation can be repeated without producing additional logical effects after the intended state is reached. Ingestion uses snapshot comparison to skip unchanged work and rechecks before mutation. That does not mean every low-level call executes once or always reuses identical physical chunk IDs.

## Why

Serialize a stable fingerprint from source revision, extraction and chunking versions, model profile, and indexing policy. Compare fingerprints only after defining which changes require a rebuild.

## Risk

Billing side effects, external writes, or custom version-store behavior may not be idempotent. The host must use stable operation identity and ensure repeated processing does not create duplicate application effects.

## Trade-off

Logical idempotency enables robust retries at the cost of hashes, state checks, and identity tracking. Exactly-once execution across external services is a much stronger claim.

## Try This

Run unchanged ingestion twice and count provider calls, active versions, and stored chunks. Then repeat after a forced failure immediately before commit.

# Who commits a caller-supplied database session?

## Answer

The caller owns a supplied session and its transaction. The pipeline yields it into the critical section but does not commit it. When the pipeline opens its own session, it commits after successful critical work. This ownership rule prevents a library from unexpectedly committing unrelated host changes.

## Why

_transacting_session implements the distinction and can acquire the advisory lock on a caller session when a lock key is supplied. The lock lifetime still follows the actual database and transaction behavior.

## Risk

A host that forgets to commit loses intended changes; a host that keeps the transaction open across slow preparation can retain connections and locks too long. Session ownership must be clear at integration boundaries.

## Trade-off

Caller ownership supports composing RAG writes with business operations, while library ownership simplifies isolated ingestion. Mixing the models implicitly is error-prone.

## Try This

Add an unrelated host row before calling ingestion with the same session. Roll back and verify whether both mutations obey the host's intended transaction.

# What does an advisory lock protect, and what does it not protect?

## Answer

An advisory lock coordinates cooperating processes using the same lock key and database locking mechanism. It can serialize the mutation phase for one source. It does not force unrelated code paths to honor the lock or create a distributed transaction with an external vector service.

## Why

The pipeline obtains the lock through a SQL adapter interface when lock_key is supplied. Lock-key derivation and consistent source scope are therefore part of the host's correctness contract.

## Risk

Inconsistent keys allow concurrent writers to bypass each other; overly broad keys serialize unrelated sources. A lock also does not guarantee that the shortest possible transaction duration has been measured.

## Trade-off

Fine-grained keys improve throughput while increasing key-management complexity. A global ingestion lock is simple but can become a bottleneck.

## Try This

Define lock keys for two tenants sharing a source name. Explain why including or excluding tenant scope changes both correctness and contention.

# How should authoritative emptiness differ from extraction failure?

## Answer

An authoritative empty dataset can mean that previously indexed content has been removed. A failed or incomplete read means the source state is unknown. The pipeline defaults empty input to a no-op and requires purge_on_empty to retire current content deliberately.

## Why

Non-authoritative a typed scan result is rejected before mutation. For a valid empty source, the purge path closes the active version and deletes its chunks inside the transacting session.

## Risk

Enabling purge for an adapter that reports failures as an ordinary empty list can destroy visibility of healthy content. Returning zero chunks is not enough information to decide deletion safely.

## Trade-off

Conservative defaults retain old knowledge during uncertainty but need a separate deletion and revocation policy. Aggressive replacement is simpler and more dangerous during source outages.

## Try This

Test a genuine empty source, an inaccessible source, and a parser returning no chunks from nonempty input. Explain why each path should have different effects.

# Why abort when nonempty documents produce zero chunks?

## Answer

Recording a new active snapshot with no useful chunks could make later runs classify the same source as already indexed and skip it indefinitely. Aborting before version mutation preserves the previous active content and allows a later retry after the chunker or extraction issue is fixed.

## Why

The pipeline explicitly checks for no chunks before embedding and before entering the critical section. This is a small guard protecting a large lifecycle invariant: an active snapshot should correspond to successfully prepared content.

## Risk

A host may misinterpret the returned zero as successful deletion or successful replacement. Diagnostics and status handling should distinguish aborted preparation from an authoritative empty purge.

## Trade-off

Retaining old content favors availability while freshness is unresolved. Some products should additionally mark it stale instead of silently treating it as current.

## Try This

Inject a chunker that returns an empty list for a nonempty source. Verify the old version remains active and that a subsequent valid chunker can ingest it.

# How does rollback interact with old-version retirement and new-vector upsert?

## Answer

The critical sequence retires the active version, deletes its chunks, creates the new version, stamps metadata, and upserts new chunks. With a shared transactional backend, a failure should roll all of that back. With nontransactional collaborators, this sequence alone cannot guarantee atomic replacement.

## Why

Passing one session is the mechanism for joining transactional writes. In-memory or remote adapters require their own consistency design; the manifest-based sync system addresses a different visibility model.

## Risk

Deleting old content before a remote upsert fails can leave an unavailable or inconsistent index. Do not assume a Python context manager can roll back writes in an external service.

## Trade-off

In-place transactional replacement is compact in one database. Generation preparation and activation use more storage and state but better fit cross-system operations.

## Try This

Inject an upsert failure after retirement. Test actual visibility and active-version state with your production adapter combination, not only a recording fake.

# Why are fixed claims such as microsecond swaps or sub-5-ms commits unreliable?

## Answer

The critical section includes reads, version mutations, deletion, and upsert, not merely a pointer assignment. Its duration depends on chunk count, database load, indexes, network latency, and adapter behavior. No timing benchmark in an illustrative implementation proves a universal duration.

## Why

Moving remote embedding out of internally owned mutation sessions is a sound architectural mechanism. That mechanism supports a narrower claim about resource occupancy, not an invented service-level objective.

## Risk

Designing connection pools or latency budgets around fictional timings can cause overload. Measure lock wait, transaction duration, upsert volume, and retry behavior under representative workloads.

## Trade-off

Shorter transactions reduce contention but preparation may still dominate end-to-end ingestion time. Optimization should target measured bottlenecks without weakening atomicity.

## Try This

Benchmark the critical section across increasing chunk counts. Report distributions and test conditions, and keep provider time separate from database time.

# How do you keep tables from PDFs meaningful in a RAG pipeline?

<!-- meta
domain: ai-rag
subdomain: ingestion
module: ingestion
concept: structure-preserving table ingestion
difficulty: debugging
misconception_target: If the PDF text was extracted, the table content is preserved
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-29
-->

## Answer

**Why tables break.** A PDF stores positioned glyphs, not semantic rows and columns. Text extractors may emit reading order that goes down columns, across rows, or mixes headers and footers. The result `Hospitalization Dental $100,000 $5,000` has lost which amount belongs to which coverage. No embedding model can repair information destroyed at extraction, and a question about dental limits can confidently return the wrong number.

**Pipeline.** (1) Classify the document: text-native, scanned, or layout-heavy. (2) Choose an extractor: libraries such as PyMuPDF or pdfplumber for text-native PDFs, OCR (optical character recognition) and layout models for scans. (3) Detect tables and extract them as a structure: columns, rows, spans and page. (4) Create retrieval chunks per row or per logical group in the form `Coverage type: Dental | Maximum amount: $5,000`, which repeats the header so a row is self-contained. (5) Attach provenance: document ID, page, table ID, bounding box if available. (6) For numeric questions keep the typed table in a structured store and retrieve rows by filters.

**Edge cases.** Tables spanning pages need header carry-over and a link between parts. Merged cells, footnotes that qualify values, and units in headers must be preserved. Charts need underlying data or a documented loss of precision.

**Evaluate the parser.** Build a gold set of tables with known cell values, then measure cell-level accuracy and row-column pairing accuracy per parser and document class. A parser that extracts more characters is not necessarily better. Add the parser version and settings to the ingestion fingerprint, send low-confidence extractions to a review state, and never silently index a table the parser flagged as uncertain.

## Spoken Summary

PDF is a layout format, so naive text extraction can read a table column by column and destroy row-column relationships, turning 'Dental $5,000' into text where the nearest amount is the wrong one. I choose a parser per document type, extract tables as structured rows with headers, and index row-level chunks that repeat the column names plus table ID and page number. I evaluate the parser on whether it preserves meaning, not on character count, and route scanned or layout-heavy files through OCR and layout analysis.

## Why

The example simulates column-wise extraction. A naive 'first dollar amount after Dental' answer returns $100,000, whereas row-level structured chunks return the correct $5,000 with page and table ID. The flattened string is a hand-made stand-in for a real extractor's failure mode.

## Production Case

An insurer's benefit schedule loses its row pairing in extraction and the assistant quotes the hospitalization limit for dental surgery. After switching to a table-aware parser and row-level chunks, the evaluation set shows pairing accuracy rising and the regression test stays in CI.

## Risk

A plausible but wrong number with a valid-looking citation. Without cell-level evaluation, the defect is invisible until a user notices.

## Trade-off

Structure-aware extraction needs heavier parsers, more compute and more engineering than plain text extraction, but it prevents errors that retrieval and generation cannot undo.

## Try This

Extend the example to a table spanning two pages whose second page lacks the header row, and write the carry-over logic that attaches headers to the continuation.

## Execution Timeline

Classify document -> choose parser -> detect tables -> extract columns and rows -> build header-carrying row chunks -> attach page and table provenance -> validate on gold cells -> index

## Complexity

Table-aware extraction costs more CPU or model inference per page than plain text extraction; row-level chunking increases the number of chunks roughly with row count.

## Definitions

- **Layout-oriented format**: A format that stores visual positions rather than semantic structure, like PDF.
- **OCR**: Optical character recognition: converting images of text into machine-readable text.
- **Row-level chunk**: A retrieval unit holding one table row together with its column names.
- **Provenance**: Recorded source details such as document, page and table identifier.

## Alternatives

- Vision-language models to read table images when parsers fail
- Structured data feeds from the source system instead of PDF scraping
- Manual review queue for high-value tables

## Pitfalls

- Judging parsers by character count
- Dropping table headers from chunks
- Ignoring page-spanning tables
- No provenance for citations

## Follow-ups

### When do you need OCR?

For scanned pages or images without selectable text. Detect this from empty or low-quality text extraction, run OCR with confidence scores, and route low-confidence output for review.

### How do you answer numeric questions about a table?

Prefer structured retrieval: store typed rows and query with filters or SQL, then show the cited row. Use embeddings for locating the right table, not for reading cells.

### What belongs in the ingestion status for failed documents?

Separate indexed, transient failure, permanent unsupported format and needs-manual-review states, with parser version and error details, so retries are safe and quality gaps are visible.

## Example

> Explanation: Column-wise PDF extraction scrambles a table; keep rows with headers and provenance.
> Output: verified

```python
"""Column-wise PDF extraction scrambles a table; keep rows with headers and provenance."""
import re

flattened = "Coverage type Maximum amount Hospitalization Dental $100,000 $5,000"


def naive_amount_after(label, text):
    after = text.split(label, 1)[1]
    return re.search(r"\$[\d,]+", after).group()


table = {
    "table_id": "benefits-1", "page": 3,
    "columns": ["Coverage type", "Maximum amount"],
    "rows": [["Hospitalization", "$100,000"], ["Dental", "$5,000"]],
}


def row_chunks(t):
    for row in t["rows"]:
        fields = " | ".join(f"{c}: {v}" for c, v in zip(t["columns"], row))
        yield {"text": fields, "table_id": t["table_id"], "page": t["page"]}


chunks = list(row_chunks(table))
structured = next(c["text"] for c in chunks if c["text"].startswith("Coverage type: Dental"))
assert naive_amount_after("Dental", flattened) == "$100,000"
assert structured.endswith("$5,000")
print("naive", naive_amount_after("Dental", flattened), "structured", structured, chunks[1]["page"])
```

## Citations

- https://pymupdf.readthedocs.io/en/latest/
- https://github.com/jsvine/pdfplumber

# What must ingestion do when an old source event arrives after a deletion?

<!-- meta
domain: backend
subdomain: ingestion
module: ingestion
concept: What must ingestion do when an old source event arrives after a deletion?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A deleted policy reappears because a delayed retry rewrites its text without comparing the stored deletion revision.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Preserve versioned deletion authority so an older upsert cannot resurrect a record. Bind source position and event identity to content, apply projection and recoverable progress under a clear transaction contract, and treat replay separately from new input. Include derived indexes and caches in visibility policy.

Concrete engineering case: A deleted policy reappears because a delayed retry rewrites its text without comparing the stored deletion revision.

Boundary defense: Not when retained source events, snapshots or backfills can recreate it. Keep the authoritative deletion or an equivalent replay guard.

## Spoken Summary

Preserve versioned deletion authority so an older upsert cannot resurrect a record. Bind source position and event identity to content, apply projection and recoverable progress under a clear transaction contract, and treat replay separately from new input. Include derived indexes and caches in visibility policy.

## Why

Preserve versioned deletion authority so an older upsert cannot resurrect a record. Bind source position and event identity to content, apply projection and recoverable progress under a clear transaction contract, and treat replay separately from new input. Include derived indexes and caches in visibility policy.

## Production Case

A deleted policy reappears because a delayed retry rewrites its text without comparing the stored deletion revision.

## Risk

A deleted policy reappears because a delayed retry rewrites its text without comparing the stored deletion revision.

## Trade-off

Not when retained source events, snapshots or backfills can recreate it. Keep the authoritative deletion or an equivalent replay guard.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: ingestion**: Preserve versioned deletion authority so an older upsert cannot resurrect a record.

## Alternatives

- Not when retained source events, snapshots or backfills can recreate it. Keep the authoritative deletion or an equivalent replay guard.

## Pitfalls

- A deleted policy reappears because a delayed retry rewrites its text without comparing the stored deletion revision.

## Follow-ups

### Does deleting the current search row suffice?

Not when retained source events, snapshots or backfills can recreate it. Keep the authoritative deletion or an equivalent replay guard.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A deleted policy reappears because a delayed retry rewrites its text without comparing the stored deletion revision.",
  "required_decision": "Preserve versioned deletion authority so an older upsert cannot resurrect a record"
}
```

## Citations

- https://www.postgresql.org/docs/current/transaction-iso.html
- https://beam.apache.org/documentation/programming-guide/
- https://kafka.apache.org/documentation/

# How would you ingest a 100 GB file with a server that has only 2 GB of RAM?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: ingestion
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Clarify RAM, disk and throughput separately.** A 100 GB object cannot reside in 2 GB of memory; it also cannot be retained on a 2 GB disk. The solution needs external durable storage or a streaming destination. Define whether 100 GB means decimal gigabytes and whether the file is compressed, encrypted, seekable or composed of independent records. A huge PDF and line-delimited JSON have different parsing requirements.

**Separate the control path from the bytes.** The application authorizes an upload session and chooses a tenant-scoped object key. The client sends independently retryable parts directly to object storage with scoped, expiring credentials. The application verifies completed object identity, size and integrity before scheduling processing. If traffic must pass through the server, disable whole-body buffering across the proxy and application and stream with strict concurrency bounds.

**Budget every live buffer.** An illustrative 2 GiB worker allocation is 512 MiB runtime, 256 MiB parser, 128 MiB embedding batches, 256 MiB network buffers and 256 MiB queues: 1,408 MiB allocated with 640 MiB headroom. Validate resident memory under adversarial inputs; object overhead, decompression and native libraries can invalidate the estimate. Bound both item counts and bytes. Two 64 MiB upload buffers need at least 128 MiB before SDK copies.

**Process incrementally with durable checkpoints.** Workers receive object references, not file bodies. Emit normalized records, semantic chunks, embedding requests and versioned index writes through bounded stages. Restart from safe record boundaries and idempotent identifiers. Quarantine files whose parser requires unavailable memory or scratch space. More concurrency helps only until memory, network or provider quotas become the bottleneck.

## Why

For a hypothetical 100,000,000,000-byte object using 64 MiB parts, ceiling division gives 1,491 parts. Uploading parts is separate from producing language-aware retrieval chunks. A worker crash at 60% should replay a bounded record range, not require another browser upload.

## Worked Case

For a hypothetical 100,000,000,000-byte object using 64 MiB parts, ceiling division gives 1,491 parts. Uploading parts is separate from producing language-aware retrieval chunks. A worker crash at 60% should replay a bounded record range, not require another browser upload.

## Risk

A streaming route may still buffer inside a reverse proxy, SDK, decompressor or document parser. Load-test the whole path.

## Trade-off

Direct uploads simplify application memory use but require upload lifecycle, ownership validation, cleanup and object-store access controls.

## Try This

Run with a memory limit, throttle the embedding stage and inject a parser crash. Record peak memory, queued bytes and the last durable checkpoint.

## Citations

- https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html

# How do you recover when an ingestion worker crashes after writing vectors but before saving its checkpoint?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: ingestion
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Assume at-least-once execution across services.** The vector database and the job store usually do not share one transaction. A worker can write data and crash before acknowledging its work. Acknowledging first instead creates the opposite failure: work can be lost. Design replay to be safe rather than claiming distributed exactly-once execution.

**Use deterministic identities and versioned publication.** Derive chunk identity from source version, parser/chunker version and stable position or content policy. Upsert the same logical chunk on retry, and persist a batch manifest with expected items and acknowledged results. If identifiers depend only on text hashes, two equal passages may incorrectly collapse distinct provenance; choose deduplication semantics explicitly.

**Protect against late writers.** A generation or fencing token identifies the currently valid indexing attempt. Verify that token when accepting results and before promotion. A worker whose lease expired cannot reactivate an older source version. Keep tombstones for deleted sources so retries cannot resurrect them. Reads use the active generation and authorization policy, not every vector that happens to exist.

**Reconcile independent stores.** Compare manifest entries against index records, retry missing writes and garbage-collect inactive generations after a retention period. Track terminal failures separately from unprocessed items. A complete count alone is insufficient if identifiers or vectors belong to the wrong version; verify provenance and model compatibility as well.

## Why

Worker A writes chunks 1–500 and dies before checkpointing. Worker B replays the batch with the same IDs, then advances the durable cursor. A later result from A carries an expired generation and is rejected from publication.

## Worked Case

Worker A writes chunks 1–500 and dies before checkpointing. Worker B replays the batch with the same IDs, then advances the durable cursor. A later result from A carries an expired generation and is rejected from publication.

## Risk

Random UUIDs on each retry turn a recoverable crash into duplicate evidence and inflated storage.

## Trade-off

Keeping inactive generations costs storage but makes rollback and consistency validation much safer.

## Try This

Inject crashes before write, after write and after checkpoint. Delete the source during replay and prove that no active result resurrects it.

## Citations

- https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html

# How do you publish a replacement retrieval index without exposing a partially built generation?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: ingestion
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Separate building from serving.** Assign an immutable generation identifier to the replacement corpus. Write chunks and vectors to that inactive generation while readers continue using the current active generation. Record a manifest containing the expected source versions, chunk identities, embedding configuration and validation results. A successful batch write is not evidence that the whole generation is ready.

**Validate before promotion.** Check for missing chunks, incompatible vector dimensions, duplicate identities, rejected records and source deletions. Run retrieval checks on the candidate generation, including authorization predicates. If some sources are allowed to fail, define that partial-publication policy explicitly and record the omissions. Otherwise leave the old generation active and report the failed build.

**Make visibility one guarded change.** Update the active-generation pointer in a short transaction only if the previously active generation and source revision still match expectations. A second publisher that built from stale assumptions must reload or abandon its candidate. Readers capture the active generation once per logical request and use that identifier for retrieval, parent expansion and citation lookup; rereading the pointer halfway through can combine incompatible versions.

**Match the guarantee to the storage boundary.** When chunks and the pointer share one transactional database, a transaction can publish them consistently. Across a vector service and a metadata database, do not imply that a database transaction covers both. Finish and verify the vector generation first, then publish its immutable reference. Retain the previous generation for rollback and in-flight readers, and garbage-collect it only after a defined retention boundary. The local example demonstrates transaction rollback of a pointer update; it does not simulate a distributed vector service.

## Why

A search request begins on generation g1 while g2 is being built. If g2 fails validation, requests continue on g1. After promotion, a request already pinned to g1 must still be able to resolve its cited chunks.

## Worked Case

A search request begins on generation g1 while g2 is being built. If g2 fails validation, requests continue on g1. After promotion, a request already pinned to g1 must still be able to resolve its cited chunks.

## Risk

Publishing a pointer before all referenced data is durable creates missing citations and inconsistent answers. Deleting the old generation immediately can break in-flight requests.

## Trade-off

Generation retention costs storage but gives an explicit rollback point and avoids making a long embedding job one database transaction.

## Try This

Inject failures during candidate writes, validation and pointer promotion. Assert that every visible pointer refers to a validated generation.

## Follow-ups

### What happens if the pointer cache is stale?

A stale pointer can serve the retained old generation consistently. Define acceptable freshness and cache invalidation, and never delete data while a permitted cached pointer can still reference it.

### Can rollback reuse the old pointer blindly?

Revalidate authorization changes and deletion intents before restoring an older generation. Operational rollback must not resurrect data that became forbidden after the original build.

## Citations

- https://www.postgresql.org/docs/current/transaction-iso.html
- https://www.sqlite.org/lang_transaction.html

# How do ingestion fingerprints distinguish unchanged content from changed embedding or parsing behavior?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: ingestion
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**A source hash answers only whether the source bytes changed.** Retrieval output also depends on extraction, normalization, chunking, overlap, tokenizer behavior, embedding model revision and metadata schema. Store a versioned fingerprint of the complete representation contract. Otherwise an unchanged file can incorrectly skip rebuilding after a model or parser change.

**Use stable serialization.** Construct a typed configuration record, serialize keys deterministically and hash the result. Include explicit defaults rather than relying on library defaults that may change. A mutable model alias is not an immutable model revision; record the actual resolved revision where the provider makes it available. Store the readable configuration alongside its digest so a mismatch is explainable.

**Differentiate kinds of change.** An access-scope update may need a payload update and cache invalidation without re-embedding if that field never entered the embedding input. A heading added to the embedding text does change the representation. A physical index tuning change may require an index rebuild but not another provider embedding call. Maintain separate source, representation and serving-index fingerprints when those operations have different costs.

**Protect historical semantics.** Do not relabel a changed chunker as an old version simply to avoid a migration. If a compatibility adapter really preserves historical output, prove that with golden fixtures covering headings, Unicode, tables and boundary conditions. On upgrade, compare candidate retrieval against a held-out query set and promote a new generation only after checks pass. The fingerprint is a decision aid, not proof that an implementation conforms to its claimed version.

## Why

A document is byte-identical, but its embedding model changes from revision A to B. A source-only hash skips the job incorrectly. A representation fingerprint changes and schedules a new compatible vector generation.

## Worked Case

A document is byte-identical, but its embedding model changes from revision A to B. A source-only hash skips the job incorrectly. A representation fingerprint changes and schedules a new compatible vector generation.

## Risk

Unknown or unstable serialization can cause either unnecessary full rebuilds or silent stale vectors.

## Trade-off

Separate fingerprints avoid expensive embedding calls for metadata-only changes but require clear dependency rules.

## Try This

List five configuration changes and classify each as payload update, re-chunk, re-embed or serving-index rebuild. Add a golden fixture for a claimed compatible parser upgrade.

## Follow-ups

### Does matching vector dimension prove compatibility?

No. Two models can emit equal-length vectors with unrelated geometry. Matching dimensions prevents one shape error; model and preprocessing identity determine whether similarity comparisons are meaningful.

### Should every application setting enter this digest?

Include settings that affect the representation. An unrelated logging level should not trigger re-embedding. Maintain an explicit dependency list and version its interpretation.

## Citations

- https://www.postgresql.org/docs/current/transaction-iso.html

# How do content hashes, source revisions and pipeline versions define reprocessing identity?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: ingestion
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A content hash identifies particular bytes under a chosen algorithm, while a source revision identifies a source-defined update. A pipeline version identifies extraction, normalization, chunking and representation behavior. Unchanged bytes can require reprocessing after a pipeline change; changed source metadata can matter even when text bytes remain equal. Store these identities separately and build deterministic derived keys from the required contract. A checksum is not a permission policy, and in-process hash values are not durable content digests.

## Why

An unchanged PDF processed by a corrected table extractor can produce different evidence. Skipping it solely because the file digest is unchanged preserves the original extraction error.

## Worked Case

An unchanged PDF processed by a corrected table extractor can produce different evidence. Skipping it solely because the file digest is unchanged preserves the original extraction error.

## Risk

A cache keyed only by source bytes can retain obsolete derived representations.

## Trade-off

Fine-grained versioning avoids unnecessary work while preserving correct invalidation.

## Try This

Define when source, extractor, chunker and embedding changes invalidate existing artifacts.

## Citations

- https://www.postgresql.org/docs/current/transaction-iso.html
- https://beam.apache.org/documentation/programming-guide/
- https://kafka.apache.org/documentation/
