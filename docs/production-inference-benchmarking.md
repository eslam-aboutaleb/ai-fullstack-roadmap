# Production inference: local capacity exercise (issue #38)

**Introduction:** Prefill, decode and stream are separate service phases. A
correct serving benchmark must distinguish TTFT, inter-token latency, p99,
requests/s, generated tokens/s, prompt lengths, scheduler admission and
hardware/memory configuration.

Run: `python3 -B labs/inference_capacity.py`. Its numbers are **simulated
step counts**, NOT observed vLLM/TGI GPU performance or token latencies.

**GPU-ready independent experiment plan:** Pin exact serving engine commit,
model checksum, tokenizer and quantization/kernel revision, CUDA/driver
versions, GPU model, concurrency and prompt/output length histogram. Warm up
and record queue time, TTFT, TPOT/ITL, end-to-end p50/p95/p99, tokens/s,
GPU VRAM peak and quality regressions. Compare TGI / vLLM only on supported
models/features using the same workload and explicit cancellation handling.

Current official sources:
- https://docs.vllm.ai/en/latest/
- https://huggingface.co/docs/text-generation-inference/en/reference/metrics
- https://huggingface.co/docs/text-generation-inference/index

Hugging Face currently labels TGI **maintenance mode**. Treat exact product
feature matrices as version-sensitive. Neither Docker, CUDA, model weights
nor external APIs are prerequisites for this static GitHub Pages exercise.
