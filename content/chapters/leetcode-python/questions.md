<!-- chapter: leetcode-python -->

# How do you solve Two Sum with optimal O(n) time complexity?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: leetcode-python
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Two Sum requires finding two distinct indices in an integer array whose values sum to a target integer. The optimal solution uses a single-pass hash map (Python `dict`) to store each seen number mapped to its index. For each element `num` at index `i`, we compute its required complement `target - num`. If the complement exists in the hash map, we immediately return the pair `[seen[complement], i]`. If not, we record `seen[num] = i` and proceed.

```python
def two_sum(nums: list[int], target: int) -> list[int]:
    seen: dict[int, int] = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of elements in `nums`. We perform exactly one pass through the list, and each dictionary insertion and lookup takes average $O(1)$ time.
- **Space Complexity:** $O(n)$ auxiliary memory to store at most $n$ key-value pairs in the `seen` hash map.

**Algorithmic mechanics and edge cases:**
Brute-force iteration using nested loops compares all $n(n - 1) / 2$ pairs, resulting in quadratic $O(n^2)$ time. A two-pointer approach over a sorted array achieves $O(n \log n)$ time due to sorting, but sorting alters the original indices unless paired with index tuples. The single-pass hash map resolves both speed and index stability. Edge cases include duplicate numbers that sum to the target (e.g., `nums = [3, 3]`, `target = 6`): the single-pass order checks the complement before inserting the second `3`, naturally preventing an index from pairing with itself.

## Why

A single-pass hash map replaces quadratic nested comparisons with O(1) complement lookups, reducing runtime from O(n^2) to linear O(n).

## Worked Case

For nums=[2, 7, 11, 15] and target=9: num=2 -> complement=7 (not in seen) -> seen={2: 0}; num=7 -> complement=2 (found at index 0) -> returns [0, 1].

## Risk

Inserting into the hash map before checking for the complement can allow a single element to pair with itself if target == 2 * num.

## Trade-off

The hash map trades O(n) auxiliary memory for an optimal O(n) runtime reduction compared to in-place nested loops.

## Try This

Test with duplicate values like nums=[3, 3] target=6, negative numbers, and arrays with no valid pair.

## Follow-ups

### What changes if the input array is already sorted in non-decreasing order?

If the array is already sorted (LeetCode 167), a bidirectional two-pointer approach achieves O(n) time with strictly O(1) auxiliary space, eliminating the hash map entirely.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html

# How do you validate balanced parentheses using a monotonic stack?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: leetcode-python
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Valid Parentheses (LeetCode 20) requires verifying that every opening bracket (`(`, `{`, `[`) has a corresponding closing bracket of the identical type in correct nested order. The optimal solution uses a Last-In, First-Out (LIFO) stack (implemented using Python's `list.append()` and `list.pop()`) combined with a hash map mapping each closing bracket to its required opening counterpart.

```python
def is_valid(s: str) -> bool:
    if len(s) % 2 != 0:
        return False
    matching = {')': '(', '}': '{', ']': '['}
    stack: list[str] = []
    for char in s:
        if char in matching:
            if not stack or stack[-1] != matching[char]:
                return False
            stack.pop()
        else:
            stack.append(char)
    return len(stack) == 0
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of string `s`. Each character is inspected once and pushed/popped from the stack at most once in $O(1)$ time.
- **Space Complexity:** $O(n)$ auxiliary space in the worst case (e.g., string consisting entirely of opening brackets `((((((`).

**Algorithmic mechanics and edge cases:**
An early optimization checks `if len(s) % 2 != 0: return False`, as balanced strings must have an even number of characters. For each character, if it is a closing bracket, the stack must neither be empty nor have a top element differing from the matching opening bracket. At the end of traversal, the stack must be empty (`len(stack) == 0`); if any unclosed opening brackets remain, the string is invalid. Edge cases include starting with a closing bracket (`)()` or `]`), strings with mismatched pairs (`(]`), and unclosed trailing brackets (`((()`).

## Why

A stack naturally enforces the LIFO nesting constraint of parentheses, matching the most recently opened symbol with the incoming closing bracket.

## Worked Case

For s='({[]})': '(' pushed, '{' pushed, '[' pushed; ']' matches top '[', popped; '}' matches top '{', popped; ')' matches top '(', popped; stack is empty -> True.

## Risk

Popping from an empty stack without an explicit emptiness guard raises an unhandled IndexError when a closing bracket arrives first.

## Trade-off

Using a stack requires O(n) auxiliary space in the worst case to guarantee O(n) single-pass validation.

## Try This

Test boundary cases: odd-length strings like '(', strings starting with closing brackets ')(', and deeply nested sequences '((([{}]))).'

## Follow-ups

### How do you solve Longest Valid Parentheses (LeetCode 32)?

Store indices instead of characters on the stack, initialized with a base index -1 to provide a boundary for substring length calculation whenever a valid pair is popped.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html

# How do you find the longest substring without repeating characters using a sliding window?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: leetcode-python
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Longest Substring Without Repeating Characters (LeetCode 3) requires finding the length of the longest contiguous substring containing no duplicate characters. The optimal solution uses a sliding window bounded by two pointers (`left` and `right`) along with a hash map (`last_seen`) recording the most recent index where each character appeared.

```python
def length_of_longest_substring(s: str) -> int:
    last_seen: dict[str, int] = {}
    max_length = 0
    left = 0
    for right, char in enumerate(s):
        if char in last_seen and last_seen[char] >= left:
            left = last_seen[char] + 1
        last_seen[char] = right
        max_length = max(max_length, right - left + 1)
    return max_length
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of string `s`. The `right` pointer advances from $0$ to $n-1$, and the `left` pointer jumps monotonically forward without backtracking.
- **Space Complexity:** $O(\min(n, m))$ auxiliary memory for the hash map, where $m$ is the size of the character alphabet (e.g., at most 128 for standard ASCII or 26 for lowercase English).

**Algorithmic mechanics and edge cases:**
A naive sliding window removes characters one-by-one from the left until the duplicate is evicted, taking $2n$ steps. Storing `last_seen[char]` allows the `left` pointer to jump immediately past the duplicate in $O(1)$ time. Crucially, the condition `last_seen[char] >= left` ensures we ignore duplicates that occur before the current window's left boundary. Edge cases include empty strings (`'' -> 0`), single-character strings (`'a' -> 1`), strings with all identical characters (`'bbbbb' -> 1`), and strings with no repeating characters (`'abcdef' -> 6`).

## Why

A sliding window with last-seen index mapping allows the left pointer to jump directly past duplicate occurrences in O(1) time without element-by-element eviction.

## Worked Case

For s='abcabcbb': window expands 'abc' (len 3); on second 'a' at idx 3, left jumps to last_seen['a']+1=1; window becomes 'bca' (len 3); max_length remains 3.

## Risk

Failing to check last_seen[char] >= left can cause the left pointer to jump backwards when encountering a character seen outside the active window.

## Trade-off

The hash map consumes O(min(n, m)) space to reduce what would be an O(n^2) nested scan to a strict O(n) single-pass traversal.

## Try This

Trace with string 'abba' to verify that when the second 'a' is encountered at index 3, left does not regress backwards from index 2 to index 1.

## Follow-ups

### How does the algorithm adapt if at most K duplicate characters are permitted?

Use a character frequency counter (Counter or defaultdict) and shrink the left pointer one step at a time whenever the sum of duplicates exceeds the allowed quota K.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html

# How do you find the maximum subarray sum using Kadane's algorithm?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: leetcode-python
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Maximum Subarray (LeetCode 53) seeks the contiguous subarray having the largest sum within a given integer array. Kadane's algorithm solves this in linear $O(n)$ time and $O(1)$ space using dynamic programming. At each index $i$, the optimal choice is whether to extend the previous running subarray sum (`current_sum + nums[i]`) or start a fresh subarray at `nums[i]` (`max(nums[i], current_sum + nums[i])`).

```python
def max_sub_array(nums: list[int]) -> int:
    if not nums:
        return 0
    max_sum = current_sum = nums[0]
    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    return max_sum
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of elements in `nums`. We visit each number exactly once in a single sequential pass.
- **Space Complexity:** $O(1)$ auxiliary space, as only two scalar variables (`current_sum` and `max_sum`) are maintained.

**Algorithmic mechanics and edge cases:**
The core invariant is that a negative prefix sum can never contribute positively to any subsequent subarray; discarding it by restarting at `num` is always optimal. Initializing `max_sum` and `current_sum` to `nums[0]` (rather than 0) correctly handles arrays consisting exclusively of negative numbers (e.g., `[-3, -2, -5]` returns `-2`, not `0`). Edge cases include single-element arrays (`[5] -> 5`), all-negative arrays, arrays with alternating large positives and negatives, and arrays with all zeroes.

## Why

Kadane's algorithm leverages the optimal substructure invariant: an incoming number either benefits from extending the existing sum or starts a superior new subarray.

## Worked Case

For nums=[-2, 1, -3, 4, -1, 2, 1, -5, 4]: current_sum resets to 1 at idx 1; extends to 4 at idx 3; peaks at 6 for subarray [4, -1, 2, 1]; returns 6.

## Risk

Initializing max_sum to 0 instead of nums[0] causes incorrect outputs for arrays composed entirely of negative numbers.

## Trade-off

Kadane's algorithm computes the maximum scalar sum in O(1) space, but reconstructing the exact subarray indices requires storing start and end pointers.

## Try This

Test with an all-negative list like [-2, -1, -3] to verify it returns -1 rather than 0, and with mixed values [-2, 1, -3, 4, -1, 2, 1, -5, 4].

## Follow-ups

### How do you solve Maximum Product Subarray (LeetCode 152)?

Maintain both running maximum and minimum products at each step, because multiplying a negative number by a negative minimum can produce the new maximum product.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html

# How do you solve Best Time to Buy and Sell Stock in a single pass?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: leetcode-python
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Best Time to Buy and Sell Stock (LeetCode 121) requires determining the maximum profit achievable by choosing a single day to buy one stock and a subsequent day to sell it. The optimal solution maintains a running minimum purchase price (`min_price`) and calculates the profit achievable by selling at the current day's price (`price - min_price`), updating `max_profit` whenever a superior spread is found.

```python
def max_profit(prices: list[int]) -> int:
    if not prices:
        return 0
    min_price = float('inf')
    max_profit = 0
    for price in prices:
        if price < min_price:
            min_price = price
        elif price - min_price > max_profit:
            max_profit = price - min_price
    return max_profit
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of price entries. We inspect each daily price exactly once.
- **Space Complexity:** $O(1)$ auxiliary space, maintaining only two scalar variables.

**Algorithmic mechanics and edge cases:**
This problem is isomorphic to finding the maximum difference between two elements where the smaller element precedes the larger element. Tracking `min_price` dynamically ensures we only evaluate valid forward temporal transitions (you cannot sell before you buy). If prices continually decline (e.g., `[7, 6, 4, 3, 1]`), `max_profit` remains `0`. Edge cases include empty lists (`[] -> 0`), single-day lists (`[5] -> 0`), monotonically decreasing prices, and identical prices (`[3, 3, 3] -> 0`).

## Why

Tracking the cumulative historical minimum price in a single forward pass guarantees that any evaluated profit satisfies temporal causality in O(1) space.

## Worked Case

For prices=[7, 1, 5, 3, 6, 4]: price=7 -> min=7, profit=0; price=1 -> min=1, profit=0; price=5 -> profit=4; price=6 -> profit=5; returns 5.

## Risk

Resetting min_price without checking whether the current price produces a superior profit compared to an earlier buy point breaks optimal spread tracking.

## Trade-off

Single-pass tracking applies strictly when exactly one buy and one sell transaction is permitted; multiple transactions require greedy slope accumulation.

## Try This

Run with monotonically decreasing prices [7, 6, 4, 3, 1] to assert zero profit, and with volatile prices [7, 1, 5, 3, 6, 4] to verify profit of 5.

## Follow-ups

### What changes for Best Time to Buy and Sell Stock II (LeetCode 122) with unlimited transactions?

Apply a greedy approach: accumulate price[i] - price[i-1] whenever price[i] > price[i-1], capturing every upward slope without complex state management.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html

# How do you find Top K Frequent Elements in O(n) time using bucket sort?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: leetcode-python
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Top K Frequent Elements (LeetCode 347) asks for the $k$ most frequent elements from an integer array. While a min-heap over a frequency dictionary yields $O(n \log k)$ runtime, bucket sort achieves linear $O(n)$ time. The algorithm counts frequencies using `collections.Counter`, then creates an array of buckets where bucket index represents frequency (from $0$ to $n$), and `buckets[freq]` stores the list of elements having that exact frequency.

```python
from collections import Counter

def top_k_frequent(nums: list[int], k: int) -> list[int]:
    counts = Counter(nums)
    buckets: list[list[int]] = [[] for _ in range(len(nums) + 1)]
    for num, freq in counts.items():
        buckets[freq].append(num)
    result: list[int] = []
    for freq in range(len(buckets) - 1, 0, -1):
        for num in buckets[freq]:
            result.append(num)
            if len(result) == k:
                return result
    return result
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is `len(nums)`. Counting takes $O(n)$, populating buckets takes $O(m) \le O(n)$, and scanning backwards from frequency $n$ down to $1$ stops as soon as $k$ elements are gathered.
- **Space Complexity:** $O(n)$ auxiliary space to store frequency counts and $n + 1$ bucket slots.

**Algorithmic mechanics and edge cases:**
Bucket sort works here because frequency is strictly bounded by array length $n$, avoiding comparison-based sorting limits ($O(n \log n)$). Traversing buckets in descending order from $n$ guarantees that the most frequent elements are appended first. Edge cases include $k$ equal to the number of unique elements (returns all unique elements), all elements having frequency 1, and single-element inputs (`nums=[1], k=1 -> [1]`).

## Why

Because frequency is an integer bounded by [1, n], bucket sort partitions elements by frequency in O(n) time, beating comparison-based O(n log k) heaps.

## Worked Case

For nums=[1, 1, 1, 2, 2, 3], k=2: counts={1: 3, 2: 2, 3: 1}; buckets[3]=[1], buckets[2]=[2], buckets[1]=[3]; iterating backwards yields [1, 2].

## Risk

Creating buckets of size max(counts.values()) without padding up to len(nums) + 1 can cause index out of bounds when all elements are identical.

## Trade-off

Bucket sort achieves O(n) time by allocating an array of n + 1 bucket lists, which uses more memory than an O(k) min-heap for small values of k.

## Try This

Test with nums=[1, 1, 1, 2, 2, 3] and k=2 to verify result is [1, 2], and with negative numbers nums=[-1, -1, 2] k=1 to verify [-1].

## Follow-ups

### When is a min-heap preferable to bucket sort for Top-K?

When processing a streaming dataset where total elements n is unbounded or unknown, a fixed-size min-heap of capacity k processes incoming items in O(log k) per element.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html

# How do you implement an LRU Cache with O(1) get and put operations?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: leetcode-python
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** An LRU (Least Recently Used) Cache (LeetCode 146) requires retrieving values by key (`get`) and inserting/updating values (`put`) in strict $O(1)$ average time, while evicting the least recently accessed key when capacity is exceeded. The optimal data structure combines a hash map (`dict`) with a doubly linked list. The hash map maps keys to doubly linked list nodes for $O(1)$ pointer lookups, while the doubly linked list maintains access recency with sentinel head and tail nodes for $O(1)$ node insertion and removal.

```python
class Node:
    def __init__(self, key: int = 0, val: int = 0):
        self.key = key
        self.val = val
        self.prev: Node | None = None
        self.next: Node | None = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: dict[int, Node] = {}
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        prev_node, next_node = node.prev, node.next
        prev_node.next, next_node.prev = next_node, prev_node

    def _add_to_front(self, node: Node) -> None:
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
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
            self._remove(lru)
            del self.cache[lru.key]
```

**Complexity analysis:**
- **Time Complexity:** $O(1)$ for both `get` and `put`. Hash map lookup and update is $O(1)$, and doubly linked list pointer manipulation is $O(1)$.
- **Space Complexity:** $O(c)$ auxiliary memory where $c$ is the configured `capacity` of the cache.

**Algorithmic mechanics and edge cases:**
Sentinel `head` and `tail` nodes eliminate null-pointer edge cases during insertions and deletions. The `Node` object must store its corresponding `key` so that when `self.tail.prev` is evicted from the list, its key can be deleted from `self.cache` in $O(1)$ without an expensive reverse lookup. In Python production code, `collections.OrderedDict` provides this exact combination (`move_to_end` and `popitem(last=False)`), but interviewers universally expect candidate implementation of the underlying doubly linked list.

## Why

A hash map provides O(1) key-to-node addressing, while a doubly linked list provides O(1) splicing and reordering of nodes without array shifts.

## Worked Case

Capacity 2: put(1, 1), put(2, 2); get(1) moves 1 to front; put(3, 3) evicts tail.prev (key 2); get(2) returns -1; get(3) and get(1) return 3 and 1.

## Risk

Omitting the key from the linked list Node prevents deleting the evicted LRU node from the hash map in O(1) time.

## Trade-off

Maintaining four pointers per node (prev, next, hash bucket links) increases memory overhead compared to an array or simple dict.

## Try This

Initialize LRUCache(2), put (1, 1), put (2, 2), get 1, put (3, 3), and assert that get(2) returns -1 because key 2 was the least recently used.

## Follow-ups

### How do you implement an LFU (Least Frequently Used) Cache (LeetCode 460)?

Maintain a min_frequency integer, a frequency-to-doubly-linked-list map, and a key-to-node map, updating node frequencies and incrementing min_frequency accordingly.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html

# How do you count the number of islands in a 2D grid using BFS or DFS?

<!-- meta
answer_format: conceptual
domain: foundations
subdomain: leetcode-python
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Number of Islands (LeetCode 200) requires finding the number of distinct connected components of `'1'`s (land) surrounded by `'0'`s (water) in an $m \times n$ grid. Land cells connect horizontally or vertically. We iterate through every cell $(r, c)$; whenever an unvisited land cell (`grid[r][c] == '1'`) is encountered, we increment the island count and initiate a Breadth-First Search (BFS) or Depth-First Search (DFS) to explore and sink or mark all connected land cells in the island.

```python
from collections import deque

def num_islands(grid: list[list[str]]) -> int:
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])
    islands = 0

    def bfs(r: int, c: int) -> None:
        queue = deque([(r, c)])
        grid[r][c] = '0'  # Mark visited by sinking land to water
        while queue:
            row, col = queue.popleft()
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == '1':
                    grid[nr][nc] = '0'  # Mark visited IMMEDIATELY upon enqueue!
                    queue.append((nr, nc))

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                islands += 1
                bfs(r, c)
    return islands
```

**Complexity analysis:**
- **Time Complexity:** $O(m \times n)$ where $m$ is rows and $n$ is columns. Every cell is visited at most twice: once in the outer loops, and once during BFS/DFS traversal.
- **Space Complexity:** $O(\min(m, n))$ for BFS queue memory (diagonal across grid), or $O(m \times n)$ worst-case call stack for DFS in a grid consisting entirely of land.

**Algorithmic mechanics and edge cases:**
A critical BFS invariant is **marking cells as visited immediately upon enqueueing** (`grid[nr][nc] = '0'`). Delaying the visited mutation until dequeuing causes adjacent cells to re-enqueue identical nodes repeatedly, exploding memory usage to $O(m \times n)$ and causing severe queue bloat. Mutating the input grid in-place avoids allocating a separate `visited` set; if mutating the grid is forbidden, maintain a set of `(row, col)` tuples. Edge cases include empty grids, grids consisting entirely of water (`'0'`), grids consisting entirely of land (`'1'`), and diagonal disconnected cells.

## Why

Graph traversal (BFS/DFS) groups connected components by systematically visiting and marking adjacent land cells, preventing duplicate island counts.

## Worked Case

For grid=[['1','1','0'],['1','1','0'],['0','0','1']]: BFS at (0,0) sinks (0,0),(0,1),(1,0),(1,1) -> island 1; cell (2,2) found -> island 2; returns 2.

## Risk

Marking cells visited on pop rather than on push in BFS causes duplicate queue insertions, causing MemoryLimitExceeded on dense grids.

## Trade-off

Mutating the grid in-place achieves O(min(m, n)) space but destroys original input data; using a visited set preserves data at the cost of O(m*n) space.

## Try This

Test a grid with only diagonal land [['1', '0'], ['0', '1']] to assert that it yields 2 distinct islands rather than 1.

## Follow-ups

### How do you solve Max Area of Island (LeetCode 695)?

Instead of merely sinking the island, return an integer area from the traversal by accumulating 1 for each visited land cell and updating global max_area.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html

# How do you find the container that can hold the most water?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Container With Most Water (LeetCode 11) finds two vertical lines in an array of heights that, together with the x-axis, form a container holding the maximum area of water. The optimal solution uses two converging pointers (`left` and `right`) initialized at opposite ends of the array, greedily moving the pointer with the smaller height inward at each step.

```python
def max_area(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    max_water = 0
    while left < right:
        width = right - left
        current_height = min(height[left], height[right])
        max_water = max(max_water, width * current_height)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_water
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `height`. The pointers converge inwards with each step visiting a new element until they meet.
- **Space Complexity:** $O(1)$ auxiliary space because only scalar pointer and area variables are maintained.

**Algorithmic mechanics and edge cases:**
The area is bounded by the shorter line: $\text{area} = (\text{right} - \text{left}) \times \min(h[l], h[r])$. Moving the taller line inward cannot increase the area because the width strictly decreases while the height remains constrained by the shorter line. Therefore, only by moving the shorter line inward is there any possibility of finding a taller boundary that offsets the width reduction. Edge cases include two-element arrays, monotonically decreasing or increasing heights, and flat arrays where all heights are equal.

## Why

Greedily discarding the shorter boundary is provably optimal because no interior line can form a larger rectangle with that shorter boundary.

## Worked Case

For [1,1]: width=1, min_h=1, area=1. Pointers meet. Result: 1. For [4,3,2,1,4]: ends 0 and 4 have height 4; width=4, area=16. Any inner move reduces width and cannot exceed height 4.

## Risk

Brute-force nested loops inspect O(n^2) pairs, timing out on arrays with tens of thousands of elements.

## Trade-off

Two-pointer greedy traversal is strictly linear but relies on the geometric property that height is constrained by the minimum of the two ends.

## Try This

Trace with height=[1, 8, 6, 2, 5, 4, 8, 3, 7] and observe that left=1 (h=8) and right=8 (h=7) produce area 7*7=49.

## Follow-ups

### What if both lines have identical heights height[left] == height[right]?

You can safely move either pointer (or both) inward, because neither line can form a larger container with any intermediate interior point.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find all unique triplets in an array that sum to zero?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** 3Sum (LeetCode 15) finds all unique triplets `[nums[i], nums[j], nums[k]]` such that $i \neq j \neq k$ and their sum equals zero. The optimal solution sorts the array in $O(n \log n)$ time, then iterates through each element using a two-pointer scan for the remaining two elements, with explicit duplicate skipping.

```python
def three_sum(nums: list[int]) -> list[list[int]]:
    nums.sort()
    res: list[list[int]] = []
    n = len(nums)
    for i in range(n - 2):
        if nums[i] > 0:
            break  # Smallest element > 0 cannot sum to 0
        if i > 0 and nums[i] == nums[i - 1]:
            continue  # Skip duplicate first element
        left, right = i + 1, n - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                res.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
    return res
```

**Complexity analysis:**
- **Time Complexity:** $O(n^2)$ where $n$ is the length of `nums`. Sorting takes $O(n \log n)$, and the outer loop runs $n$ times with an inner $O(n)$ two-pointer scan.
- **Space Complexity:** $O(1)$ auxiliary space (ignoring output and sorting space) or $O(n)$ for Python's Timsort buffer.

**Algorithmic mechanics and edge cases:**
Sorting clusters duplicate elements together. To guarantee uniqueness in the output without a costly `set` of tuples, we skip adjacent duplicate values at three places: when picking `nums[i]`, and when advancing `left` and `right` after finding a valid triplet. Edge cases include arrays with fewer than 3 elements (returns `[]`), all zeros `[0, 0, 0, 0]`, and arrays with no valid triplets.

## Why

Sorting converts a 3D search space into n linear two-pointer scans while providing deterministic duplicate elimination.

## Worked Case

Sorted: [-4, -1, -1, 0, 1, 2]. i=0 (-4): total min is -4+-1+2=-3 < 0, no match. i=1 (-1): left=2 (-1), right=5 (2) -> total 0! Add [-1, -1, 2]. left advances to 3 (0), right to 4 (1) -> total 0! Add [-1, 0, 1].

## Risk

Failing to skip duplicate values when advancing left and right creates redundant triplets in the output.

## Trade-off

Sorting mutates the input array (or requires an O(n) sorted copy) but avoids hash table collision and hashing overhead.

## Try This

Test with nums=[-1, 0, 1, 2, -1, -4] to verify that [-1, -1, 2] and [-1, 0, 1] are identified without duplicates.

## Follow-ups

### How do you generalize 3Sum to kSum in optimal polynomial time?

Use recursion reducing kSum to (k-1)Sum by fixing one element, terminating at base case 2Sum solved with two pointers in O(n^(k-1)) time.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you calculate the total amount of trapped rainwater in an elevation map?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Trapping Rain Water (LeetCode 42) computes how much water an elevation map can trap after raining. The optimal solution uses two pointers (`left` and `right`) tracking `left_max` and `right_max` boundaries, computing trapped water in a single linear pass with $O(1)$ auxiliary memory.

```python
def trap(height: list[int]) -> int:
    if not height:
        return 0
    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1
    return water
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `height`. Each bar is visited exactly once as the two pointers converge.
- **Space Complexity:** $O(1)$ auxiliary space because it avoids precomputing left and right prefix maximum arrays.

**Algorithmic mechanics and edge cases:**
The water trapped above any bar at index $i$ is determined by $\min(\text{left\_max}, \text{right\_max}) - \text{height}[i]$. By advancing the pointer with the smaller height, we guarantee that the current bar's trapped water is strictly bounded by its own side's maximum, because the opposite side already has an even taller barrier. Edge cases include empty arrays, monotonic staircases (which trap 0 water), and inverted pyramids.

## Why

The two-pointer technique determines the limiting boundary on the fly, eliminating the two O(n) prefix/suffix maximum arrays.

## Worked Case

height=[4,2,0,3,2,5]. left=0 (4), right=5 (5). Since 4 < 5, process left: idx 1 height 2, water += 4-2=2. idx 2 height 0, water += 4-0=4. idx 3 height 3, water += 4-3=1. idx 4 height 2, water += 4-2=2. Total = 9.

## Risk

Monotonic decreasing or increasing arrays trap zero water; boundary checks must handle flat elevations safely.

## Trade-off

Two-pointer O(1) space is faster and more cache-friendly than monotonic stack approaches which require O(n) memory.

## Try This

Trace with height=[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1] to confirm that 6 units of water are trapped.

## Follow-ups

### How would you solve this using a monotonic decreasing stack?

Store bar indices in a monotonic stack; when a taller bar arrives, pop the trough, compute bounded height min(curr, stack[-1]) - trough, and multiply by width.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you construct the product of an array except self without using division?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Product of Array Except Self (LeetCode 238) returns an array `output` such that `output[i]` is equal to the product of all elements of `nums` except `nums[i]`, without using the division operation. The optimal solution uses a prefix product pass followed by a backward postfix product accumulation directly in the output array.

```python
def product_except_self(nums: list[int]) -> list[int]:
    n = len(nums)
    res = [1] * n
    # Prefix products
    prefix = 1
    for i in range(n):
        res[i] = prefix
        prefix *= nums[i]
    # Postfix products accumulated directly into res
    postfix = 1
    for i in range(n - 1, -1, -1):
        res[i] *= postfix
        postfix *= nums[i]
    return res
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. Two linear passes iterate over the array.
- **Space Complexity:** $O(1)$ auxiliary space beyond the output array itself, as the running postfix variable stores the running product.

**Algorithmic mechanics and edge cases:**
For any element $i$, the result is $\prod_{j < i} nums[j] \times \prod_{j > i} nums[j]$. The first pass populates `res[i]` with the product of all elements to its left. The second pass walks backwards, multiplying `res[i]` by the running product of all elements to its right. Edge cases include arrays containing one zero (only the zero index gets a non-zero product), multiple zeros (all outputs are zero), and negative numbers.

## Why

Accumulating prefix and postfix products directly in the output array eliminates the need for division or extra arrays.

## Worked Case

nums=[-1, 1, 0, -3, 3]. Prefix pass: [1, -1, -1, 0, 0]. Postfix pass from right: idx 2 (zero) gets prefix -1 * postfix 9 = 0? Postfix at idx 2 is (-3)*3=-9, so res[2] = (-1) * (-9) = 9. Other indices hit 0.

## Risk

Using division (total_product // nums[i]) crashes on arrays containing zero (ZeroDivisionError) and violates interview constraints.

## Trade-off

Doing two passes in opposite directions trades an extra linear scan for strictly O(1) auxiliary memory.

## Try This

Test with nums=[1, 2, 3, 4]: prefix pass produces [1, 1, 2, 6]; postfix pass multiplies by [24, 12, 4, 1] yielding [24, 12, 8, 6].

## Follow-ups

### What happens if there are two or more zeros in nums?

Every single element in the output array will be 0, because excluding any one zero leaves at least one other zero in the remaining product.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you merge overlapping intervals into a consolidated set of non-overlapping intervals?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Merge Intervals (LeetCode 56) merges all overlapping intervals in a collection into mutually non-overlapping intervals spanning the same ranges. The optimal solution sorts intervals by their start times, then iterates through them, merging overlapping adjacent intervals into the current active interval.

```python
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged: list[list[int]] = [intervals[0]]
    for start, end in intervals[1:]:
        last_end = merged[-1][1]
        if start <= last_end:
            merged[-1][1] = max(last_end, end)
        else:
            merged.append([start, end])
    return merged
```

**Complexity analysis:**
- **Time Complexity:** $O(n \log n)$ where $n$ is the number of intervals, dominated by sorting the intervals by start time. The subsequent linear pass takes $O(n)$.
- **Space Complexity:** $O(n)$ space for Python's Timsort algorithm and the output list.

**Algorithmic mechanics and edge cases:**
After sorting by start time, if interval $B$ overlaps with interval $A$ (where $A$ precedes $B$), it must satisfy $B.\text{start} \le A.\text{end}$. In that case, we extend $A$'s end to $\max(A.\text{end}, B.\text{end})$. If $B.\text{start} > A.\text{end}$, no overlap is possible with any subsequent intervals, so $B$ is appended as a new interval. Edge cases include single-interval arrays, fully contained intervals (e.g. `[1, 4]` and `[2, 3]`), and intervals touching at exact endpoints (e.g. `[1, 2]` and `[2, 3]`).

## Why

Sorting by start time guarantees that any intervals capable of overlapping appear consecutively in the scan.

## Worked Case

Input: [[1,4],[4,5]]. Sorted: [[1,4],[4,5]]. start=4 <= last_end=4 -> overlap! merged[-1][1] = max(4, 5) = 5. Result: [[1,5]].

## Risk

Failing to sort first causes disjoint intervals to be missed if they appear out of order in the input list.

## Trade-off

Sorting adds O(n log n) overhead, but eliminates the need for graph-based connected components running in quadratic time.

## Try This

Test with [[1, 3], [2, 6], [8, 10], [15, 18]] and verify that [1, 3] and [2, 6] merge into [1, 6].

## Follow-ups

### How do you handle interval merging in a real-time streaming environment where intervals arrive dynamically?

Use an Interval Tree or Segment Tree to insert and merge overlapping intervals dynamically in O(log n) time per insertion.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you insert a new interval into a sorted list of non-overlapping intervals?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Insert Interval (LeetCode 57) inserts a new interval into an array of non-overlapping intervals sorted by start time, merging any overlaps that arise. The optimal solution uses a single three-phase linear scan: 1) add intervals preceding the new interval; 2) merge all overlapping intervals into `new_interval`; 3) append remaining intervals.

```python
def insert_interval(intervals: list[list[int]], new_interval: list[int]) -> list[list[int]]:
    res: list[list[int]] = []
    i = 0
    n = len(intervals)
    # Phase 1: Add intervals that end before new_interval starts
    while i < n and intervals[i][1] < new_interval[0]:
        res.append(intervals[i])
        i += 1
    # Phase 2: Merge overlapping intervals
    while i < n and intervals[i][0] <= new_interval[1]:
        new_interval[0] = min(new_interval[0], intervals[i][0])
        new_interval[1] = max(new_interval[1], intervals[i][1])
        i += 1
    res.append(new_interval)
    # Phase 3: Add remaining intervals
    while i < n:
        res.append(intervals[i])
        i += 1
    return res
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of intervals. Each interval is visited exactly once.
- **Space Complexity:** $O(n)$ to construct the new output list.

**Algorithmic mechanics and edge cases:**
Because the original list is already sorted and non-overlapping, intervals that end before `new_interval[0]` cannot overlap. Intervals whose start is $\le \text{new\_interval}[1]$ must overlap, so we expand `new_interval` to subsume them. Once an interval starts after `new_interval[1]`, all remaining intervals can be appended directly. Edge cases include empty list `[]`, `new_interval` completely before all intervals, or `new_interval` completely after all intervals.

## Why

A three-phase linear scan exploits the pre-sorted invariant to insert and merge in O(n) without re-sorting.

## Worked Case

intervals=[[1,3],[6,9]], new=[2,5]. Phase 1: [1,3] ends at 3 >= 2, stops. Phase 2: [1,3] starts at 1 <= 5 -> merge to [min(2,1), max(5,3)]=[1,5]. Next [6,9] starts at 6 > 5, stops. Append [1,5], then [6,9]. Result: [[1,5],[6,9]].

## Risk

Appending new_interval and re-sorting the whole array takes O(n log n) unnecessarily, degrading performance on large arrays.

## Trade-off

Three simple while loops partition the problem cleanly with no special edge-case branch logic required.

## Try This

Insert [4, 8] into [[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]] and trace how [3, 5], [6, 7], and [8, 10] merge into [3, 10].

## Follow-ups

### Can binary search be used to find the insertion position in O(log n)?

Binary search can locate the start and end overlapping indices in O(log n), but creating the final merged array still requires O(n) element copying.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the minimum number of intervals to remove to make the rest non-overlapping?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Non-overlapping Intervals (LeetCode 435) finds the minimum number of intervals you need to remove to make the rest of the intervals non-overlapping. The optimal solution uses greedy interval scheduling by sorting intervals by their end times and keeping intervals that finish earliest.

```python
def erase_overlap_intervals(intervals: list[list[int]]) -> int:
    if not intervals:
        return 0
    # Sort by end time
    intervals.sort(key=lambda x: x[1])
    removals = 0
    prev_end = intervals[0][1]
    for start, end in intervals[1:]:
        if start < prev_end:
            removals += 1  # Overlap detected: remove current interval
        else:
            prev_end = end  # Compatible interval: update end time
    return removals
```

**Complexity analysis:**
- **Time Complexity:** $O(n \log n)$ where $n$ is the number of intervals, dominated by sorting by finish time.
- **Space Complexity:** $O(1)$ auxiliary space (ignoring sort memory).

**Algorithmic mechanics and edge cases:**
Minimizing removals is mathematically equivalent to maximizing the number of compatible non-overlapping intervals (Interval Scheduling). Sorting by end time leaves the maximum possible remaining time for future intervals. If an interval starts before `prev_end`, it conflicts and must be removed. Edge cases include empty list, intervals that only touch at endpoints (`[1, 2]` and `[2, 3]` are non-overlapping), and identical intervals.

## Why

Sorting by finish time leaves the maximum remaining capacity for subsequent intervals, proving greedy choice optimality.

## Worked Case

Input: [[1,2],[1,2],[1,2]]. Sorted by end: all end at 2. First is kept (prev_end=2). Second has start 1 < 2 -> removals=1. Third has start 1 < 2 -> removals=2. Result: 2.

## Risk

Sorting by start time fails on cases where a long interval starts early and covers multiple smaller intervals.

## Trade-off

Sorting by end time guarantees optimal greedy choice in O(n log n) without dynamic programming O(n^2) tables.

## Try This

Test with [[1, 2], [2, 3], [3, 4], [1, 3]] and confirm that removing [1, 3] leaves 3 non-overlapping intervals with 1 removal.

## Follow-ups

### How does this relate to Meeting Rooms II (finding minimum conference rooms needed)?

Meeting Rooms II counts maximum concurrent overlapping intervals using min-heap of end times or two-pointer sweep-line, rather than removing them.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you rotate an array to the right by k steps in-place with O(1) extra memory?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Rotate Array (LeetCode 189) rotates an array of $n$ elements to the right by $k$ steps. The optimal in-place solution uses the three-step reversal algorithm: 1) reverse the entire array; 2) reverse the first $k$ elements; 3) reverse the remaining $n - k$ elements.

