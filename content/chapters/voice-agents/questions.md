<!-- chapter: voice-agents -->

# How does a cascaded voice pipeline differ from speech-to-speech?

## Answer

A cascaded system uses speech recognition, a text-based agent, and speech synthesis. A speech-to-speech model processes and generates audio more directly, with provider-specific capabilities.

## Why

Compare transcript control, latency, language support, observability, and tool integration. Evaluate the complete spoken conversation rather than only transcript quality.

## Risk

Direct audio generation can make textual audit and output filtering harder.

## Trade-off

Cascades add stage latency and offer clearer intermediate boundaries.

## Try This

Diagram both designs for the same support task and identify their dominant delays.

# What are ASR, STT, TTS, and VAD?

## Answer

ASR and STT refer to speech recognition or speech-to-text; TTS converts text to speech; VAD detects speech activity. They address different parts of a voice interaction.

## Why

VAD segments activity, recognition produces hypotheses, the agent resolves intent, and synthesis produces playback audio. Track timing and errors at each stage.

## Risk

VAD can confuse background noise with speech or clip quiet words.

## Trade-off

Separate components improve diagnosis and increase integration complexity.

## Try This

Record a noisy phrase and identify which stage first introduced an error.

# How should partial transcripts be handled?

## Answer

Treat partial recognition as revisable hypotheses. Only finalized or explicitly confirmed content should drive consequential actions.

## Why

Attach utterance IDs and revisions to transcript events and replace earlier hypotheses rather than appending them as independent facts.

## Risk

Acting on an unfinished phrase can invert intent when the user adds a negation.

## Trade-off

Waiting for finalization adds latency and improves intent stability.

## Try This

Stream I want to cancel followed by not the order, the reminder and inspect tool behavior.

# What is turn detection and why is it difficult?

## Answer

Turn detection decides when the user has finished speaking and when the agent should respond. Silence alone may reflect hesitation, language patterns, or network delay.

## Why

Combine acoustic activity with configurable timeouts and conversational signals. Let users correct premature interruptions.

## Risk

Overly aggressive endpointing can cut off names, numbers, or accessibility-related speech patterns.

## Trade-off

Longer waits improve completeness and increase perceived delay.

## Try This

Evaluate turn boundaries across slow speech, pauses, background noise, and multiple languages.

# How should barge-in and interruption work?

## Answer

When the user interrupts, stop or duck playback, cancel obsolete generation where possible, and update conversation state to reflect what was actually delivered.

## Why

Use generation IDs to reject stale audio after cancellation. Track played audio duration separately from generated audio.

## Risk

The agent may assume the user heard content that remained in a playback buffer.

## Trade-off

Precise interruption handling adds state and improves conversational control.

## Try This

Interrupt halfway through a confirmation and verify that no action is authorized by unplayed content.

# How should a voice agent confirm sensitive actions?

## Answer

Present the material parameters in a clear review and obtain a valid confirmation under the product's authorization policy. Recognition confidence alone is insufficient for consequential intent.

## Why

Bind confirmation to the exact operation and require a stronger authenticated channel when appropriate.

## Risk

Background speech, spoofed audio, or transcript errors can trigger false intent.

## Trade-off

Stronger confirmation adds friction and protects high-impact operations.

## Try This

Change an amount after spoken review and verify the old confirmation cannot execute it.

# How should audio latency be measured?

<!-- meta
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Latency is a timeline, not just a round-trip HTTP number.** In a cascaded voice agent, microphone capture, voice-activity detection (VAD), automatic speech recognition (ASR), final transcript decision, reasoning/tool calls, first synthesized speech and playback buffers contribute distinct delays. Track start-of-user-speech, end-of-turn, ASR-final, response decision, first synthesized audio, first audible playback and end-to-end time. Percentiles over task/concurrency/language slices reveal delays hidden by mean latency.

