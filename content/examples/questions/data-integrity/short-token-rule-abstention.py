"""Tiny reviewed dictionary with explicit abstention."""
def classify(text):
    phrase = ' '.join(text.casefold().split())
    return {'go': 'programming', 'r': 'programming', 'c++': 'programming'}.get(phrase, 'unknown')
assert 'go' in 'ongoing'
assert classify('ongoing') == 'unknown'
assert classify(' Go ') == 'programming'
assert classify('C++') == 'programming'
assert classify('not experienced with Go') == 'unknown'
print('short labels recognized; substrings and unsupported phrases abstain')
