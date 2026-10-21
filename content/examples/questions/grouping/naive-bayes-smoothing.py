"""Laplace smoothing for a tiny class-conditioned word vocabulary."""
vocabulary = ('refund', 'password', 'parcel')
counts = {'refund': 2, 'password': 0, 'parcel': 0}
alpha = 1
probability = {term:(counts[term]+alpha)/(sum(counts.values())+alpha*len(vocabulary)) for term in vocabulary}
assert probability['password'] > 0 and abs(sum(probability.values()) - 1) < 1e-12
print('unseen token has finite smoothed likelihood')
