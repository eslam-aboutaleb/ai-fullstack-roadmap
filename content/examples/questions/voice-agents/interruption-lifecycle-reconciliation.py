"""Interruption Lifecycle Reconciliation: Audio Playback vs Durable Tool State.

Demonstrates decoupled lifecycle reconciliation during user barge-in. Proves that
stopping client audio playback does not automatically roll back committed backend
tool mutations, and handles in-flight tool cancellation vs post-commit compensation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ToolExecutionState(str, Enum):
    QUEUED = "queued"
    EXECUTING = "executing"
    COMMITTED = "committed"
    CANCELLED = "cancelled"


@dataclass
class AssistantTurnState:
    turn_id: str
    audio_playback_active: bool = False
    spoken_playhead_offset_sec: float = 0.0
    tool_name: Optional[str] = None
    tool_state: ToolExecutionState = ToolExecutionState.QUEUED
    tool_receipt_id: Optional[str] = None


class InterruptionLifecycleReconciler:
    """Manages audio playback boundaries and backend tool lifecycle reconciliation."""

    def __init__(self) -> None:
        self.active_turns: Dict[str, AssistantTurnState] = {}
        self.compensation_events: List[str] = []

    def start_assistant_turn(self, turn_id: str, tool_name: str) -> AssistantTurnState:
        turn = AssistantTurnState(turn_id=turn_id, audio_playback_active=True, tool_name=tool_name)
        self.active_turns[turn_id] = turn
        return turn

    def commit_tool_mutation(self, turn_id: str, receipt_id: str) -> None:
        turn = self.active_turns[turn_id]
        turn.tool_state = ToolExecutionState.COMMITTED
        turn.tool_receipt_id = receipt_id

    def handle_user_barge_in(
        self, turn_id: str, interrupt_playhead_sec: float
    ) -> Dict[str, Any]:
        """Triggered when user interrupts audio playback. Coordinates playback & tools."""
        turn = self.active_turns[turn_id]

        # 1. Stop audio playback immediately on local client device
        turn.audio_playback_active = False
        turn.spoken_playhead_offset_sec = interrupt_playhead_sec

        # 2. Reconcile tool status independently of audio playback
        if turn.tool_state in {ToolExecutionState.QUEUED, ToolExecutionState.EXECUTING}:
            # Tool has not committed yet -> Safe to cancel backend worker
            turn.tool_state = ToolExecutionState.CANCELLED
            return {
                "turn_id": turn_id,
                "audio_stopped": True,
                "tool_outcome": "cancelled_in_flight",
                "tool_committed": False,
                "compensation_required": False,
                "verbal_reply": "Cancelled the operation before it committed.",
            }

        elif turn.tool_state == ToolExecutionState.COMMITTED:
            # Tool ALREADY committed to the database!
            # Muting speaker CANNOT undo the transaction! Must trigger compensation workflow.
            self.compensation_events.append(
                f"Compensation required for committed receipt {turn.tool_receipt_id}"
            )
            return {
                "turn_id": turn_id,
                "audio_stopped": True,
                "tool_outcome": "reconciled_committed",
                "tool_committed": True,
                "compensation_required": True,
                "receipt_id": turn.tool_receipt_id,
                "verbal_reply": (
                    f"I stopped speaking, but {turn.tool_name} was already confirmed under receipt "
                    f"{turn.tool_receipt_id}. Would you like me to execute a refund or cancellation?"
                ),
            }

        return {"turn_id": turn_id, "audio_stopped": True, "tool_committed": False}


def test_interruption_lifecycle_reconciliation() -> None:
    reconciler = InterruptionLifecycleReconciler()

    # Case 1: In-flight tool interrupted before commit
    turn_1 = reconciler.start_assistant_turn("turn_inflight", tool_name="book_hotel_room")
    assert turn_1.tool_state == ToolExecutionState.QUEUED

    # User interrupts at 0.5s while tool is still pending
    res_1 = reconciler.handle_user_barge_in("turn_inflight", interrupt_playhead_sec=0.5)
    assert res_1["audio_stopped"] is True
    assert res_1["tool_outcome"] == "cancelled_in_flight"
    assert res_1["tool_committed"] is False
    assert res_1["compensation_required"] is False
    assert turn_1.tool_state == ToolExecutionState.CANCELLED

    # Case 2: Committed tool interrupted during confirmation audio playback!
    # Tool committed at backend at t=0.2s
    turn_2 = reconciler.start_assistant_turn("turn_committed", tool_name="reserve_flight_seat")
    reconciler.commit_tool_mutation("turn_committed", receipt_id="rec_flight_seat_902")
    assert turn_2.tool_state == ToolExecutionState.COMMITTED

    # User interrupts at 1.4s while agent is reciting booking confirmation audio
    res_2 = reconciler.handle_user_barge_in("turn_committed", interrupt_playhead_sec=1.4)

    # CRITICAL INVARIANT: Audio is stopped, but committed tool is NOT magically rolled back!
    assert res_2["audio_stopped"] is True
    assert res_2["tool_outcome"] == "reconciled_committed"
    assert res_2["tool_committed"] is True
    assert res_2["compensation_required"] is True
    assert "already confirmed under receipt rec_flight_seat_902" in res_2["verbal_reply"]
    assert len(reconciler.compensation_events) == 1

    print(
        f"Interruption lifecycle reconciliation verified: audio_stopped=True, "
        f"inflight_cancelled=True, committed_compensated=True, "
        f"receipt_preserved={res_2['receipt_id']}"
    )


if __name__ == "__main__":
    test_interruption_lifecycle_reconciliation()
