"""
temporal-policy-applicability-matrix.py

Production-grade Temporal Policy Applicability and Targeted Clarification Suite.
Demonstrates:
1. Temporal Validity Intervals: Resolving conflicting policies by matching transaction dates
   against effective_from and effective_to intervals rather than naive vector similarity scores.
2. Targeted Clarification vs Guessing:
   When multiple conflicting policy versions exist and the critical temporal anchor
   (transaction_date) is missing, the system halts and emits a structured clarification request
   rather than hallucinating an answer.
3. Specificity / Exception Precedence:
   Evaluating specific promotional/category exceptions over general institutional rules.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class PolicyClause:
    policy_id: str
    title: str
    effective_from: date
    effective_to: Optional[date]
    product_category: Optional[str]
    rule_summary: str
    priority: int  # Higher priority indicates specific exception over general rule

    def is_temporally_valid(self, query_date: date) -> bool:
        if query_date < self.effective_from:
            return False
        if self.effective_to and query_date > self.effective_to:
            return False
        return True


class PolicyApplicabilityEngine:
    def __init__(self):
        self.knowledge_base: List[PolicyClause] = [
            PolicyClause(
                policy_id="POL-2024-GEN",
                title="2024 Standard Return Policy",
                effective_from=date(2024, 1, 1),
                effective_to=date(2024, 12, 31),
                product_category=None,
                rule_summary="Full 100% refund permitted within 30 days. No restocking fee.",
                priority=1
            ),
            PolicyClause(
                policy_id="POL-2024-HOLIDAY",
                title="2024 Holiday Season Return Exception",
                effective_from=date(2024, 11, 15),
                effective_to=date(2024, 12, 31),
                product_category="electronics",
                rule_summary="Holiday exception: Extended return window until Jan 31, 2025 with $0 fee.",
                priority=10
            ),
            PolicyClause(
                policy_id="POL-2025-CURRENT",
                title="2025-2026 Master Return Policy",
                effective_from=date(2025, 1, 1),
                effective_to=None,
                product_category=None,
                rule_summary="Standard returns permitted within 30 days with mandatory $15 restocking fee.",
                priority=1
            ),
        ]

    def resolve_applicable_policy(
        self,
        transaction_date: Optional[date],
        product_category: Optional[str]
    ) -> Dict[str, Any]:
        """
        Determines the single authoritative policy applicable to the user's specific context.
        If the transaction date is missing, abstains and requests clarification.
        """
        # Step 1: Detect missing decision-critical temporal anchor
        if transaction_date is None:
            return {
                "decision": "CLARIFICATION_REQUIRED",
                "missing_slot": "transaction_date",
                "reason": (
                    "Multiple conflicting return policies exist (2024 $0 fee vs 2025 $15 fee). "
                    "The exact purchase date is required to determine legal and commercial applicability."
                ),
                "applicable_policy": None
            }

        # Step 2: Filter clauses temporally valid for the transaction date
        valid_clauses = [
            p for p in self.knowledge_base if p.is_temporally_valid(transaction_date)
        ]

        if not valid_clauses:
            return {
                "decision": "NO_APPLICABLE_POLICY",
                "reason": f"No active policy found for date {transaction_date.isoformat()}",
                "applicable_policy": None
            }

        # Step 3: Filter by product category specificity
        matching_clauses = []
        for c in valid_clauses:
            if c.product_category is None:
                # General clause applies to all categories
                matching_clauses.append(c)
            elif product_category and c.product_category.lower() == product_category.lower():
                # Specific category match
                matching_clauses.append(c)

        # Step 4: Resolve by priority (specific exception overrides general rule)
        best_clause = max(matching_clauses, key=lambda p: p.priority)

        return {
            "decision": "POLICY_RESOLVED",
            "applicable_policy": best_clause.policy_id,
            "rule_summary": best_clause.rule_summary,
            "effective_interval": f"{best_clause.effective_from} to {best_clause.effective_to or 'Indefinite'}"
        }


def main() -> None:
    print("=== Testing Temporal Policy Applicability & Targeted Clarification ===")
    engine = PolicyApplicabilityEngine()

    # Scenario 1: Missing Transaction Date -> Must Abstain & Request Clarification
    result_missing_date = engine.resolve_applicable_policy(
        transaction_date=None,
        product_category="electronics"
    )
    print("\nScenario 1 (No Date Provided):", result_missing_date)
    assert result_missing_date["decision"] == "CLARIFICATION_REQUIRED"
    assert result_missing_date["missing_slot"] == "transaction_date"
    assert result_missing_date["applicable_policy"] is None

    # Scenario 2: 2024 Holiday Exception Purchase
    # Purchase on Dec 5, 2024 for electronics -> POL-2024-HOLIDAY overrides general 2024 rule
    result_holiday = engine.resolve_applicable_policy(
        transaction_date=date(2024, 12, 5),
        product_category="electronics"
    )
    print("\nScenario 2 (2024 Holiday Purchase):", result_holiday)
    assert result_holiday["decision"] == "POLICY_RESOLVED"
    assert result_holiday["applicable_policy"] == "POL-2024-HOLIDAY"
    assert "Extended return window" in result_holiday["rule_summary"]

    # Scenario 3: 2025 Current Policy Purchase
    # Purchase on June 20, 2025 -> POL-2025-CURRENT applies with $15 restocking fee
    result_2025 = engine.resolve_applicable_policy(
        transaction_date=date(2025, 6, 20),
        product_category="clothing"
    )
    print("\nScenario 3 (2025 Purchase):", result_2025)
    assert result_2025["decision"] == "POLICY_RESOLVED"
    assert result_2025["applicable_policy"] == "POL-2025-CURRENT"
    assert "$15 restocking fee" in result_2025["rule_summary"]

    print("\nAll temporal policy applicability and clarification invariants verified successfully.")


if __name__ == "__main__":
    main()
