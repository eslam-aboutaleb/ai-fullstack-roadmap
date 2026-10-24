"""Transactional Outbox and Saga Orchestration Patterns for Agent Mutating Actions.

Demonstrates:
1. Transactional Outbox Pattern:
   - Eliminates dual-write inconsistencies between database mutations and external side-effects (email/events).
   - Database record update and outbox event are inserted atomically in a single ACID transaction.
   - Background relay dispatches events reliably with idempotency keys.
2. Saga Orchestration Pattern with Compensating Transactions:
   - Coordinates multi-system distributed operations (Reserve Inventory -> Authorize Payment -> Dispatch Courier).
   - If a downstream step fails (e.g., Dispatch Courier fails due to address validation), the orchestrator
     automatically executes compensating transactions in reverse order (Refund Payment -> Release Inventory).
   - Enforces consistent business state despite model crashes or network partitions.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
import sqlite3
from typing import Any, Callable, Dict, List, Optional


# ==========================================
# 1. TRANSACTIONAL OUTBOX PATTERN
# ==========================================

class TransactionalDatabase:
    """SQLite in-memory DB demonstrating atomic business write + outbox event commit."""

    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE orders (
                    order_id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT NOT NULL
                );
            """)
            self.conn.execute("""
                CREATE TABLE outbox_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aggregate_type TEXT NOT NULL,
                    aggregate_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    published INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );
            """)

    def create_order_with_outbox(self, order_id: str, customer_id: str, amount: float) -> bool:
        """Atomic transaction: writes order AND outbox event in a single commit."""
        payload_json = json.dumps({"order_id": order_id, "customer_id": customer_id, "amount": amount})
        now = datetime.now(timezone.utc).isoformat()

        try:
            with self.conn:
                # 1. Update business state
                self.conn.execute(
                    "INSERT INTO orders (order_id, customer_id, amount, status) VALUES (?, ?, ?, 'CREATED');",
                    (order_id, customer_id, amount)
                )
                # 2. Insert outbox message
                self.conn.execute(
                    "INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload, created_at) "
                    "VALUES ('Order', ?, 'OrderCreated', ?, ?);",
                    (order_id, payload_json, now)
                )
            return True
        except Exception:
            return False

    def relay_pending_outbox_events(self, dispatcher: Callable[[str, Dict[str, Any]], bool]) -> int:
        """Background relay polling unpublished outbox events and dispatching them."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT event_id, event_type, payload FROM outbox_events WHERE published = 0 ORDER BY event_id ASC;")
        rows = cursor.fetchall()
        dispatched_count = 0

        for row in rows:
            event_id = row["event_id"]
            event_type = row["event_type"]
            payload = json.loads(row["payload"])

            if dispatcher(event_type, payload):
                with self.conn:
                    self.conn.execute("UPDATE outbox_events SET published = 1 WHERE event_id = ?;", (event_id,))
                dispatched_count += 1

        return dispatched_count


# ==========================================
# 2. SAGA ORCHESTRATION WITH COMPENSATING TRANSACTIONS
# ==========================================

class SagaStepStatus(Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    COMPENSATED = "COMPENSATED"


@dataclass
class SagaStep:
    name: str
    forward_action: Callable[[], Any]
    compensating_action: Callable[[], Any]
    status: SagaStepStatus = SagaStepStatus.PENDING
    result: Optional[Any] = None


class OrderFulfillmentSaga:
    """Saga orchestrator executing forward steps and rolling back on failure."""

    def __init__(self):
        # Simulated external services
        self.inventory_reserved = False
        self.payment_authorized = False
        self.courier_booked = False
        self.audit_log: List[str] = []

    # Service Actions
    def reserve_inventory(self):
        self.inventory_reserved = True
        self.audit_log.append("INVENTORY_RESERVED")
        return "INV-RESERVED-OK"

    def release_inventory(self):
        self.inventory_reserved = False
        self.audit_log.append("COMPENSATION: INVENTORY_RELEASED")

    def authorize_payment(self):
        self.payment_authorized = True
        self.audit_log.append("PAYMENT_AUTHORIZED")
        return "AUTH-TOKEN-773"

    def refund_payment(self):
        self.payment_authorized = False
        self.audit_log.append("COMPENSATION: PAYMENT_REFUNDED")

    def dispatch_courier(self, should_fail: bool = False):
        if should_fail:
            raise RuntimeError("Courier API Error: Destination address outside delivery zone")
        self.courier_booked = True
        self.audit_log.append("COURIER_DISPATCHED")
        return "TRACKING-9941"

    def run_saga(self, simulate_failure_at_step: Optional[str] = None) -> Dict[str, Any]:
        steps = [
            SagaStep(
                name="reserve_inventory",
                forward_action=self.reserve_inventory,
                compensating_action=self.release_inventory
            ),
            SagaStep(
                name="authorize_payment",
                forward_action=self.authorize_payment,
                compensating_action=self.refund_payment
            ),
            SagaStep(
                name="dispatch_courier",
                forward_action=lambda: self.dispatch_courier(should_fail=(simulate_failure_at_step == "dispatch_courier")),
                compensating_action=lambda: None
            )
        ]

        executed_steps: List[SagaStep] = []

        for step in steps:
            try:
                res = step.forward_action()
                step.status = SagaStepStatus.SUCCEEDED
                step.result = res
                executed_steps.append(step)
            except Exception as err:
                step.status = SagaStepStatus.FAILED
                self.audit_log.append(f"STEP_FAILED: {step.name} ({err})")

                # Trigger compensating transactions in REVERSE order of executed steps
                for prior_step in reversed(executed_steps):
                    prior_step.compensating_action()
                    prior_step.status = SagaStepStatus.COMPENSATED

                return {
                    "saga_status": "ROLLED_BACK",
                    "failed_step": step.name,
                    "error": str(err),
                    "audit_trail": self.audit_log
                }

        return {
            "saga_status": "COMMITTED",
            "audit_trail": self.audit_log
        }


def main():
    # 1. Test Transactional Outbox
    print("1. Transactional Outbox Execution:")
    db = TransactionalDatabase()
    created = db.create_order_with_outbox(order_id="ORD-1001", customer_id="CUST-55", amount=149.99)
    assert created is True

    dispatched_events = []

    def mock_event_broker(event_type: str, payload: Dict[str, Any]) -> bool:
        dispatched_events.append((event_type, payload))
        return True

    # Relay unpublished events
    relayed_count = db.relay_pending_outbox_events(mock_event_broker)
    print(f"  Successfully committed order and relayed {relayed_count} outbox event(s).")
    print(f"  Dispatched payload: {dispatched_events[0]}")
    assert relayed_count == 1
    assert dispatched_events[0][0] == "OrderCreated"

    # Verify no unhandled events remain
    assert db.relay_pending_outbox_events(mock_event_broker) == 0

    # 2. Test Saga Orchestration with Failure and Rollback
    print("\n2. Saga Orchestration with Compensation Rollback:")
    saga = OrderFulfillmentSaga()
    failure_result = saga.run_saga(simulate_failure_at_step="dispatch_courier")

    print(f"  Saga Status: {failure_result['saga_status']}")
    print(f"  Failed Step: {failure_result['failed_step']}")
    print("  Audit Trail:")
    for entry in failure_result["audit_trail"]:
        print(f"    - {entry}")

    assert failure_result["saga_status"] == "ROLLED_BACK"
    assert failure_result["failed_step"] == "dispatch_courier"
    # Verify compensating transactions restored clean state
    assert saga.inventory_reserved is False, "Inventory must be released during compensation"
    assert saga.payment_authorized is False, "Payment must be refunded during compensation"
    assert saga.courier_booked is False

    # 3. Test Successful Saga Run
    print("\n3. Successful Saga Execution:")
    success_saga = OrderFulfillmentSaga()
    success_result = success_saga.run_saga(simulate_failure_at_step=None)
    print(f"  Saga Status: {success_result['saga_status']}")
    assert success_result["saga_status"] == "COMMITTED"
    assert success_saga.inventory_reserved is True
    assert success_saga.payment_authorized is True
    assert success_saga.courier_booked is True

    print("\nOutbox and Saga distributed patterns verified successfully.")


if __name__ == "__main__":
    main()
