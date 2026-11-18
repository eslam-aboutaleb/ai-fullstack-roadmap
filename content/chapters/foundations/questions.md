<!-- chapter: foundations -->

# What is RAG, and how does a retrieval service fit into an AI application?

<!-- meta
domain: ai-rag
subdomain: retrieval
concept: What is RAG, and how does a retrieval service fit into an AI application
difficulty: foundations
misconception_target: RAG is just fine-tuning with documents
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

RAG means Retrieval-Augmented Generation. Before asking a language model to answer, your application finds relevant information and puts that information into the model request. The model can then explain your actual document instead of guessing from its training. A retrieval service is the part that finds and returns those passages. It does not automatically supply the chat interface, user permissions, or final answer checks.

## Spoken Summary

RAG combines retrieval with generation: find permitted, relevant, versioned evidence and give it to a model to help answer a task. Retrieval can improve grounding and freshness, but correctness still depends on source quality, applicability, citations and evaluation. It does not replace application state or permissions.

## Why

First, prepare the documents for search: read them, split them into passages, and store those passages with searchable representations. Later, when a user asks a question, search for useful passages and send their text to the model together with the question. These are two different workflows. Updating the searchable document can change the next answer without changing the model weights.

## Production Case

A support assistant retrieves an old return policy that matches the words perfectly. Version/applicability checks and a fixed regression query should reject the stale evidence despite high similarity.

## Risk

A search may return the wrong passage, or the model may misread the right passage. Check whether the selected source actually supports the answer. If the required rule is missing or the search service failed, report that state rather than inventing a rule.

## Trade-off

RAG supports changing information and inspectable sources, but you must operate indexing, permissions, search, context selection, and evaluation. A simple structured lookup is a better choice for an exact request status or a financial total.

## Try This

Trace one document through ingestion and one question through search. Draw the boundary where your own generator must be called.

## Execution Timeline

User asks question -> Application searches document index -> Relevant passages retrieved -> Passages + question sent to model -> Model generates answer using evidence

## Complexity

Measure retrieval, reranking, context assembly and generation separately. ANN has no universal O(log n) guarantee; corpus geometry, parameters, filtering, model/token lengths and hardware affect cost.

## Definitions

- **Retrieval**: Finding relevant information from a document collection
- **Generation**: Producing an answer from retrieved evidence
- **RAG**: Retrieval-Augmented Generation: combining retrieval with language model generation

## Alternatives

- Fine-tuning for style adaptation
- Structured database lookup for exact values

## Pitfalls

- Retrieval returns wrong passage
- Model misreads correct passage
- Missing evidence leads to hallucination

## Follow-ups

### Does adding retrieval eliminate hallucinations?

No. Retrieval can miss evidence, return misleading material or be ignored by the model. Evaluate the whole evidence-to-answer path.

## Example

> Explanation: Search for relevant passages, then feed them to the model with the question.
> Output: An answer grounded in the retrieved document text.

```python
passages = search_index.query("return policy")
answer = model.generate(question, context=passages)
```

## Citations

- https://developer.mozilla.org/en-US/docs/Web/HTTP

# Why can an LLM sound confident while being wrong?

## Answer

A Large Language Model predicts token sequences using learned patterns. Fluent continuation and factual verification are different capabilities. If the prompt lacks the relevant fact, or includes ambiguous evidence, a plausible continuation can still be false. Confidence in the prose is not a calibrated probability that the service request is correct.

## Why

In the reference design, the retrieval and evidence layers supply inspectable material before a host invokes generation. an evidence-status type distinguishes missing evidence from a failed backend, giving the application a basis for abstaining or asking a follow-up question.

## Risk

Presenting a citation does not establish that the citation supports the attached sentence. the retrieval service preserves evidence identity, while claim-to-evidence checking and appropriate abstention remain host responsibilities.

## Trade-off

Restricting answers to supplied evidence improves auditability but can reduce coverage. Allowing general model knowledge expands coverage while weakening the promise that every answer reflects the indexed corpus.

## Try This

Ask one answerable, one ambiguous, and one unanswerable question. Write separate expected behaviors before evaluating any generated output.

# How are search, retrieval, and generation different responsibilities?

## Answer

