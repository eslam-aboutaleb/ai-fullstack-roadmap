"""Actual Transformers + PEFT response-only causal-LM SFT on original synthetic text.

No pretrained weights, network, provider or GPU. A tiny randomly initialized
GPT-2 architecture is trained through real LoRA adapters. This verifies the
training/artifact contract; it does not establish foundation-model quality.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import importlib.metadata
import json
from pathlib import Path
import platform
import tempfile
import time

import torch
from peft import LoraConfig, PeftModel, TaskType, get_peft_model
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace
from transformers import GPT2Config, GPT2LMHeadModel, PreTrainedTokenizerFast

WORDS = ['<pad>', '<eos>', '<unk>', 'classify', 'red', 'blue', 'green', 'yellow', 'result', 'warm', 'cool', 'neutral'] + [f'item{i}' for i in range(64)]
VOCAB = {word: index for index, word in enumerate(WORDS)}
TEMPLATE = 'classify {color} {item} result'
COLORS = {'red': 'warm', 'yellow': 'warm', 'blue': 'cool', 'green': 'neutral'}


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def tokenizer():
    raw = Tokenizer(WordLevel(VOCAB, unk_token='<unk>'))
    raw.pre_tokenizer = Whitespace()
    return PreTrainedTokenizerFast(tokenizer_object=raw, pad_token='<pad>', eos_token='<eos>', unk_token='<unk>')


def examples(start, stop):
    # IDs are split before training and never overlap. Labels follow the original
    # explicit color rule; this controlled fixture is not a natural-language set.
    return [{'id': f'item{i}-{color}', 'prompt': TEMPLATE.format(color=color, item=f'item{i}'),
             'answer': answer} for i in range(start, stop) for color, answer in COLORS.items()]


def batch(rows, tok):
    inputs, labels, masks = [], [], []
    for row in rows:
        prompt = tok.encode(row['prompt'], add_special_tokens=False)
        response = tok.encode(row['answer'], add_special_tokens=False) + [tok.eos_token_id]
        inputs.append(prompt + response)
        labels.append([-100] * len(prompt) + response)
    length = max(map(len, inputs))
    for i in range(len(inputs)):
        missing = length - len(inputs[i])
        masks.append([1] * len(inputs[i]) + [0] * missing)
        inputs[i] += [tok.pad_token_id] * missing
        labels[i] += [-100] * missing
    return {'input_ids': torch.tensor(inputs), 'attention_mask': torch.tensor(masks), 'labels': torch.tensor(labels)}


def evaluate(model, rows, tok):
    model.eval()
    values = batch(rows, tok)
    with torch.no_grad():
        loss = float(model(**values).loss)
        # Score the first response token using only the prompt. Teacher-forced
        # target text is never supplied to this exact-label prediction.
        prompts = tok([row['prompt'] for row in rows], return_tensors='pt', padding=True)
        logits = model(**prompts).logits[:, -1, :]
        expected = torch.tensor([tok.encode(row['answer'], add_special_tokens=False)[0] for row in rows])
        accuracy = float((logits.argmax(dim=-1) == expected).float().mean())
    return {'response_loss': loss, 'label_accuracy': accuracy, 'cases': len(rows)}


def verify_manifest(expected, observed):
    for key in ('base_config_sha256', 'base_weights_sha256', 'tokenizer_sha256', 'template_sha256'):
        if expected[key] != observed.get(key):
            raise ValueError('incompatible adapter manifest: ' + key)


def run(output=None, steps=100):
    torch.set_num_threads(1)
    torch.manual_seed(7)
    torch.use_deterministic_algorithms(True)
    tok = tokenizer()
    config = GPT2Config(vocab_size=len(tok), n_positions=32, n_ctx=32, n_embd=32, n_layer=2,
                        n_head=2, resid_pdrop=0.0, embd_pdrop=0.0, attn_pdrop=0.0,
                        bos_token_id=tok.eos_token_id, eos_token_id=tok.eos_token_id,
                        pad_token_id=tok.pad_token_id, attn_implementation='eager')
    base = GPT2LMHeadModel(config)
    original = {name: value.detach().clone() for name, value in base.state_dict().items()}
    weights_hash = sha256(b''.join(original[key].numpy().tobytes() for key in sorted(original))).hexdigest()
    manifest = {'base_config_sha256': digest(config.to_dict()), 'base_weights_sha256': weights_hash,
                'tokenizer_sha256': digest(VOCAB), 'template_sha256': digest(TEMPLATE),
                'base_kind': 'random initialization; no pretrained model weights', 'seed': 7}
    train, validation, test = examples(0, 16), examples(16, 20), examples(20, 24)
    assert not ({r['id'] for r in train} & {r['id'] for r in validation + test})
    baseline_validation = evaluate(base, validation, tok)
    baseline_test = evaluate(base, test, tok)
    model = get_peft_model(base, LoraConfig(task_type=TaskType.CAUSAL_LM, r=4, lora_alpha=8,
                                          lora_dropout=0.0, target_modules=['c_attn', 'c_proj'], fan_in_fan_out=True))
    trainable = [(name, parameter) for name, parameter in model.named_parameters() if parameter.requires_grad]
    assert trainable and all('lora_' in name for name, _ in trainable)
    optimizer = torch.optim.AdamW([parameter for _, parameter in trainable], lr=0.02, weight_decay=0.0)
    data = batch(train, tok)
    assert torch.all(data['labels'][:, :4] == -100)
    assert torch.all(data['labels'][:, 4:] != -100)
    padded = batch([train[0], {**train[1], 'prompt': 'classify blue result'}], tok)
    assert padded['labels'][1, -1] == -100 and padded['attention_mask'][1, -1] == 0
    model.eval()
    with torch.no_grad():
        observed = model(**padded)
        expected_loss = torch.nn.functional.cross_entropy(
            observed.logits[:, :-1, :].reshape(-1, len(tok)),
            padded['labels'][:, 1:].reshape(-1), ignore_index=-100)
        assert torch.allclose(observed.loss, expected_loss, atol=1e-6)
    started = time.perf_counter()
    model.train()
    losses = []
    for step in range(steps):
        optimizer.zero_grad(set_to_none=True)
        # Two microbatches each supply half the supervised tokens; average before
        # stepping once. Equal token counts make this equal to the batch mean.
        total = 0.0
        for part in (slice(0, 32), slice(32, 64)):
            loss = model(**{key: value[part] for key, value in data.items()}).loss / 2
            loss.backward(); total += float(loss.detach())
        torch.nn.utils.clip_grad_norm_([parameter for _, parameter in trainable], 1.0)
        optimizer.step(); losses.append(total)
    training_seconds = time.perf_counter() - started
    assert losses[-1] < losses[0], losses
    # Every original base tensor is still exactly unchanged under LoRA.
    for name, before in original.items():
        target = name.replace('.c_attn.', '.c_attn.base_layer.').replace('.c_proj.', '.c_proj.base_layer.')
        current = model.base_model.model.state_dict()[target]
        assert torch.equal(before, current), name
    adapted_validation = evaluate(model, validation, tok)
    adapted_test = evaluate(model, test, tok)
    probe = tok('classify red item23 result', return_tensors='pt')
    model.eval()
    with torch.no_grad():
        reference = model(**probe).logits.detach().clone()
        # Appending future tokens cannot change an earlier causal prefix output.
        extended = dict(input_ids=torch.cat([probe['input_ids'], torch.tensor([[VOCAB['cool']]])], dim=1))
        assert torch.allclose(model(**extended).logits[:, :probe['input_ids'].shape[1]], reference, atol=1e-5, rtol=1e-5)
    with tempfile.TemporaryDirectory() as folder:
        target = Path(folder)
        model.save_pretrained(target / 'adapter', safe_serialization=True)
        tok.save_pretrained(target / 'tokenizer')
        (target / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        verify_manifest(manifest, json.loads((target / 'manifest.json').read_text()))
        incompatible = {**manifest, 'template_sha256': 'changed'}
        try: verify_manifest(manifest, incompatible)
        except ValueError: pass
        else: raise AssertionError('incompatible adapter accepted')
        fresh = GPT2LMHeadModel(config); fresh.load_state_dict(original)
        reloaded = PeftModel.from_pretrained(fresh, target / 'adapter'); reloaded.eval()
        with torch.no_grad():
            assert torch.allclose(reloaded(**probe).logits, reference, atol=1e-5, rtol=1e-5)
        merged = reloaded.merge_and_unload(); merged.eval()
        with torch.no_grad():
            assert torch.allclose(merged(**probe).logits, reference, atol=1e-4, rtol=1e-4)
    result = {'peft_causal_sft': 'PASS', 'versions': {key: importlib.metadata.version(key) for key in ('torch', 'transformers', 'peft', 'tokenizers', 'accelerate')},
              'hardware': platform.machine() + ' CPU', 'manifest': manifest, 'steps': steps,
              'effective_batch': 64, 'microbatches_per_step': 2,
              'trainable_parameters': sum(parameter.numel() for _, parameter in trainable),
              'baseline_validation': baseline_validation, 'adapted_validation': adapted_validation,
              'baseline_test': baseline_test, 'adapted_test': adapted_test,
              'initial_train_loss': losses[0], 'final_train_loss': losses[-1],
              'elapsed_training_seconds': training_seconds,
              'artifact_reload': 'pass', 'merge_equivalence': 'pass', 'base_immutable': True,
              'limits': 'original deterministic color-rule data and random tiny base; not pretrained SFT, QLoRA, GPU or production generalization evidence'}
    if output: Path(output).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output'); parser.add_argument('--steps', type=int, default=100)
    args = parser.parse_args()
    if not 1 <= args.steps <= 1000: parser.error('steps must be 1..1000')
    run(args.output, args.steps)
