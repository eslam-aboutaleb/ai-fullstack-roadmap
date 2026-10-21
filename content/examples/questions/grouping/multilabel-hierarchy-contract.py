"""Multilabel decoding and an explicit parent closure."""
scores = {'billing':0.9,'access':0.8,'delivery':0.1}
labels = {key for key,value in scores.items() if value >= 0.7}
assert labels == {'billing','access'}
parents = {'billing':'support','access':'support','delivery':'support'}
closed = labels | {parents[label] for label in labels}
assert closed == {'billing','access','support'}
print('two valid intents retained; required parent added')