Search ranks records against a query. Retrieval includes query preparation, backend selection, constraint enforcement, candidate fetching, and optional reranking. Generation turns the resulting evidence and instructions into a new answer. Treating these as one function hides whether an error came from missing data, ranking, or answer synthesis.

## Why

A hybrid retriever and the strategy classes orchestrate search; an evidence assembler builds a bounded evidence bundle. Their return types are useful without a chat model. This separation also supports source verification tools and ordinary search interfaces.

## Risk

A fallback that silently generates when search fails can convert an infrastructure outage into misinformation. Use strict retrieval and propagate backend failure into the host's response state.

## Trade-off

Explicit stages require more wiring and more status handling. They also let you benchmark retrieval independently and switch generation providers without rebuilding the corpus.

## Try This

Design three response payloads: successful evidence, successful empty search, and backend failure. Explain which may safely reach generation.

# When should I use RAG instead of fine-tuning or a SQL query?

## Answer

Use retrieval when answers depend on a changing collection and need source attribution. Use a structured query when the task is exact aggregation over authoritative fields. Consider fine-tuning when the persistent problem is behavior, style, or task adaptation rather than missing up-to-date facts. These approaches can be combined.

## Why

The retrieval service's document and evidence abstractions suit passage retrieval. A question such as total approved invoices this month should usually reach a database computation; nearest passages cannot guarantee an exact total. Fine-tuning is not implemented by this subsystem.

## Risk

A semantic similarity score can make an approximate answer look exact. The host must route tasks appropriately and preserve authorization on both document search and structured tools.

## Trade-off

Task routing adds complexity but avoids forcing every question through a vector index. A single retrieval path is easier to prototype and easier to misuse.

## Try This

Classify ten realistic product questions into passage retrieval, database computation, general explanation, or behavior adaptation. Defend two borderline cases.

# What is the difference between a document, a chunk, a vector, and evidence?

## Answer

A document is a source-level unit of text and metadata. A chunk is a searchable subdivision. An embedding vector is a numerical representation of that subdivision. Evidence is selected, attributed text prepared for a consuming model or user. These objects have different lifetimes and should not share one overloaded identity field.

## Why

The canonical Chunk, Document, and SearchResult dataclasses separate ingestion and search shapes; evidence types add revision, source, span, and citation information. A chunk hit becomes useful evidence only after selection and attribution.

## Risk

Confusing a chunk ID with a document ID breaks deletion, citation lookup, and version switching. the retrieval service carries metadata through the pipeline, but hosts must supply stable source identities and meaningful provenance.

## Trade-off

More explicit types require conversion at boundaries. They reduce accidental field loss and make changes to storage independent of the user-facing citation contract.

## Try This

Annotate a sample result with its source ID, document ID, revision, chunk ID, text, vector dimension, and evidence label. Identify which fields can change after reindexing.

# What do dense and sparse retrieval mean?

## Answer

Dense retrieval compares learned vectors, making semantic paraphrases discoverable. Sparse or lexical retrieval scores token-based signals, making exact names, identifiers, and unusual terms discoverable. They capture different notions of relevance. Neither should be described as understanding the user's authorization or guaranteeing truth.

## Why

The retrieval service separates a vector index and a lexical index capabilities and composes them in hybrid retrieval. PostgreSQL offers native full-text search; some other adapters approximate lexical ranking with token overlap. Those are different implementations, not equivalent language models.

## Risk

Dense retrieval can confuse related concepts; lexical retrieval can miss synonyms. Hybrid fusion reduces dependence on one signal but adds its own ranking choices and cannot recover absent source material.

## Trade-off

Two signals increase implementation and evaluation cost. A keyword-only strategy can be preferable for exact support codes or a prototype with no embedding service.

## Try This

Create queries containing a product code, a paraphrase, and a misspelling. Predict which retrieval stage should help, then inspect both ranked lists.

# What does grounding actually guarantee?

## Answer

Grounding means giving an answer process explicit evidence it can use. It is a relationship between a service request and supporting material, not a property conferred by vector search alone. A grounded workflow must preserve provenance, show the relevant revision, and handle insufficient evidence honestly.

## Why

An evidence assembler deduplicates, merges eligible spans, budgets rendered context, and creates citation labels. revision-aware source lookup can retrieve a bounded span from a retained revision. These mechanisms make verification possible rather than automatically performing every verification step.

