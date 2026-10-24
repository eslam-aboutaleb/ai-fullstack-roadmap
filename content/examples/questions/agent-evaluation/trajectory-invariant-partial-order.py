# /// script
# dependencies = []
# ///
"""
Trajectory Invariant Evaluation using Directed Acyclic Graph (DAG) Partial Orders.

Contrasts brittle exact-sequence matching with robust invariant-based validation:
1. Allows exploratory retrieval steps to execute in any flexible order or in parallel.
2. Strictly enforces prerequisite dependency orderings (e.g. auth < data < risk < mutation).
3. Rejects unsafe trajectories that attempt state mutations before validation gates.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple


class TrajectoryValidator:
    """Evaluates agent execution traces against DAG prerequisite invariants."""

    def __init__(self, prerequisite_rules: List[Tuple[str, str]]) -> None:
        """Rules are tuples of (prerequisite_step, dependent_step) meaning prerequisite must precede dependent."""
        self.rules = prerequisite_rules

    def validate_trace(self, trace: List[str]) -> Tuple[bool, List[str]]:
        """Returns (is_valid, list_of_violations)."""
        step_indices: Dict[str, List[int]] = {}
        for idx, step in enumerate(trace):
            step_indices.setdefault(step, []).append(idx)

        violations: List[str] = []

        for prereq, dependent in self.rules:
            # If dependent step occurred, prerequisite MUST have occurred earlier
            if dependent in step_indices:
                first_dep_idx = step_indices[dependent][0]
                if prereq not in step_indices:
                    violations.append(
                        f"Prerequisite step '{prereq}' was never executed before '{dependent}'"
                    )
                else:
                    first_prereq_idx = step_indices[prereq][0]
                    if first_prereq_idx > first_dep_idx:
                        violations.append(
                            f"Step '{prereq}' (idx {first_prereq_idx}) must precede '{dependent}' (idx {first_dep_idx})"
                        )

        return len(violations) == 0, violations


def main() -> None:
    # Define causal dependency DAG invariants:
    # 1. authenticate < fetch_user_data
    # 2. fetch_user_data < risk_assessment
    # 3. fetch_market_rates < risk_assessment
    # 4. risk_assessment < execute_financial_mutation
    # Note: fetch_user_data and fetch_market_rates have NO dependency between each other (flexible partial order).
    prerequisites = [
        ("authenticate", "fetch_user_data"),
        ("fetch_user_data", "risk_assessment"),
        ("fetch_market_rates", "risk_assessment"),
        ("risk_assessment", "execute_financial_mutation"),
    ]

    validator = TrajectoryValidator(prerequisites)

    # --- Scenario 1: Flexible Valid Order (fetch_market_rates called BEFORE fetch_user_data) ---
    valid_flexible_trace = [
        "authenticate",
        "fetch_market_rates",  # valid alternative ordering
        "fetch_user_data",
        "risk_assessment",
        "execute_financial_mutation",
    ]
    valid_1, errors_1 = validator.validate_trace(valid_flexible_trace)
    assert valid_1 is True, f"Valid trace rejected: {errors_1}"
    flexible_valid = True

    # --- Scenario 2: Unsafe Re-ordering (Mutation executed BEFORE risk assessment) ---
    unsafe_reordering_trace = [
        "authenticate",
        "fetch_user_data",
        "fetch_market_rates",
        "execute_financial_mutation",  # VIOLATION: jumped the gun before risk check
        "risk_assessment",
    ]
    valid_2, errors_2 = validator.validate_trace(unsafe_reordering_trace)
    assert valid_2 is False, "Unsafe trace should have been rejected"
    assert any("must precede 'execute_financial_mutation'" in err for err in errors_2)
    unsafe_reordering_rejected = True

    # --- Scenario 3: Missing Prerequisite (No authentication) ---
    missing_prereq_trace = [
        "fetch_user_data",
        "fetch_market_rates",
        "risk_assessment",
        "execute_financial_mutation",
    ]
    valid_3, errors_3 = validator.validate_trace(missing_prereq_trace)
    assert valid_3 is False, "Missing prerequisite trace should have been rejected"
    assert any("never executed" in err for err in errors_3)
    missing_prerequisite_rejected = True

    print(
        f"Partial order trajectory verified: flexible_valid={flexible_valid}, "
        f"unsafe_reordering_rejected={unsafe_reordering_rejected}, "
        f"missing_prerequisite_rejected={missing_prerequisite_rejected}"
    )


if __name__ == "__main__":
    main()

