"""Shared Blackboard agent memory pattern and multi-agent orchestration evaluation metrics.

Demonstrates:
1. Shared Blackboard pattern: Thread-safe centralized workspace partitioned into typed sections (problem, hypotheses, evidence, solution) with revision tracking.
2. Conflict-free multi-agent collaboration: Specialist agents read from and post contributions to the shared memory without direct point-to-point coupling.
3. Orchestration evaluation framework: Calculating completion rates, step efficiency, token costs, and failure mode distributions.
"""
from typing import Any, Dict, List, Optional
import collections
import threading

class BlackboardSection:
    def __init__(self, name: str):
        self.name = name
        self.entries: List[Dict[str, Any]] = []

    def append_entry(self, contributor_agent: str, content: Any, revision: int):
        self.entries.append({
            "contributor": contributor_agent,
            "content": content,
            "revision": revision
        })

class SharedBlackboardMemory:
    def __init__(self):
        self.lock = threading.Lock()
        self.revision = 0
        self.sections: Dict[str, BlackboardSection] = {
            "problem": BlackboardSection("problem"),
            "hypotheses": BlackboardSection("hypotheses"),
            "evidence": BlackboardSection("evidence"),
            "synthesis": BlackboardSection("synthesis")
        }

    def post(self, section_name: str, contributor: str, content: Any) -> int:
        with self.lock:
            self.revision += 1
            if section_name not in self.sections:
                self.sections[section_name] = BlackboardSection(section_name)
            self.sections[section_name].append_entry(contributor, content, self.revision)
            return self.revision

    def read_section(self, section_name: str) -> List[Dict[str, Any]]:
        with self.lock:
            if section_name not in self.sections:
                return []
            return list(self.sections[section_name].entries)

class OrchestrationEvaluator:
    @staticmethod
    def evaluate_orchestration_runs(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_runs = len(runs)
        completed = 0
        total_steps = 0
        useful_steps = 0
        total_cost_usd = 0.0
        failure_causes = collections.Counter()

        for run in runs:
            total_steps += run.get("total_steps", 0)
            useful_steps += run.get("useful_steps", 0)
            total_cost_usd += run.get("cost_usd", 0.0)

            if run.get("status") == "COMPLETED":
                completed += 1
            else:
                failure_causes[run.get("failure_reason", "UNKNOWN")] += 1

        completion_rate = (completed / total_runs * 100.0) if total_runs > 0 else 0.0
        step_efficiency = (useful_steps / total_steps * 100.0) if total_steps > 0 else 0.0
        cost_per_success = (total_cost_usd / completed) if completed > 0 else 0.0

        return {
            "total_runs_evaluated": total_runs,
            "completion_rate_percent": round(completion_rate, 1),
            "step_efficiency_percent": round(step_efficiency, 1),
            "cost_per_successful_run_usd": round(cost_per_success, 4),
            "failure_distribution": dict(failure_causes)
        }

if __name__ == "__main__":
    # 1. Blackboard multi-agent interaction
    bb = SharedBlackboardMemory()

    # Step 1: User problem
    bb.post("problem", "orchestrator", "Diagnose connection drops to PostgreSQL replica.")

    # Step 2: Diagnostic Agent posts hypothesis
    bb.post("hypotheses", "agent_diagnostician", "Hypothesis: TCP keepalive timeout under NAT firewall.")

    # Step 3: Retrieval Agent posts telemetry evidence
    bb.post("evidence", "agent_telemetry", "Log sample: BrokenPipeError after 60s idle.")

    # Step 4: Resolution Agent synthesizes solution
    bb.post("synthesis", "agent_resolver", "Action: Configure keepalives_idle=30 in postgresql.conf.")

    # Verify memory state
    problem_entries = bb.read_section("problem")
    synthesis_entries = bb.read_section("synthesis")
    assert len(problem_entries) == 1
    assert synthesis_entries[0]["contributor"] == "agent_resolver"
    assert "keepalives_idle=30" in synthesis_entries[0]["content"]
    assert bb.revision == 4

    # 2. Orchestration Evaluation Metrics
    mock_runs = [
        {"status": "COMPLETED", "total_steps": 4, "useful_steps": 4, "cost_usd": 0.04},
        {"status": "COMPLETED", "total_steps": 5, "useful_steps": 4, "cost_usd": 0.05},
        {"status": "FAILED", "failure_reason": "TOOL_TIMEOUT", "total_steps": 3, "useful_steps": 1, "cost_usd": 0.03}
    ]

    metrics = OrchestrationEvaluator.evaluate_orchestration_runs(mock_runs)
    assert metrics["total_runs_evaluated"] == 3
    assert metrics["completion_rate_percent"] == 66.7
    assert metrics["step_efficiency_percent"] == 75.0  # 9 useful / 12 total = 75.0%
    assert metrics["cost_per_successful_run_usd"] == 0.06  # ($0.12 total / 2 completed)
    assert metrics["failure_distribution"]["TOOL_TIMEOUT"] == 1

    print("Shared Blackboard memory pattern and orchestration evaluation verified successfully.")

