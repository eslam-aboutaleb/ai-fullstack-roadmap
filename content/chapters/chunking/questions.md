<!-- chapter: chunking -->

# Why chunk documents at all?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: chunking
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**A chunk is an evidence retrieval unit, not an arbitrary slice of characters.** Start with document structure: headings, paragraphs, tables, lists and exception clauses. Preserve enough surrounding meaning to interpret the passage, while keeping chunks small enough for selective retrieval. Tokenize with the target model when enforcing hard model limits; a word-count estimate is only a planning aid. Retain the original source span and transformation profile so copied text can be audited.

A fixed-window splitter is predictable but can separate 'returns within 30 days' from 'except final-sale items'. Overlap improves boundary recall at the cost of duplicate candidates, storage and context tokens. Heading-aware splitting keeps sections intact but may produce oversized tables. A parent/child strategy retrieves small children and resolves a permitted parent; recheck access and budgets at expansion. Do not expand a visible paragraph into a confidential parent section.

**Work the evidence budget.** If the model permits 4,096 tokens, reserve 512 output, 384 system/tool instructions and 256 conversation tokens: 2,944 remain for retrieved evidence and separators. This is arithmetic under stated assumptions, not a provider capability claim. Packing five 700-token passages does not fit. Select evidence for marginal claim coverage, remove repeated overlap, and retain both the general rule and decisive exception. Prefer abstention to silently dropping the clause that changes the answer.

Evaluate chunking jointly with retrieval and citation quality. Compare fixed, structural and overlapping policies on the same revision-specific gold spans; record candidate recall, duplicate rate, final-context coverage and total tokens. A bigger chunk can improve recall while lowering precision or hiding the exception in a long context. The policy capstone uses lossless sentence chunks to expose spans and a deliberately removed exception; it does not assert that sentence chunking wins on scanned tables or multilingual documents. Revisit splitting when the parser, embedding model or source layout changes.

## Why

The general return rule and final-sale exception are separate spans. A top-k answer that includes only the general rule can be wrong even with a valid citation; the assessment must require decisive exception coverage.

## Worked Case

The general return rule and final-sale exception are separate spans. A top-k answer that includes only the general rule can be wrong even with a valid citation; the assessment must require decisive exception coverage.

## Risk

Overlap can make one fact appear repeatedly and dominate ranking, while stripping headings can erase conditions needed to interpret a table or list.

## Trade-off

Small chunks improve targeting but require context reconstruction. Large chunks reduce fragmentation while increasing irrelevant tokens and privacy exposure to downstream models.

## Try This

Compute the 2,944-token evidence allowance independently. Design three chunk boundaries for a rule plus exception, then identify which policy preserves source spans and decisive evidence under a smaller budget.

## Follow-ups

### What changes for a table split across scanned pages?

Preserve row/column headers, page coordinates and continuation relationships. OCR and layout reconstruction become part of the versioned transformation; a text-only sentence splitter is insufficient, so evaluate labeled table questions separately.

## Citations

- https://arxiv.org/abs/2005.11401
- https://www.w3.org/TR/annotation-model/

# Does a sliding-window chunker count tokens, words, or characters?

## Answer

It counts whitespace-separated words using text.split(). chunk_size and overlap therefore measure words. They do not define a model tokenizer's context size, and they do not behave identically for every language or code-heavy input.

## Why

The implementation steps through words by chunk_size minus overlap and rejoins each slice. This simple algorithm has no model dependency and is suitable as a transparent baseline.

## Risk

Treating 600 words as 600 tokens can overflow a downstream budget. Languages without whitespace and punctuation-heavy text can also produce surprising retrieval units. The evidence layer has a separate tokenizer abstraction for context accounting.

## Trade-off

Word splitting is fast and dependency-free, while token-aware or structure-aware splitting can better match actual model and document constraints.

## Try This

Chunk an English paragraph, a Python file, and Arabic text with identical settings. Count actual model tokens separately and compare the ratios.

# How does overlap affect recall and ingestion cost?

## Answer

Overlap repeats material near neighboring boundaries so that a question spanning a split still has a chance to retrieve a coherent chunk. The stride is chunk_size minus overlap. With long text, the repetition factor is roughly chunk_size divided by stride, ignoring the final partial window.

## Why

For size 600 and overlap 100, the stride is 500 and the approximate repeated-word factor is 1.2. This is a mathematical estimate of chunked input, not a measured provider billing factor or a quality guarantee.

