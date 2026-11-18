<!-- chapter: model-engineering -->

# What mathematical foundations should an AI full-stack engineer learn first?

<!-- meta
domain: operations
subdomain: model-engineering
module: model-engineering
concept: What mathematical foundations should an AI full-stack engineer learn first
difficulty: implementation
misconception_target: Treating a library training run as a substitute for probability, gradients and valid evaluation
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Learn vectors, norms, dot products, probability, conditional probability, cross-entropy, optimization, and basic statistics. Connect them to retrieval geometry, training, calibration, and evaluation rather than memorizing formulas without a system consequence.

## Spoken Summary

Begin with vectors/matrices and shapes, probability and conditional reasoning, derivatives/chain rule, optimization, loss functions and data-split/evaluation design. Use small verified calculations before relying on library training loops. These foundations explain representation, uncertainty and failure modes in model systems.

## Why

Practice vector arithmetic, dot products, probability, gradients, and optimization with small executable examples. Connect each operation to embeddings, attention, training objectives, and inference instead of memorizing terms alone.

## Production Case

A classifier reports excellent held-out accuracy because preprocessing fitted on the entire dataset. Rebuild the pipeline with training-only fitting and compare grouped/time-aware validation before changing the model.

## Risk

A number can look authoritative while measuring the wrong event. Similarity is not truth probability, and judge agreement is not calibrated decision confidence.

## Trade-off

API skills enable quick prototypes; foundations improve diagnosis. Alternate practical exercises with theory.

## Try This

Compute normalized similarity by hand and estimate uncertainty in a small benchmark. Explain what each number establishes.

## Execution Timeline

Define variables/shapes -> calculate loss -> derive gradient -> test derivative -> optimize -> evaluate on independent data

## Complexity

The scalar example is constant-size; real training cost depends on tensor shapes, architecture, data and hardware. Gradient correctness is separate from generalization.

## Definitions

- **Gradient**: A vector of local derivatives of an objective with respect to parameters.
- **Conditional probability**: A probability defined under additional information and explicit population assumptions.
- **Data leakage**: Evaluation gains caused by information unavailable under the intended deployment boundary.

## Alternatives

- Full precision model
- Knowledge distillation

## Pitfalls

- No lineage record
- Quantization without evaluation
- Deploying without reliability testing

## Follow-ups

### What does a gradient check establish?

It compares an implemented derivative to a numerical approximation near chosen inputs; it does not prove the dataset, optimization process or model generalization is correct.

## Example

> Explanation: A single-parameter example makes the derivative and update visible before using an autodiff library.
> Output: 0.04

```python
x, y, w, learning_rate = 2.0, 3.0, 1.0, 0.1
gradient = 2 * x * (w*x-y)
w -= learning_rate * gradient
print(round((w*x-y)**2, 2))
```

## Citations

- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- https://scikit-learn.org/stable/common_pitfalls.html

# How do calibration and selective answering differ from ranking?

## Answer

Ranking orders candidates; calibration relates predicted confidence to observed correctness; selective answering chooses when to abstain. Define correctness and harm before turning a score into a decision threshold.

## Why

Define correctness and error cost, calibrate scores on reviewed outcomes, and report accuracy alongside answer coverage. A high ranking score is not automatically a confidence probability.

## Risk

A threshold tuned only on answerable questions can accept unsupported claims. Rare severe errors require separate treatment from average accuracy.

## Trade-off

More abstention can improve reliability among answered cases while reducing coverage. Evaluate the risk-coverage relationship with reviewed labels.

## Try This

Plot answered fraction against error rate across candidate thresholds. Separate outages, missing facts, and inapplicable knowledge rules.

# What are hard negatives and why can domain retrieval need them?

## Answer

Hard negatives appear relevant but fail a material condition, such as gradual leakage versus a sudden burst. They test whether representation and reranking distinguish the condition the user's question depends on.

## Why

Use reviewed non-relevant examples that resemble the query to teach finer distinctions. Keep false negatives out of training and compare retrieval improvements on held-out domain tasks.

## Risk

Binary labels can incorrectly mark a controlling exclusion irrelevant. Distinguish supporting, contradicting, conditional, and unrelated evidence when the task requires it.

## Trade-off

Rich labels cost review effort and reveal meaningful limitations. Easy random negatives produce cheaper and often flattering scores.

## Try This

Build a query with a positive clause, exclusion, unrelated clause, and ambiguous condition. Evaluate candidate recall and evidence completeness separately.

# When should you adapt an embedding or reranker instead of changing the prompt?

## Answer

Adapt representation when evidence consistently fails candidate retrieval or ranking after extraction, chunking, and labeling are correct. Change answer policy when useful evidence arrives but generation ignores it or overservice requests.

