"""Demonstrate core algorithmic patterns in Python: two sum hash indexing, stack validation, and LRU cache."""

def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

def is_valid_parentheses(s: str) -> bool:
    matching = {')': '(', '}': '{', ']': '['}
    stack = []
    for char in s:
        if char in matching:
            if not stack or stack[-1] != matching[char]:
                return False
            stack.pop()
        else:
            stack.append(char)
    return len(stack) == 0

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.order = []

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.order.remove(key)
        self.order.append(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            oldest = self.order.pop(0)
            del self.cache[oldest]
        self.cache[key] = value
        self.order.append(key)

# Assertions verifying algorithm correctness
assert two_sum([2, 7, 11, 15], 9) == [0, 1]
assert is_valid_parentheses("({[]})") is True
assert is_valid_parentheses("([)]") is False

cache = LRUCache(2)
cache.put(1, 100)
cache.put(2, 200)
assert cache.get(1) == 100
cache.put(3, 300)
assert cache.get(2) == -1
assert cache.get(3) == 300

print("All core LeetCode algorithm patterns verified successfully.")

