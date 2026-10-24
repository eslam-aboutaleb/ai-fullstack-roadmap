"""Adaptive Turn Detection & End-of-Turn (EoT) Endpointing.

Demonstrates conversational turn detection comparing fixed acoustic silence timeouts
against multimodal semantic endpointing. Dynamically expands silence windows when
transcripts end in incomplete syntactic clauses, preventing premature cut-offs.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class TurnDetectionDecision:
    is_turn_complete: bool
    silence_observed_ms: int
    applied_threshold_ms: int
    reason: str


class AdaptiveTurnDetector:
    """Combines acoustic silence duration with syntactic completeness heuristics."""

    TRAILING_CONNECTORS = {"and", "to", "because", "or", "with", "the", "for", "in", "at"}

    def __init__(
        self,
        base_silence_ms: int = 450,
        extended_silence_ms: int = 1200,
        accessibility_mode: bool = False,
    ) -> None:
        self.base_silence_ms = base_silence_ms + (400 if accessibility_mode else 0)
        self.extended_silence_ms = extended_silence_ms + (600 if accessibility_mode else 0)

    def is_syntactically_incomplete(self, text: str) -> bool:
        words = text.strip().lower().split()
        if not words:
            return True
        last_word = words[-1].strip(".,?!")
        # Trailing connector or trailing incomplete list indicator
        return last_word in self.TRAILING_CONNECTORS or words[-1].endswith("...")

    def evaluate_turn(self, partial_text: str, silence_duration_ms: int) -> TurnDetectionDecision:
        incomplete = self.is_syntactically_incomplete(partial_text)
        threshold_ms = self.extended_silence_ms if incomplete else self.base_silence_ms

        if silence_duration_ms >= threshold_ms:
            return TurnDetectionDecision(
                is_turn_complete=True,
                silence_observed_ms=silence_duration_ms,
                applied_threshold_ms=threshold_ms,
                reason="THRESHOLD_MET: Speaker turn concluded",
            )
        else:
            return TurnDetectionDecision(
                is_turn_complete=False,
                silence_observed_ms=silence_duration_ms,
                applied_threshold_ms=threshold_ms,
                reason=(
                    f"AWAITING_SPEECH: Silence {silence_duration_ms}ms < {threshold_ms}ms "
                    f"({'extended for incomplete syntax' if incomplete else 'standard window'})"
                ),
            )


def test_adaptive_turn_detection() -> None:
    detector = AdaptiveTurnDetector(base_silence_ms=500, extended_silence_ms=1200)

    # 1. Complete sentence with 600ms silence
    # Standard threshold is 500ms -> turn is complete!
    text_complete = "Please book the standard shipping option."
    res_complete = detector.evaluate_turn(text_complete, silence_duration_ms=600)
    assert res_complete.is_turn_complete is True
    assert res_complete.applied_threshold_ms == 500

    # 2. Incomplete sentence with 600ms silence (user hesitated mid-clause)
    # A fixed 500ms detector would RUDELY cut the user off here!
    # Adaptive detector detects trailing 'to' and expands threshold to 1200ms -> holds turn open!
    text_incomplete = "Please ship this package to"
    res_incomplete = detector.evaluate_turn(text_incomplete, silence_duration_ms=600)
    assert res_incomplete.is_turn_complete is False
    assert res_incomplete.applied_threshold_ms == 1200
    assert "extended for incomplete syntax" in res_incomplete.reason

    # 3. User finishes hesitation and provides destination address after 1300ms
    res_extended_elapsed = detector.evaluate_turn(text_incomplete, silence_duration_ms=1300)
    assert res_extended_elapsed.is_turn_complete is True

    # 4. Accessibility mode expands thresholds for speech dysfluencies
    a11y_detector = AdaptiveTurnDetector(base_silence_ms=500, accessibility_mode=True)
    res_a11y = a11y_detector.evaluate_turn("Yes", silence_duration_ms=600)
    # 500 + 400 = 900ms threshold, so 600ms does NOT prematurely conclude turn
    assert res_a11y.is_turn_complete is False
    assert res_a11y.applied_threshold_ms == 900

    print(
        f"Adaptive turn detection verified: complete_detected={res_complete.is_turn_complete}, "
        f"hesitation_protected={not res_incomplete.is_turn_complete}, "
        f"extended_threshold={res_incomplete.applied_threshold_ms}ms"
    )


if __name__ == "__main__":
    test_adaptive_turn_detection()

