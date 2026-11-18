<!-- chapter: models -->

# How do AI, ML, DL, NLP, and GenAI relate?

<!-- meta
domain: foundations
subdomain: ml-basics
module: models
concept: How do AI, ML, DL, NLP, and GenAI relate
difficulty: foundations
misconception_target: All AI is the same thing
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Artificial Intelligence is the broad field of building systems that perform intelligent tasks. Machine Learning learns behavior from data. Deep Learning uses layered neural networks. Natural Language Processing concerns language tasks. Generative AI produces new outputs such as text. A RAG application combines these ideas with conventional data and backend engineering.

## Spoken Summary

AI is a broad field; ML learns from data, and deep learning uses multilayer neural models. NLP is a language-task area that can use ML, deep learning or other methods. Generative AI produces content and overlaps these areas. They are not one universally nested taxonomy, and generation is also prediction under a model.

## Why

The retrieval service can call learned embedding and reranking providers, but much of its code is deterministic orchestration, validation, indexing, and coordination. Understanding that division prevents attributing every system behavior to a neural model.

## Production Case

A language product uses a classifier for routing, embeddings for retrieval and a generative decoder for drafting. Each component needs an evaluation suited to its task rather than a single generic AI score.

## Risk

Acronyms can hide missing skills. Knowing how to call a model API is different from understanding representation learning, and understanding attention is different from securing a multi-tenant API.

## Trade-off

An AI full-stack engineer needs practical breadth and selective depth. Research-level model training is not required for every product, but model limitations must inform system design.

## Try This

Label each reference component as deterministic infrastructure, learned-model adapter, or application boundary. Explain why several components require more than one learning discipline.

## Execution Timeline

Data → Train model → Evaluate → Deploy → Monitor → Retrain

## Complexity

Conceptual, no computational complexity

## Definitions

- **AI**: Systems that perform tasks requiring intelligence
- **ML**: Systems that learn patterns from data
- **DL**: Multi-layer neural networks that learn representations
- **NLP**: Applying AI/ML/DL to natural language
- **GenAI**: Models that generate new content

## Alternatives

- Rule-based systems
- Traditional statistics

## Pitfalls

- Using GenAI for exact computation
- Expecting ML to work without data
- Confusing NLP with GenAI

## Follow-ups

### Is every NLP system a generative deep-learning model?

No. NLP includes classification, parsing, retrieval and rule-based systems as well as neural generation.

## Example

> Explanation: Shows the nested relationship between fields.
> Output: Conceptual taxonomy

```python
# Taxonomy, not executable evidence of set relationships.
# Deep learning is a subset of machine learning, which is part of AI.
# NLP includes both neural and non-neural techniques.
# Generative AI includes text, images, audio, and other modalities.
```

## Citations

- https://www.ibm.com/topics/artificial-intelligence

# What does attention compute, and why does context length matter?

## Answer

Scaled dot-product attention forms weights from queries and keys, then combines value vectors: softmax(QK-transpose divided by square-root d) times V. This lets token representations depend on other tokens. Standard dense attention has pairwise interactions whose work and memory grow quadratically with sequence length, though implementations vary.

## Why

A retrieval application supplies selected context rather than every document. the retrieval service's evidence budget controls that supplied material; it does not implement Transformer attention or determine a provider's internal serving architecture.

## Risk

A model accepting a long context does not guarantee equal use of every passage. More evidence can increase cost and distraction, so context limits and useful context are different concepts.

## Trade-off

Larger context can preserve more information while reducing the pressure to retrieve precisely. Retrieval remains useful for selection, access control, attribution, and cost even with long windows.

## Try This

Draw token-to-token attention for four tokens, then estimate how pair counts change when sequence length doubles.

# How are encoder embeddings, decoder generation, bi-encoders, and cross-encoders different?

## Answer

An embedding encoder maps text into a reusable representation. A decoder language model generates tokens conditioned on prior context. A bi-encoder embeds query and document separately for efficient comparison. A cross-encoder jointly processes a query-document pair for more detailed scoring.

## Why

