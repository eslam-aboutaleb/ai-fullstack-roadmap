"""Detect one conflicting pair constraint before training or clustering."""
must_link = {frozenset(('a','b')),frozenset(('b','c'))}
cannot_link = {frozenset(('a','b'))}
assert must_link.intersection(cannot_link)
# A full constraint implementation also checks transitive components.
print('conflicting pair supervision detected before fitting')
