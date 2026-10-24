"""Demonstrate optimal O(n) Two Sum hash map complement lookup."""


def two_sum(nums: list[int], target: int) -> list[int]:
    seen: dict[int, int] = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []


nums = [2, 7, 11, 15]
target = 9
pair = two_sum(nums, target)
assert pair == [0, 1]
assert nums[pair[0]] + nums[pair[1]] == target
print(f"Two Sum verified: pair={pair}, values={[nums[p] for p in pair]}, target={target}")