The retrieval service's embedding interface fits reusable vector production, while the Reranker protocol permits more expensive pairwise relevance scoring. The application generator remains outside the ordinary search pipeline.

## Risk

A provider's model name or API endpoint does not prove which architecture or training objective it uses. Follow its documented task contract and validate retrieval quality rather than assuming all embeddings or rerankers are interchangeable.

## Trade-off

Separate encoding enables indexing documents once and searching quickly. Joint scoring spends more work per pair and often belongs after candidate retrieval.

## Try This

Estimate how many model computations are needed to retrieve from 100,000 documents using precomputed bi-encoder vectors versus scoring every pair with a cross-encoder.

# What is contrastive learning, and why does it matter for retrieval?

## Answer

Contrastive learning trains representations so relevant pairs score above irrelevant pairs. A common objective compares a query's positive passage with negatives using a softmax-based loss. Negative selection, label quality, and the task distribution shape what similarity means.

## Why

The retrieval service consumes pretrained embedding functions rather than training them. Understanding their objective helps explain why a general embedding may confuse domain-specific exceptions or why a specialized model improves some queries and harms others.

## Risk

False negatives can teach a model to separate two genuinely relevant passages. Training leakage can also inflate benchmark scores, and same-dimension models remain incompatible despite similar training goals.

## Trade-off

Domain adaptation can improve ranking but needs representative data, compute, evaluation, and a new index generation. Better query and chunk design may solve the problem more cheaply.

## Try This

Create one query, one positive passage, one easy negative, and one hard negative. Explain what an accidental false negative would teach.

# What are pretraining, SFT, and instruction tuning?

## Answer

Pretraining learns broad statistical structure from large datasets. Supervised Fine-Tuning trains on task examples or desired responses. Instruction tuning is supervised adaptation aimed at following instructions across tasks. These change model parameters; indexing new documents changes external knowledge storage instead.

## Why

The reference design does not include a model-training pipeline. Its datasets and answer evaluators support application evaluation, not an automatic SFT trainer. A host can use evaluation failures to decide whether behavior adaptation is warranted.

## Risk

Fine-tuning on private facts can create memorization and retention problems without solving freshness or citation. Poor examples can also teach confident unsupported answering.

## Trade-off

Behavior tuning may improve format and task consistency, while retrieval is usually more direct for changing private documents. Combining them requires separate evaluation of behavior and knowledge access.

## Try This

Divide twenty failures into missing evidence, bad ranking, bad prompt policy, and persistent behavioral problems. Choose which, if any, justify SFT.

# What are LoRA, PEFT, and quantization?

## Answer

Parameter-Efficient Fine-Tuning adapts a subset or compact parameterization instead of updating all weights. LoRA is one PEFT method that adds low-rank updates to frozen weights. Quantization represents weights or activations with reduced numerical precision; it addresses memory and compute rather than directly supplying new knowledge.

## Why

These methods belong to a different responsibility from retrieval orchestration. They belong to the model layer a host may select, while embedding-profile changes still require compatible indexing and evaluation.

## Risk

Reduced precision or adaptation can change quality, and an efficient technique is not automatically safe for every model or hardware target. Avoid promising universal speedups or equal accuracy.

## Trade-off

These methods can reduce adaptation or serving resources while adding tooling and compatibility considerations. Provider-hosted models transfer much of that operational work elsewhere.

## Try This

Compare full fine-tuning, LoRA adaptation, and quantized inference in a table of what changes, what stays frozen, and which evaluation is needed.

# How do RLHF and DPO differ from RAG?

## Answer

Reinforcement Learning from Human Feedback uses human preference information to shape model behavior, often through a learned reward and policy optimization. Direct Preference Optimization trains from preferred and rejected response pairs without the same explicit reinforcement-learning loop. RAG supplies external evidence at inference time.

## Why

These methods operate at different layers and can coexist. This reference design provides retrieval and evaluation components, not RLHF or DPO training. Its answer-quality failures may motivate better behavior data, but indexing is not preference optimization.

## Risk

Preferences can reward pleasing or verbose answers instead of faithful ones. A preference-trained model can still hallucinate, and a retrieved passage can still be wrong.

