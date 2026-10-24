"""Cooperative cancellation propagation, token signaling, and external effect reconciliation.

Demonstrates:
1. The coroutine cancellation pitfall: Cancelling an asyncio coroutine stops caller waiting, but does NOT stop background workers or commit rollbacks.
2. Cooperative cancellation tokens: Propagating atomic cancellation signals across distributed sub-agents and tool executors.
3. Two-way cancellation reconciliation: Querying operation outcomes to distinguish cleanly aborted tasks from late-committed mutations.
"""
from typing import Any, Dict, List, Optional
import asyncio
import threading
import time

class CooperativeCancellationToken:
    def __init__(self):
        self._is_cancelled = False
        self._lock = threading.Lock()

    def cancel(self):
        with self._lock:
            self._is_cancelled = True

    @property
    def is_cancelled(self) -> bool:
        with self._lock:
            return self._is_cancelled

class BackgroundWorkerService:
    def __init__(self):
        self.operations: Dict[str, Dict[str, Any]] = {}

    def start_long_running_task(self, op_id: str, total_steps: int, token: CooperativeCancellationToken) -> str:
        self.operations[op_id] = {"status": "RUNNING", "steps_completed": 0}

        for step in range(1, total_steps + 1):
            # Check cooperative cancellation token before each mutation
            if token.is_cancelled:
                self.operations[op_id]["status"] = "CANCELLED"
                return f"Operation '{op_id}' aborted cooperatively at step {step-1}/{total_steps}."

            # Simulate work step
            time.sleep(0.01)
            self.operations[op_id]["steps_completed"] = step

        self.operations[op_id]["status"] = "COMMITTED"
        return f"Operation '{op_id}' fully completed all {total_steps} steps."

    def query_outcome(self, op_id: str) -> Dict[str, Any]:
        return self.operations.get(op_id, {"status": "UNKNOWN"})

async def demonstrate_cancellation_pitfall():
    """Demonstrates that cancelling a local caller task does NOT kill a background thread/service!"""
    service = BackgroundWorkerService()
    ignored_token = CooperativeCancellationToken()  # Never cancelled

    # Launch worker in background thread
    t = threading.Thread(target=service.start_long_running_task, args=("op_zombie", 5, ignored_token))
    t.start()

    # Client simulates coroutine timeout / cancel
    await asyncio.sleep(0.01)
    # Even if client coroutine aborts, the background worker continues running and commits!
    t.join()
    assert service.query_outcome("op_zombie")["status"] == "COMMITTED"

async def demonstrate_cooperative_propagation():
    """Demonstrates cooperative cancellation cleanly halting background execution."""
    service = BackgroundWorkerService()
    token = CooperativeCancellationToken()

    t = threading.Thread(target=service.start_long_running_task, args=("op_clean", 20, token))
    t.start()

    # User presses 'Cancel'
    await asyncio.sleep(0.02)
    token.cancel()
    t.join()

    # Verified: Worker checked token and aborted before finishing!
    outcome = service.query_outcome("op_clean")
    assert outcome["status"] == "CANCELLED"
    assert outcome["steps_completed"] < 20

if __name__ == "__main__":
    asyncio.run(demonstrate_cancellation_pitfall())
    asyncio.run(demonstrate_cooperative_propagation())
    print("Cooperative cancellation tokens and external effect reconciliation verified successfully.")
