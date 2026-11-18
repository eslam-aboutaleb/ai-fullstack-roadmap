<!-- chapter: deep-learning-foundations -->

# How does backpropagation differ from an optimizer update?

<!-- meta
domain: deep-learning
subdomain: deep-learning-foundations
module: deep-learning-foundations
concept: How does backpropagation differ from an optimizer update?
difficulty: interview
misconception_target: Missing the stated gradient versus update boundary: A training loop forgets to zero gradients between independent minibatches, unintentionally accumulating them and changing effective update size.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Backpropagation computes derivatives of the chosen loss through the computation graph. An optimizer uses those derivatives and its own state to update trainable parameters. Accumulated gradients, learning-rate schedules, averaging and zeroing policies affect the actual step. Computing a gradient does not itself change a parameter.

Engineering case: A training loop forgets to zero gradients between independent minibatches, unintentionally accumulating them and changing effective update size.

Reasoning under a changed assumption: No. It can deliberately approximate a larger effective batch when loss scaling and optimizer-step timing are explicit.

## Spoken Summary

Backpropagation computes derivatives of the chosen loss through the computation graph. An optimizer uses those derivatives and its own state to update trainable parameters. Accumulated gradients, learning-rate schedules, averaging and zeroing policies affect the actual step. Computing a gradient does not itself change a parameter.

## Why

Backpropagation computes derivatives of the chosen loss through the computation graph. An optimizer uses those derivatives and its own state to update trainable parameters. Accumulated gradients, learning-rate schedules, averaging and zeroing policies affect the actual step. Computing a gradient does not itself change a parameter.

## Production Case

A training loop forgets to zero gradients between independent minibatches, unintentionally accumulating them and changing effective update size.

## Risk

A training loop forgets to zero gradients between independent minibatches, unintentionally accumulating them and changing effective update size.

## Trade-off

No. It can deliberately approximate a larger effective batch when loss scaling and optimizer-step timing are explicit.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Gradient versus update**: Backpropagation computes derivatives of the chosen loss through the computation graph.

## Alternatives

- No. It can deliberately approximate a larger effective batch when loss scaling and optimizer-step timing are explicit.

## Pitfalls

- A training loop forgets to zero gradients between independent minibatches, unintentionally accumulating them and changing effective update size.

## Follow-ups

### Is gradient accumulation always a defect?

No. It can deliberately approximate a larger effective batch when loss scaling and optimizer-step timing are explicit.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A training loop forgets to zero gradients between independent minibatches, unintentionally accumulating them and changing effective update size.",
  "decision": "Backpropagation computes derivatives of the chosen loss through the computation graph"
}
```

## Citations

- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- https://arxiv.org/abs/1706.03762
- https://arxiv.org/abs/1508.07909
- https://arxiv.org/abs/2106.09685
- https://docs.pytorch.org/tutorials/beginner/blitz/neural_networks_tutorial.html
- https://docs.pytorch.org/docs/2.14/generated/torch.nn.RNN.html

# How do batch size, learning rate and optimizer state interact with memory and stability?

<!-- meta
domain: deep-learning
subdomain: deep-learning-foundations
module: deep-learning-foundations
concept: How do batch size, learning rate and optimizer state interact with memory and stability?
difficulty: interview
misconception_target: Missing the stated training memory boundary: A model’s weights fit on a GPU but training fails when activations and Adam moments are allocated.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Batch size affects activation memory and the gradient estimate. Learning rate controls update scale under the optimizer’s rule; adaptive optimizers also retain moment state. Smaller batches reduce some memory but may change training behavior. Measure activations, gradients, parameters and optimizer state separately before assuming a parameter-count estimate predicts device fit.

Engineering case: A model’s weights fit on a GPU but training fails when activations and Adam moments are allocated.

Reasoning under a changed assumption: No. Parameter and optimizer allocations may remain fixed, and attention/sequence shapes and allocator behavior influence peak use.

## Spoken Summary

Batch size affects activation memory and the gradient estimate. Learning rate controls update scale under the optimizer’s rule; adaptive optimizers also retain moment state. Smaller batches reduce some memory but may change training behavior. Measure activations, gradients, parameters and optimizer state separately before assuming a parameter-count estimate predicts device fit.

## Why

Batch size affects activation memory and the gradient estimate. Learning rate controls update scale under the optimizer’s rule; adaptive optimizers also retain moment state. Smaller batches reduce some memory but may change training behavior. Measure activations, gradients, parameters and optimizer state separately before assuming a parameter-count estimate predicts device fit.

## Production Case

A model’s weights fit on a GPU but training fails when activations and Adam moments are allocated.

## Risk

A model’s weights fit on a GPU but training fails when activations and Adam moments are allocated.

## Trade-off

No. Parameter and optimizer allocations may remain fixed, and attention/sequence shapes and allocator behavior influence peak use.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Training memory**: Batch size affects activation memory and the gradient estimate.

## Alternatives

- No. Parameter and optimizer allocations may remain fixed, and attention/sequence shapes and allocator behavior influence peak use.

## Pitfalls

- A model’s weights fit on a GPU but training fails when activations and Adam moments are allocated.

## Follow-ups

### Does halving the batch always halve total memory?

No. Parameter and optimizer allocations may remain fixed, and attention/sequence shapes and allocator behavior influence peak use.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A model’s weights fit on a GPU but training fails when activations and Adam moments are allocated.",
  "decision": "Batch size affects activation memory and the gradient estimate"
}
```

