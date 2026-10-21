"""Response-only SFT labels plus a genuinely optimized miniature LoRA linear layer.

This is an executable numerical teaching lab. It is NOT QLoRA, HF PEFT or
foundation-model finetuning. The existing adapter_training.py separately
trains a small PyTorch causal character LM's frozen output head.
"""
from copy import deepcopy
from hashlib import sha256
import json
from math import isclose

BOS=0; EOS=1; PAD=2
def response_labels(prompt,response,max_length):
    if not prompt or not response:raise ValueError("prompt and response required")
    full=[BOS]+list(prompt)+list(response)+[EOS]
    if max_length<len(full):raise ValueError("never silently truncate supervised response")
    # At input position i, predict full[i+1]. Only tokens in the response/EOS
    # contribute to loss; BOS and prompt next-token labels are ignored.
    targets=[full[i+1] if i>=len(prompt) else -100 for i in range(len(full)-1)]
    inputs=full[:-1]
    padding=max_length-len(inputs)
    return {"input_ids":inputs+[PAD]*padding,
            "labels":targets+[-100]*padding,
            "attention_mask":[1]*len(inputs)+[0]*padding}

def effective_updates(examples,epochs,microbatch,accumulation):
    if min(examples,epochs,microbatch,accumulation)<1:
        raise ValueError("all positive")
    from math import ceil
    microsteps=ceil(examples/microbatch)*epochs
    return {"effective_batch":microbatch*accumulation,
            "microsteps":microsteps,"optimizer_steps":ceil(microsteps/accumulation)}

def projection(W,A,B,x,alpha):
    rank=len(A)
    z=[sum(a*xj for a,xj in zip(row,x)) for row in A]
    scale=alpha/rank
    return [sum(w*xj for w,xj in zip(row,x))+
            scale*sum(B[i][k]*z[k] for k in range(rank))
            for i,row in enumerate(W)]

def optimize_lora(W,x,y,steps=180,lr=.12,rank=1,alpha=1):
    if len(W)!=len(y) or any(len(row)!=len(x) for row in W):
        raise ValueError("base/output dimensionality mismatch")
    W_before=deepcopy(W)
    A=[[.5 if j==k%len(x) else 0. for j in range(len(x))]
       for k in range(rank)]
    B=[[0. for _ in range(rank)] for _ in range(len(y))]
    def loss():
        p=projection(W,A,B,x,alpha)
        return sum((a-b)**2 for a,b in zip(p,y))/2
    before=loss()
    for _ in range(steps):
        z=[sum(a*xj for a,xj in zip(row,x)) for row in A]
        errors=[p-target for p,target in zip(projection(W,A,B,x,alpha),y)]
        scale=alpha/rank
        grad_B=[[scale*error*zk for zk in z] for error in errors]
        grad_A=[[scale*sum(errors[i]*B[i][k] for i in range(len(y)))*xj
                 for xj in x] for k in range(rank)]
        for i in range(len(B)):
            for k in range(rank):B[i][k]-=lr*grad_B[i][k]
        for k in range(rank):
            for j in range(len(x)):A[k][j]-=lr*grad_A[k][j]
    assert W==W_before,"frozen base mutated"
    after=loss()
    merged=[[W[i][j]+(alpha/rank)*sum(B[i][k]*A[k][j] for k in range(rank))
             for j in range(len(x))] for i in range(len(y))]
    return {"initial_loss":before,"final_loss":after,
            "A":A,"B":B,"merged":merged,
            "trainable_parameters":rank*(len(x)+len(y)),
            "base_parameters":len(x)*len(y),
            "base_unchanged":W==W_before}

def load_manifest(manifest,*,base_sha,tokenizer_sha,template_sha):
    if {k:manifest.get(k) for k in ("base_sha","tokenizer_sha","template_sha")} != {
       "base_sha":base_sha,"tokenizer_sha":tokenizer_sha,"template_sha":template_sha}:
        raise ValueError("adapter incompatible with base/tokenizer/chat template")
    return True

def check():
    sample=response_labels([10,11],[20,21],7)
    assert sample["input_ids"]==[0,10,11,20,21,1,2]
    assert sample["labels"]==[-100,-100,-100,20,21,1,-100]
    assert sample["attention_mask"]==[1,1,1,1,1,1,0]
    assert effective_updates(103,3,8,4)=={"effective_batch":32,"microsteps":39,"optimizer_steps":10}
    W=[[1.,0.],[0.,1.]]
    results=optimize_lora(W,[1.,0.],[1.,2.])
    assert results["base_unchanged"]
    assert results["final_loss"]<results["initial_loss"]*.01
    assert results["trainable_parameters"]==4
    assert all(isclose(a,b,abs_tol=1e-8) for a,b in
               zip(projection(W,results["A"],results["B"],[1.,0.],1),
                   projection(results["merged"],[[0.,0.]],[[0.] for _ in W],[1.,0.],1)))
    identity=lambda x:sha256(x.encode()).hexdigest()
    manifest={"base_sha":identity("base"),"tokenizer_sha":identity("vocab"),
              "template_sha":identity("chat template")}
    assert load_manifest(manifest,base_sha=manifest["base_sha"],
                         tokenizer_sha=manifest["tokenizer_sha"],
                         template_sha=manifest["template_sha"])
    for fn in [lambda:response_labels([10],[20],2),
               lambda:effective_updates(10,1,0,2),
               lambda:load_manifest(manifest,base_sha=identity("wrong"),
                   tokenizer_sha=manifest["tokenizer_sha"],
                   template_sha=manifest["template_sha"])]:
        try:fn()
        except ValueError:pass
        else:raise AssertionError("invalid fine-tuning contract accepted")
    print("SFT/LoRA: target mask, accumulation, actual adapter gradient, merge, manifest PASS")
if __name__=="__main__":check()
