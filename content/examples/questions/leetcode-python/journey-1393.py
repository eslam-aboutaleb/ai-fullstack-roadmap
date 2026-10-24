"""Demonstrate longest substring without repeating characters using a sliding window."""


def length_of_longest_substring(s: str) -> int:
    last_seen: dict[str, int] = {}
    max_len = 0
    left = 0
    for right, char in enumerate(s):
        if char in last_seen and last_seen[char] >= left:
            left = last_seen[char] + 1
        last_seen[char] = right
        max_len = max(max_len, right - left + 1)
    return max_len


assert length_of_longest_substring("abcabcbb") == 3
assert length_of_longest_substring("bbbbb") == 1
assert length_of_longest_substring("pwwkew") == 3

print("Sliding window longest substring verified successfully.")