## Citations

- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- https://arxiv.org/abs/1706.03762
- https://arxiv.org/abs/1508.07909
- https://arxiv.org/abs/2106.09685
- https://docs.pytorch.org/tutorials/beginner/blitz/neural_networks_tutorial.html
- https://docs.pytorch.org/docs/2.14/generated/torch.nn.RNN.html

# What do dropout, normalization and train/eval mode change in a neural network?

<!-- meta
domain: deep-learning
subdomain: deep-learning-foundations
module: deep-learning-foundations
concept: What do dropout, normalization and train/eval mode change in a neural network?
difficulty: interview
misconception_target: Missing the stated module evaluation mode boundary: Evaluation runs with dropout active and repeated predictions vary. Another run uses no_grad but leaves the model in training mode.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Dropout randomly changes activations during training under its scaling rule; inference normally uses deterministic behavior. Some normalization layers also use learned or running statistics differently across modes. Set train/eval behavior explicitly and inspect the layer type. Disabling gradients and selecting evaluation mode solve different problems.

Engineering case: Evaluation runs with dropout active and repeated predictions vary. Another run uses no_grad but leaves the model in training mode.

Reasoning under a changed assumption: No. Evaluation mode changes module behavior. Use the appropriate gradient context separately when backward graphs are unnecessary.

## Spoken Summary

Dropout randomly changes activations during training under its scaling rule; inference normally uses deterministic behavior. Some normalization layers also use learned or running statistics differently across modes. Set train/eval behavior explicitly and inspect the layer type. Disabling gradients and selecting evaluation mode solve different problems.

## Why

Dropout randomly changes activations during training under its scaling rule; inference normally uses deterministic behavior. Some normalization layers also use learned or running statistics differently across modes. Set train/eval behavior explicitly and inspect the layer type. Disabling gradients and selecting evaluation mode solve different problems.

## Production Case

Evaluation runs with dropout active and repeated predictions vary. Another run uses no_grad but leaves the model in training mode.

## Risk

Evaluation runs with dropout active and repeated predictions vary. Another run uses no_grad but leaves the model in training mode.

## Trade-off

No. Evaluation mode changes module behavior. Use the appropriate gradient context separately when backward graphs are unnecessary.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Module evaluation mode**: Dropout randomly changes activations during training under its scaling rule; inference normally uses deterministic behavior.

## Alternatives

- No. Evaluation mode changes module behavior. Use the appropriate gradient context separately when backward graphs are unnecessary.

## Pitfalls

- Evaluation runs with dropout active and repeated predictions vary. Another run uses no_grad but leaves the model in training mode.

## Follow-ups

### Does model.eval disable gradient computation?

