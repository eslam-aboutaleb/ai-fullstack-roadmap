#!/usr/bin/env python3
"""
Knowledge Adaptation Boundary Decision Harness
Demonstrates why fine-tuning/LoRA fails to solve dynamic, changing knowledge tasks,
and proves that retrieval-augmented generation (RAG) is the mathematically correct
and operationally sound architecture for volatile enterprise facts.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class AdaptationMechanism(str, Enum):
    PROMPT_ENGINEERING = "prompt_engineering"
    FINE_TUNING_LORA = "fine_tuning_lora"
    RETRIEVAL_AUGMENTED_GENERATION = "rag"


class DefectDomain(str, Enum):
    VOLATILE_FACTS = "volatile_facts"
    OUTPUT_STYLE_SYNTAX = "output_style_syntax"
    COMPLEX_REASONING_STEPS = "complex_reasoning_steps"
    MULTI_TENANT_ACCESS_CONTROL = "multi_tenant_access_control"


@dataclass
class PolicyDocument:
    doc_id: str
    effective_date: str
    refund_window_days: int
    text: str


@dataclass
class ModelResponse:
    mechanism: AdaptationMechanism
    stated_refund_days: int
    cited_source_id: Optional[str]
    is_current: bool


class KnowledgeAdaptationEvaluator:
    """
    Evaluates system behavior when company policies update dynamically.
    Contrasts parametric weight updates (LoRA/fine-tuning) against
    non-parametric context injection (RAG).
    """

    def __init__(self, historical_policy: PolicyDocument):
        # Parametric model is fine-tuned once on historical policy
        self.fine_tuned_weights_policy = historical_policy

    def predict_fine_tuned_model(self, active_policy: PolicyDocument) -> ModelResponse:
        """
        Simulates an LLM whose weights were fine-tuned on historical data.
        The model cannot see the new policy unless expensive retraining is executed.
        """
        # Model responds from internal parametric memory (historical)
        days = self.fine_tuned_weights_policy.refund_window_days
        return ModelResponse(
            mechanism=AdaptationMechanism.FINE_TUNING_LORA,
            stated_refund_days=days,
            cited_source_id=None,  # Fine-tuning cannot provide verifiable cryptographic citations
            is_current=(days == active_policy.refund_window_days)
        )

    def predict_rag_pipeline(
        self,
        active_policy: PolicyDocument,
        retrieved_document: Optional[PolicyDocument]
    ) -> ModelResponse:
        """
        Simulates a RAG pipeline where the model is grounded on retrieved context.
        """
        if not retrieved_document:
            # Fallback when retrieval fails
            return ModelResponse(
                mechanism=AdaptationMechanism.RETRIEVAL_AUGMENTED_GENERATION,
                stated_refund_days=0,
                cited_source_id=None,
                is_current=False
            )

        # Generator extracts answer directly from retrieved non-parametric context
        days = retrieved_document.refund_window_days
        return ModelResponse(
            mechanism=AdaptationMechanism.RETRIEVAL_AUGMENTED_GENERATION,
            stated_refund_days=days,
            cited_source_id=retrieved_document.doc_id,
            is_current=(days == active_policy.refund_window_days)
        )

    @staticmethod
    def select_appropriate_intervention(defect: DefectDomain) -> AdaptationMechanism:
        """
        Architecture Decision Matrix:
        Maps the operational defect to the appropriate engineering intervention.
        """
        if defect in (DefectDomain.VOLATILE_FACTS, DefectDomain.MULTI_TENANT_ACCESS_CONTROL):
            return AdaptationMechanism.RETRIEVAL_AUGMENTED_GENERATION
        elif defect == DefectDomain.OUTPUT_STYLE_SYNTAX:
            return AdaptationMechanism.FINE_TUNING_LORA
        elif defect == DefectDomain.COMPLEX_REASONING_STEPS:
            return AdaptationMechanism.PROMPT_ENGINEERING
        raise ValueError(f"Unknown defect domain: {defect}")


def main() -> None:
    # --------------------------------------------------------------------------
    # Scenario: Policy Update Lifecycle
    # Day 1: Refund window is 14 days.
    # Day 2: Executive order updates refund window to 30 days.
    # --------------------------------------------------------------------------
    policy_day_1 = PolicyDocument(
        doc_id="policy_refund_2026_01",
        effective_date="2026-01-01",
        refund_window_days=14,
        text="Customers may return items within 14 days of purchase."
    )

    policy_day_2 = PolicyDocument(
        doc_id="policy_refund_2026_02",
        effective_date="2026-01-02",
        refund_window_days=30,
        text="Updated policy: Customers may return items within 30 days of purchase."
    )

    evaluator = KnowledgeAdaptationEvaluator(historical_policy=policy_day_1)

    # --------------------------------------------------------------------------
    # Failure Mode: Fine-Tuning Fails on Changing Facts
    # --------------------------------------------------------------------------
    # On Day 2, user asks about current refund policy
    response_lora = evaluator.predict_fine_tuned_model(active_policy=policy_day_2)

    # The fine-tuned model answers from obsolete parametric weights (14 days instead of 30)
    assert response_lora.stated_refund_days == 14
    assert response_lora.is_current is False
    assert response_lora.cited_source_id is None  # Lacks source attribution

    # --------------------------------------------------------------------------
    # Success Mode: RAG Immediately Reflects Current Facts
    # --------------------------------------------------------------------------
    # When policy updates, RAG indexes the new document in the vector store immediately
    response_rag = evaluator.predict_rag_pipeline(
        active_policy=policy_day_2,
        retrieved_document=policy_day_2
    )

    # RAG immediately serves current facts with verified citation provenance
    assert response_rag.stated_refund_days == 30
    assert response_rag.is_current is True
    assert response_rag.cited_source_id == "policy_refund_2026_02"

    # --------------------------------------------------------------------------
    # Architectural Boundary Decision Invariants
    # --------------------------------------------------------------------------
    # Invariant 1: Volatile or updated factual requirements MUST select RAG
    rec_facts = evaluator.select_appropriate_intervention(DefectDomain.VOLATILE_FACTS)
    assert rec_facts == AdaptationMechanism.RETRIEVAL_AUGMENTED_GENERATION

    # Invariant 2: Multi-tenant permission isolation MUST select RAG (weights cannot filter tenant RLS)
    rec_tenancy = evaluator.select_appropriate_intervention(DefectDomain.MULTI_TENANT_ACCESS_CONTROL)
    assert rec_tenancy == AdaptationMechanism.RETRIEVAL_AUGMENTED_GENERATION

    # Invariant 3: Specialized output syntax (e.g., proprietary JSON format) selects Fine-Tuning
    rec_style = evaluator.select_appropriate_intervention(DefectDomain.OUTPUT_STYLE_SYNTAX)
    assert rec_style == AdaptationMechanism.FINE_TUNING_LORA

    # Invariant 4: Complex multi-step reasoning selects Prompt Engineering
    rec_reasoning = evaluator.select_appropriate_intervention(DefectDomain.COMPLEX_REASONING_STEPS)
    assert rec_reasoning == AdaptationMechanism.PROMPT_ENGINEERING

    print("All knowledge adaptation boundary decision invariants verified successfully.")


if __name__ == "__main__":
    main()