## Trade-off

Alignment training addresses behavioral tendencies and requires datasets and training infrastructure. Retrieval addresses access to evidence and requires corpus infrastructure. Neither replaces the other's evaluation.

## Try This

Write a preferred and rejected answer pair where the preference is justified by citation faithfulness. Explain what that pair teaches and what source freshness it cannot teach permanently.

# What are temperature, top-p, tokens, and structured output?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: models
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**An LLM API is a probabilistic computation behind a fallible transport.** A token is one unit in that model's tokenizer, not necessarily a word or character. Temperature rescales next-token logits before sampling; top-p retains a probability-mass prefix before sampling. Their interaction and supported ranges belong to the provider/version contract. A zero-temperature setting does not promise identical execution across hardware, provider revisions or tool choices. A structured-output constraint narrows representation; it does not establish truth, permission or citation support.

Start with an application-owned request: model revision/capability, messages, authenticated scope, deadline, input budget, maximum output, schema and logical request ID. The provider adapter translates that contract into supported parameters. Validate the returned object at runtime: exact keys, types, refusal/terminal state, source eligibility and business policy. Reject unsupported capabilities rather than silently ignoring them. Never treat model-generated tool arguments as authorization.

**Budget before each attempt.** With a 128-token fixture limit, 100 input tokens leave at most 28 output tokens; 29 fails before invocation. With 100 reserved tokens and 30 reserved per attempt, one rate limit followed by success reserves 60 and leaves 40. This is the conservative accounting in `llm_contracts.py`, not a statement about any provider invoice. Actual billing uses the provider's reported input/output/cache categories and dated rate catalog; missing usage remains unresolved rather than zero.

Retry a rate limit only within a total deadline/attempt budget, honoring a bounded Retry-After and adding jitter across a fleet. Do not retry invalid JSON, forbidden citations or business denial without an explicit repair policy. A timeout after a write is an unknown outcome: reconcile the receiver using the same operation identity. Measure logical requests separately from attempts so retries cannot hide cost amplification. Keep a local scripted adapter for tests; an optional live adapter needs secret injection outside source, model/version manifests and the same negative contract suite.

## Why

The local client receives one rate-limit failure and then scoped JSON. Reserving each attempt yields 40 tokens left; validating JSON alone would still accept a citation to another tenant without the second scope check.

## Worked Case

The local client receives one rate-limit failure and then scoped JSON. Reserving each attempt yields 40 tokens left; validating JSON alone would still accept a citation to another tenant without the second scope check.

## Risk

A fallback model can change schema or tool-call semantics. Treat capability mismatch and unknown billed usage explicitly rather than claiming success because some text arrived.

## Trade-off

Strict schemas make failure legible but may reject useful prose. Repair adds another cost and injection surface; bounded refusal can be the correct product behavior.

## Try This

Run python3 labs/llm_contracts.py. Reduce the allowance to 30, predict the attempt count, then add an unauthorized citation and demonstrate that it is rejected without another provider call.

## Follow-ups

### What changes when the provider supports cached input pricing?

Keep cached and uncached input counts separate and apply their dated rates. Do not subtract an estimated cache saving from every request; record reported usage and reconcile unknown attempts before releasing reserved budget.

## Citations

- https://json-schema.org/draft/2020-12/json-schema-validation
- https://www.rfc-editor.org/rfc/rfc6585.html

# What are HyDE, agentic RAG, GraphRAG, and multimodal RAG?

## Answer

HyDE retrieves using an embedding of a generated hypothetical answer or document. Agentic RAG lets a controller choose repeated retrieval or tool actions. GraphRAG adds graph relationships to retrieval or synthesis. Multimodal RAG includes non-text modalities. These are families of techniques, not automatically enabled project features.

## Why

Query-transform, strategy, tool-bridge, and extractor seams can support experiments, but a host must implement the actual controller, graph, modality representation, and evaluation. A source connector alone does not create multimodal reasoning.

## Risk

Each added generative or traversal step expands cost and failure modes. Hypothetical content can introduce invented facts; agents can loop; graph edges can be stale; modality extraction can lose evidence fidelity.