## Why

Improve representation or ranking when the correct evidence consistently fails candidate recall or relevance ordering. Tune prompts when evidence is already correct and generation misuses it; evaluate each failure separately.

## Risk

Tiny-domain tuning can overfit visible questions and worsen rare exclusions or other languages. Training leakage can conceal the regression.

## Trade-off

Adaptation may improve difficult matching and adds training and migration cost. Structured metadata or deterministic routing can be cheaper.

## Try This

Classify twenty failures by the first stage losing correctness and justify adaptation only after simpler repairs fail.

# What do distillation and synthetic data add to a learning plan?

## Answer

Distillation trains a smaller system from a stronger teacher's signals. Synthetic data expands examples, paraphrases, or adversarial cases. Both require independent validation because confident teacher errors can be copied at scale.

## Why

Distillation transfers behavior from a stronger teacher under a defined objective. Synthetic data can broaden fixtures or training examples, but needs validation, diversity checks, provenance, and separation from held-out evaluation.

## Risk

Generated questions can mirror source wording and overstate generalization. Generated answers should not become gold labels without review.

## Trade-off

Synthetic expansion reduces annotation effort and can reduce diversity or amplify bias. Keep a reviewed core as the anchor.

## Try This

Generate toy paraphrases, review them, and compare held-out quality before and after using the accepted data.

# How do quantization, batching, and caching affect serving differently?

<!-- meta
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Begin with the request timeline.** A tokenizer emits input IDs. Prefill processes the prompt and computes per-layer attention key/value (KV) state. Autoregressive decoding generates subsequent tokens, one step at a time. A server must admit requests, allocate memory, schedule prefill/decode and stream data back. A fast model alone cannot compensate for head-of-line queueing, long prompts or a saturated GPU.

**Why the levers differ.** Weight quantization shrinks or changes arithmetic for model parameters; it does not automatically reduce runtime KV cache, activations or host overhead. Continuous batching admits newly arrived decode requests instead of waiting for a whole fixed batch to finish. Prefix caching reuses eligible, identical prefill results only under a valid prompt/model/permission cache key. Paged attention avoids requiring a contiguous cache allocation for each sequence. Each optimization changes a different bottleneck, so measure it separately.

**Memory calculation.** Simplified KV bytes = 2 × layers × KV heads × head dimension × live tokens × bytes per element × simultaneous sequences. With 32 layers, 8 KV heads, dimension 128, 4096 live tokens and 2-byte elements, one sequence requires 536,870,912 bytes = 512 MiB for the KV tensors alone. Eight such sequences imply ~4 GiB before model weights, transient activations, workspace, allocator fragmentation and headroom. Multi-query/grouped-query attention changes the KV head count; never infer fit from model parameter bytes alone.

**Scheduling experiment.** Run `python3 -B labs/inference_capacity.py`. Its bounded discrete-event toy scheduler measures queue delay and simulated first-token/completion steps for competing requests; it rejects sequences that exceed configured memory and checks a nearest-rank p99. These are **illustrative step counts, not real milliseconds**. A production benchmark requires the actual GPU, model, tokenizer, hardware driver and serving engine, warm/cold runs, concurrent request mixes, TTFT, TPOT/inter-token latency, end-to-end p50/p95/p99 and GPU memory high-water marks.

**Serving systems.** vLLM documents PagedAttention, continuous batching, chunked prefill and prefix caching. Hugging Face Text Generation Inference (TGI) exposes per-request and batch metrics; Hugging Face now calls TGI maintenance mode. Pin actual engine/model revision and verify which endpoint features are supported rather than assuming drop-in parity. References: https://docs.vllm.ai/en/latest/ and https://huggingface.co/docs/text-generation-inference/en/reference/metrics .

**Failure and recovery.** When a long prompt arrives in a near-full batch, admission delays first token for shorter requests. Raising batch size may improve throughput but worsen tail latency or trigger OOM. Apply explicit queue/memory budgets and cancellation cleanup, replay a measured workload, then evaluate quality after a precision or quantization change.

**Follow-up.** If throughput rises but the 99th-percentile time-to-first-token triples, do not call that an unqualified improvement: check request-length fairness, admission, cache hits, SLA slices and capacity limits and compare the same workload under each configuration.

## Why

Quantization, batching and caching target different resources; throughput alone can conceal queueing and tail-latency regressions.

## Risk

Cached answers may be stale after policy or permission changes. Aggressive batching can delay interactive requests, and quantization may change task quality.

## Trade-off

Optimizations reduce resources and add operational complexity. Measure successful task cost and tail latency rather than throughput alone.

