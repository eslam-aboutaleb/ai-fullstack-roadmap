"""Demonstrate bidirectional two-pointer pair finding and in-place duplicate removal."""


def two_sum_sorted(nums: list[int], target: int) -> list[int]:
    left, right = 0, len(nums) - 1
    while left < right:
        curr = nums[left] + nums[right]
        if curr == target:
            return [left, right]
        if curr < target:
            left += 1
        else:
            right -= 1
    return []


assert two_sum_sorted([2, 7, 11, 15], 9) == [0, 1]


def remove_duplicates(nums: list[int]) -> int:
    if not nums:
        return 0
    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[read - 1]:
            nums[write] = nums[read]
            write += 1
    return write


arr = [1, 1, 2, 2, 3]
count = remove_duplicates(arr)
assert count == 3
assert arr[:3] == [1, 2, 3]

print("Two-pointer sorted pair and in-place duplicate removal verified successfully.")

