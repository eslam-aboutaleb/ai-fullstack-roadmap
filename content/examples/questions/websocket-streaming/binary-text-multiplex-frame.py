# /// script
# dependencies = []
# ///
"""
Multiplexing Raw Binary Audio and Typed JSON Control Frames over WebSockets.

Demonstrates:
1. Handling binary frames (raw PCM/Opus microphone chunks) alongside text frames.
2. Ingesting text control frames (interruptions, parameters, model configuration).
3. Immediate barge-in processing: receiving an interrupt text frame halts audio synthesis.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Union


class VoiceAgentWebSocketSession:
    """Handles multiplexed binary audio chunks and JSON text control frames."""

    def __init__(self) -> None:
        self.buffered_audio_pcm_bytes: bytearray = bytearray()
        self.active_generation_id: int = 1
        self.is_synthesizing: bool = True
        self.binary_frames_count: int = 0
        self.text_control_frames_count: int = 0
        self.interrupt_processed: bool = False

    def handle_incoming_frame(self, frame: Union[bytes, str]) -> Dict[str, Any]:
        # Branch 1: Binary Frame (Microphone audio chunk)
        if isinstance(frame, bytes):
            self.binary_frames_count += 1
            self.buffered_audio_pcm_bytes.extend(frame)
            return {"type": "AUDIO_BUFFERED", "bytes_received": len(frame)}

        # Branch 2: Text Frame (Typed JSON control message)
        if isinstance(frame, str):
            self.text_control_frames_count += 1
            payload = json.loads(frame)
            msg_type = payload.get("type")

            if msg_type == "interrupt":
                # User spoke or clicked interrupt (barge-in)
                target_gen = payload.get("generation_id")
                if target_gen == self.active_generation_id:
                    self.is_synthesizing = False
                    self.interrupt_processed = True
                    return {"type": "INTERRUPT_ACK", "status": "SYNTHESIS_HALTED"}

            return {"type": "CONTROL_ACK", "status": "PROCESSED"}

        raise ValueError("Unsupported WebSocket frame type")


def main() -> None:
    session = VoiceAgentWebSocketSession()

    # 1. User streams two chunks of raw PCM audio bytes (e.g. 16kHz 16-bit audio)
    pcm_chunk_1 = b"\x00\x1f\x2a\x4e" * 64
    pcm_chunk_2 = b"\x12\x34\x56\x78" * 64

    resp_1 = session.handle_incoming_frame(pcm_chunk_1)
    assert resp_1["type"] == "AUDIO_BUFFERED"

    resp_2 = session.handle_incoming_frame(pcm_chunk_2)
    assert resp_2["type"] == "AUDIO_BUFFERED"

    assert session.binary_frames_count == 2
    binary_audio_frames = session.binary_frames_count

    # 2. User emits an in-band JSON text frame to interrupt (barge-in)
    interrupt_frame = json.dumps({"type": "interrupt", "generation_id": 1})
    resp_3 = session.handle_incoming_frame(interrupt_frame)
    assert resp_3["type"] == "INTERRUPT_ACK"

    assert session.text_control_frames_count == 1
    text_control_frames = session.text_control_frames_count

    # Invariant: Synthesis was immediately halted upon receiving interrupt frame
    assert session.is_synthesizing is False
    assert session.interrupt_processed is True
    interrupt_handled = session.interrupt_processed

    print(
        f"Binary text multiplexing verified: binary_audio_frames={binary_audio_frames}, "
        f"text_control_frames={text_control_frames}, interrupt_handled={interrupt_handled}"
    )


if __name__ == "__main__":
    main()