## Risk

Excessive overlap produces near-duplicate hits and increases embedding work. Evidence deduplication and eligible span merging reduce redundant context, but they do not undo ingestion cost.

## Trade-off

More overlap can improve boundary coverage while reducing diversity among top hits. Tune against a labeled question set rather than maximizing repetition.

## Try This

Calculate chunk counts for 1,100 words at several overlaps, then verify them with sliding_window_chunk. Explain why the loop stops after the final covered window.

# Why validate that overlap is smaller than chunk_size?

## Answer

The stride must be positive for the window to advance. An overlap equal to the chunk size creates a zero stride; a larger overlap creates an invalid or backward progression. These are algorithm validity constraints, not optional quality preferences.

## Why

Both the function and the chunker constructor validate positive size and overlap in the interval from zero inclusive to size exclusive. Invalid configuration fails early before ingestion mutates versions or spends embedding calls.

## Risk

A malformed chunking configuration can block all ingestion or unexpectedly produce no chunks. Startup validation and focused boundary tests make such failures easier to diagnose than late failures inside a scheduled job.

## Trade-off

Strict validation rejects configurations that a permissive implementation might silently repair. Silent repair would conceal the actual indexing configuration and make snapshot identity less meaningful.

## Try This

Exercise zero size, negative overlap, overlap equal to size, and empty text. Distinguish invalid configuration from a valid empty result.

# How does a section-aware chunker preserve semantic structure?

## Answer

It splits Markdown on H2 headings, reconstructs a section with its title, and delegates that section to an inner chunker. Section titles therefore participate in embedded text rather than existing only as metadata. The inner strategy still controls subdivision of a long section.

## Why

Composition reuses the sliding-window algorithm while adding section, chunk index, and sub-chunk index metadata. File reading remains in the source adapter; the chunker operates on text.

## Risk

A regular expression for H2 headings is not a complete Markdown parser. Unusual markup and headings inside fenced code can create misleading boundaries. Evaluate actual corpus syntax before relying on section semantics.

## Trade-off

This wrapper is lightweight and understandable, while a full syntax-tree parser handles richer structure at higher implementation and dependency cost.

## Try This

Use a document with a preamble, H2 sections, H3 headings, and a fenced code sample containing a heading-like line. Inspect the exact emitted chunk text.

# Are chunk IDs deterministic in this implementation?

## Answer

Chunk IDs may be content-derived, position-derived, randomly generated, or scoped to an index generation. No choice is universally stable. Define identity around the operations it must support: deduplication, revision tracking, source lookup, and safe replacement.

## Why

Store document revision, span, chunker profile, and generation separately where needed. Test repeated chunking and document edits; stable identity requires an explicit contract rather than an assumption about UUIDs.

## Risk

Conflating position metadata with the actual store ID can break deduplication, deletion, and citation mapping. Comments about position-based chunk identifiers should be interpreted in the relevant adapter context, not generalized to every chunker.

## Trade-off

Random physical IDs avoid some collisions but need lifecycle tracking. Deterministic IDs simplify repeat writes but must include enough scope and revision information to avoid accidental replacement.

## Try This

Chunk identical input twice, edit a paragraph, and compare the identity guarantees of content-based, positional, and generation-scoped IDs.

# Why must chunker configuration be part of an ingestion fingerprint?

## Answer

The same source text produces a different index when chunk size, overlap, section handling, or algorithm version changes. Hashing only file content would incorrectly classify that index as current and skip the required rebuild.

## Why

The snapshot builder records chunker identity, version, and sanitized configuration alongside source and embedding information. snapshot_matches therefore represents compatibility of the indexing process rather than only equality of input bytes.

## Risk

A custom chunker that hides meaningful configuration can keep stale vectors active after a behavior change. A version property is useful only if maintainers update it when output semantics change.

## Trade-off

Detailed fingerprints trigger more rebuilds and improve reproducibility. Minimal fingerprints save work while making silent configuration drift more likely.

## Try This

Ingest unchanged text, change overlap, and ingest again. Verify that the snapshot changes even though the source hash remains equal.

# What would parent-child or hierarchical retrieval add?

## Answer

Parent-child retrieval searches fine-grained child chunks, then expands selected hits into a larger parent section or document for context. Hierarchical retrieval can first choose a topic or summary and then search within it. These are design extensions, not a default pipeline implemented by this reference design.

