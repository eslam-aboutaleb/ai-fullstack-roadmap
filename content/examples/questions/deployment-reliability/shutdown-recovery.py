"""Graceful Shutdown Draining & Recoverable Task Checkpoints.

Demonstrates graceful worker termination on SIGTERM. Halts new task admission,
checkpoints active task progress to durable storage, and marks incomplete work
as recoverable so failover workers can resume without duplicate side effects.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class TaskExecutionState(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    RECOVERABLE = "recoverable"
    COMPLETED = "completed"


@dataclass
class BackgroundTask:
    task_id: str
    operation: str
    processed_items: int = 0
    total_items: int = 100
    state: TaskExecutionState = TaskExecutionState.QUEUED
    last_checkpoint_token: Optional[str] = None


class ResilientWorkerProcess:
    """Worker handling SIGTERM by draining in-flight work and checkpointing state."""

    def __init__(self, worker_id: str) -> None:
        self.worker_id = worker_id
        self.accepting_new_work: bool = True
        self.active_task: Optional[BackgroundTask] = None
        self.persisted_checkpoint_store: Dict[str, Dict[str, Any]] = {}

    def admit_task(self, task: BackgroundTask) -> bool:
        if not self.accepting_new_work:
            return False  # Refuse admission during shutdown draining
        self.active_task = task
        task.state = TaskExecutionState.IN_PROGRESS
        return True

    def process_work_batch(self, batch_size: int) -> None:
        if self.active_task and self.active_task.state == TaskExecutionState.IN_PROGRESS:
            self.active_task.processed_items += batch_size
            self.active_task.last_checkpoint_token = f"offset_{self.active_task.processed_items}"

    def handle_sigterm(self) -> Dict[str, Any]:
        """Triggered upon receiving OS SIGTERM signal."""
        # 1. Stop admitting new tasks immediately
        self.accepting_new_work = False

        receipt = {"worker_id": self.worker_id, "action": "sigterm_handled"}

        # 2. If an active task is incomplete, checkpoint and mark recoverable
        if self.active_task and self.active_task.processed_items < self.active_task.total_items:
            task = self.active_task
            task.state = TaskExecutionState.RECOVERABLE

            # Persist checkpoint to durable store
            self.persisted_checkpoint_store[task.task_id] = {
                "operation": task.operation,
                "processed_items": task.processed_items,
                "checkpoint_token": task.last_checkpoint_token,
                "status": task.state.value,
            }
            receipt["task_id"] = task.task_id
            receipt["status"] = task.state.value
            receipt["saved_offset"] = task.processed_items
            self.active_task = None
            return receipt

        return receipt


def test_shutdown_recovery() -> None:
    worker = ResilientWorkerProcess("worker_pod_01")
    assert worker.accepting_new_work is True

    # 1. Admit long-running batch embedding task
    task = BackgroundTask(task_id="task_embed_docs_99", operation="batch_vectorize", total_items=100)
    assert worker.admit_task(task) is True

    # Process 40 items
    worker.process_work_batch(40)
    assert task.processed_items == 40
    assert task.last_checkpoint_token == "offset_40"

    # 2. Kubernetes issues SIGTERM to worker_pod_01 for rolling deployment
    sigterm_receipt = worker.handle_sigterm()

    # INVARIANTS:
    # A: Worker must reject any further work
    assert worker.accepting_new_work is False
    assert worker.admit_task(BackgroundTask("task_new", "op_new")) is False

    # B: Active task must NOT be marked completed, but RECOVERABLE with checkpoint!
    assert sigterm_receipt["status"] == "recoverable"
    assert sigterm_receipt["saved_offset"] == 40
    assert "task_embed_docs_99" in worker.persisted_checkpoint_store

    # 3. New failover worker resumes from saved checkpoint
    new_worker = ResilientWorkerProcess("worker_pod_02")
    checkpoint_data = worker.persisted_checkpoint_store["task_embed_docs_99"]

    resumed_task = BackgroundTask(
        task_id="task_embed_docs_99",
        operation=checkpoint_data["operation"],
        processed_items=checkpoint_data["processed_items"],
        total_items=100,
    )
    assert new_worker.admit_task(resumed_task) is True
    # Finish remaining 60 items
    new_worker.process_work_batch(60)
    assert resumed_task.processed_items == 100
    resumed_task.state = TaskExecutionState.COMPLETED

    print(
        f"Shutdown recovery verified: accepting_new={worker.accepting_new_work}, "
        f"interrupted_task_state={checkpoint_data['status']}, "
        f"checkpoint_offset={checkpoint_data['processed_items']}, "
        f"failover_completed=True"
    )


if __name__ == "__main__":
    test_shutdown_recovery()