```python
def rotate(nums: list[int], k: int) -> None:
    n = len(nums)
    k = k % n
    def reverse(start: int, end: int) -> None:
        while start < end:
            nums[start], nums[end] = nums[end], nums[start]
            start += 1
            end -= 1
    reverse(0, n - 1)      # Reverse entire array
    reverse(0, k - 1)      # Reverse first k elements
    reverse(k, n - 1)      # Reverse remaining elements
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. Each element is moved exactly twice.
- **Space Complexity:** $O(1)$ auxiliary space because reversals occur directly in-place via pointer swapping.

**Algorithmic mechanics and edge cases:**
Reversing the entire array places the last $k$ elements at the front, but in reverse order. Reversing the first $k$ elements restores their relative order. Reversing the remaining $n - k$ elements restores their relative order. Edge cases include $k = 0$, $k \ge n$ (handled by `k % n`), single-element arrays, and arrays where $k$ is a multiple of $n$.

## Why

Three in-place reversals transpose the two partitioned subarrays [A, B] into [B, A] with zero extra memory allocation.

## Worked Case

nums=[-1,-100,3,99], k=2. Reverse all: [99, 3, -100, -1]. Reverse first 2: [3, 99, -100, -1]. Reverse last 2: [3, 99, -1, -100]. Matches expected rotated order.

## Risk

Failing to execute k = k % n raises IndexError when k exceeds array length.

## Trade-off

The reversal algorithm does 2n swaps; cyclic replacements do n swaps but require complex greatest common divisor cycle logic.

## Try This

Trace nums=[1, 2, 3, 4, 5, 6, 7] with k=3: reverse all -> [7, 6, 5, 4, 3, 2, 1]; reverse first 3 -> [5, 6, 7, ...]; reverse rest -> [5, 6, 7, 1, 2, 3, 4].

## Follow-ups

### How do cyclic replacements achieve the rotation with exactly n element writes?

Move each element to (i + k) % n in a cycle until returning to the start index, repeating for gcd(n, k) distinct cycles.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the next lexicographical permutation of an array of numbers in-place?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Next Permutation (LeetCode 31) rearranges numbers into the lexicographically next greater permutation of numbers in-place. If no greater arrangement is possible, it rearranges it as the lowest possible order (sorted ascending). The optimal solution uses a three-step scan: find pivot, find successor, swap and reverse suffix.

```python
def next_permutation(nums: list[int]) -> None:
    n = len(nums)
    # Step 1: Find largest index i such that nums[i] < nums[i + 1]
    i = n - 2
    while i >= 0 and nums[i] >= nums[i + 1]:
        i -= 1
    # Step 2: If pivot found, find successor j such that nums[j] > nums[i]
    if i >= 0:
        j = n - 1
        while nums[j] <= nums[i]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]
    # Step 3: Reverse the suffix starting at i + 1
    left, right = i + 1, n - 1
    while left < right:
        nums[left], nums[right] = nums[right], nums[left]
        left += 1
        right -= 1
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. In the worst case, two scans of the array and one reversal are performed.
- **Space Complexity:** $O(1)$ auxiliary space as all modifications are done in-place.

**Algorithmic mechanics and edge cases:**
Any strictly decreasing suffix cannot be made larger. Thus, we scan from the right to find the first decrease `nums[i] < nums[i+1]`. Next, we find the smallest value in the suffix that is strictly greater than `nums[i]` (at index `j`) and swap them. Finally, because the suffix from `i+1` onward remains strictly decreasing, reversing it turns it into strictly increasing order, guaranteeing the smallest lexicographical increment. Edge cases include entirely descending arrays (which simply reverse) and arrays with duplicate values.

## Why

Swapping the pivot with its smallest larger successor and reversing the suffix guarantees the minimal lexicographical increment.

## Worked Case

Input: nums=[3, 2, 1]. i decrements to -1 (entirely descending). i >= 0 check fails. Reversing suffix from 0 to 2 yields [1, 2, 3] (lowest order).

## Risk

Using strictly greater > instead of >= when scanning for pivot causes infinite loops or incorrect swaps on duplicate elements.

## Trade-off

The single-pass in-place pointer algorithm operates in O(n) time and O(1) memory without generating permutations.

## Try This

Trace nums=[1, 2, 3]: i=1 (nums[1]=2 < 3); j=2 (3); swap -> [1, 3, 2]; reverse suffix -> [1, 3, 2].

## Follow-ups

### How do you find the previous lexicographical permutation?

Mirror the logic: find the first index i from right where nums[i] > nums[i+1], swap with largest smaller element in suffix, and reverse suffix.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you count the total number of continuous subarrays whose sum equals k?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Subarray Sum Equals K (LeetCode 560) counts the number of continuous subarrays whose sum equals `k`. The optimal solution uses a prefix sum frequency hash map, running in linear $O(n)$ time and handling both positive and negative integers.

```python
def subarray_sum(nums: list[int], k: int) -> int:
    prefix_counts: dict[int, int] = {0: 1}
    curr_sum = 0
    total_subarrays = 0
    for x in nums:
        curr_sum += x
        complement = curr_sum - k
        if complement in prefix_counts:
            total_subarrays += prefix_counts[complement]
        prefix_counts[curr_sum] = prefix_counts.get(curr_sum, 0) + 1
    return total_subarrays
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. We traverse the array once and perform $O(1)$ average-time dictionary lookups.
- **Space Complexity:** $O(n)$ auxiliary memory to store prefix sum frequencies in the hash map.

**Algorithmic mechanics and edge cases:**
A continuous subarray from index $i$ to $j$ has sum equal to $\text{prefix}[j] - \text{prefix}[i-1]$. If $\text{prefix}[j] - \text{prefix}[i-1] = k$, then $\text{prefix}[i-1] = \text{prefix}[j] - k$. Initializing `prefix_counts = {0: 1}` accounts for subarrays starting at index 0. Because elements can be negative, prefix sums are non-monotonic, meaning sliding window fails and hash table lookup is required. Edge cases include all-zero arrays, arrays with negative numbers, and $k = 0$.

## Why

Prefix sum complement lookup finds matching subarray intervals in O(1) time even when negative numbers break sliding window monotonicity.

## Worked Case

nums=[1, 1, 1], k=2. x=1: curr=1, comp=-1 (not in map), map={0:1, 1:1}. x=1: curr=2, comp=0 (count 1) -> total=1, map={0:1, 1:1, 2:1}. x=1: curr=3, comp=1 (count 1) -> total=2. Result: 2.

## Risk

A sliding window assumes non-negative integers; negative numbers cause window shrinkage to be invalid and produce wrong counts.

## Trade-off

Consuming O(n) space for the hash map is required because prefix sums do not grow monotonically.

## Try This

Trace nums=[1, -1, 1, 1, 1, -1] with k=2 and verify that prefix_counts correctly matches multiple overlapping subarrays totaling 6.

## Follow-ups

### Why is sliding window invalid for this problem when negative numbers are allowed?

In sliding window, expanding right must strictly increase sum and contracting left must decrease sum; negative values break this directional monotonicity.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/collections.html

# How do you find the maximum length of a contiguous subarray with an equal number of 0 and 1?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Contiguous Array (LeetCode 525) finds the maximum length of a binary subarray with equal numbers of `0` and `1`. The optimal solution transforms all `0`s to `-1`s, turning the problem into finding the longest subarray with sum equal to zero, solved using a prefix sum first-seen index map.

```python
def find_max_length(nums: list[int]) -> int:
    first_seen: dict[int, int] = {0: -1}
    curr_sum = 0
    max_len = 0
    for i, num in enumerate(nums):
        curr_sum += 1 if num == 1 else -1
        if curr_sum in first_seen:
            max_len = max(max_len, i - first_seen[curr_sum])
        else:
            first_seen[curr_sum] = i
    return max_len
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. A single pass traverses the array with $O(1)$ dictionary lookups.
- **Space Complexity:** $O(n)$ auxiliary space to store the earliest index of each unique prefix sum.

**Algorithmic mechanics and edge cases:**
If the prefix sum at index $j$ equals the prefix sum at index $i$ (where $i < j$), then the sum of elements between $i+1$ and $j$ must be exactly $0$. Since $1$ represents `1` and $-1$ represents `0`, sum 0 implies equal counts. To maximize length $(j - i)$, we record only the *first* occurrence of each prefix sum and never overwrite it. Initializing `first_seen = {0: -1}` accounts for subarrays starting at index 0. Edge cases include all zeros `[0, 0, 0]`, alternating patterns `[0, 1, 0, 1]`, and single elements.

## Why

Mapping 0 to -1 reduces the equal-count invariant to a net zero sum, located in O(1) via prefix sum index caching.

## Worked Case

nums=[0, 1]. i=0 (0->-1): curr=-1, first_seen={0:-1, -1:0}. i=1 (1->+1): curr=0. 0 is in first_seen at -1 -> len = 1 - (-1) = 2. max_len=2.

## Risk

Updating first_seen[curr_sum] on subsequent occurrences shrinks the distance instead of maximizing the interval span.

## Trade-off

Using a hash map takes O(n) memory; alternatively, a fixed array of size 2n+1 can store indices with offset n to avoid hash collisions.

## Try This

Test with nums=[0, 1, 0] and verify that at idx 1 (sum=0), distance 1 - (-1) = 2 is recorded as max length.

## Follow-ups

### How do you generalize this to an array with 0s, 1s, and 2s having equal counts?

Track a 2D tuple (count1 - count0, count2 - count0) in the first_seen map, checking when both delta coordinates match.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you set matrix zeroes in-place with O(1) extra space?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Set Matrix Zeroes (LeetCode 73) modifies an $m \times n$ integer matrix such that if an element is `0`, its entire row and column are set to `0`. The optimal solution uses the matrix's own first row and first column as flag markers, using two boolean variables to track whether the first row and column themselves should be zeroed.

```python
def set_zeroes(matrix: list[list[int]]) -> None:
    m, n = len(matrix), len(matrix[0])
    first_row_zero = any(matrix[0][j] == 0 for j in range(n))
    first_col_zero = any(matrix[i][0] == 0 for i in range(m))
    # Use first row and column as flags
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][j] == 0:
                matrix[i][0] = 0
                matrix[0][j] = 0
    # Zero out cells based on flags
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0
    # Zero out first row and column if needed
    if first_row_zero:
        for j in range(n):
            matrix[0][j] = 0
    if first_col_zero:
        for i in range(m):
            matrix[i][0] = 0
```

**Complexity analysis:**
- **Time Complexity:** $O(m \cdot n)$ where $m$ and $n$ are matrix dimensions. Two passes inspect every cell in the grid.
- **Space Complexity:** $O(1)$ auxiliary space because state is stored inside `matrix[0][:]` and `matrix[:][0]`.

**Algorithmic mechanics and edge cases:**
Using auxiliary $O(m + n)$ row and column sets is easy but violates the $O(1)$ space constraint. By reusing `matrix[0][j]` and `matrix[i][0]`, we record zero requirements directly in the grid. Because `matrix[0][0]` overlaps both the first row and column, two separate boolean flags `first_row_zero` and `first_col_zero` preserve the original state of the first row and column. Edge cases include $1 \times 1$ matrices, matrices with no zeroes, and matrices where every element is zero.

## Why

Reusing the matrix perimeter as zero flags achieves O(1) auxiliary space without overwriting cell values prematurely.

## Worked Case

matrix=[[0,1,2,0],[3,4,5,2],[1,3,1,5]]. first_row_zero=True (has 0s). matrix[0][0]=0, matrix[0][3]=0. Inner loop updates row 1 and col 0, 3. Final first row pass sets row 0 to 0.

## Risk

Updating matrix[i][j] during the first pass triggers cascading zeroes that erroneously wipe the entire matrix.

## Trade-off

Reusing row 0 and col 0 requires two boolean variables to resolve the shared corner matrix[0][0] collision.

## Try This

Trace with [[1,1,1],[1,0,1],[1,1,1]] and observe how matrix[1][0]=0 and matrix[0][1]=0 flag row 1 and col 1.

## Follow-ups

### Can you use a single variable instead of two booleans?

Yes, let matrix[0][0] track the first row and a single boolean col0 track whether the first column has a zero.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you traverse a matrix in clockwise spiral order?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Spiral Matrix (LeetCode 54) returns all elements of an $m \times n$ matrix in clockwise spiral order. The optimal solution uses four directional boundaries (`top`, `bottom`, `left`, `right`) that contract inwards after traversing each row or column.

```python
def spiral_order(matrix: list[list[int]]) -> list[int]:
    if not matrix:
        return []
    res: list[int] = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        # Traverse Right
        for j in range(left, right + 1):
            res.append(matrix[top][j])
        top += 1
        # Traverse Down
        for i in range(top, bottom + 1):
            res.append(matrix[i][right])
        right -= 1
        # Traverse Left (if still valid row)
        if top <= bottom:
            for j in range(right, left - 1, -1):
                res.append(matrix[bottom][j])
            bottom -= 1
        # Traverse Up (if still valid col)
        if left <= right:
            for i in range(bottom, top - 1, -1):
                res.append(matrix[i][left])
            left += 1
    return res
```

**Complexity analysis:**
- **Time Complexity:** $O(m \cdot n)$ where $m$ and $n$ are matrix rows and columns. Every cell is visited exactly once.
- **Space Complexity:** $O(1)$ auxiliary space (ignoring the output list).

**Algorithmic mechanics and edge cases:**
At each outer layer, we: 1) read top row and increment `top`; 2) read right column and decrement `right`; 3) read bottom row and decrement `bottom`; 4) read left column and increment `left`. Crucially, checks `top <= bottom` and `left <= right` prevent reading duplicate elements when the matrix has an odd number of rows or columns. Edge cases include single-row matrices, single-column matrices, and $1 \times 1$ matrices.

## Why

Four shrinking boundary pointers eliminate visited matrices and navigate layer by layer in-place.

## Worked Case

matrix=[[1,2,3,4],[5,6,7,8],[9,10,11,12]]. Layer 1: right (1,2,3,4), down (8,12), left (11,10,9), up (5). Inner: right (6,7). Total: [1,2,3,4,8,12,11,10,9,5,6,7].

## Risk

Omitting the if top <= bottom check causes single-row matrices to re-read elements in reverse during the left traversal.

## Trade-off

Boundary pointer arithmetic avoids allocating an m x n visited boolean array.

## Try This

Test with matrix=[[1, 2, 3], [4, 5, 6], [7, 8, 9]] and trace traversal 1,2,3 -> 6,9 -> 8,7 -> 4 -> 5.

## Follow-ups

### How do you solve Spiral Matrix II to generate an n x n matrix filled with 1 to n^2?

Initialize an empty n x n matrix with zeros and write incrementing numbers 1 to n^2 using the same boundary contraction.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you rotate an n x n 2D image matrix by 90 degrees clockwise in-place?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Rotate Image (LeetCode 48) rotates an $n \times n$ 2D matrix representing an image by 90 degrees clockwise in-place with $O(1)$ extra space. The optimal solution combines two simple matrix reflections: 1) transpose the matrix along its main diagonal; 2) reverse each row horizontally.

```python
def rotate_image(matrix: list[list[int]]) -> None:
    n = len(matrix)
    # Step 1: Transpose matrix (swap matrix[i][j] with matrix[j][i])
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    # Step 2: Reverse each row horizontally
    for i in range(n):
        matrix[i].reverse()
```

**Complexity analysis:**
- **Time Complexity:** $O(n^2)$ where $n$ is the matrix dimension. Transposing visits $n(n - 1) / 2$ elements, and reversing rows visits $n^2 / 2$ elements.
- **Space Complexity:** $O(1)$ auxiliary space because all element swaps occur directly in-place.

**Algorithmic mechanics and edge cases:**
Mathematically, a 90-degree clockwise rotation maps cell $(i, j)$ to $(j, n - 1 - i)$. Transposing maps $(i, j)$ to $(j, i)$. Reversing each row maps $(j, i)$ to $(j, n - 1 - i)$, which matches the target transformation. Performing two standard reflections is far less error-prone than rotating 4-element cycles manually. Edge cases include $1 \times 1$ matrices (no-op), $2 \times 2$ matrices, and identity matrices.

## Why

Transposing followed by horizontal reflection achieves a 90-degree clockwise rotation without complex 4-way coordinate tracking.

## Worked Case

matrix=[[1,2,3],[4,5,6],[7,8,9]]. Transpose: [[1,4,7],[2,5,8],[3,6,9]]. Reverse rows: row 0 -> [7,4,1]; row 1 -> [8,5,2]; row 2 -> [9,6,3]. Correct.

## Risk

Iterating j across the entire row range(n) during transposition swaps elements twice, undoing the transpose operation.

## Trade-off

Two passes (transpose then reverse) do slightly more memory writes than a single 4-cycle pass but avoid nested index math bugs.

## Try This

Trace with [[1, 2], [3, 4]]: transpose -> [[1, 3], [2, 4]]; reverse rows -> [[3, 1], [4, 2]] (verified 90-degree rotation).

## Follow-ups

### How do you rotate the matrix 90 degrees counter-clockwise in-place?

Reverse each row horizontally first, then transpose along the main diagonal (or transpose along the anti-diagonal).

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you compute the next generation in Conway's Game of Life in-place?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Game of Life (LeetCode 289) calculates the next state of an $m \times n$ board according to Conway's four rules: underpopulation (<2), survival (2-3), overpopulation (>3), and reproduction (exactly 3). The optimal in-place solution uses intermediate two-bit state transitions ($0 \to 1$: state 2; $1 \to 0$: state -1) to preserve past states while computing next states.

```python
def game_of_life(board: list[list[int]]) -> None:
    m, n = len(board), len(board[0])
    directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    for r in range(m):
        for c in range(n):
            live_neighbors = 0
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and abs(board[nr][nc]) == 1:
                    live_neighbors += 1
            # Rule 1 & 3: Live cell dies -> -1
            if board[r][c] == 1 and (live_neighbors < 2 or live_neighbors > 3):
                board[r][c] = -1
            # Rule 4: Dead cell becomes alive -> 2
            elif board[r][c] == 0 and live_neighbors == 3:
                board[r][c] = 2
    # Final pass: update intermediate states to binary
    for r in range(m):
        for c in range(n):
            board[r][c] = 1 if board[r][c] > 0 else 0
```

**Complexity analysis:**
- **Time Complexity:** $O(m \cdot n)$ where $m$ and $n$ are board dimensions. Each cell inspects 8 neighbors.
- **Space Complexity:** $O(1)$ auxiliary space because transitions are encoded directly in-place.

**Algorithmic mechanics and edge cases:**
Because updates must happen simultaneously, updating a cell directly to its new state destroys the information its neighbors need. By encoding state transitions (1 was originally alive; -1 was alive and is now dead; 0 was originally dead; 2 was dead and is now alive), inspecting `abs(board[nr][nc]) == 1` accurately counts original living neighbors. Edge cases include $1 \times 1$ boards, dead boards, and boards with infinite oscillators.

## Why

Intermediate state encoding preserves original neighbor values while writing future states in-place.

## Worked Case

board=[[1,1],[1,0]]. Cell (0,0) has 2 live neighbors -> survives (stays 1). Cell (0,1) has 2 neighbors -> stays 1. Cell (1,0) has 2 neighbors -> stays 1. Cell (1,1) has 3 neighbors -> 0 becomes 2. Final pass yields all 1s.

## Risk

Creating an m x n board copy takes O(m * n) extra memory, which fails scalable in-memory simulation constraints.

## Trade-off

Two-bit state encoding uses abs() checks to decode past values with zero auxiliary heap allocations.

