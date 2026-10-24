"""Demonstrate amortized list growth versus tuple immutability."""
import sys

items: list[int] = []
sizes: list[int] = [sys.getsizeof(items)]
for i in range(9):
    items.append(i)
    sizes.append(sys.getsizeof(items))

# Tuple containing a mutable container
t = (1, [2, 3])
t[1].append(4)
assert t == (1, [2, 3, 4])

try:
    # Reassigning a tuple element is forbidden
    t[0] = 99  # type: ignore
    assert False, "Should have raised TypeError"
except TypeError:
    pass

print("List growth and tuple immutability boundaries verified successfully.")

