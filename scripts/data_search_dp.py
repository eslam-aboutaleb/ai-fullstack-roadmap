"""16 Binary Search, Backtracking, and Dynamic Programming Questions."""

QUESTIONS = [
    {
        "Q": "How do you search for a target value in a rotated sorted array in O(log n) time?",
        "A": "**Direct answer:** Search in Rotated Sorted Array (LeetCode 33) finds the index of a target in an array sorted in ascending order with distinct values rotated at an unknown pivot. The optimal solution uses a modified binary search: at any midpoint `mid`, at least one half of the array is guaranteed to be strictly sorted, allowing the algorithm to determine whether `target` falls within the sorted interval and halve the search space.\n\n```python\ndef search_rotated_array(nums: list[int], target: int) -> int:\n    left, right = 0, len(nums) - 1\n    while left <= right:\n        mid = left + (right - left) // 2\n        if nums[mid] == target:\n            return mid\n        # Check if left half is sorted\n        if nums[left] <= nums[mid]:\n            if nums[left] <= target < nums[mid]:\n                right = mid - 1\n            else:\n                left = mid + 1\n        # Otherwise right half must be sorted\n        else:\n            if nums[mid] < target <= nums[right]:\n                left = mid + 1\n            else:\n                right = mid - 1\n    return -1\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(\\log n)$ where $n$ is the length of `nums`. Each step cuts the search space in half.\n- **Space Complexity:** $O(1)$ auxiliary space because execution requires only index pointers.\n\n**Algorithmic mechanics and edge cases:**\nDividing a rotated sorted array at any point always yields one strictly sorted half and one rotated half. If `nums[left] <= nums[mid]`, the left half is monotonic; we then test whether `nums[left] <= target < nums[mid]`. If so, `target` must be in the left half; otherwise it must be in the right. If the left half is not sorted, the right half is guaranteed to be sorted. Edge cases include target not found (returns `-1`), array not rotated (standard binary search), and single-element arrays.",
        "Why": "Identifying the strictly sorted half allows testing boundary inclusion in O(1), maintaining logarithmic reduction.",
        "Risk": "Missing <= in nums[left] <= nums[mid] breaks when left == mid on two-element subarrays.",
        "Trade": "Modified binary search eliminates the need for an initial O(log n) pass to locate the pivot index.",
        "Try": "Trace nums=[4, 5, 6, 7, 0, 1, 2] with target=0: left half [4, 5, 6, 7] is sorted; target 0 is not within [4, 7], so search moves to right half.",
        "worked_case": "nums=[4,5,6,7,0,1,2], target=3. mid=3 (7). Left half [4,7] sorted; 3 is not in [4,7] -> left=4. Subarray [0,1,2], mid=5 (1). Right half [1,2] sorted; 3 is not in [1,2] -> right=4. Subarray [0], mid=4 (0 != 3). Exits, returns -1.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "What happens if duplicate values are allowed in the array (Search in Rotated Sorted Array II)?",
                "A": "When nums[left] == nums[mid] == nums[right], you cannot determine which half is sorted; you must increment left and decrement right, degrading worst-case to O(n)."
            }
        ]
    },
    {
        "Q": "How do you find the minimum element in a rotated sorted array in logarithmic time?",
        "A": "**Direct answer:** Find Minimum in Rotated Sorted Array (LeetCode 153) finds the minimum element in an array of unique sorted elements rotated between 1 and $n$ times. The optimal solution uses binary search comparing `nums[mid]` directly against `nums[right]` to locate the rotation cliff.\n\n```python\ndef find_min(nums: list[int]) -> int:\n    left, right = 0, len(nums) - 1\n    while left < right:\n        mid = left + (right - left) // 2\n        if nums[mid] > nums[right]:\n            # Cliff is to the right; minimum must be in right half\n            left = mid + 1\n        else:\n            # Minimum is at mid or in left half\n            right = mid\n    return nums[left]\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(\\log n)$ where $n$ is the length of `nums`. Halves search space on each step.\n- **Space Complexity:** $O(1)$ auxiliary space because it uses only two index pointers.\n\n**Algorithmic mechanics and edge cases:**\nBecause elements are unique, if `nums[mid] > nums[right]`, the rotation pivot (the minimum element) must lie strictly to the right of `mid`, so we set `left = mid + 1`. If `nums[mid] <= nums[right]`, the right half is sorted, meaning the minimum lies at `mid` or to the left of `mid`, so we set `right = mid` (retaining `mid` as a candidate). The loop terminates when `left == right`. Edge cases include fully sorted arrays (not rotated), two-element arrays, and single-element arrays.",
        "Why": "Comparing nums[mid] against nums[right] determines whether the inflection cliff lies to the left or right of midpoint.",
        "Risk": "Setting right = mid - 1 instead of right = mid can accidentally discard the minimum element when nums[mid] is the minimum.",
        "Trade": "Comparing against nums[right] handles both rotated and unrotated arrays seamlessly without special casing.",
        "Try": "Trace nums=[3, 4, 5, 1, 2]: mid=2 (5 > 2) -> left=3 (1); mid=3 (1 < 2) -> right=3; terminates with min=1.",
        "worked_case": "nums=[4,5,6,7,0,1,2]. mid=3 (val 7 > 2) -> left=4. Subarray [0,1,2]: mid=5 (val 1 < 2) -> right=5. Subarray [0,1]: mid=4 (val 0 < 1) -> right=4. left==right=4. nums[4]=0.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you find the minimum if duplicates are allowed (LeetCode 154)?",
                "A": "When nums[mid] == nums[right], decrement right -= 1 to safely shrink the boundary while preserving the minimum candidate."
            }
        ]
    },
    {
        "Q": "How do you search for a target in an m x n matrix with sorted rows and columns in logarithmic time?",
        "A": "**Direct answer:** Search a 2D Matrix (LeetCode 74) searches for a target value in an $m \\times n$ integer matrix where each row is sorted and the first integer of each row is greater than the last integer of the previous row. The optimal solution treats the matrix as a virtual 1D sorted array of length $m \\cdot n$, performing binary search with coordinate mapping `row = mid // n` and `col = mid % n`.\n\n```python\ndef search_matrix(matrix: list[list[int]], target: int) -> bool:\n    if not matrix or not matrix[0]:\n        return False\n    m, n = len(matrix), len(matrix[0])\n    left, right = 0, m * n - 1\n    while left <= right:\n        mid = left + (right - left) // 2\n        val = matrix[mid // n][mid % n]\n        if val == target:\n            return True\n        elif val < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return False\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(\\log(m \\cdot n))$ which equals $O(\\log m + \\log n)$, finding the element in pure logarithmic time.\n- **Space Complexity:** $O(1)$ auxiliary space because it uses virtual 1D indexing without copying matrix cells.\n\n**Algorithmic mechanics and edge cases:**\nBecause each row's start is strictly greater than the previous row's end, the 2D matrix unfolds into a strictly sorted 1D array of size $m \\times n$. Virtual indexing maps any 1D index `idx` to 2D row `idx // n` and column `idx % n` in $O(1)$ time. Edge cases include $1 \\times 1$ matrices, single-row matrices, single-column matrices, and target smaller than `matrix[0][0]` or larger than `matrix[-1][-1]`.",
        "Why": "Virtual 1D coordinate mapping converts 2D matrix lookups into standard binary search in O(log(m*n)) time.",
        "Risk": "Dividing by m instead of n during coordinate mapping inverts row and column coordinate translations.",
        "Trade": "A single virtual binary search is cleaner and faster than doing two separate binary searches (one for row, one for column).",
        "Try": "Search 3 in matrix=[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]] and trace mid=5 (idx // 4 = 1, idx % 4 = 1 -> val=11).",
        "worked_case": "matrix=[[1,3,5,7],[10,11,16,20],[23,30,34,60]], target=13. left=0, right=11. mid=5 -> (1,1) val 11 < 13 -> left=6. mid=8 -> (2,0) val 23 > 13 -> right=7. mid=6 -> (1,2) val 16 > 13 -> right=5. left > right. Returns False.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you solve Search a 2D Matrix II where rows and columns are sorted but row starts do not exceed previous ends?",
                "A": "Start from the top-right corner (0, n - 1); if target is smaller move left (col -= 1), if larger move down (row += 1) in O(m + n) time."
            }
        ]
    },
    {
        "Q": "How do you find the minimum integer eating speed using binary search on answer?",
        "A": "**Direct answer:** Koko Eating Bananas (LeetCode 875) finds the minimum integer eating speed $k$ such that Koko can eat all bananas from $n$ piles within $h$ hours. The optimal solution uses binary search on answer over the range $[1, \\max(\\text{piles})]$, evaluating whether a speed $k$ allows finishing within $h$ hours using a monotonic predicate.\n\n```python\nimport math\n\ndef min_eating_speed(piles: list[int], h: int) -> int:\n    left, right = 1, max(piles)\n    while left < right:\n        mid = left + (right - left) // 2\n        # Hours required at speed mid\n        hours = sum(math.ceil(p / mid) for p in piles)\n        if hours <= h:\n            # Speed is sufficient, try slower speed\n            right = mid\n        else:\n            # Speed is too slow, must eat faster\n            left = mid + 1\n    return left\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n \\log(\\max(\\text{piles})))$ where $n$ is the number of piles. Binary search takes $\\log(\\max)$ steps, each taking $O(n)$ to sum hours.\n- **Space Complexity:** $O(1)$ auxiliary space because it only calculates sums over piles.\n\n**Algorithmic mechanics and edge cases:**\nThe predicate function $f(k) = (\\text{total\\_hours}(k) \\le h)$ is monotonic: if speed $k$ is sufficient to finish in $h$ hours, any speed $k' > k$ is also sufficient. Binary search exploits this monotonicity to locate the smallest speed where $f(k)$ becomes true. At each pile, Koko spends $\\lceil p / k \\rceil = (p + k - 1) // k$ hours. Edge cases include $h = \\text{len}(piles)$ (speed must be $\\max(piles)$) and large pile sizes up to $10^9$.",
        "Why": "The total hours function is monotonically decreasing with speed, allowing binary search to find the minimal feasible parameter.",
        "Risk": "Using right = sum(piles) unnecessarily expands binary search bounds; max(piles) is the absolute upper bound needed.",
        "Trade": "Using (p + mid - 1) // mid integer arithmetic avoids floating-point ceiling imprecision on large pile values.",
        "Try": "Trace piles=[3, 6, 7, 11] with h=8: max speed is 11; binary search converges on optimal speed k=4 (hours = 1 + 2 + 2 + 3 = 8).",
        "worked_case": "piles=[30,11,23,4,20], h=5. Range [1, 30]. Since h==len(piles), Koko must eat at least the largest pile in 1 hour. Result is max(piles) = 30.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/math.html"],
        "follow_ups": [
            {
                "Q": "How does this pattern apply to Capacity To Ship Packages Within D Days (LeetCode 1011)?",
                "A": "Binary search on ship capacity over [max(weights), sum(weights)], checking if days_needed(capacity) <= D."
            }
        ]
    },
    {
        "Q": "How do you find a peak element in an array in logarithmic time?",
        "A": "**Direct answer:** Find Peak Element (LeetCode 162) finds an element that is strictly greater than its neighbors in an array where $nums[i] \\neq nums[i+1]$. The optimal solution uses binary search following the upward slope: if `nums[mid] < nums[mid + 1]`, a peak is guaranteed to exist in the right half; otherwise, a peak exists at `mid` or to its left.\n\n```python\ndef find_peak_element(nums: list[int]) -> int:\n    left, right = 0, len(nums) - 1\n    while left < right:\n        mid = left + (right - left) // 2\n        if nums[mid] < nums[mid + 1]:\n            left = mid + 1  # Ascending slope -> peak is to the right\n        else:\n            right = mid      # Descending slope -> peak is at mid or to the left\n    return left\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(\\log n)$ where $n$ is the length of `nums`. Each step halves the search range.\n- **Space Complexity:** $O(1)$ auxiliary space because it only tracks two indices.\n\n**Algorithmic mechanics and edge cases:**\nBecause $nums[-1] = nums[n] = -\\infty$, if `nums[mid] < nums[mid + 1]`, following the ascending slope upwards must eventually reach a peak, because either the array keeps climbing to the final element (which is a peak compared to $-\\infty$) or encounters a drop (which creates an interior peak). Thus, we can safely eliminate the left half. Edge cases include strictly increasing arrays (returns $n-1$), strictly decreasing arrays (returns $0$), and single-element arrays.",
        "Why": "Walking in the direction of the positive gradient guarantees reaching a local maximum in logarithmic time.",
        "Risk": "Comparing nums[mid] with nums[mid - 1] without checking mid > 0 causes IndexError when mid == 0.",
        "Trade": "Binary search finds any valid local peak in O(log n); finding the global maximum requires scanning all n elements.",
        "Try": "Trace nums=[1, 2, 3, 1]: mid=1 (2 < 3) -> left=2; mid=2 (3 > 1) -> right=2; loop terminates at peak index 2.",
        "worked_case": "nums=[1,2,1,3,5,6,4]. mid=3 (3 < 5) -> left=4. Subarray [5,6,4]: mid=5 (6 > 4) -> right=5. left==right=5. nums[5]=6 is a peak. Returns 5.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "Can this be extended to find a peak in a 2D matrix in O(m log n) time?",
                "A": "Yes, find the row maximum at middle column mid_col, and check if it is greater than left/right neighbors; halve columns accordingly."
            }
        ]
    },
    {
        "Q": "How do you design a time-based key-value store supporting timestamped lookups?",
        "A": "**Direct answer:** Time Based Key-Value Store (LeetCode 981) stores multiple values for the same key at different timestamps and retrieves the key's value at a given `timestamp` (or the largest `prev_timestamp <= timestamp`). The optimal solution uses a hash map of lists containing `(timestamp, value)` pairs, using binary search (`bisect_right`) to find the valid value in $O(\\log n)$ time.\n\n```python\nfrom bisect import bisect_right\nfrom collections import defaultdict\n\nclass TimeMap:\n    def __init__(self):\n        self.store: defaultdict[str, list[tuple[int, str]]] = defaultdict(list)\n\n    def set(self, key: str, value: str, timestamp: int) -> None:\n        # Timestamps are strictly increasing for each key\n        self.store[key].append((timestamp, value))\n\n    def get(self, key: str, timestamp: int) -> str:\n        if key not in self.store:\n            return \"\"\n        values = self.store[key]\n        # Binary search for rightmost timestamp <= query timestamp\n        idx = bisect_right(values, (timestamp, chr(127))) - 1\n        return values[idx][1] if idx >= 0 else \"\"\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(1)$ for `set` operations (appending to list). $O(\\log n)$ for `get` operations where $n$ is the number of timestamps recorded for `key`.\n- **Space Complexity:** $O(N)$ where $N$ is total number of `set` entries stored in the data structure.\n\n**Algorithmic mechanics and edge cases:**\nBecause timestamps are strictly increasing per problem constraints, entries in `self.store[key]` are naturally sorted by timestamp. `bisect_right(values, (timestamp, chr(127))) - 1` locates the largest timestamp $\\le \\text{timestamp}$ in $O(\\log n)$ time. If all recorded timestamps are greater than the query timestamp, `idx == -1` and `\"\"` is returned. Edge cases include querying non-existent keys, timestamps earlier than all recorded values, and exact timestamp matches.",
        "Why": "Natural chronological ordering allows append-only O(1) writes with O(log n) binary search lookups on timestamps.",
        "Risk": "Linear scanning of the timestamp list degrades get operations to O(n), causing time limit exceeded on high-volume queries.",
        "Trade": "List appending assumes monotonically increasing timestamps; if timestamps arrive out of order, bisect.insort takes O(n).",
        "Try": "set('foo', 'bar', 1); get('foo', 1) -> 'bar'; get('foo', 3) -> 'bar'; set('foo', 'bar2', 4); get('foo', 4) -> 'bar2'; get('foo', 3) -> 'bar'.",
        "worked_case": "set('love', 'high', 10), set('love', 'low', 20). get('love', 5) -> earlier than 10, returns ''. get('love', 10) -> 'high'. get('love', 15) -> 'high'. get('love', 25) -> 'low'.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/bisect.html"],
        "follow_ups": [
            {
                "Q": "How is this data structure implemented in production time-series databases like Prometheus?",
                "A": "Prometheus groups samples in memory into 2-hour chunks sorted by timestamp, using delta-of-delta compression and binary search for lookups."
            }
        ]
    },
    {
        "Q": "How do you solve Climbing Stairs using space-optimized dynamic programming?",
        "A": "**Direct answer:** Climbing Stairs (LeetCode 70) calculates the number of distinct ways to climb a staircase of $n$ steps taking either 1 or 2 steps at a time. The optimal solution uses dynamic programming with two rolling state variables, matching the Fibonacci recurrence $dp[i] = dp[i-1] + dp[i-2]$ in $O(n)$ time and $O(1)$ space.\n\n```python\ndef climb_stairs(n: int) -> int:\n    if n <= 2:\n        return n\n    prev2 = 1  # ways to reach step 1\n    prev1 = 2  # ways to reach step 2\n    for _ in range(3, n + 1):\n        curr = prev1 + prev2\n        prev2 = prev1\n        prev1 = curr\n    return prev1\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ requiring a single linear loop of $n - 2$ iterations.\n- **Space Complexity:** $O(1)$ auxiliary memory because only two previous step values are retained in memory.\n\n**Algorithmic mechanics and edge cases:**\nTo reach step $i$, one must take 1 step from step $i-1$, or 2 steps from step $i-2$. Therefore, the total combinations to reach step $i$ is $dp[i-1] + dp[i-2]$. Storing the entire $O(n)$ array is unnecessary because computing $dp[i]$ only requires the immediately preceding two values. Edge cases include $n = 1$ (1 way) and $n = 2$ (2 ways).",
        "Why": "Because state transitions depend strictly on the two preceding steps, rolling variables reduce memory from O(n) to O(1).",
        "Risk": "Unmemoized naive recursion Fibonacci(n) takes exponential O(2^n) time and crashes due to repeated subproblems.",
        "Trade": "Rolling state iteration achieves O(1) space and avoids matrix exponentiation complexity for standard constraints.",
        "Try": "Compute climb_stairs(4): step 1=1, step 2=2, step 3=3, step 4=5; verify 5 combinations.",
        "worked_case": "n=3. prev2=1, prev1=2. Loop runs for step 3: curr = 2 + 1 = 3. Returns 3. Combinations are: 1+1+1, 1+2, 2+1.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How can you compute climb_stairs in O(log n) time?",
                "A": "Use Matrix Exponentiation with transformation matrix [[1, 1], [1, 0]], squaring matrices using binary exponentiation in O(log n) steps."
            }
        ]
    },
    {
        "Q": "How do you maximize the total loot in House Robber without triggering alarms?",
        "A": "**Direct answer:** House Robber (LeetCode 198) maximizes the sum of money robbed from houses along a street without robbing any two adjacent houses. The optimal solution uses dynamic programming: for each house, decide whether to rob it (adding its value to the maximum loot from two houses back) or skip it (keeping the maximum loot from the adjacent house).\n\n```python\ndef rob(nums: list[int]) -> int:\n    rob_prev2 = 0  # max money robbing up to house i - 2\n    rob_prev1 = 0  # max money robbing up to house i - 1\n    for num in nums:\n        curr = max(rob_prev1, rob_prev2 + num)\n        rob_prev2 = rob_prev1\n        rob_prev1 = curr\n    return rob_prev1\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ where $n$ is the number of houses, visiting each house once.\n- **Space Complexity:** $O(1)$ auxiliary space because it uses two rolling variables rather than an $O(n)$ DP array.\n\n**Algorithmic mechanics and edge cases:**\nAt each house with value `num`, the state recurrence is $dp[i] = \\max(dp[i-1], dp[i-2] + num)$. Skipping the house preserves $dp[i-1]$; robbing the house adds its loot to $dp[i-2]$. We only need the previous two optimal values, allowing $O(1)$ rolling variable space. Edge cases include empty list (returns 0), single house `[5] -> 5`, and two houses `[1, 2] -> 2`.",
        "Why": "The non-adjacent constraint creates an optimal substructure depending only on max(rob(i-1), rob(i-2) + val).",
        "Risk": "Assuming greedy alternating choices (even vs odd houses) fails on cases like [2, 1, 1, 2] where optimal is robbing 2 and 2 (sum=4).",
        "Trade": "Rolling state variables achieve strict O(1) space without allocating an auxiliary DP table.",
        "Try": "Test with nums=[2, 7, 9, 3, 1]: rob house 0 (2), house 2 (9), house 4 (1) -> total 12.",
        "worked_case": "nums=[1, 2, 3, 1]. i=0 (1): curr=max(0, 0+1)=1. i=1 (2): curr=max(1, 0+2)=2. i=2 (3): curr=max(2, 1+3)=4. i=3 (1): curr=max(4, 2+1)=4. Result: 4.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you solve House Robber II where houses are arranged in a circle?",
                "A": "Run the algorithm twice: once for houses nums[:-1] (excluding last house) and once for nums[1:] (excluding first house), returning max."
            }
        ]
    },
    {
        "Q": "How do you find the fewest number of coins needed to make up a given amount?",
        "A": "**Direct answer:** Coin Change (LeetCode 322) finds the minimum number of coins needed to make up a target amount using an infinite supply of given coin denominations. The optimal solution uses bottom-up dynamic programming: compute the minimum coins for every sub-amount from 1 to `amount` using recurrence $dp[i] = 1 + \\min(dp[i - c])$.\n\n```python\ndef coin_change(coins: list[int], amount: int) -> int:\n    dp = [float(\"inf\")] * (amount + 1)\n    dp[0] = 0  # Base case: 0 coins needed for amount 0\n    for coin in coins:\n        for i in range(coin, amount + 1):\n            dp[i] = min(dp[i], dp[i - coin] + 1)\n    return dp[amount] if dp[amount] != float(\"inf\") else -1\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(\\text{amount} \\times |\\text{coins}|)$. For each coin, we update the DP table from `coin` up to `amount`.\n- **Space Complexity:** $O(\\text{amount})$ auxiliary space to store the DP array.\n\n**Algorithmic mechanics and edge cases:**\nGreedy choice fails for general coin systems (e.g. coins=[1, 3, 4], amount=6: greedy takes 4+1+1=3 coins, but optimal DP takes 3+3=2 coins). Dynamic programming systematically evaluates all denominations. Iterating `i` from `coin` to `amount` implements the *unbounded knapsack* pattern, allowing coins to be reused multiple times. Edge cases include `amount = 0` (returns 0), impossible amounts (returns `-1`), and coins larger than `amount`.",
        "Why": "Unbounded knapsack dynamic programming evaluates all valid combinations to guarantee the global minimum.",
        "Risk": "A greedy approach selecting the largest coin fails on arbitrary currency systems and returns non-optimal counts.",
        "Trade": "Bottom-up 1D array iteration is cache-efficient and avoids recursive call stack overhead.",
        "Try": "Test coins=[1, 2, 5], amount=11: dp builds 11=5+5+1 -> 3 coins.",
        "worked_case": "coins=[2], amount=3. dp[0]=0, dp[1]=inf, dp[2]=1, dp[3]=min(inf, dp[1]+1)=inf. dp[3]==inf -> returns -1 (impossible).",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you count the number of combinations that make up the amount (Coin Change II)?",
                "A": "Change recurrence to dp[i] += dp[i - coin] with coin loop outer to count unique combinations without permutations."
            }
        ]
    },
    {
        "Q": "How do you find the length of the longest strictly increasing subsequence in O(n log n) time?",
        "A": "**Direct answer:** Longest Increasing Subsequence (LeetCode 300) finds the length of the longest strictly increasing subsequence in an array. The optimal solution uses patience sorting with binary search (`bisect_left`): maintain an array `tails` where `tails[i]` stores the smallest tail element among all increasing subsequences of length $i + 1$.\n\n```python\nfrom bisect import bisect_left\n\ndef length_of_lis(nums: list[int]) -> int:\n    tails: list[int] = []\n    for x in nums:\n        idx = bisect_left(tails, x)\n        if idx == len(tails):\n            tails.append(x)  # x is larger than all tails; extends LIS length\n        else:\n            tails[idx] = x   # x can form a smaller tail for subsequence of length idx + 1\n    return len(tails)\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n \\log n)$ where $n$ is the length of `nums`. Each element triggers a binary search over `tails` of length at most $n$.\n- **Space Complexity:** $O(n)$ auxiliary space to store the `tails` array.\n\n**Algorithmic mechanics and edge cases:**\n`tails` is always strictly sorted, which enables binary search. If incoming number `x` is greater than all elements in `tails`, it extends the maximum LIS length found so far (`tails.append(x)`). If `x` falls within `tails`, it replaces the first element $\\ge x$, creating a smaller, more advantageous tail for that subsequence length without changing the current LIS length. Note that `tails` does not necessarily represent the actual LIS elements, but its length strictly equals the LIS length. Edge cases include strictly decreasing arrays (`len=1`), strictly increasing arrays (`len=n`), and arrays with duplicates (`bisect_left` enforces strictly increasing order).",
        "Why": "Patience sorting maintains the minimal tail for every subsequence length, enabling binary search updates in O(log n).",
        "Risk": "A standard O(n^2) nested DP approach times out on arrays with length >= 10,000.",
        "Trade": "Patience sorting tracks optimal tail values but requires a predecessor pointer array if the actual subsequence elements must be reconstructed.",
        "Try": "Trace nums=[10, 9, 2, 5, 3, 7, 101, 18]: tails evolves [10] -> [9] -> [2] -> [2, 5] -> [2, 3] -> [2, 3, 7] -> [2, 3, 7, 101] -> [2, 3, 7, 18] (length 4).",
        "worked_case": "nums=[0,1,0,3,2,3]. tails updates: [0] -> [0,1] -> [0,1] -> [0,1,3] -> [0,1,2] -> [0,1,2,3]. Final length is 4.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/bisect.html"],
        "follow_ups": [
            {
                "Q": "How do you reconstruct the actual sequence of elements forming the LIS in O(n log n)?",
                "A": "Store parent index pointers when replacing or appending elements in tails, then trace back from the final tail element."
            }
        ]
    },
    {
        "Q": "How do you find the number of unique paths in an m x n grid from top-left to bottom-right?",
        "A": "**Direct answer:** Unique Paths (LeetCode 62) finds the number of unique paths from the top-left corner to the bottom-right corner of an $m \\times n$ grid, moving only down or right. The optimal dynamic programming solution compresses the $m \\times n$ grid into a 1D row array, updating cells via $dp[j] = dp[j] + dp[j-1]$ in $O(m \\cdot n)$ time and $O(n)$ space.\n\n```python\ndef unique_paths(m: int, n: int) -> int:\n    dp = [1] * n  # Base case: 1 path along the top row\n    for _ in range(1, m):\n        for j in range(1, n):\n            dp[j] += dp[j - 1]\n    return dp[-1]\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(m \\cdot n)$ requiring $(m - 1) \\times (n - 1)$ addition operations.\n- **Space Complexity:** $O(\\min(m, n))$ auxiliary memory by keeping a single row array.\n\n**Algorithmic mechanics and edge cases:**\nAny cell $(i, j)$ can only be reached from $(i-1, j)$ (from above) or $(i, j-1)$ (from the left). Thus, $\\text{paths}(i, j) = \\text{paths}(i-1, j) + \\text{paths}(i, j-1)$. In a 1D row array, `dp[j]` before the update holds the value from the row above $(i-1, j)$, and `dp[j-1]` holds the updated value from the left $(i, j-1)$. Adding `dp[j] += dp[j-1]` performs the state transition in-place. Edge cases include $1 \\times n$ and $m \\times 1$ grids (always returns 1) and $1 \\times 1$ grids.",
        "Why": "Because state transitions only reference the current and previous row, a single 1D array achieves O(n) memory.",
        "Risk": "Allocating full m x n matrices consumes extra memory; mathematical combinations C(m+n-2, m-1) risk integer overflow in static languages.",
        "Trade": "1D DP avoids big-integer factorial division bugs while running in negligible milliseconds.",
        "Try": "Compute unique_paths(3, 7): dp initialized to [1,1,1,1,1,1,1]; row 1 updates to [1,2,3,4,5,6,7]; row 2 updates to [1,3,6,10,15,21,28]; returns 28.",
        "worked_case": "m=3, n=2. dp=[1, 1]. Row 1: dp[1] += dp[0] -> dp=[1, 2]. Row 2: dp[1] += dp[0] -> dp=[1, 3]. Returns 3.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you handle grid obstacles (Unique Paths II)?",
                "A": "If grid[i][j] == 1, set dp[j] = 0; otherwise update dp[j] += dp[j-1] if j > 0."
            }
        ]
    },
    {
        "Q": "How do you determine if you can reach the last index of an array in Jump Game?",
        "A": "**Direct answer:** Jump Game (LeetCode 55) determines if you can reach the last index starting from index 0, where `nums[i]` represents your maximum jump length from position $i$. The optimal solution uses a greedy approach tracking the maximum reachable index (`max_reach`) in a single linear pass.\n\n```python\ndef can_jump(nums: list[int]) -> bool:\n    max_reach = 0\n    for i, jump in enumerate(nums):\n        if i > max_reach:\n            return False  # Cannot reach index i\n        max_reach = max(max_reach, i + jump)\n        if max_reach >= len(nums) - 1:\n            return True\n    return True\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. It performs a single pass with early exit.\n- **Space Complexity:** $O(1)$ auxiliary space because it only maintains a single integer variable `max_reach`.\n\n**Algorithmic mechanics and edge cases:**\nAt any point, `max_reach` is the farthest index we can reach from all previously explored positions. If the current index $i$ is strictly greater than `max_reach`, we have encountered an unreachable gap (e.g. stalled by preceding zeros) and can terminate immediately with `False`. If `max_reach >= len(nums) - 1`, we can reach the end. Edge cases include single-element arrays `[0]` (returns True, already at destination) and arrays with zeros.",
        "Why": "Tracking the maximal reach boundary greedily establishes reachability in O(1) space without backtracking.",
        "Risk": "Using DFS/BFS backtracking explores exponential O(2^n) branches on large arrays filled with identical jump numbers.",
        "Trade": "Greedy reach tracking is strictly linear and terminates as soon as max_reach covers the final index.",
        "Try": "Test nums=[2, 3, 1, 1, 4]: i=0 reaches 2; i=1 reaches 1+3=4 >= 4 -> returns True immediately.",
        "worked_case": "nums=[3, 2, 1, 0, 4]. i=0: reach=3. i=1: reach=max(3, 3)=3. i=2: reach=max(3, 3)=3. i=3: reach=max(3, 3)=3. i=4: i=4 > reach=3 -> cannot reach index 4! Returns False.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you find the minimum number of jumps to reach the last index (Jump Game II)?",
                "A": "Use BFS greedy levels tracking current_end and farthest_reach; when i == current_end, increment jumps and update current_end = farthest_reach."
            }
        ]
    },
    {
        "Q": "How do you determine if an array can be partitioned into two subsets with equal sum?",
        "A": "**Direct answer:** Partition Equal Subset Sum (LeetCode 416) determines whether an integer array can be partitioned into two subsets with equal sums. The problem reduces to 0/1 Knapsack: check if a subset of `nums` sums to `target = sum(nums) // 2`. The optimal solution uses a 1D boolean DP array or integer bitmask.\n\n```python\ndef can_partition(nums: list[int]) -> bool:\n    total = sum(nums)\n    if total % 2 != 0:\n        return False\n    target = total // 2\n    dp = [False] * (target + 1)\n    dp[0] = True  # Base case: subset sum of 0 is always possible\n    for num in nums:\n        # Iterate backwards to ensure each element is used at most once\n        for i in range(target, num - 1, -1):\n            if dp[i - num]:\n                dp[i] = True\n        if dp[target]:\n            return True\n    return dp[target]\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n \\cdot \\text{target})$ where $n$ is the length of `nums` and `target` is half the total sum.\n- **Space Complexity:** $O(\\text{target})$ space for the 1D boolean array (or $O(1)$ integer using bitwise shifts `bits |= bits << num`).\n\n**Algorithmic mechanics and edge cases:**\nIf the total sum is odd, partitioning into two integer equal sums is impossible (returns `False`). `dp[i]` is True if sum `i` can be formed using a subset. Iterating `i` *backwards* from `target` down to `num` ensures that each number is used at most once (0/1 Knapsack invariant). If we iterated forward, `num` could be added repeatedly like unbounded knapsack. Edge cases include `target < max(nums)` (returns False), single-element arrays, and arrays with duplicate values.",
        "Why": "Iterating backwards across the 1D DP array guarantees 0/1 knapsack element reuse prevention in O(target) space.",
        "Risk": "Iterating forward (range(num, target + 1)) allows a single number to be reused multiple times, producing incorrect sums.",
        "Trade": "Bitmasking (bits |= (bits << num)) computes 64 state transitions per CPU instruction, achieving a 64x speedup over boolean arrays.",
        "Try": "Test with nums=[1, 5, 11, 5]: total=22, target=11; numbers 1, 5, 5 sum to 11 -> returns True.",
        "worked_case": "For nums=[1, 5, 11, 5]: total sum is 22; target = 11. Array iteration: num 1 sets dp[1]=True; num 5 sets dp[6], dp[5]=True; num 11 sets dp[11]=True -> target reached, returns True.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you implement this in a single line using Python's arbitrary-precision integers?",
                "A": "total = sum(nums); return not total % 2 and bool((functools.reduce(lambda b, x: b | (b << x), nums, 1) >> (total // 2)) & 1)."
            }
        ]
    },
    {
        "Q": "How do you find if a word exists in a 2D character grid using backtracking?",
        "A": "**Direct answer:** Word Search (LeetCode 79) checks if a word exists in an $m \\times n$ grid of characters, moving sequentially to adjacent cells (horizontally or vertically) without reusing the same cell twice. The optimal solution uses DFS backtracking with in-place cell masking.\n\n```python\ndef exist(board: list[list[str]], word: str) -> bool:\n    m, n = len(board), len(board[0])\n    def dfs(r: int, c: int, idx: int) -> bool:\n        if idx == len(word):\n            return True\n        if not (0 <= r < m and 0 <= c < n) or board[r][c] != word[idx]:\n            return False\n        temp = board[r][c]\n        board[r][c] = \"#\"  # In-place visited mark\n        found = (dfs(r + 1, c, idx + 1) or\n                 dfs(r - 1, c, idx + 1) or\n                 dfs(r, c + 1, idx + 1) or\n                 dfs(r, c - 1, idx + 1))\n        board[r][c] = temp  # Backtrack restore\n        return found\n    for r in range(m):\n        for c in range(n):\n            if board[r][c] == word[0] and dfs(r, c, 0):\n                return True\n    return False\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(m \\cdot n \\cdot 3^L)$ where $L$ is word length. From the second character onwards, we explore at most 3 directions (excluding the cell we came from).\n- **Space Complexity:** $O(L)$ auxiliary space for the recursion call stack.\n\n**Algorithmic mechanics and edge cases:**\nAt each cell, we verify boundary conditions and character match `board[r][c] == word[idx]`. To avoid visiting the same cell twice along a path without allocating an $m \\times n$ visited matrix, we temporarily replace `board[r][c]` with `'#'` and restore it after exploring all 4 directions (backtracking). Edge cases include word longer than total grid cells (returns False), single-letter words, and palindromic words requiring reverse search pruning.",
        "Why": "Temporarily masking board[r][c] = '#' prevents cycle revisits in-place with O(1) extra memory.",
        "Risk": "Failing to restore board[r][c] = temp corrupts grid characters for subsequent search iterations from other starting cells.",
        "Trade": "In-place masking avoids allocating and clearing an m x n boolean visited grid for each path exploration.",
        "Try": "Search 'ABCCED' in [['A','B','C','E'],['S','F','C','S'],['A','D','E','E']] and trace path A->B->C->C->E->D.",
        "worked_case": "board=[['a','b'],['c','d']], word='abcd'. Starts at (0,0) 'a'. Moves to (0,1) 'b'. From 'b', neighbors are 'a' (#, skipped) and (1,1) 'd' (mismatch with 'c'). Backtracks. Returns False.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you prune searches when word contains characters with high frequency on the board?",
                "A": "If word ends with fewer occurrences than it starts on the board, reverse word to start searching from rare characters first."
            }
        ]
    },
    {
        "Q": "How do you generate all possible subsets (the power set) of an array of unique integers?",
        "A": "**Direct answer:** Subsets (LeetCode 78) generates the power set (all $2^n$ subsets) of a collection of unique integers. The optimal solution uses backtracking to explore the binary decision tree (include or exclude each element) or cascading iterative expansion.\n\n```python\ndef subsets(nums: list[int]) -> list[list[int]]:\n    res: list[list[int]] = []\n    subset: list[int] = []\n    def backtrack(idx: int) -> None:\n        if idx == len(nums):\n            res.append(subset.copy())\n            return\n        # Decision 1: Include nums[idx]\n        subset.append(nums[idx])\n        backtrack(idx + 1)\n        # Decision 2: Exclude nums[idx]\n        subset.pop()\n        backtrack(idx + 1)\n    backtrack(0)\n    return res\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n \\cdot 2^n)$ because there are $2^n$ subsets, and copying each subset to the output list takes $O(n)$ time.\n- **Space Complexity:** $O(n)$ auxiliary space to maintain the `subset` stack during recursion (excluding output list).\n\n**Algorithmic mechanics and edge cases:**\nFor each element $x$, every valid subset either includes $x$ or excludes $x$. The recursion tree branches twice at each index, creating a full binary tree of depth $n$ with $2^n$ leaf nodes. Alternatively, cascading iteration starts with `res = [[]]` and for each `x in nums`, appends `s + [x]` for every existing subset `s`. Edge cases include empty list `nums = []` (returns `[[]]`), single-element arrays `[1] -> [[], [1]]`, and arrays with negative numbers.",
        "Why": "Binary decision tree branching (include or exclude) systematically enumerates all 2^n subsets in linear recursion depth.",
        "Risk": "Appending subset directly without subset.copy() causes all entries in res to reference the same mutable empty list.",
        "Trade": "Backtracking maintains a single working list in O(n) space; bitmask generation (0 to 2^n - 1) is iterative and avoids recursion.",
        "Try": "Trace nums=[1, 2]: backtrack produces [[1, 2], [1], [2], []].",
        "worked_case": "nums=[0]. Decision tree: root -> include 0: [0]; exclude 0: []. Leaves output [[0], []]. Total 2^1 = 2 subsets.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you handle duplicate numbers in nums so that the power set contains no duplicate subsets (Subsets II)?",
                "A": "Sort nums first; during the exclude branch, skip identical adjacent elements using while idx + 1 < len(nums) and nums[idx] == nums[idx+1]: idx += 1."
            }
        ]
    },
    {
        "Q": "How do you find the single number that appears once in an array where all other numbers appear twice?",
        "A": "**Direct answer:** Single Number (LeetCode 136) finds the single element that appears only once in an array where every other element appears exactly twice. The optimal solution uses the bitwise XOR operator (`^`), which cancels out all paired numbers in $O(n)$ time and $O(1)$ space.\n\n```python\ndef single_number(nums: list[int]) -> int:\n    res = 0\n    for num in nums:\n        res ^= num\n    return res\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`, scanning each element once.\n- **Space Complexity:** $O(1)$ auxiliary space because it only maintains a single accumulator variable.\n\n**Algorithmic mechanics and edge cases:**\nBitwise XOR has three mathematical properties: 1) $x \\oplus 0 = x$ (identity); 2) $x \\oplus x = 0$ (self-inverse); 3) commutative and associative ($a \\oplus b \\oplus a = a \\oplus a \\oplus b = 0 \\oplus b = b$). XORing all numbers together cancels every paired duplicate out to 0, leaving only the unique single number. Edge cases include single-element array `[1] -> 1`, negative numbers, and arrays with large integers.",
        "Why": "Bitwise XOR cancellation (x ^ x == 0 and x ^ 0 == x) isolates the unique element in a single pass without extra memory.",
        "Risk": "Using a hash set or Counter takes O(n) memory, which violates the strict O(1) memory constraint.",
        "Trade": "XOR accumulator uses zero extra memory and is faster than any hash table or sorting approach.",
        "Try": "Test nums=[4, 1, 2, 1, 2]: (1^1) cancels to 0, (2^2) cancels to 0, leaving 4 ^ 0 = 4.",
        "worked_case": "For nums=[4, 1, 2, 1, 2]: res starts at 0. res ^= 4 (4); res ^= 1 (5); res ^= 2 (7); res ^= 1 (6); res ^= 2 (4). Paired duplicates cancel out, returning 4.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you find the single number if every other number appears three times (Single Number II)?",
                "A": "Count set bits modulo 3 for each of the 32 bit positions, or use two bitmasks (ones, twos) tracking bit frequencies modulo 3."
            }
        ]
    }
]
