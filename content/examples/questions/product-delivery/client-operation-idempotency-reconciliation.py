"""
client-operation-idempotency-reconciliation.py

Production-grade Client Operation Lifecycle, Retry Reconciliation, and UI State Suite.
Demonstrates:
1. The Naive UI Retry Trap:
   - Network timeout occurs after the backend accepts an operation.
   - The UI displays a 'Try Again' button that mints a brand-new operation key,
     triggering duplicate external mutations (double billing, duplicate bookings).
2. The Resilient Client Operation State Machine:
   - Decoupling Model Operation state, Transport Connection state, and UI Draft text.
   - Retaining the stable client_operation_key across retries.
   - Reconciling with backend idempotency records to prevent duplicate task execution.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TransportStatus(str, Enum):
    CONNECTED = "CONNECTED"
    TIMEOUT = "TIMEOUT"
    DISCONNECTED = "DISCONNECTED"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMMITTED = "COMMITTED"


@dataclass
class ClientSessionState:
    session_id: str
    active_operation_key: Optional[str] = None
    last_known_task_id: Optional[str] = None
    visible_draft_text: str = ""
    is_reconciling: bool = False


class BackendOperationGateway:
    def __init__(self):
        # Maps client_operation_key -> Task record
        self.idempotency_store: Dict[str, Dict[str, Any]] = {}
        self.mutation_counter: int = 0

    def submit_task(self, client_key: str, amount: float, simulate_ack_loss: bool = False) -> Dict[str, Any]:
        """
        Accepts and processes an operation under an idempotency key.
        """
        if client_key in self.idempotency_store:
            # Replay existing task state without re-executing business mutations
            return {
                "status": "REPLAYED",
                "task": self.idempotency_store[client_key]
            }

        # New mutation executed
        self.mutation_counter += 1
        task_record = {
            "task_id": f"task_{self.mutation_counter:04d}",
            "client_key": client_key,
            "amount": amount,
            "state": TaskStatus.COMMITTED.value
        }
        self.idempotency_store[client_key] = task_record

        if simulate_ack_loss:
            # Backend committed the task, but response drops on network
            raise TimeoutError("TCP connection timed out before ACK received by client")

        return {"status": "COMMITTED", "task": task_record}

    def reconcile_task_status(self, client_key: str) -> Optional[Dict[str, Any]]:
        return self.idempotency_store.get(client_key)


def main() -> None:
    print("=== Testing Client Operation Idempotency & Retry Reconciliation Suite ===")
    gateway = BackendOperationGateway()
    client = ClientSessionState(session_id="client_sess_001")

    # 1. User submits an order for $120.00
    client.active_operation_key = "op_uuid_8844"
    client.visible_draft_text = "Order 2x Wireless Headphones ($120.00)"

    print(f"\nAttempt 1: Submitting with client_key '{client.active_operation_key}' (Simulating network ACK drop)...")
    try:
        gateway.submit_task(
            client_key=client.active_operation_key,
            amount=120.0,
            simulate_ack_loss=True
        )
        assert False, "Should have thrown TimeoutError"
    except TimeoutError:
        print("  Network timeout! Client did not receive the HTTP 200 response.")

    # Invariant: The backend actually committed the task before network drop
    assert gateway.mutation_counter == 1
    assert "op_uuid_8844" in gateway.idempotency_store

    # 2. Test The Naive Retry Anti-Pattern (What an amateur UI does)
    # The naive UI mints a brand new key upon clicking 'Try Again'
    naive_new_key = "op_uuid_9999"
    print("\n[Vulnerability] Naive UI mints a new key on 'Try Again':")
    naive_res = gateway.submit_task(client_key=naive_new_key, amount=120.0, simulate_ack_loss=False)
    print("  Naive Retry Result:", naive_res)
    # Catastrophic failure: Backend executed mutation TWICE (charged $240 instead of $120)
    assert gateway.mutation_counter == 2, "Naive retry caused double billing!"

    # 3. Test The Resilient Reconciliation Pattern (Production UI)
    # The client UI enters RECONCILING state, keeping the original active_operation_key
    print("\n[Resilient] Production UI retries using the STABLE client_operation_key:")
    client.is_reconciling = True

    # Retry using the original key
    reconciled_res = gateway.submit_task(
        client_key=client.active_operation_key,
        amount=120.0,
        simulate_ack_loss=False
    )
    print("  Reconciled Retry Result:", reconciled_res)

    # Invariants:
    # 1. Status is REPLAYED, not a new mutation
    assert reconciled_res["status"] == "REPLAYED"
    # 2. Mutation counter did NOT increment
    assert gateway.mutation_counter == 2
    # 3. Client captures the original task ID
    client.last_known_task_id = reconciled_res["task"]["task_id"]
    client.is_reconciling = False
    assert client.last_known_task_id == "task_0001"

    print("\nAll client operation idempotency and reconciliation invariants verified successfully.")


if __name__ == "__main__":
    main()
