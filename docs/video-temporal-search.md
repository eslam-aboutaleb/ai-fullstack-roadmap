# Video search, synchronization and multimodal grounding (issue #41)

Introduction: A video is not simply an unordered array of images.
Understand original presentation timestamps (PTS), timebases, variable frame
rate and audio-transcript segment clocks before retrieving clips or building
a video RAG answer.

Run: `python3 -B labs/video_temporal_alignment.py`.
This is a **synthetic timestamp fixture**, not decoded or generated video.

Core study path: sampling by PTS → adaptive/shot-aware sampling tradeoffs →
temporal event indexing and ordered reasoning → align ASR/transcript/time
ranges with frames → combine multimodal embeddings and source citations →
evaluate event localization, temporal recall, sync drift, subtitle-injection
safety and bystander privacy.

Optional practical FFmpeg work should use an explicit file supplied by the
learner, preserve PTS/timebases in sidecar manifests and verify expected
frame/clip ranges. Document codec and FFmpeg version before comparing results.
Do not blindly infer timestamps from integer frame indices or claim a real
multimodal video understanding model ran.

No hosted media processing, live video, private datasets or mandatory API
keys are required by the static course.
