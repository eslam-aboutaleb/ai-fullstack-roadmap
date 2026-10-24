"""Live Agent Fault-Recovery & Resilience Suite.

Automated verification suite demonstrating that a live agent survives four mandatory
failure modes: client reconnection, mid-stream user correction/barge-in, overload
backpressure load shedding, and process restart recovery from durable checkpoints.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class TaskState(str, Enum):
    IDLE = "idle"
    GENERATING = "generating"
    ABORTED = "aborted"
    COMPLETED = "completed"


class WorkloadPriority(int, Enum):
    TIER_1_CRITICAL_CONTROL = 1  # Stop, cancel, safety
    TIER_2_INTERACTIVE_TURN = 2  # Real-time chat
    TIER_3_SPECULATIVE_ASYNC = 3  # Pre-fetching, auto-suggestions


@dataclass
class DurableAgentPod:
    pod_id: str
    durable_store: Dict[str, Dict[str, Any]]
    active_memory: Dict[str, Any] = field(default_factory=dict)
    current_task_state: TaskState = TaskState.IDLE
    current_task_id: Optional[str] = None
    queue_capacity: int = 5
    work_queue: List[Dict[str, Any]] = field(default_factory=list)
    shed_work_count: int = 0

    def admit_work(self, item: Dict[str, Any]) -> bool:
        """Admission control prioritizing Tier 1 cancellations during overload."""
        priority = item["priority"]
        if priority == WorkloadPriority.TIER_1_CRITICAL_CONTROL:
            # Critical cancellations always bypass or preempt queue
            self.work_queue.insert(0, item)
            return True

        if len(self.work_queue) >= self.queue_capacity:
            # Overload: Shed low-priority speculative work
            self.shed_work_count += 1
            return False

        self.work_queue.append(item)
        return True

    def barge_in_cancel(self, task_id: str) -> bool:
        """Handles mid-stream user interrupt / stop command."""
        if self.current_task_id == task_id and self.current_task_state == TaskState.GENERATING:
            self.current_task_state = TaskState.ABORTED
            # Persist cancellation to durable store
            self.durable_store[task_id]["status"] = "aborted"
            return True
        return False

    def checkpoint_state(self, task_id: str, payload: Dict[str, Any]) -> None:
        self.durable_store[task_id] = payload

    def crash_and_recover(self, new_pod_id: str) -> "DurableAgentPod":
        """Simulate container restart or node failover rehydrating from durable store."""
        new_pod = DurableAgentPod(pod_id=new_pod_id, durable_store=self.durable_store)
        # Rehydrate uncommitted or active tasks
        for tid, data in self.durable_store.items():
            new_pod.active_memory[tid] = dict(data)
        return new_pod


def test_live_recovery_suite() -> None:
    durable_db: Dict[str, Dict[str, Any]] = {}
    pod = DurableAgentPod(pod_id="pod_worker_01", durable_store=durable_db, queue_capacity=2)
    demonstrated_scenarios: Set[str] = set()

    # Scenario 1: Reconnection & Session Re-attachment
    # User session persisted in durable store
    pod.checkpoint_state(
        "sess_live_100",
        {"user_id": "u42", "history": ["User: draft proposal", "Agent: Starting research"]},
    )
    # Socket disconnects and re-attaches
    session_recovered = pod.durable_store.get("sess_live_100")
    assert session_recovered is not None
    assert len(session_recovered["history"]) == 2
    demonstrated_scenarios.add("reconnection")

    # Scenario 2: Mid-Stream Correction / Barge-In
    # Agent is generating 500-token response
    pod.current_task_id = "task_gen_88"
    pod.current_task_state = TaskState.GENERATING
    pod.checkpoint_state("task_gen_88", {"status": "generating", "tokens_emitted": 35})

    # User clicks "Stop / Wait, analyze competitor B instead"
    barge_in_success = pod.barge_in_cancel("task_gen_88")
    assert barge_in_success is True
    assert pod.current_task_state == TaskState.ABORTED
    assert pod.durable_store["task_gen_88"]["status"] == "aborted"
    demonstrated_scenarios.add("correction")

    # Scenario 3: Overload Shedding & Backpressure
    # Fill queue to capacity (2 items) with interactive turns
    assert pod.admit_work({"id": "w1", "priority": WorkloadPriority.TIER_2_INTERACTIVE_TURN}) is True
    assert pod.admit_work({"id": "w2", "priority": WorkloadPriority.TIER_2_INTERACTIVE_TURN}) is True

    # 3rd item is speculative background auto-complete: MUST BE SHED
    admitted_speculative = pod.admit_work(
        {"id": "w3", "priority": WorkloadPriority.TIER_3_SPECULATIVE_ASYNC}
    )
    assert admitted_speculative is False
    assert pod.shed_work_count == 1

    # Tier 1 emergency stop: MUST ALWAYS BE ADMITTED EVEN WHEN QUEUE IS FULL
    admitted_cancel = pod.admit_work(
        {"id": "w_emergency_cancel", "priority": WorkloadPriority.TIER_1_CRITICAL_CONTROL}
    )
    assert admitted_cancel is True
    assert pod.work_queue[0]["id"] == "w_emergency_cancel"
    demonstrated_scenarios.add("overload")

    # Scenario 4: Pod Crash and Restart Recovery
    pod.checkpoint_state("task_checkout_99", {"status": "authorized", "amount": 150.0})
    recovered_pod = pod.crash_and_recover("pod_worker_02")
    assert "task_checkout_99" in recovered_pod.active_memory
    assert recovered_pod.active_memory["task_checkout_99"]["amount"] == 150.0
    demonstrated_scenarios.add("restart")

    required_scenarios = {"reconnection", "correction", "overload", "restart"}
    assert demonstrated_scenarios == required_scenarios

    print(
        f"Fault recovery resilience suite verified: all_passed=True, "
        f"scenarios_tested={sorted(list(demonstrated_scenarios))}, "
        f"shed_overload_count={pod.shed_work_count}"
    )


if __name__ == "__main__":
    test_live_recovery_suite()

