#!/usr/bin/env python3
"""
Evaluation Failure Boundary Isolation Harness
Demonstrates why retrieval relevance, answer support (faithfulness), and abstention
represent decoupled failure boundaries, and proves that composite score averages
mask catastrophic safety and policy contradictions in RAG pipelines.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class SystemOutcome(str, Enum):
    ANSWERED = "answered"
    ABSTAINED = "abstained"


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    query: str
    gold_doc_ids: Set[str]  # Empty set indicates query is unanswerable
    expected_answer_summary: Optional[str] = None
    is_answerable: bool = True


@dataclass
class PipelinePrediction:
    case_id: str
    retrieved_doc_ids: List[str]
    outcome: SystemOutcome
    generated_answer: str
    cited_doc_ids: List[str]


@dataclass
class StageMetrics:
    case_id: str
    # Retrieval Boundary
    retrieval_hit: bool
    reciprocal_rank: float
    # Faithfulness / Support Boundary (Does the answer follow the cited evidence?)
    supported_claims: int
    contradicted_claims: int
    unsupported_claims: int
    faithfulness_score: float
    # Abstention Boundary
    correct_abstention: Optional[bool]  # None if query was answerable
    hallucination_on_unanswerable: bool
    # Blocker flags
    policy_contradiction_blocker: bool


class DecoupledRAGEvaluator:
    """
    Evaluates RAG systems across isolated failure boundaries rather than
    conflating them into a single misleading scalar score.
    """

    def __init__(self, ground_truth_corpus: Dict[str, str]):
        self.corpus = ground_truth_corpus

    def evaluate_case(
        self,
        case: EvaluationCase,
        pred: PipelinePrediction,
        contradiction_keywords: Optional[Dict[str, List[str]]] = None
    ) -> StageMetrics:
        # 1. Retrieval Boundary
        if case.is_answerable and case.gold_doc_ids:
            hit = any(doc_id in case.gold_doc_ids for doc_id in pred.retrieved_doc_ids)
            rr = 0.0
            for rank, doc_id in enumerate(pred.retrieved_doc_ids, start=1):
                if doc_id in case.gold_doc_ids:
                    rr = 1.0 / rank
                    break
        else:
            # Unanswerable query has no gold document to retrieve
            hit = len(pred.retrieved_doc_ids) == 0
            rr = 1.0 if hit else 0.0

        # 2. Abstention Boundary
        if not case.is_answerable:
            if pred.outcome == SystemOutcome.ABSTAINED:
                correct_abstention = True
                hallucinated_unanswerable = False
            else:
                correct_abstention = False
                hallucinated_unanswerable = True
        else:
            correct_abstention = None
            hallucinated_unanswerable = False

        # 3. Faithfulness & Policy Contradiction Boundary
        contradiction_detected = False
        supported = 0
        contradicted = 0
        unsupported = 0

        if pred.outcome == SystemOutcome.ANSWERED:
            # Check claims against retrieved documents
            # In a production suite this uses NLI cross-encoders or deterministic rules
            if contradiction_keywords:
                for rule_key, forbidden_phrases in contradiction_keywords.items():
                    for phrase in forbidden_phrases:
                        if phrase.lower() in pred.generated_answer.lower():
                            contradicted += 1
                            contradiction_detected = True

            if not contradiction_detected:
                # If no contradiction and cited docs overlap gold, mark as supported
                if case.is_answerable and any(d in case.gold_doc_ids for d in pred.cited_doc_ids):
                    supported += 1
                else:
                    unsupported += 1

            total_claims = supported + contradicted + unsupported
            faithfulness = (supported / total_claims) if total_claims > 0 else 0.0
        else:
            faithfulness = 1.0 if not case.is_answerable else 0.0

        return StageMetrics(
            case_id=case.case_id,
            retrieval_hit=hit,
            reciprocal_rank=rr,
            supported_claims=supported,
            contradicted_claims=contradicted,
            unsupported_claims=unsupported,
            faithfulness_score=faithfulness,
            correct_abstention=correct_abstention,
            hallucination_on_unanswerable=hallucinated_unanswerable,
            policy_contradiction_blocker=contradiction_detected
        )


def compute_naive_composite_score(metrics: StageMetrics) -> float:
    """
    Anti-Pattern: Averaging retrieval and answer scores masks critical contradictions.
    """
    return (metrics.reciprocal_rank + metrics.faithfulness_score) / 2.0


def main() -> None:
    corpus = {
        "doc-refund-001": "Refund Policy: Items returned within 30 days receive 100% refund. Final-sale clearance items are strictly non-refundable.",
        "doc-shipping-002": "Standard shipping takes 3-5 business days across the continental US.",
    }

    evaluator = DecoupledRAGEvaluator(corpus)

    # --------------------------------------------------------------------------
    # Case 1: The Classic Failure Boundary Trap
    # System retrieves the exact policy doc, but contradicts it by stating
    # final-sale items ARE refundable.
    # --------------------------------------------------------------------------
    case_1 = EvaluationCase(
        case_id="case-contradiction-01",
        query="Can I return a final-sale clearance item within 30 days?",
        gold_doc_ids={"doc-refund-001"},
        is_answerable=True
    )

    pred_1 = PipelinePrediction(
        case_id="case-contradiction-01",
        retrieved_doc_ids=["doc-refund-001"],
        outcome=SystemOutcome.ANSWERED,
        generated_answer="Yes, as long as it is within 30 days, final-sale clearance items are eligible for a full refund [doc-refund-001].",
        cited_doc_ids=["doc-refund-001"]
    )

    metrics_1 = evaluator.evaluate_case(
        case_1,
        pred_1,
        contradiction_keywords={"refund": ["eligible for a full refund", "final-sale clearance items are eligible"]}
    )

    # Verification: Retrieval succeeded (Hit=True, RR=1.0)
    assert metrics_1.retrieval_hit is True
    assert metrics_1.reciprocal_rank == 1.0
    # But Faithfulness failed completely (contradicted policy)
    assert metrics_1.contradicted_claims > 0
    assert metrics_1.faithfulness_score == 0.0
    assert metrics_1.policy_contradiction_blocker is True

    # Demonstrate the Anti-Pattern: A naive average gives 0.50, hiding the severe defect
    naive_score_1 = compute_naive_composite_score(metrics_1)
    assert naive_score_1 == 0.5

    # --------------------------------------------------------------------------
    # Case 2: Correct Abstention on Unanswerable Query
    # Query asks about international pet shipping; corpus has zero relevant policies.
    # System correctly abstains.
    # --------------------------------------------------------------------------
    case_2 = EvaluationCase(
        case_id="case-unanswerable-02",
        query="What are the quarantine rules for shipping parrots to Iceland?",
        gold_doc_ids=set(),
        is_answerable=False
    )

    pred_2 = PipelinePrediction(
        case_id="case-unanswerable-02",
        retrieved_doc_ids=[],
        outcome=SystemOutcome.ABSTAINED,
        generated_answer="I cannot answer this question as the provided documentation contains no policies regarding international livestock shipping.",
        cited_doc_ids=[]
    )

    metrics_2 = evaluator.evaluate_case(case_2, pred_2)
    assert metrics_2.correct_abstention is True
    assert metrics_2.hallucination_on_unanswerable is False
    assert metrics_2.policy_contradiction_blocker is False

    # --------------------------------------------------------------------------
    # Case 3: Hallucination on Unanswerable Query
    # System hallucinates a fictitious policy rather than abstaining.
    # --------------------------------------------------------------------------
    pred_3_hallucinated = PipelinePrediction(
        case_id="case-unanswerable-02",
        retrieved_doc_ids=["doc-shipping-002"],
        outcome=SystemOutcome.ANSWERED,
        generated_answer="Parrots must quarantine for 14 days before entry into Iceland.",
        cited_doc_ids=["doc-shipping-002"]
    )

    metrics_3 = evaluator.evaluate_case(case_2, pred_3_hallucinated)
    assert metrics_3.correct_abstention is False
    assert metrics_3.hallucination_on_unanswerable is True

    # --------------------------------------------------------------------------
    # Boundary Gating Decision: Independent Gates Prevent Promotion
    # --------------------------------------------------------------------------
    def passes_production_release_gate(metrics_list: List[StageMetrics]) -> Tuple[bool, List[str]]:
        reasons = []
        for m in metrics_list:
            if m.policy_contradiction_blocker:
                reasons.append(f"Hard Blocker on {m.case_id}: Policy contradiction detected.")
            if m.hallucination_on_unanswerable:
                reasons.append(f"Hard Blocker on {m.case_id}: Failed to abstain on unanswerable query.")
        return len(reasons) == 0, reasons

    passed, blockers = passes_production_release_gate([metrics_1, metrics_2])
    assert passed is False
    assert len(blockers) == 1
    assert "Policy contradiction detected" in blockers[0]

    # Verify that clean system passes the decoupled gate
    pred_1_fixed = PipelinePrediction(
        case_id="case-contradiction-01",
        retrieved_doc_ids=["doc-refund-001"],
        outcome=SystemOutcome.ANSWERED,
        generated_answer="No, final-sale clearance items are strictly non-refundable according to our policy [doc-refund-001].",
        cited_doc_ids=["doc-refund-001"]
    )
    metrics_1_fixed = evaluator.evaluate_case(case_1, pred_1_fixed)
    assert metrics_1_fixed.policy_contradiction_blocker is False
    assert metrics_1_fixed.faithfulness_score == 1.0

    clean_passed, clean_blockers = passes_production_release_gate([metrics_1_fixed, metrics_2])
    assert clean_passed is True
    assert len(clean_blockers) == 0

    print("All evaluation failure boundary isolation invariants verified successfully.")


if __name__ == "__main__":
    main()
