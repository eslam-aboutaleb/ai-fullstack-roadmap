# /// script
# dependencies = []
# ///
"""
Incremental UTF-8 Byte Stream Decoding Across Arbitrary Network Chunk Boundaries.

Demonstrates:
1. TCP packet fragmentation splitting multibyte UTF-8 characters across chunk reads.
2. Naive decoding resulting in corrupted Unicode replacement characters.
3. Stateful codecs.getincrementaldecoder('utf-8') preserving partial byte sequences
   across every possible byte split offset.
"""

from __future__ import annotations

import codecs
from typing import List


def test_incremental_utf8_decoding() -> None:
    # Text containing 1-byte (ASCII), 2-byte (Latin/Cyrillic), 3-byte (Arabic/Chinese), and 4-byte (Emoji) characters
    sample_text = 'data: {"greeting": "مرحبا بالعالم", "icon": "🚀✨", "lang": "人工智能"}\n\n'
    raw_bytes = sample_text.encode("utf-8")
    total_len = len(raw_bytes)

    # 1. Demonstrate naive decoding failure when splitting inside a 4-byte emoji (🚀)
    # The emoji 🚀 is 4 bytes: 0xF0 0x9F 0x9A 0x80
    emoji_bytes = "🚀".encode("utf-8")
    split_index = raw_bytes.index(emoji_bytes) + 2  # Split directly in the middle of the emoji

    chunk_a = raw_bytes[:split_index]
    chunk_b = raw_bytes[split_index:]

    # Naive decode creates corruption (Unicode replacement char \ufffd)
    naive_a = chunk_a.decode("utf-8", errors="replace")
    assert "\ufffd" in naive_a, "Expected naive decode to corrupt split multibyte character"

    # 2. Stateful Incremental Decoder handles every single split boundary perfectly
    corruptions = 0
    for split in range(1, total_len):
        decoder = codecs.getincrementaldecoder("utf-8")()
        part1 = decoder.decode(raw_bytes[:split], final=False)
        part2 = decoder.decode(raw_bytes[split:], final=True)
        reassembled = part1 + part2

        if reassembled != sample_text or "\ufffd" in reassembled:
            corruptions += 1

    assert corruptions == 0, f"Found {corruptions} decoding errors across split points"
    all_byte_partitions_passed = True

    print(
        f"Incremental UTF-8 decoding verified: all_byte_partitions_passed={all_byte_partitions_passed}, "
        f"corruptions={corruptions}"
    )


def main() -> None:
    test_incremental_utf8_decoding()


if __name__ == "__main__":
    main()
