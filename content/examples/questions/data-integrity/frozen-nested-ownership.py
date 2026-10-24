"""Frozen fields do not freeze nested containers."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Shallow:
    tags: list
@dataclass(frozen=True)
class Value:
    tags: tuple
    def __post_init__(self):
        if any(not isinstance(tag, str) or not tag for tag in self.tags):
            raise ValueError('tags must be nonempty strings')
        object.__setattr__(self, 'tags', tuple(self.tags))
original = ['alpha']
shallow, value = Shallow(original), Value(original)
original.append('beta')
assert shallow.tags == ['alpha', 'beta']
assert value.tags == ('alpha',)
print('shallow frozen changed through alias; immutable value stayed stable')
