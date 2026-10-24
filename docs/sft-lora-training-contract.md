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

## Executed Transformers/PEFT causal-LM training

`labs/peft_causal_sft.py` now executes a real Transformers GPT-2 architecture
with real PEFT LoRA adapters. Install the pinned model requirements and
`requirements-peft.txt`, then run:

```sh
python3 -B labs/peft_causal_sft.py --output peft-result.json
```

The default run is offline and CPU-only: no pretrained weights, model downloads,
service account or provider calls. It starts from an explicitly random tiny
base and original synthetic color-rule data. This tests SFT mechanics and real
SDK/artifact compatibility, not a foundation model's general language quality.
The tokenizer vocabulary and prompt template are hashed. Example IDs are split
before training, and evaluation predicts the first response token from the
prompt alone rather than reading teacher-forced target text.

The run checks response-only and padding label masks, shifted causal loss against
an independent cross-entropy calculation, two equal-token microbatches per
optimizer step, causal prefix invariance, frozen base tensors, compatible
adapter manifest, actual save/reload and merged output equivalence. A changed
base/tokenizer/template digest is rejected. The actual held-out validation and
test counts, losses, label accuracy, parameter count, SDK versions and measured
CPU training time are in `docs/evidence/peft-causal-sft.json`. Those 16-case sets
are a narrowly controlled oracle and do not support production-quality claims.

A pretrained-model SFT profile, broader safety/forgetting evaluation and genuine
QLoRA/GPU measurements remain separate requirements; this report does not
relabel the random base or a CPU result as any of those.

## Executed pretrained profile — 23 October 2026

The optional command now loads real pretrained EleutherAI/pythia-14m weights
and tokenizer at immutable revision cf967c0a9a04383db6f7b1108d86b2962634b4ac
(Apache-2.0). This CPU profile downloads model artifacts; it is distinct from
the default offline random GPT-2 profile. Use the pinned model/PEFT requirements:

```sh
python3 -B labs/peft_causal_sft.py --pretrained --revision cf967c0a9a04383db6f7b1108d86b2962634b4ac --steps 6 --output pretrained-peft-sft.json
```

`docs/evidence/pretrained-peft-sft.json` records the executed baseline/adapter
validation/test metrics, measured training time, versions and hardware. Both
splits are original synthetic color-rule cases separated by item ID before
training, not a representative language/safety benchmark. `label_accuracy`
means first-response-token accuracy from prompt-only logits, not full generated
answer correctness. The run checks response and padding masks, shifted loss,
actual token-weighted accumulation, frozen weights, future-token invariance,
manifest mismatch denial, serialized reload and merged-output equivalence.
The tokenizer digest includes its backend rules and special/padding settings,
not only the vocabulary. The temporary adapter directory is removed after checks;
no service, account credential or deployed endpoint is used.

This closes the missing *pretrained execution* evidence, not all of issue #46.
Representative safety/forgetting studies, full course outcome/rubric mapping and
actual QLoRA/GPU results remain unverified. No GPU or production-quality claim
is inferred from the CPU fixture, and the issue remains open.
