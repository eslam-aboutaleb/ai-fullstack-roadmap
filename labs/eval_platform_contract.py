"""Immutable golden-case evaluation, judge calibration and release decisions.

No external dashboard, LLM judge, or online provider is called. Replays are
deterministic fixtures and should be compared by immutable case IDs/splits.
"""
from dataclasses import dataclass
from hashlib import sha256
import json

@dataclass(frozen=True)
class Case:
    id: str
    expected: tuple
    forbidden: tuple
    split: str

def fingerprint(cases):
    serialized=json.dumps([vars(c) for c in cases],sort_keys=True)
    return sha256(serialized.encode()).hexdigest()

def evaluate(cases, runs):
    if set(runs)!=set(c.id for c in cases):raise ValueError("dataset/run ID mismatch")
    scores={}
    for case in cases:
        result=runs[case.id]
        cited=set(result["citations"])
        relevant=set(case.expected)
        if not relevant:raise ValueError("nonempty expected evidence set required")
        if cited.intersection(case.forbidden):raise ValueError("unauthorized citation")
        # Strict source recall and answer support are separate measurements.
        recall=len(cited&relevant)/len(relevant)
        abstained=bool(result["abstained"])
        scores[case.id]={"recall":recall,"answer_supported":bool(result["supported"]),
                         "abstained":abstained,"split":case.split,
                         "trace_id":result["trace_id"]}
    return scores

def judge_confusion(human, judge):
    if set(human)!=set(judge):raise ValueError("paired labels required")
    if not human:raise ValueError("empty adjudication set")
    counts={"TP":0,"TN":0,"FP":0,"FN":0}
    for identity,label in human.items():
        if type(label) is not bool or type(judge[identity]) is not bool:
            raise ValueError("binary labels required")
        counts["TP" if judge[identity] and label else
               "FP" if judge[identity] else "FN" if label else "TN"]+=1
    return counts

def paired_gate(cases, baseline, candidate, *, max_unsupported=0, min_mean_recall=.80):
    before=evaluate(cases,baseline);after=evaluate(cases,candidate)
    if any(not score["answer_supported"] and not score["abstained"]
           for score in after.values()):
        return False,"unsupported answer"
    if any(b["recall"]==1. and a["recall"]<1. for b,a in zip(before.values(),after.values())):
        return False,"critical previously-correct retrieval regressed"
    avg=sum(row["recall"] for row in after.values())/len(after)
    if avg<min_mean_recall:return False,"mean recall below release threshold"
    return True,"paired fixture checks passed"

def check():
    cases=[Case("q1",("p1",),("other-tenant",),"release"),
           Case("q2",("p2","p3"),("other-tenant",),"release")]
    baseline={"q1":{"citations":["p1"],"abstained":False,"supported":True,"trace_id":"t1"},
              "q2":{"citations":["p2"],"abstained":False,"supported":True,"trace_id":"t2"}}
    candidate={"q1":dict(baseline["q1"]),"q2":{"citations":["p2","p3"],
                                     "abstained":False,"supported":True,"trace_id":"t3"}}
    assert paired_gate(cases,baseline,candidate)[0]
    assert fingerprint(cases)==fingerprint(list(cases))
    broken={**candidate,"q2":{**candidate["q2"],"supported":False}}
    assert paired_gate(cases,baseline,broken)[0] is False
    regressed={**candidate,"q1":{**candidate["q1"],"citations":[],"abstained":True}}
    assert paired_gate(cases,baseline,regressed)[0] is False
    forbidden={**candidate,"q1":{**candidate["q1"],"citations":["other-tenant"]}}
    try:evaluate(cases,forbidden)
    except ValueError:pass
    else:raise AssertionError("foreign tenant evidence accepted")
    assert judge_confusion({"a":True,"b":False,"c":False,"d":True},
                           {"a":True,"b":True,"c":False,"d":False})=={"TP":1,"TN":1,"FP":1,"FN":1}
    print("Eval gates: paired dataset, trace IDs, judge disagreement, release regression PASS")
if __name__=="__main__":check()
