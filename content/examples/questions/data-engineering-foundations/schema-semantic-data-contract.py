"""Semantic data contract vs structural type compatibility verification harness.

Demonstrates why structural schema validation (e.g. JSON schema, Avro, Protobuf) alone is insufficient:
1. The structural compatibility illusion: changing a monetary field's units from dollars ($100.50)
   to integer cents (10050) preserves numeric type parsing, but silently breaks business thresholds.
2. Semantic contract enforcement: contracts must explicitly declare units, allowed ranges,
   nullability semantics, and business invariants alongside physical primitive types.
3. Automated drift rejection: alerts or blocks pipeline processing when semantic contracts are breached,
   preventing silent data corruption in downstream machine learning or financial reporting.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class SemanticDataContract:
    contract_version: str
    expected_unit: str  # e.g., "USD_DOLLARS" or "USD_CENTS"
    min_value: float
    max_value: float


class ContractViolationError(ValueError):
    """Raised when data violates semantic contract invariants."""
    pass


def naive_structural_check(record: Dict[str, Any]) -> bool:
    """Anti-pattern: checks only that the field exists and is numeric."""
    amount = record.get("amount")
    return isinstance(amount, (int, float)) and amount >= 0


def validate_semantic_contract(
    record: Dict[str, Any], contract: SemanticDataContract
) -> Tuple[bool, Optional[str]]:
    """Production pattern: validates semantic unit, range, and version compatibility."""
    if record.get("contract_version") != contract.contract_version:
        return False, f"Contract version mismatch: expected {contract.contract_version}"

    if record.get("unit") != contract.expected_unit:
        return False, f"Unit violation: expected {contract.expected_unit}, got {record.get('unit')}"

    amount = record.get("amount")
    if not isinstance(amount, (int, float)):
        return False, "Amount must be numeric"

    if amount < contract.min_value or amount > contract.max_value:
        return False, f"Value {amount} exceeds bounded semantic range [{contract.min_value}, {contract.max_value}]"

    return True, None


def run_test_suite() -> None:
    # Contract v1: amounts are in USD_DOLLARS, typical range [1.0, 5000.0]
    contract_v1 = SemanticDataContract(
        contract_version="v1.0",
        expected_unit="USD_DOLLARS",
        min_value=0.01,
        max_value=10000.00,
    )

    # Valid transaction in dollars ($45.00)
    valid_record = {
        "txn_id": "TXN-001",
        "contract_version": "v1.0",
        "unit": "USD_DOLLARS",
        "amount": 45.00,
    }

    # Upstream breaking change: Producer switched to integer cents without bumping version
    # amount = 4500 cents ($45.00), but labeled or omitted as dollars
    breaking_record_cents = {
        "txn_id": "TXN-002",
        "contract_version": "v1.0",
        "unit": "USD_CENTS",  # Semantic shift!
        "amount": 4500,
    }

    # Record where unit header is completely missing and value shifted to cents (silent bug):
    silent_drift_record = {
        "txn_id": "TXN-003",
        "contract_version": "v1.0",
        "amount": 45000.0,  # 450.00 dollars represented as 45000 cents, exceeding $10,000 threshold
    }

    # 1. Demonstrate naive structural validation flaw:
    assert naive_structural_check(valid_record) is True
    # BUG: Naive validator passes the cents record because 4500 is a valid number:
    assert naive_structural_check(breaking_record_cents) is True
    assert naive_structural_check(silent_drift_record) is True

    # Downstream threshold logic: Flag transactions over $500 for fraud review
    # With cents, a routine $45 transaction (4500 cents) is falsely flagged as $4,500!
    is_fraud_flagged_naive = breaking_record_cents["amount"] > 500.0
    assert is_fraud_flagged_naive is True, "False fraud positive triggered by semantic unit shift!"

    # 2. Demonstrate robust semantic contract validation:
    is_valid_1, err_1 = validate_semantic_contract(valid_record, contract_v1)
    assert is_valid_1 is True
    assert err_1 is None

    # Semantic contract catches the unit violation:
    is_valid_2, err_2 = validate_semantic_contract(breaking_record_cents, contract_v1)
    assert is_valid_2 is False
    assert "Unit violation: expected USD_DOLLARS, got USD_CENTS" in str(err_2)

    # Semantic contract catches range violation on unlabelled cent value:
    is_valid_3, err_3 = validate_semantic_contract(silent_drift_record, contract_v1)
    assert is_valid_3 is False
    assert "exceeds bounded semantic range" in str(err_3) or "Unit violation" in str(err_3)

    print("All schema semantic contract assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
