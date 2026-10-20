"""Optional local NumPy/PyTorch bridge; CPU only, tiny synthetic data.

Tested with numpy 2.5.4 and torch 2.14.1. No model downloads or pickle loading.
"""
import json
import numpy as np
import torch
from .model_training import TRAIN, VALIDATION, TEST, initial, loss_and_gradient


def verify():
    torch.set_num_threads(1)
    rows=np.asarray([x for x,_ in TRAIN],dtype=np.float64)
    targets=np.asarray([y for _,y in TRAIN],dtype=np.float64)
    x=torch.from_numpy(rows); y=torch.from_numpy(targets)
    theta=torch.tensor(initial(),dtype=torch.float64,requires_grad=True)

    def logits(parameters,features=x):
        w1=parameters[:8].reshape(4,2);b1=parameters[8:12]
        w2=parameters[12:16];b2=parameters[16]
        return torch.tanh(features@w1.T+b1)@w2+b2

    def objective(parameters):
        return torch.nn.functional.binary_cross_entropy_with_logits(logits(parameters),y)

    loss=objective(theta);loss.backward()
    manual_loss,manual_gradient=loss_and_gradient(initial(),TRAIN)
    assert abs(loss.item()-manual_loss)<1e-12
    maximum=float(np.max(np.abs(theta.grad.numpy()-np.asarray(manual_gradient))))
    assert maximum<1e-10
    assert torch.autograd.gradcheck(objective,(theta,),eps=1e-6,atol=1e-5)
    optimizer=torch.optim.SGD([theta],lr=.2)
    for _ in range(600):
        optimizer.zero_grad(set_to_none=True)
        objective(theta).backward()
        optimizer.step()
    with torch.no_grad():
        def accuracy(data):
            features=torch.tensor([row for row,_ in data],dtype=torch.float64)
            labels=torch.tensor([target for _,target in data],dtype=torch.bool)
            return float(((logits(theta,features)>=0)==labels).double().mean())
        report={'manual_autograd_max_difference':maximum,'gradcheck':True,
                'final_loss':round(objective(theta).item(),6),
                'validation_accuracy':accuracy(VALIDATION),'test_accuracy':accuracy(TEST)}
    assert report['final_loss']<.05 and report['test_accuracy']==1
    # NumPy independently verifies the scalar attention calculation.
    query=np.array([[1.]],dtype=np.float64);keys=np.array([[1.],[0.]])
    scores=query@keys.T/np.sqrt(query.shape[-1]);weights=np.exp(scores-scores.max(axis=-1,keepdims=True));weights/=weights.sum(axis=-1,keepdims=True)
    assert np.allclose(weights,[[.7310585786300049,.2689414213699951]])
    print(json.dumps(report,indent=2))


if __name__=='__main__':verify()
