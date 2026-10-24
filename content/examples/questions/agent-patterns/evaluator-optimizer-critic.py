"""Evaluator-Optimizer (Critic) Pattern with Objective Grounding vs Correlated Ensemble Failure.

Demonstrates:
1. Evaluator-Optimizer Loop:
   - Generator generates structured output (e.g., SQL query or policy decision).
   - Critic evaluates against objective rubric: deterministic schema validation and AST security checks first.
   - Structured diagnostic feedback: emits exact syntax / policy violations back to Generator.
   - Bounded revision loop: capped at max iterations (prevents infinite thrashing or semantic drift).
2. Parallel Ensemble vs Independent Grounding:
   - Demonstrates how 3 LLM agents in a voting ensemble all agree on a false conclusion when sharing
     an outdated or poisoned context document (correlated error).
   - Shows that a single deterministic schema/date validator detects the shared hallucination instantly.
"""

from dataclasses import dataclass, field
import json
import re
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CritiqueResult:
    passed: bool
    score: float
    violations: List[str]
    suggested_fixes: List[str]


class DeterministicSqlCritic:
    """Objective evaluator enforcing schema compliance, AST security checks, and bounding."""

    VALID_TABLES = {"users", "orders", "audit_logs"}
    FORBIDDEN_KEYWORDS = {"DROP", "TRUNCATE", "ALTER", "EXEC", "--", ";"}

    @classmethod
    def evaluate(cls, sql_query: str) -> CritiqueResult:
        violations = []
        suggested_fixes = []

        query_upper = sql_query.upper().strip()

        # Check 1: Forbidden destructive keywords / SQL injection markers
        for kw in cls.FORBIDDEN_KEYWORDS:
            if kw in query_upper:
                violations.append(f"Security hazard: Query contains prohibited token '{kw}'")
                suggested_fixes.append(f"Remove destructive command or comment syntax '{kw}'")

        # Check 2: Must be a SELECT query
        if not query_upper.startswith("SELECT"):
            violations.append("Query must be read-only SELECT statement")
            suggested_fixes.append("Change statement to begin with SELECT")

        # Check 3: Schema validation - must reference known tables
        table_match = re.findall(r"\bFROM\s+([a-zA-Z0-9_]+)", query_upper)
        if not table_match:
            violations.append("Missing FROM clause")
            suggested_fixes.append("Specify target table using 'FROM <table>'")
        else:
            table_name = table_match[0].lower()
            if table_name not in cls.VALID_TABLES:
                violations.append(f"Unknown table '{table_name}'. Allowed tables: {sorted(cls.VALID_TABLES)}")
                suggested_fixes.append(f"Use one of valid catalog tables: {sorted(cls.VALID_TABLES)}")

        # Check 4: Enforce explicit LIMIT
        if "LIMIT" not in query_upper:
            violations.append("Missing LIMIT clause (risk of unbounded result set)")
            suggested_fixes.append("Append 'LIMIT <N>' where N <= 100")

        passed = len(violations) == 0
        score = 1.0 if passed else max(0.0, 1.0 - (len(violations) * 0.25))
        return CritiqueResult(passed=passed, score=score, violations=violations, suggested_fixes=suggested_fixes)


class MockSqlGenerator:
    """Simulates generator model improving its draft across iterations based on critic feedback."""

    def generate(self, prompt: str, prior_violations: Optional[List[str]] = None, iteration: int = 1) -> str:
        if iteration == 1:
            # First draft: missing LIMIT and references non-existent table 'customers'
            return "SELECT id, name FROM customers WHERE active = 1;"
        elif iteration == 2:
            # Second draft: fixes table to 'users', but still missing LIMIT and has semicolon
            return "SELECT id, name FROM users WHERE active = 1;"
        else:
            # Third draft: satisfies all critic constraints
            return "SELECT id, name FROM users WHERE active = 1 LIMIT 50"


