"""PCM Audio Frame Calculator & Network Buffer Budgeting.

Calculates uncompressed PCM audio byte throughput, samples per frame, and jitter
buffer sizing across audio configurations (e.g. 16kHz mono vs 48kHz stereo),
comparing raw PCM bandwidth with compressed Opus streams.
"""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class AudioStreamProfile:
    name: str
    sample_rate_hz: int
    channels: int
    bit_depth: int  # 16-bit or 24-bit


class AudioFrameCalculator:
    """Computes byte throughput and packet sizes for real-time streaming audio."""

    @staticmethod
    def calculate_throughput_bytes_per_sec(profile: AudioStreamProfile) -> int:
        bytes_per_sample = profile.bit_depth // 8
        return profile.sample_rate_hz * profile.channels * bytes_per_sample

    @staticmethod
    def calculate_frame_size(
        profile: AudioStreamProfile, frame_duration_ms: float
    ) -> Tuple[int, int]:
        """Returns (samples_per_frame, bytes_per_frame)."""
        duration_sec = frame_duration_ms / 1000.0
        samples_per_channel = int(profile.sample_rate_hz * duration_sec)
        total_samples = samples_per_channel * profile.channels
        bytes_per_sample = profile.bit_depth // 8
        total_bytes = total_samples * bytes_per_sample
        return total_samples, total_bytes

    @staticmethod
    def calculate_jitter_buffer_budget(
        profile: AudioStreamProfile, max_buffer_duration_ms: float
    ) -> int:
        """Returns max bytes needed to hold the declared jitter buffer duration."""
        throughput = AudioFrameCalculator.calculate_throughput_bytes_per_sec(profile)
        return int(throughput * (max_buffer_duration_ms / 1000.0))


def test_audio_frame_calculator() -> None:
    # Standard Conversational Telephony Profile: 16kHz, 16-bit, Mono PCM
    mono_16k = AudioStreamProfile(
        name="telephony_16k_mono",
        sample_rate_hz=16000,
        channels=1,
        bit_depth=16,
    )

    # 1. Byte throughput per second
    # 16000 * 1 * (16 / 8) = 32,000 bytes/sec
    throughput_16k = AudioFrameCalculator.calculate_throughput_bytes_per_sec(mono_16k)
    assert throughput_16k == 32000

    # 2. Standard real-time frame size (20ms)
    # Samples: 16000 * 0.02 = 320 samples
    # Bytes: 320 * 2 = 640 bytes
    samples_20ms, bytes_20ms = AudioFrameCalculator.calculate_frame_size(mono_16k, frame_duration_ms=20.0)
    assert samples_20ms == 320
    assert bytes_20ms == 640

    # 3. Jitter buffer budget for 250ms packet burst tolerance
    # 32000 * 0.25 = 8000 bytes
    buffer_budget = AudioFrameCalculator.calculate_jitter_buffer_budget(mono_16k, max_buffer_duration_ms=250.0)
    assert buffer_budget == 8000

    # 4. High-Fidelity Studio Profile: 48kHz, 24-bit, Stereo
    # 48000 * 2 * 3 = 288,000 bytes/sec
    studio_48k = AudioStreamProfile(
        name="studio_48k_stereo",
        sample_rate_hz=48000,
        channels=2,
        bit_depth=24,
    )
    throughput_studio = AudioFrameCalculator.calculate_throughput_bytes_per_sec(studio_48k)
    assert throughput_studio == 288000

    print(
        f"PCM audio frame calculator verified: throughput_16k={throughput_16k} B/s, "
        f"frame_20ms_bytes={bytes_20ms}, jitter_buffer_budget={buffer_budget} B"
    )


if __name__ == "__main__":
    test_audio_frame_calculator()

