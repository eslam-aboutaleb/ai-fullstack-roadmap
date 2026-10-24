"""File ingestion memory amplification and streaming parser benchmark.

Demonstrates why in-memory data processing often consumes orders of magnitude more RAM
than the on-disk file size:
1. Object overhead & representation explosion: a 50 KB compressed JSON file expands upon decompression
   into raw bytes, then into Python Unicode strings (each carrying 48-80 bytes of PyObject header),
   then into dictionary hash tables (carrying bucket tables and hash caches).
2. Pipeline retention accumulation: retaining the compressed buffer, raw decompressed string,
   parsed AST dictionaries, and converted domain models simultaneously multiplies peak working memory.
3. Streaming mitigation: streaming line-by-line parsing processes and discards each record in O(1)
   working memory, avoiding multi-stage heap accumulation.
"""

from __future__ import annotations

import gzip
import io
import json
import sys
from dataclasses import dataclass
from typing import Generator, List, Tuple


@dataclass(frozen=True)
class LogEntry:
    entry_id: str
    timestamp: str
    message: str


def generate_compressed_json_lines(record_count: int) -> bytes:
    """Generates an in-memory gzipped JSON-lines byte buffer."""
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        for i in range(record_count):
            record = {
                "id": f"rec-{i:05d}",
                "timestamp": "2026-10-24T12:00:00Z",
                "message": f"Log payload status check for cluster node {i % 10}",
                "metadata": {"env": "prod", "shard": i % 4, "retry": False},
            }
            line = (json.dumps(record) + "\n").encode("utf-8")
            gz.write(line)
    return buf.getvalue()


def eager_ingestion_pipeline(compressed_data: bytes) -> Tuple[List[LogEntry], int]:
    """Anti-pattern: retains all intermediate stages simultaneously in memory.

    Stage 1: compressed_data (retained)
    Stage 2: decompressed_raw_bytes (retained)
    Stage 3: decoded_unicode_str (retained)
    Stage 4: parsed_dicts_list (retained)
    Stage 5: normalized_models (retained)
    """
    # Stage 2: Decompress
    raw_bytes = gzip.decompress(compressed_data)

    # Stage 3: Decode full string
    full_str = raw_bytes.decode("utf-8")

    # Stage 4: Parse entire document into list of dicts
    dict_list = [json.loads(line) for line in full_str.strip().split("\n")]

    # Stage 5: Convert into domain objects
    models = [
        LogEntry(entry_id=d["id"], timestamp=d["timestamp"], message=d["message"])
        for d in dict_list
    ]

    # Calculate approximate memory occupied by all concurrently retained stages:
    accumulated_bytes = (
        sys.getsizeof(compressed_data)
        + sys.getsizeof(raw_bytes)
        + sys.getsizeof(full_str)
        + sys.getsizeof(dict_list)
        + sum(sys.getsizeof(d) for d in dict_list)
        + sys.getsizeof(models)
        + sum(sys.getsizeof(m) for m in models)
    )

    return models, accumulated_bytes


def streaming_ingestion_pipeline(
    compressed_data: bytes,
) -> Generator[LogEntry, None, None]:
    """Production pattern: streams decompressed lines one by one without accumulating."""
    bio = io.BytesIO(compressed_data)
    with gzip.GzipFile(fileobj=bio, mode="rb") as gz:
        for raw_line in gz:
            record_dict = json.loads(raw_line.decode("utf-8"))
            yield LogEntry(
                entry_id=record_dict["id"],
                timestamp=record_dict["timestamp"],
                message=record_dict["message"],
            )


def run_test_suite() -> None:
    record_count = 1000
    compressed_bytes = generate_compressed_json_lines(record_count)
    compressed_size = len(compressed_bytes)

    # 1. Run eager ingestion:
    eager_models, accumulated_memory = eager_ingestion_pipeline(compressed_bytes)
    assert len(eager_models) == record_count

    # Verify memory amplification:
    # Retaining all 5 intermediate pipeline representations causes severe amplification
    # compared to the compressed file size on disk:
    amplification_ratio = accumulated_memory / compressed_size
    assert amplification_ratio > 10.0, (
        f"Expected memory amplification > 10x, observed {amplification_ratio:.1f}x"
    )

    # 2. Run streaming ingestion:
    stream_gen = streaming_ingestion_pipeline(compressed_bytes)
    stream_models = list(stream_gen)
    assert len(stream_models) == record_count

    # Exact parity of extracted data:
    assert stream_models[0] == eager_models[0]
    assert stream_models[-1] == eager_models[-1]

    print("All file ingestion memory amplification assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
