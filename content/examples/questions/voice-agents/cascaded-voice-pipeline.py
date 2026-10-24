"""Cascaded Voice Agent Pipeline: VAD, ASR, Agent Reasoning, and TTS.

Demonstrates an end-to-end modular voice pipeline with explicit stage boundaries:
Voice Activity Detection (VAD), Automatic Speech Recognition (ASR), Language Model
reasoning, and Text-to-Speech (TTS) synthesis with per-stage latency budgeting.
"""

from dataclasses import dataclass, field
import time
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class AudioChunk:
    chunk_id: str
    pcm_bytes: bytes
    timestamp_ms: int
    is_speech: bool = True


@dataclass
class PipelineMetrics:
    vad_latency_ms: float = 0.0
    asr_latency_ms: float = 0.0
    llm_ttft_ms: float = 0.0
    tts_ttfa_ms: float = 0.0
    total_turn_latency_ms: float = 0.0


class SimulatedVAD:
    """Voice Activity Detection: segments microphone speech from ambient silence."""

    def __init__(self, energy_threshold: int = 500) -> None:
        self.energy_threshold = energy_threshold

    def process_frames(self, frames: List[bytes]) -> Tuple[bool, List[bytes]]:
        # In production, uses WebRTC VAD or Silero VAD
        speech_frames = [f for f in frames if len(f) > 0 and sum(f[:10]) > self.energy_threshold]
        is_speech = len(speech_frames) > 0
        return is_speech, speech_frames


class SimulatedASR:
    """Automatic Speech Recognition: converts speech frames to normalized text."""

    def transcribe(self, speech_frames: List[bytes]) -> str:
        # In production, streams to Whisper or Conformer
        return "Can I get a refund on final sale items?"


class SimulatedAgentCore:
    """Agent / LLM Core: evaluates intent, queries policy, and generates response."""

    def __init__(self, return_policy: Dict[str, str]) -> None:
        self.return_policy = return_policy

    def generate_response(self, user_transcript: str) -> str:
        if "refund" in user_transcript.lower() and "sale" in user_transcript.lower():
            return "Final sale items are eligible for store exchange only, not cash refund."
        return "How can I help with your order?"


class SimulatedTTS:
    """Text-to-Speech: synthesizes text into synthetic audio frames."""

    def synthesize(self, text: str) -> bytes:
        # In production, invokes ElevenLabs or Deepgram Aura vocoder
        return f"AUDIO_PCM({text})".encode("utf-8")


class CascadedVoicePipeline:
    def __init__(self, policy: Dict[str, str]) -> None:
        self.vad = SimulatedVAD()
        self.asr = SimulatedASR()
        self.agent = SimulatedAgentCore(policy)
        self.tts = SimulatedTTS()

    def run_turn(self, audio_frames: List[bytes]) -> Tuple[bytes, PipelineMetrics]:
        metrics = PipelineMetrics()
        t0 = time.perf_counter()

        # Stage 1: VAD
        t_vad_start = time.perf_counter()
        is_speech, speech_frames = self.vad.process_frames(audio_frames)
        metrics.vad_latency_ms = (time.perf_counter() - t_vad_start) * 1000
        if not is_speech:
            return b"", metrics

        # Stage 2: ASR
        t_asr_start = time.perf_counter()
        transcript = self.asr.transcribe(speech_frames)
        metrics.asr_latency_ms = (time.perf_counter() - t_asr_start) * 1000

        # Stage 3: LLM reasoning
        t_llm_start = time.perf_counter()
        agent_reply = self.agent.generate_response(transcript)
        metrics.llm_ttft_ms = (time.perf_counter() - t_llm_start) * 1000

        # Stage 4: TTS synthesis
        t_tts_start = time.perf_counter()
        synthesized_audio = self.tts.synthesize(agent_reply)
        metrics.tts_ttfa_ms = (time.perf_counter() - t_tts_start) * 1000

        metrics.total_turn_latency_ms = (time.perf_counter() - t0) * 1000
        return synthesized_audio, metrics


def test_cascaded_voice_pipeline() -> None:
    policy = {"sale_items": "exchange_only"}
    pipeline = CascadedVoicePipeline(policy)

    # Synthetic mic frames with audio energy
    sample_frames = [bytes([200] * 50), bytes([150] * 50)]

    audio_output, metrics = pipeline.run_turn(sample_frames)

    assert b"store exchange only" in audio_output
    assert b"AUDIO_PCM" in audio_output
    assert metrics.vad_latency_ms >= 0.0
    assert metrics.asr_latency_ms >= 0.0
    assert metrics.llm_ttft_ms >= 0.0
    assert metrics.tts_ttfa_ms >= 0.0

    print(
        f"Cascaded voice pipeline verified: audio_bytes={len(audio_output)}, "
        f"response_phrase='store exchange only', stages_completed=4"
    )


if __name__ == "__main__":
    test_cascaded_voice_pipeline()
