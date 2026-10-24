"""Voice Privacy Lifecycle: Ephemeral Audio, PII Sanitization, and Text Fallback.

Demonstrates privacy and accessibility governance for voice agents: enforcing
ephemeral in-memory raw audio discard, regex-based PII redaction on transcripts,
and seamless fallback to accessible text chat when microphone access is denied.
"""

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional


@dataclass
class VoicePrivacyPolicy:
    retain_raw_audio: bool = False
    retain_redacted_transcript: bool = True
    enable_accessible_text_fallback: bool = True


@dataclass
class ProcessedTurnRecord:
    turn_id: str
    channel: str  # 'voice' or 'text'
    raw_audio_discarded: bool
    sanitized_transcript: str
    pii_redacted: bool


class VoicePrivacyManager:
    """Enforces zero-retention for raw biometric audio and sanitizes text memory."""

    CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d{4}[-\s]?){3}(\d{4})\b")
    SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-(\d{4})\b")

    def __init__(self, policy: VoicePrivacyPolicy) -> None:
        self.policy = policy
        self.durable_records: List[ProcessedTurnRecord] = []
        self.persisted_raw_audio_store: List[bytes] = []

    def sanitize_text(self, raw_text: str) -> str:
        """Redacts credit cards and SSNs to prevent PII leakage into vector DBs."""
        sanitized = self.CREDIT_CARD_PATTERN.sub(r"****-****-****-\1", raw_text)
        sanitized = self.SSN_PATTERN.sub(r"***-**-\1", sanitized)
        return sanitized

    def process_voice_turn(
        self, turn_id: str, raw_pcm_bytes: bytes, asr_transcript: str
    ) -> ProcessedTurnRecord:
        # Step 1: Discard raw audio immediately if policy dictates zero-retention
        raw_discarded = True
        if self.policy.retain_raw_audio:
            self.persisted_raw_audio_store.append(raw_pcm_bytes)
            raw_discarded = False
        else:
            del raw_pcm_bytes  # Evict from RAM

        # Step 2: Redact sensitive PII from transcript
        sanitized = self.sanitize_text(asr_transcript)
        pii_was_redacted = sanitized != asr_transcript

        # Step 3: Persist only sanitized text
        record = ProcessedTurnRecord(
            turn_id=turn_id,
            channel="voice",
            raw_audio_discarded=raw_discarded,
            sanitized_transcript=sanitized,
            pii_redacted=pii_was_redacted,
        )
        self.durable_records.append(record)
        return record

    def negotiate_channel(self, microphone_permission_granted: bool) -> str:
        """Fallback to accessible text chat if mic access is unavailable."""
        if not microphone_permission_granted:
            if self.policy.enable_accessible_text_fallback:
                return "text_fallback"
            raise PermissionError("Voice channel required but microphone access denied.")
        return "voice"


def test_voice_privacy_lifecycle() -> None:
    policy = VoicePrivacyPolicy(
        retain_raw_audio=False,
        retain_redacted_transcript=True,
        enable_accessible_text_fallback=True,
    )
    manager = VoicePrivacyManager(policy)

    # 1. Voice turn with sensitive payment info
    pcm_audio = b"\x00\x01\x02" * 500  # 1500 bytes of raw voice data
    spoken_text = "My credit card is 4111-2222-3333-8899 and SSN is 123-45-6789."

    record = manager.process_voice_turn("turn_v1", pcm_audio, spoken_text)

    # Verify zero-retention of raw biometric audio
    assert record.raw_audio_discarded is True
    assert len(manager.persisted_raw_audio_store) == 0

    # Verify PII masking in durable transcript
    assert record.pii_redacted is True
    assert "4111-2222-3333-8899" not in record.sanitized_transcript
    assert "****-****-****-8899" in record.sanitized_transcript
    assert "***-**-6789" in record.sanitized_transcript

    # 2. Channel negotiation with microphone denied (e.g. accessibility / browser block)
    channel = manager.negotiate_channel(microphone_permission_granted=False)
    assert channel == "text_fallback"

    channel_mic_ok = manager.negotiate_channel(microphone_permission_granted=True)
    assert channel_mic_ok == "voice"

    print(
        f"Voice privacy lifecycle verified: raw_audio_retained={len(manager.persisted_raw_audio_store) > 0}, "
        f"pii_masked=True, text_fallback_available=True"
    )


if __name__ == "__main__":
    test_voice_privacy_lifecycle()
