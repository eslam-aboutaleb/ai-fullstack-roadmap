# Framework evaluation contract (#49)

Introduction: provider SDKs, retrieval frameworks, agent orchestration, and
MCP/A2A protocols solve different layers. Evaluate a controlled end-to-end
task with identical datasets, permitted tools, gold citations and retry policy.

Run python3 -B labs/framework_contract_compare.py. It compares three local
reference strategies under one typed Task/Outcome contract and rejects hidden
write effects or forbidden tool calls. The observed durations are fixture
timings only; do NOT publish them as LangChain/LlamaIndex/ADK/Agents SDK metrics.

Real comparative adapter acceptance: separately install pinned SDK versions,
implement exactly the canonical task, capture actual trace+token cost, verify
denied tools, malformed JSON, cancellation, state recovery and authenticated
tenant isolation. Repeat equal cold/warm measurements and disclose overhead,
dependency footprint and provider model consistency. These optional vendor
runs do not execute in static GitHub Pages or this offline PR.
