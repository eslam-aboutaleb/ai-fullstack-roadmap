# RAG end-to-end synthetic capstone increment (#17)

Introduction: a strong RAG assistant is a data and retrieval system whose
model-generated answer is constrained by source evidence. Teach input
contracts, ingestion, metadata authorization, lexical/dense retrieval,
fusion, citation checking and abstention before introducing LLM provider APIs.

Offline runnable example: python3 -B labs/grounded_policy_pipeline.py
Uses deterministic, owner-scoped BM25, a toy cosine vector, RRF, and
an **extractive** citation-backed answer. Negative fixtures include a deleted
policy, another tenant's stronger matching source, absent evidence and
malicious source instructions. The intended return rule is measured by
gold-retrieval recall/MRR.

This does not use embeddings from a trained model, OCR, a live database,
a remote reranker or a generative LLM. Reproduce the fixture first, then
optionally build actual model and vector-store adapters with pinning,
claim-level faithfulness metrics, cross-domain gold sets, injection testing,
provider spend and independent content review.