## Trade-off

Advanced methods can solve demonstrated complex cases while making the baseline harder to understand and operate. Add them incrementally with bounded execution.

## Try This

Pick one baseline failure and design the smallest extension that addresses it. Define a cost ceiling and a benchmark that could prove the extension unnecessary.

# How should an AI full-stack engineer learn deep learning alongside this reference design?

## Answer

Learn vectors and similarity first, then tokenization, neural training objectives, attention, model adaptation, and inference. Tie each topic to an observable product failure: incompatible vectors, poor paraphrase recall, context overflow, unsupported generation, or latency under load.

## Why

The code offers a concrete laboratory for interfaces around learned systems while keeping infrastructure inspectable. Training a small encoder or language model is a separate learning exercise that deepens understanding without requiring a rewrite of the retrieval subsystem.

## Risk

Studying only theory misses deployment and security; studying only APIs leaves model behavior mysterious. A portfolio should demonstrate both a measured model comparison and a robust application boundary.

## Trade-off

Breadth requires sustained practice. Sequence small, testable projects rather than attempting to master distributed storage and large-model training simultaneously.

## Try This

Follow the roadmap labs, then train a tiny contrastive encoder on a reviewed toy dataset. Compare it with the hashing baseline and a pretrained model using the same held-out queries.

# How do FlashAttention-2 and FlashAttention-3 achieve IO-awareness, and why does avoiding HBM read/writes yield a 2-4x speedup over standard attention?

<!-- meta
answer_format: conceptual
domain: machine-learning
subdomain: deep-learning
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**FlashAttention is an exact, IO-aware algorithm that computes scaled dot-product attention without materializing the intermediate $N \times N$ attention matrix in High Bandwidth Memory (HBM).** In standard attention implementations (such as native PyTorch naive attention), computing $\text{Softmax}(QK^T / \sqrt{d})V$ requires multiple round-trips to GPU global memory (HBM): first materializing the $N \times N$ logits matrix, writing it to HBM, reading it back to compute row-wise softmax max and sum normalization factors, writing normalized probabilities back to HBM, and finally reading them to multiply with $V$. For context lengths of 8k or 32k tokens, memory reads and writes scale quadratically ($O(N^2)$), causing compute units (Tensor Cores) to sit idle waiting for memory bandwidth (memory-bound bottleneck).\n\n**Tiling and Online Softmax in SRAM.** FlashAttention leverages the GPU's fast, on-chip Shared Memory (SRAM) by tiling the $Q$, $K$, and $V$ matrices into smaller blocks that fit completely within SRAM.

It uses the mathematical trick of *Online Softmax* (Milakov & Gimelshein, 2018): as new tiles of $K$ and $V$ are streamed from HBM into SRAM, FlashAttention maintains running row-maxima and normalization denominators. It rescales the accumulated output vector incrementally without ever writing the massive intermediate attention matrix back to HBM.\n\n**FlashAttention-2 and FlashAttention-3 optimizations.** FlashAttention-2 optimizes work partitioning across thread blocks and warps, reducing non-matmul FLOPs and increasing Tensor Core occupancy. FlashAttention-3 specifically targets the NVIDIA Hopper (H100) architecture, exploiting asynchronous Tensor Memory Accelerator (TMA) hardware, FP8 low-precision Tensor Cores, and ping-pong GEMM scheduling to overlap asynchronous data transfers with computation, approaching the theoretical hardware compute limit.

## Why

Serving a 32,000-token prompt on an A100 GPU with naive attention fails with an Out-Of-Memory (OOM) error because materializing the float16 attention matrix requires tens of gigabytes of HBM. FlashAttention computes the exact same mathematical output within 128KB of SRAM per SM, running 3x faster and requiring only $O(N)$ memory.

## Worked Case

Serving a 32,000-token prompt on an A100 GPU with naive attention fails with an Out-Of-Memory (OOM) error because materializing the float16 attention matrix requires tens of gigabytes of HBM. FlashAttention computes the exact same mathematical output within 128KB of SRAM per SM, running 3x faster and requiring only $O(N)$ memory.