## Risk

A wrong retrieved passage, stale document, or unsupported inference can survive into the answer. Host-side citation checks and evaluation are still necessary; delimiter escaping is only one mitigation against untrusted source instructions.

## Trade-off

Strong attribution needs snapshot retention and richer metadata. Minimal text-only search is cheaper but cannot support reliable historical verification.

## Try This

Write an answer with three factual claims. Map each claim to an exact evidence span; flag any sentence whose support requires an unstated inference.

# How do relevance, correctness, faithfulness, and freshness differ?

## Answer

Relevance asks whether material addresses the question. Correctness asks whether the service request is true. Faithfulness asks whether the answer follows the provided evidence. Freshness asks whether the evidence reflects an appropriate time or revision. An answer can be faithful to an obsolete policy and therefore be incorrect for today's user.

## Why

The reference design separates retrieval evaluation from answer evaluation and carries freshness and revision fields in evidence. These signals allow a host to assess different failure modes rather than collapse quality into a single score.

## Risk

High retrieval recall does not establish answer correctness. A heuristic overlap score also cannot establish that a reasoning step is valid or that the source itself is authoritative.

## Trade-off

Multiple metrics complicate release decisions but expose regressions that one average hides. The right acceptance criteria depend on the product's questions and corpus.

## Try This

Construct four answers that each fail a different dimension. Explain which measurement and which code boundary would reveal each failure.

# What are the main cost and latency stages in a RAG request?

## Answer

Typical stages are query transformation, query embedding, candidate search, fusion, reranking, evidence assembly, and host generation. Ingestion has separate extraction, chunking, embedding, and storage costs. The relative expense depends on providers, data size, network placement, and configuration; this reference design does not establish universal timings.

## Why

Separating candidate_k from final_k permits a larger search pool without necessarily sending every hit to generation. Telemetry records stage events and durations, and the embedding executor bounds concurrency and provider call duration when configured.

## Risk

Increasing query variants, candidate counts, and retries together can multiply load. No single semaphore controls an entire fleet or gives an end-to-end request deadline.

## Trade-off

Higher candidate recall often costs more latency and money. Optimize against a quality target using measured stage distributions, not guessed millisecond service requests.

## Try This

Create a latency budget spreadsheet with p50 and p95 per stage and an overall deadline. Mark every number as a hypothesis until you measure it.

# What does domain-agnostic mean, and what does it not solve?

## Answer

Domain-agnostic means the core can work with different application schemas, sources, settings, and storage implementations through explicit interfaces. It does not mean every domain has identical chunking needs, permissions, legal retention rules, or quality thresholds. Those knowledge rules remain part of the host's product design.

## Why

The retrieval service receives settings, sessions, version storage, embedders, and retrieval strategies rather than importing a host's models. The same core can serve a knowledge corpus or a support corpus while their adapters and evaluation datasets differ.

## Risk

Generic abstractions can hide important domain constraints if the host never models them. A tenant filter is useful only when trusted identity selects the correct scope and every storage path respects it.

## Trade-off

Reusability reduces coupling but requires deliberate integration work. A specialized application may be quicker initially and harder to reuse safely later.

## Try This

Compare an HR policy assistant and a public FAQ assistant. List five knowledge rules that differ even if they use identical the retrieval service components.

# A retrieved policy is relevant but no longer applicable. What makes the RAG answer defensible?

<!-- meta
domain: ai-rag
subdomain: foundations
module: foundations
concept: A retrieved policy is relevant but no longer applicable. What makes the RAG answer defensible?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: The top-ranked result describes last year’s refund rule, while the current rule has a sale-item exception.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Relevance is only one gate. Filter by caller authority, source revision, effective date and the case’s applicability before using a passage. Then inspect whether each material claim is supported by the selected evidence. Return an evidence gap or a focused clarification when those conditions cannot be established; a plausible answer with a citation is insufficient.

Concrete engineering case: The top-ranked result describes last year’s refund rule, while the current rule has a sale-item exception.

Boundary defense: No. More conflicting or obsolete text can increase ambiguity. Establish authority and applicability before optimizing context size.

## Spoken Summary

