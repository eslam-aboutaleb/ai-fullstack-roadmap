"""20 Array and Sequence Data Structure Algorithmic Questions."""

QUESTIONS = [
    {
        "Q": "How do you find the container that can hold the most water?",
        "A": "**Direct answer:** Container With Most Water (LeetCode 11) finds two vertical lines in an array of heights that, together with the x-axis, form a container holding the maximum area of water. The optimal solution uses two converging pointers (`left` and `right`) initialized at opposite ends of the array, greedily moving the pointer with the smaller height inward at each step.\n\n```python\ndef max_area(height: list[int]) -> int:\n    left, right = 0, len(height) - 1\n    max_water = 0\n    while left < right:\n        width = right - left\n        current_height = min(height[left], height[right])\n        max_water = max(max_water, width * current_height)\n        if height[left] < height[right]:\n            left += 1\n        else:\n            right -= 1\n    return max_water\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ where $n$ is the length of `height`. The pointers converge inwards with each step visiting a new element until they meet.\n- **Space Complexity:** $O(1)$ auxiliary space because only scalar pointer and area variables are maintained.\n\n**Algorithmic mechanics and edge cases:**\nThe area is bounded by the shorter line: $\\text{area} = (\\text{right} - \\text{left}) \\times \\min(h[l], h[r])$. Moving the taller line inward cannot increase the area because the width strictly decreases while the height remains constrained by the shorter line. Therefore, only by moving the shorter line inward is there any possibility of finding a taller boundary that offsets the width reduction. Edge cases include two-element arrays, monotonically decreasing or increasing heights, and flat arrays where all heights are equal.",
        "Why": "Greedily discarding the shorter boundary is provably optimal because no interior line can form a larger rectangle with that shorter boundary.",
        "Risk": "Brute-force nested loops inspect O(n^2) pairs, timing out on arrays with tens of thousands of elements.",
        "Trade": "Two-pointer greedy traversal is strictly linear but relies on the geometric property that height is constrained by the minimum of the two ends.",
        "Try": "Trace with height=[1, 8, 6, 2, 5, 4, 8, 3, 7] and observe that left=1 (h=8) and right=8 (h=7) produce area 7*7=49.",
        "worked_case": "For [1,1]: width=1, min_h=1, area=1. Pointers meet. Result: 1. For [4,3,2,1,4]: ends 0 and 4 have height 4; width=4, area=16. Any inner move reduces width and cannot exceed height 4.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "What if both lines have identical heights height[left] == height[right]?",
                "A": "You can safely move either pointer (or both) inward, because neither line can form a larger container with any intermediate interior point."
            }
        ]
    },
    {
        "Q": "How do you find all unique triplets in an array that sum to zero?",
        "A": "**Direct answer:** 3Sum (LeetCode 15) finds all unique triplets `[nums[i], nums[j], nums[k]]` such that $i \\neq j \\neq k$ and their sum equals zero. The optimal solution sorts the array in $O(n \\log n)$ time, then iterates through each element using a two-pointer scan for the remaining two elements, with explicit duplicate skipping.\n\n```python\ndef three_sum(nums: list[int]) -> list[list[int]]:\n    nums.sort()\n    res: list[list[int]] = []\n    n = len(nums)\n    for i in range(n - 2):\n        if nums[i] > 0:\n            break  # Smallest element > 0 cannot sum to 0\n        if i > 0 and nums[i] == nums[i - 1]:\n            continue  # Skip duplicate first element\n        left, right = i + 1, n - 1\n        while left < right:\n            total = nums[i] + nums[left] + nums[right]\n            if total < 0:\n                left += 1\n            elif total > 0:\n                right -= 1\n            else:\n                res.append([nums[i], nums[left], nums[right]])\n                while left < right and nums[left] == nums[left + 1]:\n                    left += 1\n                while left < right and nums[right] == nums[right - 1]:\n                    right -= 1\n                left += 1\n                right -= 1\n    return res\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n^2)$ where $n$ is the length of `nums`. Sorting takes $O(n \\log n)$, and the outer loop runs $n$ times with an inner $O(n)$ two-pointer scan.\n- **Space Complexity:** $O(1)$ auxiliary space (ignoring output and sorting space) or $O(n)$ for Python's Timsort buffer.\n\n**Algorithmic mechanics and edge cases:**\nSorting clusters duplicate elements together. To guarantee uniqueness in the output without a costly `set` of tuples, we skip adjacent duplicate values at three places: when picking `nums[i]`, and when advancing `left` and `right` after finding a valid triplet. Edge cases include arrays with fewer than 3 elements (returns `[]`), all zeros `[0, 0, 0, 0]`, and arrays with no valid triplets.",
        "Why": "Sorting converts a 3D search space into n linear two-pointer scans while providing deterministic duplicate elimination.",
        "Risk": "Failing to skip duplicate values when advancing left and right creates redundant triplets in the output.",
        "Trade": "Sorting mutates the input array (or requires an O(n) sorted copy) but avoids hash table collision and hashing overhead.",
        "Try": "Test with nums=[-1, 0, 1, 2, -1, -4] to verify that [-1, -1, 2] and [-1, 0, 1] are identified without duplicates.",
        "worked_case": "Sorted: [-4, -1, -1, 0, 1, 2]. i=0 (-4): total min is -4+-1+2=-3 < 0, no match. i=1 (-1): left=2 (-1), right=5 (2) -> total 0! Add [-1, -1, 2]. left advances to 3 (0), right to 4 (1) -> total 0! Add [-1, 0, 1].",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you generalize 3Sum to kSum in optimal polynomial time?",
                "A": "Use recursion reducing kSum to (k-1)Sum by fixing one element, terminating at base case 2Sum solved with two pointers in O(n^(k-1)) time."
            }
        ]
    },
    {
        "Q": "How do you calculate the total amount of trapped rainwater in an elevation map?",
        "A": "**Direct answer:** Trapping Rain Water (LeetCode 42) computes how much water an elevation map can trap after raining. The optimal solution uses two pointers (`left` and `right`) tracking `left_max` and `right_max` boundaries, computing trapped water in a single linear pass with $O(1)$ auxiliary memory.\n\n```python\ndef trap(height: list[int]) -> int:\n    if not height:\n        return 0\n    left, right = 0, len(height) - 1\n    left_max, right_max = 0, 0\n    water = 0\n    while left < right:\n        if height[left] < height[right]:\n            if height[left] >= left_max:\n                left_max = height[left]\n            else:\n                water += left_max - height[left]\n            left += 1\n        else:\n            if height[right] >= right_max:\n                right_max = height[right]\n            else:\n                water += right_max - height[right]\n            right -= 1\n    return water\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ where $n$ is the length of `height`. Each bar is visited exactly once as the two pointers converge.\n- **Space Complexity:** $O(1)$ auxiliary space because it avoids precomputing left and right prefix maximum arrays.\n\n**Algorithmic mechanics and edge cases:**\nThe water trapped above any bar at index $i$ is determined by $\\min(\\text{left\\_max}, \\text{right\\_max}) - \\text{height}[i]$. By advancing the pointer with the smaller height, we guarantee that the current bar's trapped water is strictly bounded by its own side's maximum, because the opposite side already has an even taller barrier. Edge cases include empty arrays, monotonic staircases (which trap 0 water), and inverted pyramids.",
        "Why": "The two-pointer technique determines the limiting boundary on the fly, eliminating the two O(n) prefix/suffix maximum arrays.",
        "Risk": "Monotonic decreasing or increasing arrays trap zero water; boundary checks must handle flat elevations safely.",
        "Trade": "Two-pointer O(1) space is faster and more cache-friendly than monotonic stack approaches which require O(n) memory.",
        "Try": "Trace with height=[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1] to confirm that 6 units of water are trapped.",
        "worked_case": "height=[4,2,0,3,2,5]. left=0 (4), right=5 (5). Since 4 < 5, process left: idx 1 height 2, water += 4-2=2. idx 2 height 0, water += 4-0=4. idx 3 height 3, water += 4-3=1. idx 4 height 2, water += 4-2=2. Total = 9.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How would you solve this using a monotonic decreasing stack?",
                "A": "Store bar indices in a monotonic stack; when a taller bar arrives, pop the trough, compute bounded height min(curr, stack[-1]) - trough, and multiply by width."
            }
        ]
    },
    {
        "Q": "How do you construct the product of an array except self without using division?",
        "A": "**Direct answer:** Product of Array Except Self (LeetCode 238) returns an array `output` such that `output[i]` is equal to the product of all elements of `nums` except `nums[i]`, without using the division operation. The optimal solution uses a prefix product pass followed by a backward postfix product accumulation directly in the output array.\n\n```python\ndef product_except_self(nums: list[int]) -> list[int]:\n    n = len(nums)\n    res = [1] * n\n    # Prefix products\n    prefix = 1\n    for i in range(n):\n        res[i] = prefix\n        prefix *= nums[i]\n    # Postfix products accumulated directly into res\n    postfix = 1\n    for i in range(n - 1, -1, -1):\n        res[i] *= postfix\n        postfix *= nums[i]\n    return res\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. Two linear passes iterate over the array.\n- **Space Complexity:** $O(1)$ auxiliary space beyond the output array itself, as the running postfix variable stores the running product.\n\n**Algorithmic mechanics and edge cases:**\nFor any element $i$, the result is $\\prod_{j < i} nums[j] \\times \\prod_{j > i} nums[j]$. The first pass populates `res[i]` with the product of all elements to its left. The second pass walks backwards, multiplying `res[i]` by the running product of all elements to its right. Edge cases include arrays containing one zero (only the zero index gets a non-zero product), multiple zeros (all outputs are zero), and negative numbers.",
        "Why": "Accumulating prefix and postfix products directly in the output array eliminates the need for division or extra arrays.",
        "Risk": "Using division (total_product // nums[i]) crashes on arrays containing zero (ZeroDivisionError) and violates interview constraints.",
        "Trade": "Doing two passes in opposite directions trades an extra linear scan for strictly O(1) auxiliary memory.",
        "Try": "Test with nums=[1, 2, 3, 4]: prefix pass produces [1, 1, 2, 6]; postfix pass multiplies by [24, 12, 4, 1] yielding [24, 12, 8, 6].",
        "worked_case": "nums=[-1, 1, 0, -3, 3]. Prefix pass: [1, -1, -1, 0, 0]. Postfix pass from right: idx 2 (zero) gets prefix -1 * postfix 9 = 0? Postfix at idx 2 is (-3)*3=-9, so res[2] = (-1) * (-9) = 9. Other indices hit 0.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "What happens if there are two or more zeros in nums?",
                "A": "Every single element in the output array will be 0, because excluding any one zero leaves at least one other zero in the remaining product."
            }
        ]
    },
    {
        "Q": "How do you merge overlapping intervals into a consolidated set of non-overlapping intervals?",
        "A": "**Direct answer:** Merge Intervals (LeetCode 56) merges all overlapping intervals in a collection into mutually non-overlapping intervals spanning the same ranges. The optimal solution sorts intervals by their start times, then iterates through them, merging overlapping adjacent intervals into the current active interval.\n\n```python\ndef merge_intervals(intervals: list[list[int]]) -> list[list[int]]:\n    if not intervals:\n        return []\n    intervals.sort(key=lambda x: x[0])\n    merged: list[list[int]] = [intervals[0]]\n    for start, end in intervals[1:]:\n        last_end = merged[-1][1]\n        if start <= last_end:\n            merged[-1][1] = max(last_end, end)\n        else:\n            merged.append([start, end])\n    return merged\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n \\log n)$ where $n$ is the number of intervals, dominated by sorting the intervals by start time. The subsequent linear pass takes $O(n)$.\n- **Space Complexity:** $O(n)$ space for Python's Timsort algorithm and the output list.\n\n**Algorithmic mechanics and edge cases:**\nAfter sorting by start time, if interval $B$ overlaps with interval $A$ (where $A$ precedes $B$), it must satisfy $B.\\text{start} \\le A.\\text{end}$. In that case, we extend $A$'s end to $\\max(A.\\text{end}, B.\\text{end})$. If $B.\\text{start} > A.\\text{end}$, no overlap is possible with any subsequent intervals, so $B$ is appended as a new interval. Edge cases include single-interval arrays, fully contained intervals (e.g. `[1, 4]` and `[2, 3]`), and intervals touching at exact endpoints (e.g. `[1, 2]` and `[2, 3]`).",
        "Why": "Sorting by start time guarantees that any intervals capable of overlapping appear consecutively in the scan.",
        "Risk": "Failing to sort first causes disjoint intervals to be missed if they appear out of order in the input list.",
        "Trade": "Sorting adds O(n log n) overhead, but eliminates the need for graph-based connected components running in quadratic time.",
        "Try": "Test with [[1, 3], [2, 6], [8, 10], [15, 18]] and verify that [1, 3] and [2, 6] merge into [1, 6].",
        "worked_case": "Input: [[1,4],[4,5]]. Sorted: [[1,4],[4,5]]. start=4 <= last_end=4 -> overlap! merged[-1][1] = max(4, 5) = 5. Result: [[1,5]].",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you handle interval merging in a real-time streaming environment where intervals arrive dynamically?",
                "A": "Use an Interval Tree or Segment Tree to insert and merge overlapping intervals dynamically in O(log n) time per insertion."
            }
        ]
    },
    {
        "Q": "How do you insert a new interval into a sorted list of non-overlapping intervals?",
        "A": "**Direct answer:** Insert Interval (LeetCode 57) inserts a new interval into an array of non-overlapping intervals sorted by start time, merging any overlaps that arise. The optimal solution uses a single three-phase linear scan: 1) add intervals preceding the new interval; 2) merge all overlapping intervals into `new_interval`; 3) append remaining intervals.\n\n```python\ndef insert_interval(intervals: list[list[int]], new_interval: list[int]) -> list[list[int]]:\n    res: list[list[int]] = []\n    i = 0\n    n = len(intervals)\n    # Phase 1: Add intervals that end before new_interval starts\n    while i < n and intervals[i][1] < new_interval[0]:\n        res.append(intervals[i])\n        i += 1\n    # Phase 2: Merge overlapping intervals\n    while i < n and intervals[i][0] <= new_interval[1]:\n        new_interval[0] = min(new_interval[0], intervals[i][0])\n        new_interval[1] = max(new_interval[1], intervals[i][1])\n        i += 1\n    res.append(new_interval)\n    # Phase 3: Add remaining intervals\n    while i < n:\n        res.append(intervals[i])\n        i += 1\n    return res\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ where $n$ is the number of intervals. Each interval is visited exactly once.\n- **Space Complexity:** $O(n)$ to construct the new output list.\n\n**Algorithmic mechanics and edge cases:**\nBecause the original list is already sorted and non-overlapping, intervals that end before `new_interval[0]` cannot overlap. Intervals whose start is $\\le \\text{new\\_interval}[1]$ must overlap, so we expand `new_interval` to subsume them. Once an interval starts after `new_interval[1]`, all remaining intervals can be appended directly. Edge cases include empty list `[]`, `new_interval` completely before all intervals, or `new_interval` completely after all intervals.",
        "Why": "A three-phase linear scan exploits the pre-sorted invariant to insert and merge in O(n) without re-sorting.",
        "Risk": "Appending new_interval and re-sorting the whole array takes O(n log n) unnecessarily, degrading performance on large arrays.",
        "Trade": "Three simple while loops partition the problem cleanly with no special edge-case branch logic required.",
        "Try": "Insert [4, 8] into [[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]] and trace how [3, 5], [6, 7], and [8, 10] merge into [3, 10].",
        "worked_case": "intervals=[[1,3],[6,9]], new=[2,5]. Phase 1: [1,3] ends at 3 >= 2, stops. Phase 2: [1,3] starts at 1 <= 5 -> merge to [min(2,1), max(5,3)]=[1,5]. Next [6,9] starts at 6 > 5, stops. Append [1,5], then [6,9]. Result: [[1,5],[6,9]].",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "Can binary search be used to find the insertion position in O(log n)?",
                "A": "Binary search can locate the start and end overlapping indices in O(log n), but creating the final merged array still requires O(n) element copying."
            }
        ]
    },
    {
        "Q": "How do you find the minimum number of intervals to remove to make the rest non-overlapping?",
        "A": "**Direct answer:** Non-overlapping Intervals (LeetCode 435) finds the minimum number of intervals you need to remove to make the rest of the intervals non-overlapping. The optimal solution uses greedy interval scheduling by sorting intervals by their end times and keeping intervals that finish earliest.\n\n```python\ndef erase_overlap_intervals(intervals: list[list[int]]) -> int:\n    if not intervals:\n        return 0\n    # Sort by end time\n    intervals.sort(key=lambda x: x[1])\n    removals = 0\n    prev_end = intervals[0][1]\n    for start, end in intervals[1:]:\n        if start < prev_end:\n            removals += 1  # Overlap detected: remove current interval\n        else:\n            prev_end = end  # Compatible interval: update end time\n    return removals\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n \\log n)$ where $n$ is the number of intervals, dominated by sorting by finish time.\n- **Space Complexity:** $O(1)$ auxiliary space (ignoring sort memory).\n\n**Algorithmic mechanics and edge cases:**\nMinimizing removals is mathematically equivalent to maximizing the number of compatible non-overlapping intervals (Interval Scheduling). Sorting by end time leaves the maximum possible remaining time for future intervals. If an interval starts before `prev_end`, it conflicts and must be removed. Edge cases include empty list, intervals that only touch at endpoints (`[1, 2]` and `[2, 3]` are non-overlapping), and identical intervals.",
        "Why": "Sorting by finish time leaves the maximum remaining capacity for subsequent intervals, proving greedy choice optimality.",
        "Risk": "Sorting by start time fails on cases where a long interval starts early and covers multiple smaller intervals.",
        "Trade": "Sorting by end time guarantees optimal greedy choice in O(n log n) without dynamic programming O(n^2) tables.",
        "Try": "Test with [[1, 2], [2, 3], [3, 4], [1, 3]] and confirm that removing [1, 3] leaves 3 non-overlapping intervals with 1 removal.",
        "worked_case": "Input: [[1,2],[1,2],[1,2]]. Sorted by end: all end at 2. First is kept (prev_end=2). Second has start 1 < 2 -> removals=1. Third has start 1 < 2 -> removals=2. Result: 2.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How does this relate to Meeting Rooms II (finding minimum conference rooms needed)?",
                "A": "Meeting Rooms II counts maximum concurrent overlapping intervals using min-heap of end times or two-pointer sweep-line, rather than removing them."
            }
        ]
    },
    {
        "Q": "How do you rotate an array to the right by k steps in-place with O(1) extra memory?",
        "A": "**Direct answer:** Rotate Array (LeetCode 189) rotates an array of $n$ elements to the right by $k$ steps. The optimal in-place solution uses the three-step reversal algorithm: 1) reverse the entire array; 2) reverse the first $k$ elements; 3) reverse the remaining $n - k$ elements.\n\n```python\ndef rotate(nums: list[int], k: int) -> None:\n    n = len(nums)\n    k = k % n\n    def reverse(start: int, end: int) -> None:\n        while start < end:\n            nums[start], nums[end] = nums[end], nums[start]\n            start += 1\n            end -= 1\n    reverse(0, n - 1)      # Reverse entire array\n    reverse(0, k - 1)      # Reverse first k elements\n    reverse(k, n - 1)      # Reverse remaining elements\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. Each element is moved exactly twice.\n- **Space Complexity:** $O(1)$ auxiliary space because reversals occur directly in-place via pointer swapping.\n\n**Algorithmic mechanics and edge cases:**\nReversing the entire array places the last $k$ elements at the front, but in reverse order. Reversing the first $k$ elements restores their relative order. Reversing the remaining $n - k$ elements restores their relative order. Edge cases include $k = 0$, $k \\ge n$ (handled by `k % n`), single-element arrays, and arrays where $k$ is a multiple of $n$.",
        "Why": "Three in-place reversals transpose the two partitioned subarrays [A, B] into [B, A] with zero extra memory allocation.",
        "Risk": "Failing to execute k = k % n raises IndexError when k exceeds array length.",
        "Trade": "The reversal algorithm does 2n swaps; cyclic replacements do n swaps but require complex greatest common divisor cycle logic.",
        "Try": "Trace nums=[1, 2, 3, 4, 5, 6, 7] with k=3: reverse all -> [7, 6, 5, 4, 3, 2, 1]; reverse first 3 -> [5, 6, 7, ...]; reverse rest -> [5, 6, 7, 1, 2, 3, 4].",
        "worked_case": "nums=[-1,-100,3,99], k=2. Reverse all: [99, 3, -100, -1]. Reverse first 2: [3, 99, -100, -1]. Reverse last 2: [3, 99, -1, -100]. Matches expected rotated order.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do cyclic replacements achieve the rotation with exactly n element writes?",
                "A": "Move each element to (i + k) % n in a cycle until returning to the start index, repeating for gcd(n, k) distinct cycles."
            }
        ]
    },
    {
        "Q": "How do you find the next lexicographical permutation of an array of numbers in-place?",
        "A": "**Direct answer:** Next Permutation (LeetCode 31) rearranges numbers into the lexicographically next greater permutation of numbers in-place. If no greater arrangement is possible, it rearranges it as the lowest possible order (sorted ascending). The optimal solution uses a three-step scan: find pivot, find successor, swap and reverse suffix.\n\n```python\ndef next_permutation(nums: list[int]) -> None:\n    n = len(nums)\n    # Step 1: Find largest index i such that nums[i] < nums[i + 1]\n    i = n - 2\n    while i >= 0 and nums[i] >= nums[i + 1]:\n        i -= 1\n    # Step 2: If pivot found, find successor j such that nums[j] > nums[i]\n    if i >= 0:\n        j = n - 1\n        while nums[j] <= nums[i]:\n            j -= 1\n        nums[i], nums[j] = nums[j], nums[i]\n    # Step 3: Reverse the suffix starting at i + 1\n    left, right = i + 1, n - 1\n    while left < right:\n        nums[left], nums[right] = nums[right], nums[left]\n        left += 1\n        right -= 1\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. In the worst case, two scans of the array and one reversal are performed.\n- **Space Complexity:** $O(1)$ auxiliary space as all modifications are done in-place.\n\n**Algorithmic mechanics and edge cases:**\nAny strictly decreasing suffix cannot be made larger. Thus, we scan from the right to find the first decrease `nums[i] < nums[i+1]`. Next, we find the smallest value in the suffix that is strictly greater than `nums[i]` (at index `j`) and swap them. Finally, because the suffix from `i+1` onward remains strictly decreasing, reversing it turns it into strictly increasing order, guaranteeing the smallest lexicographical increment. Edge cases include entirely descending arrays (which simply reverse) and arrays with duplicate values.",
        "Why": "Swapping the pivot with its smallest larger successor and reversing the suffix guarantees the minimal lexicographical increment.",
        "Risk": "Using strictly greater > instead of >= when scanning for pivot causes infinite loops or incorrect swaps on duplicate elements.",
        "Trade": "The single-pass in-place pointer algorithm operates in O(n) time and O(1) memory without generating permutations.",
        "Try": "Trace nums=[1, 2, 3]: i=1 (nums[1]=2 < 3); j=2 (3); swap -> [1, 3, 2]; reverse suffix -> [1, 3, 2].",
        "worked_case": "Input: nums=[3, 2, 1]. i decrements to -1 (entirely descending). i >= 0 check fails. Reversing suffix from 0 to 2 yields [1, 2, 3] (lowest order).",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you find the previous lexicographical permutation?",
                "A": "Mirror the logic: find the first index i from right where nums[i] > nums[i+1], swap with largest smaller element in suffix, and reverse suffix."
            }
        ]
    },
    {
        "Q": "How do you count the total number of continuous subarrays whose sum equals k?",
        "A": "**Direct answer:** Subarray Sum Equals K (LeetCode 560) counts the number of continuous subarrays whose sum equals `k`. The optimal solution uses a prefix sum frequency hash map, running in linear $O(n)$ time and handling both positive and negative integers.\n\n```python\ndef subarray_sum(nums: list[int], k: int) -> int:\n    prefix_counts: dict[int, int] = {0: 1}\n    curr_sum = 0\n    total_subarrays = 0\n    for x in nums:\n        curr_sum += x\n        complement = curr_sum - k\n        if complement in prefix_counts:\n            total_subarrays += prefix_counts[complement]\n        prefix_counts[curr_sum] = prefix_counts.get(curr_sum, 0) + 1\n    return total_subarrays\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. We traverse the array once and perform $O(1)$ average-time dictionary lookups.\n- **Space Complexity:** $O(n)$ auxiliary memory to store prefix sum frequencies in the hash map.\n\n**Algorithmic mechanics and edge cases:**\nA continuous subarray from index $i$ to $j$ has sum equal to $\\text{prefix}[j] - \\text{prefix}[i-1]$. If $\\text{prefix}[j] - \\text{prefix}[i-1] = k$, then $\\text{prefix}[i-1] = \\text{prefix}[j] - k$. Initializing `prefix_counts = {0: 1}` accounts for subarrays starting at index 0. Because elements can be negative, prefix sums are non-monotonic, meaning sliding window fails and hash table lookup is required. Edge cases include all-zero arrays, arrays with negative numbers, and $k = 0$.",
        "Why": "Prefix sum complement lookup finds matching subarray intervals in O(1) time even when negative numbers break sliding window monotonicity.",
        "Risk": "A sliding window assumes non-negative integers; negative numbers cause window shrinkage to be invalid and produce wrong counts.",
        "Trade": "Consuming O(n) space for the hash map is required because prefix sums do not grow monotonically.",
        "Try": "Trace nums=[1, -1, 1, 1, 1, -1] with k=2 and verify that prefix_counts correctly matches multiple overlapping subarrays totaling 6.",
        "worked_case": "nums=[1, 1, 1], k=2. x=1: curr=1, comp=-1 (not in map), map={0:1, 1:1}. x=1: curr=2, comp=0 (count 1) -> total=1, map={0:1, 1:1, 2:1}. x=1: curr=3, comp=1 (count 1) -> total=2. Result: 2.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/collections.html"],
        "follow_ups": [
            {
                "Q": "Why is sliding window invalid for this problem when negative numbers are allowed?",
                "A": "In sliding window, expanding right must strictly increase sum and contracting left must decrease sum; negative values break this directional monotonicity."
            }
        ]
    },
    {
        "Q": "How do you find the maximum length of a contiguous subarray with an equal number of 0 and 1?",
        "A": "**Direct answer:** Contiguous Array (LeetCode 525) finds the maximum length of a binary subarray with equal numbers of `0` and `1`. The optimal solution transforms all `0`s to `-1`s, turning the problem into finding the longest subarray with sum equal to zero, solved using a prefix sum first-seen index map.\n\n```python\ndef find_max_length(nums: list[int]) -> int:\n    first_seen: dict[int, int] = {0: -1}\n    curr_sum = 0\n    max_len = 0\n    for i, num in enumerate(nums):\n        curr_sum += 1 if num == 1 else -1\n        if curr_sum in first_seen:\n            max_len = max(max_len, i - first_seen[curr_sum])\n        else:\n            first_seen[curr_sum] = i\n    return max_len\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. A single pass traverses the array with $O(1)$ dictionary lookups.\n- **Space Complexity:** $O(n)$ auxiliary space to store the earliest index of each unique prefix sum.\n\n**Algorithmic mechanics and edge cases:**\nIf the prefix sum at index $j$ equals the prefix sum at index $i$ (where $i < j$), then the sum of elements between $i+1$ and $j$ must be exactly $0$. Since $1$ represents `1` and $-1$ represents `0`, sum 0 implies equal counts. To maximize length $(j - i)$, we record only the *first* occurrence of each prefix sum and never overwrite it. Initializing `first_seen = {0: -1}` accounts for subarrays starting at index 0. Edge cases include all zeros `[0, 0, 0]`, alternating patterns `[0, 1, 0, 1]`, and single elements.",
        "Why": "Mapping 0 to -1 reduces the equal-count invariant to a net zero sum, located in O(1) via prefix sum index caching.",
        "Risk": "Updating first_seen[curr_sum] on subsequent occurrences shrinks the distance instead of maximizing the interval span.",
        "Trade": "Using a hash map takes O(n) memory; alternatively, a fixed array of size 2n+1 can store indices with offset n to avoid hash collisions.",
        "Try": "Test with nums=[0, 1, 0] and verify that at idx 1 (sum=0), distance 1 - (-1) = 2 is recorded as max length.",
        "worked_case": "nums=[0, 1]. i=0 (0->-1): curr=-1, first_seen={0:-1, -1:0}. i=1 (1->+1): curr=0. 0 is in first_seen at -1 -> len = 1 - (-1) = 2. max_len=2.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you generalize this to an array with 0s, 1s, and 2s having equal counts?",
                "A": "Track a 2D tuple (count1 - count0, count2 - count0) in the first_seen map, checking when both delta coordinates match."
            }
        ]
    },
    {
        "Q": "How do you set matrix zeroes in-place with O(1) extra space?",
        "A": "**Direct answer:** Set Matrix Zeroes (LeetCode 73) modifies an $m \\times n$ integer matrix such that if an element is `0`, its entire row and column are set to `0`. The optimal solution uses the matrix's own first row and first column as flag markers, using two boolean variables to track whether the first row and column themselves should be zeroed.\n\n```python\ndef set_zeroes(matrix: list[list[int]]) -> None:\n    m, n = len(matrix), len(matrix[0])\n    first_row_zero = any(matrix[0][j] == 0 for j in range(n))\n    first_col_zero = any(matrix[i][0] == 0 for i in range(m))\n    # Use first row and column as flags\n    for i in range(1, m):\n        for j in range(1, n):\n            if matrix[i][j] == 0:\n                matrix[i][0] = 0\n                matrix[0][j] = 0\n    # Zero out cells based on flags\n    for i in range(1, m):\n        for j in range(1, n):\n            if matrix[i][0] == 0 or matrix[0][j] == 0:\n                matrix[i][j] = 0\n    # Zero out first row and column if needed\n    if first_row_zero:\n        for j in range(n):\n            matrix[0][j] = 0\n    if first_col_zero:\n        for i in range(m):\n            matrix[i][0] = 0\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(m \\cdot n)$ where $m$ and $n$ are matrix dimensions. Two passes inspect every cell in the grid.\n- **Space Complexity:** $O(1)$ auxiliary space because state is stored inside `matrix[0][:]` and `matrix[:][0]`.\n\n**Algorithmic mechanics and edge cases:**\nUsing auxiliary $O(m + n)$ row and column sets is easy but violates the $O(1)$ space constraint. By reusing `matrix[0][j]` and `matrix[i][0]`, we record zero requirements directly in the grid. Because `matrix[0][0]` overlaps both the first row and column, two separate boolean flags `first_row_zero` and `first_col_zero` preserve the original state of the first row and column. Edge cases include $1 \\times 1$ matrices, matrices with no zeroes, and matrices where every element is zero.",
        "Why": "Reusing the matrix perimeter as zero flags achieves O(1) auxiliary space without overwriting cell values prematurely.",
        "Risk": "Updating matrix[i][j] during the first pass triggers cascading zeroes that erroneously wipe the entire matrix.",
        "Trade": "Reusing row 0 and col 0 requires two boolean variables to resolve the shared corner matrix[0][0] collision.",
        "Try": "Trace with [[1,1,1],[1,0,1],[1,1,1]] and observe how matrix[1][0]=0 and matrix[0][1]=0 flag row 1 and col 1.",
        "worked_case": "matrix=[[0,1,2,0],[3,4,5,2],[1,3,1,5]]. first_row_zero=True (has 0s). matrix[0][0]=0, matrix[0][3]=0. Inner loop updates row 1 and col 0, 3. Final first row pass sets row 0 to 0.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "Can you use a single variable instead of two booleans?",
                "A": "Yes, let matrix[0][0] track the first row and a single boolean col0 track whether the first column has a zero."
            }
        ]
    },
    {
        "Q": "How do you traverse a matrix in clockwise spiral order?",
        "A": "**Direct answer:** Spiral Matrix (LeetCode 54) returns all elements of an $m \\times n$ matrix in clockwise spiral order. The optimal solution uses four directional boundaries (`top`, `bottom`, `left`, `right`) that contract inwards after traversing each row or column.\n\n```python\ndef spiral_order(matrix: list[list[int]]) -> list[int]:\n    if not matrix:\n        return []\n    res: list[int] = []\n    top, bottom = 0, len(matrix) - 1\n    left, right = 0, len(matrix[0]) - 1\n    while top <= bottom and left <= right:\n        # Traverse Right\n        for j in range(left, right + 1):\n            res.append(matrix[top][j])\n        top += 1\n        # Traverse Down\n        for i in range(top, bottom + 1):\n            res.append(matrix[i][right])\n        right -= 1\n        # Traverse Left (if still valid row)\n        if top <= bottom:\n            for j in range(right, left - 1, -1):\n                res.append(matrix[bottom][j])\n            bottom -= 1\n        # Traverse Up (if still valid col)\n        if left <= right:\n            for i in range(bottom, top - 1, -1):\n                res.append(matrix[i][left])\n            left += 1\n    return res\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(m \\cdot n)$ where $m$ and $n$ are matrix rows and columns. Every cell is visited exactly once.\n- **Space Complexity:** $O(1)$ auxiliary space (ignoring the output list).\n\n**Algorithmic mechanics and edge cases:**\nAt each outer layer, we: 1) read top row and increment `top`; 2) read right column and decrement `right`; 3) read bottom row and decrement `bottom`; 4) read left column and increment `left`. Crucially, checks `top <= bottom` and `left <= right` prevent reading duplicate elements when the matrix has an odd number of rows or columns. Edge cases include single-row matrices, single-column matrices, and $1 \\times 1$ matrices.",
        "Why": "Four shrinking boundary pointers eliminate visited matrices and navigate layer by layer in-place.",
        "Risk": "Omitting the if top <= bottom check causes single-row matrices to re-read elements in reverse during the left traversal.",
        "Trade": "Boundary pointer arithmetic avoids allocating an m x n visited boolean array.",
        "Try": "Test with matrix=[[1, 2, 3], [4, 5, 6], [7, 8, 9]] and trace traversal 1,2,3 -> 6,9 -> 8,7 -> 4 -> 5.",
        "worked_case": "matrix=[[1,2,3,4],[5,6,7,8],[9,10,11,12]]. Layer 1: right (1,2,3,4), down (8,12), left (11,10,9), up (5). Inner: right (6,7). Total: [1,2,3,4,8,12,11,10,9,5,6,7].",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you solve Spiral Matrix II to generate an n x n matrix filled with 1 to n^2?",
                "A": "Initialize an empty n x n matrix with zeros and write incrementing numbers 1 to n^2 using the same boundary contraction."
            }
        ]
    },
    {
        "Q": "How do you rotate an n x n 2D image matrix by 90 degrees clockwise in-place?",
        "A": "**Direct answer:** Rotate Image (LeetCode 48) rotates an $n \\times n$ 2D matrix representing an image by 90 degrees clockwise in-place with $O(1)$ extra space. The optimal solution combines two simple matrix reflections: 1) transpose the matrix along its main diagonal; 2) reverse each row horizontally.\n\n```python\ndef rotate_image(matrix: list[list[int]]) -> None:\n    n = len(matrix)\n    # Step 1: Transpose matrix (swap matrix[i][j] with matrix[j][i])\n    for i in range(n):\n        for j in range(i + 1, n):\n            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]\n    # Step 2: Reverse each row horizontally\n    for i in range(n):\n        matrix[i].reverse()\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n^2)$ where $n$ is the matrix dimension. Transposing visits $n(n - 1) / 2$ elements, and reversing rows visits $n^2 / 2$ elements.\n- **Space Complexity:** $O(1)$ auxiliary space because all element swaps occur directly in-place.\n\n**Algorithmic mechanics and edge cases:**\nMathematically, a 90-degree clockwise rotation maps cell $(i, j)$ to $(j, n - 1 - i)$. Transposing maps $(i, j)$ to $(j, i)$. Reversing each row maps $(j, i)$ to $(j, n - 1 - i)$, which matches the target transformation. Performing two standard reflections is far less error-prone than rotating 4-element cycles manually. Edge cases include $1 \\times 1$ matrices (no-op), $2 \\times 2$ matrices, and identity matrices.",
        "Why": "Transposing followed by horizontal reflection achieves a 90-degree clockwise rotation without complex 4-way coordinate tracking.",
        "Risk": "Iterating j across the entire row range(n) during transposition swaps elements twice, undoing the transpose operation.",
        "Trade": "Two passes (transpose then reverse) do slightly more memory writes than a single 4-cycle pass but avoid nested index math bugs.",
        "Try": "Trace with [[1, 2], [3, 4]]: transpose -> [[1, 3], [2, 4]]; reverse rows -> [[3, 1], [4, 2]] (verified 90-degree rotation).",
        "worked_case": "matrix=[[1,2,3],[4,5,6],[7,8,9]]. Transpose: [[1,4,7],[2,5,8],[3,6,9]]. Reverse rows: row 0 -> [7,4,1]; row 1 -> [8,5,2]; row 2 -> [9,6,3]. Correct.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you rotate the matrix 90 degrees counter-clockwise in-place?",
                "A": "Reverse each row horizontally first, then transpose along the main diagonal (or transpose along the anti-diagonal)."
            }
        ]
    },
    {
        "Q": "How do you compute the next generation in Conway's Game of Life in-place?",
        "A": "**Direct answer:** Game of Life (LeetCode 289) calculates the next state of an $m \\times n$ board according to Conway's four rules: underpopulation (<2), survival (2-3), overpopulation (>3), and reproduction (exactly 3). The optimal in-place solution uses intermediate two-bit state transitions ($0 \\to 1$: state 2; $1 \\to 0$: state -1) to preserve past states while computing next states.\n\n```python\ndef game_of_life(board: list[list[int]]) -> None:\n    m, n = len(board), len(board[0])\n    directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]\n    for r in range(m):\n        for c in range(n):\n            live_neighbors = 0\n            for dr, dc in directions:\n                nr, nc = r + dr, c + dc\n                if 0 <= nr < m and 0 <= nc < n and abs(board[nr][nc]) == 1:\n                    live_neighbors += 1\n            # Rule 1 & 3: Live cell dies -> -1\n            if board[r][c] == 1 and (live_neighbors < 2 or live_neighbors > 3):\n                board[r][c] = -1\n            # Rule 4: Dead cell becomes alive -> 2\n            elif board[r][c] == 0 and live_neighbors == 3:\n                board[r][c] = 2\n    # Final pass: update intermediate states to binary\n    for r in range(m):\n        for c in range(n):\n            board[r][c] = 1 if board[r][c] > 0 else 0\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(m \\cdot n)$ where $m$ and $n$ are board dimensions. Each cell inspects 8 neighbors.\n- **Space Complexity:** $O(1)$ auxiliary space because transitions are encoded directly in-place.\n\n**Algorithmic mechanics and edge cases:**\nBecause updates must happen simultaneously, updating a cell directly to its new state destroys the information its neighbors need. By encoding state transitions (1 was originally alive; -1 was alive and is now dead; 0 was originally dead; 2 was dead and is now alive), inspecting `abs(board[nr][nc]) == 1` accurately counts original living neighbors. Edge cases include $1 \\times 1$ boards, dead boards, and boards with infinite oscillators.",
        "Why": "Intermediate state encoding preserves original neighbor values while writing future states in-place.",
        "Risk": "Creating an m x n board copy takes O(m * n) extra memory, which fails scalable in-memory simulation constraints.",
        "Trade": "Two-bit state encoding uses abs() checks to decode past values with zero auxiliary heap allocations.",
        "Try": "Test with a blinker oscillator [[0,1,0],[0,1,0],[0,1,0]] and verify that it transitions to [[0,0,0],[1,1,1],[0,0,0]].",
        "worked_case": "board=[[1,1],[1,0]]. Cell (0,0) has 2 live neighbors -> survives (stays 1). Cell (0,1) has 2 neighbors -> stays 1. Cell (1,0) has 2 neighbors -> stays 1. Cell (1,1) has 3 neighbors -> 0 becomes 2. Final pass yields all 1s.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you handle an infinite grid where only a sparse set of coordinates are alive?",
                "A": "Store live coordinates in a hash set; iterate over live cells and their immediate neighbors to compute transitions."
            }
        ]
    },
    {
        "Q": "How do you find the first missing positive integer in an unsorted array in O(n) time and O(1) space?",
        "A": "**Direct answer:** First Missing Positive (LeetCode 41) finds the smallest missing positive integer from an unsorted array. The optimal solution uses cyclic sort, placing each number $x$ in the range $[1, n]$ at its target index $x - 1$ in-place via element swapping.\n\n```python\ndef first_missing_positive(nums: list[int]) -> int:\n    n = len(nums)\n    for i in range(n):\n        # While nums[i] is in range [1, n] and not already at its correct index\n        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:\n            target_idx = nums[i] - 1\n            nums[i], nums[target_idx] = nums[target_idx], nums[i]\n    for i in range(n):\n        if nums[i] != i + 1:\n            return i + 1\n    return n + 1\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. Each number is swapped to its correct destination at most once; total swaps across all iterations cannot exceed $n$.\n- **Space Complexity:** $O(1)$ auxiliary space because array slots are reused as their own hash buckets.\n\n**Algorithmic mechanics and edge cases:**\nBy the pigeonhole principle, the first missing positive must lie in the range $[1, n + 1]$. We use the array indices $0$ to $n-1$ as a hash table where index $i$ should store $i + 1$. The `while` loop swaps `nums[i]` with the element at index `nums[i] - 1` until either `nums[i]` is out of range $[1, n]$ or already matches. A final linear scan finds the first index $i$ where `nums[i] != i + 1`. Edge cases include negative numbers, numbers $> n$, duplicates (handled by `nums[nums[i] - 1] != nums[i]`), and arrays already sorted `[1, 2, 3] -> 4`.",
        "Why": "Cyclic sort places each number 1 <= x <= n into bucket index x - 1 in-place in linear amortized time.",
        "Risk": "Swapping nums[i] == nums[nums[i]-1] without checking for duplicate values causes an infinite while loop.",
        "Trade": "Cyclic sort mutates the input array but achieves the hard O(n) time and O(1) space constraints.",
        "Try": "Trace nums=[3, 4, -1, 1]: 3 swaps to idx 2 -> [-1, 4, 3, 1]; 4 swaps to idx 3 -> [-1, 1, 3, 4]; 1 swaps to idx 0 -> [1, -1, 3, 4]; missing is idx 1 (value 2).",
        "worked_case": "nums=[7,8,9,11,12]. None are in range [1, 5], so no swaps occur. First loop ends. Second loop inspects idx 0: nums[0]=7 != 1. Returns 1 immediately.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you solve this if modifying the input array is strictly prohibited?",
                "A": "If mutating is forbidden, you must use an O(n) space hash set or bitset, or accept an O(n log n) sorting copy."
            }
        ]
    },
    {
        "Q": "How do you find the majority element that appears more than n // 2 times in linear time and O(1) space?",
        "A": "**Direct answer:** Majority Element (LeetCode 169) finds the element that appears more than $\\lfloor n / 2 \\rfloor$ times in an array. The optimal solution uses the Boyer-Moore Voting Algorithm, which tracks a candidate element and a vote counter in a single linear pass with $O(1)$ memory.\n\n```python\ndef majority_element(nums: list[int]) -> int:\n    candidate = 0\n    count = 0\n    for num in nums:\n        if count == 0:\n            candidate = num\n        count += 1 if num == candidate else -1\n    return candidate\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`, scanning each element once.\n- **Space Complexity:** $O(1)$ auxiliary space because it only maintains two scalar variables (`candidate` and `count`).\n\n**Algorithmic mechanics and edge cases:**\nThe intuition is pairing up differing elements and canceling them out. Because the majority element occurs strictly more than $n / 2$ times, even if every other element cancels out a majority instance, at least one majority element will remain uncanceled. When `count` reaches 0, we select the current number as the new candidate. Edge cases include single-element arrays `[1]`, arrays where all elements are identical, and alternating sequences.",
        "Why": "Boyer-Moore voting pairs up distinct elements for cancellation, guaranteeing the majority element survives.",
        "Risk": "Boyer-Moore assumes a majority element is guaranteed to exist; if not guaranteed, a second verification pass is required.",
        "Trade": "Eliminating the hash table dictionary tally reduces auxiliary memory from O(n) to strict O(1).",
        "Try": "Trace nums=[2, 2, 1, 1, 1, 2, 2]: observe candidate changes between 2 and 1 as count increments and decrements, terminating at candidate=2.",
        "worked_case": "nums=[3,2,3]. i=0: count=0 -> cand=3, count=1. i=1: num=2 != 3 -> count=0. i=2: count=0 -> cand=3, count=1. Loop terminates, returns candidate 3.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you find all elements that appear more than n // 3 times (Majority Element II)?",
                "A": "Extend Boyer-Moore to maintain two candidates and two counters, since at most two elements can appear > n // 3 times."
            }
        ]
    },
    {
        "Q": "How do you find the contiguous subarray with the largest product in Python?",
        "A": "**Direct answer:** Maximum Product Subarray (LeetCode 152) finds the contiguous subarray within an array that has the largest product. The optimal solution uses dynamic programming tracking both the maximum and minimum product ending at the current position, because multiplying a negative number by a negative minimum produces a positive maximum.\n\n```python\ndef max_product(nums: list[int]) -> int:\n    if not nums:\n        return 0\n    max_so_far = nums[0]\n    min_so_far = nums[0]\n    global_max = nums[0]\n    for i in range(1, len(nums)):\n        curr = nums[i]\n        # If negative, max and min swap roles when multiplied\n        temp_max = max(curr, max_so_far * curr, min_so_far * curr)\n        min_so_far = min(curr, max_so_far * curr, min_so_far * curr)\n        max_so_far = temp_max\n        global_max = max(global_max, max_so_far)\n    return global_max\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`, scanning through the array once.\n- **Space Complexity:** $O(1)$ auxiliary space because only running state variables are maintained.\n\n**Algorithmic mechanics and edge cases:**\nUnlike Kadane's algorithm for sum (where negative numbers only decrease the total), in multiplication, two negative numbers yield a positive result. Therefore, `min_so_far` captures a potentially large negative product that can flip to a large positive product upon encountering another negative number. Encountering a `0` resets both `max_so_far` and `min_so_far` to `0`. Edge cases include single negative numbers `[-2]`, arrays containing zeros `[0, 2]`, and alternating negative numbers `[-2, 3, -4] -> 24`.",
        "Why": "Tracking both running maximum and minimum products accounts for parity sign inversions caused by negative multipliers.",
        "Risk": "Failing to store temp_max causes min_so_far to use the newly updated max_so_far in the same iteration, producing incorrect results.",
        "Trade": "State compression reduces Kadane dynamic programming to three scalar variables in O(1) space.",
        "Try": "Test with nums=[2, 3, -2, 4]: max_so_far becomes 6, then -2 (min=-12), then 4 (min=-48) -> global_max remains 6.",
        "worked_case": "nums=[-2, 3, -4]. i=0: max=-2, min=-2, res=-2. i=1 (3): max=3, min=-6, res=3. i=2 (-4): max=max(-4, 3*-4, -6*-4)=24, min=min(-4, -12, 24)=-12, res=24. Returns 24.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "Can this be solved using two directional passes (left-to-right and right-to-left)?",
                "A": "Yes, computing running prefix products and suffix products (resetting to 1 on zero) finds the max product without min tracking."
            }
        ]
    },
    {
        "Q": "How do you merge two sorted arrays in-place from the back without shifting elements?",
        "A": "**Direct answer:** Merge Sorted Array (LeetCode 88) merges two sorted integer arrays `nums1` and `nums2` into `nums1` as one sorted array. `nums1` has size $m + n$ with trailing zeros. The optimal solution uses three pointers working backwards from the end of `nums1`, placing the largest remaining element at the back to avoid shifting elements.\n\n```python\ndef merge(nums1: list[int], m: int, nums2: list[int], n: int) -> None:\n    p1 = m - 1\n    p2 = n - 1\n    p = m + n - 1\n    while p1 >= 0 and p2 >= 0:\n        if nums1[p1] > nums2[p2]:\n            nums1[p] = nums1[p1]\n            p1 -= 1\n        else:\n            nums1[p] = nums2[p2]\n            p2 -= 1\n        p -= 1\n    # If nums2 still has elements, copy them\n    while p2 >= 0:\n        nums1[p] = nums2[p2]\n        p2 -= 1\n        p -= 1\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(m + n)$ because each element from `nums1` and `nums2` is placed in its final position exactly once.\n- **Space Complexity:** $O(1)$ auxiliary space because elements are written directly into the pre-allocated buffer at the end of `nums1`.\n\n**Algorithmic mechanics and edge cases:**\nMerging from the front requires shifting elements in `nums1` to the right, which incurs an $O(m \\cdot n)$ worst-case penalty. Merging from the back writes into unused trailing space (initially filled with zeros), guaranteeing that unread elements in `nums1` are never overwritten. If `p1` finishes first, remaining elements in `nums2` are copied over. If `p2` finishes first, `nums1`'s remaining elements are already in their sorted positions. Edge cases include $m = 0$, $n = 0$, and identical arrays.",
        "Why": "Filling backwards into the pre-allocated tail buffer avoids shifting elements in O(1) space.",
        "Risk": "Merging from the front overwrites valid elements in nums1 unless a copy array is allocated.",
        "Trade": "Backwards merging requires no auxiliary allocation and completes in a single linear pass.",
        "Try": "Merge nums1=[1, 2, 3, 0, 0, 0] (m=3) and nums2=[2, 5, 6] (n=3) from the back and verify the result [1, 2, 2, 3, 5, 6].",
        "worked_case": "nums1=[0], m=0, nums2=[1], n=1. p1=-1, p2=0, p=0. First loop skipped. Second loop copies nums2[0]=1 to nums1[0]. Result: nums1=[1].",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "Why is there no need for a while p1 >= 0 cleanup loop?",
                "A": "If p2 finishes first, all remaining elements in nums1 are already in their correct sorted positions at the front of the array."
            }
        ]
    },
    {
        "Q": "How do you group consecutive numbers into summary ranges in Python?",
        "A": "**Direct answer:** Summary Ranges (LeetCode 228) takes a sorted unique integer array `nums` and returns the smallest sorted list of ranges covering all numbers in the array. The optimal solution uses two pointers (`start` and `i`) scanning linearly to detect discontinuities where `nums[i] + 1 != nums[i + 1]`.\n\n```python\ndef summary_ranges(nums: list[int]) -> list[str]:\n    ranges: list[str] = []\n    if not nums:\n        return ranges\n    start = 0\n    for i in range(len(nums)):\n        # Check if at the end of the array or next number is non-consecutive\n        if i == len(nums) - 1 or nums[i] + 1 != nums[i + 1]:\n            if start == i:\n                ranges.append(str(nums[start]))\n            else:\n                ranges.append(f\"{nums[start]}->{nums[i]}\")\n            start = i + 1\n    return ranges\n```\n\n**Complexity analysis:**\n- **Time Complexity:** $O(n)$ where $n$ is the length of `nums`. A single pass iterates through the numbers.\n- **Space Complexity:** $O(1)$ auxiliary space (ignoring the output list of formatted range strings).\n\n**Algorithmic mechanics and edge cases:**\nBecause `nums` is sorted and elements are unique, a contiguous range extends as long as `nums[i + 1] == nums[i] + 1`. When this condition fails (or we reach the end of the array), the range closes. If `start == i`, a single isolated number is formatted as `\"a\"`; otherwise, an interval is formatted as `\"a->b\"`. Edge cases include empty list `[]`, single element `[0] -> [\"0\"]`, completely contiguous array `[1, 2, 3] -> [\"1->3\"]`, and array with no adjacent numbers `[1, 3, 5] -> [\"1\", \"3\", \"5\"]`.",
        "Why": "A linear scan comparing adjacent elements identifies sequence breaks in O(n) without auxiliary state.",
        "Risk": "Checking nums[i+1] without an i == len(nums) - 1 boundary check causes IndexError on the last element.",
        "Trade": "Formatted f-strings provide concise string representation with negligible memory overhead.",
        "Try": "Test with nums=[0, 1, 2, 4, 5, 7] and verify output ['0->2', '4->5', '7'].",
        "worked_case": "nums=[0, 2, 3, 4, 6, 8, 9]. i=0 (0): next is 2 (!=1) -> '0'. i=1 to 3 (2,3,4): break at 4 -> '2->4'. i=4 (6): break at 6 -> '6'. i=5 to 6 (8,9): end -> '8->9'.",
        "citations": ["https://docs.python.org/3/tutorial/datastructures.html", "https://docs.python.org/3/library/stdtypes.html"],
        "follow_ups": [
            {
                "Q": "How do you handle integer overflow if numbers can be close to 32-bit integer limits in C++?",
                "A": "In statically typed languages, write nums[i + 1] - nums[i] != 1 or cast to 64-bit int to avoid signed overflow on INT_MAX."
            }
        ]
    }
]

