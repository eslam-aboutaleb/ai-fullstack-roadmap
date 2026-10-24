"""A2A Remote Task Lifecycle and Artifact Reconciliation Pattern.

Demonstrates:
1. Distinct Roles:
   - Ordinary API: Synchronous CRUD operations (fast, deterministic).
   - MCP (Model Context Protocol): Host-to-local-process tool/resource integration protocol.
   - A2A (Agent-to-Agent): Cross-network, autonomous agent task delegation with independent lifecycle,
     asynchronous state progression, and typed artifact delivery.
2. Progressive Lifecycle:
   - SUBMITTED -> WORKING (streaming thoughts / interim artifacts) -> COMPLETED.
3. Early Artifact Reconciliation:
   - Safely reconciles an interim artifact received while task is still in WORKING status before terminal transition.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
import time
from typing import Any, Dict, List, Optional
import uuid


class TaskState(Enum):
    SUBMITTED = "SUBMITTED"
    WORKING = "WORKING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class AgentArtifact:
    artifact_id: str
    artifact_type: str  # e.g., "report/markdown", "dataset/json"
    content: str
    is_interim: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class RemoteAgentTask:
    task_id: str
    initiator_agent: str
    specialist_agent: str
    intent: str
    state: TaskState = TaskState.SUBMITTED
    messages: List[Dict[str, str]] = field(default_factory=list)
    artifacts: List[AgentArtifact] = field(default_factory=list)
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None


class MockRemoteSpecialistAgent:
    """Simulates a remote financial auditor agent running over A2A protocol."""

    def __init__(self, agent_id: str = "agent-fin-auditor-v2"):
        self.agent_id = agent_id
        self.tasks: Dict[str, RemoteAgentTask] = {}

    def submit_task(self, initiator: str, intent: str, params: Dict[str, Any]) -> str:
        task_id = "task_ee6157961048"
        task = RemoteAgentTask(
            task_id=task_id,
            initiator_agent=initiator,
            specialist_agent=self.agent_id,
            intent=intent
        )
        task.messages.append({"role": "user", "text": f"Audit request: {params}"})
        self.tasks[task_id] = task
        return task_id

    def progress_task_step(self, task_id: str, step_type: str) -> RemoteAgentTask:
        task = self.tasks[task_id]
        if step_type == "start_analysis":
            task.state = TaskState.WORKING
            task.messages.append({"role": "agent", "text": "Parsing ledger records..."})
            # Emits interim artifact before final completion!
            interim_report = AgentArtifact(
                artifact_id=f"art_interim_{task_id[:6]}",
                artifact_type="report/draft",
                content="# Interim Findings: Discrepancy detected in Q3 expense allocations.",
                is_interim=True
            )
            task.artifacts.append(interim_report)

        elif step_type == "complete_analysis":
            task.state = TaskState.COMPLETED
            task.completed_at = datetime.now(timezone.utc).isoformat()
            task.messages.append({"role": "agent", "text": "Audit complete. Final report attached."})
            final_report = AgentArtifact(
                artifact_id=f"art_final_{task_id[:6]}",
                artifact_type="report/markdown",
                content="# Final Audit Report: All Q3 allocations reconciled. Net adjustment: -$1,240.00.",
                is_interim=False
            )
            task.artifacts.append(final_report)

        return task


class A2ACoordinatorClient:
    """Client handling remote A2A task lifecycle and interim artifact reconciliation."""

    def __init__(self, remote_service: MockRemoteSpecialistAgent):
        self.remote = remote_service
        self.tracked_artifacts: Dict[str, AgentArtifact] = {}

    def run_coordinated_audit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Submit task
        task_id = self.remote.submit_task(
            initiator="coordinator-core",
            intent="conduct_q3_financial_audit",
            params=params
        )

        # 2. Poll/Stream step 1: Interim artifact in WORKING state
        task_state_1 = self.remote.progress_task_step(task_id, "start_analysis")
        assert task_state_1.state == TaskState.WORKING
        assert len(task_state_1.artifacts) == 1

        # Reconcile early artifact received before terminal state!
        early_art = task_state_1.artifacts[0]
        # Safety invariant: mark early artifact as PROVISIONAL and DO NOT execute mutations based on it
        self.reconcile_early_artifact(task_id, early_art, current_state=task_state_1.state)

        # 3. Poll/Stream step 2: Final completion
        task_state_2 = self.remote.progress_task_step(task_id, "complete_analysis")
        assert task_state_2.state == TaskState.COMPLETED
        assert len(task_state_2.artifacts) == 2

        final_art = [a for a in task_state_2.artifacts if not a.is_interim][0]
        self.reconcile_terminal_artifact(task_id, final_art)

        return {
            "task_id": task_id,
            "final_state": task_state_2.state.value,
            "total_artifacts": len(task_state_2.artifacts),
            "provisional_handled": early_art.artifact_id in self.tracked_artifacts,
            "final_artifact_id": final_art.artifact_id
        }

    def reconcile_early_artifact(self, task_id: str, artifact: AgentArtifact, current_state: TaskState):
        """Invariant: An artifact received prior to terminal state is provisional

        and cannot trigger downstream external mutations until verified against final task completion.
        """
        self.tracked_artifacts[artifact.artifact_id] = artifact
        print(f"  [Interim Artifact] Recorded {artifact.artifact_id} ({artifact.artifact_type}) while task is {current_state.value}")

    def reconcile_terminal_artifact(self, task_id: str, artifact: AgentArtifact):
        self.tracked_artifacts[artifact.artifact_id] = artifact
        print(f"  [Terminal Artifact] Authoritative result {artifact.artifact_id} committed.")


def main():
    print("Testing A2A Task Lifecycle and Early Artifact Reconciliation:")
    specialist = MockRemoteSpecialistAgent("agent-fin-auditor-v2")
    coordinator = A2ACoordinatorClient(specialist)

    audit_params = {"department": "engineering", "quarter": "Q3", "ledger_id": "LEDG-9021"}
    result = coordinator.run_coordinated_audit(audit_params)

    print("\nA2A Orchestration Result:")
    print(json.dumps(result, indent=2))

    assert result["final_state"] == "COMPLETED"
    assert result["total_artifacts"] == 2
    assert result["provisional_handled"] is True

    print("\nA2A task lifecycle and early artifact reconciliation verified successfully.")


if __name__ == "__main__":
    main()