## Try This

Run the offline scheduler with capacity one and two; compute KV memory on paper and explain why real GPU p99 must be measured separately.

## Follow-ups

### When throughput increases but p99 time-to-first-token deteriorates, what should serving engineers investigate first?

Inspect admission and queue wait per request-length/concurrency slice, token-budget saturation and prefix-cache hit rates. Compare the identical real workload under both schedulers, report TTFT/TPOT and memory peaks, and do not confuse toy step counts with GPU milliseconds.

## Citations

- https://docs.vllm.ai/en/latest/
- https://huggingface.co/docs/text-generation-inference/en/index
- https://docs.vllm.ai/en/latest/design/metrics/

# Why separate model quality from inference-system reliability?

## Answer

A capable model can fail through timeouts, rate limits, broken schemas, streaming errors, or unsupported settings. A reliable serving path can consistently deliver poor reasoning. Measure execution availability and behavioral quality separately.

## Why

Separate inference, tool, retrieval, queue, and network costs. Provider sampling settings and context size affect both quality and operational behavior, so version them with experiments.

## Risk

Replacing a model to fix a parser or transaction bug wastes effort and can introduce incompatibilities. More retries cannot repair consistently unsupported reasoning.

## Trade-off

Layered measurement requires instrumentation and identifies effective changes. One end-to-end score captures impact but does not locate cause.

## Try This

Create incidents in model, retrieval, tool, transport, database, and frontend categories. State which signal identifies each.

# How should experimentation record lineage and reproducibility?

## Answer

Record code and dependency revisions, corpus, source versions, chunking, profiles, prompts, generation settings, judge configuration, and execution mode. Keep case identity stable without assuming temporary chunk UUIDs never change.

## Why

Store model, prompt, context, data, code, and environment identifiers with measured outputs. Distinguish configured, observed, estimated, and unknown values in reports.

## Risk

Equal model names may hide provider changes. Broad dependency ranges or a context-proxy fallback can change metrics without an obvious application diff.

## Trade-off

Rich lineage costs metadata and supports meaningful comparison. A screenshot of one average is easier to share and cannot reproduce a result.

## Try This

Write a machine-readable experiment manifest distinguishing configured, observed, estimated, and unknown values.

# What advanced topics should follow the core journey?

<!-- meta
answer_format: conceptual
domain: fullstack-engineering
subdomain: model-engineering
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**After the core journey, study reproducible model releases, adaptation, inference scheduling and evaluation-linked operations through measured projects.** Add domain or multimodal specializations when a task justifies them, rather than collecting framework names. Each extension should identify prerequisites, a held-out success oracle, a failure case and the hardware or vendor boundary it actually exercised.

**A model release couples weights with the code and data contracts needed to interpret them.** Register the base/model revision, tokenizer, prompt/template, feature and embedding profiles, training-data lineage, evaluation set, adapter configuration and serving runtime. A weights filename or a registry entry marked Production is not evidence of quality, compatibility or authorization to use the data.

CI should validate source/schema contracts, execute bounded code examples, train or load the declared local reference where appropriate, and compare candidate against baseline on held-out cases. Prevent train/evaluation leakage by grouping duplicated entities or source documents across splits. A lower training loss can coexist with worse held-out quality or catastrophic forgetting. Keep fixed evaluation IDs and task-specific regression gates, not a leaderboard optimized by repeated tuning on the release set.

Serving introduces batching, queueing, token limits, cancellation, memory and concurrency constraints. Separate first-token latency from completion latency and report hardware/runtime/version when measuring performance. A local analytic capacity estimate or a tiny CPU model run cannot certify GPU production throughput. An adapter must be compatible with its exact base/tokenizer/template; reject a mismatch before loading or answering.

Promote an immutable release bundle only after compatibility, safety, quality and recovery checks. Roll out under an explicit exposure policy, watch request/attempt usage and per-slice failures, and retain a tested rollback path. Monitor source/data drift separately from model/runtime errors. The production course's scorecard and policy fixtures make the decision rules inspectable; optional real infrastructure exercises require their own execution evidence. Model registry, orchestration and telemetry systems support this process but do not supply the missing judgment or independent labels automatically.

## Why

A LoRA adapter is loaded with a tokenizer that assigns different IDs to the same text. The weights load successfully but behavior is invalid; the release bundle must bind tokenizer and base revisions, not only tensor shapes.

## Worked Case

A LoRA adapter is loaded with a tokenizer that assigns different IDs to the same text. The weights load successfully but behavior is invalid; the release bundle must bind tokenizer and base revisions, not only tensor shapes.

## Risk