## Try This

Test with a blinker oscillator [[0,1,0],[0,1,0],[0,1,0]] and verify that it transitions to [[0,0,0],[1,1,1],[0,0,0]].

## Follow-ups

### How do you handle an infinite grid where only a sparse set of coordinates are alive?

Store live coordinates in a hash set; iterate over live cells and their immediate neighbors to compute transitions.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the first missing positive integer in an unsorted array in O(n) time and O(1) space?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** First Missing Positive (LeetCode 41) finds the smallest missing positive integer from an unsorted array. The optimal solution uses cyclic sort, placing each number $x$ in the range $[1, n]$ at its target index $x - 1$ in-place via element swapping.

```python
def first_missing_positive(nums: list[int]) -> int:
    n = len(nums)
    for i in range(n):
        # While nums[i] is in range [1, n] and not already at its correct index
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            target_idx = nums[i] - 1
            nums[i], nums[target_idx] = nums[target_idx], nums[i]
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1
    return n + 1
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. Each number is swapped to its correct destination at most once; total swaps across all iterations cannot exceed $n$.
- **Space Complexity:** $O(1)$ auxiliary space because array slots are reused as their own hash buckets.

**Algorithmic mechanics and edge cases:**
By the pigeonhole principle, the first missing positive must lie in the range $[1, n + 1]$. We use the array indices $0$ to $n-1$ as a hash table where index $i$ should store $i + 1$. The `while` loop swaps `nums[i]` with the element at index `nums[i] - 1` until either `nums[i]` is out of range $[1, n]$ or already matches. A final linear scan finds the first index $i$ where `nums[i] != i + 1`. Edge cases include negative numbers, numbers $> n$, duplicates (handled by `nums[nums[i] - 1] != nums[i]`), and arrays already sorted `[1, 2, 3] -> 4`.

## Why

Cyclic sort places each number 1 <= x <= n into bucket index x - 1 in-place in linear amortized time.

## Worked Case

nums=[7,8,9,11,12]. None are in range [1, 5], so no swaps occur. First loop ends. Second loop inspects idx 0: nums[0]=7 != 1. Returns 1 immediately.

## Risk

Swapping nums[i] == nums[nums[i]-1] without checking for duplicate values causes an infinite while loop.

## Trade-off

Cyclic sort mutates the input array but achieves the hard O(n) time and O(1) space constraints.

## Try This

Trace nums=[3, 4, -1, 1]: 3 swaps to idx 2 -> [-1, 4, 3, 1]; 4 swaps to idx 3 -> [-1, 1, 3, 4]; 1 swaps to idx 0 -> [1, -1, 3, 4]; missing is idx 1 (value 2).

## Follow-ups

### How do you solve this if modifying the input array is strictly prohibited?

If mutating is forbidden, you must use an O(n) space hash set or bitset, or accept an O(n log n) sorting copy.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the majority element that appears more than n // 2 times in linear time and O(1) space?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Majority Element (LeetCode 169) finds the element that appears more than $\lfloor n / 2 \rfloor$ times in an array. The optimal solution uses the Boyer-Moore Voting Algorithm, which tracks a candidate element and a vote counter in a single linear pass with $O(1)$ memory.

```python
def majority_element(nums: list[int]) -> int:
    candidate = 0
    count = 0
    for num in nums:
        if count == 0:
            candidate = num
        count += 1 if num == candidate else -1
    return candidate
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`, scanning each element once.
- **Space Complexity:** $O(1)$ auxiliary space because it only maintains two scalar variables (`candidate` and `count`).

**Algorithmic mechanics and edge cases:**
The intuition is pairing up differing elements and canceling them out. Because the majority element occurs strictly more than $n / 2$ times, even if every other element cancels out a majority instance, at least one majority element will remain uncanceled. When `count` reaches 0, we select the current number as the new candidate. Edge cases include single-element arrays `[1]`, arrays where all elements are identical, and alternating sequences.

## Why

Boyer-Moore voting pairs up distinct elements for cancellation, guaranteeing the majority element survives.

## Worked Case

nums=[3,2,3]. i=0: count=0 -> cand=3, count=1. i=1: num=2 != 3 -> count=0. i=2: count=0 -> cand=3, count=1. Loop terminates, returns candidate 3.

## Risk

Boyer-Moore assumes a majority element is guaranteed to exist; if not guaranteed, a second verification pass is required.

## Trade-off

Eliminating the hash table dictionary tally reduces auxiliary memory from O(n) to strict O(1).

## Try This

Trace nums=[2, 2, 1, 1, 1, 2, 2]: observe candidate changes between 2 and 1 as count increments and decrements, terminating at candidate=2.

## Follow-ups

### How do you find all elements that appear more than n // 3 times (Majority Element II)?

Extend Boyer-Moore to maintain two candidates and two counters, since at most two elements can appear > n // 3 times.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the contiguous subarray with the largest product in Python?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Maximum Product Subarray (LeetCode 152) finds the contiguous subarray within an array that has the largest product. The optimal solution uses dynamic programming tracking both the maximum and minimum product ending at the current position, because multiplying a negative number by a negative minimum produces a positive maximum.

```python
def max_product(nums: list[int]) -> int:
    if not nums:
        return 0
    max_so_far = nums[0]
    min_so_far = nums[0]
    global_max = nums[0]
    for i in range(1, len(nums)):
        curr = nums[i]
        # If negative, max and min swap roles when multiplied
        temp_max = max(curr, max_so_far * curr, min_so_far * curr)
        min_so_far = min(curr, max_so_far * curr, min_so_far * curr)
        max_so_far = temp_max
        global_max = max(global_max, max_so_far)
    return global_max
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`, scanning through the array once.
- **Space Complexity:** $O(1)$ auxiliary space because only running state variables are maintained.

**Algorithmic mechanics and edge cases:**
Unlike Kadane's algorithm for sum (where negative numbers only decrease the total), in multiplication, two negative numbers yield a positive result. Therefore, `min_so_far` captures a potentially large negative product that can flip to a large positive product upon encountering another negative number. Encountering a `0` resets both `max_so_far` and `min_so_far` to `0`. Edge cases include single negative numbers `[-2]`, arrays containing zeros `[0, 2]`, and alternating negative numbers `[-2, 3, -4] -> 24`.

## Why

Tracking both running maximum and minimum products accounts for parity sign inversions caused by negative multipliers.

## Worked Case

nums=[-2, 3, -4]. i=0: max=-2, min=-2, res=-2. i=1 (3): max=3, min=-6, res=3. i=2 (-4): max=max(-4, 3*-4, -6*-4)=24, min=min(-4, -12, 24)=-12, res=24. Returns 24.

## Risk

Failing to store temp_max causes min_so_far to use the newly updated max_so_far in the same iteration, producing incorrect results.

## Trade-off

State compression reduces Kadane dynamic programming to three scalar variables in O(1) space.

## Try This

Test with nums=[2, 3, -2, 4]: max_so_far becomes 6, then -2 (min=-12), then 4 (min=-48) -> global_max remains 6.

## Follow-ups

### Can this be solved using two directional passes (left-to-right and right-to-left)?

Yes, computing running prefix products and suffix products (resetting to 1 on zero) finds the max product without min tracking.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you merge two sorted arrays in-place from the back without shifting elements?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Merge Sorted Array (LeetCode 88) merges two sorted integer arrays `nums1` and `nums2` into `nums1` as one sorted array. `nums1` has size $m + n$ with trailing zeros. The optimal solution uses three pointers working backwards from the end of `nums1`, placing the largest remaining element at the back to avoid shifting elements.

```python
def merge(nums1: list[int], m: int, nums2: list[int], n: int) -> None:
    p1 = m - 1
    p2 = n - 1
    p = m + n - 1
    while p1 >= 0 and p2 >= 0:
        if nums1[p1] > nums2[p2]:
            nums1[p] = nums1[p1]
            p1 -= 1
        else:
            nums1[p] = nums2[p2]
            p2 -= 1
        p -= 1
    # If nums2 still has elements, copy them
    while p2 >= 0:
        nums1[p] = nums2[p2]
        p2 -= 1
        p -= 1
```

**Complexity analysis:**
- **Time Complexity:** $O(m + n)$ because each element from `nums1` and `nums2` is placed in its final position exactly once.
- **Space Complexity:** $O(1)$ auxiliary space because elements are written directly into the pre-allocated buffer at the end of `nums1`.

**Algorithmic mechanics and edge cases:**
Merging from the front requires shifting elements in `nums1` to the right, which incurs an $O(m \cdot n)$ worst-case penalty. Merging from the back writes into unused trailing space (initially filled with zeros), guaranteeing that unread elements in `nums1` are never overwritten. If `p1` finishes first, remaining elements in `nums2` are copied over. If `p2` finishes first, `nums1`'s remaining elements are already in their sorted positions. Edge cases include $m = 0$, $n = 0$, and identical arrays.

## Why

Filling backwards into the pre-allocated tail buffer avoids shifting elements in O(1) space.

## Worked Case

nums1=[0], m=0, nums2=[1], n=1. p1=-1, p2=0, p=0. First loop skipped. Second loop copies nums2[0]=1 to nums1[0]. Result: nums1=[1].

## Risk

Merging from the front overwrites valid elements in nums1 unless a copy array is allocated.

## Trade-off

Backwards merging requires no auxiliary allocation and completes in a single linear pass.

## Try This

Merge nums1=[1, 2, 3, 0, 0, 0] (m=3) and nums2=[2, 5, 6] (n=3) from the back and verify the result [1, 2, 2, 3, 5, 6].

## Follow-ups

### Why is there no need for a while p1 >= 0 cleanup loop?

If p2 finishes first, all remaining elements in nums1 are already in their correct sorted positions at the front of the array.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you group consecutive numbers into summary ranges in Python?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Summary Ranges (LeetCode 228) takes a sorted unique integer array `nums` and returns the smallest sorted list of ranges covering all numbers in the array. The optimal solution uses two pointers (`start` and `i`) scanning linearly to detect discontinuities where `nums[i] + 1 != nums[i + 1]`.

```python
def summary_ranges(nums: list[int]) -> list[str]:
    ranges: list[str] = []
    if not nums:
        return ranges
    start = 0
    for i in range(len(nums)):
        # Check if at the end of the array or next number is non-consecutive
        if i == len(nums) - 1 or nums[i] + 1 != nums[i + 1]:
            if start == i:
                ranges.append(str(nums[start]))
            else:
                ranges.append(f"{nums[start]}->{nums[i]}")
            start = i + 1
    return ranges
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. A single pass iterates through the numbers.
- **Space Complexity:** $O(1)$ auxiliary space (ignoring the output list of formatted range strings).

**Algorithmic mechanics and edge cases:**
Because `nums` is sorted and elements are unique, a contiguous range extends as long as `nums[i + 1] == nums[i] + 1`. When this condition fails (or we reach the end of the array), the range closes. If `start == i`, a single isolated number is formatted as `"a"`; otherwise, an interval is formatted as `"a->b"`. Edge cases include empty list `[]`, single element `[0] -> ["0"]`, completely contiguous array `[1, 2, 3] -> ["1->3"]`, and array with no adjacent numbers `[1, 3, 5] -> ["1", "3", "5"]`.

## Why

A linear scan comparing adjacent elements identifies sequence breaks in O(n) without auxiliary state.

## Worked Case

nums=[0, 2, 3, 4, 6, 8, 9]. i=0 (0): next is 2 (!=1) -> '0'. i=1 to 3 (2,3,4): break at 4 -> '2->4'. i=4 (6): break at 6 -> '6'. i=5 to 6 (8,9): end -> '8->9'.

## Risk

Checking nums[i+1] without an i == len(nums) - 1 boundary check causes IndexError on the last element.

## Trade-off

Formatted f-strings provide concise string representation with negligible memory overhead.

## Try This

Test with nums=[0, 1, 2, 4, 5, 7] and verify output ['0->2', '4->5', '7'].

## Follow-ups

### How do you handle integer overflow if numbers can be close to 32-bit integer limits in C++?

In statically typed languages, write nums[i + 1] - nums[i] != 1 or cast to 64-bit int to avoid signed overflow on INT_MAX.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you reverse a singly linked list iteratively in-place?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Reverse Linked List (LeetCode 206) inverts the pointers of a singly linked list so the tail becomes the new head. The optimal solution uses three pointers (`prev`, `curr`, `next_node`) traversing the list in a single pass, updating each node's `next` reference in-place.

```python
from typing import Optional

class ListNode:
    def __init__(self, val: int = 0, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next

def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
    prev: Optional[ListNode] = None
    curr = head
    while curr:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    return prev
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of nodes in the list. Each node's `next` pointer is updated exactly once.
- **Space Complexity:** $O(1)$ auxiliary space because pointers are updated in-place without recursion stack allocations.

**Algorithmic mechanics and edge cases:**
At each step, saving `curr.next` into `next_node` prevents losing the remainder of the list before severing the link. Pointing `curr.next = prev` reverses the direction of the edge. Advancing `prev = curr` and `curr = next_node` steps forward until `curr` becomes `None`, at which point `prev` references the new head. Edge cases include empty list `head = None`, single-node list `[1]`, and two-node lists.

## Why

Three-pointer traversal updates links in-place with O(1) memory, avoiding O(n) call stack overhead from recursion.

## Worked Case

head: 1 -> 2 -> None. Loop 1: next_node=2, 1.next=None, prev=1, curr=2. Loop 2: next_node=None, 2.next=1, prev=2, curr=None. Returns prev (node 2).

## Risk

Updating curr.next before saving curr.next in a temporary variable severs the chain and loses the rest of the list.

## Trade-off

Iterative pointer updates use O(1) space; recursive reversal is mathematically elegant but risks recursion depth limits.

## Try This

Trace 1 -> 2 -> 3 -> None and confirm that pointer reversal outputs 3 -> 2 -> 1 -> None with new head pointing to 3.

## Follow-ups

### How do you reverse a sublist between position left and right (Reverse Linked List II)?

Navigate to position left - 1, retain references to the sublist head and predecessor, and reverse the sublist segment in-place.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you merge two sorted linked lists using a sentinel dummy head?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Merge Two Sorted Lists (LeetCode 21) merges two sorted linked lists into a single sorted list. The optimal solution uses a sentinel dummy head node and a tail pointer, iteratively appending the smaller of the two head nodes in-place.

```python
from typing import Optional

def merge_two_lists(list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode(0)
    tail = dummy
    while list1 and list2:
        if list1.val <= list2.val:
            tail.next = list1
            list1 = list1.next
        else:
            tail.next = list2
            list2 = list2.next
        tail = tail.next
    tail.next = list1 if list1 else list2
    return dummy.next
```

**Complexity analysis:**
- **Time Complexity:** $O(n + m)$ where $n$ and $m$ are the lengths of the two lists. Each comparison splices one node.
- **Space Complexity:** $O(1)$ auxiliary space because existing node references are rearranged without allocating new nodes.

**Algorithmic mechanics and edge cases:**
A sentinel dummy node eliminates boundary conditions when initializing the merged head. When one list runs out of nodes, `tail.next = list1 if list1 else list2` splices the remaining sorted tail in $O(1)$ time without further looping. Edge cases include both lists being empty (`None, None`), one list empty (`None, [1]`), and lists with duplicate values.

## Why

A sentinel dummy head provides a fixed reference anchor that eliminates special-case logic for the first node.

## Worked Case

list1=[1,2,4], list2=[1,3,4]. dummy->tail. tail.next=list1 (1). tail.next=list2 (1). tail.next=list1 (2). tail.next=list2 (3). tail.next=list1 (4). tail.next=list2 (4). Returns dummy.next.

## Risk

Creating new ListNode objects inside the loop wastes memory; in-place node relinking takes O(1) auxiliary space.

## Trade-off

Iterative splicing uses O(1) space, whereas recursive merging uses O(n + m) call stack frames.

## Try This

Merge list1: 1 -> 2 -> 4 and list2: 1 -> 3 -> 4, confirming output 1 -> 1 -> 2 -> 3 -> 4 -> 4.

## Follow-ups

### How do you merge k sorted linked lists in O(N log k) time?

Use a min-heap of size k to extract the smallest node across all k lists, or use divide-and-conquer pair merges.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you reorder a linked list to alternate first and last nodes in-place?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Reorder List (LeetCode 143) rearranges $L_0 \to L_1 \to \dots \to L_{n-1} \to L_n$ into $L_0 \to L_n \to L_1 \to L_{n-1} \to L_2 \dots$ in-place. The optimal solution uses a three-step algorithm: 1) find the middle using fast and slow pointers; 2) reverse the second half; 3) merge the two halves alternately.

```python
from typing import Optional

def reorder_list(head: Optional[ListNode]) -> None:
    if not head or not head.next:
        return
    # Step 1: Find middle using slow and fast pointers
    slow, fast = head, head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    # Step 2: Reverse second half starting at slow.next
    prev = None
    curr = slow.next
    slow.next = None  # Cut list into two halves
    while curr:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    # Step 3: Alternating merge of first half (head) and second half (prev)
    first, second = head, prev
    while second:
        tmp1, tmp2 = first.next, second.next
        first.next = second
        second.next = tmp1
        first = tmp1
        second = tmp2
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of nodes. Finding middle, reversing half, and merging each take linear time.
- **Space Complexity:** $O(1)$ auxiliary space because all pointer adjustments occur in-place.

**Algorithmic mechanics and edge cases:**
Severing `slow.next = None` partitions the list into two disjoint chains. Reversing the second half prepares nodes to be spliced in reverse order. Interleaving updates pointers using temporary next references. Edge cases include lists with odd vs even node counts, two-node lists (`1 -> 2`), and single nodes.

## Why

Combining middle-splitting, sublist reversal, and alternating merge reorders the list in-place in O(1) space.

## Worked Case

head: 1 -> 2 -> 3 -> 4 -> 5. slow reaches 3. Second half starts at 4, reversed to 5 -> 4. First half: 1 -> 2 -> 3. Interleaving: 1 -> 5 -> 2 -> 4 -> 3 -> None.

## Risk

Failing to sever slow.next creates a cycle between the first and second halves during the alternating merge.

## Trade-off

In-place pointer manipulation avoids copying nodes to an array, preserving O(1) memory guarantees.

## Try This

Trace 1 -> 2 -> 3 -> 4: middle splits 1->2 and 3->4; reverse 2nd -> 4->3; merge -> 1 -> 4 -> 2 -> 3 -> None.

## Follow-ups

### How do you test if a linked list is a palindrome using these exact building blocks?

Find the middle, reverse the second half, compare values of the first and second halves, and optionally restore the second half.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you remove the nth node from the end of a linked list in a single pass?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Remove Nth Node From End of List (LeetCode 19) deletes the $n$-th node from the end in a single pass. The optimal solution uses two pointers (`fast` and `slow`) separated by $n + 1$ steps, anchored with a sentinel dummy node.

```python
from typing import Optional

def remove_nth_from_end(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    dummy = ListNode(0, head)
    fast = dummy
    slow = dummy
    # Advance fast pointer by n + 1 steps
    for _ in range(n + 1):
        fast = fast.next
    # Advance both pointers until fast reaches the end
    while fast:
        fast = fast.next
        slow = slow.next
    # Delete target node
    slow.next = slow.next.next
    return dummy.next
```

**Complexity analysis:**
- **Time Complexity:** $O(L)$ where $L$ is the length of the linked list. A single pass visits each node at most once.
- **Space Complexity:** $O(1)$ auxiliary space as it only maintains two pointer references and a dummy node.

**Algorithmic mechanics and edge cases:**
By advancing `fast` by $n + 1$ steps ahead of `slow`, when `fast` drops off the end (`fast = None`), `slow` lands on the node immediately preceding the target node to be deleted. Splicing `slow.next = slow.next.next` deletes the target node cleanly. The dummy node handles the case where the very first node (the head) must be deleted. Edge cases include deleting the head ($n = L$), deleting the tail ($n = 1$), and single-node lists.

## Why

A fixed gap of n+1 steps between two pointers positions the slow pointer directly before the deletion target.

## Worked Case

head=[1], n=1. dummy(0)->1. fast advances 2 steps to None. while fast loop skipped. slow is at dummy. slow.next = slow.next.next = None. Returns dummy.next which is None.

## Risk

Attempting to delete without a dummy head node requires special if n == length branching to re-anchor the head.

## Trade-off

Two pointers with a gap require a single pass rather than two passes (one to count length, one to delete).

## Try This

Trace list 1 -> 2 -> 3 -> 4 -> 5 with n=2: fast advances 3 steps to node 3; both advance until fast is None; slow is at node 3; deletes node 4.

## Follow-ups

### What if n is greater than the total number of nodes in the list?

Add a defensive check during the initial loop if not fast: to catch invalid n values and raise ValueError.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the starting node of a cycle in a linked list using Floyd's algorithm?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Linked List Cycle II (LeetCode 142) detects if a cycle exists and returns the node where the cycle begins. The optimal solution uses Floyd's Tortoise and Hare algorithm: find intersection point using slow and fast pointers, then reset one pointer to head and advance both at speed 1 until they meet.

```python
from typing import Optional

def detect_cycle(head: Optional[ListNode]) -> Optional[ListNode]:
    slow, fast = head, head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            # Cycle detected: find entry node
            p1 = head
            p2 = slow
            while p1 != p2:
                p1 = p1.next
                p2 = p2.next
            return p1
    return None
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of nodes. The meeting point is reached within $n$ steps, and finding entry takes $< n$ steps.
- **Space Complexity:** $O(1)$ auxiliary space because pointers navigate node references directly without storing visited addresses.

**Algorithmic mechanics and edge cases:**
Let $L_1$ be distance from head to cycle entrance, and $L_2$ be distance from entrance to meeting point. Fast pointer travels $2 \times \text{slow}$. Mathematical derivation yields $L_1 = k \cdot C - L_2$, meaning advancing one pointer from `head` and one from the meeting point at identical 1x speeds guarantees they meet at the cycle entry node. Edge cases include no cycle (returns `None`), circular lists starting at head ($L_1 = 0$), and single-node loops.

## Why

The distance from the head to cycle entry is mathematically equal to the distance from meeting point to cycle entry modulo cycle length.

## Worked Case

head: 1 -> 2 -> loop to 1. slow reaches 2, fast reaches 1 (loop), slow reaches 1, fast reaches 1 -> meet at 1. p1=1, p2=1 -> p1==p2 immediately, returns node 1.

## Risk

Using a hash set to record seen node IDs consumes O(n) memory, which violates the strict O(1) space constraint.

## Trade-off

Floyd's algorithm uses two pointer phases to achieve O(1) space without modifying node structures or values.

## Try This

Trace 3 -> 2 -> 0 -> -4 with loop from -4 to 2: slow/fast meet at -4; reset p1=3, p2=-4; both advance 1 step to node 2, detecting entry at 2.

## Follow-ups

### How do you calculate the exact length of the cycle once detected?

Hold slow pointer fixed at the meeting point and advance fast pointer by 1 step at a time, counting steps until fast meets slow again.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you merge k sorted linked lists in optimal O(N log k) time?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Merge k Sorted Lists (LeetCode 23) merges $k$ sorted linked lists into one sorted list. The optimal solution uses a min-heap (priority queue) of size $k$ to continuously extract the minimum node across all lists and insert its successor.

```python
import heapq
from typing import Optional

def merge_k_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    dummy = ListNode(0)
    tail = dummy
    heap: list[tuple[int, int, ListNode]] = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))
    while heap:
        val, i, node = heapq.heappop(heap)
        tail.next = node
        tail = tail.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next
```

**Complexity analysis:**
- **Time Complexity:** $O(N \log k)$ where $N$ is total nodes across all lists and $k$ is number of linked lists. Each node insertion and extraction takes $O(\log k)$.
- **Space Complexity:** $O(k)$ auxiliary space to maintain the min-heap containing at most one node per linked list.

**Algorithmic mechanics and edge cases:**
Including the index `i` in the heap tuple `(node.val, i, node)` prevents Python `TypeError` when two nodes have identical values, since Python falls back to comparing `i` before inspecting `node`. Merging lists one by one serially takes $O(k N)$, which is too slow. Edge cases include empty list `lists = []`, lists with empty heads `[None, None]`, and lists of drastically differing lengths.

## Why

A min-heap prioritizes the smallest node across k active list heads in O(log k) time per step.

## Worked Case

Input: [[]]. Heap remains empty. Loop does not execute. Returns dummy.next = None. Correct for empty inner list.

## Risk

Pushing (node.val, node) into heapq raises TypeError on duplicate values because ListNode does not define __lt__.

## Trade-off

Heap merge takes O(k) memory; divide-and-conquer pair merging takes O(1) extra space and identical O(N log k) time.

## Try This

Merge [[1,4,5],[1,3,4],[2,6]]: heap starts with [1, 1, 2]; nodes are popped in order: 1, 1, 2, 3, 4, 4, 5, 6.

## Follow-ups

### How does divide-and-conquer pair merging achieve this without heap overhead?

Pair up lists and merge each pair using merge_two_lists in O(N); repeat for log k rounds until 1 list remains.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/heapq.html

# How do you reverse nodes in k-group in a linked list in-place?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Reverse Nodes in k-Group (LeetCode 25) reverses nodes of a linked list $k$ at a time. If the number of nodes is not a multiple of $k$, left-out nodes remain in their original order. The optimal solution counts $k$ nodes ahead; if available, it reverses the $k$-node subsegment and links it to the previous group.

```python
from typing import Optional

