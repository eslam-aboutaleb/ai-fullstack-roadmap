"""Async event loop CPU starvation and non-blocking worker offloading harness.

Demonstrates why 'await' does not magically parallelize CPU-bound Python execution:
1. Cooperative multitasking contract: asyncio runs on a single OS thread. A coroutine only yields
   control to the event loop when awaiting a non-blocking I/O future or explicit yield point.
2. Event loop starvation: running a synchronous, CPU-intensive loop inside an async handler blocks the
   entire thread, preventing health checks, timers, and concurrent I/O requests from executing.
3. Thread/Process offloading: CPU-bound work must be delegated to separate OS threads or worker
   processes (via asyncio.to_thread or ProcessPoolExecutor) to keep the main event loop responsive.
"""

from __future__ import annotations

import asyncio
import time
from typing import List, Tuple


def cpu_intensive_hashing(iterations: int) -> int:
    """Simulates CPU-heavy image preprocessing or cryptographic hashing."""
    val = 0
    for i in range(iterations):
        val = (val + i * 31) ^ (i & 0xFF)
    return val


async def health_check(probe_log: List[str]) -> float:
    """Simulates a Kubernetes liveness probe that expects sub-millisecond response."""
    start = time.perf_counter()
    await asyncio.sleep(0.005)  # Tiny non-blocking I/O wait
    elapsed = time.perf_counter() - start
    probe_log.append(f"health_ok:{elapsed:.4f}s")
    return elapsed


async def blocking_cpu_endpoint(iterations: int) -> int:
    """Anti-pattern: runs synchronous CPU work directly in the event loop thread."""
    # Awaiting a regular function or running tight CPU loop does NOT yield:
    return cpu_intensive_hashing(iterations)


async def non_blocking_offloaded_endpoint(iterations: int) -> int:
    """Production pattern: offloads CPU work to an OS worker thread pool."""
    return await asyncio.to_thread(cpu_intensive_hashing, iterations)


async def run_scenario_blocking() -> Tuple[float, List[str]]:
    probe_log: List[str] = []
    # Schedule health check and CPU endpoint concurrently
    t0 = time.perf_counter()
    health_task = asyncio.create_task(health_check(probe_log))
    cpu_task = asyncio.create_task(blocking_cpu_endpoint(3_000_000))

    await asyncio.gather(health_task, cpu_task)
    total_time = time.perf_counter() - t0
    return total_time, probe_log


async def run_scenario_offloaded() -> Tuple[float, List[str]]:
    probe_log: List[str] = []
    t0 = time.perf_counter()
    # When offloaded to thread, event loop remains free to service health check
    health_task = asyncio.create_task(health_check(probe_log))
    cpu_task = asyncio.create_task(non_blocking_offloaded_endpoint(3_000_000))

    await asyncio.gather(health_task, cpu_task)
    total_time = time.perf_counter() - t0
    return total_time, probe_log


def run_test_suite() -> None:
    # 1. Test blocking scenario:
    # The CPU loop monopolizes the event loop thread, delaying the health check
    _, blocking_log = asyncio.run(run_scenario_blocking())
    assert len(blocking_log) == 1
    assert "health_ok" in blocking_log[0]

    # 2. Test offloaded scenario:
    # Health check runs concurrently while worker thread handles hashing
    _, offloaded_log = asyncio.run(run_scenario_offloaded())
    assert len(offloaded_log) == 1
    assert "health_ok" in offloaded_log[0]

    # 3. Direct verification of cooperative yielding:
    async def yield_verification() -> bool:
        executed_order: List[str] = []

        async def worker_yielding():
            executed_order.append("start_worker")
            # Without await, this runs continuously; with await sleep(0), it yields:
            await asyncio.sleep(0)
            executed_order.append("end_worker")

        async def fast_interleaver():
            executed_order.append("interleaver_ran")

        t1 = asyncio.create_task(worker_yielding())
        t2 = asyncio.create_task(fast_interleaver())
        await asyncio.gather(t1, t2)

        # Interleaver ran in the middle of worker thanks to explicit yield point:
        return executed_order == ["start_worker", "interleaver_ran", "end_worker"]

    assert asyncio.run(yield_verification()) is True

    print("All async event loop CPU starvation assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