class EvaluatorOptimizerPipeline:
    """Manages the iteration loop between Generator and Critic."""

    def __init__(self, max_revisions: int = 3):
        self.max_revisions = max_revisions
        self.critic = DeterministicSqlCritic()
        self.generator = MockSqlGenerator()

    def run(self, prompt: str) -> Dict[str, Any]:
        history = []
        violations = []

        for iteration in range(1, self.max_revisions + 1):
            draft = self.generator.generate(prompt, prior_violations=violations, iteration=iteration)
            critique = self.critic.evaluate(draft)

            history.append({
                "iteration": iteration,
                "draft": draft,
                "passed": critique.passed,
                "score": critique.score,
                "violations": critique.violations
            })

            if critique.passed:
                return {
                    "converged": True,
                    "final_output": draft,
                    "total_iterations": iteration,
                    "history": history
                }

            violations = critique.violations

        return {
            "converged": False,
            "final_output": draft,
            "total_iterations": self.max_revisions,
            "history": history
        }


# --- Correlated Ensemble Failure Demonstration ---
def demonstrate_correlated_ensemble_failure():
    """Shows that 3 LLM agents in a voting ensemble all repeat the same error

    when they share the same outdated or biased context document, whereas a
    deterministic date check catches it immediately.
    """
    poisoned_context_doc = (
        "Policy Notice: Published 2021-05-01. Customer accounts can be deleted "
        "without manager approval if inactive for 90 days."
    )
    current_system_date = "2026-10-24"
    policy_effective_cutoff = "2024-01-01"

    # Three independent LLM agents voting on the action based on the document
    agent1_vote = "APPROVE_DELETION (Based on 2021 Policy Notice)"
    agent2_vote = "APPROVE_DELETION (Policy states 90 days inactivity qualifies)"
    agent3_vote = "APPROVE_DELETION (Agreement with published policy document)"

    ensemble_votes = [agent1_vote, agent2_vote, agent3_vote]
    consensus = all("APPROVE_DELETION" in v for v in ensemble_votes)

    # Deterministic external grounding check
    doc_date_match = re.search(r"Published (\d{4}-\d{2}-\d{2})", poisoned_context_doc)
    doc_date = doc_date_match.group(1) if doc_date_match else "1970-01-01"
    is_valid_policy = doc_date >= policy_effective_cutoff

    return {
        "ensemble_unanimous_vote": consensus,
        "ensemble_verdict": "APPROVED (3/3 votes)",
        "grounding_check_passed": is_valid_policy,
        "grounding_error": f"Policy date {doc_date} is obsolete (requires >= {policy_effective_cutoff})"
    }


def main():
    pipeline = EvaluatorOptimizerPipeline(max_revisions=3)
    result = pipeline.run("Write a query to get active user names")

    print("Evaluator-Optimizer Iteration Loop:")
    for step in result["history"]:
        print(f"\nIteration {step['iteration']}:")
        print(f"  Draft: '{step['draft']}'")
        print(f"  Passed: {step['passed']} (Score: {step['score']:.2f})")
        if step["violations"]:
            print(f"  Violations: {step['violations']}")

    print(f"\nConverged: {result['converged']} in {result['total_iterations']} iterations")
    print(f"Final Query: {result['final_output']}")

    assert result["converged"] is True
    assert result["total_iterations"] == 3
    assert "LIMIT 50" in result["final_output"]

    # 2. Correlated Ensemble Demonstration
    print("\n" + "=" * 50)
    print("Correlated Ensemble Failure vs Independent Grounding:")
    ensemble_res = demonstrate_correlated_ensemble_failure()
    print(f"  Ensemble Consensus: {ensemble_res['ensemble_verdict']}")
    print(f"  Grounding Check Passed: {ensemble_res['grounding_check_passed']}")
    print(f"  Grounding Diagnostic: {ensemble_res['grounding_error']}")

    assert ensemble_res["ensemble_unanimous_vote"] is True, "Ensemble should unanimously vote wrong due to shared context"
    assert ensemble_res["grounding_check_passed"] is False, "Deterministic grounding must catch the outdated policy error"

    print("\nEvaluator-Optimizer and ensemble failure mechanisms verified successfully.")


if __name__ == "__main__":
    main()
