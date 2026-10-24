"""Train a tiny causal character LM, freeze it and adapt only a low-rank output head.

Actual optimization and artifact reload on an authored miniature corpus. This is
not foundation-model SFT or a benchmark of language understanding. Optional CUDA
measurements are emitted only if explicitly requested on available hardware.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
import argparse
import hashlib
import json
import platform

import torch
from torch import nn
from torch.nn import functional as F

VOCAB = ' \nabcdefghijklmnopqrstuvwxyz0123456789.,:-'
BASE_TEXT = ('public policy: refunds within 14 days.\npublic guide: read the source.\n' * 8)
ADAPT_TEXT = ('api guide: retries use stable keys.\napi guide: deny private policy reads.\napi guide: cap stream buffers.\n' * 6)
VALID_TEXT = 'api guide: refunds use stable keys.\napi guide: read private buffers.\n'


def batches(text, device):
    encoded = torch.tensor([VOCAB.index(char) for char in text], device=device)
    size=32; count=(len(encoded)-1)//size
    x=encoded[:count*size].reshape(count,size)
    y=encoded[1:count*size+1].reshape(count,size)
    return x,y


class TinyLM(nn.Module):
    def __init__(self):
        super().__init__()
        self.embedding=nn.Embedding(len(VOCAB),32)
        self.position=nn.Embedding(32,32)
        layer=nn.TransformerEncoderLayer(32,4,64,dropout=0,batch_first=True)
        self.decoder=nn.TransformerEncoder(layer,1,enable_nested_tensor=False)
        self.head=nn.Linear(32,len(VOCAB))

    def features(self,x):
        positions=torch.arange(x.shape[1],device=x.device)
        embedded=self.embedding(x)+self.position(positions)
        mask=torch.triu(torch.ones(x.shape[1],x.shape[1],dtype=torch.bool,device=x.device),diagonal=1)
        return self.decoder(embedded,mask=mask)

    def forward(self,x):
        return self.head(self.features(x))


class Adapted(nn.Module):
    def __init__(self,base,rank=4):
        super().__init__(); self.base=base
        for parameter in base.parameters():
            parameter.requires_grad_(False);parameter.grad=None
        self.a=nn.Linear(32,rank,bias=False)
        self.b=nn.Linear(rank,len(VOCAB),bias=False)
        nn.init.zeros_(self.b.weight)
        self.scale=8/rank

    def forward(self,x):
        # Output-head-only adaptation: frozen features need no backward graph.
        with torch.no_grad():features=self.base.features(x)
        return self.base.head(features)+self.b(self.a(features))*self.scale


def fingerprint(model):
    digest=hashlib.sha256()
    for name,value in sorted(model.state_dict().items()):
        digest.update(name.encode());digest.update(value.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def loss(model,data):
    x,y=data
    return F.cross_entropy(model(x).reshape(-1,len(VOCAB)),y.reshape(-1))


def train(model,data,steps,rate):
    optimizer=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=rate)
    model.train()
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)
        value=loss(model,data);assert torch.isfinite(value)
        value.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.0);optimizer.step()
    model.eval()


def load_adapter(artifact,base,device):
    payload=torch.load(artifact,map_location=device,weights_only=True)
    manifest=payload['manifest']
    expected={'base_sha256':fingerprint(base),'vocab_sha256':hashlib.sha256(VOCAB.encode()).hexdigest(),
              'data_sha256':hashlib.sha256(ADAPT_TEXT.encode()).hexdigest(),'rank':4,'alpha':8}
    if manifest!=expected:
        raise ValueError('Adapter/base/vocabulary manifest mismatch')
    result=Adapted(base).to(device)
    result.a.load_state_dict(payload['a']);result.b.load_state_dict(payload['b']);result.eval()
    return result


def verify(device='cpu'):
    if device=='cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA was requested but is unavailable; no GPU result can be reported')
    torch.manual_seed(23);torch.set_num_threads(1)
    base=TinyLM().to(device)
    train(base,batches(BASE_TEXT,device),80,0.01)
    base_hash=fingerprint(base)
    adapted=Adapted(base).to(device)
    train_data,valid_data=batches(ADAPT_TEXT,device),batches(VALID_TEXT,device)
    with torch.no_grad():before=float(loss(adapted,train_data));valid_before=float(loss(adapted,valid_data))
    peak=None
    if device=='cuda':torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
    started=perf_counter();train(adapted,train_data,100,0.015)
    if device=='cuda':
        torch.cuda.synchronize();peak=torch.cuda.memory.max_memory_allocated()
    elapsed=perf_counter()-started
    with torch.no_grad():after=float(loss(adapted,train_data));valid_after=float(loss(adapted,valid_data))
    assert after < before and fingerprint(base)==base_hash
    assert all(not p.requires_grad for p in base.parameters())
    # Adaptation metadata binds exact base weights, vocabulary and training data.
    manifest={'base_sha256':base_hash,'vocab_sha256':hashlib.sha256(VOCAB.encode()).hexdigest(),
              'data_sha256':hashlib.sha256(ADAPT_TEXT.encode()).hexdigest(),'rank':4,'alpha':8}
    with TemporaryDirectory(prefix='roadmap-adapter-') as folder:
        artifact=Path(folder)/'adapter.pt'
        torch.save({'a':adapted.a.state_dict(),'b':adapted.b.state_dict(),'manifest':manifest},artifact)
        reloaded=load_adapter(artifact,base,device)
        with torch.no_grad():
            assert torch.allclose(adapted(valid_data[0]),reloaded(valid_data[0]),atol=1e-6)
            changed=valid_data[0].clone();changed[:,20:]=(changed[:,20:]+1)%len(VOCAB)
            assert torch.allclose(adapted(valid_data[0])[:,:20],adapted(changed)[:,:20],atol=1e-5), 'Future input leaked through the causal mask'
        invalid={**manifest,'base_sha256':'wrong-base'}
        torch.save({'a':adapted.a.state_dict(),'b':adapted.b.state_dict(),'manifest':invalid},artifact)
        try:load_adapter(artifact,base,device)
        except ValueError:pass
        else:raise AssertionError('Incompatible adapter was accepted')
    trainable=sum(p.numel() for p in adapted.parameters() if p.requires_grad)
    total=sum(p.numel() for p in adapted.parameters())
    assert trainable < total/10
    return {'task':'tiny character next-token LM; output-head low-rank adaptation','device':device,
        'seed':23,'torch':torch.__version__,'python':platform.python_version(),
        'trainable_parameters':trainable,'total_parameters':total,'base_weights_unchanged':True,
        'train_loss_before':before,'train_loss_after':after,'validation_loss_before':valid_before,'validation_loss_after':valid_after,
        'measured_adaptation_seconds':elapsed,'steps':100,'sequence_length':32,
        'parameter_bytes_only':sum(p.numel()*p.element_size() for p in adapted.parameters()),
        'cuda_peak_tensor_bytes':peak,
        'artifact_reload':'logits match; incompatible base rejected; causal prefix invariant passed','manifest':manifest,
        'limitations':['Authored miniature corpus; no foundation-model or domain-generalization claim.',
                      'Output-head adaptation only; not a full attention-layer LoRA implementation.',
                      'Parameter bytes exclude activations, optimizer state and allocator overhead.',
                      'CUDA fields are unmeasured on the default CPU path.']}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--device',choices=['cpu','cuda'],default='cpu')
    print(json.dumps(verify(parser.parse_args().device),indent=2))
