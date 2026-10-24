"""Demonstrate deque sliding window and heapq streaming top-K selection."""
from collections import deque
import heapq

# Bounded ring-buffer sliding window
window: deque[int] = deque(maxlen=3)
for val in [10, 20, 30, 40]:
    window.append(val)
assert list(window) == [20, 30, 40]

# Streaming Top-K largest using min-heap
stream = [7, 2, 9, 4, 1, 8, 5, 6, 3]
top_3: list[int] = []
for num in stream:
    if len(top_3) < 3:
        heapq.heappush(top_3, num)
    elif num > top_3[0]:
        heapq.heapreplace(top_3, num)

assert sorted(top_3, reverse=True) == [9, 8, 7]
print("Deque ring-buffer and heapq streaming top-K verified successfully.")

