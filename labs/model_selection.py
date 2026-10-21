"""Reproducible digits experiment: train-only preprocessing, validation selection,
held-out evaluation, uncertainty, corruption slice and local CPU timing.

Requires requirements-advanced.txt; no download or external model is needed.
"""
from hashlib import sha256
from importlib.metadata import version
from math import sqrt
from time import perf_counter
import json
import platform

import numpy as np
from sklearn.datasets import load_digits
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, log_loss
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits


def wilson(correct: int, count: int, z: float = 1.959963984540054) -> list[float]:
    if type(count) is not int or type(correct) is not int or count <= 0 or not 0 <= correct <= count:
        raise ValueError('Valid binomial counts required')
    p = correct/count; denominator = 1+z*z/count
    center = (p+z*z/(2*count))/denominator
    half = z*sqrt(p*(1-p)/count+z*z/(4*count*count))/denominator
    return [max(0.0, center-half), min(1.0, center+half)]


def paired_interval(first, second, labels, seed=41):
    difference = (first == labels).astype(float) - (second == labels).astype(float)
    rng = np.random.default_rng(seed)
    draws = rng.choice(difference, (1000, len(labels)), replace=True).mean(axis=1)
    return np.quantile(draws, [0.025, 0.975]).tolist()


def experiment() -> dict:
    assert np.allclose(wilson(98,100), [0.929988209271456,0.9944980324498377])
    assert np.isclose(wilson(0,10)[0],0.0) and np.isclose(wilson(10,10)[1],1.0)
    dataset = load_digits()
    x, y = dataset.data, dataset.target
    indices = np.arange(len(y))
    train, remaining = train_test_split(indices, test_size=0.4, stratify=y, random_state=41)
    valid, test = train_test_split(remaining, test_size=0.5, stratify=y[remaining], random_state=42)
    assert not set(train) & set(valid) and not set(train) & set(test) and not set(valid) & set(test)
    candidates = []
    # Test labels never enter fitting, scaling or candidate selection.
    for regularization in (0.01, 0.1, 1.0):
        model = make_pipeline(StandardScaler(), LogisticRegression(C=regularization, max_iter=1500, random_state=41))
        model.fit(x[train], y[train])
        assert np.allclose(model[0].mean_, x[train].mean(axis=0))
        candidates.append((log_loss(y[valid], model.predict_proba(x[valid]), labels=np.arange(10)), regularization, model))
    validation_loss, selected_c, model = min(candidates, key=lambda row: row[0])
    baseline = DummyClassifier(strategy='most_frequent').fit(x[train], y[train])
    predicted, reference = model.predict(x[test]), baseline.predict(x[test])
    correct = int((predicted == y[test]).sum())
    # Defined corruption stress test; not a measured future deployment distribution.
    corrupted = x[test].copy(); corrupted[:, 24:40] = 0
    wrong = test[predicted != y[test]].tolist()
    # Warm-up and repeated one-sample calls include sklearn/Python overhead.
    model.predict(x[test[:1]])
    samples = []
    for row in x[test[:100]]:
        started = perf_counter(); model.predict(row.reshape(1, -1)); samples.append((perf_counter()-started)*1000)
    result = {'dataset':'sklearn bundled digits, 8x8 handwritten images', 'rows':len(y),
        'dataset_sha256':sha256(x.tobytes()+y.tobytes()).hexdigest(),
        'split':{'train':len(train),'validation':len(valid),'test':len(test),'seed':41},
        'selection':{'metric':'validation multiclass log loss','C':selected_c,'validation_loss':validation_loss},
        'test':{'accuracy':accuracy_score(y[test],predicted),'correct':correct,'count':len(test),
                'wilson_95':wilson(correct,len(test)), 'baseline_accuracy':accuracy_score(y[test],reference),
                'paired_bootstrap_accuracy_difference_95':paired_interval(predicted,reference,y[test]),
                'log_loss':log_loss(y[test],model.predict_proba(x[test]),labels=np.arange(10)),
                'confusion_matrix':confusion_matrix(y[test],predicted,labels=np.arange(10)).tolist(),
                'error_row_indices':wrong,
                'corruption_accuracy':accuracy_score(y[test],model.predict(corrupted))},
        'cpu_latency_ms':{'batch_size':1,'repetitions':100,'p50':float(np.percentile(samples,50)),'p95':float(np.percentile(samples,95))},
        'environment':{'python':platform.python_version(),'platform':platform.platform(),'sklearn':version('scikit-learn'),'numpy':version('numpy'),'threads':1},
        'limitations':['Random row split is not writer-independent; writer identities unavailable in this loader.',
                      'Wilson/bootstrap intervals assume approximately independent samples; correlated handwriting can make them optimistic.',
                      'Corruption slice and timing are local diagnostics, not production accuracy or load tests.']}
    assert result['test']['accuracy'] > result['test']['baseline_accuracy']
    assert len(wrong) == len(test)-correct
    return result


if __name__ == '__main__':
    with threadpool_limits(limits=1):
        print(json.dumps(experiment(),indent=2))
