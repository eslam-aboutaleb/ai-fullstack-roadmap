"""Durable Checkpointers, External Effect Separation, and Crash-Replay Idempotency.

Demonstrates:
1. Workflow Checkpoint vs Business Database Commit:
   - Checkpointers (e.g., PostgresSaver) commit internal graph channel values and superstep cursors.
   - They do NOT provide atomic distributed commits across third-party SaaS APIs or separate databases.
2. The Dual-Write Crash Gap & Node Replay:
   - Demonstrates a worker node executing an external side-effect (e.g., booking an airline seat)
     and crashing immediately before the checkpointer commits the step.
3. Durable Operation Key Reconciliation:
   - Upon restart, the checkpointer resumes and replays the interrupted node.
   - The node presents its deterministic idempotency key (`op_id`). The external service reconciles
     the existing reservation rather than creating a duplicate booking.
4. What Checkpoints Fail to Reveal:
   - A checkpoint indicates that the node never finished; only the downstream authoritative service
     can reveal whether the mutation actually succeeded.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional


@dataclass
class WorkflowCheckpoint:
    thread_id: str
    checkpoint_id: str
    current_node: str
    state_payload: Dict[str, Any]
    committed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ExternalBookingService:
    """Mock external third-party flight reservation API with idempotency tracking."""

    def __init__(self):
        self.reservations: Dict[str, Dict[str, Any]] = {}
        self.call_count: Dict[str, int] = {}

    def book_flight(self, idempotency_key: str, flight_number: str, passenger: str) -> Dict[str, Any]:
        self.call_count[idempotency_key] = self.call_count.get(idempotency_key, 0) + 1

        if idempotency_key in self.reservations:
            # Replay detected: Return existing reservation receipt without duplicate booking!
            return {
                "status": "RECONCILED_EXISTING",
                "confirmation": self.reservations[idempotency_key]["confirmation"],
                "replayed": True
            }

        confirmation = f"CONF-{flight_number}-{len(self.reservations) + 1}"
        record = {
            "confirmation": confirmation,
            "flight": flight_number,
            "passenger": passenger,
            "booked_at": datetime.now(timezone.utc).isoformat()
        }
        self.reservations[idempotency_key] = record
        return {
            "status": "NEWLY_COMMITTED",
            "confirmation": confirmation,
            "replayed": False
        }


class MockPostgresSaver:
    """Simulates durable PostgreSQL LangGraph checkpointer storage."""

    def __init__(self):
        self.storage: Dict[str, WorkflowCheckpoint] = {}

    def put(self, thread_id: str, checkpoint: WorkflowCheckpoint):
        self.storage[thread_id] = checkpoint

    def get(self, thread_id: str) -> Optional[WorkflowCheckpoint]:
        return self.storage.get(thread_id)


class FlightBookingWorkflow:
    """Workflow demonstrating the crash window between external mutation and checkpointer commit."""

    def __init__(self, checkpointer: MockPostgresSaver, booking_service: ExternalBookingService):
        self.checkpointer = checkpointer
        self.booking_service = booking_service

    def run_step_with_crash_simulation(
        self,
        thread_id: str,
        passenger: str,
        flight_number: str,
        crash_before_checkpoint: bool = False
    ) -> Dict[str, Any]:
        # Step 1: Check if prior checkpoint exists in checkpointer
        prior_cp = self.checkpointer.get(thread_id)
        if prior_cp:
            current_state = dict(prior_cp.state_payload)
            print(f"  [Resume] Resuming thread {thread_id} from checkpoint at node '{prior_cp.current_node}'")
        else:
            current_state = {"step": 0, "operation_key": f"op_{thread_id}_flight"}
            print(f"  [Start] Initializing new workflow for thread {thread_id}")

        # Step 2: Pure deterministic calculation (replay-safe)
        current_state["step"] += 1
        operation_key = current_state["operation_key"]

        # Step 3: External side-effect (guarded with durable operation key!)
        booking_result = self.booking_service.book_flight(
            idempotency_key=operation_key,
            flight_number=flight_number,
            passenger=passenger
        )
        current_state["confirmation"] = booking_result["confirmation"]
        current_state["replayed"] = booking_result["replayed"]

        # Step 4: The Dual-Write Window! Simulate worker crash before checkpointer save
        if crash_before_checkpoint:
            print("  [CRASH] Worker process crashed BEFORE checkpointer could save state!")
            raise RuntimeError("CRASH_DURING_DUAL_WRITE_WINDOW")

        # Step 5: Successful checkpointer commit
        new_cp = WorkflowCheckpoint(
            thread_id=thread_id,
            checkpoint_id=f"cp_{current_state['step']}",
            current_node="book_flight_completed",
            state_payload=current_state
        )
        self.checkpointer.put(thread_id, new_cp)
        return current_state


def main():
    checkpointer = MockPostgresSaver()
    booking_api = ExternalBookingService()
    workflow = FlightBookingWorkflow(checkpointer, booking_api)

    thread_id = "thread_travel_772"
    print("1. Executing Node with Simulated Crash in Dual-Write Window:")
    try:
        workflow.run_step_with_crash_simulation(
            thread_id=thread_id,
            passenger="Alice Smith",
            flight_number="AA-100",
            crash_before_checkpoint=True  # Crash occurs AFTER external call but BEFORE checkpoint save!
        )
        assert False, "Should have crashed"
    except RuntimeError as err:
        print(f"  Caught expected crash: {err}")

    # Inspect state: The external service booked the seat, BUT the checkpointer has NO RECORD!
    op_key = f"op_{thread_id}_flight"
    assert op_key in booking_api.reservations, "External mutation succeeded before crash"
    assert checkpointer.get(thread_id) is None, "Checkpointer failed to commit step due to crash"
    print("  Authoritative external booking exists, but LangGraph checkpointer is empty!")

    # 2. Worker Fleet Replays the Node after Recovery
    print("\n2. Fleet Restarts and Replays Interrupted Node:")
    resumed_state = workflow.run_step_with_crash_simulation(
        thread_id=thread_id,
        passenger="Alice Smith",
        flight_number="AA-100",
        crash_before_checkpoint=False  # Succeeds this time
    )

    print("\nReplay Execution Result:")
    print(f"  Confirmation: {resumed_state['confirmation']}")
    print(f"  Replayed flag from service: {resumed_state['replayed']}")
    print(f"  External Service Calls for Key: {booking_api.call_count[op_key]}")
    print(f"  Total Unique Bookings in Database: {len(booking_api.reservations)}")

    # Assertions
    assert resumed_state["replayed"] is True, "Booking service must recognize the idempotent key"
    assert booking_api.call_count[op_key] == 2, "Node ran twice across crash/resume"
    assert len(booking_api.reservations) == 1, "Only ONE real booking must exist"
    assert checkpointer.get(thread_id) is not None, "Checkpointer has now committed step"

    print("\nDurable checkpointer dual-write reconciliation and effect idempotency verified successfully.")


if __name__ == "__main__":
    main()
