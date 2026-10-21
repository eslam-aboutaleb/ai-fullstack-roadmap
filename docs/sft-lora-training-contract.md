# SFT and LoRA: validated CPU learning contract (#46)

Introduction: Teach stable task behavior vs factual knowledge. Retrieval fixes
missing or stale sources; SFT optimizes model parameters to change behavior.
LoRA keeps a base weight frozen and trains a scaled low-rank update; QLoRA
requires a genuinely supported quantized base and training environment.

Run: `python3 -B labs/sft_lora_contract.py`.

The standard-library fixture demonstrates response-only next-token labels,
train/padding masks, microbatch/gradient accumulation arithmetic, **actual
gradient optimization** of a frozen 2x2 matrix with a rank-one adapter, weight
merge equivalence, and refusal of incompatible manifest IDs.

This is not a full causal transformer fine-tune or real PEFT/QLoRA GPU run.
The existing `labs/adapter_training.py` independently trains a tiny
PyTorch causal character LM output-head low-rank adaptation and checks
causal leakage, artifact reload and base immutability. These two fixtures
cover different pieces of the end-to-end teaching contract.

Production continuation: pin model/tokenizer/chat template and license;
create consented, deduplicated train/validation/test splits before packing;
mask assistant targets correctly; define hardware, NF4/compute precision,
optimizer state, gradient clipping/checkpoint policy; train pinned PEFT
target modules; compare frozen baseline and adapter on a sealed dataset;
evaluate security/forgetting/privacy; document artifact rollback. Never
equate a toy decrease in training loss with production quality.

Primary sources:
https://huggingface.co/docs/peft/developer_guides/quantization
https://arxiv.org/abs/2106.09685