**Video adds a separate clock problem.** Video frames and audio samples often use different rational presentation timestamp (PTS) *timebases*. A frame PTS of 90,000 ticks with timebase 1/90,000 represents 1 second. Do not assume the Nth encoded video frame plays at N/frame_rate seconds when the source has variable frame rate, dropped frames, B-frames or discontinuities. Normalize times using presentation timestamps; decode order and display order can differ. An audio transcript has a start/end segment and speaker/channel identity; use explicit alignment to cite a video clip where both the words and visible event occurred.

**Worked alignment.** If a transcript says “driver opens door” during [1,3) seconds, the frame at 1 second and the one at 2 seconds are candidates for evidence, while the frame at 3 seconds is outside the half-open interval. A fixed two-second frame sampler could skip the moment of contact at 1 second; adaptive frame sampling or shot-boundary expansion may recover it at additional embedding and indexing cost. Temporal ordering is not causation: a model seeing a person near an object does not prove that person caused an action.

**Drift computation.** Let `offset_start = audio_time_start - video_time_start` and `offset_end = audio_time_end - video_time_end`. Drift over the segment is `offset_end-offset_start`. A 0.05-second initial offset that becomes a 1.0-second offset indicates 0.95 seconds of accumulated drift, not a constant synchronization offset. In production measure timing uncertainty, discontinuities, resampling and buffering; do not “fix” all drift by shifting every subtitle by one constant.

**Offline verification.** Run `python3 -B labs/video_temporal_alignment.py`. It models integer PTS with `fractions.Fraction`, uniform frame sampling, owner-scoped transcript alignment, exact segment citations and drift/invalid-time cases. It does **not** actually decode video, run FFmpeg, ASR, a VLM or a multimodal embedding model. Optional real-media exercises must pin codecs/FFmpeg and use source-owned or licensed media and verified timestamp results.

**Privacy, safety and follow-up.** A clip may expose bystanders/faces or injected subtitles; the source video remains lower-trust data, and access must be checked per asset. Prevent cross-owner retrieval even when a transcript semantically matches. **If the source is variable frame rate and two frames share an apparent index interval**, use their real PTS rather than synthetic frame numbers to ground citations; prove event recall by annotated intervals and report missing segments separately from hallucinated summaries.

## Why

AV pipelines contain multiple independent queues and clocks, so single-roundtrip metrics or frame-number approximations cannot establish synchronized temporal evidence.

## Risk

A fast model token metric can hide slow endpoint detection or playback buffering.

## Trade-off

More instrumentation increases complexity and identifies the real bottleneck.

## Try This

Run rational-PTS frame sampling, force a 0.95-second sync drift and verify clips cannot be cited from another owner.

## Follow-ups

### Why can using frame index divided by nominal FPS produce false temporal citations on variable-frame-rate video?

Encoded decode order and presentation times can differ, and frame durations need not be constant. Use each frame's rational presentation timestamp and source timebase, align transcript intervals on a common clock, and check dropped/discontinuous frames before claiming an event occurred in a cited clip.

## Citations

- https://ffmpeg.org/ffmpeg-formats.html

# How do WebRTC and WebSockets differ for voice?

## Answer

WebRTC provides media-oriented transport and real-time communication features; WebSockets provide a general ordered duplex channel. The best choice depends on client, provider, and infrastructure support.

## Why

Evaluate audio encoding, network behavior, media controls, authentication, and deployment complexity. Use short-lived credentials for direct client sessions when supported.

## Risk

A long-lived provider secret must not be embedded in browser code.

## Trade-off

WebRTC can suit interactive media while requiring signaling and session setup.

## Try This

Explain the credential flow for a browser-to-provider audio connection.

# How should voice privacy and accessibility be designed?

## Answer

Decide whether raw audio, transcripts, and derived summaries are retained, for how long, and who can access them. Provide a usable text alternative and visible recording state.

## Why

Minimize collection, redact sensitive content where appropriate, and evaluate speech quality across accents, noise, and assistive needs.

## Risk

Voice can reveal identity and sensitive traits beyond the spoken words.

## Trade-off

Reduced retention limits diagnosis and exposure.

## Try This