A registry promotion can publish an incompatible or leaked evaluation result. Administrative status and green build metadata do not prove held-out task quality.

## Trade-off

Strict release bundles improve reproducibility but require artifact storage and compatibility maintenance. Hot-swapping loosely identified components is convenient until an incident cannot be reproduced.

## Try This

Use the local production scorecard and model requirements to define a release manifest. Mark each field as observed, derived or pending and show the rejection path for an incompatible tokenizer/template.

## Follow-ups

### What if the new model is faster but refuses more supported policy questions?

Treat latency and false refusal as separate acceptance dimensions. Compare paired held-out cases and declared thresholds; do not exchange a critical correctness regression for an unqualified average speed gain.

## Citations

- https://mlflow.org/docs/latest/ml/model-registry/
- https://sre.google/workbook/canarying-releases/

# What demonstrates completion of the full AI full-stack learning journey?

## Answer

Build and explain the path from source bytes to authorized evidence, conversational intent to validated tools, reviewed action to atomic commit, and measured behavior to deployment and recovery. Defend alternatives with observations rather than slogans.

## Why

Show an end-to-end application, evaluated outcomes, failure recovery, and defended decisions. Completion is demonstrated engineering ability rather than finishing a list of technology names.

## Risk

Familiarity from reading can exceed practical skill. Production service requests need real integration, security, load, and recovery evidence beyond static review.

## Trade-off

A sustained portfolio is slower than memorization and stronger evidence of competence. Finish one reliable product before adding orchestration layers.

## Try This

Deliver the capstone with a working assistant, held-out report, write tests, trace-privacy review, restore drill, and three defended architectural alternatives.

# How would you distinguish prefill, decode and queue bottlenecks in a real language-model serving benchmark?

<!-- meta
answer_format: conceptual
domain: inference
subdomain: model-engineering
difficulty: design
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-23
-->

## Answer

**A model-serving request has multiple clocks.** The client waits for admission to a server queue, prompt tokenization and prefill, first generated token, iterative decoding and network streaming. Time-to-first-token (TTFT) includes queue/preprocessing/prefill and the first decode step under the benchmark's precise timing convention; inter-token latency/TPOT describes generation cadence after the first token. Throughput counts requests or tokens per unit time over a declared workload. None of these alone characterizes interactive user experience; p95/p99 and differences by input/output length and concurrency matter.

**Measure real phases independently.** Pin the exact engine/commit (e.g., supported vLLM version), model/tokenizer checksum, GPU type and VRAM, precision, cache configuration, prompt/output length distribution, concurrency profile and warm/cold state. Record arrival/admission timestamp, queue wait, prefill duration, first token, each subsequent token and completion. Normalize the endpoint streaming and cancellation policy. Use a stable held-out prompt set and deterministic seed where supported, but don't assume identical generated lengths if the model or decoding changes.

**Capacity worked example.** A simplified grouped-query attention cache needs 2 × L × H_kv × d_head × T × bytes per scalar × live sequences. With 32 layers, 8 KV heads, head width 128, 4096 retained tokens and FP16 (2 bytes), one sequence consumes 536,870,912 bytes = 512 MiB of KV tensors, *before* weights, activations, allocator overhead and other workspace. Four equal sequences use roughly 2 GiB for their KV tensors in this simple accounting. A larger batch can raise generated tokens/s but also lengthen queue waiting, cause unfairness for short prompts or exceed VRAM.

**Failure analysis.** If output tokens/s improves but p99 TTFT triples, inspect queue saturation and prefill admission for long prompts rather than proclaiming victory. If TTFT is fine but TPOT degrades, investigate decode scheduling and memory bandwidth; if both are fine but final latency is poor, look at length, server buffering, transport or client rendering. Compare GPU metrics to the application success/error budget and real answer quality when changing precision or model. A CPU simulator reporting artificial steps is a valuable scheduling exercise, **not** a measured GPU benchmark.

## Why

Prefill, queueing and token-by-token decode have different memory, compute and latency costs; conflating them hides product regressions.

## Worked Case

Illustrative hypothetical comparison (not an executed benchmark): A candidate scheduler increases output throughput from 300 to 370 tokens/s while p99 TTFT grows from 700 ms to 2,200 ms under the same request mix. Compare admission and prefill traces, the interactive SLA and per-length slices before choosing either configuration.

## Risk

Treating simulated steps as milliseconds or reporting only throughput can mask p99 latency, capacity problems and real quality regressions.

## Trade-off

More simultaneous decode sequences may improve aggregate GPU utilization at the price of memory pressure, scheduler fairness and tail latency.

## Try This

