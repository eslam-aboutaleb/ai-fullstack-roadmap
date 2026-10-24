"""Fan-in branch reduction, partial failure degradation, and error provenance preservation.

Demonstrates:
1. Branch classification: Critical (Required) vs Supplementary (Optional) branches.
2. Preserving discrete error provenance: Capturing error categories (Timeout, Service Unavailable) without masking failures as empty results.
3. Partial degradation policy: Returning PARTIAL_SUCCESS with explicit degradation flags when optional branches fail.
4. Synthesizer input assembly: Clearly indicating failed sources to prevent hallucinated conclusions.
"""
from typing import Any, Dict, List, Optional
import asyncio

class BranchResult:
    def __init__(self, name: str, is_required: bool, data: Optional[Any] = None, error_category: Optional[str] = None):
        self.name = name
        self.is_required = is_required
        self.data = data
        self.error_category = error_category
        self.status = "SUCCESS" if error_category is None else "FAILED"

class FanInReducer:
    @staticmethod
    def reduce_branches(branch_results: List[BranchResult]) -> Dict[str, Any]:
        critical_failures = []
        optional_failures = []
        successful_data = {}

        for branch in branch_results:
            if branch.status == "SUCCESS":
                successful_data[branch.name] = branch.data
            else:
                if branch.is_required:
                    critical_failures.append({"branch": branch.name, "error": branch.error_category})
                else:
                    optional_failures.append({"branch": branch.name, "error": branch.error_category})

        # 1. If any critical branch failed, the entire fan-in barrier fails
        if critical_failures:
            return {
                "workflow_status": "FAILED",
                "critical_failures": critical_failures,
                "partial_data": successful_data,
                "message": f"Critical branches failed: {[f['branch'] for f in critical_failures]}"
            }

        # 2. If all critical succeeded but some optional failed, return PARTIAL_SUCCESS
        if optional_failures:
            return {
                "workflow_status": "PARTIAL_SUCCESS",
                "degraded": True,
                "data": successful_data,
                "missing_optional_sources": optional_failures,
                "synthesizer_context": FanInReducer._format_context_for_llm(successful_data, optional_failures)
            }

        # 3. All branches succeeded
        return {
            "workflow_status": "FULL_SUCCESS",
            "degraded": False,
            "data": successful_data,
            "synthesizer_context": FanInReducer._format_context_for_llm(successful_data, [])
        }

    @staticmethod
    def _format_context_for_llm(data: Dict[str, Any], missing: List[Dict[str, str]]) -> str:
        lines = ["=== AVAILABLE VERIFIED SOURCES ==="]
        for name, content in data.items():
            lines.append(f"[{name}]: {content}")

        if missing:
            lines.append("\n=== UNAVAILABLE SOURCES (DO NOT GUESS OR HALLUCINATE) ===")
            for item in missing:
                lines.append(f"[{item['branch']}]: FAILED with error '{item['error']}'")

        return "\n".join(lines)

if __name__ == "__main__":
    # Test Scenario 1: All branches succeed
    results_full = [
        BranchResult("core_pricing", is_required=True, data="$50/user"),
        BranchResult("user_discounts", is_required=True, data="10% volume discount"),
        BranchResult("promo_codes", is_required=False, data="WINTER2026")
    ]
    reduced_full = FanInReducer.reduce_branches(results_full)
    assert reduced_full["workflow_status"] == "FULL_SUCCESS"
    assert reduced_full["degraded"] is False

    # Test Scenario 2: Optional branch fails (Graceful Partial Degradation)
    results_degraded = [
        BranchResult("core_pricing", is_required=True, data="$50/user"),
        BranchResult("user_discounts", is_required=True, data="10% volume discount"),
        BranchResult("promo_codes", is_required=False, error_category="TIMEOUT")
    ]
    reduced_degraded = FanInReducer.reduce_branches(results_degraded)
    assert reduced_degraded["workflow_status"] == "PARTIAL_SUCCESS"
    assert reduced_degraded["degraded"] is True
    # Synthesizer context warns the model that promo_codes failed!
    assert "UNAVAILABLE SOURCES" in reduced_degraded["synthesizer_context"]
    assert "promo_codes" in reduced_degraded["synthesizer_context"]

    # Test Scenario 3: Critical branch fails (Immediate Workflow Failure)
    results_critical_fail = [
        BranchResult("core_pricing", is_required=True, error_category="DATABASE_DOWN"),
        BranchResult("user_discounts", is_required=True, data="10% volume discount"),
        BranchResult("promo_codes", is_required=False, data="WINTER2026")
    ]
    reduced_crit = FanInReducer.reduce_branches(results_critical_fail)
    assert reduced_crit["workflow_status"] == "FAILED"
    assert "core_pricing" in reduced_crit["message"]

    print("Fan-in partial failure reduction and error provenance verified successfully.")

