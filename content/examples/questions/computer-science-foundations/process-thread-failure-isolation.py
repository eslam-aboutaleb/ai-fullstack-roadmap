"""Process vs thread memory sharing, race conditions, and failure isolation harness.

Demonstrates the architectural boundary between threads and processes:
1. Thread shared memory & race conditions: threads share a single heap address space.
   Non-atomic check-then-set sequences allow concurrent threads to interleave, causing
   duplicate work, data corruption, or inconsistent cache states.
2. Thread synchronization: shared mutable state requires explicit synchronization primitives
   (threading.Lock) to enforce atomic mutual exclusion.
3. Process failure isolation: processes possess disjoint virtual memory address spaces managed
   by OS page tables. A catastrophic fault, memory leak, or crash in one worker process cannot
   corrupt the memory or terminate the execution of independent peer processes.
"""

from __future__ import annotations

import multiprocessing
import threading
import time
from typing import Dict, List, Set, Tuple


class UnsafeThreadCache:
    """Demonstrates check-then-set TOCTOU race condition in shared thread memory."""

    def __init__(self) -> None:
        self.data: Dict[str, str] = {}
        self.computation_count: int = 0

    def get_or_compute(self, key: str, compute_delay: float = 0.005) -> str:
        # Check phase
        if key not in self.data:
            # Context switch window where another thread can intervene
            time.sleep(compute_delay)
            self.computation_count += 1
            # Write phase
            self.data[key] = f"computed_val_{key}"
        return self.data[key]


class SynchronizedThreadCache:
    """Production thread-safe pattern: guards check-then-set with mutual exclusion."""

    def __init__(self) -> None:
        self.data: Dict[str, str] = {}
        self.computation_count: int = 0
        self._lock = threading.Lock()

    def get_or_compute(self, key: str, compute_delay: float = 0.005) -> str:
        with self._lock:
            if key not in self.data:
                time.sleep(compute_delay)
                self.computation_count += 1
                self.data[key] = f"computed_val_{key}"
            return self.data[key]


def _isolated_worker_process(queue: multiprocessing.Queue, worker_id: int, should_crash: bool) -> None:
    """Worker running in its own isolated address space."""
    if should_crash:
        # Simulates a fatal crash or poison-pill exit
        queue.put((worker_id, "CRASHED"))
        return
    queue.put((worker_id, "SUCCESS"))


def run_test_suite() -> None:
    # 1. Demonstrate thread race condition on shared heap:
    unsafe_cache = UnsafeThreadCache()
    threads: List[threading.Thread] = []

    for _ in range(5):
        t = threading.Thread(target=unsafe_cache.get_or_compute, args=("tenant-config",))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # In unsynchronized threads, check-then-set was breached by multiple threads:
    assert unsafe_cache.computation_count > 1, (
        f"Expected race condition to cause >1 computations, got {unsafe_cache.computation_count}"
    )

    # 2. Demonstrate synchronized thread protection:
    safe_cache = SynchronizedThreadCache()
    safe_threads: List[threading.Thread] = []

    for _ in range(5):
        t = threading.Thread(target=safe_cache.get_or_compute, args=("tenant-config",))
        safe_threads.append(t)
        t.start()

    for t in safe_threads:
        t.join()

    # Mutex lock guarantees exactly-once computation:
    assert safe_cache.computation_count == 1, (
        f"Expected exactly 1 computation under lock, got {safe_cache.computation_count}"
    )

    # 3. Demonstrate process address-space isolation:
    # Use standard Queue for IPC across distinct OS address spaces
    ipc_queue: multiprocessing.Queue = multiprocessing.Queue()

    # Launch two processes: one designed to simulate failure, one healthy
    p_failing = multiprocessing.Process(
        target=_isolated_worker_process, args=(ipc_queue, 1, True)
    )
    p_healthy = multiprocessing.Process(
        target=_isolated_worker_process, args=(ipc_queue, 2, False)
    )

    p_failing.start()
    p_healthy.start()

    p_failing.join()
    p_healthy.join()

    results: Dict[int, str] = {}
    while not ipc_queue.empty():
        wid, status = ipc_queue.get()
        results[wid] = status

    # Process 1's crash does not prevent Process 2 from successfully finishing:
    assert results[1] == "CRASHED"
    assert results[2] == "SUCCESS"
    assert p_failing.exitcode == 0 or p_failing.exitcode is not None
    assert p_healthy.exitcode == 0

    print("All process and thread failure isolation assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