No. Evaluation mode changes module behavior. Use the appropriate gradient context separately when backward graphs are unnecessary.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "Evaluation runs with dropout active and repeated predictions vary. Another run uses no_grad but leaves the model in training mode.",
  "decision": "Dropout randomly changes activations during training under its scaling rule; inference normally uses deterministic behavior"
}
```

## Citations

- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- https://arxiv.org/abs/1706.03762
- https://arxiv.org/abs/1508.07909
- https://arxiv.org/abs/2106.09685
- https://docs.pytorch.org/tutorials/beginner/blitz/neural_networks_tutorial.html
- https://docs.pytorch.org/docs/2.14/generated/torch.nn.RNN.html

# When do convolutional, recurrent and attention architectures make different assumptions?

<!-- meta
domain: deep-learning
subdomain: deep-learning-foundations
module: deep-learning-foundations
concept: When do convolutional, recurrent and attention architectures make different assumptions?
difficulty: interview
misconception_target: Missing the stated architectural inductive bias boundary: A small image task is served under tight latency constraints. A compact convolutional baseline is easier to deploy than an oversized attention model.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Convolutions share local filters, recurrent models propagate state through an ordered sequence, and attention combines representations through data-dependent weights. These choices change inductive bias, parallelism and memory. Compare them against the task’s spatial or temporal structure rather than treating the most fashionable architecture as universally best.

Engineering case: A small image task is served under tight latency constraints. A compact convolutional baseline is easier to deploy than an oversized attention model.

Reasoning under a changed assumption: Yes. A content-based attention operation alone does not necessarily encode the intended token order. Position representations and masking define important sequence semantics.

## Spoken Summary

Convolutions share local filters, recurrent models propagate state through an ordered sequence, and attention combines representations through data-dependent weights. These choices change inductive bias, parallelism and memory. Compare them against the task’s spatial or temporal structure rather than treating the most fashionable architecture as universally best.

## Why

Convolutions share local filters, recurrent models propagate state through an ordered sequence, and attention combines representations through data-dependent weights. These choices change inductive bias, parallelism and memory. Compare them against the task’s spatial or temporal structure rather than treating the most fashionable architecture as universally best.

## Production Case

A small image task is served under tight latency constraints. A compact convolutional baseline is easier to deploy than an oversized attention model.

## Risk

A small image task is served under tight latency constraints. A compact convolutional baseline is easier to deploy than an oversized attention model.

## Trade-off

Yes. A content-based attention operation alone does not necessarily encode the intended token order. Position representations and masking define important sequence semantics.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Architectural inductive bias**: Convolutions share local filters, recurrent models propagate state through an ordered sequence, and attention combines representations through data-dependent weights.

## Alternatives

- Yes. A content-based attention operation alone does not necessarily encode the intended token order. Position representations and masking define important sequence semantics.

## Pitfalls

- A small image task is served under tight latency constraints. A compact convolutional baseline is easier to deploy than an oversized attention model.

## Follow-ups

### Can attention still need position information?

Yes. A content-based attention operation alone does not necessarily encode the intended token order. Position representations and masking define important sequence semantics.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A small image task is served under tight latency constraints. A compact convolutional baseline is easier to deploy than an oversized attention model.",
  "decision": "Convolutions share local filters, recurrent models propagate state through an ordered sequence, and attention combines representations through data-dependent weights"
}
```

## Citations

- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- https://arxiv.org/abs/1706.03762
- https://arxiv.org/abs/1508.07909
- https://arxiv.org/abs/2106.09685
- https://docs.pytorch.org/tutorials/beginner/blitz/neural_networks_tutorial.html
- https://docs.pytorch.org/docs/2.14/generated/torch.nn.RNN.html

# How do tokenizer units and causal labels define a language-model training example?

<!-- meta
domain: deep-learning
subdomain: deep-learning-foundations
module: deep-learning-foundations
concept: How do tokenizer units and causal labels define a language-model training example?
difficulty: interview
misconception_target: Missing the stated causal next-token labels boundary: A training sample allows the input to attend to the target token at the same future position. Loss looks excellent but autoregressive generation fails.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

A tokenizer maps text to a vocabulary-specific sequence of IDs. Next-token learning aligns each input position with the following target and applies a causal restriction against future information. Token counts are not character or word counts. Preserve the tokenizer identity and inspect padding, special tokens and label masks.

Engineering case: A training sample allows the input to attend to the target token at the same future position. Loss looks excellent but autoregressive generation fails.

Reasoning under a changed assumption: No. It is a transparent bounded fixture, but its vocabulary, context and efficiency are unlike those of a production subword model.

## Spoken Summary