## Risk

Assuming FlashAttention changes model accuracy: FlashAttention is numerically identical (modulo floating-point associativity) to standard attention, unlike approximate sparse attention methods.

## Trade-off

FlashAttention drastically cuts memory footprint and latency for long sequences, but requires custom CUDA/Triton kernels tailored to specific GPU architectures (Ampere, Hopper, Blackwell).

## Try This

Benchmark `torch.nn.functional.scaled_dot_product_attention` with `enable_flash=True` versus naive matrix multiplication on sequence lengths from 512 to 16,384 tokens. Plot GPU memory usage and kernel runtime.

## Follow-ups

### What is FlashDecoding and how does it optimize the autoregressive generation phase?

FlashDecoding parallelizes along the sequence length dimension (K/V cache) during the single-token decode phase, avoiding SM underutilization when batch sizes are small.

## Citations

- https://arxiv.org/abs/2205.14135
- https://arxiv.org/abs/2307.08691
- https://tridao.me/blog/2024/flashdecoding/

# How do Rotary Position Embeddings (RoPE) encode relative token distance, and how do NTK-aware scaling and YaRN extrapolate context windows?

<!-- meta
answer_format: conceptual
domain: machine-learning
subdomain: deep-learning
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Rotary Position Embedding (RoPE) encodes relative positional information by rotating query and key vectors in complex 2D planes proportional to their absolute sequence positions.** Traditional sinusoidal absolute positional embeddings add position vectors directly to token embeddings ($x_m + p_m$), which degrades as sequence length grows because the dot product does not preserve purely relative distance. RoPE instead represents 2D slices of token representations as complex numbers and multiplies them by orthogonal rotation matrices: $R_{\Theta, m} q_m$, where each coordinate pair $(2i, 2i+1)$ is rotated by angle $m \theta_i$ with frequency $\theta_i = 10000^{-2i/d}$.\n\n**Relative distance preservation.** When calculating the inner product between query at position $m$ and key at position $n$, the rotation matrices satisfy: $\langle R_m q, R_n k \rangle = q^T R_{n-m} k$.

The attention score depends strictly on the relative distance $(m - n)$, decaying naturally as relative distance increases.\n\n**Context length extrapolation challenges.** When a model trained on 4k tokens encounters token 8,000, the rotation angles $m \theta_i$ enter unseen frequency regimes, causing catastrophic perplexity explosion.\n\n**Linear Scaling, NTK-aware scaling, and YaRN.** Direct linear interpolation (Position Interpolation / PI) compresses all frequencies uniformly by a scale factor $s = L_{\text{target}} / L_{\text{train}}$, but this damages high-frequency components that distinguish adjacent tokens. *NTK-aware scaling* distributes interpolation non-uniformly across frequencies: high frequencies (local token syntax) are preserved with little interpolation, while low frequencies (global context) are scaled down. *YaRN (Yet another RoPE extensioN)* refines this further by partitioning dimensions into unscaled high frequencies, interpolated low frequencies, and blended mid frequencies, combined with temperature scaling to counteract attention entropy dilution, enabling models trained on 4k context to generalize cleanly to 128k context with minimal fine-tuning.

## Why

A team deploys an open-weights LLM pre-trained on 4,096 tokens to analyze 32,000-token legal contracts. Simply feeding 32k tokens causes repetitive hallucinations. Applying YaRN RoPE scaling extends the effective context window to 32k without requiring multi-million-dollar full re-training.

## Worked Case

A team deploys an open-weights LLM pre-trained on 4,096 tokens to analyze 32,000-token legal contracts. Simply feeding 32k tokens causes repetitive hallucinations. Applying YaRN RoPE scaling extends the effective context window to 32k without requiring multi-million-dollar full re-training.

## Risk

Applying naive linear position interpolation without temperature adjustment dilutes attention sharpness, causing the model to struggle with 'Needle In A Haystack' retrieval tasks.

## Trade-off

RoPE extrapolation techniques enable massive context expansions with negligible fine-tuning, but slightly increase perplexity on short-range tasks compared to native long-context pre-training.