Design a deletion request that covers audio artifacts, transcripts, and searchable derivatives.

# How should voice agents be evaluated?

## Answer

Measure task completion, transcription errors affecting intent, interruption quality, unsafe actions, latency, and accessibility across representative speakers and conditions.

## Why

Use consented or synthetic fixtures and human listening review for aspects text metrics miss. Validate durable outcomes in sandbox services.

## Risk

Word error rate alone cannot measure whether the correct task was completed.

## Trade-off

Audio evaluation costs more and captures real interaction failures.

## Try This

Compare two agents on noisy numeric inputs, corrections, interruptions, and failed tool calls.

# How does real-time bidirectional audio streaming work in Voice AI agents, and why is WebRTC preferred over WebSockets for voice transport?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: voice-agents
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Real-time voice AI agents require full-duplex, low-latency audio transmission where latency spikes over 300ms break natural conversational rhythm.** In voice interactions, users expect conversational latency matching human standards (200–400ms). The choice of transport protocol directly dictates audio jitter, packet loss recovery, and end-to-end responsiveness.

**WebSockets over TCP: the head-of-line blocking trap.** WebSocket connections run over TCP. TCP is a reliable, ordered transport protocol: if a single audio packet is dropped due to transient Wi-Fi or cellular packet loss, TCP halts delivery of all subsequent audio frames while waiting for retransmission. This phenomenon—head-of-line (HOL) blocking—introduces 500ms–2000ms audio stutter and latency buffering, completely destroying conversational flow. Furthermore, WebSockets lack native browser echo cancellation and adaptive jitter buffering.

**WebRTC over UDP: the real-time standard.** WebRTC operates over UDP using Secure Real-Time Transport Protocol (SRTP). Key advantages: (1) Unordered, immediate delivery: if a packet drops, WebRTC drops it gracefully and plays forward audio using packet loss concealment (PLC) rather than halting the audio stream; (2) Built-in Browser Media Engines: WebRTC integrates hardware-accelerated Acoustic Echo Cancellation (AEC), Noise Suppression (NS), and Automatic Gain Control (AGC) directly in the browser; (3) Adaptive Jitter Buffers: dynamically adjusting buffer depths based on network congestion; and (4) Native Opus codec: dynamically adapting bitrate (6kbps to 64kbps) to network bandwidth.

## Why

A mobile user speaks to a voice agent over a spotty 4G connection. On WebSockets, packet loss causes audio buffering and a 3-second delay. On WebRTC, the audio remains continuous and clear with sub-250ms round-trip latency.

## Worked Case

A mobile user speaks to a voice agent over a spotty 4G connection. On WebSockets, packet loss causes audio buffering and a 3-second delay. On WebRTC, the audio remains continuous and clear with sub-250ms round-trip latency.

## Risk

WebRTC requires managing STUN/TURN traversal servers and ICE negotiation, introducing more complex infrastructure setup than simple WebSockets.

## Trade-off

WebSockets are simpler to deploy over standard HTTP/2 reverse proxies; WebRTC requires dedicated media server infrastructure (e.g. LiveKit, Pion) but delivers superior real-time conversational latency.

## Try This

Compare audio packet latency over a simulated 2% lossy network using a raw WebSocket stream vs WebRTC. Measure audio dropouts and latency drift.

## Follow-ups

### When is WebSockets acceptable in voice applications?

WebSockets are acceptable for backend server-to-server audio pipes (e.g. between an API gateway and an LLM audio provider over dedicated low-latency cloud VPC networks).

## Citations

- https://webrtc.org/getting-started/overview
- https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API

# How do Voice Activity Detection and turn-taking algorithms detect user end-of-turn without introducing unnatural conversation latency?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: voice-agents
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Detecting when a human speaker has finished their turn is the most critical and difficult timing challenge in conversational voice systems.** If the system cuts off the speaker too quickly, it interrupts the user mid-thought during a natural pause; if it waits too long, the awkward silence makes the agent feel sluggish and robotic.

