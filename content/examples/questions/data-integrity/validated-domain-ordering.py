"""A genuinely linear rank domain with explicit unsupported comparisons."""
from dataclasses import dataclass
from functools import total_ordering
@total_ordering
@dataclass(frozen=True)
class Rank:
    value: int
    def __post_init__(self):
        if type(self.value) is not int or not 0 <= self.value <= 3:
            raise ValueError('invalid rank')
    def __lt__(self, other):
        if not isinstance(other, Rank):
            return NotImplemented
        return self.value < other.value
assert Rank(0) < Rank(1) < Rank(3)
assert Rank(2) >= Rank(2)
try:
    Rank(1) > 1
except TypeError:
    pass
else:
    raise AssertionError('unrelated type ordered')
try:
    Rank(-1)
except ValueError:
    pass
else:
    raise AssertionError('negative rank accepted')
print('valid ordering consistent; unrelated types and negative ranks rejected')
