"""Prompt contract and behavioral invariant evaluation suite.

Demonstrates evaluating prompt candidates against semantic behavioral contracts,
abstention rules, and factual containment rather than brittle lexical string matching.
Lexical string equality or n-gram overlap (BLEU/ROUGE) creates high false positives
(rewarding memorized benchmark phrasing with factual errors) and high false negatives
(penalizing valid paraphrased answers).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class ContractStatus(str, Enum):
    SATISFIED = "satisfied"
    FACTUAL_VIOLATION = "factual_violation"
    ABSTENTION_VIOLATION = "abstention_violation"
    SCHEMA_VIOLATION = "schema_violation"
    FORBIDDEN_LEAKAGE = "forbidden_leakage"


@dataclass(frozen=True)
class EvaluationTestCase:
    case_id: str
    query: str
    context: str
    expected_status: str  # "ANSWER" or "ABSTAIN"
    required_entities: Set[str]
    forbidden_tokens: Set[str]
    gold_reference_text: str


@dataclass(frozen=True)
class CandidateOutput:
    raw_text: str
    structured_payload: Optional[Dict[str, Any]] = None


def lexical_exact_match(candidate: str, reference: str) -> float:
    """Brittle baseline: checks normalized word overlap ratio against reference string."""
    cand_words = set(re.findall(r"\w+", candidate.lower()))
    ref_words = set(re.findall(r"\w+", reference.lower()))
    if not ref_words:
        return 0.0
    overlap = cand_words.intersection(ref_words)
    return len(overlap) / len(ref_words)


def evaluate_behavioral_contract(
    candidate: CandidateOutput, test_case: EvaluationTestCase
) -> ContractStatus:
    """Evaluates candidate response against declarative invariant rules."""
    text = candidate.raw_text

    # 1. Check forbidden tokens / system prompt leakages
    text_lower = text.lower()
    for forbidden in test_case.forbidden_tokens:
        if forbidden.lower() in text_lower:
            return ContractStatus.FORBIDDEN_LEAKAGE

    # 2. Check schema / structured contract if required
    payload = candidate.structured_payload
    if payload is not None:
        required_keys = {"status", "claims"}
        if not required_keys.issubset(payload.keys()):
            return ContractStatus.SCHEMA_VIOLATION

        status = payload.get("status")
        if test_case.expected_status == "ABSTAIN":
            if status != "ABSTAIN":
                return ContractStatus.ABSTENTION_VIOLATION
            return ContractStatus.SATISFIED
    else:
        # Fallback text-based abstention detection
        abstention_patterns = [
            "insufficient evidence",
            "cannot be determined",
            "not mentioned in context",
            "i do not have enough information",
        ]
        is_abstaining = any(p in text_lower for p in abstention_patterns)
        if test_case.expected_status == "ABSTAIN":
            if not is_abstaining:
                return ContractStatus.ABSTENTION_VIOLATION
            return ContractStatus.SATISFIED
        elif is_abstaining and test_case.expected_status == "ANSWER":
            return ContractStatus.FACTUAL_VIOLATION

    # 3. Factual containment: verify all required entity facts exist in output
    for entity in test_case.required_entities:
        if entity.lower() not in text_lower:
            return ContractStatus.FACTUAL_VIOLATION

    # 4. Context grounding: verify claimed entities are supported by source context
    context_lower = test_case.context.lower()
    # If the output claims a specific numerical value not present in context:
    cand_numbers = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", text_lower))
    ctx_numbers = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", context_lower))
    unsupported_numbers = cand_numbers - ctx_numbers
    if unsupported_numbers:
        return ContractStatus.FACTUAL_VIOLATION

    return ContractStatus.SATISFIED


def run_test_suite() -> None:
    test_case_answer = EvaluationTestCase(
        case_id="case-401-sla",
        query="What is the guaranteed uptime SLA and reimbursement credit?",
        context="The Enterprise SLA guarantees 99.95% monthly uptime. If downtime exceeds this threshold, customers receive a 15% billing credit.",
        expected_status="ANSWER",
        required_entities={"99.95%", "15%"},
        forbidden_tokens={"System Prompt:", "Developer instructions:"},
        gold_reference_text="The Enterprise SLA guarantees 99.95% monthly uptime with a 15% billing credit for outages.",
    )

    test_case_abstain = EvaluationTestCase(
        case_id="case-402-unsupported",
        query="What is the refund policy for annual enterprise tier accounts?",
        context="The documentation covers monthly subscriptions and maintenance downtime windows only.",
        expected_status="ABSTAIN",
        required_entities=set(),
        forbidden_tokens={"System Prompt:", "Internal policy:"},
        gold_reference_text="Insufficient evidence: The provided documentation does not detail annual refund policies.",
    )

    # Candidate 1: Verbatim repetition of gold reference text, but with subtle corrupted numbers (Hallucination)
    cand_memorized_corrupt = CandidateOutput(
        raw_text="The Enterprise SLA guarantees 99.99% monthly uptime with a 25% billing credit for outages.",
        structured_payload={"status": "ANSWER", "claims": ["99.99% uptime", "25% credit"]},
    )

    # Candidate 2: Completely paraphrased wording, 100% correct factual containment
    cand_paraphrased_correct = CandidateOutput(
        raw_text="Under our enterprise agreement, availability is backed up to 99.95%, and impacted tenants receive a 15% discount credit.",
        structured_payload={"status": "ANSWER", "claims": ["99.95% uptime", "15% discount"]},
    )

    # Candidate 3: Correct abstention on missing evidence
    cand_abstention_valid = CandidateOutput(
        raw_text="Insufficient evidence: The provided documentation does not mention annual refund terms.",
        structured_payload={"status": "ABSTAIN", "claims": []},
    )

    # Candidate 4: Hallucinated answer on missing evidence (violates abstention)
    cand_abstention_hallucinated = CandidateOutput(
        raw_text="Annual subscriptions can be refunded within 30 days of purchase upon written notice.",
        structured_payload={"status": "ANSWER", "claims": ["30 days refund"]},
    )

    # 1. Demonstrate brittle lexical evaluation pathology:
    lexical_score_corrupt = lexical_exact_match(
        cand_memorized_corrupt.raw_text, test_case_answer.gold_reference_text
    )
    lexical_score_paraphrased = lexical_exact_match(
        cand_paraphrased_correct.raw_text, test_case_answer.gold_reference_text
    )

    # Lexical overlap gives high score to corrupted numbers due to phrasing repetition:
    assert lexical_score_corrupt >= 0.70, f"Expected high lexical overlap, got {lexical_score_corrupt}"
    # Lexical overlap penalizes fresh paraphrasing:
    assert lexical_score_paraphrased < 0.50, f"Expected lower lexical overlap, got {lexical_score_paraphrased}"

    # 2. Demonstrate robust behavioral contract evaluation:
    eval_result_corrupt = evaluate_behavioral_contract(cand_memorized_corrupt, test_case_answer)
    eval_result_paraphrased = evaluate_behavioral_contract(cand_paraphrased_correct, test_case_answer)
    eval_result_abstain_valid = evaluate_behavioral_contract(cand_abstention_valid, test_case_abstain)
    eval_result_abstain_hallucinated = evaluate_behavioral_contract(cand_abstention_hallucinated, test_case_abstain)

    # Behavioral contract correctly rejects the hallucinated number despite lexical similarity:
    assert eval_result_corrupt == ContractStatus.FACTUAL_VIOLATION
    # Behavioral contract correctly accepts paraphrased truth:
    assert eval_result_paraphrased == ContractStatus.SATISFIED
    # Behavioral contract validates honest abstention:
    assert eval_result_abstain_valid == ContractStatus.SATISFIED
    # Behavioral contract catches hallucination on missing context:
    assert eval_result_abstain_hallucinated == ContractStatus.ABSTENTION_VIOLATION

    print("All prompt contract evaluation assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