## Why

The retrieval service's metadata, fetch capabilities, and evidence assembly seams provide useful building blocks, but a host must implement expansion, identity mapping, authorization, and evaluation. Expansion should occur before final budgeting so its actual rendered size is counted.

## Risk

Parent expansion can expose unauthorized neighboring text or overwhelm context. A child being authorized does not automatically authorize every parent span or sibling chunk.

## Trade-off

More context may resolve ambiguity while increasing latency and irrelevant material. A simple section-aware chunker may be sufficient for a small structured corpus.

## Try This

Design an extension that expands a hit to its section. State which metadata is required and where scope checks and budget checks must run.

# How should chunking change for code, tables, and multilingual documents?

## Answer

Use boundaries that preserve the relationships questions depend on: functions and classes for code, row and column context for tables, and language-appropriate segmentation for text. A word window is a baseline, not proof that all these formats retain their semantics.

## Why

The Chunker protocol lets a host substitute a parser-based strategy without changing the entire ingestion pipeline. Metadata can preserve symbols, table identifiers, or locations for evidence presentation.

## Risk

Combining unrelated rows or truncating a function's preconditions can generate a misleading answer from faithfully quoted text. Arbitrary structure metadata also needs stable versioning and source lookup support.

## Trade-off

Specialized chunkers improve some domains while increasing maintenance and creating less comparable retrieval units. Maintain a shared evaluation interface across them.

## Try This

Build three questions that require a function's error branch, a table's unit header, and a multilingual synonym. Compare a structural chunker with the word-window baseline.

# How do I tune chunking scientifically?

## Answer

Hold the corpus, query set, embedding profile, backend settings, and evaluation procedure fixed while varying chunking. Measure retrieval recall and rank, evidence fit, answer faithfulness, index size, and embedding volume. Record configurations so the result is reproducible.

## Why

The retrieval service separates chunking from embedding and evaluation, making controlled experiments possible. Its snapshots help identify configuration changes, but they are not an experiment tracker by themselves.

## Risk

Optimizing on a handful of visible questions overfits the benchmark. Split tuning and held-out questions and include boundary cases, exact identifiers, long sections, and unanswerable queries.

## Trade-off

A full grid search costs indexing time. Start with a small set of plausible configurations and investigate failure examples before expanding the search.

## Try This

Compare three sizes with two overlaps and publish a table containing quality, indexed chunk count, and estimated embedding input. Explain the winning configuration's remaining failure cases.

# How does Semantic Chunking compute embedding distance thresholds between adjacent sentences, and why does adaptive percentile thresholding outperform fixed cosine cutoffs?

<!-- meta
answer_format: conceptual
domain: rag
subdomain: chunking
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Semantic chunking segments unstructured text into coherent, topical chunks by measuring cosine distance between adjacent sentence embeddings and splitting text only where semantic dissimilarity spikes.** Traditional fixed-length chunking (e.g., slicing every 500 characters or 200 tokens) blindly splits text across paragraph boundaries, mid-argument reasoning steps, and semantic definitions, separating related concepts and polluting vector indices with fragmented context.\n\n**The semantic distance calculation workflow.** Semantic chunking operates through four structured steps:\n1. *Sentence splitting:* The raw text is split into discrete sentences using rule-based or statistical tokenizers (e.g., spaCy, NLTK, or regex on sentence-ending punctuation).\n2. *Sliding context window embedding:* To ensure individual sentences have sufficient contextual richness, each sentence is concatenated with a small buffer of neighboring sentences (e.g., $k=1$ before and after) and passed through an embedding model.\n3.

*Distance calculation:* The cosine distance $d_i = 1 - \cos(e_i, e_{i+1})$ between each consecutive sentence embedding pair is computed, generating a sequential distance trajectory across the entire document.\n4. *Adaptive percentile thresholding:* Instead of applying a static, hardcoded distance threshold (e.g., splitting whenever $d > 0.3$), which fails across documents of varying writing styles and vocabulary densities, adaptive chunking computes a statistical breakpoint based on the document's own distance distribution: $\tau = \mu + k \cdot \sigma$, or by setting $\tau$ to the 90th or 95th percentile of distances within that document. Splits are inserted only at local maxima exceeding $\tau$, preserving long thematic sections while isolating sharp topic transitions.

## Why

