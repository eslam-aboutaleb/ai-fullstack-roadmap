"""Demonstrate LRU Cache with O(1) operations using doubly linked list and hash map."""
from typing import Optional


class Node:

    def __init__(self, key: int = 0, val: int = 0):
        self.key: int = key
        self.val: int = val
        self.prev: Optional["Node"] = None
        self.next: Optional["Node"] = None


class LRUCache:

    def __init__(self, capacity: int):
        self.capacity: int = capacity
        self.cache: dict[int, Node] = {}
        self.head: Node = Node()
        self.tail: Node = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        prev_node, next_node = node.prev, node.next
        if prev_node and next_node:
            prev_node.next = next_node
            next_node.prev = prev_node

    def _add_to_front(self, node: Node) -> None:
        first = self.head.next
        node.next = first
        node.prev = self.head
        if first:
            first.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self._remove(self.cache[key])
        node = Node(key, value)
        self._add_to_front(node)
        self.cache[key] = node
        if len(self.cache) > self.capacity:
            lru = self.tail.prev
            if lru and lru != self.head:
                self._remove(lru)
                del self.cache[lru.key]


cache = LRUCache(2)
cache.put(1, 100)
cache.put(2, 200)
val1 = cache.get(1)
assert val1 == 100
cache.put(3, 300)
val2 = cache.get(2)
assert val2 == -1
val3 = cache.get(3)
assert val3 == 300
print(f"LRU Cache verified: capacity=2, get(1)={val1}, evicted key 2, get(2)={val2}, get(3)={val3}")

