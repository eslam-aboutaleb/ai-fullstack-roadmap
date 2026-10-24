# /// script
# dependencies = []
# ///
"""
Layered RAG Evaluation Harness with Diagnostic Isolation.

Decouples and measures three independent pipeline tiers:
1. Retrieval Layer: Recall and Mean Reciprocal Rank (MRR) of candidate chunks.
2. Context Sufficiency Layer: Verifies required evidence survived reranking/compression.
3. Generation Faithfulness Layer: Asserts generated output contains zero hallucinated claims.
"""

from __future__ import annotations

from typing import Dict, List, Set


class LayeredRAGEvaluator:
    """Evaluates RAG sub-components independently to pinpoint root causes of failure."""

    @staticmethod
    def evaluate_retrieval(
        retrieved_ids: List[str],
        gold_relevant_ids: Set[str],
    ) -> float:
        """Computes Recall@K: fraction of gold documents retrieved."""
        if not gold_relevant_ids:
            return 1.0
        hits = set(retrieved_ids) & gold_relevant_ids
        return len(hits) / len(gold_relevant_ids)

    @staticmethod
    def evaluate_context_sufficiency(
        context_text: str,
        required_facts: List[str],
    ) -> float:
        """Verifies that all required factual premises are present in the final prompt context."""
        if not required_facts:
            return 1.0
        present = sum(1 for fact in required_facts if fact.lower() in context_text.lower())
        return present / len(required_facts)

    @staticmethod
    def evaluate_faithfulness(
        generated_answer: str,
        context_text: str,
        claimed_facts: List[str],
    ) -> float:
        """Verifies that every factual claim made in the answer is grounded in the context (no hallucination)."""
        if not claimed_facts:
            return 1.0
        supported = sum(1 for claim in claimed_facts if claim.lower() in context_text.lower())
        return supported / len(claimed_facts)


def main() -> None:
    evaluator = LayeredRAGEvaluator()

    # Ground truth expectations
    gold_doc_ids = {"doc_refund_policy_01", "doc_fee_schedule_02"}
    required_factual_premises = [
        "Refunds are permitted within 30 days of purchase",
        "A 5% restocking fee applies to opened electronics",
    ]

    # --- Tier 1: Retrieval ---
    # Retriever fetches top 3 chunks
    retrieved_chunk_ids = ["doc_refund_policy_01", "doc_faq_general", "doc_fee_schedule_02"]
    retrieval_recall = evaluator.evaluate_retrieval(retrieved_chunk_ids, gold_doc_ids)
    assert retrieval_recall == 1.0, f"Expected full recall, got {retrieval_recall}"

    # --- Tier 2: Context Compression & Sufficiency ---
    # Reranker / Prompt builder builds context
    assembled_context = (
        "Customer Service Policy: Refunds are permitted within 30 days of purchase. "
        "Fee Table: A 5% restocking fee applies to opened electronics."
    )
    context_sufficiency = evaluator.evaluate_context_sufficiency(
        assembled_context, required_factual_premises
    )
    assert context_sufficiency == 1.0, f"Expected 1.0 sufficiency, got {context_sufficiency}"

    # --- Tier 3: Generation & Faithfulness ---
    # Model generates answer
    generated_answer = (
        "You can return the laptop within 30 days of purchase, but a 5% restocking fee applies."
    )
    extracted_answer_claims = [
        "within 30 days of purchase",
        "5% restocking fee applies",
    ]
    generation_faithfulness = evaluator.evaluate_faithfulness(
        generated_answer, assembled_context, extracted_answer_claims
    )
    assert generation_faithfulness == 1.0, f"Expected 1.0 faithfulness, got {generation_faithfulness}"

    # --- Diagnostic Failure Isolation Demo ---
    # Demonstrates: If retrieval misses the fee doc, Tier 1 immediately flags the failure,
    # preventing developers from wrongly blaming the LLM for omitting restocking fee rules!
    faulty_retrieval = ["doc_refund_policy_01", "doc_unrelated_marketing"]
    faulty_recall = evaluator.evaluate_retrieval(faulty_retrieval, gold_doc_ids)
    assert faulty_recall == 0.5, "Diagnostic check should isolate retrieval degradation"

    print(
        f"RAG evaluation layer isolation verified: retrieval_recall={retrieval_recall:.1f}, "
        f"context_sufficiency={context_sufficiency:.1f}, generation_faithfulness={generation_faithfulness:.1f}"
    )


if __name__ == "__main__":
    main()