## Try This

Implement a toy 2D RoPE rotation function in NumPy. Compute the dot product between two identical vectors at positions $m=2, n=5$ versus $m=10, n=13$. Verify that both inner products are identical because their relative offset is 3.

## Follow-ups

### What is the base frequency $\theta$ parameter in RoPE, and why did Llama 3 increase it from 10,000 to 500,000?

Increasing the base frequency slows down rotation of low-frequency dimensions, naturally extending the theoretical context window before phase wrapping occurs.

## Citations

- https://arxiv.org/abs/2104.09864
- https://arxiv.org/abs/2309.00071

# How do Multi-Head Attention (MHA), Multi-Query Attention (MQA), and Grouped-Query Attention (GQA) trade off memory bandwidth, KV cache size, and model expressiveness?

<!-- meta
answer_format: conceptual
domain: machine-learning
subdomain: deep-learning
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Grouped-Query Attention (GQA) is an architectural interpolation between standard Multi-Head Attention (MHA) and Multi-Query Attention (MQA) that slashes KV cache memory consumption by an order of magnitude with negligible loss in model accuracy.** In standard MHA (e.g., GPT-3, original LLaMA), each of the $H$ attention heads has its own independent Query ($Q$), Key ($K$), and Value ($V$) projection matrices: $H_Q = H_K = H_V = H$. During autoregressive decoding, every generated token requires loading the entire accumulated $K$ and $V$ cache for all heads from HBM into SRAM, turning inference into a severe memory-bandwidth-bound workload.\n\n**The MQA extreme.** Multi-Query Attention (Shazeer, 2019) collapses this by using multiple Query heads ($H_Q = H$) but only a single shared Key head and Value head ($H_K = H_V = 1$). This reduces the KV cache size by a factor of $H$ (typically 32x or 64x), dramatically increasing batch throughput and decoding speed.

However, MQA can suffer from capacity degradation, instability during fine-tuning, and quality loss on complex reasoning tasks because all query heads are forced to attend over identical key/value representations.\n\n**Grouped-Query Attention as the golden mean.** GQA (Ainslie et al., 2023; adopted in LLaMA-2 70B, LLaMA-3, and Mistral) groups query heads into $G$ groups, where each group shares a single key and value head ($H_K = H_V = G$, where $1 < G < H$). For example, with $H=32$ query heads and $G=8$ KV heads, each KV pair is shared across 4 query heads (an 8:1 compression ratio). GQA delivers nearly the same high decoding throughput and low VRAM footprint as MQA while retaining the representational expressiveness and downstream quality of full MHA.

## Why

Serving a 70B parameter model with 32k context on an 8x H100 node under MHA requires 160GB of VRAM solely for the KV cache of a single batch of 8 concurrent requests, capping maximum concurrency. With GQA (8 groups), KV cache VRAM drops to 20GB, enabling an 8x increase in concurrent user throughput.

## Worked Case

Serving a 70B parameter model with 32k context on an 8x H100 node under MHA requires 160GB of VRAM solely for the KV cache of a single batch of 8 concurrent requests, capping maximum concurrency. With GQA (8 groups), KV cache VRAM drops to 20GB, enabling an 8x increase in concurrent user throughput.

## Risk

Assuming KV cache size is determined solely by hidden dimension: KV cache per token per layer is $2 \times \text{n\_kv\_heads} \times \text{head\_dim} \times \text{dtype\_bytes}$. Failing to account for $H_K$ leads to dramatic VRAM capacity miscalculations.

## Trade-off

GQA sacrifices a negligible fraction of attention diversity in exchange for an 8x reduction in KV cache memory bandwidth pressure and proportional gains in serving concurrency.

## Try This

Calculate the exact KV cache memory footprint in gigabytes for 1,000 concurrent streams of 4,096 tokens on a 32-layer model under MHA (32 heads) vs GQA (8 heads) vs MQA (1 head) in FP16.

## Follow-ups

### Can an existing MHA pre-trained checkpoint be converted to GQA during fine-tuning?