A tokenizer maps text to a vocabulary-specific sequence of IDs. Next-token learning aligns each input position with the following target and applies a causal restriction against future information. Token counts are not character or word counts. Preserve the tokenizer identity and inspect padding, special tokens and label masks.

## Why

A tokenizer maps text to a vocabulary-specific sequence of IDs. Next-token learning aligns each input position with the following target and applies a causal restriction against future information. Token counts are not character or word counts. Preserve the tokenizer identity and inspect padding, special tokens and label masks.

## Production Case

A training sample allows the input to attend to the target token at the same future position. Loss looks excellent but autoregressive generation fails.

## Risk

A training sample allows the input to attend to the target token at the same future position. Loss looks excellent but autoregressive generation fails.

## Trade-off

No. It is a transparent bounded fixture, but its vocabulary, context and efficiency are unlike those of a production subword model.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Causal next-token labels**: A tokenizer maps text to a vocabulary-specific sequence of IDs.

## Alternatives

- No. It is a transparent bounded fixture, but its vocabulary, context and efficiency are unlike those of a production subword model.

## Pitfalls

- A training sample allows the input to attend to the target token at the same future position. Loss looks excellent but autoregressive generation fails.

## Follow-ups

### Is a character tokenizer wrong for every teaching model?

No. It is a transparent bounded fixture, but its vocabulary, context and efficiency are unlike those of a production subword model.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A training sample allows the input to attend to the target token at the same future position. Loss looks excellent but autoregressive generation fails.",
  "decision": "A tokenizer maps text to a vocabulary-specific sequence of IDs"
}
```

## Citations

- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- https://arxiv.org/abs/1706.03762
- https://arxiv.org/abs/1508.07909
- https://arxiv.org/abs/2106.09685
- https://docs.pytorch.org/tutorials/beginner/blitz/neural_networks_tutorial.html
- https://docs.pytorch.org/docs/2.14/generated/torch.nn.RNN.html

# Trace query, key and value shapes through one attention head.

<!-- meta
domain: deep-learning
subdomain: deep-learning-foundations
module: deep-learning-foundations
concept: Trace query, key and value shapes through one attention head.
difficulty: interview
misconception_target: Missing the stated attention shape boundary: A decoder applies softmax along the query axis instead of the key axis, producing normalized values with the wrong interpretation.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

For a sequence of length T and head width d, projected queries and keys produce a T-by-T score matrix. Scaling by the square root of d helps control score magnitudes, a mask restricts permitted positions, and normalized weights combine the value vectors. Shape checks and a tiny numerical example expose transposition and masking errors.

Engineering case: A decoder applies softmax along the query axis instead of the key axis, producing normalized values with the wrong interpretation.

Reasoning under a changed assumption: No. The computation mixes representations. A semantic support or explanation claim requires its own evidence rather than reading attention weights as an entailment certificate.

## Spoken Summary

For a sequence of length T and head width d, projected queries and keys produce a T-by-T score matrix. Scaling by the square root of d helps control score magnitudes, a mask restricts permitted positions, and normalized weights combine the value vectors. Shape checks and a tiny numerical example expose transposition and masking errors.

## Why

For a sequence of length T and head width d, projected queries and keys produce a T-by-T score matrix. Scaling by the square root of d helps control score magnitudes, a mask restricts permitted positions, and normalized weights combine the value vectors. Shape checks and a tiny numerical example expose transposition and masking errors.

## Production Case

A decoder applies softmax along the query axis instead of the key axis, producing normalized values with the wrong interpretation.

## Risk

A decoder applies softmax along the query axis instead of the key axis, producing normalized values with the wrong interpretation.

## Trade-off

No. The computation mixes representations. A semantic support or explanation claim requires its own evidence rather than reading attention weights as an entailment certificate.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Attention shape**: For a sequence of length T and head width d, projected queries and keys produce a T-by-T score matrix.

## Alternatives

- No. The computation mixes representations. A semantic support or explanation claim requires its own evidence rather than reading attention weights as an entailment certificate.

## Pitfalls

- A decoder applies softmax along the query axis instead of the key axis, producing normalized values with the wrong interpretation.

## Follow-ups

### Does attention weight prove a source supports a generated claim?

No. The computation mixes representations. A semantic support or explanation claim requires its own evidence rather than reading attention weights as an entailment certificate.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A decoder applies softmax along the query axis instead of the key axis, producing normalized values with the wrong interpretation.",
  "decision": "For a sequence of length T and head width d, projected queries and keys produce a T-by-T score matrix"
}
```

