"""Demonstrate prefix sum hash map subarray sum lookup with negative values."""


def subarray_sum_equals_k(nums: list[int], k: int) -> int:
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


assert subarray_sum_equals_k([1, -1, 1, 1, 1, -1], 2) == 6

print("Prefix sum hash map subarray lookup verified successfully.")
