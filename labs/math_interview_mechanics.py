"""First-principles numerical AI: Bayes, gradient check and causal attention.

All computations use stdlib floats on tiny deterministic examples. These are
mechanism checks, NOT GPU/transformer throughput or held-out model quality.
"""
from math import exp, isclose, sqrt

def positive_predictive_value(prevalence, sensitivity, false_positive_rate):
    values=(prevalence,sensitivity,false_positive_rate)
    if any(not 0<=v<=1 for v in values):
        raise ValueError("probabilities must lie in [0,1]")
    numerator=prevalence*sensitivity
    denominator=numerator+(1-prevalence)*false_positive_rate
    if not denominator:
        raise ValueError("positive label event has zero probability")
    return numerator/denominator

def mse(w, x, y):
    return (w*x-y)**2

def mse_gradient(w,x,y):
    return 2*x*(w*x-y)

def finite_difference(fn, w, h=1e-5):
    if h<=0:raise ValueError("positive difference step required")
    return (fn(w+h)-fn(w-h))/(2*h)

def stable_softmax(logits, mask):
    if not logits or len(mask)!=len(logits):
        raise ValueError("logit/mask shape mismatch")
    if not any(mask):
        raise ValueError("all-masked softmax undefined")
    highest=max(x for x,allowed in zip(logits,mask) if allowed)
    values=[exp(x-highest) if allowed else 0 for x,allowed in zip(logits,mask)]
    total=sum(values)
    return [x/total for x in values]

def dot(a,b):
    if len(a)!=len(b) or not a:
        raise ValueError("equal positive dimensions required")
    return sum(x*y for x,y in zip(a,b))

def causal_attention(queries,keys,values):
    n=len(queries)
    if not n or len(keys)!=n or len(values)!=n:
        raise ValueError("sequence length mismatch")
    d=len(queries[0])
    if d<=0 or any(len(v)!=d for v in queries+keys):
        raise ValueError("key/query dimension mismatch")
    value_dim=len(values[0])
    if not value_dim or any(len(v)!=value_dim for v in values):
        raise ValueError("value dimension mismatch")
    out=[];all_weights=[]
    for t,query in enumerate(queries):
        logits=[dot(query,key)/sqrt(d) for key in keys]
        weights=stable_softmax(logits,[i<=t for i in range(n)])
        out.append([sum(weights[i]*values[i][j] for i in range(n))
                    for j in range(value_dim)])
        all_weights.append(weights)
    return out,all_weights

def check():
    result=positive_predictive_value(.01,.90,.05)
    assert isclose(result,.009/(.009+.0495),rel_tol=1e-12)
    assert 0.15<result<0.16, "a 90%-sensitive test need not have 90% PPV"
    analytic=mse_gradient(.25,3,1)
    numeric=finite_difference(lambda w:mse(w,3,1),.25)
    assert isclose(analytic,numeric,abs_tol=1e-7)
    new_w=.25-.01*analytic
    assert mse(new_w,3,1)<mse(.25,3,1)
    probs=stable_softmax([9000,8999,-50],[True,True,False])
    assert isclose(sum(probs),1,abs_tol=1e-12)
    assert probs[-1]==0 and probs[0]>probs[1]
    out,weights=causal_attention([[1,0],[0,1]],[[1,0],[0,1]],[[10,0],[0,20]])
    assert weights[0]==[1.0,0.0]
    assert out[0]==[10.0,0.0]
    assert len(out)==2 and out[1][1]>0
    try:stable_softmax([1,2],[False,False])
    except ValueError:pass
    else:raise AssertionError("all-masked row accepted")
    try:causal_attention([[1]],[[1]],[[1],[2]])
    except ValueError:pass
    else:raise AssertionError("sequence mismatch accepted")
    print("Numerical ML foundations: Bayes, analytic vs finite gradient, stable masked attention PASS")

if __name__=="__main__":
    check()