## Citations

- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- https://arxiv.org/abs/1706.03762
- https://arxiv.org/abs/1508.07909
- https://arxiv.org/abs/2106.09685
- https://docs.pytorch.org/tutorials/beginner/blitz/neural_networks_tutorial.html
- https://docs.pytorch.org/docs/2.14/generated/torch.nn.RNN.html

# Why do prefill and token decoding have different serving bottlenecks?

<!-- meta
domain: deep-learning
subdomain: deep-learning-foundations
module: deep-learning-foundations
concept: Why do prefill and token decoding have different serving bottlenecks?
difficulty: interview
misconception_target: Missing the stated kv-cache contract boundary: A service looks fast on short prompts but runs out of cache memory on long concurrent sessions even though model weights are unchanged.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Prefill processes the prompt context; decoding repeatedly produces new tokens while reusing cached keys and values where supported. KV caching trades recomputation for memory and must bind to the exact model, tokens and request state. Measure first-token and completion behavior separately under the relevant batch and context shapes.

Engineering case: A service looks fast on short prompts but runs out of cache memory on long concurrent sessions even though model weights are unchanged.

Reasoning under a changed assumption: Not for every workload or hardware configuration. Include transfer, allocation, batch behavior and memory pressure in actual measurements.

## Spoken Summary

Prefill processes the prompt context; decoding repeatedly produces new tokens while reusing cached keys and values where supported. KV caching trades recomputation for memory and must bind to the exact model, tokens and request state. Measure first-token and completion behavior separately under the relevant batch and context shapes.

## Why

Prefill processes the prompt context; decoding repeatedly produces new tokens while reusing cached keys and values where supported. KV caching trades recomputation for memory and must bind to the exact model, tokens and request state. Measure first-token and completion behavior separately under the relevant batch and context shapes.

## Production Case

A service looks fast on short prompts but runs out of cache memory on long concurrent sessions even though model weights are unchanged.

## Risk

A service looks fast on short prompts but runs out of cache memory on long concurrent sessions even though model weights are unchanged.

## Trade-off

Not for every workload or hardware configuration. Include transfer, allocation, batch behavior and memory pressure in actual measurements.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **KV-cache contract**: Prefill processes the prompt context; decoding repeatedly produces new tokens while reusing cached keys and values where supported.

## Alternatives

- Not for every workload or hardware configuration. Include transfer, allocation, batch behavior and memory pressure in actual measurements.

## Pitfalls

- A service looks fast on short prompts but runs out of cache memory on long concurrent sessions even though model weights are unchanged.

## Follow-ups

### Does a cache always make inference faster?

