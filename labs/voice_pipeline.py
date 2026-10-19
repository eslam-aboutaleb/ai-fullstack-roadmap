"""Injected voice pipeline with synthetic adapters. No microphone or provider use."""
import asyncio
from typing import Protocol

class SpeechToText(Protocol):
    async def transcribe(self, audio: bytes) -> str: ...
class TextAgent(Protocol):
    async def answer(self, text: str) -> str: ...
class TextToSpeech(Protocol):
    async def synthesize(self, text: str) -> bytes: ...

async def voice_turn(audio, stt, agent, tts, cancelled):
    # Real capture needs utterance finalization, limits, privacy, and timeouts.
    text = await stt.transcribe(audio)
    if cancelled.is_set(): return None
    answer = await agent.answer(text)
    if cancelled.is_set(): return None
    speech = await tts.synthesize(answer)
    if cancelled.is_set(): return None
    return {"transcript": text, "answer": answer, "audio": speech}

class SyntheticAdapters:
    async def transcribe(self, audio): return "What are your hours?"
    async def answer(self, text): return "Synthetic office hours: 9 to 5."
    async def synthesize(self, text): return b"SYNTHETIC-NOT-REAL-AUDIO"

async def demo():
    adapter = SyntheticAdapters()
    result = await voice_turn(b"synthetic-input", adapter, adapter, adapter, asyncio.Event())
    assert result["transcript"] == "What are your hours?"
    assert result["audio"] == b"SYNTHETIC-NOT-REAL-AUDIO"
if __name__ == "__main__": asyncio.run(demo())