def reverse_k_group(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    dummy = ListNode(0, head)
    group_prev = dummy
    while True:
        # Check if there are k nodes remaining
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if not kth:
                return dummy.next
        group_next = kth.next
        # Reverse k nodes: between group_prev and group_next
        prev = group_next
        curr = group_prev.next
        while curr != group_next:
            tmp = curr.next
            curr.next = prev
            prev = curr
            curr = tmp
        tmp = group_prev.next
        group_prev.next = kth
        group_prev = tmp
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is total nodes in the list. Each node is visited twice (once to verify count, once to reverse).
- **Space Complexity:** $O(1)$ auxiliary space because all pointer rearrangements occur in-place.

**Algorithmic mechanics and edge cases:**
`kth` advances $k$ steps to verify that a complete group exists. If `kth` hits `None`, the loop terminates and the remaining nodes are left unmodified. The segment between `group_prev.next` and `kth` is reversed, with `prev` initialized to `group_next` so the reversed segment's tail connects seamlessly to the next group. Edge cases include $k = 1$ (no change), $k = n$ (reverses entire list), and list lengths smaller than $k$.

## Why

Verifying k nodes ahead before in-place reversal leaves trailing incomplete segments unchanged without recursion.

## Worked Case

head=[1,2,3,4,5], k=3. First group has 3 nodes (1,2,3). Reversed to 3->2->1. Remaining is [4,5], which has length 2 < 3. Stops. Result: [3,2,1,4,5].

## Risk

Reversing before checking for k nodes requires backtracking or reversing back if the segment is shorter than k.

## Trade-off

In-place pointer reversal avoids O(n) memory allocation or array copying.

## Try This

Trace 1 -> 2 -> 3 -> 4 -> 5 with k=2: group 1 reverses to 2->1; group 2 reverses to 4->3; 5 remains -> 2 -> 1 -> 4 -> 3 -> 5.

## Follow-ups

### How do you solve this recursively?

Check for k nodes; reverse the first k nodes; head.next = reverse_k_group(next_head, k); return new_head.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you deep-copy a linked list with random pointers in O(1) extra space?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Copy List with Random Pointer (LeetCode 138) clones a linked list where each node has a `next` pointer and a `random` pointer. The optimal solution avoids a hash map by interleaving cloned nodes directly alongside original nodes: $A \to A' \to B \to B' \to C \to C'$, copying random pointers, then decoupling the two lists.

```python
class Node:
    def __init__(self, val: int, next: 'Node' = None, random: 'Node' = None):
        self.val = val
        self.next = next
        self.random = random

def copy_random_list(head: 'Node') -> 'Node':
    if not head:
        return None
    # Phase 1: Create cloned nodes interleaved directly after original nodes
    curr = head
    while curr:
        clone = Node(curr.val, curr.next)
        curr.next = clone
        curr = clone.next
    # Phase 2: Assign random pointers for cloned nodes
    curr = head
    while curr:
        if curr.random:
            curr.next.random = curr.random.next
        curr = curr.next.next
    # Phase 3: Decouple original and cloned lists
    dummy = Node(0)
    copy_curr = dummy
    curr = head
    while curr:
        clone = curr.next
        curr.next = clone.next
        copy_curr.next = clone
        copy_curr = clone
        curr = curr.next
    return dummy.next
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is number of nodes. Three passes iterate through the list.
- **Space Complexity:** $O(1)$ auxiliary space (ignoring cloned nodes) because no hash map is used.

**Algorithmic mechanics and edge cases:**
Interleaving node $A'$ after $A$ means $A.\text{random}.\text{next}$ is exactly the clone of $A.\text{random}$. This eliminates the need for an $O(n)$ hash table mapping `original -> clone`. Phase 3 restores the original list's `next` pointers while stitching the clones together. Edge cases include `head = None`, nodes with `random = None`, and self-referencing nodes (`node.random = node`).

## Why

Interleaving cloned nodes inside the original list embeds clone mapping directly into the node structure in O(1) extra space.

## Worked Case

Input: [[7,null],[13,0]]. Clone creates 7->7'->13->13'. Assign random: 13'.random = 13.random.next = 7.next = 7'. Decouple yields separate cloned list.

## Risk

Failing to restore original node next pointers in Phase 3 mutates caller data and breaks external invariants.

## Trade-off

Interleaving requires three passes and temporary mutation of the list; hash map approach is two passes with O(n) memory.

## Try This

Trace node A with A.random=A: clone A' placed after A; A.next.random = A.random.next = A.next (A'); decouples A and A'.

## Follow-ups

### How do you clone an arbitrary directed graph with cycles?

Use DFS/BFS with a visited hash map mapping original node pointers to newly instantiated cloned node instances.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you add two numbers represented by linked lists in reverse order?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Add Two Numbers (LeetCode 2) adds two non-empty linked lists representing two non-negative integers stored in reverse order. The optimal solution uses a sentinel dummy head, traversing both lists simultaneously while propagating a running `carry` digit.

```python
from typing import Optional

def add_two_numbers(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode(0)
    curr = dummy
    carry = 0
    while l1 or l2 or carry:
        val1 = l1.val if l1 else 0
        val2 = l2.val if l2 else 0
        total = val1 + val2 + carry
        carry = total // 10
        curr.next = ListNode(total % 10)
        curr = curr.next
        l1 = l1.next if l1 else None
        l2 = l2.next if l2 else None
    return dummy.next
```

**Complexity analysis:**
- **Time Complexity:** $O(\max(m, n))$ where $m$ and $n$ are lengths of `l1` and `l2`.
- **Space Complexity:** $O(\max(m, n))$ for the new linked list output.

**Algorithmic mechanics and edge cases:**
Because digits are stored in reverse order (least significant digit first), traversal mirrors column addition directly from units to tens to hundreds. The condition `while l1 or l2 or carry` guarantees that a final carry digit (e.g. $5 + 5 = 10$) creates a trailing node without special post-loop logic. Edge cases include lists of differing lengths (e.g., adding `999` and `1`), single-digit zeros, and carries propagating across multiple digits.

## Why

Reverse-order storage allows streaming column addition directly with single-digit carry propagation.

## Worked Case

l1=[9,9,9,9], l2=[9,9]. Digits: 9+9=18 (8, c=1); 9+9+1=19 (9, c=1); 9+0+1=10 (0, c=1); 9+0+1=10 (0, c=1); carry 1 -> [8,9,0,0,1].

## Risk

Converting linked lists to Python integers using loops risks exceeding integer string conversion limits on lists with 100,000 nodes.

## Trade-off

Streaming node-by-node construction requires O(max(m, n)) allocations for the result list.

## Try This

Add l1=[2, 4, 3] (342) and l2=[5, 6, 4] (465): 2+5=7; 4+6=10 (0, carry 1); 3+4+1=8 -> [7, 0, 8] (807).

## Follow-ups

### How do you solve Add Two Numbers II where digits are stored in forward most-significant order?

Push digits of both lists onto two stacks, then pop from stacks to perform addition from least significant digit forward.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you calculate the number of days until a warmer temperature using a monotonic stack?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Daily Temperatures (LeetCode 739) computes an array `answer` where `answer[i]` is the number of days you have to wait after the $i$-th day to get a warmer temperature. The optimal solution uses a monotonic decreasing stack storing indices of temperatures that have not yet found a warmer day.

```python
def daily_temperatures(temperatures: list[int]) -> list[int]:
    n = len(temperatures)
    res = [0] * n
    stack: list[int] = []  # Monotonic decreasing stack of indices
    for i, temp in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < temp:
            prev_index = stack.pop()
            res[prev_index] = i - prev_index
        stack.append(i)
    return res
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `temperatures`. Each index is pushed and popped at most once.
- **Space Complexity:** $O(n)$ auxiliary space in the worst case where temperatures are monotonically decreasing.

**Algorithmic mechanics and edge cases:**
The stack maintains indices of unresolved days in strictly decreasing temperature order. When the current temperature `temp` exceeds the temperature at `stack[-1]`, `temp` is the *next warmer temperature* for that day. We pop the index and record the distance `i - prev_index`. Edge cases include monotonically decreasing arrays (all answers remain `0`), monotonically increasing arrays (every answer is `1`), and all identical temperatures.

## Why

A monotonic decreasing stack resolves the nearest greater element for each item in amortized O(1) operations.

## Worked Case

T=[30, 40, 50, 60]. i=0 (30): stack=[0]. i=1 (40 > 30): pop 0, res[0]=1-0=1, stack=[1]. i=2 (50 > 40): pop 1, res[1]=2-1=1, stack=[2]. i=3 (60 > 50): pop 2, res[2]=3-2=1, stack=[3]. Result: [1, 1, 1, 0].

## Risk

Brute-force nested loops inspect O(n^2) pairs, timing out on arrays with 100,000 elements.

## Trade-off

Storing indices rather than temperature values allows calculating distance intervals directly upon pop.

## Try This

Trace temperatures=[73, 74, 75, 71, 69, 72, 76, 73] and observe stack pops resolving earlier days.

## Follow-ups

### How do you solve Next Greater Element II where the array is circular?

Iterate through the array twice (from 0 to 2n - 1) using index modulo i % n with the same monotonic stack.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you implement a stack that supports push, pop, top, and retrieving the minimum element in O(1) time?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Min Stack (LeetCode 155) designs a stack supporting `push`, `pop`, `top`, and `getMin` operations in $O(1)$ time. The optimal solution maintains a secondary minimum stack (or stores tuples `(val, current_min)` on a single stack) tracking the running minimum associated with each stack level.

```python
class MinStack:
    def __init__(self):
        self.stack: list[int] = []
        self.min_stack: list[int] = []

    def push(self, val: int) -> None:
        self.stack.append(val)
        # Push onto min_stack if it's the new minimum
        if not self.min_stack or val <= self.min_stack[-1]:
            self.min_stack.append(val)

    def pop(self) -> None:
        val = self.stack.pop()
        if val == self.min_stack[-1]:
            self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.min_stack[-1]
```

**Complexity analysis:**
- **Time Complexity:** $O(1)$ for all four operations (`push`, `pop`, `top`, `getMin`).
- **Space Complexity:** $O(n)$ where $n$ is the number of elements pushed onto the stack.

**Algorithmic mechanics and edge cases:**
Because stack operations are LIFO (Last-In, First-Out), the minimum element of the stack cannot change unless an element is pushed or popped. By pushing onto `min_stack` only when `val <= min_stack[-1]` (note `<=`, not `<`), we preserve duplicate minimums. When popping, if the removed value equals `min_stack[-1]`, it is popped from `min_stack` as well. Edge cases include pushing duplicate minimums, popping the current minimum, and negative numbers.

## Why

LIFO stack semantics guarantee that the minimum element among all current elements is monotonic with stack depth.

## Worked Case

push(2), min_stack=[2]. push(0), min_stack=[2, 0]. push(3), min_stack=[2, 0]. push(0), min_stack=[2, 0, 0]. pop() -> pops 0, min_stack=[2, 0]. getMin()=0.

## Risk

Using strictly less < instead of <= when pushing to min_stack causes premature eviction of duplicate minimums.

## Trade-off

A secondary min_stack pushes only when min updates, saving memory compared to storing (val, min) on every entry.

## Try This

Push -2, 0, -3. getMin() -> -3. pop(). top() -> 0. getMin() -> -2. Confirm both stacks remain in sync.

## Follow-ups

### How can you achieve this in O(1) space per element without a secondary stack?

Store the difference val - current_min on the stack; when the difference is negative, current_min updates and can be restored on pop.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you evaluate an arithmetic expression in Reverse Polish Notation (postfix)?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Evaluate Reverse Polish Notation (LeetCode 150) evaluates an arithmetic expression in postfix notation containing `+`, `-`, `*`, `/`. The optimal solution uses an operand stack: push numbers, and when an operator is encountered, pop the top two operands, evaluate, and push the result back.

```python
def eval_rpn(tokens: list[str]) -> int:
    stack: list[int] = []
    for token in tokens:
        if token in {"+", "-", "*", "/"}:
            b = stack.pop()
            a = stack.pop()
            if token == "+":
                stack.append(a + b)
            elif token == "-":
                stack.append(a - b)
            elif token == "*":
                stack.append(a * b)
            elif token == "/":
                stack.append(int(a / b))  # Truncate towards zero
        else:
            stack.append(int(token))
    return stack[0]
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of tokens. Each token is pushed and popped at most once.
- **Space Complexity:** $O(n)$ auxiliary space to store operands on the stack.

**Algorithmic mechanics and edge cases:**
In Reverse Polish Notation, operators appear immediately after their operands, completely eliminating the need for parentheses or operator precedence rules. Note that the first popped value is operand `b` (the right operand) and the second popped value is `a` (the left operand), which is critical for non-commutative operations like `-` and `/`. In Python, `int(a / b)` correctly truncates toward zero (e.g. `int(-6 / 132) == 0`), whereas `a // b` rounds down towards negative infinity (`-6 // 132 == -1`). Edge cases include single-token expressions `["18"]` and negative numbers.

## Why

Postfix notation orders operations explicitly so an operand stack evaluates operators immediately upon arrival.

## Worked Case

Evaluation walkthrough: For tokens=['2', '1', '+', '3', 'x']: stack pushes 2 then 1; on '+' pops 1 and 2, evaluates 2+1=3, pushes 3; pushes 3; on multiplication operator pops 3 and 3, evaluates 3 multiplied by 3 = 9, pushes 9. Result returned is 9.

## Risk

Popping in wrong order (a then b instead of b then a) inverts division a / b to b / a and subtraction a - b to b - a.

## Trade-off

Using int(a / b) rather than a // b guarantees compliance with LeetCode truncation toward zero requirements.

## Try This

Evaluate tokens=['4', '13', '5', '/', '+']: 13/5=2; 4+2=6; verify stack terminates with [6].

## Follow-ups

### How do you convert standard infix expressions (e.g., 3 + 4 * 2) into Reverse Polish Notation?

Use Dijkstra's Shunting-Yard algorithm using an operator stack and precedence comparisons to reorder tokens into postfix.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the largest rectangular area in a histogram in linear time?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Largest Rectangle in Histogram (LeetCode 84) finds the area of the largest rectangle that can be formed within a histogram. The optimal solution uses a monotonic increasing stack storing `(index, height)` pairs, calculating rectangular areas when encountering a height drop.

```python
def largest_rectangle_area(heights: list[int]) -> int:
    stack: list[tuple[int, int]] = []  # (index, height)
    max_area = 0
    for i, h in enumerate(heights):
        start = i
        while stack and stack[-1][1] > h:
            idx, height = stack.pop()
            max_area = max(max_area, height * (i - idx))
            start = idx  # Extend start index backward
        stack.append((start, h))
    for idx, height in stack:
        max_area = max(max_area, height * (len(heights) - idx))
    return max_area
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of bars in `heights`. Each bar is pushed and popped at most once.
- **Space Complexity:** $O(n)$ auxiliary space for the monotonic stack.

**Algorithmic mechanics and edge cases:**
When current height `h` is smaller than `stack[-1][1]`, the popped bar cannot extend any further to the right. Its width is bounded on the right by `i` and on the left by its stored `start` index. Because the popped bar was taller than `h`, the current bar `h` can extend its own left boundary backward to `idx`. A cleanup pass evaluates all bars remaining in the stack extending to the end of the histogram. Edge cases include empty list, monotonically increasing bars, and single-bar histograms.

## Why

A monotonic increasing stack computes the maximal span for each bar as soon as a rightward boundary drop occurs.

## Worked Case

heights=[2, 4]. i=0: stack=[(0,2)]. i=1: 4 > 2 -> stack=[(0,2), (1,4)]. Cleanup: bar 4 extends len 2-1=1 -> area 4; bar 2 extends len 2-0=2 -> area 4. Max=4.

## Risk

Brute-force testing all pairs of bars takes O(n^2) time, which times out on histograms with 100,000 bars.

## Trade-off

Tracking start indices directly during pop eliminates the need for two separate left/right boundary arrays.

## Try This

Trace heights=[2, 1, 5, 6, 2, 3] and observe that bars 5 and 6 form a 2x5 rectangle of area 10.

## Follow-ups

### How do you use this to solve Maximal Rectangle (LeetCode 85) in a 2D binary matrix?

Treat each row of the matrix as the base of a histogram, accumulating consecutive 1s down columns, and run largest_rectangle_area on each row.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you simulate asteroid collisions using a stack?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Asteroid Collision (LeetCode 735) simulates asteroids moving along a line where positive values move right and negative values move left, colliding when they meet. The optimal solution uses a stack to simulate collisions: an asteroid only collides if it moves left (`< 0`) and the top of the stack moves right (`> 0`).

```python
def asteroid_collision(asteroids: list[int]) -> list[int]:
    stack: list[int] = []
    for ast in asteroids:
        while stack and ast < 0 and stack[-1] > 0:
            diff = ast + stack[-1]
            if diff < 0:
                stack.pop()  # Right-moving asteroid explodes, left continues
            elif diff > 0:
                ast = 0      # Left-moving asteroid explodes
                break
            else:
                stack.pop()  # Both asteroids explode
                ast = 0
                break
        if ast != 0:
            stack.append(ast)
    return stack
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of asteroids. Each asteroid is pushed and popped at most once.
- **Space Complexity:** $O(n)$ auxiliary space to store remaining asteroids on the stack.

**Algorithmic mechanics and edge cases:**
Collisions occur only when `ast < 0` and `stack[-1] > 0` (moving towards each other). If both move in the same direction or move away from each other (`stack[-1] < 0` and `ast > 0`), no collision is possible and `ast` is appended. When masses match (`diff == 0`), both explode. Edge cases include all asteroids moving in the same direction, all asteroids exploding (`[8, -8] -> []`), and negative asteroids preceding positive asteroids (`[-2, -1, 1, 2] -> [-2, -1, 1, 2]`).

## Why

A stack models sequential localized physical collisions because newly arriving asteroids only collide with the most recent survivor.

## Worked Case

asteroids=[10, 2, -5]. stack=[10, 2]. ast=-5: collides with 2 (2 explodes, popped). collides with 10 (diff = 10-5=5 > 0, -5 explodes, ast=0). stack=[10].

## Risk

Assuming negative asteroids always collide; negative asteroids at the front of the array move left into empty space and never collide.

## Trade-off

Setting ast = 0 and breaking acts as an in-place annihilation flag without requiring complex boolean variables.

## Try This

Test with [5, 10, -5] -> 10 and -5 collide, 10 survives -> output [5, 10].

## Follow-ups

### What happens when multiple consecutive asteroids explode simultaneously?

The while loop naturally chains pops until either the incoming asteroid explodes, stack is empty, or stack top is moving left.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you remove k digits from a number string to form the smallest possible number?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Remove K Digits (LeetCode 402) removes `k` digits from a non-negative integer string `num` so that the remaining digits form the smallest possible number. The optimal solution uses a monotonic increasing stack: greedily remove the previous digit whenever the current digit is smaller.

```python
def remove_kdigits(num: str, k: int) -> str:
    stack: list[str] = []
    for digit in num:
        while k > 0 and stack and stack[-1] > digit:
            stack.pop()
            k -= 1
        stack.append(digit)
    # If k removals remain, truncate from the right
    final_stack = stack[:-k] if k > 0 else stack
    # Strip leading zeros
    res = "".join(final_stack).lstrip("0")
    return res if res else "0"
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `num`. Each digit is pushed and popped at most once.
- **Space Complexity:** $O(n)$ auxiliary space to store characters on the stack.

**Algorithmic mechanics and edge cases:**
To make a number as small as possible, digits in higher place values (leftmost) should be as small as possible. If `stack[-1] > digit`, replacing `stack[-1]` with `digit` strictly decreases the number's magnitude. If all digits are in non-decreasing order (e.g. `"12345"`), we truncate the remaining `k` digits from the tail `stack[:-k]`. Leading zeros are stripped using `.lstrip('0')`. Edge cases include $k = n$ (returns `"0"`), numbers with trailing zeros (`"10200", k=1 -> "200"`), and strictly ascending digits.

## Why

A monotonic increasing stack greedily minimizes leading high-place digits to produce the minimal numerical magnitude.

## Worked Case

num='10200', k=1. i=0 ('1'): stack=['1']. i=1 ('0'): '1' > '0', pop '1', k=0, stack=['0']. Next digits '2','0','0' append. stack=['0','2','0','0']. lstrip('0') -> '200'.

## Risk

Failing to remove remaining k digits when the string is already ascending (e.g., '12345', k=3) produces a larger number.

## Trade-off

Using list stack avoids string immutability reallocations during iterative popping.

## Try This

Trace num='1432219', k=3: 4 pops for 3; 3 pops for 2; 2 pops for 1; leaves '1219'.

## Follow-ups

### How do you find the largest possible number by removing k digits?

Invert the condition to a monotonic decreasing stack: while k > 0 and stack and stack[-1] < digit: stack.pop().

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you decode an encoded string with nested repetition brackets?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Decode String (LeetCode 394) decodes strings formatted like `k[encoded_string]`, where the `encoded_string` inside square brackets is repeated exactly `k` times. The optimal solution uses a stack storing tuples of `(previous_string, multiplier)` to resolve arbitrarily nested bracket expressions.

```python
def decode_string(s: str) -> str:
    stack: list[tuple[str, int]] = []
    curr_str = ""
    curr_num = 0
    for char in s:
        if char.isdigit():
            curr_num = curr_num * 10 + int(char)
        elif char == '[':
            stack.append((curr_str, curr_num))
            curr_str = ""
            curr_num = 0
        elif char == ']':
            prev_str, num = stack.pop()
            curr_str = prev_str + curr_str * num
        else:
            curr_str += char
    return curr_str
```

**Complexity analysis:**
- **Time Complexity:** $O(N)$ where $N$ is the length of the final decoded string. Every character in the output is generated and concatenated.
- **Space Complexity:** $O(N)$ to hold intermediate and final string buffers on the stack.

**Algorithmic mechanics and edge cases:**
Encountering `'['` pushes the currently accumulated string context and the repetition multiplier onto the stack, resetting both for the nested scope. Encountering `']'` pops the enclosing context, multiplies the current inner string by `num`, and prepends the outer `prev_str`. Edge cases include multi-digit numbers (e.g. `100[leetcode]`), multiple sibling brackets (`2[a]3[b]`), and deeply nested brackets (`2[a3[b]]`).

## Why

A stack naturally isolates nested variable scopes, restoring parent string buffers upon matching closing brackets.

## Worked Case

s='2[abc]3[cd]ef'. 2[abc] decodes to 'abcabc'. 3[cd] decodes to 'cdcdcd'. 'ef' appends. Result: 'abcabccdcdcdef'.

## Risk

Resetting curr_num without parsing multi-digit numbers (num = num * 10 + int(c)) corrupts counts >= 10.

## Trade-off

Stack iteration is simpler and avoids the maximum recursion depth limit associated with recursive parsing.

## Try This

Trace '3[a2[c]]': stack pushes ('', 3) on first '[', pushes ('a', 2) on second '['; 'c' repeats 2x -> 'acc'; repeats 3x -> 'accaccacc'.

## Follow-ups

### Can this be implemented as a recursive descent parser?

Yes, pass an index pointer; on '[' call decode_subproblem recursively and return when ']' is met.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you search for a target value in a rotated sorted array in O(log n) time?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Search in Rotated Sorted Array (LeetCode 33) finds the index of a target in an array sorted in ascending order with distinct values rotated at an unknown pivot. The optimal solution uses a modified binary search: at any midpoint `mid`, at least one half of the array is guaranteed to be strictly sorted, allowing the algorithm to determine whether `target` falls within the sorted interval and halve the search space.

```python
def search_rotated_array(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        # Check if left half is sorted
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        # Otherwise right half must be sorted
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```

**Complexity analysis:**
- **Time Complexity:** $O(\log n)$ where $n$ is the length of `nums`. Each step cuts the search space in half.
- **Space Complexity:** $O(1)$ auxiliary space because execution requires only index pointers.

**Algorithmic mechanics and edge cases:**
Dividing a rotated sorted array at any point always yields one strictly sorted half and one rotated half. If `nums[left] <= nums[mid]`, the left half is monotonic; we then test whether `nums[left] <= target < nums[mid]`. If so, `target` must be in the left half; otherwise it must be in the right. If the left half is not sorted, the right half is guaranteed to be sorted. Edge cases include target not found (returns `-1`), array not rotated (standard binary search), and single-element arrays.

## Why

Identifying the strictly sorted half allows testing boundary inclusion in O(1), maintaining logarithmic reduction.

## Worked Case

nums=[4,5,6,7,0,1,2], target=3. mid=3 (7). Left half [4,7] sorted; 3 is not in [4,7] -> left=4. Subarray [0,1,2], mid=5 (1). Right half [1,2] sorted; 3 is not in [1,2] -> right=4. Subarray [0], mid=4 (0 != 3). Exits, returns -1.

## Risk

Missing <= in nums[left] <= nums[mid] breaks when left == mid on two-element subarrays.

## Trade-off

Modified binary search eliminates the need for an initial O(log n) pass to locate the pivot index.

## Try This

Trace nums=[4, 5, 6, 7, 0, 1, 2] with target=0: left half [4, 5, 6, 7] is sorted; target 0 is not within [4, 7], so search moves to right half.

## Follow-ups

### What happens if duplicate values are allowed in the array (Search in Rotated Sorted Array II)?

When nums[left] == nums[mid] == nums[right], you cannot determine which half is sorted; you must increment left and decrement right, degrading worst-case to O(n).

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the minimum element in a rotated sorted array in logarithmic time?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Find Minimum in Rotated Sorted Array (LeetCode 153) finds the minimum element in an array of unique sorted elements rotated between 1 and $n$ times. The optimal solution uses binary search comparing `nums[mid]` directly against `nums[right]` to locate the rotation cliff.

```python
def find_min(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] > nums[right]:
            # Cliff is to the right; minimum must be in right half
            left = mid + 1
        else:
            # Minimum is at mid or in left half
            right = mid
    return nums[left]
```

**Complexity analysis:**
- **Time Complexity:** $O(\log n)$ where $n$ is the length of `nums`. Halves search space on each step.
- **Space Complexity:** $O(1)$ auxiliary space because it uses only two index pointers.

**Algorithmic mechanics and edge cases:**
Because elements are unique, if `nums[mid] > nums[right]`, the rotation pivot (the minimum element) must lie strictly to the right of `mid`, so we set `left = mid + 1`. If `nums[mid] <= nums[right]`, the right half is sorted, meaning the minimum lies at `mid` or to the left of `mid`, so we set `right = mid` (retaining `mid` as a candidate). The loop terminates when `left == right`. Edge cases include fully sorted arrays (not rotated), two-element arrays, and single-element arrays.

## Why

Comparing nums[mid] against nums[right] determines whether the inflection cliff lies to the left or right of midpoint.

## Worked Case

nums=[4,5,6,7,0,1,2]. mid=3 (val 7 > 2) -> left=4. Subarray [0,1,2]: mid=5 (val 1 < 2) -> right=5. Subarray [0,1]: mid=4 (val 0 < 1) -> right=4. left==right=4. nums[4]=0.

## Risk

Setting right = mid - 1 instead of right = mid can accidentally discard the minimum element when nums[mid] is the minimum.

## Trade-off

Comparing against nums[right] handles both rotated and unrotated arrays seamlessly without special casing.

## Try This

Trace nums=[3, 4, 5, 1, 2]: mid=2 (5 > 2) -> left=3 (1); mid=3 (1 < 2) -> right=3; terminates with min=1.

## Follow-ups

### How do you find the minimum if duplicates are allowed (LeetCode 154)?

When nums[mid] == nums[right], decrement right -= 1 to safely shrink the boundary while preserving the minimum candidate.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you search for a target in an m x n matrix with sorted rows and columns in logarithmic time?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Search a 2D Matrix (LeetCode 74) searches for a target value in an $m \times n$ integer matrix where each row is sorted and the first integer of each row is greater than the last integer of the previous row. The optimal solution treats the matrix as a virtual 1D sorted array of length $m \cdot n$, performing binary search with coordinate mapping `row = mid // n` and `col = mid % n`.

```python
def search_matrix(matrix: list[list[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False
    m, n = len(matrix), len(matrix[0])
    left, right = 0, m * n - 1
    while left <= right:
        mid = left + (right - left) // 2
        val = matrix[mid // n][mid % n]
        if val == target:
            return True
        elif val < target:
            left = mid + 1
        else:
            right = mid - 1
    return False
```

**Complexity analysis:**
- **Time Complexity:** $O(\log(m \cdot n))$ which equals $O(\log m + \log n)$, finding the element in pure logarithmic time.
- **Space Complexity:** $O(1)$ auxiliary space because it uses virtual 1D indexing without copying matrix cells.

**Algorithmic mechanics and edge cases:**
Because each row's start is strictly greater than the previous row's end, the 2D matrix unfolds into a strictly sorted 1D array of size $m \times n$. Virtual indexing maps any 1D index `idx` to 2D row `idx // n` and column `idx % n` in $O(1)$ time. Edge cases include $1 \times 1$ matrices, single-row matrices, single-column matrices, and target smaller than `matrix[0][0]` or larger than `matrix[-1][-1]`.

## Why

Virtual 1D coordinate mapping converts 2D matrix lookups into standard binary search in O(log(m*n)) time.

## Worked Case

matrix=[[1,3,5,7],[10,11,16,20],[23,30,34,60]], target=13. left=0, right=11. mid=5 -> (1,1) val 11 < 13 -> left=6. mid=8 -> (2,0) val 23 > 13 -> right=7. mid=6 -> (1,2) val 16 > 13 -> right=5. left > right. Returns False.

## Risk

Dividing by m instead of n during coordinate mapping inverts row and column coordinate translations.

## Trade-off

A single virtual binary search is cleaner and faster than doing two separate binary searches (one for row, one for column).

## Try This

Search 3 in matrix=[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]] and trace mid=5 (idx // 4 = 1, idx % 4 = 1 -> val=11).

## Follow-ups

### How do you solve Search a 2D Matrix II where rows and columns are sorted but row starts do not exceed previous ends?

Start from the top-right corner (0, n - 1); if target is smaller move left (col -= 1), if larger move down (row += 1) in O(m + n) time.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the minimum integer eating speed using binary search on answer?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Koko Eating Bananas (LeetCode 875) finds the minimum integer eating speed $k$ such that Koko can eat all bananas from $n$ piles within $h$ hours. The optimal solution uses binary search on answer over the range $[1, \max(\text{piles})]$, evaluating whether a speed $k$ allows finishing within $h$ hours using a monotonic predicate.

```python
import math

def min_eating_speed(piles: list[int], h: int) -> int:
    left, right = 1, max(piles)
    while left < right:
        mid = left + (right - left) // 2
        # Hours required at speed mid
        hours = sum(math.ceil(p / mid) for p in piles)
        if hours <= h:
            # Speed is sufficient, try slower speed
            right = mid
        else:
            # Speed is too slow, must eat faster
            left = mid + 1
    return left
```

**Complexity analysis:**
- **Time Complexity:** $O(n \log(\max(\text{piles})))$ where $n$ is the number of piles. Binary search takes $\log(\max)$ steps, each taking $O(n)$ to sum hours.
- **Space Complexity:** $O(1)$ auxiliary space because it only calculates sums over piles.

**Algorithmic mechanics and edge cases:**
The predicate function $f(k) = (\text{total\_hours}(k) \le h)$ is monotonic: if speed $k$ is sufficient to finish in $h$ hours, any speed $k' > k$ is also sufficient. Binary search exploits this monotonicity to locate the smallest speed where $f(k)$ becomes true. At each pile, Koko spends $\lceil p / k \rceil = (p + k - 1) // k$ hours. Edge cases include $h = \text{len}(piles)$ (speed must be $\max(piles)$) and large pile sizes up to $10^9$.

## Why

The total hours function is monotonically decreasing with speed, allowing binary search to find the minimal feasible parameter.

## Worked Case

piles=[30,11,23,4,20], h=5. Range [1, 30]. Since h==len(piles), Koko must eat at least the largest pile in 1 hour. Result is max(piles) = 30.

## Risk

Using right = sum(piles) unnecessarily expands binary search bounds; max(piles) is the absolute upper bound needed.

## Trade-off

Using (p + mid - 1) // mid integer arithmetic avoids floating-point ceiling imprecision on large pile values.

## Try This

Trace piles=[3, 6, 7, 11] with h=8: max speed is 11; binary search converges on optimal speed k=4 (hours = 1 + 2 + 2 + 3 = 8).

## Follow-ups

### How does this pattern apply to Capacity To Ship Packages Within D Days (LeetCode 1011)?

Binary search on ship capacity over [max(weights), sum(weights)], checking if days_needed(capacity) <= D.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/math.html

# How do you find a peak element in an array in logarithmic time?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Find Peak Element (LeetCode 162) finds an element that is strictly greater than its neighbors in an array where $nums[i] \neq nums[i+1]$. The optimal solution uses binary search following the upward slope: if `nums[mid] < nums[mid + 1]`, a peak is guaranteed to exist in the right half; otherwise, a peak exists at `mid` or to its left.

```python
def find_peak_element(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] < nums[mid + 1]:
            left = mid + 1  # Ascending slope -> peak is to the right
        else:
            right = mid      # Descending slope -> peak is at mid or to the left
    return left
```

**Complexity analysis:**
- **Time Complexity:** $O(\log n)$ where $n$ is the length of `nums`. Each step halves the search range.
- **Space Complexity:** $O(1)$ auxiliary space because it only tracks two indices.

**Algorithmic mechanics and edge cases:**
Because $nums[-1] = nums[n] = -\infty$, if `nums[mid] < nums[mid + 1]`, following the ascending slope upwards must eventually reach a peak, because either the array keeps climbing to the final element (which is a peak compared to $-\infty$) or encounters a drop (which creates an interior peak). Thus, we can safely eliminate the left half. Edge cases include strictly increasing arrays (returns $n-1$), strictly decreasing arrays (returns $0$), and single-element arrays.

## Why

Walking in the direction of the positive gradient guarantees reaching a local maximum in logarithmic time.

## Worked Case

nums=[1,2,1,3,5,6,4]. mid=3 (3 < 5) -> left=4. Subarray [5,6,4]: mid=5 (6 > 4) -> right=5. left==right=5. nums[5]=6 is a peak. Returns 5.

## Risk

Comparing nums[mid] with nums[mid - 1] without checking mid > 0 causes IndexError when mid == 0.

## Trade-off

Binary search finds any valid local peak in O(log n); finding the global maximum requires scanning all n elements.

## Try This

Trace nums=[1, 2, 3, 1]: mid=1 (2 < 3) -> left=2; mid=2 (3 > 1) -> right=2; loop terminates at peak index 2.

## Follow-ups

### Can this be extended to find a peak in a 2D matrix in O(m log n) time?

Yes, find the row maximum at middle column mid_col, and check if it is greater than left/right neighbors; halve columns accordingly.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you design a time-based key-value store supporting timestamped lookups?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Time Based Key-Value Store (LeetCode 981) stores multiple values for the same key at different timestamps and retrieves the key's value at a given `timestamp` (or the largest `prev_timestamp <= timestamp`). The optimal solution uses a hash map of lists containing `(timestamp, value)` pairs, using binary search (`bisect_right`) to find the valid value in $O(\log n)$ time.

```python
from bisect import bisect_right
from collections import defaultdict

class TimeMap:
    def __init__(self):
        self.store: defaultdict[str, list[tuple[int, str]]] = defaultdict(list)

    def set(self, key: str, value: str, timestamp: int) -> None:
        # Timestamps are strictly increasing for each key
        self.store[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        if key not in self.store:
            return ""
        values = self.store[key]
        # Binary search for rightmost timestamp <= query timestamp
        idx = bisect_right(values, (timestamp, chr(127))) - 1
        return values[idx][1] if idx >= 0 else ""
```

**Complexity analysis:**
- **Time Complexity:** $O(1)$ for `set` operations (appending to list). $O(\log n)$ for `get` operations where $n$ is the number of timestamps recorded for `key`.
- **Space Complexity:** $O(N)$ where $N$ is total number of `set` entries stored in the data structure.

**Algorithmic mechanics and edge cases:**
Because timestamps are strictly increasing per problem constraints, entries in `self.store[key]` are naturally sorted by timestamp. `bisect_right(values, (timestamp, chr(127))) - 1` locates the largest timestamp $\le \text{timestamp}$ in $O(\log n)$ time. If all recorded timestamps are greater than the query timestamp, `idx == -1` and `""` is returned. Edge cases include querying non-existent keys, timestamps earlier than all recorded values, and exact timestamp matches.

## Why

Natural chronological ordering allows append-only O(1) writes with O(log n) binary search lookups on timestamps.

## Worked Case

set('love', 'high', 10), set('love', 'low', 20). get('love', 5) -> earlier than 10, returns ''. get('love', 10) -> 'high'. get('love', 15) -> 'high'. get('love', 25) -> 'low'.

## Risk

Linear scanning of the timestamp list degrades get operations to O(n), causing time limit exceeded on high-volume queries.

## Trade-off

List appending assumes monotonically increasing timestamps; if timestamps arrive out of order, bisect.insort takes O(n).

## Try This

set('foo', 'bar', 1); get('foo', 1) -> 'bar'; get('foo', 3) -> 'bar'; set('foo', 'bar2', 4); get('foo', 4) -> 'bar2'; get('foo', 3) -> 'bar'.

## Follow-ups

### How is this data structure implemented in production time-series databases like Prometheus?

Prometheus groups samples in memory into 2-hour chunks sorted by timestamp, using delta-of-delta compression and binary search for lookups.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/bisect.html

# How do you solve Climbing Stairs using space-optimized dynamic programming?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Climbing Stairs (LeetCode 70) calculates the number of distinct ways to climb a staircase of $n$ steps taking either 1 or 2 steps at a time. The optimal solution uses dynamic programming with two rolling state variables, matching the Fibonacci recurrence $dp[i] = dp[i-1] + dp[i-2]$ in $O(n)$ time and $O(1)$ space.

```python
def climb_stairs(n: int) -> int:
    if n <= 2:
        return n
    prev2 = 1  # ways to reach step 1
    prev1 = 2  # ways to reach step 2
    for _ in range(3, n + 1):
        curr = prev1 + prev2
        prev2 = prev1
        prev1 = curr
    return prev1
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ requiring a single linear loop of $n - 2$ iterations.
- **Space Complexity:** $O(1)$ auxiliary memory because only two previous step values are retained in memory.

**Algorithmic mechanics and edge cases:**
To reach step $i$, one must take 1 step from step $i-1$, or 2 steps from step $i-2$. Therefore, the total combinations to reach step $i$ is $dp[i-1] + dp[i-2]$. Storing the entire $O(n)$ array is unnecessary because computing $dp[i]$ only requires the immediately preceding two values. Edge cases include $n = 1$ (1 way) and $n = 2$ (2 ways).

## Why

Because state transitions depend strictly on the two preceding steps, rolling variables reduce memory from O(n) to O(1).

## Worked Case

n=3. prev2=1, prev1=2. Loop runs for step 3: curr = 2 + 1 = 3. Returns 3. Combinations are: 1+1+1, 1+2, 2+1.

## Risk

Unmemoized naive recursion Fibonacci(n) takes exponential O(2^n) time and crashes due to repeated subproblems.

## Trade-off

Rolling state iteration achieves O(1) space and avoids matrix exponentiation complexity for standard constraints.

## Try This

Compute climb_stairs(4): step 1=1, step 2=2, step 3=3, step 4=5; verify 5 combinations.

## Follow-ups

### How can you compute climb_stairs in O(log n) time?

Use Matrix Exponentiation with transformation matrix [[1, 1], [1, 0]], squaring matrices using binary exponentiation in O(log n) steps.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you maximize the total loot in House Robber without triggering alarms?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** House Robber (LeetCode 198) maximizes the sum of money robbed from houses along a street without robbing any two adjacent houses. The optimal solution uses dynamic programming: for each house, decide whether to rob it (adding its value to the maximum loot from two houses back) or skip it (keeping the maximum loot from the adjacent house).

```python
def rob(nums: list[int]) -> int:
    rob_prev2 = 0  # max money robbing up to house i - 2
    rob_prev1 = 0  # max money robbing up to house i - 1
    for num in nums:
        curr = max(rob_prev1, rob_prev2 + num)
        rob_prev2 = rob_prev1
        rob_prev1 = curr
    return rob_prev1
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of houses, visiting each house once.
- **Space Complexity:** $O(1)$ auxiliary space because it uses two rolling variables rather than an $O(n)$ DP array.

**Algorithmic mechanics and edge cases:**
At each house with value `num`, the state recurrence is $dp[i] = \max(dp[i-1], dp[i-2] + num)$. Skipping the house preserves $dp[i-1]$; robbing the house adds its loot to $dp[i-2]$. We only need the previous two optimal values, allowing $O(1)$ rolling variable space. Edge cases include empty list (returns 0), single house `[5] -> 5`, and two houses `[1, 2] -> 2`.

## Why

The non-adjacent constraint creates an optimal substructure depending only on max(rob(i-1), rob(i-2) + val).

## Worked Case

nums=[1, 2, 3, 1]. i=0 (1): curr=max(0, 0+1)=1. i=1 (2): curr=max(1, 0+2)=2. i=2 (3): curr=max(2, 1+3)=4. i=3 (1): curr=max(4, 2+1)=4. Result: 4.

## Risk

Assuming greedy alternating choices (even vs odd houses) fails on cases like [2, 1, 1, 2] where optimal is robbing 2 and 2 (sum=4).

## Trade-off

Rolling state variables achieve strict O(1) space without allocating an auxiliary DP table.

## Try This

Test with nums=[2, 7, 9, 3, 1]: rob house 0 (2), house 2 (9), house 4 (1) -> total 12.

## Follow-ups

### How do you solve House Robber II where houses are arranged in a circle?

Run the algorithm twice: once for houses nums[:-1] (excluding last house) and once for nums[1:] (excluding first house), returning max.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the fewest number of coins needed to make up a given amount?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Coin Change (LeetCode 322) finds the minimum number of coins needed to make up a target amount using an infinite supply of given coin denominations. The optimal solution uses bottom-up dynamic programming: compute the minimum coins for every sub-amount from 1 to `amount` using recurrence $dp[i] = 1 + \min(dp[i - c])$.

```python
def coin_change(coins: list[int], amount: int) -> int:
    dp = [float("inf")] * (amount + 1)
    dp[0] = 0  # Base case: 0 coins needed for amount 0
    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != float("inf") else -1
```

**Complexity analysis:**
- **Time Complexity:** $O(\text{amount} \times |\text{coins}|)$. For each coin, we update the DP table from `coin` up to `amount`.
- **Space Complexity:** $O(\text{amount})$ auxiliary space to store the DP array.

**Algorithmic mechanics and edge cases:**
Greedy choice fails for general coin systems (e.g. coins=[1, 3, 4], amount=6: greedy takes 4+1+1=3 coins, but optimal DP takes 3+3=2 coins). Dynamic programming systematically evaluates all denominations. Iterating `i` from `coin` to `amount` implements the *unbounded knapsack* pattern, allowing coins to be reused multiple times. Edge cases include `amount = 0` (returns 0), impossible amounts (returns `-1`), and coins larger than `amount`.

## Why

Unbounded knapsack dynamic programming evaluates all valid combinations to guarantee the global minimum.

## Worked Case

coins=[2], amount=3. dp[0]=0, dp[1]=inf, dp[2]=1, dp[3]=min(inf, dp[1]+1)=inf. dp[3]==inf -> returns -1 (impossible).

## Risk

A greedy approach selecting the largest coin fails on arbitrary currency systems and returns non-optimal counts.

## Trade-off

Bottom-up 1D array iteration is cache-efficient and avoids recursive call stack overhead.

## Try This

Test coins=[1, 2, 5], amount=11: dp builds 11=5+5+1 -> 3 coins.

## Follow-ups

### How do you count the number of combinations that make up the amount (Coin Change II)?

Change recurrence to dp[i] += dp[i - coin] with coin loop outer to count unique combinations without permutations.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the length of the longest strictly increasing subsequence in O(n log n) time?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Longest Increasing Subsequence (LeetCode 300) finds the length of the longest strictly increasing subsequence in an array. The optimal solution uses patience sorting with binary search (`bisect_left`): maintain an array `tails` where `tails[i]` stores the smallest tail element among all increasing subsequences of length $i + 1$.

```python
from bisect import bisect_left

def length_of_lis(nums: list[int]) -> int:
    tails: list[int] = []
    for x in nums:
        idx = bisect_left(tails, x)
        if idx == len(tails):
            tails.append(x)  # x is larger than all tails; extends LIS length
        else:
            tails[idx] = x   # x can form a smaller tail for subsequence of length idx + 1
    return len(tails)
```

**Complexity analysis:**
- **Time Complexity:** $O(n \log n)$ where $n$ is the length of `nums`. Each element triggers a binary search over `tails` of length at most $n$.
- **Space Complexity:** $O(n)$ auxiliary space to store the `tails` array.

**Algorithmic mechanics and edge cases:**
`tails` is always strictly sorted, which enables binary search. If incoming number `x` is greater than all elements in `tails`, it extends the maximum LIS length found so far (`tails.append(x)`). If `x` falls within `tails`, it replaces the first element $\ge x$, creating a smaller, more advantageous tail for that subsequence length without changing the current LIS length. Note that `tails` does not necessarily represent the actual LIS elements, but its length strictly equals the LIS length. Edge cases include strictly decreasing arrays (`len=1`), strictly increasing arrays (`len=n`), and arrays with duplicates (`bisect_left` enforces strictly increasing order).

## Why

Patience sorting maintains the minimal tail for every subsequence length, enabling binary search updates in O(log n).

## Worked Case

nums=[0,1,0,3,2,3]. tails updates: [0] -> [0,1] -> [0,1] -> [0,1,3] -> [0,1,2] -> [0,1,2,3]. Final length is 4.

## Risk

A standard O(n^2) nested DP approach times out on arrays with length >= 10,000.

## Trade-off

Patience sorting tracks optimal tail values but requires a predecessor pointer array if the actual subsequence elements must be reconstructed.

## Try This

Trace nums=[10, 9, 2, 5, 3, 7, 101, 18]: tails evolves [10] -> [9] -> [2] -> [2, 5] -> [2, 3] -> [2, 3, 7] -> [2, 3, 7, 101] -> [2, 3, 7, 18] (length 4).

## Follow-ups

### How do you reconstruct the actual sequence of elements forming the LIS in O(n log n)?

Store parent index pointers when replacing or appending elements in tails, then trace back from the final tail element.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/bisect.html

# How do you find the number of unique paths in an m x n grid from top-left to bottom-right?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Unique Paths (LeetCode 62) finds the number of unique paths from the top-left corner to the bottom-right corner of an $m \times n$ grid, moving only down or right. The optimal dynamic programming solution compresses the $m \times n$ grid into a 1D row array, updating cells via $dp[j] = dp[j] + dp[j-1]$ in $O(m \cdot n)$ time and $O(n)$ space.

```python
def unique_paths(m: int, n: int) -> int:
    dp = [1] * n  # Base case: 1 path along the top row
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]
    return dp[-1]
```

**Complexity analysis:**
- **Time Complexity:** $O(m \cdot n)$ requiring $(m - 1) \times (n - 1)$ addition operations.
- **Space Complexity:** $O(\min(m, n))$ auxiliary memory by keeping a single row array.

**Algorithmic mechanics and edge cases:**
Any cell $(i, j)$ can only be reached from $(i-1, j)$ (from above) or $(i, j-1)$ (from the left). Thus, $\text{paths}(i, j) = \text{paths}(i-1, j) + \text{paths}(i, j-1)$. In a 1D row array, `dp[j]` before the update holds the value from the row above $(i-1, j)$, and `dp[j-1]` holds the updated value from the left $(i, j-1)$. Adding `dp[j] += dp[j-1]` performs the state transition in-place. Edge cases include $1 \times n$ and $m \times 1$ grids (always returns 1) and $1 \times 1$ grids.

## Why

Because state transitions only reference the current and previous row, a single 1D array achieves O(n) memory.

## Worked Case

m=3, n=2. dp=[1, 1]. Row 1: dp[1] += dp[0] -> dp=[1, 2]. Row 2: dp[1] += dp[0] -> dp=[1, 3]. Returns 3.

## Risk

Allocating full m x n matrices consumes extra memory; mathematical combinations C(m+n-2, m-1) risk integer overflow in static languages.

## Trade-off

1D DP avoids big-integer factorial division bugs while running in negligible milliseconds.

## Try This

Compute unique_paths(3, 7): dp initialized to [1,1,1,1,1,1,1]; row 1 updates to [1,2,3,4,5,6,7]; row 2 updates to [1,3,6,10,15,21,28]; returns 28.

## Follow-ups

### How do you handle grid obstacles (Unique Paths II)?

If grid[i][j] == 1, set dp[j] = 0; otherwise update dp[j] += dp[j-1] if j > 0.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you determine if you can reach the last index of an array in Jump Game?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Jump Game (LeetCode 55) determines if you can reach the last index starting from index 0, where `nums[i]` represents your maximum jump length from position $i$. The optimal solution uses a greedy approach tracking the maximum reachable index (`max_reach`) in a single linear pass.

```python
def can_jump(nums: list[int]) -> bool:
    max_reach = 0
    for i, jump in enumerate(nums):
        if i > max_reach:
            return False  # Cannot reach index i
        max_reach = max(max_reach, i + jump)
        if max_reach >= len(nums) - 1:
            return True
    return True
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. It performs a single pass with early exit.
- **Space Complexity:** $O(1)$ auxiliary space because it only maintains a single integer variable `max_reach`.

**Algorithmic mechanics and edge cases:**
At any point, `max_reach` is the farthest index we can reach from all previously explored positions. If the current index $i$ is strictly greater than `max_reach`, we have encountered an unreachable gap (e.g. stalled by preceding zeros) and can terminate immediately with `False`. If `max_reach >= len(nums) - 1`, we can reach the end. Edge cases include single-element arrays `[0]` (returns True, already at destination) and arrays with zeros.

## Why

Tracking the maximal reach boundary greedily establishes reachability in O(1) space without backtracking.

## Worked Case

nums=[3, 2, 1, 0, 4]. i=0: reach=3. i=1: reach=max(3, 3)=3. i=2: reach=max(3, 3)=3. i=3: reach=max(3, 3)=3. i=4: i=4 > reach=3 -> cannot reach index 4! Returns False.

## Risk

Using DFS/BFS backtracking explores exponential O(2^n) branches on large arrays filled with identical jump numbers.

## Trade-off

Greedy reach tracking is strictly linear and terminates as soon as max_reach covers the final index.

## Try This

Test nums=[2, 3, 1, 1, 4]: i=0 reaches 2; i=1 reaches 1+3=4 >= 4 -> returns True immediately.

## Follow-ups

### How do you find the minimum number of jumps to reach the last index (Jump Game II)?

Use BFS greedy levels tracking current_end and farthest_reach; when i == current_end, increment jumps and update current_end = farthest_reach.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you determine if an array can be partitioned into two subsets with equal sum?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Partition Equal Subset Sum (LeetCode 416) determines whether an integer array can be partitioned into two subsets with equal sums. The problem reduces to 0/1 Knapsack: check if a subset of `nums` sums to `target = sum(nums) // 2`. The optimal solution uses a 1D boolean DP array or integer bitmask.

```python
def can_partition(nums: list[int]) -> bool:
    total = sum(nums)
    if total % 2 != 0:
        return False
    target = total // 2
    dp = [False] * (target + 1)
    dp[0] = True  # Base case: subset sum of 0 is always possible
    for num in nums:
        # Iterate backwards to ensure each element is used at most once
        for i in range(target, num - 1, -1):
            if dp[i - num]:
                dp[i] = True
        if dp[target]:
            return True
    return dp[target]
```

**Complexity analysis:**
- **Time Complexity:** $O(n \cdot \text{target})$ where $n$ is the length of `nums` and `target` is half the total sum.
- **Space Complexity:** $O(\text{target})$ space for the 1D boolean array (or $O(1)$ integer using bitwise shifts `bits |= bits << num`).

**Algorithmic mechanics and edge cases:**
If the total sum is odd, partitioning into two integer equal sums is impossible (returns `False`). `dp[i]` is True if sum `i` can be formed using a subset. Iterating `i` *backwards* from `target` down to `num` ensures that each number is used at most once (0/1 Knapsack invariant). If we iterated forward, `num` could be added repeatedly like unbounded knapsack. Edge cases include `target < max(nums)` (returns False), single-element arrays, and arrays with duplicate values.

## Why

Iterating backwards across the 1D DP array guarantees 0/1 knapsack element reuse prevention in O(target) space.

## Worked Case

For nums=[1, 5, 11, 5]: total sum is 22; target = 11. Array iteration: num 1 sets dp[1]=True; num 5 sets dp[6], dp[5]=True; num 11 sets dp[11]=True -> target reached, returns True.

## Risk

Iterating forward (range(num, target + 1)) allows a single number to be reused multiple times, producing incorrect sums.

## Trade-off

Bitmasking (bits |= (bits << num)) computes 64 state transitions per CPU instruction, achieving a 64x speedup over boolean arrays.

## Try This

Test with nums=[1, 5, 11, 5]: total=22, target=11; numbers 1, 5, 5 sum to 11 -> returns True.

## Follow-ups

### How do you implement this in a single line using Python's arbitrary-precision integers?

total = sum(nums); return not total % 2 and bool((functools.reduce(lambda b, x: b | (b << x), nums, 1) >> (total // 2)) & 1).

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find if a word exists in a 2D character grid using backtracking?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Word Search (LeetCode 79) checks if a word exists in an $m \times n$ grid of characters, moving sequentially to adjacent cells (horizontally or vertically) without reusing the same cell twice. The optimal solution uses DFS backtracking with in-place cell masking.

```python
def exist(board: list[list[str]], word: str) -> bool:
    m, n = len(board), len(board[0])
    def dfs(r: int, c: int, idx: int) -> bool:
        if idx == len(word):
            return True
        if not (0 <= r < m and 0 <= c < n) or board[r][c] != word[idx]:
            return False
        temp = board[r][c]
        board[r][c] = "#"  # In-place visited mark
        found = (dfs(r + 1, c, idx + 1) or
                 dfs(r - 1, c, idx + 1) or
                 dfs(r, c + 1, idx + 1) or
                 dfs(r, c - 1, idx + 1))
        board[r][c] = temp  # Backtrack restore
        return found
    for r in range(m):
        for c in range(n):
            if board[r][c] == word[0] and dfs(r, c, 0):
                return True
    return False
```

**Complexity analysis:**
- **Time Complexity:** $O(m \cdot n \cdot 3^L)$ where $L$ is word length. From the second character onwards, we explore at most 3 directions (excluding the cell we came from).
- **Space Complexity:** $O(L)$ auxiliary space for the recursion call stack.

**Algorithmic mechanics and edge cases:**
At each cell, we verify boundary conditions and character match `board[r][c] == word[idx]`. To avoid visiting the same cell twice along a path without allocating an $m \times n$ visited matrix, we temporarily replace `board[r][c]` with `'#'` and restore it after exploring all 4 directions (backtracking). Edge cases include word longer than total grid cells (returns False), single-letter words, and palindromic words requiring reverse search pruning.

## Why

Temporarily masking board[r][c] = '#' prevents cycle revisits in-place with O(1) extra memory.

## Worked Case

board=[['a','b'],['c','d']], word='abcd'. Starts at (0,0) 'a'. Moves to (0,1) 'b'. From 'b', neighbors are 'a' (#, skipped) and (1,1) 'd' (mismatch with 'c'). Backtracks. Returns False.

## Risk

Failing to restore board[r][c] = temp corrupts grid characters for subsequent search iterations from other starting cells.

## Trade-off

In-place masking avoids allocating and clearing an m x n boolean visited grid for each path exploration.

## Try This

Search 'ABCCED' in [['A','B','C','E'],['S','F','C','S'],['A','D','E','E']] and trace path A->B->C->C->E->D.

## Follow-ups

### How do you prune searches when word contains characters with high frequency on the board?

If word ends with fewer occurrences than it starts on the board, reverse word to start searching from rare characters first.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you generate all possible subsets (the power set) of an array of unique integers?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Subsets (LeetCode 78) generates the power set (all $2^n$ subsets) of a collection of unique integers. The optimal solution uses backtracking to explore the binary decision tree (include or exclude each element) or cascading iterative expansion.

```python
def subsets(nums: list[int]) -> list[list[int]]:
    res: list[list[int]] = []
    subset: list[int] = []
    def backtrack(idx: int) -> None:
        if idx == len(nums):
            res.append(subset.copy())
            return
        # Decision 1: Include nums[idx]
        subset.append(nums[idx])
        backtrack(idx + 1)
        # Decision 2: Exclude nums[idx]
        subset.pop()
        backtrack(idx + 1)
    backtrack(0)
    return res
```

**Complexity analysis:**
- **Time Complexity:** $O(n \cdot 2^n)$ because there are $2^n$ subsets, and copying each subset to the output list takes $O(n)$ time.
- **Space Complexity:** $O(n)$ auxiliary space to maintain the `subset` stack during recursion (excluding output list).

**Algorithmic mechanics and edge cases:**
For each element $x$, every valid subset either includes $x$ or excludes $x$. The recursion tree branches twice at each index, creating a full binary tree of depth $n$ with $2^n$ leaf nodes. Alternatively, cascading iteration starts with `res = [[]]` and for each `x in nums`, appends `s + [x]` for every existing subset `s`. Edge cases include empty list `nums = []` (returns `[[]]`), single-element arrays `[1] -> [[], [1]]`, and arrays with negative numbers.

## Why

Binary decision tree branching (include or exclude) systematically enumerates all 2^n subsets in linear recursion depth.

## Worked Case

nums=[0]. Decision tree: root -> include 0: [0]; exclude 0: []. Leaves output [[0], []]. Total 2^1 = 2 subsets.

## Risk

Appending subset directly without subset.copy() causes all entries in res to reference the same mutable empty list.

## Trade-off

Backtracking maintains a single working list in O(n) space; bitmask generation (0 to 2^n - 1) is iterative and avoids recursion.

## Try This

Trace nums=[1, 2]: backtrack produces [[1, 2], [1], [2], []].

## Follow-ups

### How do you handle duplicate numbers in nums so that the power set contains no duplicate subsets (Subsets II)?

Sort nums first; during the exclude branch, skip identical adjacent elements using while idx + 1 < len(nums) and nums[idx] == nums[idx+1]: idx += 1.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the single number that appears once in an array where all other numbers appear twice?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Single Number (LeetCode 136) finds the single element that appears only once in an array where every other element appears exactly twice. The optimal solution uses the bitwise XOR operator (`^`), which cancels out all paired numbers in $O(n)$ time and $O(1)$ space.

```python
def single_number(nums: list[int]) -> int:
    res = 0
    for num in nums:
        res ^= num
    return res
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`, scanning each element once.
- **Space Complexity:** $O(1)$ auxiliary space because it only maintains a single accumulator variable.

**Algorithmic mechanics and edge cases:**
Bitwise XOR has three mathematical properties: 1) $x \oplus 0 = x$ (identity); 2) $x \oplus x = 0$ (self-inverse); 3) commutative and associative ($a \oplus b \oplus a = a \oplus a \oplus b = 0 \oplus b = b$). XORing all numbers together cancels every paired duplicate out to 0, leaving only the unique single number. Edge cases include single-element array `[1] -> 1`, negative numbers, and arrays with large integers.

## Why

Bitwise XOR cancellation (x ^ x == 0 and x ^ 0 == x) isolates the unique element in a single pass without extra memory.

## Worked Case

For nums=[4, 1, 2, 1, 2]: res starts at 0. res ^= 4 (4); res ^= 1 (5); res ^= 2 (7); res ^= 1 (6); res ^= 2 (4). Paired duplicates cancel out, returning 4.

## Risk

Using a hash set or Counter takes O(n) memory, which violates the strict O(1) memory constraint.

## Trade-off

XOR accumulator uses zero extra memory and is faster than any hash table or sorting approach.

## Try This

Test nums=[4, 1, 2, 1, 2]: (1^1) cancels to 0, (2^2) cancels to 0, leaving 4 ^ 0 = 4.

## Follow-ups

### How do you find the single number if every other number appears three times (Single Number II)?

Count set bits modulo 3 for each of the 32 bit positions, or use two bitmasks (ones, twos) tracking bit frequencies modulo 3.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you determine if two strings are valid anagrams in Python?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** To determine if two strings are valid anagrams (LeetCode 242), count the occurrence frequency of each character across both strings and assert that the character frequencies are identical. In Python, this is accomplished in optimal linear time using a single hash table or fixed-size array tallying character counts.

```python
def is_anagram(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    counts: dict[str, int] = {}
    for char in s:
        counts[char] = counts.get(char, 0) + 1
    for char in t:
        if char not in counts or counts[char] == 0:
            return False
        counts[char] -= 1
    return True
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of the strings. A single pass over string `s` builds the dictionary, and a single pass over string `t` decrements counts with early termination upon encountering an unexpected character.
- **Space Complexity:** $O(1)$ auxiliary memory when constrained to standard alphabets (e.g. at most 26 lowercase English letters), or $O(k)$ where $k$ is the distinct Unicode alphabet size.

**Algorithmic mechanics and edge cases:**
A naive approach sorts both strings in $O(n \log n)$ time, which allocates $O(n)$ memory for new string buffers. The single-pass frequency count terminates immediately if lengths mismatch or if a character in `t` exceeds its quota in `s`. Edge cases include empty strings, identical single characters, strings with identical lengths but different frequency distributions (e.g., 'aa' and 'bb'), and Unicode graphemes.

## Why

Frequency counting provides strict linear time validation without incurring the O(n log n) sorting overhead or auxiliary string allocations.

## Worked Case

For s='anagram' and t='nagaram': len check passes (7==7); counts builds {'a':3, 'n':1, 'g':1, 'r':1, 'm':1}; second loop decrements each letter down to zero without missing keys, returning True.

## Risk

Comparing naive sorted strings creates new list and string allocations that blow memory on multi-megabyte text buffers.

## Trade-off

Using collections.Counter simplifies syntax to one line but incurs tuple-allocation overhead compared to an inlined dictionary loop.

## Try This

Test with string 'rat' and 'car' to verify that count decrement detects mismatched letter counts and returns False on first exhaustion.

## Follow-ups

### How would you handle Unicode input where characters may have multiple equivalent representations?

Normalize both strings using unicodedata.normalize('NFC', s) before counting, ensuring precomposed characters and combining characters resolve to identical code point sequences.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/collections.html

# How do you group anagrams together from a list of strings?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Grouping anagrams (LeetCode 49) groups words sharing identical character frequencies together into sublists. The optimal solution uses a hash map whose keys represent canonical anagram signatures, mapping each canonical signature to a list of matching original strings.

```python
from collections import defaultdict

def group_anagrams(strs: list[str]) -> list[list[str]]:
    groups: defaultdict[tuple[int, ...], list[str]] = defaultdict(list)
    for s in strs:
        count = [0] * 26
        for char in s:
            count[ord(char) - ord('a')] += 1
        groups[tuple(count)].append(s)
    return list(groups.values())
```

**Complexity analysis:**
- **Time Complexity:** $O(n \cdot k)$ where $n$ is the number of strings and $k$ is the maximum length of a string in the list. Counting 26 character frequencies avoids sorting each individual string.
- **Space Complexity:** $O(n \cdot k)$ to store the grouped strings inside the hash map table.

**Algorithmic mechanics and edge cases:**
While sorting each word yields an $O(n \cdot k \log k)$ runtime, building a 26-element integer tuple `(c_0, c_1, ..., c_25)` executes in strictly linear $O(k)$ per string. Tuples are immutable and hashable, making them ideal dictionary keys in Python. Edge cases include empty string lists `['']`, words consisting of single distinct letters, and inputs with high duplicate frequencies.

## Why

Tuple frequency signatures establish an O(n * k) linear hashing grouping without sorting each individual word.

## Worked Case

Input: ['eat', 'tea', 'tan', 'ate', 'nat', 'bat']. Word 'eat' generates tuple with index 0=1, 4=1, 19=1. Words 'tea' and 'ate' match this exact tuple, grouping them into ['eat', 'tea', 'ate'].

## Risk

Using sorted strings as dictionary keys incurs an unnecessary O(k log k) sorting step per word, degrading throughput on long strings.

## Trade-off

Constructing 26-element tuples trades a small constant memory overhead for eliminating string sorting completely.

## Try This

Trace with ['eat', 'tea', 'tan', 'ate', 'nat', 'bat'] and verify that 'eat', 'tea', and 'ate' map to the identical count tuple.

## Follow-ups

### What if the input strings contain arbitrary Unicode characters rather than 26 lowercase ASCII letters?

Use sorted strings or sorted item tuples from a standard dictionary tally as the hash map key when alphabet bounds are unbounded.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/collections.html

# How do you find the longest palindromic substring in a string?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Longest Palindromic Substring (LeetCode 5) requires locating the longest contiguous sequence that reads identically forwards and backwards. The optimal practical approach expands outwards from every potential palindrome center, checking both single-character odd centers and two-character even centers.

```python
def longest_palindrome(s: str) -> str:
    if not s:
        return ""
    start, end = 0, 0
    def expand(left: int, right: int) -> tuple[int, int]:
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return left + 1, right - 1
    for i in range(len(s)):
        l1, r1 = expand(i, i)
        if r1 - l1 > end - start:
            start, end = l1, r1
        l2, r2 = expand(i, i + 1)
        if r2 - l2 > end - start:
            start, end = l2, r2
    return s[start:end + 1]
```

**Complexity analysis:**
- **Time Complexity:** $O(n^2)$ where $n$ is the length of `s`. There are $2n - 1$ potential centers, and each expansion scans at most $O(n)$ characters.
- **Space Complexity:** $O(1)$ auxiliary space because we only maintain indices rather than allocating auxiliary DP tables.

**Algorithmic mechanics and edge cases:**
A 2D Dynamic Programming table requires $O(n^2)$ space, which causes cache misses and memory allocation pressure. Expanding around centers inspects characters directly in-place with zero memory allocation. Edge cases include strings where all characters are identical ('aaaa'), alternating characters ('abcba'), and single-character strings.

## Why

Expanding around centers achieves the same O(n^2) time bound as dynamic programming while using O(1) auxiliary memory.

## Worked Case

For s='cbbd': odd expansion around each index yields len 1; even expansion around i=1 (s[1]=='b', s[2]=='b') expands to 'bb' (len 2); returns 'bb'.

## Risk

Allocating an n x n boolean dynamic programming matrix consumes O(n^2) memory, which easily causes out-of-memory errors on strings with len > 10,000.

## Trade-off

Center expansion is simpler and more space-efficient than Manacher's O(n) algorithm while being fast enough for all practical constraints.

## Try This

Trace with string 'babad' and observe that center index 1 ('a') expands to substring 'bab' with length 3.

## Follow-ups

### How does Manacher's Algorithm achieve linear O(n) time for longest palindromic substring?

Manacher's algorithm inserts sentinel delimiters between characters and reuses palindrome radius values from previously expanded symmetry boundaries.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you count the number of palindromic substrings in a string?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Counting Palindromic Substrings (LeetCode 647) counts every contiguous substring that forms a palindrome. The optimal solution expands outwards from all $2n - 1$ possible centers, incrementing the count for each valid expansion step until characters mismatch.

```python
def count_substrings(s: str) -> int:
    total = 0
    n = len(s)
    for i in range(n):
        # Odd-length palindromes centered at i
        left, right = i, i
        while left >= 0 and right < n and s[left] == s[right]:
            total += 1
            left -= 1
            right += 1
        # Even-length palindromes centered between i and i+1
        left, right = i, i + 1
        while left >= 0 and right < n and s[left] == s[right]:
            total += 1
            left -= 1
            right += 1
    return total
```

**Complexity analysis:**
- **Time Complexity:** $O(n^2)$ worst-case (e.g. for strings with all identical characters like 'aaaa') and $O(n)$ best-case for strings with no adjacent duplicate characters.
- **Space Complexity:** $O(1)$ auxiliary memory since expansion only tracks pointer indices.

**Algorithmic mechanics and edge cases:**
Every character is individually a palindrome of length 1 (contributing $n$ to the total). As the two pointers `left` and `right` step outward, every step where `s[left] == s[right]` extends a previously verified palindrome, adding exactly 1 to the count. Edge cases include empty strings, single-letter strings, and homogenous strings like 'aaaa' where total equals $n(n+1)/2 = 10$.

## Why

Expanding around 2n - 1 centers counts all palindromes without storing intermediate substrings or dynamic programming matrices.

## Worked Case

Input: s='abc'. Centers: i=0 ('a') -> 1; i=1 ('b') -> 1; i=2 ('c') -> 1. Even centers: (0,1) -> 0; (1,2) -> 0. Total = 3.

## Risk

Generating all O(n^2) substrings and testing each for palindromicity with s == s[::-1] degrades runtime to O(n^3).

## Trade-off

Two-pointer expansion uses O(1) space and avoids the complex sentinel padding logic required by Manacher's linear algorithm.

## Try This

Run with s='aaa' and confirm that individual characters count for 3, pairs count for 2, and the full string counts for 1, totaling 6.

## Follow-ups

### Can this problem be solved with 2D dynamic programming, and what is the trade-off?

Yes, using dp[i][j] = (s[i] == s[j]) and (j - i <= 2 or dp[i+1][j-1]), but it consumes O(n^2) auxiliary memory compared to O(1) for center expansion.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the minimum window substring containing all characters of another string?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Minimum Window Substring (LeetCode 76) finds the shortest substring in `s` that contains all characters of string `t` (including duplicate frequencies). The optimal algorithm uses an adaptive sliding window (`left` and `right`) with a target frequency map and a match counter.

```python
from collections import Counter

def min_window(s: str, t: str) -> str:
    if not s or not t or len(s) < len(t):
        return ""
    target_counts = Counter(t)
    window_counts: dict[str, int] = {}
    required = len(target_counts)
    formed = 0
    ans = (float("inf"), 0, 0)
    left = 0
    for right, char in enumerate(s):
        window_counts[char] = window_counts.get(char, 0) + 1
        if char in target_counts and window_counts[char] == target_counts[char]:
            formed += 1
        while left <= right and formed == required:
            if (right - left + 1) < ans[0]:
                ans = (right - left + 1, left, right)
            char_left = s[left]
            window_counts[char_left] -= 1
            if char_left in target_counts and window_counts[char_left] < target_counts[char_left]:
                formed -= 1
            left += 1
    return "" if ans[0] == float("inf") else s[ans[1]:ans[2] + 1]
```

**Complexity analysis:**
- **Time Complexity:** $O(|s| + |t|)$ because both pointers `left` and `right` traverse the string `s` at most once, and building `target_counts` takes $O(|t|)$.
- **Space Complexity:** $O(|s| + |t|)$ to store character frequencies in the window and target maps.

**Algorithmic mechanics and edge cases:**
The variable `formed` tracks how many unique characters currently meet the required frequency in `t`. When `formed == required`, the window is valid, and the `left` pointer contracts to find the minimal valid window. Edge cases include `len(s) < len(t)`, `t` having repeated identical characters, and cases where no valid window exists.

## Why

Tracking formed character matches avoids re-scanning entire frequency dictionaries on every window contraction step.

## Worked Case

For s='ADOBECODEBANC', t='ABC': right expands to index 5 ('ADOBEC'), formed==3. Left contracts to 0 ('ADOBEC', len 6). Later window at right=12 contracts to left=9 ('BANC', len 4). Result: 'BANC'.

## Risk

Checking dict equality window_counts == target_counts inside the loop adds O(|alphabet|) overhead per character step.

## Trade-off

Maintaining the formed match counter trades an integer variable for eliminating dictionary comparison loops.

## Try This

Trace with s='ADOBECODEBANC' and t='ABC', verifying that the window contracts at 'ADOBEC' and updates at 'BANC'.

## Follow-ups

### How do you optimize this when string s contains many characters not present in t?

Filter s into a list of tuples (index, char) containing only characters present in t, then run sliding window over the filtered list.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/collections.html

# How do you find the longest repeating character replacement with at most k edits?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Longest Repeating Character Replacement (LeetCode 424) determines the length of the longest substring containing identical letters after changing at most `k` characters. The optimal solution uses a sliding window maintaining the maximum frequency of any single character currently in the window.

```python
def character_replacement(s: str, k: int) -> int:
    counts: dict[str, int] = {}
    max_freq = 0
    left = 0
    max_len = 0
    for right, char in enumerate(s):
        counts[char] = counts.get(char, 0) + 1
        max_freq = max(max_freq, counts[char])
        # If window length minus most frequent char exceeds k, contract left
        while (right - left + 1) - max_freq > k:
            counts[s[left]] -= 1
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `s`. Each pointer advances from $0$ to $n-1$ at most once.
- **Space Complexity:** $O(1)$ auxiliary space since `counts` stores at most 26 uppercase English letters.

**Algorithmic mechanics and edge cases:**
The invariant is that a window of length $W = (\text{right} - \text{left} + 1)$ is valid if and only if $W - \text{max\_freq} \le k$. Crucially, we do not need to decrement `max_freq` when contracting `left`, because a smaller `max_freq` cannot produce a window larger than our existing `max_len`. Edge cases include $k \ge n$ (returns $n$), all identical characters, and $k = 0$.

## Why

The condition window_length - max_freq <= k guarantees that at most k replacements can turn the whole window uniform.

## Worked Case

Input: s='ABAB', k=2. Window expands: right=0 ('A'), max_f=1; right=1 ('AB'), len 2, diff 1 <= 2; right=2 ('ABA'), len 3, diff 1 <= 2; right=3 ('ABAB'), len 4, diff 2 <= 2. Result: 4.

## Risk

Recalculating max_freq by scanning all 26 dictionary entries on every step introduces an unnecessary constant slowdown.

## Trade-off

Allowing max_freq to remain temporarily stale during contractions preserves correctness because only higher max_freq can expand the record window.

## Try This

Trace with s='AABABBA', k=1: show that window grows to length 4 ('AABA') and max_len records 4.

## Follow-ups

### Can the window contraction while loop be replaced with a single if statement?

Yes, because once the window reaches a valid size, it only needs to slide forward without shrinking to find if a larger window exists.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you validate a palindrome while ignoring non-alphanumeric characters in-place?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Valid Palindrome (LeetCode 125) checks whether a phrase is a palindrome after converting all uppercase letters to lowercase and removing all non-alphanumeric characters. The optimal solution uses two pointers converging from both ends in-place without creating filtered copies of the string.

```python
def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `s`. Each character is visited at most twice as pointers converge.
- **Space Complexity:** $O(1)$ auxiliary space because pointers navigate the original string directly without creating an intermediate filtered string.

**Algorithmic mechanics and edge cases:**
Filtering the string first with `[c.lower() for c in s if c.isalnum()]` allocates $O(n)$ auxiliary memory. The two-pointer in-place approach uses `s[left].isalnum()` to skip punctuation, spaces, and symbols on the fly. Edge cases include empty strings, strings containing only punctuation (e.g. `' '` or `'.,'`), and single characters.

## Why

Two converging pointers skipping non-alphanumeric characters achieve O(1) space without allocating filtered string buffers.

## Worked Case

For s='race a car': left compares 'r' to 'r' (idx 0 vs 9); left 'a' vs 'a' (idx 1 vs 7); left 'c' vs 'c' (idx 2 vs 5); left 'e' at idx 3 vs right 'a' at idx 4 -> mismatch, returns False.

## Risk

Creating a cleaned string copy doubles peak memory consumption on large input documents.

## Trade-off

In-place pointer skipping adds inner while loops with boundary checks left < right to prevent index out of bounds.

## Try This

Test with s='A man, a plan, a canal: Panama' and confirm that whitespace and punctuation are skipped seamlessly.

## Follow-ups

### How do you solve Valid Palindrome II where you may delete at most one character?

When a mismatch occurs at s[left] != s[right], test whether the remaining substring without s[left] or without s[right] is a valid palindrome.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you design an algorithm to encode and decode a list of strings safely?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Encode and Decode Strings (LeetCode 271) requires serializing a list of arbitrary strings into a single string and subsequently deserializing it back to the original list. The optimal approach prefixes each string with its length followed by a unique delimiter (e.g., `"<length>#<string>"`).

```python
class Codec:
    def encode(self, strs: list[str]) -> str:
        """Encodes a list of strings to a single string."""
        return "".join(f"{len(s)}#{s}" for s in strs)

    def decode(self, s: str) -> list[str]:
        """Decodes a single string to a list of strings."""
        res: list[str] = []
        i = 0
        while i < len(s):
            delimiter = s.find("#", i)
            length = int(s[i:delimiter])
            start = delimiter + 1
            res.append(s[start:start + length])
            i = start + length
        return res
```

**Complexity analysis:**
- **Time Complexity:** $O(N)$ for both encode and decode, where $N$ is the total number of characters across all strings in the list.
- **Space Complexity:** $O(N)$ to hold the serialized string and output list.

**Algorithmic mechanics and edge cases:**
Using fixed delimiters (like commas or colons) fails when strings contain those exact delimiters. Length-prefixing is immune to delimiter collisions because the parser reads the length integer first, jumps past the `#` separator, and slices exactly `length` bytes without inspecting internal content. Edge cases include empty lists `[]`, lists of empty strings `['', '']`, and strings containing `#` or numbers.

## Why

Length prefixing establishes framing boundaries immune to delimiter collisions or escape character parsing bugs.

## Worked Case

Encode ['lint', 'code'] -> '4#lint4#code'. Decode reads '4', finds '#', extracts next 4 chars ('lint'), updates pointer; reads '4', finds '#', extracts 'code'. Returns ['lint', 'code'].

## Risk

Using standard delimiters without length prefixing or escaping causes truncation or corruption when strings contain the delimiter.

## Trade-off

Length prefixes add a small integer header per string but guarantee stateless, unescapable serialization.

## Try This

Encode ['hello', '#world#', '12#45'] and trace how the decode loop reads 5#hello7##world#5#12#45 correctly.

## Follow-ups

### How is this length-prefixed framing pattern used in production network protocols?

Protocols like HTTP/2 (frame headers), gRPC, and Redis RESP use length-prefixed headers so network sockets know exact payload byte sizes in advance.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you evaluate an arithmetic expression string with addition, subtraction, multiplication, and division?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Basic Calculator II (LeetCode 227) evaluates non-negative integers separated by `+`, `-`, `*`, and `/` without parentheses. The optimal solution uses a stack (or running accumulator) to perform high-precedence multiplication and division immediately while deferring addition and subtraction.

```python
def calculate(s: str) -> int:
    stack: list[int] = []
    num = 0
    sign = '+'
    for i, char in enumerate(s):
        if char.isdigit():
            num = num * 10 + int(char)
        if (not char.isdigit() and char != ' ') or i == len(s) - 1:
            if sign == '+':
                stack.append(num)
            elif sign == '-':
                stack.append(-num)
            elif sign == '*':
                stack.append(stack.pop() * num)
            elif sign == '/':
                stack.append(int(stack.pop() / num))  # Truncate towards zero
            sign = char
            num = 0
    return sum(stack)
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `s`. Each character is scanned once, and stack operations run in $O(1)$ amortized time.
- **Space Complexity:** $O(n)$ auxiliary space to store intermediate summands on the stack (reducible to $O(1)$ with two running variables).

**Algorithmic mechanics and edge cases:**
When an operator or the end of the string is reached, the previous operator (`sign`) determines how the current number is incorporated. `+` and `-` push values onto the stack, while `*` and `/` pop the top value, evaluate the high-precedence term immediately, and push the product/quotient back. Edge cases include multi-digit numbers, spaces between digits and operators, and Python integer division truncation towards zero (`int(a / b)` vs `a // b`).

## Why

Stack deferral evaluates high-precedence multiplication and division immediately while accumulating addition and subtraction.

## Worked Case

For s=' 3/2 ': num parses 3, sign='+'; next operator is '/' -> stack=[3], sign='/'; num parses 2; end of string triggers '/': stack.pop() / 2 -> int(3/2)=1. stack=[1]. sum=1.

## Risk

Using Python floor division a // b on negative results produces incorrect floor values instead of truncation towards zero (-3 // 2 == -2 vs int(-3 / 2) == -1).

## Trade-off

Using a stack simplifies logic compared to a two-variable running sum/last_term approach that achieves O(1) space.

## Try This

Trace with s='3+2*2' to show that 2*2 is evaluated immediately to 4, leaving [3, 4] on the stack for sum=7.

## Follow-ups

### How do you extend this parser to handle parentheses as in Basic Calculator I and III?

When an opening parenthesis '(' is encountered, push the current running sum and sign onto the stack, reset them, and pop/apply when closing ')' is met.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the longest common prefix among an array of strings?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Longest Common Prefix (LeetCode 14) finds the longest string prefix shared across all strings in an array. The optimal solution uses vertical scanning, comparing characters column by column across all strings and terminating on the first mismatch or length boundary.

```python
def longest_common_prefix(strs: list[str]) -> str:
    if not strs:
        return ""
    for i in range(len(strs[0])):
        char = strs[0][i]
        for s in strs[1:]:
            if i == len(s) or s[i] != char:
                return strs[0][:i]
    return strs[0]
```

**Complexity analysis:**
- **Time Complexity:** $O(S)$ where $S$ is the sum of all characters across all strings. In the best case, it terminates after $O(n)$ comparisons if the first character mismatches.
- **Space Complexity:** $O(1)$ auxiliary space as it directly slices the original string reference without auxiliary allocations.

**Algorithmic mechanics and edge cases:**
Horizontal scanning compares string 1 and 2, then compares the result with string 3. Vertical scanning is superior in practice because if any string has a different character at index $i$, the algorithm exits immediately without inspecting the rest of the strings. Edge cases include empty input array `[]`, single string `['flower']`, strings with no common prefix `['dog', 'racecar']`, and empty strings inside the array `['', 'b']`.

## Why

Vertical scanning inspects characters column-by-column across strings, terminating early on the very first character mismatch.

## Worked Case

Input: ['flower', 'flow', 'flight']. i=0: 'f' matches all. i=1: 'l' matches all. i=2: strs[0][2]=='o' but strs[2][2]=='i' -> mismatch! Returns strs[0][:2] which is 'fl'.

## Risk

Horizontal scanning processes entire strings even when a tiny mismatch exists early on in later strings.

## Trade-off

Vertical scanning requires simple index boundary checks i == len(s) to avoid IndexError on shorter strings.

## Try This

Test with ['flower', 'flow', 'flight'] and verify that at column i=2 ('o' vs 'i'), it terminates and returns 'fl'.

## Follow-ups

### When would a Trie (Prefix Tree) be preferred for prefix queries?

When queries are repeated dynamically over a static dictionary of words, building a Trie allows prefix lookups in O(k) time per query.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you implement string to integer (atoi) conversion in Python?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** String to Integer (atoi) (LeetCode 8) parses a 32-bit signed integer from a string, handling leading whitespace, optional signs (`+` or `-`), non-digit termination, and overflow clamping between $[-2^{31}, 2^{31}-1]$.

```python
def my_atoi(s: str) -> int:
    s = s.lstrip()
    if not s:
        return 0
    sign = 1
    idx = 0
    if s[0] == '-':
        sign = -1
        idx = 1
    elif s[0] == '+':
        idx = 1
    res = 0
    INT_MAX = 2**31 - 1
    INT_MIN = -2**31
    while idx < len(s) and s[idx].isdigit():
        digit = int(s[idx])
        res = res * 10 + digit
        idx += 1
    res = sign * res
    if res < INT_MIN:
        return INT_MIN
    if res > INT_MAX:
        return INT_MAX
    return res
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `s`, scanning the string in a single linear pass.
- **Space Complexity:** $O(1)$ auxiliary memory since conversion uses numeric variables directly.

**Algorithmic mechanics and edge cases:**
The state machine sequence is: 1) discard leading whitespace; 2) inspect single optional sign; 3) accumulate contiguous digits until a non-digit character or end of string; 4) clamp to 32-bit integer limits. Edge cases include empty strings, strings with only signs (`"+"`), strings starting with letters (`"words and 987" -> 0`), and overflow values (`"-91283472332" -> -2147483648`).

## Why

A deterministic state machine parses sign and digits sequentially while enforcing 32-bit integer saturation arithmetic.

## Worked Case

For s='4193 with words': lstrip() retains '4193 with words'; no sign; digits accumulate 4 -> 41 -> 419 -> 4193; space at idx 4 stops loop; returns 4193.

## Risk

Relying on int() casting directly raises ValueError on inputs with trailing characters like '4193 with words'.

## Trade-off

Clamping after full accumulation relies on Python arbitrary-precision integers; in C/C++, overflow checks must precede multiplication.

## Try This

Test with s=' -042' and confirm that whitespace is stripped, negative sign preserved, and integer 42 returned as -42.

## Follow-ups

### How do you detect 32-bit overflow before multiplication in languages without arbitrary-precision integers?

Check if res > INT_MAX // 10 or (res == INT_MAX // 10 and digit > 7) before executing res = res * 10 + digit.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you multiply two numbers represented as strings without direct integer conversion?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Multiply Strings (LeetCode 43) computes the product of two non-negative integers represented as strings without using built-in big-integer libraries or direct `int()` conversion. The optimal solution implements grade-school column multiplication into an integer array of size $m + n$.

```python
def multiply(num1: str, num2: str) -> str:
    if num1 == "0" or num2 == "0":
        return "0"
    m, n = len(num1), len(num2)
    res = [0] * (m + n)
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            mul = int(num1[i]) * int(num2[j])
            p1, p2 = i + j, i + j + 1
            total = mul + res[p2]
            res[p2] = total % 10
            res[p1] += total // 10
    # Skip leading zeros
    start = 0
    while start < len(res) and res[start] == 0:
        start += 1
    return "".join(str(d) for d in res[start:])
```

**Complexity analysis:**
- **Time Complexity:** $O(m \cdot n)$ where $m$ and $n$ are the lengths of `num1` and `num2`, computing each pair of digits once.
- **Space Complexity:** $O(m + n)$ to store the result digits in the array before string construction.

**Algorithmic mechanics and edge cases:**
The product of digits at index `i` and `j` contributes to indices `i + j` (carry) and `i + j + 1` (units) in the result array. Accumulating values directly into array positions avoids complex carries between separate intermediate products. Edge cases include zero multiplication (`"0" * "1234" = "0"`), identical single digits (`"2" * "3" = "6"`), and large numbers producing leading zeros in the array.

## Why

Positioning digit products at i + j and i + j + 1 simulates grade-school arithmetic in fixed O(m + n) memory.

## Worked Case

num1='12', num2='3': i=1 (2) * j=0 (3) = 6 -> res[2]=6. i=0 (1) * j=0 (3) = 3 -> res[1]=3. Array=[0, 3, 6]. Stripping leading zero gives '36'.

## Risk

Casting strings directly to int exceeds maximum integer conversion limits and fails interview constraints.

## Trade-off

The O(m * n) array multiplication is simpler and has lower constant overhead than Karatsuba O(n^1.58) multiplication for typical lengths.

## Try This

Multiply '123' and '456' manually with the nested loop and verify that res array accumulates up to '56088'.

## Follow-ups

### What is the theoretical lower bound for large integer multiplication?

Harvey-Hoeven achieved O(n log n) multiplication using multi-dimensional Fast Fourier Transforms (FFT), improving upon Schönhage-Strassen.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you simplify a Unix-style canonical file path using a stack?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Simplify Path (LeetCode 71) resolves an absolute Unix file path containing redundant slashes (`//`), current directories (`.`), and parent directories (`..`). The optimal solution splits the path by `/`, iterates through tokens, and uses a stack to manage directory navigation.

```python
def simplify_path(path: str) -> str:
    stack: list[str] = []
    for part in path.split("/"):
        if part == "" or part == ".":
            continue
        elif part == "..":
            if stack:
                stack.pop()
        else:
            stack.append(part)
    return "/" + "/".join(stack)
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `path`, as splitting and scanning tokens take linear time.
- **Space Complexity:** $O(n)$ to store directory names in the stack and tokens list.

**Algorithmic mechanics and edge cases:**
Splitting by `/` automatically collapses multiple consecutive slashes into empty strings `""`. An empty string or `"."` indicates no movement; `".."` pops the most recent directory from the stack if non-empty; any valid directory name is pushed onto the stack. Edge cases include root directory `"/"`, paths navigating above root `"/../" -> "/"`, trailing slashes, and directories named `"..."` (which are treated as valid folder names).

## Why

A stack models hierarchical filesystem traversal where '..' represents popping the current directory level.

## Worked Case

For path='/home//foo/': split gives ['home', '', 'foo', '']. Ignore empty strings. Stack pushes 'home', then 'foo'. Result: '/' + '/'.join(['home', 'foo']) = '/home/foo'.

## Risk

Popping an empty stack when encountering '..' at root raises IndexError without defensive if stack: checks.

## Trade-off

Splitting by '/' creates an intermediate token list; a manual character parser uses O(1) extra space but increases code complexity.

## Try This

Test with '/a/./b/../../c/' to show that 'a' and 'b' are pushed and popped, leaving only 'c' to produce '/c'.

## Follow-ups

### Why is '...' treated as a directory name rather than a syntax error or special symbol?

In POSIX filesystems, only '.' (current) and '..' (parent) are reserved directory link tokens; any other string of dots is a valid filename.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find all starting indices of anagrams of string p in string s?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Find All Anagrams in a String (LeetCode 438) finds all start indices of `p`'s anagrams in `s`. The optimal solution uses a fixed-size sliding window of length $|p|$ with two character frequency arrays, updating character counts incrementally in $O(1)$ per step.

```python
def find_anagrams(s: str, p: str) -> list[int]:
    ns, np = len(s), len(p)
    if ns < np:
        return []
    p_counts = [0] * 26
    s_counts = [0] * 26
    for char in p:
        p_counts[ord(char) - ord('a')] += 1
    res: list[int] = []
    for i in range(ns):
        s_counts[ord(s[i]) - ord('a')] += 1
        if i >= np:
            s_counts[ord(s[i - np]) - ord('a')] -= 1
        if s_counts == p_counts:
            res.append(i - np + 1)
    return res
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n = |s|$. Fixed array comparisons `s_counts == p_counts` take $O(26) = O(1)$ constant time.
- **Space Complexity:** $O(1)$ auxiliary space as the frequency tables are fixed at size 26.

**Algorithmic mechanics and edge cases:**
At each step $i$, we add the new incoming character `s[i]` and remove the outgoing character `s[i - np]`. When `s_counts == p_counts`, the substring $s[i - np + 1 : i + 1]$ is a valid anagram of `p`. Edge cases include $|s| < |p|$ (returns `[]`), $|s| == |p|$, and strings with identical repeated characters.

## Why

A fixed-size sliding window adds the right character and drops the left character in O(1) time per step.

## Worked Case

p='abc' (counts: a=1, b=1, c=1). Window at i=2: s[:3]='cba' matches p_counts -> res=[0]. Window slides: at i=8, substring s[6:9]='bac' matches -> res=[0, 6].

## Risk

Recomputing collections.Counter for every substring of length np degrades total runtime to O(n * np).

## Trade-off

Comparing 26-element integer lists in Python is highly optimized in C and simpler than maintaining a match delta counter.

## Try This

Trace with s='cbaebabacd', p='abc' and verify that indices 0 ('cba') and 6 ('bac') are captured.

## Follow-ups

### How do you avoid the 26-element list comparison entirely?

Maintain a single integer variable matches tracking how many of the 26 character slots currently match between the window and target.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/collections.html

# How do you identify all repeated 10-letter nucleotide sequences in a DNA molecule?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Repeated DNA Sequences (LeetCode 187) identifies all 10-letter substrings that occur more than once in a DNA sequence composed of `'A'`, `'C'`, `'G'`, and `'T'`. The optimal solution uses a rolling hash or bitmask representation to store 10-letter k-mers in a hash set.

```python
def find_repeated_dna_sequences(s: str) -> list[str]:
    n = len(s)
    if n < 10:
        return []
    mapping = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
    bitmask = 0
    seen: set[int] = set()
    repeated: set[str] = set()
    for i in range(10):
        bitmask = (bitmask << 2) | mapping[s[i]]
    seen.add(bitmask)
    mask_20_bits = (1 << 20) - 1
    for i in range(10, n):
        bitmask = ((bitmask << 2) & mask_20_bits) | mapping[s[i]]
        if bitmask in seen:
            repeated.add(s[i - 9:i + 1])
        else:
            seen.add(bitmask)
    return list(repeated)
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `s`. Updating the 20-bit integer bitmask takes $O(1)$ bitwise operations per character.
- **Space Complexity:** $O(n)$ to store up to $n$ integer keys in the hash set.

**Algorithmic mechanics and edge cases:**
Because there are only 4 nucleotides, each nucleotide fits in 2 bits ($00, 01, 10, 11$). A 10-nucleotide sequence fits in exactly $10 \times 2 = 20$ bits, fitting into a standard integer. Rolling the window shifts left by 2 bits, masks to 20 bits, and bitwise-ORs the new nucleotide. Edge cases include sequences of length $< 10$, sequences with no repetitions, and strings where all nucleotides repeat identically.

## Why

Packing 10 nucleotides into a 20-bit integer reduces hash set lookup overhead from string hashing to integer hashing.

## Worked Case

s starts with 'AAAAACCCCC'. Mask encodes 5 zeros followed by 5 ones. When index 10-19 encounters 'AAAAACCCCC' again, its 20-bit mask is in seen, adding it to repeated.

## Risk

Storing raw 10-character string slices in a set allocates millions of tiny string objects, exhausting memory on genomic data.

## Trade-off

Bitmask rolling hash trades simple string slicing for bit manipulation arithmetic but cuts memory by a factor of 4x.

## Try This

Test with s='AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT' and verify 'AAAAACCCCC' and 'CCCCCAAAAA' are returned.

## Follow-ups

### How does this compare to the Rabin-Karp polynomial rolling hash?

Rabin-Karp uses modular arithmetic (hash = (hash * base + val) % mod) which can suffer hash collisions; 20-bit bitmasks have zero collisions.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you determine if a string can be segmented into dictionary words?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Word Break (LeetCode 139) determines whether string `s` can be partitioned into a space-separated sequence of one or more dictionary words from `wordDict`. The optimal solution uses 1D Dynamic Programming where `dp[i]` indicates whether prefix `s[:i]` can be segmented.

```python
def word_break(s: str, word_dict: list[str]) -> bool:
    words = set(word_dict)
    max_len = max(len(w) for w in words) if words else 0
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True  # Base case: empty string prefix
    for i in range(1, n + 1):
        for j in range(max(0, i - max_len), i):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break
    return dp[n]
```

**Complexity analysis:**
- **Time Complexity:** $O(n \cdot L)$ where $n = |s|$ and $L$ is the maximum length of any word in `word_dict`. Bounding the inner loop by `max_len` avoids checking invalid slice lengths.
- **Space Complexity:** $O(n)$ for the `dp` array plus $O(M)$ to store words in a hash set.

**Algorithmic mechanics and edge cases:**
`dp[i] = True` if there exists some split point `j < i` such that `dp[j] == True` and `s[j:i]` is in `words`. Pruning the inner search to `j >= i - max_len` reduces the quadratic $O(n^2)$ search to $O(n \cdot L)$. Edge cases include empty dictionary, single-character words, strings with no valid segmentation, and repeated single-word matches.

## Why

Dynamic programming memorizes prefix segmentations, preventing exponential re-computation on repeated subproblems.

## Worked Case

s='catsandog', dict=['cats', 'dog', 'sand', 'and', 'cat']. dp[3] ('cat')=True, dp[4] ('cats')=True, dp[7] ('catsand')=True. At i=9 ('catsandog'), s[7:9]='og' not in dict; returns False.

## Risk

Unmemoized backtracking search degenerates to O(2^n) exponential time on inputs like s='aaaa...b' with dict=['a', 'aa'].

## Trade-off

Limiting inner slice checks to max_len optimizes worst-case string slicing from O(n^2) to O(n * L).

## Try This

Trace with s='leetcode', word_dict=['leet', 'code']: dp[0]=True; at i=4, s[0:4]='leet' -> dp[4]=True; at i=8, s[4:8]='code' -> dp[8]=True.

## Follow-ups

### How do you solve Word Break II to return all possible segmented sentences?

Use DFS with memoization returning list of formed sentences for suffix s[i:], combining words with suffixes.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you calculate the minimum edit distance between two strings?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Edit Distance (LeetCode 72 / Levenshtein Distance) calculates the minimum number of insertions, deletions, or substitutions required to convert `word1` into `word2`. The optimal solution uses 2D Dynamic Programming where `dp[i][j]` represents the edit distance between prefixes `word1[:i]` and `word2[:j]`.

```python
def min_distance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    # dp[j] stores distance for current word1 prefix
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            temp = dp[j]
            if word1[i - 1] == word2[j - 1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev,       # replace
                                dp[j],       # delete
                                dp[j - 1])   # insert
            prev = temp
    return dp[n]
```

**Complexity analysis:**
- **Time Complexity:** $O(m \cdot n)$ where $m$ and $n$ are the lengths of `word1` and `word2`.
- **Space Complexity:** $O(\min(m, n))$ space by rolling the 2D matrix into a single 1D row array.

**Algorithmic mechanics and edge cases:**
If `word1[i-1] == word2[j-1]`, no operation is needed: `dp[i][j] = dp[i-1][j-1]`. Otherwise, we take $1 + \min$ of: substitution (`dp[i-1][j-1]`), deletion (`dp[i-1][j]`), or insertion (`dp[i][j-1]`). Edge cases include one or both strings being empty (returns length of the non-empty string) and identical strings (returns 0).

## Why

Dynamic programming systematically considers insertion, deletion, and replacement transitions across all prefixes.

## Worked Case

word1='intention', word2='execution'. dp computes transitions: remove 'i', replace 'n'->'e', replace 't'->'x', replace 'e'->'c', insert 'u' -> 5 total edits.

## Risk

Allocating full m x n matrices on large texts causes memory pressure; rolling arrays maintain O(n) space.

## Trade-off

Space compression reduces auxiliary memory to O(n) while requiring a temporary variable prev to preserve the top-left diagonal value.

## Try This

Compute distance between 'horse' and 'ros': replace 'h' with 'r', remove 'r', remove 'e' -> result 3.

## Follow-ups

### How do you reconstruct the actual sequence of edit operations rather than just the edit count?

Retain the full 2D DP matrix or parent pointer back-references, tracing backward from dp[m][n] to dp[0][0].

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you validate a string of parentheses containing wildcard asterisks?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Valid Parenthesis String (LeetCode 678) determines whether a string of `'('`, `')'`, and `'*'` is valid, where `'*'` can represent an open parenthesis, a close parenthesis, or an empty string. The optimal solution uses greedy range tracking of the minimum and maximum possible open parenthesis counts.

```python
def check_valid_string(s: str) -> bool:
    cmin, cmax = 0, 0
    for char in s:
        if char == '(':
            cmin += 1
            cmax += 1
        elif char == ')':
            cmin = max(0, cmin - 1)
            cmax -= 1
        elif char == '*':
            cmin = max(0, cmin - 1)  # treated as ')' or ''
            cmax += 1              # treated as '('
        if cmax < 0:
            return False
    return cmin == 0
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the length of `s`, scanning the string in a single linear pass.
- **Space Complexity:** $O(1)$ auxiliary space because it only maintains two integer bounds.

**Algorithmic mechanics and edge cases:**
`cmin` represents the minimum possible number of unclosed open parentheses, and `cmax` represents the maximum possible count. If `cmax < 0`, there are more closing parentheses than can ever be matched, returning `False`. At the end, `cmin == 0` guarantees all open parentheses can be closed. Edge cases include `"*"` (True), `"(*)"` (True), `")("` (False), and `"***"` (True).

## Why

Tracking the plausible range [cmin, cmax] of open parentheses captures all wildcard possibilities in O(1) space.

## Worked Case

Evaluation walkthrough: For s='(*)': initial count range is [0, 0]. First char '(' increases range to [1, 1]. Wildcard char expands range: minimum decreases to 0 and maximum increases to 2, yielding [0, 2]. Final char ')' decreases range to [0, 1]. Range ends with minimum 0, confirming valid balance.

## Risk

Allowing cmin to become negative invalidates the lower bound; it must be clamped to 0 since surplus '(' can be nullified by '*'.

## Trade-off

Greedy range tracking achieves O(1) space compared to two stacks or 2D DP memoization requiring O(n) memory.

## Try This

Test with '(*))': i=0 '(' -> [1,1]; i=1 '*' -> [0,2]; i=2 ')' -> [0,1]; i=3 ')' -> [0,0] -> cmin==0, returns True.

## Follow-ups

### Can this be solved with two stacks, and what do they store?

Yes, one stack for '(' indices and one stack for '*' indices, matching remaining '(' with '*' whose index is greater.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you rearrange a string so that no two adjacent characters are identical?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Reorganize String (LeetCode 767) rearranges characters of string `s` so that no adjacent characters are identical. The optimal solution counts character frequencies, verifies that the maximum frequency does not exceed $(n + 1) // 2$, and alternates placement using a max-heap or parity indexing.

```python
import heapq
from collections import Counter

def reorganize_string(s: str) -> str:
    counts = Counter(s)
    n = len(s)
    max_freq = max(counts.values())
    if max_freq > (n + 1) // 2:
        return ""
    # Max-heap storing (-freq, char)
    heap = [(-freq, char) for char, freq in counts.items()]
    heapq.heapify(heap)
    res: list[str] = []
    prev_freq, prev_char = 0, ''
    while heap:
        freq, char = heapq.heappop(heap)
        res.append(char)
        if prev_freq < 0:
            heapq.heappush(heap, (prev_freq, prev_char))
        prev_freq, prev_char = freq + 1, char
    return "".join(res)
```

**Complexity analysis:**
- **Time Complexity:** $O(n \log k)$ where $n = |s|$ and $k \le 26$ is the number of distinct characters, which simplifies to $O(n)$.
- **Space Complexity:** $O(k) = O(1)$ auxiliary space for the heap.

**Algorithmic mechanics and edge cases:**
By always popping the most frequent available character and holding the previously used character until the next turn, we guarantee adjacent letters never match. The pigeonhole principle dictates that if any character's frequency exceeds $(n + 1) // 2$, collisions are mathematically unavoidable (returns `""`). Edge cases include single-character strings, strings with already unique characters, and impossible inputs like `'aaab'`.

## Why

A max-heap greedily places the most frequent available character while holding the previous character in reserve.

## Worked Case

s='vvvlo'. Counts: v=3, l=1, o=1. n=5. max_freq=3 <= (5+1)//2=3 (possible). Heap pops 'v', holds 'v'. Pops 'l', pushes 'v'. Pops 'v', holds 'v'. Pops 'o', pushes 'v'. Pops 'v'. Result: 'vlvov'.

## Risk

Failing to check max_freq > (n + 1) // 2 before processing leads to deadlocks or invalid consecutive placements.

## Trade-off

Heap simulation is easy to reason about; alternatively, placing characters in even indices then odd indices achieves O(n) without heap operations.

## Try This

Test with s='aab' and observe that 'a' is placed, held, 'b' is placed, and remaining 'a' placed to form 'aba'.

## Follow-ups

### How do you generalize this when identical characters must be separated by at least distance d?

Use a queue to hold popped characters for d cooling turns before returning them to the max-heap (like Rearrange String k Distance Apart).

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/heapq.html

# How do you find the longest substring with at most k distinct characters?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Longest Substring with At Most K Distinct Characters (LeetCode 340) finds the maximum length of a substring containing at most `k` distinct characters. The optimal solution uses a sliding window bounded by `left` and `right` pointers with a hash table tracking character frequencies.

```python
def length_of_longest_substring_k_distinct(s: str, k: int) -> int:
    if k == 0 or not s:
        return 0
    counts: dict[str, int] = {}
    max_len = 0
    left = 0
    for right, char in enumerate(s):
        counts[char] = counts.get(char, 0) + 1
        while len(counts) > k:
            left_char = s[left]
            counts[left_char] -= 1
            if counts[left_char] == 0:
                del counts[left_char]
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n = |s|$. Both `left` and `right` pointers advance monotonically from $0$ to $n-1$.
- **Space Complexity:** $O(k)$ auxiliary space because the dictionary stores at most $k + 1$ character keys at any time.

**Algorithmic mechanics and edge cases:**
As the `right` pointer advances, each new character is recorded in `counts`. When `len(counts) > k`, the `left` pointer contracts the window until a character's frequency drops to 0 and is deleted from `counts`. Edge cases include $k = 0$, $k \ge \text{len}(s)$ (returns $\text{len}(s)$), and strings with fewer than $k$ distinct characters.

## Why

A sliding window maintaining a frequency map of size at most k guarantees strict linear runtime.

## Worked Case

For s='eceba', k=2: right expands 'e', 'c', 'e' (len 3, dict={'e':2, 'c':1}). On 'b', dict has 3 keys; left contracts past 'e', 'c' until 'c' count drops to 0 and deleted; window is 'eb'. max_len remains 3.

## Risk

Failing to delete key when frequency drops to 0 keeps len(counts) artificially high and contracts the window prematurely.

## Trade-off

Using a standard dict takes O(k) space; an OrderedDict or map storing the last-seen index can jump left in O(1) operations.

## Try This

Trace with s='eceba' and k=2: show that window 'ece' has length 3 and contracts when 'b' enters.

## Follow-ups

### How can you optimize this using an OrderedDict storing last-seen indices?

Store each char's rightmost index; when size exceeds k, pop the oldest item from OrderedDict and jump left directly past its index.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/collections.html

# How do you invert a binary tree recursively and iteratively?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Invert Binary Tree (LeetCode 226) swaps the left and right child subtrees for every node in a binary tree. The optimal recursive solution visits each node in post-order or pre-order, swaps its children, and recursively inverts both branches.

```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def invert_tree(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if not root:
        return None
    root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    return root
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of nodes in the tree. Each node is visited exactly once.
- **Space Complexity:** $O(h)$ where $h$ is the height of the tree, representing the recursion call stack ($O(\log n)$ for balanced trees, $O(n)$ worst-case for degenerate linked lists).

**Algorithmic mechanics and edge cases:**
At every node, swapping `root.left` and `root.right` inverts the current level. Python's tuple unpacking `root.left, root.right = invert_tree(root.right), invert_tree(root.left)` evaluates both recursive calls before assignment, avoiding intermediate variables. Alternatively, a queue-based Breadth-First Search (BFS) inverts the tree level-by-level without recursion stack limits. Edge cases include empty tree (`root = None`), single-node trees, and asymmetric trees.

## Why

Swapping child pointers at every level mirrors the tree structure across its vertical axis in linear time.

## Worked Case

root=[2, 1, 3]. root.left (1) and root.right (3) swap -> root.left becomes 3, root.right becomes 1. Leaves have no children. Returns root=[2, 3, 1].

## Risk

Deeply unbalanced linear trees with 10,000 nodes cause Python RecursionError unless sys.setrecursionlimit is raised or BFS is used.

## Trade-off

Recursive post-order traversal is extremely concise; BFS queue traversal requires O(w) memory where w is maximum tree width.

## Try This

Trace root=[4, 2, 7, 1, 3, 6, 9]: left child 2 and right child 7 swap, and their descendants mirror to yield [4, 7, 2, 9, 6, 3, 1].

## Follow-ups

### How do you invert the tree iteratively using a queue (BFS)?

Use collections.deque; pop node, swap node.left and node.right, and push non-null children into the queue until empty.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the maximum depth (height) of a binary tree?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Maximum Depth of Binary Tree (LeetCode 104) finds the number of nodes along the longest path from the root down to the farthest leaf node. The optimal solution uses Depth-First Search (DFS) post-order recursion: the height of any node is $1 + \max(\text{height}(\text{left}), \text{height}(\text{right}))$.

```python
from typing import Optional

def max_depth(root: Optional[TreeNode]) -> int:
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of nodes, visiting each node once.
- **Space Complexity:** $O(h)$ where $h$ is tree height, matching recursion call stack depth ($O(\log n)$ balanced, $O(n)$ skewed).

**Algorithmic mechanics and edge cases:**
The base case returns 0 when reaching an empty subtree (`None`). Each parent node aggregates the maximum depths of its two subtrees and adds 1 for itself. Alternatively, level-order BFS traversal counts the total number of level iterations before the queue empties. Edge cases include empty tree (`root = None`, depth 0), single-node tree (depth 1), and completely skewed linked-list trees.

## Why

Post-order tree traversal aggregates subtree heights bottom-up in a single pass without extra state.

## Worked Case

root=[1, null, 2]. Left is None (0). Right is node 2, which has left None (0) and right None (0) -> depth 1. Root returns 1 + max(0, 1) = 2.

## Risk

Assuming balanced tree depth O(log n); degenerate trees degrade space complexity to O(n) call stack frames.

## Trade-off

DFS recursion is one line of code; BFS queue iteration requires O(w) heap memory but avoids stack overflow.

## Try This

Trace root=[3, 9, 20, null, null, 15, 7]: left branch has depth 2 (3->9); right branch has depth 3 (3->20->15); max is 3.

## Follow-ups

### How do you find the minimum depth to a leaf node (Minimum Depth of Binary Tree)?

If a node has only one child, you cannot take min(0, child_depth); you must return the depth of the non-empty child branch.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you determine if two binary trees are identical in structure and node values?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Same Tree (LeetCode 100) checks if two binary trees are structurally identical and have identical node values. The optimal solution uses simultaneous recursive traversal, asserting that both current nodes are null or both have identical values, followed by recursive left and right checks.

```python
from typing import Optional

def is_same_tree(p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
    if not p and not q:
        return True
    if not p or not q or p.val != q.val:
        return False
    return is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the minimum number of nodes between the two trees. Traversal terminates early on the first discrepancy.
- **Space Complexity:** $O(h)$ where $h$ is the height of the trees, representing recursion stack depth.

**Algorithmic mechanics and edge cases:**
The three base cases are: 1) both nodes are `None` (returns `True`); 2) one node is `None` while the other is not (structural mismatch, returns `False`); 3) node values differ (value mismatch, returns `False`). If all pass, both subtrees are verified recursively. Edge cases include two empty trees (True), one empty tree and one non-empty tree (False), and trees with identical values but mirrored structures.

## Why

Simultaneous tree traversal compares structure and node values lockstep with immediate short-circuiting on mismatch.

## Worked Case

p=[1,2,3], q=[1,2,3]. Roots match (1==1). Left nodes match (2==2), their children are None -> True. Right nodes match (3==3) -> True. Returns True.

## Risk

Comparing p.val == q.val without first verifying that neither node is None triggers an AttributeError: 'NoneType' object has no attribute 'val'.

## Trade-off

Lockstep DFS recursion short-circuits on the first mismatch, minimizing unnecessary subtree visits.

## Try This

Test with p=[1, 2] and q=[1, null, 2]: structural check at p.left (node 2) vs q.left (None) returns False immediately.

## Follow-ups

### How do you check if a single tree is symmetric around its vertical center (Symmetric Tree)?

Run is_mirror(t1.left, t2.right) and is_mirror(t1.right, t2.left) comparing mirrored child pairs.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you determine if a binary tree contains another binary tree as a subtree?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Subtree of Another Tree (LeetCode 572) checks if tree `root` contains a subtree identical in structure and node values to tree `subRoot`. The optimal solution uses Depth-First Search: at each node in `root`, check if `is_same_tree(root, subRoot)` is true, or recursively check left and right subtrees.

```python
from typing import Optional

def is_subtree(root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:
    if not subRoot:
        return True  # An empty tree is always a subtree
    if not root:
        return False # Non-empty subRoot cannot be in an empty root
    if is_same_tree(root, subRoot):
        return True
    return is_subtree(root.left, subRoot) or is_subtree(root.right, subRoot)

def is_same_tree(s: Optional[TreeNode], t: Optional[TreeNode]) -> bool:
    if not s and not t:
        return True
    if not s or not t or s.val != t.val:
        return False
    return is_same_tree(s.left, t.left) and is_same_tree(s.right, t.right)
```

**Complexity analysis:**
- **Time Complexity:** $O(|root| \cdot |subRoot|)$ in the worst case where many nodes share identical values with `subRoot`.
- **Space Complexity:** $O(h)$ where $h$ is the maximum tree height, corresponding to recursion stack frames.

**Algorithmic mechanics and edge cases:**
A subtree must match identically all the way down to the leaf nodes; matching an intermediate subset of nodes is not sufficient. `is_subtree` traverses every candidate node in `root`, calling `is_same_tree` whenever the node value matches `subRoot.val`. Edge cases include `subRoot` being identical to `root`, `subRoot` having identical values but extra child nodes, and duplicate node values across the parent tree.

## Why

Traversing candidate roots and verifying complete subtree equality guarantees exact topological matching.

## Worked Case

root=[3,4,5,1,2], subRoot=[4,1,2]. root(3) != subRoot(4). Recurse left to root(4): is_same_tree(node 4, subRoot) returns True. Final result is True.

## Risk

Assuming value match at root is sufficient; a valid subtree must match all descendant child pointers down to null leaves.

## Trade-off

Naive recursive search takes O(N * M); tree serialization with KMP string matching or Merkle hashing achieves O(N + M) linear time.

## Try This

Test with root=[3,4,5,1,2,null,null,null,null,0] and subRoot=[4,1,2]: note that node 2 has an extra child 0 in root, so returns False.

## Follow-ups

### How do you achieve strictly linear O(|root| + |subRoot|) runtime for subtree matching?

Serialize both trees using preorder traversal with explicit null delimiters (e.g. '^4,1,#,#,2,#,#'$) and run KMP pattern matching.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the Lowest Common Ancestor (LCA) in a Binary Search Tree?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Lowest Common Ancestor of a BST (LeetCode 235) finds the lowest node in a BST that has both nodes `p` and `q` as descendants. The optimal solution exploits the BST ordering property: if both values are smaller than the current node, search left; if both are larger, search right; the split point is the LCA.

```python
from typing import Optional

def lowest_common_ancestor_bst(root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
    curr = root
    while curr:
        if p.val < curr.val and q.val < curr.val:
            curr = curr.left
        elif p.val > curr.val and q.val > curr.val:
            curr = curr.right
        else:
            # Split point: either p and q lie on opposite sides, or curr is p or q
            return curr
    return root
```

**Complexity analysis:**
- **Time Complexity:** $O(h)$ where $h$ is the height of the BST ($O(\log n)$ for balanced trees, $O(n)$ for skewed trees). At most one path from root to leaf is traversed.
- **Space Complexity:** $O(1)$ auxiliary space because the search executes iteratively without recursion stack frames.

**Algorithmic mechanics and edge cases:**
In a BST, all values in the left subtree are $< \text{root.val}$, and all values in the right subtree are $> \text{root.val}$. If both `p.val` and `q.val` are strictly less than `curr.val`, the LCA must lie in the left subtree. If both are strictly greater, the LCA must lie in the right subtree. The moment `p.val` and `q.val` diverge (one is $\le \text{curr.val}$ and one is $\ge \text{curr.val}$), `curr` is the lowest common ancestor. Edge cases include `p` being the direct ancestor of `q`, or `p` and `q` lying in opposite subtrees.

## Why

The BST ordering property guarantees that the first node where p and q diverge in search direction is their unique LCA.

## Worked Case

root=[6, 2, 8, 0, 4, 7, 9], p=2, q=4. At root 6: both 2,4 < 6 -> curr moves to 2. At node 2: p.val == 2 (diverges/matches) -> returns node 2.

## Risk

Using general binary tree LCA post-order traversal on a BST wastes the sorted ordering invariant and takes O(n) instead of O(h).

## Trade-off

Iterative BST search uses O(1) space and avoids recursion call stack overhead.

## Try This

Trace root=[6, 2, 8, 0, 4, 7, 9] with p=2, q=8: 2 < 6 and 8 > 6 -> split point is root 6.

## Follow-ups

### How does this change if the tree is an arbitrary Binary Tree without the BST ordering property?

Use post-order DFS checking if left or right subtrees return non-null nodes; when both return non-null, the current root is the LCA.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the Lowest Common Ancestor (LCA) in an arbitrary Binary Tree?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Lowest Common Ancestor of a Binary Tree (LeetCode 236) finds the lowest node in a general binary tree that has both `p` and `q` as descendants. The optimal solution uses post-order DFS: recurse on both subtrees, returning `root` if the current node is `p` or `q`, or if `p` and `q` are found in different subtrees.

```python
from typing import Optional

def lowest_common_ancestor(root: Optional[TreeNode], p: TreeNode, q: TreeNode) -> Optional[TreeNode]:
    if not root or root == p or root == q:
        return root
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    if left and right:
        return root  # p and q found in separate subtrees; root is the LCA
    return left if left else right  # Return the non-null result (propagates LCA up)
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of nodes in the binary tree, visiting every node in the worst case.
- **Space Complexity:** $O(h)$ where $h$ is tree height, matching recursion call stack depth.

**Algorithmic mechanics and edge cases:**
If `root` is `p` or `q`, we return `root` immediately. Otherwise, we search the left and right subtrees. If both `left` and `right` return non-null values, it means `p` was found in one subtree and `q` in the other; therefore, `root` is their lowest common ancestor. If only one side returns non-null, both nodes lie in that subtree, so we propagate that result up. Edge cases include `p` being the parent of `q` (returns `p`), nodes in opposite subtrees, and degenerate linear trees.

## Why

Post-order bottom-up traversal identifies the unique junction node where search results from left and right meet.

## Worked Case

root=[3, 5, 1, 6, 2, 0, 8], p=5, q=4 (child of 5). When root reaches 5, root == p returns 5 immediately without exploring its subtrees. 5 propagates to top as LCA.

## Risk

Assuming p and q have distinct values; if duplicate values exist in the tree, pointer reference equality root == p must be used.

## Trade-off

Bottom-up DFS eliminates the need to build and store explicit root-to-node path arrays for p and q.

## Try This

Trace root=[3, 5, 1, 6, 2, 0, 8] with p=5, q=1: left returns 5, right returns 1; since both are non-null, returns root 3.

## Follow-ups

### How do you solve LCA if nodes have parent pointers (node.parent)?

Store all ancestors of p in a hash set, then traverse up from q until finding the first ancestor present in the set.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you traverse a binary tree level by level using Breadth-First Search (BFS)?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Binary Tree Level Order Traversal (LeetCode 102) returns the level-order traversal of its nodes' values (i.e. from left to right, level by level). The optimal solution uses a queue (`collections.deque`), processing nodes in batches corresponding to the number of elements present at the start of each level.

```python
from collections import deque
from typing import Optional

def level_order(root: Optional[TreeNode]) -> list[list[int]]:
    if not root:
        return []
    res: list[list[int]] = []
    queue: deque[TreeNode] = deque([root])
    while queue:
        level_size = len(queue)
        level_vals: list[int] = []
        for _ in range(level_size):
            node = queue.popleft()
            level_vals.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        res.append(level_vals)
    return res
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of nodes in the tree. Each node is enqueued and dequeued exactly once.
- **Space Complexity:** $O(w)$ where $w$ is the maximum width of the tree ($O(n / 2) = O(n)$ in a complete binary tree), storing one level in the queue.

**Algorithmic mechanics and edge cases:**
Taking `level_size = len(queue)` at the start of the while loop snapshots the exact number of nodes belonging to the current depth level. Inner loop iterations pop only those `level_size` nodes, while their child nodes are appended to the back of the queue to be processed in the subsequent level iteration. Edge cases include empty tree (`root = None`, returns `[]`), single-node tree `[[1]]`, and skewed trees.

## Why

Snap-shotting len(queue) isolates level boundaries, enabling 2D level grouping in a single queue.

## Worked Case

root=[1]. queue=[1]. level_size=1. node 1 popped, no children. res=[[1]]. queue empty. Loop terminates. Result: [[1]].

## Risk

Popping from a standard Python list with pop(0) takes O(n) per pop, degrading total traversal to O(n^2); collections.deque popleft() is O(1).

## Trade-off

Queue batching groups nodes by level without needing to store depth integers alongside each node.

## Try This

Trace root=[3, 9, 20, null, null, 15, 7]: Level 1 -> [3]; Level 2 -> [9, 20]; Level 3 -> [15, 7].

## Follow-ups

### How do you implement Zigzag Level Order Traversal (LeetCode 103)?

Add a boolean flag left_to_right toggled each level; if false, reverse level_vals before appending to res.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/collections.html

# How do you validate whether a binary tree is a valid Binary Search Tree (BST)?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Validate Binary Search Tree (LeetCode 98) determines if a binary tree is a valid BST. A valid BST requires that all nodes in the left subtree have values strictly less than the node's value, and all nodes in the right subtree have values strictly greater than the node's value. The optimal solution uses DFS range propagation, passing valid open intervals `(min_val, max_val)` down the tree.

```python
from typing import Optional

def is_valid_bst(root: Optional[TreeNode]) -> bool:
    def validate(node: Optional[TreeNode], min_val: float, max_val: float) -> bool:
        if not node:
            return True
        if not (min_val < node.val < max_val):
            return False
        return (validate(node.left, min_val, node.val) and
                validate(node.right, node.val, max_val))
    return validate(root, float("-inf"), float("inf"))
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of nodes in the tree, visiting each node once.
- **Space Complexity:** $O(h)$ where $h$ is tree height, representing recursion call stack depth.

**Algorithmic mechanics and edge cases:**
Checking only that `node.left.val < node.val < node.right.val` locally is incorrect, because it fails to catch violations where a node deep in the left subtree is greater than an ancestor. Range propagation enforces global bounds: branching left tightens `max_val` to `node.val`, while branching right tightens `min_val` to `node.val`. Alternatively, an in-order traversal of a valid BST must yield strictly ascending values. Edge cases include duplicate node values (invalid in strict BSTs), values equal to `INT_MIN` or `INT_MAX`, and single-node trees.

## Why

Propagating open boundary intervals (min_val, max_val) down subtrees validates ancestor constraints globally.

## Worked Case

root=[2, 1, 3]. validate(2, -inf, inf): True. validate(1, -inf, 2): True. validate(3, 2, inf): True. All return True -> valid BST.

## Risk

Comparing only immediate child nodes node.left < node < node.right accepts invalid trees like [5, 1, 6, null, null, 3, 7] (where 3 is in right subtree of 5).

## Trade-off

Range propagation validates bounds in a single DFS pass; in-order traversal achieves identical O(n) time by comparing with prev_val.

## Try This

Test root=[5, 1, 4, null, null, 3, 6]: at node 4, condition min_val (5) < 4 < max_val (inf) fails (4 is not > 5), returning False.

## Follow-ups

### How do you validate a BST using iterative in-order traversal?

Use a stack to traverse in-order; assert that each popped node's value is strictly greater than prev_val, then update prev_val = node.val.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the kth smallest element in a Binary Search Tree?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Kth Smallest Element in a BST (LeetCode 230) finds the $k$-th smallest value (1-indexed) in a BST. The optimal solution uses an iterative in-order traversal with a stack, terminating as soon as the $k$-th element is popped without traversing the remainder of the tree.

```python
from typing import Optional

def kth_smallest(root: Optional[TreeNode], k: int) -> int:
    stack: list[TreeNode] = []
    curr = root
    while curr or stack:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        k -= 1
        if k == 0:
            return curr.val
        curr = curr.right
    return -1
```

**Complexity analysis:**
- **Time Complexity:** $O(h + k)$ where $h$ is tree height and $k$ is the target index. It traverses down to the leftmost leaf in $O(h)$ and pops $k$ elements.
- **Space Complexity:** $O(h)$ auxiliary space to store at most $h$ ancestors in the stack.

**Algorithmic mechanics and edge cases:**
An in-order traversal (`Left -> Node -> Right`) of a Binary Search Tree visits node values in strictly sorted ascending order. By using an explicit stack rather than full recursion or array generation, the traversal halts immediately when `k == 0`, avoiding unnecessary traversal of the remaining $n - k$ nodes. Edge cases include $k = 1$ (the leftmost leaf), $k = n$ (the rightmost node), and single-node trees.

## Why

In-order traversal visits BST nodes in sorted ascending order; early termination at step k achieves O(h + k) runtime.

## Worked Case

root=[5,3,6,2,4,null,null,1], k=3. Stack goes left: 5, 3, 2, 1. Pop 1 (k=2). Pop 2 (k=1). Node 2 has no right. Pop 3 (k=0) -> returns 3.

## Risk

Extracting full in-order traversal into an array takes O(n) memory and time, wasting work when k is small.

## Trade-off

Iterative stack traversal stops early at step k with O(h) memory, while full recursion traverses all nodes.

## Try This

Trace root=[3, 1, 4, null, 2], k=1: stack pushes 3, 1; pops 1; k becomes 0, returns 1 immediately.

## Follow-ups

### How do you optimize this if the BST is modified frequently and kth smallest queries are repeated often?

Augment each TreeNode with a count of nodes in its left subtree, enabling O(h) binary search lookups like an Order Statistic Tree.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you construct a binary tree from preorder and inorder traversal arrays?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Construct Binary Tree from Preorder and Inorder Traversal (LeetCode 105) reconstructs the unique binary tree given its preorder and inorder traversal sequences. The optimal solution uses a hash map storing the indices of values in the inorder array, recursively partitioning subtrees in $O(n)$ time.

```python
from typing import Optional

def build_tree(preorder: list[int], inorder: list[int]) -> Optional[TreeNode]:
    inorder_map = {val: idx for idx, val in enumerate(inorder)}
    pre_idx = 0
    def helper(left: int, right: int) -> Optional[TreeNode]:
        nonlocal pre_idx
        if left > right:
            return None
        root_val = preorder[pre_idx]
        pre_idx += 1
        root = TreeNode(root_val)
        mid = inorder_map[root_val]
        root.left = helper(left, mid - 1)
        root.right = helper(mid + 1, right)
        return root
    return helper(0, len(inorder) - 1)
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of nodes. Building the index hash map takes $O(n)$, and each tree node is created in $O(1)$ time.
- **Space Complexity:** $O(n)$ space for the `inorder_map` plus $O(h)$ for the recursion call stack.

**Algorithmic mechanics and edge cases:**
In preorder traversal, the first element is always the root of the current subtree. Finding that root value in the inorder traversal splits the inorder array into the left subtree (`left` to `mid - 1`) and the right subtree (`mid + 1` to `right`). Using a hash map achieves $O(1)$ root index lookups. Recursing on `root.left` before `root.right` mirrors the preorder traversal order. Edge cases include single-node trees, left-skewed trees, and right-skewed trees.

## Why

Preorder identifies root values sequentially, while an inorder hash map partitions left and right subtrees in O(1) time.

## Worked Case

preorder=[-1], inorder=[-1]. Map={-1:0}. pre_idx=0 -> root=-1, mid=0. left=0, right=0. left child: helper(0, -1) -> None. right child: helper(1, 0) -> None. Returns TreeNode(-1).

## Risk

Using inorder.index(root_val) or list slicing inside recursion adds O(n) per call, degrading total construction time to O(n^2).

## Trade-off

Precomputing the inorder hash map consumes O(n) auxiliary space to achieve strict linear O(n) runtime.

## Try This

Trace preorder=[3, 9, 20, 15, 7], inorder=[9, 3, 15, 20, 7]: root=3; inorder splits [9] (left) and [15, 20, 7] (right).

## Follow-ups

### Can a binary tree be uniquely reconstructed from preorder and postorder traversals alone?

No, unless every non-leaf node has exactly two children (Full Binary Tree); otherwise, single-child branch direction is ambiguous.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you find the maximum path sum in a binary tree across any sequence of nodes?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Binary Tree Maximum Path Sum (LeetCode 124) finds the maximum path sum in a non-empty binary tree along any path connecting any two nodes (not necessarily passing through the root). The optimal solution uses post-order DFS: each node computes the maximum path sum passing *through* itself, while returning its maximum single-branch contribution to its parent.

```python
from typing import Optional

def max_path_sum(root: Optional[TreeNode]) -> int:
    max_sum = float("-inf")
    def max_gain(node: Optional[TreeNode]) -> int:
        nonlocal max_sum
        if not node:
            return 0
        # Max gain from left and right subtrees (ignore negative gains)
        left_gain = max(max_gain(node.left), 0)
        right_gain = max(max_gain(node.right), 0)
        # Price of current path with node as highest turn-point
        current_path_sum = node.val + left_gain + right_gain
        max_sum = max(max_sum, current_path_sum)
        # Return max single-branch gain to parent
        return node.val + max(left_gain, right_gain)
    max_gain(root)
    return int(max_sum)
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ where $n$ is the number of nodes in the tree, visiting each node once.
- **Space Complexity:** $O(h)$ where $h$ is tree height, representing recursion call stack depth.

**Algorithmic mechanics and edge cases:**
A valid path cannot split: it can pass through a node and go down both subtrees, but it can only extend upward to its parent through *one* subtree branch. Therefore, `max_gain` returns `node.val + max(left_gain, right_gain)` to its parent. If a child's gain is negative, `max(gain, 0)` clamps it to 0 (ignoring that branch). Edge cases include trees where all node values are negative (e.g. `[-3]`), single-node trees, and zigzag paths.

## Why

Post-order DFS calculates the inverted-V path sum at each node while propagating only the best linear branch to ancestors.

## Worked Case

root=[1, 2, 3]. node 2 returns 2 (left=0, right=0). node 3 returns 3. node 1 evaluates path 1 + 2 + 3 = 6. max_sum=6. Returns 6.

## Risk

Initializing max_sum to 0 fails on trees where all node values are negative; it must be initialized to float('-inf').

## Trade-off

Bottom-up dynamic programming on trees calculates both local turning paths and linear branch gains in a single linear pass.

## Try This

Trace root=[-10, 9, 20, null, null, 15, 7]: at node 20, path sum is 20 + 15 + 7 = 42; max_sum records 42.

## Follow-ups

### How do you return the actual list of nodes forming the maximum path?

Store the best left and right child references whenever max_sum updates, and reconstruct the path from the apex node down both branches.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you design an algorithm to serialize and deserialize a binary tree?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Serialize and Deserialize Binary Tree (LeetCode 297) converts a binary tree into a string and deserializes that string back to the original tree structure. The optimal solution uses preorder DFS traversal with comma delimiters and a designated null symbol (e.g., `'#'`).

```python
from typing import Optional

class Codec:
    def serialize(self, root: Optional[TreeNode]) -> str:
        """Encodes a tree to a single string."""
        vals: list[str] = []
        def dfs(node: Optional[TreeNode]) -> None:
            if not node:
                vals.append("#")
                return
            vals.append(str(node.val))
            dfs(node.left)
            dfs(node.right)
        dfs(root)
        return ",".join(vals)

    def deserialize(self, data: str) -> Optional[TreeNode]:
        """Decodes encoded data to tree."""
        tokens = iter(data.split(","))
        def dfs() -> Optional[TreeNode]:
            val = next(tokens)
            if val == "#":
                return None
            node = TreeNode(int(val))
            node.left = dfs()
            node.right = dfs()
            return node
        return dfs()
```

**Complexity analysis:**
- **Time Complexity:** $O(n)$ for both serialization and deserialization, visiting each node and null leaf once.
- **Space Complexity:** $O(n)$ to store the serialized string buffer and recursion call stacks.

**Algorithmic mechanics and edge cases:**
Preorder traversal outputs `Root -> Left -> Right`. Because null pointers are explicitly recorded as `'#'`, the tree structure is uniquely preserved without needing a secondary inorder array. During deserialization, using a Python iterator `iter(tokens)` allows `next(tokens)` to consume tokens sequentially in $O(1)$ time. Edge cases include empty tree (`root = None -> "#"`), single-node trees, and trees with negative numbers.

## Why

Recording explicit null delimiters preserves tree topology, allowing preorder traversal to uniquely reconstruct the tree.

## Worked Case

root=None. serialize outputs '#'. deserialize splits ['#'], next() is '#' -> returns None. Round-trip verified.

## Risk

Using split(',') and list.pop(0) during deserialization causes an O(n^2) bottleneck; iter(tokens) ensures linear O(n) decoding.

## Trade-off

Preorder DFS with null delimiters produces a larger string than BFS binary packing, but code is compact and human-readable.

## Try This

Serialize root=[1, 2, 3, null, null, 4, 5]: outputs '1,2,#,#,3,4,#,#,5,#,#'; deserialize reconstructs identical tree.

## Follow-ups

### How do you serialize the tree using level-order BFS traversal?

Enqueue nodes; pop and record value or '#' for nulls, appending comma-separated strings; during decoding, use a queue to link left/right children.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you clone an undirected connected graph with cycles?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Clone Graph (LeetCode 133) creates a deep copy of a connected undirected graph where each node contains a value and a list of neighbors. The optimal solution uses DFS (or BFS) with a hash map mapping each original node to its newly instantiated clone, handling cycles seamlessly.

```python
from typing import Optional

class Node:
    def __init__(self, val = 0, neighbors = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

def clone_graph(node: Optional['Node']) -> Optional['Node']:
    if not node:
        return None
    visited: dict['Node', 'Node'] = {}
    def dfs(curr: 'Node') -> 'Node':
        if curr in visited:
            return visited[curr]
        copy = Node(curr.val)
        visited[curr] = copy
        for neighbor in curr.neighbors:
            copy.neighbors.append(dfs(neighbor))
        return copy
    return dfs(node)
```

**Complexity analysis:**
- **Time Complexity:** $O(V + E)$ where $V$ is the number of vertices (nodes) and $E$ is the number of edges. Each vertex and edge is traversed once.
- **Space Complexity:** $O(V)$ auxiliary space to store the cloned nodes in the `visited` dictionary and recursion stack.

**Algorithmic mechanics and edge cases:**
Graph cycles would cause infinite recursion if not intercepted. By storing `copy` in `visited` *before* iterating over its neighbors, any cycle back to `curr` returns `visited[curr]` immediately without recursing. Edge cases include empty graph (`node = None`), single isolated node with no neighbors (`[[]]`), and fully connected complete graphs.

## Why

Registering the cloned node in visited before traversing neighbors terminates cycles immediately upon back-edge detection.

## Worked Case

node=Node(1). No neighbors. visited[1]=Node(1). Loop over neighbors is empty. Returns cloned Node(1). Correct.

## Risk

Appending dfs(neighbor) before recording visited[curr] leads to infinite recursion on cyclic graphs.

## Trade-off

Recursion takes O(V) call stack memory; BFS queue iteration takes O(V) heap memory with identical time complexity.

## Try This

Trace a triangle graph 1-2-3-1: node 1 clones, traverses 2, 2 clones and traverses 3, 3 connects back to 1 (returns visited[1]).

## Follow-ups

### How do you implement graph cloning iteratively using BFS?

Use collections.deque; when dequeuing node, iterate over neighbors, create and enqueue unvisited neighbors, and append clones to copy.neighbors.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you detect cycles and find valid course orderings using topological sort?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Course Schedule (LeetCode 207) determines whether it is possible to finish all courses given prerequisite pairs `[a, b]` (where course `b` must be taken before course `a`). The optimal solution uses Kahn's algorithm for topological sorting: compute in-degrees for all vertices and use a BFS queue to process courses with 0 in-degrees.

```python
from collections import deque

def can_finish(num_courses: int, prerequisites: list[list[int]]) -> bool:
    adj: list[list[int]] = [[] for _ in range(num_courses)]
    in_degree = [0] * num_courses
    for dest, src in prerequisites:
        adj[src].append(dest)
        in_degree[dest] += 1
    queue = deque([i for i in range(num_courses) if in_degree[i] == 0])
    processed = 0
    while queue:
        curr = queue.popleft()
        processed += 1
        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return processed == num_courses
```

**Complexity analysis:**
- **Time Complexity:** $O(V + E)$ where $V = \text{num\_courses}$ and $E = \text{len}(\text{prerequisites})$. Building the graph and processing vertices takes linear time.
- **Space Complexity:** $O(V + E)$ space to store the adjacency list and in-degree counts.

**Algorithmic mechanics and edge cases:**
A valid course ordering exists if and only if the directed graph is a Directed Acyclic Graph (DAG). Courses with in-degree 0 have no prerequisites and can be taken immediately. When a course is processed, we decrement the in-degree of its dependent courses. If any cycle exists, nodes in the cycle never reach in-degree 0, causing `processed < num_courses`. Edge cases include no prerequisites (returns True), self-loops (`[0, 0]`), and disconnected DAG components.

## Why

Kahn's BFS in-degree reduction identifies directed cycles by proving whether all vertices can be topologically ordered.

## Worked Case

num_courses=2, prerequisites=[[1,0]]. in_degree: [0, 1]. queue=[0]. Pop 0, processed=1. in_degree[1] decrements to 0, enqueue 1. Pop 1, processed=2 == 2. Returns True.

## Risk

Building the graph with reversed edge directions (dest -> src instead of src -> dest) inverts dependency prerequisites.

## Trade-off

Kahn's algorithm handles disconnected components and cycle detection cleanly without managing 3-state DFS recursion colors.

## Try This

Test num_courses=2, prerequisites=[[1, 0], [0, 1]]: both in-degrees are 1; queue starts empty; processed=0 != 2 -> False.

## Follow-ups

### How do you return the actual course sequence (Course Schedule II)?

Append curr to an order list when popped from queue; if processed == num_courses return order, else return [].

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/collections.html

# How do you find all grid coordinates that can flow water to both the Pacific and Atlantic oceans?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Pacific Atlantic Water Flow (LeetCode 417) finds all grid cells from which rain water can flow to both the Pacific and Atlantic oceans, where water flows from a cell to adjacent cells of equal or lower elevation. The optimal solution reverses the flow: run BFS (or DFS) inward from the Pacific borders and Atlantic borders separately, then return the intersection of reachable cells.

```python
def pacific_atlantic(heights: list[list[int]]) -> list[list[int]]:
    if not heights:
        return []
    m, n = len(heights), len(heights[0])
    pacific: set[tuple[int, int]] = set()
    atlantic: set[tuple[int, int]] = set()
    def dfs(r: int, c: int, visited: set[tuple[int, int]]) -> None:
        visited.add((r, c))
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and (nr, nc) not in visited:
                # Reverse flow: water flows uphill or equal
                if heights[nr][nc] >= heights[r][c]:
                    dfs(nr, nc, visited)
    for r in range(m):
        dfs(r, 0, pacific)         # Pacific left
        dfs(r, n - 1, atlantic)    # Atlantic right
    for c in range(n):
        dfs(0, c, pacific)         # Pacific top
        dfs(m - 1, c, atlantic)    # Atlantic bottom
    return [[r, c] for r, c in pacific & atlantic]
```

**Complexity analysis:**
- **Time Complexity:** $O(m \cdot n)$ where $m$ and $n$ are grid dimensions. Each cell is visited at most twice (once for Pacific, once for Atlantic).
- **Space Complexity:** $O(m \cdot n)$ to store visited sets and recursion call stack.

**Algorithmic mechanics and edge cases:**
Simulating flow from every individual cell outward to the ocean takes $O((m \cdot n)^2)$ which times out. Inverting the problem flows water *uphill* from ocean boundaries into the island: starting at the Pacific border (top and left edges) and Atlantic border (bottom and right edges). Any cell present in both `pacific` and `atlantic` sets can reach both oceans. Edge cases include $1 \times 1$ grids (reaches both oceans), flat grids, and isolated mountain ridges.

## Why

Reversing flow from ocean borders inward reduces a quadratic O((m*n)^2) search to linear O(m*n) multi-source reachability.

## Worked Case

heights=[[1,2,2,3,5],[3,2,3,4,4],[2,4,5,3,1],[6,7,1,4,5],[5,1,1,2,4]]. Pacific borders start from top/left. Atlantic borders start from bottom/right. Intersection captures peak coordinates like [0,4], [1,3], [1,4], [2,2], [3,0], [3,1], [4,0].

## Risk

Searching outward from every cell causes redundant traversals and easily exceeds time limits.

## Trade-off

Using set intersection pacific & atlantic finds overlapping cells in O(m * n) time.

## Try This

Trace a 1x1 grid [[1]]: cell (0,0) is visited from both borders; returns [[0, 0]].

## Follow-ups

### How do you implement this using Breadth-First Search (BFS)?

Initialize a queue with all Pacific boundary cells; run BFS expanding to neighbors with height >= current; repeat for Atlantic.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/stdtypes.html

# How do you calculate the minimum minutes until all fresh oranges rot using multi-source BFS?

<!-- meta
answer_format: conceptual
difficulty: interview
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Direct answer:** Rotting Oranges (LeetCode 994) calculates the minimum minutes until all fresh oranges (`1`) turn rotten, where rotten oranges (`2`) infect adjacent 4-directional fresh oranges every minute. The optimal solution uses multi-source BFS: enqueue all initially rotten oranges, count fresh oranges, and expand minute-by-minute until no fresh oranges remain.

```python
from collections import deque

def oranges_rotting(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])
    queue: deque[tuple[int, int]] = deque()
    fresh = 0
    for r in range(m):
        for c in range(n):
            if grid[r][c] == 2:
                queue.append((r, c))
            elif grid[r][c] == 1:
                fresh += 1
    if fresh == 0:
        return 0
    minutes = 0
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    while queue and fresh > 0:
        minutes += 1
        for _ in range(len(queue)):
            r, c = queue.popleft()
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))
    return minutes if fresh == 0 else -1
```

**Complexity analysis:**
- **Time Complexity:** $O(m \cdot n)$ where $m$ and $n$ are grid dimensions. Each cell is processed at most once.
- **Space Complexity:** $O(m \cdot n)$ for the BFS queue storing at most $m \times n$ cell coordinates.

**Algorithmic mechanics and edge cases:**
Rotting is a simultaneous wave propagation process. Initializing the BFS queue with all initially rotten oranges ensures that the infection advances by 1 step in all directions per minute (multi-source BFS). Tracking `fresh` ensures we stop as soon as all fresh oranges rot and detect disconnected fresh oranges that can never be reached (returning `-1`). Edge cases include no fresh oranges initially (returns `0`), no rotten oranges with fresh oranges present (returns `-1`), and empty cells (`0`).

## Why

Multi-source BFS models simultaneous parallel infection waves, tracking elapsed time accurately level by level.

## Worked Case

grid=[[2,1,1],[0,1,1],[1,0,1]]. Orange at (2,0) is separated by 0s from rotten oranges. Multi-source BFS finishes with fresh=1 > 0. Returns -1.

## Risk

Incrementing minutes unconditionally when the queue is non-empty adds 1 extra minute after all fresh oranges have already rotted.

## Trade-off

Mutating grid[nr][nc] = 2 in-place eliminates the need for an auxiliary visited boolean matrix.

## Try This

Trace grid=[[2,1,1],[1,1,0],[0,1,1]]: queue starts with (0,0); fresh=6. Minutes increment to 4 when fresh drops to 0.

## Follow-ups

### How does multi-source BFS differ from single-source BFS on a graph?

All starting sources are seeded at distance 0 in the queue initially, expanding wavefronts concurrently.

## Citations

- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/collections.html