A technical report discusses database indexing, transitions into query optimization, and concludes with hardware sizing. Fixed 200-word chunking splits the B-Tree index explanation across two separate chunks, blinding the retriever. Semantic chunking identifies the exact transition sentence where the discussion shifts to query optimization, isolating complete conceptual units.

## Worked Case

A technical report discusses database indexing, transitions into query optimization, and concludes with hardware sizing. Fixed 200-word chunking splits the B-Tree index explanation across two separate chunks, blinding the retriever. Semantic chunking identifies the exact transition sentence where the discussion shifts to query optimization, isolating complete conceptual units.

## Risk

Embedding every individual sentence in a 1,000-page document introduces significant computational overhead and embedding API latency during offline ingestion pipelines.

## Trade-off

Semantic chunking produces highly coherent chunks that maximize retrieval precision, at the expense of higher ingestion compute costs and variable chunk lengths that require secondary length guardrails.

## Try This

Implement semantic chunking in Python using sentence-transformers and NumPy. Calculate the pairwise cosine distances between sentences in a multi-topic blog post, plot the distance curve, and verify that split points coincide with topic shifts.

## Follow-ups

### What happens if a semantic chunk exceeds the embedding model's context window?

A secondary length guardrail must recursively apply token-based chunking with overlap to oversized semantic chunks to prevent silent truncation.

## Citations

- https://github.com/FullStackRetrieval-com/RetrievalTutorials
- https://docs.llamaindex.ai/en/stable/examples/node_parsers/semantic_chunking/

# How do Markdown AST-aware chunking parsers preserve structural hierarchy, code blocks, and complex tables without truncation corruption?