Yes, 'uptraining' collapses MHA heads into GQA groups by mean-pooling the projection weights, requiring only ~5% of pre-training tokens to recover full benchmark scores.

## Citations

- https://arxiv.org/abs/2305.13245
- https://arxiv.org/abs/1911.02150

# How do Sparse Mixture of Experts (MoE) architectures route tokens, and why are auxiliary load balancing loss and expert capacity factors necessary to prevent routing collapse?

<!-- meta
answer_format: conceptual
domain: machine-learning
subdomain: deep-learning
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Sparse Mixture of Experts (MoE) replaces dense feed-forward networks (FFN) with multiple parallel expert networks, activating only a small subset of experts per token to decouple total parameter capacity from compute cost per token.** In standard dense models (e.g., standard GPT), every token activates 100% of the model's weights. In a Sparse MoE (such as Mixtral 8x7B or DeepSeek-V2), the dense FFN is replaced by $E$ distinct expert FFNs, coordinated by a parameterized gating (router) network $W_g$.\n\n**Top-$k$ routing mechanism.** For a given token representation $x$, the router computes logits $H(x) = x \cdot W_g$, applies a softmax over all experts, and selects the top-$k$ experts (typically $k=2$): $y = \sum_{i \in \text{Top-}k} \text{Softmax}(H(x))_i \cdot E_i(x)$. While the model may possess 47B total parameters, each token executes compute on only 13B active parameters, providing high model knowledge with the inference latency of a much smaller model.\n\n**The routing collapse pathology.** Without intervention, the gating network quickly suffers from *routing collapse*: early in training, small random weight initialization causes the router to send slightly more tokens to Expert 1.

Expert 1 receives more gradient updates and improves faster, incentivizing the router to send even more tokens to Expert 1. Soon, 1 or 2 'celebrity experts' process 95% of all tokens, while the remaining experts starve and never learn, degrading the MoE into an underparameterized dense network.\n\n**Auxiliary load balancing loss and expert capacity factors.** To enforce uniform load distribution, models introduce an auxiliary load balancing loss $\mathcal{L}_{\text{aux}} = \alpha \cdot E \sum_{i=1}^E f_i \cdot P_i$, where $f_i$ is the actual fraction of tokens assigned to expert $i$, and $P_i$ is the router's average softmax probability for expert $i$. This penalizes uneven distributions. Additionally, distributed hardware clusters enforce an *Expert Capacity Factor* (e.g., $1.0$ to $1.25 \times \text{tokens} / E$): if an expert receives more tokens than its fixed buffer allocation, excess tokens are dropped (bypassed via residual connections) to prevent distributed stragglers from stalling pipeline parallelism.

## Why

Deploying an MoE model across 8 GPUs without load balancing causes GPU 0 (hosting the overloaded expert) to run at 100% compute while the other 7 GPUs sit idle at 5% compute, causing catastrophic latency spikes and pipeline bubbles. Load balancing loss restores equal device utilization.

## Worked Case

Deploying an MoE model across 8 GPUs without load balancing causes GPU 0 (hosting the overloaded expert) to run at 100% compute while the other 7 GPUs sit idle at 5% compute, causing catastrophic latency spikes and pipeline bubbles. Load balancing loss restores equal device utilization.

## Risk

Setting the auxiliary loss coefficient $\alpha$ too high forces the router to assign tokens randomly to satisfy load quotas, overriding semantic specialization and degrading reasoning quality.

## Trade-off

MoE delivers massive parameter capacity and low inference FLOPs, at the expense of requiring large total VRAM to store all expert weights across distributed GPU memory.

## Try This

Simulate a router choosing top-2 experts among 8 experts in PyTorch. Compute the auxiliary loss across 1,024 random tokens and verify that the loss reaches minimum value when all experts receive exactly 1/8th of the probability mass.

## Follow-ups

### What is the difference between token-choice routing and expert-choice routing?

In token-choice routing, each token selects its top-k experts (risking load imbalance); in expert-choice routing, each expert selects its top-c tokens (guaranteeing perfect load balance but potentially leaving some tokens unassigned).

## Citations

- https://arxiv.org/abs/2101.03961
- https://arxiv.org/abs/2401.04088