Benchmark two pinned serving configurations with identical prompt-length mixes; report observed TTFT/TPOT and p99, request counts, VRAM high-water and correctness.

## Follow-ups

### Can you infer the performance of a real vLLM deployment from an offline CPU scheduling fixture?

No. The toy model verifies dimension/capacity invariants and a chosen discrete scheduling policy, not real CUDA kernels, tokenizer overhead, prefill compute or measured network streaming. Use actual hardware, engine and workload to report latency and memory.

## Citations

- https://docs.vllm.ai/en/latest/design/metrics/

# What belongs in a reproducible model release beyond a weight file?

<!-- meta
domain: operations
subdomain: model-engineering
module: model-engineering
concept: What belongs in a reproducible model release beyond a weight file?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: An adapter is deployed with the wrong tokenizer revision and still loads because tensor dimensions happen to match.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Record architecture/configuration, exact base and tokenizer, training or adaptation data provenance, dependency/toolchain versions, evaluation manifest and serving assumptions. Verify compatible reload and task behavior before promotion. Parameter count alone cannot predict target-hardware latency, cache memory or concurrent capacity.

Concrete engineering case: An adapter is deployed with the wrong tokenizer revision and still loads because tensor dimensions happen to match.

Boundary defense: No. It proves only a portion of the artifact contract. Check semantic compatibility, quality slices, authority and measured serving behavior.

## Spoken Summary

Record architecture/configuration, exact base and tokenizer, training or adaptation data provenance, dependency/toolchain versions, evaluation manifest and serving assumptions. Verify compatible reload and task behavior before promotion. Parameter count alone cannot predict target-hardware latency, cache memory or concurrent capacity.

## Why

Record architecture/configuration, exact base and tokenizer, training or adaptation data provenance, dependency/toolchain versions, evaluation manifest and serving assumptions. Verify compatible reload and task behavior before promotion. Parameter count alone cannot predict target-hardware latency, cache memory or concurrent capacity.

## Production Case

An adapter is deployed with the wrong tokenizer revision and still loads because tensor dimensions happen to match.

## Risk

An adapter is deployed with the wrong tokenizer revision and still loads because tensor dimensions happen to match.

## Trade-off

No. It proves only a portion of the artifact contract. Check semantic compatibility, quality slices, authority and measured serving behavior.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: model engineering**: Record architecture/configuration, exact base and tokenizer, training or adaptation data provenance, dependency/toolchain versions, evaluation manifest and serving assumptions.

## Alternatives

- No. It proves only a portion of the artifact contract. Check semantic compatibility, quality slices, authority and measured serving behavior.

## Pitfalls

- An adapter is deployed with the wrong tokenizer revision and still loads because tensor dimensions happen to match.

## Follow-ups

### Does a successful weight load establish release correctness?

No. It proves only a portion of the artifact contract. Check semantic compatibility, quality slices, authority and measured serving behavior.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "An adapter is deployed with the wrong tokenizer revision and still loads because tensor dimensions happen to match.",
  "required_decision": "Record architecture/configuration, exact base and tokenizer, training or adaptation data provenance, dependency/toolchain versions, evaluation manifest and serving assumptions"
}
```

## Citations

- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- https://scikit-learn.org/stable/common_pitfalls.html
- https://mlflow.org/docs/latest/ml/tracking/

# How do quantization and low-rank adaptation affect quality, memory and release compatibility?

<!-- meta
answer_format: conceptual
domain: operations
subdomain: model-engineering
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Quantization changes numerical representation and can reduce parameter storage or computation under supported kernels. Low-rank adaptation learns constrained updates to selected layers while retaining a base model. Neither guarantees faster end-to-end inference on every device or unchanged quality. Account for activation and cache memory, loading overhead and actual target hardware. Version the base model, tokenizer, adapter and quantization profile together, then evaluate important slices and reject incompatible combinations. A small mechanism exercise is not evidence of production-scale adaptation quality.

## Why

An adapter trained for one base revision may load structurally against another but change behavior unexpectedly. Require a compatible base identity and evaluate the assembled model rather than treating matching tensor shapes as sufficient.

## Worked Case

An adapter trained for one base revision may load structurally against another but change behavior unexpectedly. Require a compatible base identity and evaluate the assembled model rather than treating matching tensor shapes as sufficient.

## Risk

Parameter compression can leave attention-cache memory or latency as the dominant bottleneck.

## Trade-off

Measure the complete target workload before choosing a compression or adaptation method.

## Try This

Compare compatible and incompatible model manifests and state the unmeasured hardware limits.

## Citations

- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- https://scikit-learn.org/stable/common_pitfalls.html
- https://mlflow.org/docs/latest/ml/tracking/