<!-- meta
answer_format: conceptual
domain: rag
subdomain: chunking
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Markdown AST-aware chunking parses text into an Abstract Syntax Tree (AST), preserving structural boundaries so that headers, code blocks, lists, and multi-line tables are never split across arbitrary character boundaries.** Plain-text chunking algorithms treat markdown symbols (`#`, ```, `|`, `-`) as ordinary strings. When a 500-token chunk boundary falls inside a Python code block or a 10-row Markdown table, the code syntax is truncated (missing closing brackets or imports) and the table loses its header row and delimiter formatting, turning clean structured data into garbled text that severely degrades LLM comprehension.\n\n**AST traversal and hierarchical grouping.** AST parsers (such as `markdown-it`, `mistletoe`, or tree-sitter) parse the document into structured semantic nodes:\n1. *Header hierarchy tracking:* As the parser traverses headings (`# H1`, `## H2`, `### H3`), it maintains an active breadcrumb stack (e.g., `# API Documentation > ## Authentication > ### OAuth2 Token Flow`). This breadcrumb is prepended to every child chunk, ensuring that retrieved text retains complete hierarchical provenance even when isolated from the document.\n2.

*Indivisible leaf nodes:* Nodes representing code blocks (````python ... ````) and tables (`<table>...</table>`) are marked as indivisible units. If a table's token count fits within the chunk budget, it is kept intact. If it exceeds the maximum chunk size, the parser splits it by rows while re-injecting the header row into every sub-chunk.\n3. *Recursive container aggregation:* The chunker aggregates sibling paragraphs and sub-sections until the token budget is reached, splitting only at semantic AST node boundaries rather than arbitrary character offsets.

## Why

An API documentation retriever returns a chunk containing the middle 5 lines of a SQL query without table names or SELECT statements, causing the LLM to hallucinate schema details. AST-aware chunking keeps the entire code block and its preceding markdown explanation together.

## Worked Case

An API documentation retriever returns a chunk containing the middle 5 lines of a SQL query without table names or SELECT statements, causing the LLM to hallucinate schema details. AST-aware chunking keeps the entire code block and its preceding markdown explanation together.

## Risk

Encountering malformed markdown (e.g., unclosed backticks or broken table syntax) can cause AST parsers to misclassify large portions of a document as raw text or fail with parsing exceptions.

## Trade-off

AST chunking guarantees grammatical and structural integrity and attaches valuable header metadata, but requires format-specific parsers and cannot be applied directly to arbitrary plain text.

## Try This

Parse a Markdown file containing a 20-row table using a standard LangChain `CharacterTextSplitter` versus an AST-aware `MarkdownHeaderTextSplitter`. Compare table completeness in the output chunks.

## Follow-ups

### How should oversized Markdown tables be chunked when they exceed the total model context window?

Convert the table rows into independent key-value JSON records or Markdown rows with repeated column headers prepended to each slice.

## Citations

- https://python.langchain.com/docs/how_to/markdown_header_metadata_splitter/
- https://github.com/executablebooks/markdown-it-py

# How does Hierarchical Parent-Child chunking resolve the fundamental tension between high-granularity vector search and rich LLM prompt context?

<!-- meta
answer_format: conceptual
domain: rag
subdomain: chunking
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Hierarchical Parent-Child chunking decouples the unit of retrieval from the unit of synthesis, indexing small, focused child chunks for precise vector matching while passing their large parent sections to the LLM for comprehensive reasoning.** Standard RAG architectures suffer from an inherent trade-off in chunk sizing:\n1. *Small chunks (e.g., 100-200 tokens):* Ideal for vector search because sentence embeddings have high semantic specificity and avoid averaging out key details. However, passing a 150-token fragment to an LLM leaves out necessary background, context, and nuance.\n2. *Large chunks (e.g., 1,500-2,000 tokens):* Provide rich, comprehensive context for LLM prompt generation. However, embedding a 2,000-token section dilutes specific facts, causing vector search to miss subtle queries and suffer from low cosine similarity scores.\n\n**The Parent-Child architecture.** Hierarchical chunking resolves this dilemma through a two-tier data model:\n1.

*Ingestion:* The document is first segmented into large parent chunks (e.g., 1,500 tokens). Each parent is then sub-divided into multiple smaller child chunks (e.g., 200 tokens). Each child chunk stores a reference attribute: `parent_id = parent.uuid`.\n2. *Indexing:* Vector embeddings are computed and indexed **only for the child chunks** in the vector database.\n3. *Retrieval & Expansion:* When a user query arrives, vector similarity search matches the top child chunks. Instead of feeding these raw child fragments to the LLM, the system reads their `parent_id`, looks up the full parent chunks from a key-value document store (e.g., Redis, MongoDB, or S3), deduplicates parent IDs, and passes the complete parent sections to the LLM prompt.

## Why

A user asks, 'What was the specific EBITDA margin in Q3?' A vector search on 200-token child chunks pinpoints the exact sentence with the percentage. The system then expands that child into its 1,500-token parent financial report section, allowing the LLM to explain the strategic drivers behind that EBITDA margin without hallucinations.

## Worked Case

A user asks, 'What was the specific EBITDA margin in Q3?' A vector search on 200-token child chunks pinpoints the exact sentence with the percentage. The system then expands that child into its 1,500-token parent financial report section, allowing the LLM to explain the strategic drivers behind that EBITDA margin without hallucinations.

## Risk

If multiple retrieved child chunks belong to distinct parents, expanding all of them can rapidly saturate the LLM's prompt context window with redundant information.

## Trade-off

Parent-child chunking dramatically improves both retrieval recall and generation quality, at the cost of requiring a secondary document store and extra lookup latency during the retrieval pipeline.

## Try This

Build a parent-child index using LlamaIndex or LangChain's `ParentDocumentRetriever`. Query a complex multi-page PDF and compare the accuracy and completeness of generated answers against a flat 500-token chunk baseline.

## Follow-ups

### Can parent-child chunking be extended to three or more hierarchical levels?

Yes, hierarchical tree index structures can link sentence-level nodes to paragraph parents, which link to section or full-document roots.

## Citations

- https://python.langchain.com/docs/how_to/parent_document_retriever/
- https://docs.llamaindex.ai/en/stable/examples/node_parsers/hierarchical/

# How do layout-aware PDF parsers reconstruct reading order and multi-column text flow, and why does naive OCR/stream extraction cause semantic fragmentation?

<!-- meta
answer_format: conceptual
domain: rag
subdomain: chunking
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Layout-aware PDF parsers use computer vision bounding boxes and spatial graph analysis to reconstruct true human reading order, preventing multi-column text interleaving and header/footer contamination.** PDF is not a document flow format; it is a presentation language designed for print reproduction. A PDF file contains positioned instructions (e.g., `BT /F1 12 Tf 72 712 Td (Hello) Tj ET`) that place text glyphs at absolute Cartesian coordinates $(x, y)$. PDFs possess no inherent concept of paragraphs, columns, tables, reading order, or reading flow.\n\n**The multi-column interleaving disaster.** When a naive PDF extractor (e.g., standard `pypdf` or raw `pdfminer`) extracts text by reading raw content streams, it reads glyphs in the order they were written to the file stream or sorted strictly by vertical coordinate $y$. In a two-column academic or financial paper, horizontal sorting reads across the entire page: line 1 of column 1 is concatenated with line 1 of column 2, line 2 of column 1 with line 2 of column 2.

The resulting text is an unintelligible, garbled mixture that completely destroys semantic embeddings.\n\n**Layout analysis and spatial heuristics.** Layout-aware tools (such as Marker, Nougat, MinerU, or Unstructured) apply document layout analysis models (YOLO, LayoutLM, or heuristic XY-cut algorithms):\n1. *Bounding box clustering:* Words are clustered into spatial blocks based on horizontal and vertical whitespace distances.\n2. *Column boundary detection & XY-Cut:* The page is recursively partitioned along continuous whitespace valleys. Vertical separators identify independent columns, ensuring that column 1 is completely read from top to bottom before processing column 2.\n3. *Header/footer and artifact suppression:* Text blocks recurring at identical $(x, y)$ coordinates across multiple pages with matching patterns (page numbers, running headers) are classified as peripheral artifacts and stripped to prevent polluting search indices.

## Why

Indexing an annual report formatted in three columns using standard PDF extraction interleaves balance sheet descriptions with unrelated footnotes. A layout-aware parser extracts each column sequentially, allowing chunking and vector embeddings to represent clean, continuous financial narrative.

## Worked Case

Indexing an annual report formatted in three columns using standard PDF extraction interleaves balance sheet descriptions with unrelated footnotes. A layout-aware parser extracts each column sequentially, allowing chunking and vector embeddings to represent clean, continuous financial narrative.

## Risk

Running deep vision-based layout models (e.g., LayoutLM or vision transformers) on millions of PDF pages increases ingestion compute costs and processing time by 50x compared to text-based extraction.

## Trade-off

Vision/spatial layout analysis ensures pristine, grammatically intact chunks from complex documents, requiring higher compute and specialized parsing libraries.

## Try This

Extract text from a two-column research paper using `pypdf` versus `pymupdf4llm` or `marker-pdf`. Inspect the extracted text of the abstract and verify column separation.

## Follow-ups

### What is the Recursive XY-Cut algorithm?

A spatial heuristic algorithm that recursively projects document pixels or word boxes onto X and Y axes to find whitespace valleys that cleanly partition multi-column pages.

## Citations

- https://github.com/VikParuchuri/marker
- https://pymupdf.readthedocs.io/en/latest/rag.html

# How do you evaluate chunk overlap without counting duplicate evidence as extra recall?

<!-- meta
domain: ai-rag
subdomain: chunking
module: chunking
concept: How do you evaluate chunk overlap without counting duplicate evidence as extra recall?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: Five top results are overlapping windows from one paragraph while the policy exception lives just outside all of them.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Define relevance at the appropriate source or passage identity, deduplicate overlapping hits under that evaluation contract and inspect answer-support coverage. Overlap can preserve context but increases storage, repeated tokens and correlated results. Evaluate boundary cases such as headings, exceptions and table rows instead of choosing chunk size solely by a convenient token number.

Concrete engineering case: Five top results are overlapping windows from one paragraph while the policy exception lives just outside all of them.

Boundary defense: No. Inspect structural boundaries, document parsing and retrieval diversity. More duplicate context can crowd out the needed evidence.

## Spoken Summary

Define relevance at the appropriate source or passage identity, deduplicate overlapping hits under that evaluation contract and inspect answer-support coverage. Overlap can preserve context but increases storage, repeated tokens and correlated results. Evaluate boundary cases such as headings, exceptions and table rows instead of choosing chunk size solely by a convenient token number.

## Why

Define relevance at the appropriate source or passage identity, deduplicate overlapping hits under that evaluation contract and inspect answer-support coverage. Overlap can preserve context but increases storage, repeated tokens and correlated results. Evaluate boundary cases such as headings, exceptions and table rows instead of choosing chunk size solely by a convenient token number.

## Production Case

Five top results are overlapping windows from one paragraph while the policy exception lives just outside all of them.

## Risk

Five top results are overlapping windows from one paragraph while the policy exception lives just outside all of them.

## Trade-off

No. Inspect structural boundaries, document parsing and retrieval diversity. More duplicate context can crowd out the needed evidence.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: chunking**: Define relevance at the appropriate source or passage identity, deduplicate overlapping hits under that evaluation contract and inspect answer-support coverage.

## Alternatives

- No. Inspect structural boundaries, document parsing and retrieval diversity. More duplicate context can crowd out the needed evidence.

## Pitfalls

- Five top results are overlapping windows from one paragraph while the policy exception lives just outside all of them.

## Follow-ups

### Can increasing overlap always repair the missing exception?

No. Inspect structural boundaries, document parsing and retrieval diversity. More duplicate context can crowd out the needed evidence.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "Five top results are overlapping windows from one paragraph while the policy exception lives just outside all of them.",
  "required_decision": "Define relevance at the appropriate source or passage identity, deduplicate overlapping hits under that evaluation contract and inspect answer-support coverage"
}
```

## Citations

- https://arxiv.org/abs/2005.11401

# How do you chunk a 100 GB stream without splitting records, losing provenance or exhausting memory?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: chunking
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Transport parts and retrieval chunks solve different problems.** A byte range is useful for transfer; a retrieval chunk should preserve meaning and fit the embedding tokenizer. Never assume that an upload part ends at a character, JSON record, paragraph or table boundary.

**Maintain bounded parsing state.** Decode text incrementally so a multibyte character split across reads survives. Then use a format-aware parser to identify records or document structures. Apply maximum record size, decompressed size and nesting limits. A file with one enormous record can defeat an otherwise streaming iterator; quarantine or use a parser designed for that structure. For formats requiring random access, use bounded scratch storage or a worker with appropriate resources.

**Create semantic windows within hard bounds.** Preserve headings, table headers, list structure and rule-exception relationships. Use token limits for the embedding model and a smaller retrieval target justified by evaluation. Carry overlap intentionally across semantic boundaries rather than repeatedly adding the entire prior chunk. Keep source byte offsets where reliable, page or section coordinates, parent identifiers and extraction/chunker versions. Offsets in extracted text are not interchangeable with offsets in the original binary file.

**Checkpoint only at reproducible boundaries.** Persist a record cursor and the deterministic identities of emitted chunks after durable writes. Decoder state or an arbitrary byte offset may be insufficient for restart. For compressed streams, restart from indexed compression boundaries or replay from an earlier safe checkpoint. Evaluate chunking on boundary-spanning questions and exclusions, not only chunk length statistics.

## Why

A UTF-8 character crosses a transport boundary, and a refund rule ends just before its exclusion. The decoder preserves the character; the chunker retains a parent link so retrieval can recover both clauses without including an entire book.

## Worked Case

A UTF-8 character crosses a transport boundary, and a refund rule ends just before its exclusion. The decoder preserves the character; the chunker retains a parent link so retrieval can recover both clauses without including an entire book.

## Risk

Unbounded lines, compression bombs and pathological tables can exceed the memory plan even when read buffers are small.

## Trade-off

Overlap improves boundary recall but adds embedding cost and duplicate evidence; compare against parent expansion.

## Try This

Create fixtures with split multibyte characters, a long record, repeated table headers and a cross-page exception. Verify stable chunk IDs after replay.

## Citations

- https://docs.python.org/3/library/codecs.html

# How do you evaluate semantic boundaries without confusing chunk size with retrieval quality?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: chunking
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Chunking decides which evidence remains together and which context must be recovered later. Fixed token windows provide predictable sizes, while structural boundaries can preserve headings, lists and exceptions. Neither guarantees a self-contained answer. Evaluate whether relevant facts, exclusions and provenance survive retrieval and final context assembly. Overlap increases storage and repeated context, and duplicated text can crowd out distinct evidence. Record the chunker version and parent relationship so changes can be reindexed and evaluated consistently.

## Why

A positive eligibility paragraph and its immediately following exclusion must be recoverable together. A small window may separate them; a huge window may waste budget and bury the decisive clause among unrelated sections.

## Worked Case

A positive eligibility paragraph and its immediately following exclusion must be recoverable together. A small window may separate them; a huge window may waste budget and bury the decisive clause among unrelated sections.

## Risk

Tuning only average chunk length can miss answer-critical boundaries.

## Trade-off

Combine size bounds with document structure and measured downstream evidence support.

## Try This

Compare two chunking policies on a rule, exclusion, table and cross-page reference.

## Citations

- https://arxiv.org/abs/2005.11401