Not for every workload or hardware configuration. Include transfer, allocation, batch behavior and memory pressure in actual measurements.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A service looks fast on short prompts but runs out of cache memory on long concurrent sessions even though model weights are unchanged.",
  "decision": "Prefill processes the prompt context; decoding repeatedly produces new tokens while reusing cached keys and values where supported"
}
```

## Citations

- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- https://arxiv.org/abs/1706.03762
- https://arxiv.org/abs/1508.07909
- https://arxiv.org/abs/2106.09685
- https://docs.pytorch.org/tutorials/beginner/blitz/neural_networks_tutorial.html
- https://docs.pytorch.org/docs/2.14/generated/torch.nn.RNN.html

# What does a low-rank adapter reduce, and what still needs to be measured?

<!-- meta
domain: deep-learning
subdomain: deep-learning-foundations
module: deep-learning-foundations
concept: What does a low-rank adapter reduce, and what still needs to be measured?
difficulty: interview
misconception_target: Missing the stated low-rank update boundary: An adapter loads against a base with the same architecture name but different weights or vocabulary, silently changing its semantics.
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Fine-tuning changes learned behavior; retrieval supplies current facts.** Supervised fine-tuning (SFT) optimizes a pretrained causal model on task-specific examples. LoRA (low-rank adaptation) freezes the original weight matrix W and learns two smaller matrices A and B, adding ΔW=(α/r)BA. QLoRA combines a low-bit quantized base with trainable adapters, subject to actual GPU/kernel support. Do not confuse an output-head-only exercise with adapters attached to all transformer attention/MLP projections, and do not assume LoRA reduces KV cache memory at inference.

**Parameter arithmetic.** For an output×input linear weight W of 4096×4096, a rank-16 LoRA adapter has r×input + output×r = 16×4096 + 4096×16 = **131,072 trainable scalar parameters** instead of 16,777,216 frozen base-weight scalars for that matrix, before optimizer states and bias. Adapter parameter bytes are only one part of training memory: forward activations, gradients, optimizer states, precision and quantized-base buffers remain. α/r scales the adapter update; different target modules and ranks change the capacity and memory cost.

**SFT token-label mechanics.** A prompt-response sequence often becomes [BOS, instruction, response, EOS] under a tokenizer and chat template. In causal next-token training, input position i predicts token i+1; for response-only SFT, assign ignore_index (often -100) to labels whose *target* belongs to the prompt, and also ignore padding. Preserve the answer tokens and EOS targets. If labels are shifted or masked incorrectly, the optimizer may train on user prompts instead of assistant responses or lose the first response token. Verify chat template, tokenizer revision, special tokens, pad/packing policies and attention masks.

**Training arithmetic and split integrity.** With 103 examples, microbatch 8 and accumulation 4, one epoch has ceil(103/8)=13 microsteps. Over three epochs that is 39 microsteps and ceil(39/4)=10 optimizer updates if accumulation continues across epochs and the last partial group is stepped. Some trainers flush per epoch instead; document the exact training loop. Hold out source families/users/times before templating to avoid train/evaluation overlap. Compare baseline prompt/RAG with SFT/LoRA under equal prompts, decoding and sealed evaluation cases.

**Runnable exercise and actual optimization.** Run `python3 -B labs/sft_lora_contract.py`: it checks response-only target masking, effective batch arithmetic, **optimizes** a frozen 2×2 linear matrix with rank-one adapter gradients, verifies loss decrease and merge equivalence, and rejects a mismatched base/tokenizer/template manifest. This is real numerical training of a tiny adapter, not a foundation-model SFT or QLoRA implementation. The repository already contains a separate CPU PyTorch `labs/adapter_training.py` that trains a miniature character LM with a frozen output-head adapter; its quality claims are likewise limited to its small authored corpus.

**Production decision and release.** If the failure is missing current policy information, fix retrieval/source freshness first. If the model repeatedly violates a stable formatting or domain response pattern despite good retrieved evidence, a controlled SFT experiment can be appropriate. An adapter artifact must bind an exact base revision, tokenizer/chat template and training/eval dataset lineage. Evaluate regressions in refusal/security slices, privacy memorization, style/accuracy, calibration and cost/latency. A merged adapter needs numerical equivalence checks and must not silently alter a quantized base.

**Follow-up.** If a 4-bit QLoRA checkpoint is served with an incompatible tokenizer or merged into a different base revision, matching matrix shapes cannot establish correctness. Reject the artifact, pin the compatible base/template and rerun output regression tests before deployment.

## Spoken Summary

Low-rank adaptation trains smaller factor matrices against a frozen base. It reduces trainable parameters and associated optimizer work, but the base and relevant activations still occupy memory. An output-head-only fixture has different gradient paths from adapters inside attention layers. Verify frozen weights, exact artifact compatibility and held-out behavior.

## Why

Low-rank adapter parameter savings are real but do not establish model improvement, correct causal masks or low GPU memory without a controlled full training evaluation.

## Production Case

An adapter loads against a base with the same architecture name but different weights or vocabulary, silently changing its semantics.

## Risk

An adapter loads against a base with the same architecture name but different weights or vocabulary, silently changing its semantics.

## Trade-off

No. Inspect data permission, leakage, validation quality, task and safety slices, artifact reload and actual target-hardware serving behavior.

## Try This

Compute the rank-16 parameter count, run the target-masking and trained adapter fixture, then change the base manifest and confirm load fails.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Low-rank update**: Low-rank adaptation trains smaller factor matrices against a frozen base.

## Alternatives

- No. Inspect data permission, leakage, validation quality, task and safety slices, artifact reload and actual target-hardware serving behavior.

## Pitfalls

- An adapter loads against a base with the same architecture name but different weights or vocabulary, silently changing its semantics.

## Follow-ups

### Does low training loss establish a safe production finetune?

No. Inspect data permission, leakage, validation quality, task and safety slices, artifact reload and actual target-hardware serving behavior.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "An adapter loads against a base with the same architecture name but different weights or vocabulary, silently changing its semantics.",
  "decision": "Low-rank adaptation trains smaller factor matrices against a frozen base"
}
```

