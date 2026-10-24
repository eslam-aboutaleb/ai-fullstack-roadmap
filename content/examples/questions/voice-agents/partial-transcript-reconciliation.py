"""Partial Transcript Reconciliation & Consequential Action Gating.

Demonstrates handling streaming Automatic Speech Recognition (ASR) hypotheses.
Ensures non-monotonic interim transcripts update UI captions speculatively but are
strictly gated from triggering irreversible tool actions until is_final=True.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ActionSafetyLevel(str, Enum):
    SPECULATIVE_READ = "speculative_read"  # Pre-fetching UI, live captions
    CONSEQUENTIAL_MUTATION = "consequential_mutation"  # Payments, order cancellations


@dataclass(frozen=True)
class AsrTranscriptEvent:
    utterance_id: str
    revision: int
    text: str
    is_final: bool
    confidence: float


@dataclass
class ToolExecutionResult:
    action: str
    executed: bool
    reason: str


class VoiceActionDispatcher:
    """Gates tool execution based on utterance finalization status and safety tier."""

    def __init__(self) -> None:
        self.live_ui_caption: str = ""
        self.executed_mutations: List[str] = []
        self.rejected_mutations: List[str] = []
        self.active_utterance_revisions: Dict[str, int] = {}

    def ingest_asr_event(
        self, event: AsrTranscriptEvent, requested_action: str, safety: ActionSafetyLevel
    ) -> ToolExecutionResult:
        # Invariant: Track monotonic revision per utterance
        last_rev = self.active_utterance_revisions.get(event.utterance_id, 0)
        if event.revision <= last_rev:
            return ToolExecutionResult(
                action=requested_action,
                executed=False,
                reason=f"STALE_ASR_REVISION: rev {event.revision} <= {last_rev}",
            )
        self.active_utterance_revisions[event.utterance_id] = event.revision

        # Speculative UI updates are permitted on interim transcripts
        self.live_ui_caption = event.text

        # Gate consequential mutations on utterance finalization
        if safety == ActionSafetyLevel.CONSEQUENTIAL_MUTATION:
            if not event.is_final:
                self.rejected_mutations.append(requested_action)
                return ToolExecutionResult(
                    action=requested_action,
                    executed=False,
                    reason="GATED_ON_INTERIM_TRANSCRIPT: Consequential actions require is_final=True",
                )

        # Finalized or speculative read: execute action
        if safety == ActionSafetyLevel.CONSEQUENTIAL_MUTATION:
            self.executed_mutations.append(requested_action)
        return ToolExecutionResult(
            action=requested_action,
            executed=True,
            reason=f"Executed with is_final={event.is_final}",
        )


def test_partial_transcript_reconciliation() -> None:
    dispatcher = VoiceActionDispatcher()

    # Scenario: User says "Cancel the order... [pause] ... actually do not cancel it!"
    # Interim Hypothesis 1 at t=300ms
    event_interim_1 = AsrTranscriptEvent(
        utterance_id="utt_user_101",
        revision=1,
        text="Cancel the order",
        is_final=False,
        confidence=0.78,
    )
    res_1 = dispatcher.ingest_asr_event(
        event_interim_1,
        requested_action="cancel_order_442",
        safety=ActionSafetyLevel.CONSEQUENTIAL_MUTATION,
    )

    # Invariant: Must NOT cancel order on interim hypothesis
    assert res_1.executed is False
    assert "GATED_ON_INTERIM_TRANSCRIPT" in res_1.reason
    assert dispatcher.live_ui_caption == "Cancel the order"
    assert len(dispatcher.executed_mutations) == 0

    # Interim Hypothesis 2 at t=700ms (user continued speaking: "wait do not")
    event_interim_2 = AsrTranscriptEvent(
        utterance_id="utt_user_101",
        revision=2,
        text="Cancel the order wait do not",
        is_final=False,
        confidence=0.85,
    )
    res_2 = dispatcher.ingest_asr_event(
        event_interim_2,
        requested_action="cancel_order_442",
        safety=ActionSafetyLevel.CONSEQUENTIAL_MUTATION,
    )
    assert res_2.executed is False
    assert dispatcher.live_ui_caption == "Cancel the order wait do not"
    assert len(dispatcher.executed_mutations) == 0

    # Finalized Transcript at t=1200ms: Polar opposite intent!
    event_final = AsrTranscriptEvent(
        utterance_id="utt_user_101",
        revision=3,
        text="Do not cancel the order keep it active",
        is_final=True,
        confidence=0.97,
    )
    res_final = dispatcher.ingest_asr_event(
        event_final,
        requested_action="keep_order_active",
        safety=ActionSafetyLevel.CONSEQUENTIAL_MUTATION,
    )

    # Now the finalized action is executed
    assert res_final.executed is True
    assert dispatcher.live_ui_caption == "Do not cancel the order keep it active"
    assert len(dispatcher.executed_mutations) == 1
    assert dispatcher.executed_mutations[0] == "keep_order_active"
    assert "cancel_order_442" not in dispatcher.executed_mutations

    print(
        f"Partial transcript reconciliation verified: interim_gated=True, "
        f"final_executed=True, executed_action='{dispatcher.executed_mutations[0]}'"
    )


if __name__ == "__main__":
    test_partial_transcript_reconciliation()
