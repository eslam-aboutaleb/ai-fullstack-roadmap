# /// script
# dependencies = []
# ///
"""
WebSocket Application-Layer Acknowledgments and Idempotent Reconnection Protocol.

Demonstrates:
1. Returning explicit application ACKs for consequential commands.
2. Handling network drops before ACK delivery.
3. Client reconnecting and querying or re-sending command with deterministic operation key.
4. Server returning cached execution receipt without duplicate side effects.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class CommandReceipt:
    operation_key: str
    action: str
    status: str
    receipt_id: str
    committed_at: float = field(default_factory=time.time)


class DurableCommandLedger:
    """Server-side durable idempotency ledger for WebSocket commands."""

    def __init__(self) -> None:
        self.ledger: Dict[str, CommandReceipt] = {}
        self.mutation_executions: int = 0

    def execute_command(self, op_key: str, action: str, payload: Dict[str, Any]) -> CommandReceipt:
        # Idempotency check: if already committed, return existing receipt without re-executing
        if op_key in self.ledger:
            return self.ledger[op_key]

        # Execute business mutation
        self.mutation_executions += 1
        receipt = CommandReceipt(
            operation_key=op_key,
            action=action,
            status="completed",
            receipt_id=f"receipt_{action}",
        )
        self.ledger[op_key] = receipt
        return receipt


def main() -> None:
    ledger = DurableCommandLedger()
    op_key = "op_checkout_8819"

    # --- Step 1: Client dispatches command on Socket 1 ---
    # Server commits mutation and creates receipt
    receipt_1 = ledger.execute_command(
        op_key=op_key,
        action="order_88",
        payload={"item": "Enterprise License", "qty": 1},
    )
    assert receipt_1.status == "completed"
    assert receipt_1.receipt_id == "receipt_order_88"
    assert ledger.mutation_executions == 1

    # --- Step 2: Network drop occurs before ACK frame reaches client ---
    # Client has not received the ACK, so it does not know if command succeeded

    # --- Step 3: Client reconnects on Socket 2 and replays command with same op_key ---
    receipt_2 = ledger.execute_command(
        op_key=op_key,
        action="order_88",
        payload={"item": "Enterprise License", "qty": 1},
    )

    # Invariant 1: Server returns the exact same completed receipt
    assert receipt_2.receipt_id == receipt_1.receipt_id
    assert receipt_2.status == "completed"

    # Invariant 2: Zero duplicate side effects executed!
    assert ledger.mutation_executions == 1, "Duplicate mutation occurred on reconnect replay!"
    duplicate_mutations = ledger.mutation_executions - 1

    print(
        f"WebSocket command ACK verified: status={receipt_2.status}, "
        f"receipt={receipt_2.receipt_id}, duplicate_mutations={duplicate_mutations}"
    )


if __name__ == "__main__":
    main()
