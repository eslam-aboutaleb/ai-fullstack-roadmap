"""Standard-library training/evaluation capstone with analytic backpropagation.

A tiny 2→4→1 tanh classifier. Synthetic fixtures, fixed split, no provider or GPU.
"""
import json
import math
import random

TRAIN = [([-2.,-1.],0),([-1.,-2.],0),([-2.,0.],0),([0.,-2.],0),([1.,2.],1),([2.,1.],1),([2.,0.],1),([0.,2.],1)]
VALIDATION = [([-1.5,-.5],0),([-.5,-1.5],0),([1.5,.5],1),([.5,1.5],1)]
TEST = [([-1.,-.25],0),([-.25,-1.],0),([1.,.25],1),([.25,1.],1)]


def initial(seed=7):
    rng = random.Random(seed)
    # Flattened: eight W1 values, four b1, four W2, one b2.
    return [rng.uniform(-.3,.3) for _ in range(8)] + [0.]*4 + [rng.uniform(-.3,.3) for _ in range(4)] + [0.]


def forward(parameters, x):
    hidden = [math.tanh(x[0]*parameters[2*j] + x[1]*parameters[2*j+1] + parameters[8+j]) for j in range(4)]
    logit = sum(hidden[j]*parameters[12+j] for j in range(4)) + parameters[16]
    probability = 1/(1+math.exp(-logit)) if logit >= 0 else math.exp(logit)/(1+math.exp(logit))
    return hidden, logit, probability


def loss_and_gradient(parameters, rows):
    gradient=[0.]*17; loss=0.
    for x,y in rows:
        hidden,logit,p = forward(parameters,x)
        # BCE from logits avoids log(0) and large-exp overflow.
        loss += max(logit,0)-logit*y+math.log1p(math.exp(-abs(logit)))
        dz = p-y
        for j in range(4):
            dh = dz*parameters[12+j]*(1-hidden[j]**2)
            gradient[2*j] += dh*x[0]; gradient[2*j+1] += dh*x[1]
            gradient[8+j] += dh; gradient[12+j] += dz*hidden[j]
        gradient[16] += dz
    return loss/len(rows),[value/len(rows) for value in gradient]


def train(epochs=600, rate=.2):
    parameters=initial()
    baseline,_=loss_and_gradient(parameters,TRAIN)
    _,analytic=loss_and_gradient(parameters,TRAIN)
    errors=[]
    for index in range(len(parameters)):
        plus=parameters.copy();minus=parameters.copy();plus[index]+=1e-5;minus[index]-=1e-5
        numerical=(loss_and_gradient(plus,TRAIN)[0]-loss_and_gradient(minus,TRAIN)[0])/2e-5
        errors.append(abs(numerical-analytic[index]))
    assert max(errors)<1e-7,errors
    for _ in range(epochs):
        _,gradient=loss_and_gradient(parameters,TRAIN)
        parameters=[value-rate*delta for value,delta in zip(parameters,gradient)]
    loss,_=loss_and_gradient(parameters,TRAIN)
    accuracy=lambda rows:sum((forward(parameters,x)[2]>=.5)==bool(y) for x,y in rows)/len(rows)
    report={'seed':7,'epochs':epochs,'train_rows':len(TRAIN),'validation_rows':len(VALIDATION),'test_rows':len(TEST),
            'initial_loss':round(baseline,6),'final_loss':round(loss,6),'validation_accuracy':accuracy(VALIDATION),
            'test_accuracy':accuracy(TEST),'gradient_max_error':max(errors)}
    assert loss<.05 and loss<baseline
    assert report['validation_accuracy']==1 and report['test_accuracy']==1
    return report


if __name__=='__main__':
    print(json.dumps(train(),indent=2))