**Energy-based VAD vs Neural VAD.** Traditional Voice Activity Detection (VAD) relied on energy thresholds (RMS volume) and zero-crossing rates. While fast, energy-based VAD fails in real-world environments: it is fooled by background keyboard clicks, traffic noise, and breathing sounds. Modern voice architectures deploy lightweight neural VAD models (such as Silero VAD) that process 30ms audio chunks in under 1ms on CPU, classifying human speech probability with high noise immunity.

**Turn-taking heuristics and semantic end-of-turn classifiers.** Neural VAD alone cannot distinguish between an intra-sentence pause (e.g., 'I want to buy a ticket to... [pause 600ms] ...Chicago') and a true end-of-turn. Production voice pipelines combine VAD with semantic analysis: (1) Dynamic silence thresholds: setting baseline silence timeout to 700ms, but reducing it to 300ms if the preceding words form a syntactically complete sentence with falling acoustic pitch; (2) Semantic turn-taking models: passing the real-time streaming speech-to-text transcript through a fast classification head to predict whether the utterance is semantically complete or continuing; and (3) Backchanneling: emitting subtle vocal acknowledgments ('mm-hmm', 'sure') during prolonged pauses to signal active listening without taking the turn.

## Why

A user pauses for 400ms while thinking of a flight date: 'I want to fly on... [400ms] ...Friday'. A naive 300ms VAD cuts the user off and answers: 'Where do you want to fly?', frustrating the user. A semantic turn-taker detects the sentence was incomplete and holds the turn.

## Worked Case

A user pauses for 400ms while thinking of a flight date: 'I want to fly on... [400ms] ...Friday'. A naive 300ms VAD cuts the user off and answers: 'Where do you want to fly?', frustrating the user. A semantic turn-taker detects the sentence was incomplete and holds the turn.

## Risk

A static silence threshold of 1000ms guarantees sluggish, frustrating conversations; a threshold of 300ms causes chronic user interruptions.

## Trade-off

Semantic turn-taking requires evaluating partial transcripts with an SLM, trading a few milliseconds of compute for natural, human-like conversation flow.

## Try This

Run Silero VAD on an audio recording containing speech with natural mid-sentence pauses. Adjust the silence timeout from 200ms to 800ms and observe where false turn-completions occur.

## Follow-ups

### How does acoustic pitch help detect end-of-turn?

In human speech prosody, a falling intonation pitch contour typically indicates a completed declarative statement, while a rising pitch signals a question or mid-clause continuation.

## Citations

- https://github.com/snakers4/silero-vad
- https://arxiv.org/abs/2204.00768

# How is Barge-in engineered in full-duplex voice pipelines to halt ongoing LLM generation and audio playback instantaneously?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: voice-agents
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Barge-in allows human speakers to interrupt an AI agent mid-sentence, instantly halting synthesized audio playback and ongoing model generation.** In natural human conversation, listeners interject or change their mind while the other party is speaking. In voice AI, if the user speaks while the agent is playing an answer, the agent must silence itself within 100ms; playing through user speech creates an unusable, disorienting experience.

**Acoustic Echo Cancellation (AEC) is the prerequisite.** Barge-in is technically impossible without Acoustic Echo Cancellation. When the agent speaks, the device speakers play loud audio into the physical room. The device microphone captures both the human's voice AND the agent's own loudspeaker audio. Without AEC, the VAD detects the agent's own voice as a human interruption, causing the agent to interrupt itself constantly! AEC uses adaptive digital filters to subtract the speaker output reference signal from the microphone input signal in real time, isolating the human's actual voice.

**The cancellation cascade.** Once AEC isolates the human voice and VAD detects genuine user speech during agent playback, the system triggers an immediate multi-tiered cancellation cascade: (1) Client audio buffer flush: the browser or mobile app immediately clears its audio playback queue, silencing output in under 50ms; (2) Audio generation halt: the client sends a `barge_in` cancellation frame over the WebSocket/WebRTC control channel; (3) Text-to-Speech (TTS) cancellation: the server terminates active audio synthesis workers; and (4) LLM generation cancellation: the server aborts the active LLM completion stream and appends a `[User interrupted here]` marker into the conversation history.

