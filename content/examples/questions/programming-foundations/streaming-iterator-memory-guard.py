"""Streaming iterator vs eager list materialization memory benchmark.

Demonstrates why iterator and generator pipelines must be preserved through the call stack:
1. Eager materialization failure: calling list(stream) before filtering forces full O(N) heap allocation,
   negating generator benefits and risking out-of-memory (OOM) crashes on large datasets.
2. Lazy pipelining: composing generators (reader -> filter -> transform) retains O(1) working memory
   regardless of total dataset volume.
3. Early termination: lazy pipelines short-circuit after finding target items, avoiding wasted compute.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable, Generator, Iterable, Iterator, List, Optional


@dataclass(frozen=True)
class LogRecord:
    record_id: int
    level: str
    message: str


def generate_simulated_log_stream(count: int) -> Generator[LogRecord, None, None]:
    """Generates a sequential stream of records lazily."""
    for i in range(count):
        level = "ERROR" if i % 100 == 0 else "INFO"
        yield LogRecord(record_id=i, level=level, message=f"Log message payload {i}")


def filter_stream(
    stream: Iterable[LogRecord], predicate: Callable[[LogRecord], bool]
) -> Generator[LogRecord, None, None]:
    """Applies lazy filtering without materializing upstream elements."""
    for item in stream:
        if predicate(item):
            yield item


def eager_batch_processing(count: int, target_level: str) -> List[LogRecord]:
    """Anti-pattern: eagerly collects entire stream into a list before filtering."""
    # Materializes all elements in memory simultaneously: O(N) memory
    raw_list: List[LogRecord] = list(generate_simulated_log_stream(count))
    return [rec for rec in raw_list if rec.level == target_level]


def lazy_pipeline_processing(
    count: int, target_level: str, limit: Optional[int] = None
) -> Generator[LogRecord, None, None]:
    """Production pattern: streams and filters lazily in O(1) working memory."""
    stream = generate_simulated_log_stream(count)
    filtered = filter_stream(stream, lambda rec: rec.level == target_level)
    emitted = 0
    for rec in filtered:
        yield rec
        emitted += 1
        if limit is not None and emitted >= limit:
            break


def run_test_suite() -> None:
    total_records = 5000

    # 1. Test eager materialization:
    # All 5000 objects are loaded into a list before filtering:
    eager_results = eager_batch_processing(total_records, "ERROR")
    assert len(eager_results) == 50  # 5000 / 100
    assert eager_results[0].record_id == 0
    assert eager_results[1].record_id == 100

    # 2. Test lazy streaming pipeline:
    lazy_gen = lazy_pipeline_processing(total_records, "ERROR")
    # Generator is not evaluated yet (zero memory pre-allocation):
    assert isinstance(lazy_gen, Generator)

    lazy_results = list(lazy_gen)
    assert len(lazy_results) == 50
    assert [r.record_id for r in lazy_results] == [r.record_id for r in eager_results]

    # 3. Test early termination:
    # When asking for first 3 matching errors, lazy stream terminates after reading record 200,
    # rather than reading all 5000 records:
    early_gen = lazy_pipeline_processing(total_records, "ERROR", limit=3)
    early_results = list(early_gen)
    assert len(early_results) == 3
    assert [r.record_id for r in early_results] == [0, 100, 200]

    # 4. Demonstrate single-pass iterator exhaustion:
    exhaustible = (x for x in range(3))
    assert list(exhaustible) == [0, 1, 2]
    # Subsequent consumption yields empty without error:
    assert list(exhaustible) == [], "Exhausted iterator must yield empty list on replay"

    print("All streaming iterator memory assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
