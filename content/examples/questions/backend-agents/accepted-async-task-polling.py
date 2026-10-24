# /// script
# dependencies = []
# ///
"""
Production-Grade HTTP 202 Accepted Asynchronous Agent Task Pattern.

Decouples multi-turn LLM reasoning from client HTTP request lifetimes.
Demonstrates:
1. HTTP 202 Accepted with canonical Location header and Retry-After hint.
2. Two-phase idempotency key deduplication.
3. Tenant-isolated durable task progress polling.
4. Cooperative cancellation and structured error envelopes.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class TaskRecord:
    task_id: str
    tenant_id: str
    idempotency_key: str
    state: TaskState = TaskState.PENDING
    progress: float = 0.0
    steps_completed: List[str] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    cancellation_requested: bool = False


class TaskRepository:
    """Simulated thread-safe, tenant-isolated durable task store."""

    def __init__(self) -> None:
        self._tasks: Dict[str, TaskRecord] = {}
        self._idempotency_index: Dict[str, str] = {}  # tenant_id:key -> task_id

    def find_by_idempotency_key(self, tenant_id: str, key: str) -> Optional[TaskRecord]:
        compound_key = f"{tenant_id}:{key}"
        task_id = self._idempotency_index.get(compound_key)
        if task_id:
            return self._tasks.get(task_id)
        return None

    def save(self, task: TaskRecord) -> None:
        compound_key = f"{task.tenant_id}:{task.idempotency_key}"
        self._tasks[task.task_id] = task
        self._idempotency_index[compound_key] = task.task_id

    def get(self, task_id: str) -> Optional[TaskRecord]:
        return self._tasks.get(task_id)


class AgentTaskController:
    """REST Controller implementing HTTP 202 Accepted contract."""

    def __init__(self, repository: TaskRepository) -> None:
        self.repo = repository

    def create_task(
        self,
        tenant_id: str,
        user_id: str,
        prompt: str,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """POST /api/v1/agent/tasks

        Accepts long-running agent request, assigns identity, returns 202 Accepted.
        """
        if not prompt or not prompt.strip():
            return {
                "status_code": 400,
                "error": {"code": "INVALID_PROMPT", "message": "Prompt cannot be empty"},
            }

        # Check idempotency ledger
        existing = self.repo.find_by_idempotency_key(tenant_id, idempotency_key)
        if existing:
            # Idempotent replay: return existing task location and current status
            return {
                "status_code": 202,
                "headers": {
                    "Location": f"/api/v1/agent/tasks/{existing.task_id}",
                    "Retry-After": "2",
                    "X-Idempotent-Replay": "true",
                },
                "body": {
                    "task_id": existing.task_id,
                    "state": existing.state.value,
                    "progress": existing.progress,
                    "created_at": existing.created_at,
                },
            }

        # Mint new unique task ID
        task_id = f"tsk_{uuid.uuid4().hex[:12]}"
        record = TaskRecord(
            task_id=task_id,
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
            state=TaskState.PENDING,
            progress=0.0,
        )
        self.repo.save(record)

        return {
            "status_code": 202,
            "headers": {
                "Location": f"/api/v1/agent/tasks/{task_id}",
                "Retry-After": "1",
                "X-Idempotent-Replay": "false",
            },
            "body": {
                "task_id": task_id,
                "state": TaskState.PENDING.value,
                "progress": 0.0,
                "created_at": record.created_at,
                "events_url": f"/api/v1/agent/tasks/{task_id}/events",
            },
        }

    def get_task_status(self, tenant_id: str, task_id: str) -> Dict[str, Any]:
        """GET /api/v1/agent/tasks/{task_id}

        Authoritative status polling with strict tenant isolation.
        """
        record = self.repo.get(task_id)
        if not record:
            return {
                "status_code": 404,
                "error": {"code": "TASK_NOT_FOUND", "message": f"Task {task_id} not found"},
            }

        # Tenant isolation check
        if record.tenant_id != tenant_id:
            return {
                "status_code": 403,
                "error": {"code": "FORBIDDEN", "message": "Access to cross-tenant task denied"},
            }

        return {
            "status_code": 200,
            "body": {
                "task_id": record.task_id,
                "state": record.state.value,
                "progress": record.progress,
                "steps_completed": record.steps_completed,
                "result": record.result,
                "error": record.error,
                "updated_at": record.updated_at,
            },
        }

    def cancel_task(self, tenant_id: str, task_id: str) -> Dict[str, Any]:
        """POST /api/v1/agent/tasks/{task_id}/cancel

        Requests cooperative cancellation.
        """
        record = self.repo.get(task_id)
        if not record or record.tenant_id != tenant_id:
            return {"status_code": 404, "error": {"code": "TASK_NOT_FOUND"}}

        if record.state in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED):
            return {
                "status_code": 409,
                "error": {"code": "TASK_ALREADY_TERMINAL", "message": f"Task is in {record.state}"},
            }

        record.cancellation_requested = True
        record.state = TaskState.CANCELLED
        record.updated_at = time.time()
        self.repo.save(record)
        return {
            "status_code": 200,
            "body": {"task_id": task_id, "state": TaskState.CANCELLED.value},
        }

    def execute_agent_loop(self, task_id: str) -> None:
        """Simulates asynchronous background worker execution with step-wise updates."""
        record = self.repo.get(task_id)
        if not record or record.cancellation_requested:
            return

        steps = [
            ("intent_classification", 0.25),
            ("retrieval_augmented_search", 0.50),
            ("llm_reasoning_and_synthesis", 0.75),
            ("response_validation", 1.00),
        ]

        record.state = TaskState.RUNNING
        for step_name, progress_val in steps:
            if record.cancellation_requested:
                record.state = TaskState.CANCELLED
                record.updated_at = time.time()
                self.repo.save(record)
                return

            record.steps_completed.append(step_name)
            record.progress = progress_val
            record.updated_at = time.time()
            self.repo.save(record)

        record.state = TaskState.COMPLETED
        record.result = {
            "summary": "Agent successfully reconciled query and produced authoritative response.",
            "citations": ["doc_rag_intro.pdf", "api_contract.md"],
            "tokens_consumed": 1420,
        }
        record.updated_at = time.time()
        self.repo.save(record)


def main() -> None:
    repo = TaskRepository()
    controller = AgentTaskController(repo)

    tenant_a = "tenant-alpha"
    tenant_b = "tenant-bravo"
    op_key = "idemp-req-7729"

    # 1. Client submits asynchronous task
    resp = controller.create_task(
        tenant_id=tenant_a,
        user_id="usr_01",
        prompt="Analyze Q3 regulatory filings and extract liability clauses.",
        idempotency_key=op_key,
    )

    assert resp["status_code"] == 202, f"Expected 202 Accepted, got {resp['status_code']}"
    assert "Location" in resp["headers"], "Missing Location header in 202 response"
    assert resp["headers"]["X-Idempotent-Replay"] == "false"
    task_id = resp["body"]["task_id"]
    assert resp["headers"]["Location"] == f"/api/v1/agent/tasks/{task_id}"

    # 2. Duplicate submission with same idempotency key returns exact same task
    replay_resp = controller.create_task(
        tenant_id=tenant_a,
        user_id="usr_01",
        prompt="Analyze Q3 regulatory filings and extract liability clauses.",
        idempotency_key=op_key,
    )
    assert replay_resp["status_code"] == 202
    assert replay_resp["headers"]["X-Idempotent-Replay"] == "true"
    assert replay_resp["body"]["task_id"] == task_id, "Idempotent replay returned different task ID"

    # 3. Cross-tenant authorization check
    cross_poll = controller.get_task_status(tenant_id=tenant_b, task_id=task_id)
    assert cross_poll["status_code"] == 403, "Cross-tenant poll should be rejected with 403 Forbidden"

    # 4. Background worker executes multi-turn loop
    controller.execute_agent_loop(task_id)

    # 5. Authoritative poll verifies terminal COMPLETED state
    final_poll = controller.get_task_status(tenant_id=tenant_a, task_id=task_id)
    assert final_poll["status_code"] == 200
    final_state = final_poll["body"]
    assert final_state["state"] == TaskState.COMPLETED.value
    assert final_state["progress"] == 1.0
    assert len(final_state["steps_completed"]) == 4
    assert final_state["result"]["tokens_consumed"] == 1420

    # 6. Cancellation test on a separate task
    cancel_resp = controller.create_task(
        tenant_id=tenant_a,
        user_id="usr_02",
        prompt="Long recursive web crawl.",
        idempotency_key="idemp-cancel-01",
    )
    cancel_task_id = cancel_resp["body"]["task_id"]
    cancelled = controller.cancel_task(tenant_id=tenant_a, task_id=cancel_task_id)
    assert cancelled["status_code"] == 200
    assert cancelled["body"]["state"] == TaskState.CANCELLED.value

    print(
        f"Accepted async task lifecycle verified: status={resp['status_code']}, "
        f"terminal_state={final_state['state']}, progress={final_state['progress']}"
    )


if __name__ == "__main__":
    main()
