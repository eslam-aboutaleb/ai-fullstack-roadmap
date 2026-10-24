"""Barge-In Interruption Controller & Generational Audio Fencing.

Demonstrates client-server coordination during user barge-in. Immediately clears
client audio output queues, aborts in-flight backend TTS generation, advances the
generation epoch to reject stale in-flight audio frames, and reconciles played text.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class AudioStreamFrame:
    frame_id: str
    generation_id: int
    pcm_payload: bytes
    sentence_offset: int
    total_sentences: int


class BargeInInterruptionController:
    """Coordinates playback cancellation and generational frame filtering."""

    def __init__(self) -> None:
        self.active_generation_id: int = 1
        self.client_playback_buffer: List[AudioStreamFrame] = []
        self.played_frames_history: List[AudioStreamFrame] = []
        self.dropped_stale_frames: List[AudioStreamFrame] = []
        self.backend_synthesis_cancelled: bool = False

    def enqueue_audio_frame(self, frame: AudioStreamFrame) -> bool:
        """Client receives an audio frame; accepts only if matching active generation."""
        if frame.generation_id != self.active_generation_id:
            # Reject and drop stale audio frames from previous interrupted generations!
            self.dropped_stale_frames.append(frame)
            return False
        self.client_playback_buffer.append(frame)
        return True

    def play_next_frame(self) -> Optional[AudioStreamFrame]:
        if self.client_playback_buffer:
            frame = self.client_playback_buffer.pop(0)
            self.played_frames_history.append(frame)
            return frame
        return None

    def trigger_barge_in(self) -> Dict[str, Any]:
        # 1. Purge client playback buffer (instant physical silence)
        purged_count = len(self.client_playback_buffer)
        self.client_playback_buffer.clear()

        # 2. Signal backend to abort in-flight TTS synthesis & LLM generation
        self.backend_synthesis_cancelled = True

        # 3. Advance active generation ID to fence out any in-transit network packets
        old_gen = self.active_generation_id
        self.active_generation_id += 1

        return {
            "purged_buffer_frames": purged_count,
            "backend_cancelled": True,
            "fenced_generation_id": old_gen,
            "new_active_generation_id": self.active_generation_id,
            "frames_user_actually_heard": len(self.played_frames_history),
        }


def test_barge_in_controller() -> None:
    controller = BargeInInterruptionController()
    assert controller.active_generation_id == 1

    # Assistant starts speaking Generation 1 (3 frames)
    f1 = AudioStreamFrame("f1", generation_id=1, pcm_payload=b"pcm_hello", sentence_offset=1, total_sentences=3)
    f2 = AudioStreamFrame("f2", generation_id=1, pcm_payload=b"pcm_world", sentence_offset=2, total_sentences=3)
    f3 = AudioStreamFrame("f3", generation_id=1, pcm_payload=b"pcm_confirm", sentence_offset=3, total_sentences=3)

    assert controller.enqueue_audio_frame(f1) is True
    assert controller.enqueue_audio_frame(f2) is True
    assert len(controller.client_playback_buffer) == 2

    # User hears frame 1
    played = controller.play_next_frame()
    assert played.frame_id == "f1"
    assert len(controller.client_playback_buffer) == 1

    # USER INTERRUPTS: Barge-in triggered!
    barge_receipt = controller.trigger_barge_in()

    assert barge_receipt["purged_buffer_frames"] == 1  # f2 was purged
    assert len(controller.client_playback_buffer) == 0  # Buffer cleared
    assert controller.active_generation_id == 2  # Epoch bumped
    assert controller.backend_synthesis_cancelled is True

    # Delayed frame f3 from Generation 1 arrives over the network after barge-in
    enqueued_stale = controller.enqueue_audio_frame(f3)
    # INVARIANT: Stale frame must be rejected by generational fence!
    assert enqueued_stale is False
    assert len(controller.dropped_stale_frames) == 1
    assert controller.dropped_stale_frames[0].frame_id == "f3"

    # New turn (Generation 2) frames arrive and are accepted cleanly
    f_new = AudioStreamFrame("f_new_01", generation_id=2, pcm_payload=b"pcm_how_can_i_help", sentence_offset=1, total_sentences=1)
    assert controller.enqueue_audio_frame(f_new) is True
    assert len(controller.client_playback_buffer) == 1

    print(
        f"Barge-in interruption controller verified: buffer_purged=True, "
        f"generation_advanced_to={controller.active_generation_id}, "
        f"stale_frames_dropped={len(controller.dropped_stale_frames)}, "
        f"new_turn_accepted=True"
    )


if __name__ == "__main__":
    test_barge_in_controller()