## Citations

- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- https://arxiv.org/abs/1706.03762
- https://arxiv.org/abs/1508.07909
- https://arxiv.org/abs/2106.09685
- https://docs.pytorch.org/tutorials/beginner/blitz/neural_networks_tutorial.html
- https://docs.pytorch.org/docs/2.14/generated/torch.nn.RNN.html

# How do activations and loss functions change what a neural network can learn?

<!-- meta
answer_format: conceptual
domain: deep-learning
subdomain: deep-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Without nonlinear activations, stacked affine layers collapse to a single affine transformation. Activations introduce nonlinear behavior and different gradient regimes. A loss translates the target and prediction contract into an optimization objective: squared error suits some numeric targets, while cross-entropy suits specified classification distributions. Match output representation, target shape and loss expectations. A library may expect logits rather than already-normalized probabilities. Low training loss means fit to the objective on those examples, not guaranteed task usefulness or safety.

## Why

Passing softmax probabilities into a loss expecting raw logits can apply the wrong transformation and degrade learning. Check the documented input contract and compare a tiny hand-computed example.

## Worked Case

Passing softmax probabilities into a loss expecting raw logits can apply the wrong transformation and degrade learning. Check the documented input contract and compare a tiny hand-computed example.

## Risk

A shape-compatible loss can still optimize the wrong target axis or label mapping.

## Trade-off

Choose an objective from the task and verify a small numerical case before scaling.

## Try This

Trace logits, target indices and loss values for a two-class batch.

## Citations

- https://docs.pytorch.org/docs/2.14/notes/autograd.html
- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html

# Why do vanishing gradients, exploding gradients and initialization affect training?

<!-- meta
answer_format: conceptual
domain: deep-learning
subdomain: deep-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Backpropagation multiplies local sensitivities through the computational graph. Repeated small factors can make early-layer gradients tiny; large factors can make updates unstable. Initialization, activation choice, normalization and residual paths influence this behavior. Gradient clipping bounds a selected gradient measure but does not fix bad data or an incorrect objective. Monitor gradient norms, activations and finite values by layer, and distinguish true convergence from parameters that never receive useful gradients. A single total loss curve hides many of these problems.

## Why

A recurrent model may have a finite loss while early-state gradients are effectively zero. Increasing training duration does not repair a graph whose useful gradient signal has disappeared.

## Worked Case

A recurrent model may have a finite loss while early-state gradients are effectively zero. Increasing training duration does not repair a graph whose useful gradient signal has disappeared.

## Risk

Blindly lowering the learning rate can hide instability without correcting its cause.

## Trade-off

Stability interventions need measurements and controlled comparisons.

## Try This

Inspect gradient norms by layer and inject one nonfinite input to check diagnostics.

## Citations

- https://docs.pytorch.org/docs/2.14/notes/autograd.html
- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html

# How do residual connections and normalization support deep architectures?

<!-- meta
answer_format: conceptual
domain: deep-learning
subdomain: deep-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A residual block adds a transformed path to a compatible skip path, improving information and gradient flow while still requiring compatible shapes. Normalization controls statistics under a defined set of axes. Batch normalization uses batch-related statistics during training and typically running statistics for evaluation; layer normalization operates across selected features and behaves differently. Neither is interchangeable without considering architecture and batch regime. Train/eval mode must be set intentionally, and learned affine parameters remain part of the model state.

## Why

A model evaluated in training mode can produce changing results because dropout is active or batch statistics depend on its companions. A saved checkpoint alone does not choose the correct inference mode.

## Worked Case

A model evaluated in training mode can produce changing results because dropout is active or batch statistics depend on its companions. A saved checkpoint alone does not choose the correct inference mode.

## Risk

A tiny or shifted batch can invalidate assumptions about batch statistics.

## Trade-off

Residual and normalization choices improve some training regimes at additional implementation constraints.

## Try This

Compare repeated inference in train and eval modes and document the expected difference.

## Citations

- https://docs.pytorch.org/docs/2.14/notes/autograd.html
- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html

