"""Durable agent state persistence, crash recovery, and uncertain action reconciliation.

Demonstrates:
1. Two-phase mutation protocol: Recording durable PENDING intent before dispatching external side effects.
2. Crash recovery scanner: Identifying uncertain operations upon harness restart.
3. Authoritative reconciliation: Querying downstream service status using operation_id, avoiding blind mutation retries.
4. Exactly-once business semantics across process termination.
"""
from typing import Any, Dict, List, Optional
import json

class RemotePaymentGateway:
    def __init__(self):
        # Downstream ledger: operation_id -> transaction record
        self.committed_transactions: Dict[str, Dict[str, Any]] = {}

    def execute_charge(self, operation_id: str, account_id: str, amount: float) -> Dict[str, Any]:
        if operation_id in self.committed_transactions:
            # Idempotent replay
            return self.committed_transactions[operation_id]

        record = {
            "status": "COMMITTED",
            "operation_id": operation_id,
            "account_id": account_id,
            "amount": amount,
            "transaction_ref": f"tx_bank_{len(self.committed_transactions)+1:04d}"
        }
        self.committed_transactions[operation_id] = record
        return record

    def query_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        return self.committed_transactions.get(operation_id)

class DurableAgentHarness:
    def __init__(self, downstream_gateway: RemotePaymentGateway):
        self.gateway = downstream_gateway
        # Local durable operational database
        self.durable_log: Dict[str, Dict[str, Any]] = {}

    def stage_intent(self, task_id: str, operation_id: str, tool_name: str, parameters: Dict[str, Any]) -> None:
        """Phase 1: Persist durable intent before crossing network boundary."""
        self.durable_log[operation_id] = {
            "task_id": task_id,
            "operation_id": operation_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "status": "PENDING"
        }

    def mark_completed(self, operation_id: str, result: Dict[str, Any]) -> None:
        """Phase 2: Commit successful outcome to local state."""
        self.durable_log[operation_id]["status"] = "COMPLETED"
        self.durable_log[operation_id]["result"] = result

    def simulate_crash_and_recover(self) -> List[Dict[str, Any]]:
        """Crash recovery procedure executed upon harness restart."""
        reconciled_events = []

        # Scan for any operations left in PENDING state
        for op_id, op_record in self.durable_log.items():
            if op_record["status"] == "PENDING":
                # DO NOT RE-DISPATCH THE WRITE!
                # Instead, query the authoritative downstream system by operation_id
                remote_state = self.gateway.query_status(op_id)

                if remote_state and remote_state["status"] == "COMMITTED":
                    # Remote already committed the change! Reconcile local state without duplicating mutation.
                    op_record["status"] = "RECONCILED_COMMITTED"
                    op_record["result"] = remote_state
                    reconciled_events.append({
                        "operation_id": op_id,
                        "resolution": "RESOLVED_FROM_DOWNSTREAM",
                        "transaction_ref": remote_state["transaction_ref"]
                    })
                else:
                    # Downstream never received it; safe to re-dispatch or fail
                    op_record["status"] = "RECONCILED_ABORTED"
                    reconciled_events.append({
                        "operation_id": op_id,
                        "resolution": "UNCOMMITTED_SAFE_TO_RETRY"
                    })

        return reconciled_events

if __name__ == "__main__":
    gateway = RemotePaymentGateway()
    harness = DurableAgentHarness(gateway)

    # 1. Normal execution flow
    op_id_1 = "op_charge_user_101"
    harness.stage_intent("task_01", op_id_1, "charge_customer", {"account": "acc_42", "amount": 100.0})
    res1 = gateway.execute_charge(op_id_1, "acc_42", 100.0)
    harness.mark_completed(op_id_1, res1)
    assert harness.durable_log[op_id_1]["status"] == "COMPLETED"

    # 2. Crash Interleaving Scenario:
    # Harness writes intent to durable log
    op_id_2 = "op_charge_user_102"
    harness.stage_intent("task_02", op_id_2, "charge_customer", {"account": "acc_99", "amount": 500.0})

    # Gateway executes and commits the charge on the bank's ledger
    gateway.execute_charge(op_id_2, "acc_99", 500.0)

    # CRASH OCCURS HERE! (Network drops response or agent process is killed before calling mark_completed)
    # Notice: harness.durable_log[op_id_2]['status'] remains 'PENDING'!
    assert harness.durable_log[op_id_2]["status"] == "PENDING"
    assert len(gateway.committed_transactions) == 2

    # 3. Harness Restarts and Recovers
    reconciled = harness.simulate_crash_and_recover()
    assert len(reconciled) == 1
    assert reconciled[0]["operation_id"] == op_id_2
    assert reconciled[0]["resolution"] == "RESOLVED_FROM_DOWNSTREAM"
    assert reconciled[0]["transaction_ref"] == "tx_bank_0002"

    # Verified: Gateway did NOT execute duplicate charge!
    assert len(gateway.committed_transactions) == 2
    # Local state is now reconciled
    assert harness.durable_log[op_id_2]["status"] == "RECONCILED_COMMITTED"

    print("Durable action logging and crash reconciliation verified successfully.")
