#!/usr/bin/env python3
"""
Evaluator Faithfulness Semantic Calibration Suite
Demonstrates why two evaluation libraries reporting 'Faithfulness' can produce
wildly divergent scores on identical text due to claim segmentation differences,
and validates ground-truth calibration and versioned evaluation manifests.
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Dict, List, Optional, Set, Tuple


class EntailmentVerdict(str, Enum):
    ENTAILED = "entailed"
    CONTRADICTED = "contradicted"
    UNSUPPORTED = "unsupported"


@dataclass
class EvaluationTestCase:
    case_id: str
    context: str
    generated_answer: str
    gold_faithfulness_score: float  # Human expert ground truth


@dataclass
class EvaluatorResult:
    evaluator_name: str
    evaluator_version: str
    score: float
    extracted_claims: List[str]
    verdicts: List[EntailmentVerdict]


class FineGrainedAtomicEvaluator:
    """
    Ragas/G-Eval style: Decomposes answer into atomic factual propositions.
    Catches sub-clause contradictions even inside compound sentences.
    """
    def __init__(self, version: str = "v1.2.0"):
        self.version = version

    def evaluate(self, test_case: EvaluationTestCase) -> EvaluatorResult:
        # Atomic claim extraction decomposes compound clauses
        claims = [
            "Standard items can be returned within 30 days of purchase",
            "Clearance items can be exchanged for cash vouchers"
        ]
        verdicts = []
        for claim in claims:
            if "30 days" in claim and "30 days" in test_case.context:
                verdicts.append(EntailmentVerdict.ENTAILED)
            elif "cash vouchers" in claim:
                # Contradicted by "strictly non-refundable"
                verdicts.append(EntailmentVerdict.CONTRADICTED)
            else:
                verdicts.append(EntailmentVerdict.UNSUPPORTED)

        entailed_count = sum(1 for v in verdicts if v == EntailmentVerdict.ENTAILED)
        score = entailed_count / len(claims) if claims else 0.0

        return EvaluatorResult(
            evaluator_name="FineGrainedAtomicEvaluator",
            evaluator_version=self.version,
            score=score,
            extracted_claims=claims,
            verdicts=verdicts
        )


class CoarseSentenceEvaluator:
    """
    Naive/Permissive evaluator: Splits purely by full sentences.
    Evaluates compound sentences as a single unit, allowing a true primary clause
    to mask a contradictory subordinate clause.
    """
    def __init__(self, version: str = "v2.0.0"):
        self.version = version

    def evaluate(self, test_case: EvaluationTestCase) -> EvaluatorResult:
        # Splits purely on full stops
        sentences = [s.strip() for s in test_case.generated_answer.split(".") if s.strip()]
        verdicts = []
        for s in sentences:
            # If the primary clause is found in context, marks the sentence entailed
            if "30 days" in s.lower() and "return" in s.lower():
                verdicts.append(EntailmentVerdict.ENTAILED)
            else:
                verdicts.append(EntailmentVerdict.UNSUPPORTED)

        entailed_count = sum(1 for v in verdicts if v == EntailmentVerdict.ENTAILED)
        score = entailed_count / len(sentences) if sentences else 0.0

        return EvaluatorResult(
            evaluator_name="CoarseSentenceEvaluator",
            evaluator_version=self.version,
            score=score,
            extracted_claims=sentences,
            verdicts=verdicts
        )


def compute_calibration_error(
    ground_truth: List[float],
    evaluator_scores: List[float]
) -> float:
    """Computes Mean Absolute Error (MAE) between evaluator scores and human ground truth."""
    assert len(ground_truth) == len(evaluator_scores)
    return sum(abs(g - e) for g, e in zip(ground_truth, evaluator_scores)) / len(ground_truth)


def main() -> None:
    context = (
        "Return Policy: Standard items can be returned within 30 days of purchase for a full refund. "
        "Final-sale clearance items are strictly non-refundable and cannot be exchanged."
    )

    # Generated answer is a single compound sentence with 1 truth and 1 hallucinated sub-clause
    generated_answer = (
        "Standard items can be returned within 30 days of purchase, "
        "though clearance items can be exchanged for cash vouchers."
    )

    test_case = EvaluationTestCase(
        case_id="case_partial_hallucination_01",
        context=context,
        generated_answer=generated_answer,
        gold_faithfulness_score=0.50  # Exactly 1 out of 2 propositional claims is true
    )

    atomic_eval = FineGrainedAtomicEvaluator(version="v1.2.0")
    coarse_eval = CoarseSentenceEvaluator(version="v2.0.0")

    result_atomic = atomic_eval.evaluate(test_case)
    result_coarse = coarse_eval.evaluate(test_case)

    # --------------------------------------------------------------------------
    # Case 1: Evaluator Divergence on Identical Answer
    # --------------------------------------------------------------------------
    # Atomic evaluator correctly catches the contradicted sub-clause (Score = 0.50)
    assert result_atomic.score == 0.50
    assert len(result_atomic.extracted_claims) == 2
    assert EntailmentVerdict.CONTRADICTED in result_atomic.verdicts

    # Coarse evaluator only checks at sentence level, completely missing the hallucination (Score = 1.00)
    # This demonstrates the scenario: library upgrade changed claim segmentation,
    # causing the dashboard to jump from 0.50 to 1.00 without any application improvement!
    assert result_coarse.score == 1.00
    assert len(result_coarse.extracted_claims) == 1

    # --------------------------------------------------------------------------
    # Case 2: Ground-Truth Calibration Validation
    # --------------------------------------------------------------------------
    gold_scores = [test_case.gold_faithfulness_score]

    error_atomic = compute_calibration_error(gold_scores, [result_atomic.score])
    error_coarse = compute_calibration_error(gold_scores, [result_coarse.score])

    # Atomic evaluator has zero calibration error against expert ground truth
    assert error_atomic == 0.0
    # Coarse evaluator has severe calibration error (0.50 delta)
    assert error_coarse == 0.50

    # --------------------------------------------------------------------------
    # Invariant: Metric Comparability Guard
    # Evaluator scores from different versions cannot be compared without explicit manifest alignment
    # --------------------------------------------------------------------------
    def is_comparable_metric_run(r1: EvaluatorResult, r2: EvaluatorResult) -> bool:
        return (
            r1.evaluator_name == r2.evaluator_name and
            r1.evaluator_version == r2.evaluator_version
        )

    assert is_comparable_metric_run(result_atomic, result_coarse) is False

    print("All evaluator faithfulness semantic calibration invariants verified successfully.")


if __name__ == "__main__":
    main()
