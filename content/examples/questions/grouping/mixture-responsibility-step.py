"""Normalize weighted component likelihoods for one observation."""
weights,likelihoods = [0.5,0.5],[0.8,0.2]
unnormalized = [w*p for w,p in zip(weights,likelihoods)]
responsibility = [p/sum(unnormalized) for p in unnormalized]
assert responsibility==[0.8,0.2]
print('responsibilities: [0.8, 0.2]; conditional on the declared mixture')
