"""Remote Agent Task Cancellation, Timeout Reconciliation, and Idempotent Retries.

Demonstrates:
1. Idempotency Key Preservation:
   - Client generates a stable, unique task_id for remote invocations.
   - Retrying with the same task_id re-attaches to existing work rather than spawning duplicate agents.
2. Network Timeout Recovery:
   - When a remote call times out, client avoids blind retry by querying authoritative task status.
3. Cooperative Cancellation Semantics:
   - Cancelling an in-flight remote task halts active computation and uncommitted steps.
   - Authoritative audit records explicitly separate committed irreversible effects (e.g. notifications sent)
     from aborted steps.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
import time
from typing import Any, Dict, List, Optional


class RemoteStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


@dataclass
class RemoteTaskRecord:
    task_id: str
    action: str
    params: Dict[str, Any]
    status: RemoteStatus = RemoteStatus.PENDING
    committed_effects: List[str] = field(default_factory=list)
    aborted_steps: List[str] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    cancellation_requested: bool = False


class RemoteAgentService:
    """Mock remote agent service maintaining authoritative state for remote tasks."""

    def __init__(self):
        self.tasks: Dict[str, RemoteTaskRecord] = {}
        self.invocation_counts: Dict[str, int] = {}

    def dispatch_or_attach(self, task_id: str, action: str, params: Dict[str, Any]) -> RemoteTaskRecord:
        """Idempotent dispatch: if task_id already exists, return current record without duplicating work."""
        self.invocation_counts[task_id] = self.invocation_counts.get(task_id, 0) + 1

        if task_id in self.tasks:
            # Re-attach to existing task!
            return self.tasks[task_id]

        record = RemoteTaskRecord(task_id=task_id, action=action, params=params, status=RemoteStatus.PENDING)
        self.tasks[task_id] = record
        return record

    def advance_execution_step(self, task_id: str, step_name: str, is_irreversible: bool = False):
        record = self.tasks[task_id]
        if record.cancellation_requested:
            record.status = RemoteStatus.CANCELLED
            record.aborted_steps.append(step_name)
            return

        record.status = RemoteStatus.IN_PROGRESS
        if is_irreversible:
            record.committed_effects.append(step_name)

    def request_cancellation(self, task_id: str) -> Dict[str, Any]:
        record = self.tasks.get(task_id)
        if not record:
            raise KeyError(f"Task {task_id} not found")

        record.cancellation_requested = True
        record.status = RemoteStatus.CANCELLED

        return {
            "task_id": task_id,
            "status": record.status.value,
            "committed_effects": record.committed_effects,
            "aborted_steps": record.aborted_steps
        }

    def query_status(self, task_id: str) -> RemoteTaskRecord:
        if task_id not in self.tasks:
            raise KeyError(f"Task {task_id} not found")
        return self.tasks[task_id]


class ResilientA2AClient:
    """Coordinator client managing timeouts, retries, and cancellation."""

    def __init__(self, service: RemoteAgentService):
        self.service = service

    def execute_with_timeout_reconciliation(self, task_id: str, action: str, params: Dict[str, Any]) -> RemoteTaskRecord:
        # Step 1: Initial dispatch
        self.service.dispatch_or_attach(task_id, action, params)

        # Step 2: Progress step 1 (irreversible notification sent)
        self.service.advance_execution_step(task_id, "SEND_CUSTOMER_EMAIL_RECEIPT", is_irreversible=True)

        # Simulate network timeout: client dropped connection before receiving step 1 response!
        # Step 3: Reconnect with same task_id rather than minting a new task!
        reconnected_record = self.service.dispatch_or_attach(task_id, action, params)
        assert len(self.service.tasks) == 1, "Idempotency key must prevent duplicate task creation"

        # Step 4: Progress step 2 (long-running model computation)
        self.service.advance_execution_step(task_id, "GENERATE_FINANCIAL_FORECAST", is_irreversible=False)

        # Step 5: User triggers cancellation during execution
        cancel_summary = self.service.request_cancellation(task_id)

        # Step 6: Server attempts next step, but detects cancellation flag!
        self.service.advance_execution_step(task_id, "COMMIT_DATABASE_LEDGER_UPDATE", is_irreversible=True)

        final_record = self.service.query_status(task_id)
        return final_record


def main():
    service = RemoteAgentService()
    client = ResilientA2AClient(service)

    task_id = "task_fin_report_9901"
    print(f"Executing remote task with ID: {task_id}")

    final_record = client.execute_with_timeout_reconciliation(
        task_id=task_id,
        action="generate_and_commit_financial_audit",
        params={"quarter": "Q4", "amount": 50000}
    )

    print("\nAuthoritative Remote Task State:")
    print(f"  Status: {final_record.status.value}")
    print(f"  Service Invocation Count for ID: {service.invocation_counts[task_id]} (Idempotent duplicate caught)")
    print(f"  Committed Irreversible Effects: {final_record.committed_effects}")
    print(f"  Aborted Steps: {final_record.aborted_steps}")

    # Assertions
    assert final_record.status == RemoteStatus.CANCELLED
    assert service.invocation_counts[task_id] == 2, "Client dispatched twice due to simulated timeout"
    assert len(service.tasks) == 1, "Only one authoritative task must exist"
    assert "SEND_CUSTOMER_EMAIL_RECEIPT" in final_record.committed_effects, "Pre-cancellation email must be recorded"
    assert "COMMIT_DATABASE_LEDGER_UPDATE" in final_record.aborted_steps, "Post-cancellation DB commit must be aborted"

    print("\nRemote cancellation and idempotent retry reconciliation verified successfully.")


if __name__ == "__main__":
    main()
