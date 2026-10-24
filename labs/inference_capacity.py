"""Deterministic LLM serving admission simulation (not a GPU/vLLM benchmark).

Each discrete step represents an illustrative decode interval. Prefill,
queuing and decode latency constants are caller-provided teaching assumptions.
"""
from dataclasses import dataclass
from math import ceil
from statistics import median

@dataclass(frozen=True)
class Request:
    identity: str
    arrival: int
    prompt: int
    output: int

def kv_bytes(*, layers, kv_heads, head_width, live_tokens, bytes_per_element, sequences=1):
    values=(layers,kv_heads,head_width,live_tokens,bytes_per_element,sequences)
    if any(type(x) is not int or x<=0 for x in values):
        raise ValueError("positive integral KV dimensions required")
    return 2*layers*kv_heads*head_width*live_tokens*bytes_per_element*sequences

def percentile_nearest_rank(values,p):
    if not values or not 0<p<=100:raise ValueError("invalid percentile")
    ordered=sorted(values)
    return ordered[ceil(p*len(ordered)/100)-1]

def serve(requests, *, max_sequences=2, max_active_tokens=200):
    if max_sequences<1 or max_active_tokens<1:raise ValueError("positive capacity")
    if len({r.identity for r in requests})!=len(requests):
        raise ValueError("unique request identities required")
    for r in requests:
        if r.arrival<0 or r.prompt<1 or r.output<1:
            raise ValueError("invalid request")
        if r.prompt+r.output>max_active_tokens:
            raise ValueError("single request exceeds KV capacity")
    waiting=sorted(requests,key=lambda r:(r.arrival,r.identity))
    active={};completed={};clock=0
    # Simplified continuous admission + one output token per active sequence/step.
    while waiting or active:
        for r in list(waiting):
            if r.arrival>clock:break
            current=sum(x["request"].prompt+x["request"].output for x in active.values())
            if len(active)<max_sequences and current+r.prompt+r.output<=max_active_tokens:
                active[r.identity]={"request":r,"start":clock,"done_tokens":0,"first":None}
                waiting.remove(r)
        for key in list(active):
            state=active[key]
            if state["first"] is None:state["first"]=clock+1
            state["done_tokens"]+=1
            if state["done_tokens"]==state["request"].output:
                r=state["request"]
                completed[key]={"ttft_steps":state["first"]-r.arrival,
                                "latency_steps":clock+1-r.arrival,
                                "queue_steps":state["start"]-r.arrival,
                                "output_tokens":r.output}
                del active[key]
        clock+=1
        if clock>100000:raise AssertionError("unexpected unbounded simulation")
    return {"per_request":completed,"elapsed_steps":clock,
            "p99_ttft_steps":percentile_nearest_rank([x["ttft_steps"] for x in completed.values()],99)
            if completed else None,
            "total_output_tokens":sum(x["output_tokens"] for x in completed.values())}

def check():
    mib=1024**2
    assert kv_bytes(layers=32,kv_heads=8,head_width=128,live_tokens=4096,
                    bytes_per_element=2)==512*mib
    jobs=[Request("a",0,40,3),Request("b",0,40,2),
          Request("c",0,40,1),Request("d",1,40,1)]
    parallel=serve(jobs,max_sequences=2,max_active_tokens=160)
    serial=serve(jobs,max_sequences=1,max_active_tokens=160)
    assert parallel["total_output_tokens"]==7
    assert parallel["elapsed_steps"]<serial["elapsed_steps"]
    assert parallel["per_request"]["c"]["queue_steps"]>0
    assert parallel["p99_ttft_steps"]>=1
    assert percentile_nearest_rank([1,2,100],99)==100
    for fn in [lambda:kv_bytes(layers=0,kv_heads=1,head_width=1,live_tokens=1,bytes_per_element=2),
               lambda:serve([Request("too-large",0,300,1)],max_active_tokens=300),
               lambda:serve([Request("same",0,1,1),Request("same",0,1,1)])]:
        try:fn()
        except ValueError:pass
        else:raise AssertionError("invalid inference contract was accepted")
    print("Inference scheduler: KV dimensions, bounded admission, TTFT/tails, invalid workload PASS")
if __name__=="__main__":check()