## Why

An agent begins reading a long 5-step return policy. At step 2, the user interrupts: 'Wait, I lost my receipt'. Barge-in instantly silences the agent, cancels the remaining policy synthesis, and immediately routes the LLM to address the missing receipt.

## Worked Case

An agent begins reading a long 5-step return policy. At step 2, the user interrupts: 'Wait, I lost my receipt'. Barge-in instantly silences the agent, cancels the remaining policy synthesis, and immediately routes the LLM to address the missing receipt.

## Risk

Incomplete echo cancellation causes the agent to trigger false-positive barge-in events on its own speech when volume is high or speaker reflections are intense.

## Trade-off

Barge-in requires real-time bi-directional cancellation signaling across frontend and backend, but is indispensable for natural conversational voice interfaces.

## Try This

Play audio from your computer speakers while speaking into the microphone. Inspect the microphone waveform with and without software Acoustic Echo Cancellation enabled.

## Follow-ups

### What should the agent record in conversational history when interrupted?

The transcript must record only the words the user actually heard before the interrupt occurred, followed by an interruption marker, ensuring future context reflects what was communicated.

## Citations

- https://webrtc.org/getting-started/overview
- https://en.wikipedia.org/wiki/Acoustic_echo_cancellation

# What are the latency bottlenecks in Voice-to-Voice pipelines, and how do native multimodal audio-to-audio models achieve sub-300ms response times?

<!-- meta
answer_format: conceptual
domain: agents
subdomain: voice-agents
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Cascaded voice architectures suffer from compounded latencies across three independent models, whereas native audio-to-audio foundation models collapse the pipeline into a single inference pass.** In traditional voice systems, handling a spoken query requires cascading three separate components: (1) Speech-to-Text (STT, e.g. Whisper): transcribing audio frames to text (150–400ms); (2) Large Language Model (LLM): streaming text tokens (300–800ms Time-to-First-Token); and (3) Text-to-Speech (TTS, e.g. ElevenLabs, Cartesia): synthesizing tokens back into audio waveforms (150–350ms).

**The Cascaded Latency Trap (800ms–2000ms).** Even with aggressive streaming optimizations (such as chunking LLM output into 3-word phrases before sending to TTS), total latency routinely exceeds 800ms–1500ms. Furthermore, cascaded pipelines strip emotional nuances, pauses, laughs, accents, and vocal inflection during the STT step: the LLM receives only flat ASCII text and generates flat text, losing rich acoustic context.

**Native Multimodal Audio-to-Audio architectures.** Native speech models (such as GPT-4o voice mode or Gemini 2.0 Live) eliminate text cascading entirely. The model architecture uses continuous audio tokenizers (e.g., SoundStream, EnCodec, or SNAC) that encode raw audio waveforms into discrete acoustic tokens. The transformer processes audio tokens directly into audio token outputs in a single autoregressive pass. This achieves: (1) Sub-300ms glass-to-glass latency, matching human conversational speed; (2) Preservation of paralinguistic features (emotion, tone, whispers, singing, and pacing); and (3) Native barge-in recognition directly inside the attention matrix.

## Why

A cascaded voice agent takes 1,400ms to respond to a customer question, making the conversation feel sluggish. A native audio-to-audio model responds in 280ms, laughing naturally at the customer's joke while answering.

## Worked Case

A cascaded voice agent takes 1,400ms to respond to a customer question, making the conversation feel sluggish. A native audio-to-audio model responds in 280ms, laughing naturally at the customer's joke while answering.

## Risk

Native audio models can be susceptible to novel audio jailbreaks (e.g. whispered commands, ultrasound frequencies) that bypass text-based content filters.

## Trade-off

Cascaded pipelines use modular, easily testable text components with transparent inspection; native audio models deliver human latency and prosody but require end-to-end multimodal infrastructure.

## Try This

