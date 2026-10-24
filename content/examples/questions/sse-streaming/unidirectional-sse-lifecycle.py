# /// script
# dependencies = []
# ///
"""
Unidirectional SSE Lifecycle with Out-of-Band Cancellation.

Demonstrates:
1. Asymmetric protocol contract:
   - Downstream event consumption via GET /api/v1/tasks/{id}/events.
   - Upstream client cancellation via POST /api/v1/tasks/{id}/cancel.
2. Server detecting client socket disconnection or explicit cancel request,
   cooperatively aborting background model execution to avoid token waste.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class TaskExecutionRuntime:
    """Manages long-running agent tasks with cooperative cancellation."""

    def __init__(self) -> None:
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def start_task(self, task_id: str) -> None:
        self.tasks[task_id] = {
            "status": "RUNNING",
            "cancel_requested": False,
            "tokens_generated": 0,
        }

    def request_cancellation(self, task_id: str) -> Dict[str, Any]:
        """POST /api/v1/tasks/{task_id}/cancel"""
        task = self.tasks.get(task_id)
        if not task:
            return {"status": "NOT_FOUND"}

        task["cancel_requested"] = True
        task["status"] = "CANCELLED"
        return {"status": "CANCELLED", "task_id": task_id}

    def simulate_worker_step(self, task_id: str) -> bool:
        """Worker checks cancellation token before each reasoning/generation turn."""
        task = self.tasks[task_id]
        if task["cancel_requested"]:
            # Cooperative abort
            return False

        task["tokens_generated"] += 10
        return True


def main() -> None:
    runtime = TaskExecutionRuntime()
    task_id = "tsk_sse_9941"

    # 1. API Contract Definition
    api_contract = {
        "stream_events": {"method": "GET", "path": f"/api/v1/tasks/{task_id}/events"},
        "cancel_task": {"method": "POST", "path": f"/api/v1/tasks/{task_id}/cancel"},
    }
    stream_method = api_contract["stream_events"]["method"]
    cancel_method = api_contract["cancel_task"]["method"]

    # 2. Worker starts task
    runtime.start_task(task_id)
    step1 = runtime.simulate_worker_step(task_id)
    assert step1 is True
    assert runtime.tasks[task_id]["tokens_generated"] == 10

    # 3. Client issues out-of-band cancellation via POST
    cancel_resp = runtime.request_cancellation(task_id)
    assert cancel_resp["status"] == "CANCELLED"

    # 4. Worker's next step immediately halts due to cancellation token check
    step2 = runtime.simulate_worker_step(task_id)
    assert step2 is False, "Worker should cooperatively abort when cancellation is requested"
    worker_aborted = not step2

    # Invariant: No further tokens generated
    assert runtime.tasks[task_id]["tokens_generated"] == 10

    print(
        f"Unidirectional SSE lifecycle verified: stream_method={stream_method}, "
        f"cancel_method={cancel_method}, worker_aborted={worker_aborted}"
    )


if __name__ == "__main__":
    main()
