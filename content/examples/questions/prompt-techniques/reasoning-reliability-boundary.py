"""Reliability boundary: Free-form chain-of-thought vs structured deterministic decomposition.

Demonstrates why unconstrained intermediate reasoning can degrade application reliability:
1. Persuasive confabulation: intermediate reasoning generates fluent rationalizations that
   misapply policy rules across entities while projecting artificial certainty.
2. Latency and token bloat: unconstrained CoT inflates token consumption and p99 latency.
3. Failure isolation: free-form reasoning obscures semantic failures, whereas typed
   decomposition isolates extraction from deterministic policy validation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class CustomerTier(str, Enum):
    CONSUMER = "consumer"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass(frozen=True)
class PolicyRule:
    rule_id: str
    target_tier: CustomerTier
    max_claim_amount: float
    requires_manager_override: bool


# Authoritative policy matrix
POLICY_RULES = {
    "POL-CONS-01": PolicyRule("POL-CONS-01", CustomerTier.CONSUMER, 100.0, False),
    "POL-PRO-02": PolicyRule("POL-PRO-02", CustomerTier.PRO, 500.0, False),
    "POL-ENT-03": PolicyRule("POL-ENT-03", CustomerTier.ENTERPRISE, 5000.0, True),
}


@dataclass(frozen=True)
class ClaimRequest:
    claim_id: str
    user_tier: CustomerTier
    requested_amount: float
    description: str


@dataclass(frozen=True)
class FreeFormCoTResponse:
    reasoning_tokens: int
    reasoning_text: str
    approved: bool
    confidence_statement: str


def simulate_free_form_cot(request: ClaimRequest) -> FreeFormCoTResponse:
    """Simulates an LLM generating unconstrained intermediate reasoning.

    Pathology: The model generates fluent, convincing steps, but in step 3 hallucinates
    that 'consumer tier qualifies for enterprise goodwill exception under POL-ENT-03'.
    """
    if request.user_tier == CustomerTier.CONSUMER and request.requested_amount > 100.0:
        # Confabulated reasoning: sounds rigorous but inverts policy boundary
        reasoning = (
            "Step 1: Inspect customer request for claim amount $350.00.\n"
            "Step 2: Customer is currently Consumer tier, standard limit is $100.00.\n"
            "Step 3: However, under Section 4 goodwill guidelines, Enterprise policy POL-ENT-03 "
            "can be provisionally applied to high-satisfaction consumer accounts.\n"
            "Step 4: Amount $350.00 is below the $5000.00 limit, so manager override is waived.\n"
            "Conclusion: Claim is approved."
        )
        return FreeFormCoTResponse(
            reasoning_tokens=185,
            reasoning_text=reasoning,
            approved=True,  # BUG: Falsely approved due to confabulated reasoning!
            confidence_statement="High confidence based on detailed multi-step policy evaluation.",
        )
    return FreeFormCoTResponse(
        reasoning_tokens=50,
        reasoning_text="Standard claim within limits.",
        approved=True,
        confidence_statement="Standard approval.",
    )


@dataclass(frozen=True)
class StructuredExtraction:
    tier: CustomerTier
    amount: float
    applicable_rule_id: str


def execute_deterministic_decomposition(
    request: ClaimRequest,
) -> Tuple[bool, str, Dict[str, Any]]:
    """Production architecture: separates structured extraction from authoritative policy code."""
    # Step 1: Deterministic extraction / binding (can be schema-constrained LLM or parser)
    if request.user_tier == CustomerTier.CONSUMER:
        rule_id = "POL-CONS-01"
    elif request.user_tier == CustomerTier.PRO:
        rule_id = "POL-PRO-02"
    else:
        rule_id = "POL-ENT-03"

    extraction = StructuredExtraction(
        tier=request.user_tier,
        amount=request.requested_amount,
        applicable_rule_id=rule_id,
    )

    # Step 2: Authoritative code evaluation (impossible to hallucinate policy boundaries)
    rule = POLICY_RULES.get(extraction.applicable_rule_id)
    if not rule:
        return False, "Unknown policy rule", {"extraction": extraction.__dict__}

    if extraction.amount > rule.max_claim_amount:
        return (
            False,
            f"Exceeds max claim limit of ${rule.max_claim_amount:.2f} for tier {rule.target_tier.value}",
            {"rule_id": rule.rule_id, "limit": rule.max_claim_amount},
        )

    return True, "Approved within policy limits", {"rule_id": rule.rule_id}


def run_test_suite() -> None:
    # Test case: Consumer user requesting $350 (exceeds $100 consumer limit)
    claim = ClaimRequest(
        claim_id="CLM-9821",
        user_tier=CustomerTier.CONSUMER,
        requested_amount=350.0,
        description="Damaged peripheral replacement",
    )

    # 1. Evaluate Free-form CoT:
    cot_result = simulate_free_form_cot(claim)

    # Free-form CoT generates persuasive reasoning, but results in a false positive:
    assert cot_result.approved is True, "CoT falsely approved the claim"
    assert "Enterprise policy POL-ENT-03" in cot_result.reasoning_text
    assert cot_result.reasoning_tokens > 100

    # 2. Evaluate Deterministic Decomposition:
    approved, reason, metadata = execute_deterministic_decomposition(claim)

    # Deterministic pipeline catches the breach authoritatively:
    assert approved is False
    assert "Exceeds max claim limit of $100.00" in reason
    assert metadata["rule_id"] == "POL-CONS-01"

    # 3. Valid claim test: Consumer requesting $75 (within $100 limit)
    valid_claim = ClaimRequest(
        claim_id="CLM-9822",
        user_tier=CustomerTier.CONSUMER,
        requested_amount=75.0,
        description="Standard cable replacement",
    )
    valid_approved, valid_reason, valid_meta = execute_deterministic_decomposition(valid_claim)
    assert valid_approved is True
    assert valid_meta["rule_id"] == "POL-CONS-01"

    print("All intermediate reasoning reliability assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