# When should you choose retrieval, a larger prompt or finetuning for a changing knowledge task?

<!-- meta
domain: foundations
subdomain: models
module: models
concept: When should you choose retrieval, a larger prompt or finetuning for a changing knowledge task?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A model answers correctly in a static benchmark but misses a policy updated yesterday. Training a larger adapter does not resolve the missing current source path.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Separate the defect first. Retrieval supplies changing external facts with source identity; context design selects what is exposed to the model; finetuning changes learned behavior from data. Evaluate a simple baseline and choose an intervention tied to observed errors. Finetuning does not by itself guarantee current facts, permission checks or supported citations.

Concrete engineering case: A model answers correctly in a static benchmark but misses a policy updated yesterday. Training a larger adapter does not resolve the missing current source path.

Boundary defense: Investigate instructions, runtime schema handling and model capability on that slice. The appropriate repair can be different from adding more documents.

## Spoken Summary

Separate the defect first. Retrieval supplies changing external facts with source identity; context design selects what is exposed to the model; finetuning changes learned behavior from data. Evaluate a simple baseline and choose an intervention tied to observed errors. Finetuning does not by itself guarantee current facts, permission checks or supported citations.

## Why

Separate the defect first. Retrieval supplies changing external facts with source identity; context design selects what is exposed to the model; finetuning changes learned behavior from data. Evaluate a simple baseline and choose an intervention tied to observed errors. Finetuning does not by itself guarantee current facts, permission checks or supported citations.

## Production Case

A model answers correctly in a static benchmark but misses a policy updated yesterday. Training a larger adapter does not resolve the missing current source path.

## Risk

A model answers correctly in a static benchmark but misses a policy updated yesterday. Training a larger adapter does not resolve the missing current source path.

## Trade-off

Investigate instructions, runtime schema handling and model capability on that slice. The appropriate repair can be different from adding more documents.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: models**: Separate the defect first.

## Alternatives

- Investigate instructions, runtime schema handling and model capability on that slice. The appropriate repair can be different from adding more documents.

## Pitfalls

- A model answers correctly in a static benchmark but misses a policy updated yesterday. Training a larger adapter does not resolve the missing current source path.

## Follow-ups

### What if the source is present and the requested output shape still fails?

Investigate instructions, runtime schema handling and model capability on that slice. The appropriate repair can be different from adding more documents.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A model answers correctly in a static benchmark but misses a policy updated yesterday. Training a larger adapter does not resolve the missing current source path.",
  "required_decision": "Separate the defect first"
}
```

## Citations

- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- https://scikit-learn.org/stable/common_pitfalls.html
- https://arxiv.org/abs/1706.03762
- https://arxiv.org/abs/1508.07909
- https://arxiv.org/abs/1808.06226

# How do token limits, decoding settings and model capability profiles affect provider selection?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: models
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A model profile includes supported inputs, output modes, context accounting, tool semantics, deployment limits and evaluation evidence. A published context window does not establish usable evidence capacity after instructions, tools, history and output reserve are included. Decoding parameters change sampling behavior but do not create missing knowledge or enforce authorization. Compare providers on representative tasks, latency, cost, privacy and failure behavior rather than only parameter count or a leaderboard rank. Record the actual model revision and request contract.

## Why

Two providers may both advertise tool calling while exposing different argument validation and streaming behavior. An adapter must normalize only genuinely compatible behavior and surface unsupported capabilities explicitly.

## Worked Case

Two providers may both advertise tool calling while exposing different argument validation and streaming behavior. An adapter must normalize only genuinely compatible behavior and surface unsupported capabilities explicitly.

## Risk

An opaque alias can change behavior without an application source change.

## Trade-off

Portability benefits from explicit capability checks rather than pretending all models are identical.

## Try This

Build a provider comparison covering one success, one unsupported feature and one malformed output.

## Citations

- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- https://scikit-learn.org/stable/common_pitfalls.html
- https://arxiv.org/abs/1706.03762
- https://arxiv.org/abs/1508.07909
- https://arxiv.org/abs/1808.06226