# How do padding, causal masks and attention masks prevent information leakage?

<!-- meta
answer_format: conceptual
domain: deep-learning
subdomain: deep-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Padding lets unequal sequences share a tensor shape, but padded positions must be handled according to the model and loss contracts. A causal mask prevents a position from attending to future positions in an autoregressive task. These masks serve different purposes and often need to be combined. Confirm shape, polarity and broadcasting rules in the actual library. Masking a loss alone does not necessarily prevent hidden representations from seeing forbidden future information during training.

## Why

A next-token model without causal attention can read the answer token during training and report excellent loss. At generation time that future token is unavailable, so the apparent performance collapses.

## Worked Case

A next-token model without causal attention can read the answer token during training and report excellent loss. At generation time that future token is unavailable, so the apparent performance collapses.

## Risk

A reversed boolean-mask convention can silently expose forbidden positions.

## Trade-off

Explicit tiny attention examples are easier to verify than only large training runs.

## Try This

Change a future token and verify that earlier causal outputs remain unchanged.

## Citations

- https://docs.pytorch.org/docs/2.14/notes/autograd.html
- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html

# How do training memory, inference memory and gradient accumulation differ?

<!-- meta
answer_format: conceptual
domain: deep-learning
subdomain: deep-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Parameter bytes are only one part of memory use.** Inventory the state required by the actual workload and measure peak allocation on the intended hardware.

| Component | Training | Inference |
| --- | --- | --- |
| Model parameters | Required | Required |
| Parameter gradients | Retained for updates | Usually unnecessary |
| Optimizer state | Depends on optimizer | Usually unnecessary |
| Intermediate activations | Retained or recomputed for backward | Needed for current computation under the inference strategy |
| Attention key/value cache | Depends on training method | Can grow with generated context and concurrent sequences |
| Temporary workspaces | Kernel and shape dependent | Kernel and shape dependent |

**Gradient accumulation changes the update boundary.** Process smaller microbatches, scale the losses or gradients to match the intended effective batch, accumulate them, then perform one optimizer update. Clear accumulated gradients at the correct boundary.

Accumulation can reduce activation memory per microbatch at the cost of more sequential work. It need not be identical to one large batch when layers depend on batch statistics or other batch-coupled behavior. Account for allocator peaks, temporary workspaces and cache growth rather than calculating capacity from parameter storage alone.

## Why

Four microbatches accumulated before one update can reduce activation memory compared with a single larger batch. If the loss is summed incorrectly, the resulting gradient scale and effective learning rate change.

## Worked Case

Four microbatches accumulated before one update can reduce activation memory compared with a single larger batch. If the loss is summed incorrectly, the resulting gradient scale and effective learning rate change.

## Risk

Counting only model weights can substantially underestimate the memory required.

## Trade-off

Accumulation trades additional sequential work for a smaller per-microbatch footprint.

## Try This

Inventory memory components and verify accumulation against a small controlled reference.

## Citations

- https://docs.pytorch.org/docs/2.14/notes/autograd.html
- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html

# How do checkpointing, seeds and deterministic settings support reproducible experiments?

<!-- meta
answer_format: conceptual
domain: deep-learning
subdomain: deep-learning-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A training checkpoint may need model weights, optimizer and scheduler state, preprocessing, vocabulary, data position and random-number-generator state. Loading weights alone is not necessarily a true continuation of the same optimization process. Seeds reduce some variability but do not guarantee identical results across devices, kernels or library versions. Record environment and data lineage, compare within justified tolerances and state which determinism settings were enabled. Keep a separate evaluation manifest so a restored run uses the intended held-out data.

## Why

Resuming with a fresh optimizer can produce a different trajectory even from identical weights because momentum or adaptive moments were lost. A shuffled data loader also needs its position or replay contract considered.

## Worked Case

Resuming with a fresh optimizer can produce a different trajectory even from identical weights because momentum or adaptive moments were lost. A shuffled data loader also needs its position or replay contract considered.

## Risk

A named seed is often mistaken for complete cross-platform reproducibility.

## Trade-off

Stronger determinism can cost performance and still has a defined compatibility scope.

## Try This

Resume a tiny run with and without optimizer state and compare the next update.

## Citations

- https://docs.pytorch.org/docs/2.14/notes/autograd.html
- https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
