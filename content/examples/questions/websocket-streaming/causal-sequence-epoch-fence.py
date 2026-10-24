# /// script
# dependencies = []
# ///
"""
Causal Sequence Horizons and Session Epoch Fencing Across WebSocket Reconnects.

Demonstrates:
1. Session Epoch Fencing: discarding in-flight delayed packets from older connection epochs.
2. Monotonic Client Sequence Horizons: discarding stale out-of-order commands.
3. Preventing state corruption when packets from a dropped socket arrive after reconnection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ClientCommandFrame:
    epoch: int
    client_seq: int
    action: str
    payload: Dict[str, Any]


class CausalOrderGateway:
    def __init__(self) -> None:
        self.current_epoch: int = 1
        self.last_committed_seq: int = 0
        self.committed_actions: List[str] = []

    def handle_reconnect(self) -> int:
        """Client opens new socket; server advances epoch to fence out previous connection."""
        self.current_epoch += 1
        return self.current_epoch

    def process_command(self, cmd: ClientCommandFrame) -> Tuple[bool, str]:
        # 1. Epoch Fencing Check
        if cmd.epoch < self.current_epoch:
            return False, f"FENCED: Command epoch {cmd.epoch} is older than current epoch {self.current_epoch}"

        # 2. Monotonic Sequence Horizon Check
        if cmd.client_seq <= self.last_committed_seq:
            return False, f"STALE: Command sequence {cmd.client_seq} <= last committed {self.last_committed_seq}"

        # 3. Commit mutation
        self.last_committed_seq = cmd.client_seq
        self.committed_actions.append(cmd.action)
        return True, "COMMITTED"


def main() -> None:
    gateway = CausalOrderGateway()

    # --- Phase 1: Client on Socket 1 (Epoch 1) dispatches Command 1 ---
    cmd_1 = ClientCommandFrame(
        epoch=1,
        client_seq=1,
        action="UPDATE_DRAFT_TEXT",
        payload={"text": "Initial proposal"},
    )
    ok_1, msg_1 = gateway.process_command(cmd_1)
    assert ok_1 is True
    assert gateway.last_committed_seq == 1

    # --- Phase 2: Socket 1 drops! Client reconnects on Socket 2 ---
    # Handshake advances server epoch to 2
    new_epoch = gateway.handle_reconnect()
    assert new_epoch == 2

    # Client dispatches Command 2 on new Socket 2 with Epoch 2 and Seq 2
    cmd_2 = ClientCommandFrame(
        epoch=2,
        client_seq=2,
        action="FINALIZE_AND_SUBMIT",
        payload={"text": "Final proposal"},
    )
    ok_2, msg_2 = gateway.process_command(cmd_2)
    assert ok_2 is True
    assert gateway.last_committed_seq == 2
    newer_command_committed = True

    # --- Phase 3: Pathological Delayed Packet from Socket 1 belatedly arrives ---
    # A delayed network packet containing an older command (Epoch 1, Seq 1) arrives NOW
    delayed_stale_cmd = ClientCommandFrame(
        epoch=1,
        client_seq=1,
        action="UPDATE_DRAFT_TEXT_REVERT",
        payload={"text": "Reverted old text"},
    )
    ok_delayed, msg_delayed = gateway.process_command(delayed_stale_cmd)

    # Invariant: Server fences out the old epoch and rejects the stale command!
    assert ok_delayed is False
    assert "FENCED" in msg_delayed
    delayed_stale_command_fenced = True

    # --- Phase 4: Duplicate sequence number in current epoch ---
    duplicate_cmd = ClientCommandFrame(
        epoch=2,
        client_seq=2,  # seq 2 already committed
        action="REPEAT_FINALIZE",
        payload={},
    )
    ok_dup, msg_dup = gateway.process_command(duplicate_cmd)
    assert ok_dup is False
    assert "STALE" in msg_dup
    duplicate_seq_rejected = True

    # Invariant: Only the two valid forward transitions are in committed history
    assert gateway.committed_actions == ["UPDATE_DRAFT_TEXT", "FINALIZE_AND_SUBMIT"]

    print(
        f"Causal sequence epoch fence verified: newer_command_committed={newer_command_committed}, "
        f"delayed_stale_command_fenced={delayed_stale_command_fenced}, "
        f"duplicate_seq_rejected={duplicate_seq_rejected}"
    )


if __name__ == "__main__":
    main()