Benchmark the component latencies of a local Whisper STT -> Llama-3 -> Kokoro TTS pipeline. Compare the sum of TTFT against a native audio streaming API endpoint.

## Follow-ups

### What is an audio codec token in neural audio models?

Audio codec tokens are discrete integer indices produced by residual vector quantization (RVQ) neural networks that compress continuous audio waveforms into compact, tokenized representations.

## Citations

- https://arxiv.org/abs/2402.08846
- https://arxiv.org/abs/2107.03312

# How should interruption be handled when a spoken answer and a tool effect are at different stages?

<!-- meta
domain: ai-rag
subdomain: voice-agents
module: voice-agents
concept: How should interruption be handled when a spoken answer and a tool effect are at different stages?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: The user interrupts confirmation playback after a booking has already committed. The client labels the booking cancelled because it stopped the audio.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Treat capture, recognition, reasoning, tool execution and playback as separate lifecycles. Stop or replace playback promptly under the interaction policy, but reconcile any tool effect independently. Retain timestamps and identities needed to understand partial transcripts without logging private audio by default.

Concrete engineering case: The user interrupts confirmation playback after a booking has already committed. The client labels the booking cancelled because it stopped the audio.

Boundary defense: No. It is an interaction event. A receiver-confirmed task or effect status must establish whether the business operation stopped or committed.

## Spoken Summary

Treat capture, recognition, reasoning, tool execution and playback as separate lifecycles. Stop or replace playback promptly under the interaction policy, but reconcile any tool effect independently. Retain timestamps and identities needed to understand partial transcripts without logging private audio by default.

## Why

Treat capture, recognition, reasoning, tool execution and playback as separate lifecycles. Stop or replace playback promptly under the interaction policy, but reconcile any tool effect independently. Retain timestamps and identities needed to understand partial transcripts without logging private audio by default.

## Production Case

The user interrupts confirmation playback after a booking has already committed. The client labels the booking cancelled because it stopped the audio.

## Risk

The user interrupts confirmation playback after a booking has already committed. The client labels the booking cancelled because it stopped the audio.

## Trade-off

No. It is an interaction event. A receiver-confirmed task or effect status must establish whether the business operation stopped or committed.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: voice agents**: Treat capture, recognition, reasoning, tool execution and playback as separate lifecycles.

## Alternatives

- No. It is an interaction event. A receiver-confirmed task or effect status must establish whether the business operation stopped or committed.

## Pitfalls

- The user interrupts confirmation playback after a booking has already committed. The client labels the booking cancelled because it stopped the audio.

## Follow-ups

### Can barge-in guarantee a remote cancellation?

No. It is an interaction event. A receiver-confirmed task or effect status must establish whether the business operation stopped or committed.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "The user interrupts confirmation playback after a booking has already committed. The client labels the booking cancelled because it stopped the audio.",
  "required_decision": "Treat capture, recognition, reasoning, tool execution and playback as separate lifecycles"
}
```

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API

# How do barge-in, echo, end-of-turn detection and committed tools interact?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: voice-agents
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Barge-in lets user speech interrupt current output, but stopping playback is different from stopping generation or reversing a committed tool. Voice activity detection estimates speech regions; it does not establish a complete intent, and echo from the assistant can trigger false activity without appropriate handling. Track input and output turns separately, define when partial transcripts become actionable and cancel or invalidate obsolete generation. Require a separate confirmation boundary where a misunderstood utterance would cause a consequential effect.

## Why

The user says 'wait, do not send' while the assistant is speaking. Stop audio promptly, but inspect whether a send operation was already accepted and report its real status rather than claiming that playback cancellation undid it.

## Worked Case

The user says 'wait, do not send' while the assistant is speaking. Stop audio promptly, but inspect whether a send operation was already accepted and report its real status rather than claiming that playback cancellation undid it.

## Risk

Executing from an unstable partial transcript can act on words the recognizer later revises.

## Trade-off

Lower perceived latency must be balanced against intent stability and effect safety.

## Try This

Test interruption before proposal, during synthesis and after authoritative tool acceptance.

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API