Relevance is only one gate. Filter by caller authority, source revision, effective date and the case’s applicability before using a passage. Then inspect whether each material claim is supported by the selected evidence. Return an evidence gap or a focused clarification when those conditions cannot be established; a plausible answer with a citation is insufficient.

## Why

Relevance is only one gate. Filter by caller authority, source revision, effective date and the case’s applicability before using a passage. Then inspect whether each material claim is supported by the selected evidence. Return an evidence gap or a focused clarification when those conditions cannot be established; a plausible answer with a citation is insufficient.

## Production Case

The top-ranked result describes last year’s refund rule, while the current rule has a sale-item exception.

## Risk

The top-ranked result describes last year’s refund rule, while the current rule has a sale-item exception.

## Trade-off

No. More conflicting or obsolete text can increase ambiguity. Establish authority and applicability before optimizing context size.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: foundations**: Relevance is only one gate.

## Alternatives

- No. More conflicting or obsolete text can increase ambiguity. Establish authority and applicability before optimizing context size.

## Pitfalls

- The top-ranked result describes last year’s refund rule, while the current rule has a sale-item exception.

## Follow-ups

### Would a larger context window necessarily repair this?

No. More conflicting or obsolete text can increase ambiguity. Establish authority and applicability before optimizing context size.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "The top-ranked result describes last year’s refund rule, while the current rule has a sale-item exception.",
  "required_decision": "Relevance is only one gate"
}
```

## Citations

- https://docs.python.org/3/tutorial/
- https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control

# When is RAG unnecessary, and when should a task use a database query or deterministic rule?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Retrieval-augmented generation is useful when answering requires external unstructured evidence and language synthesis. It adds failure modes in indexing, ranking, context construction and generation. Exact account balances, authorization decisions and well-defined arithmetic should generally use authoritative structured operations rather than similarity search over copied text. A hybrid application may retrieve policy language while querying current account state and applying a deterministic eligibility rule. Choose each component from its needed authority and output contract.

## Why

To answer 'what is my current balance?', query the authenticated account record. A retrieved statement from last month can explain history but cannot establish the current amount simply because it ranks highly.

## Worked Case

To answer 'what is my current balance?', query the authenticated account record. A retrieved statement from last month can explain history but cannot establish the current amount simply because it ranks highly.

## Risk

Treating a retrieved passage as current transactional truth can mislead users and actions.

## Trade-off

Use generation for explanation where helpful while retaining authoritative operations for exact state.

## Try This

Separate evidence, live state, arithmetic and authorization for one support workflow.

## Citations

- https://docs.python.org/3/tutorial/
- https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control

# How do you diagnose a wrong RAG answer without blaming the model first?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Debug a wrong answer by finding the **first failed evidence boundary**. Changing the model before locating that boundary can hide the cause and add cost.

1. **Source:** Does the correct revision contain the necessary fact, date or exception?
2. **Extraction and chunking:** Did processing preserve its text, relationships and provenance?
3. **Representation and filtering:** Is it indexed with a compatible embedding profile and visible to the authorized caller?
4. **Candidate retrieval:** Was it retrieved before reranking? A reranker cannot recover an absent candidate.
5. **Final context:** Did selection retain the decisive material under the token budget?
6. **Generation and support:** Does each answer claim follow from the included applicable evidence?

Retain stable source, chunk, index, prompt and model identities so one failure can be replayed at each stage. Compare one controlled change at a time.

A fluent answer can cite a positive eligibility clause while omitting a nearby exclusion. If the exclusion disappeared during chunking or context selection, a higher generation temperature or longer answer cannot supply the missing authority. Use **stage-specific checks to diagnose** and an **end-to-end evaluation to assess user impact**.

## Why

A policy exclusion exists in the source but is separated from the positive clause and omitted from the final context. The answer can be fluent and cite the positive clause while still contradicting the actual rule.

## Worked Case

A policy exclusion exists in the source but is separated from the positive clause and omitted from the final context. The answer can be fluent and cite the positive clause while still contradicting the actual rule.

## Risk

An end-to-end score alone does not localize the defect.

## Trade-off

Stage-specific evidence speeds repair while end-to-end checks assess user impact.

## Try This

Build a failure trace showing the first boundary where necessary evidence disappears.

## Citations

- https://docs.python.org/3/tutorial/
- https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control
