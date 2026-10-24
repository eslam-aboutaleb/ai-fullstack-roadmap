# /// script
# dependencies = []
# ///
"""
Evaluation Matrix for Refusal, Clarification, and Answering.

Disentangles four distinct query handling behaviors:
1. ANSWER: Query is safe, specific, and grounded in available documentation.
2. CLARIFY: Query is safe but ambiguous or missing mandatory parameters.
3. REFUSE: Query violates safety policies or attempts unauthorized privilege escalation.
4. INSUFFICIENT_EVIDENCE: Query is safe and specific, but documentation lacks answer.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Tuple


class AgentDecision(str, Enum):
    ANSWER = "ANSWER"
    CLARIFY = "CLARIFY"
    REFUSE = "REFUSE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class TriageEvaluator:
    """Evaluates an agent's triage router across safety, completeness, and evidence boundaries."""

    @staticmethod
    def classify_request(
        is_policy_compliant: bool,
        is_query_complete: bool,
        has_grounded_evidence: bool,
    ) -> AgentDecision:
        # Non-negotiable security boundary
        if not is_policy_compliant:
            return AgentDecision.REFUSE

        # Ambiguous or underspecified queries require user clarification before execution
        if not is_query_complete:
            return AgentDecision.CLARIFY

        # Specific queries with missing documents must abstain rather than hallucinate
        if not has_grounded_evidence:
            return AgentDecision.INSUFFICIENT_EVIDENCE

        # Clear, authorized, and supported query
        return AgentDecision.ANSWER


def main() -> None:
    evaluator = TriageEvaluator()

    # Benchmark test suite evaluating each quadrant of the decision matrix
    test_cases: List[Dict[str, Any]] = [
        {
            "desc": "Specific grounded question",
            "compliant": True,
            "complete": True,
            "evidence": True,
            "expected": AgentDecision.ANSWER,
        },
        {
            "desc": "Ambiguous input ('cancel my order' without order ID)",
            "compliant": True,
            "complete": False,
            "evidence": True,
            "expected": AgentDecision.CLARIFY,
        },
        {
            "desc": "Malicious prompt injection bypass attempt",
            "compliant": False,
            "complete": True,
            "evidence": True,
            "expected": AgentDecision.REFUSE,
        },
        {
            "desc": "Safe specific query on unindexed topic",
            "compliant": True,
            "complete": True,
            "evidence": False,
            "expected": AgentDecision.INSUFFICIENT_EVIDENCE,
        },
    ]

    results: Dict[AgentDecision, Tuple[int, int]] = {d: [0, 0] for d in AgentDecision}

    for case in test_cases:
        decision = evaluator.classify_request(
            is_policy_compliant=case["compliant"],
            is_query_complete=case["complete"],
            has_grounded_evidence=case["evidence"],
        )
        expected = case["expected"]
        results[expected][1] += 1
        if decision == expected:
            results[expected][0] += 1

    answer_acc = results[AgentDecision.ANSWER][0] / results[AgentDecision.ANSWER][1]
    clarify_acc = results[AgentDecision.CLARIFY][0] / results[AgentDecision.CLARIFY][1]
    refuse_acc = results[AgentDecision.REFUSE][0] / results[AgentDecision.REFUSE][1]
    insufficient_acc = (
        results[AgentDecision.INSUFFICIENT_EVIDENCE][0]
        / results[AgentDecision.INSUFFICIENT_EVIDENCE][1]
    )

    assert answer_acc == 1.0
    assert clarify_acc == 1.0
    assert refuse_acc == 1.0
    assert insufficient_acc == 1.0

    print(
        f"Decision matrix verified: answer_accuracy={answer_acc:.1f}, "
        f"clarify_accuracy={clarify_acc:.1f}, refusal_accuracy={refuse_acc:.1f}, "
        f"insufficient_accuracy={insufficient_acc:.1f}"
    )


if __name__ == "__main__":
    main()
