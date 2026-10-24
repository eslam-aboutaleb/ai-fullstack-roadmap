"""Asyncio task cancellation resource cleanup and queue join deadlock guard.

Demonstrates why resource management must account for asyncio.CancelledError:
1. Cancellation control flow: when a task is cancelled, an asyncio.CancelledError is injected at the
   current await point. Normal code execution terminates immediately unless caught or shielded.
2. Queue join deadlock pathology: if a worker receives an item from an asyncio.Queue and gets cancelled
   before calling queue.task_done(), the queue's internal unfinished task counter never reaches zero.
   Any subsequent await queue.join() deadlocks permanently.
3. Defensive invariant: all stateful resources (queue acknowledgments, mutex locks, open file handles,
   database transactions) must be protected by try/finally blocks or context managers.
"""

from __future__ import annotations

import asyncio
from typing import List, Optional


async def buggy_worker(queue: asyncio.Queue[str], processed: List[str]) -> None:
    """Anti-pattern: task_done() is only called on the happy path."""
    item = await queue.get()
    # Simulated long network call that gets cancelled mid-stream:
    await asyncio.sleep(1.0)
    processed.append(item)
    queue.task_done()  # NEVER REACHED if cancelled during sleep!


async def resilient_worker(
    queue: asyncio.Queue[str], processed: List[str], failure_log: List[str]
) -> None:
    """Production pattern: guarantees task_done() executes even under cancellation."""
    item = await queue.get()
    try:
        await asyncio.sleep(1.0)
        processed.append(item)
    except asyncio.CancelledError:
        failure_log.append(f"task_cancelled:{item}")
        raise  # Re-raise CancelledError to respect structured cancellation
    finally:
        # Crucial invariant: task_done must execute on normal completion, exception, AND cancellation:
        queue.task_done()


async def test_cancellation_deadlock() -> None:
    queue: asyncio.Queue[str] = asyncio.Queue()
    await queue.put("job-101")
    processed: List[str] = []

    # Launch buggy worker
    task = asyncio.create_task(buggy_worker(queue, processed))
    await asyncio.sleep(0.01)  # Allow worker to dequeue item

    # Cancel the worker while it is asleep
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    # Notice: item was dequeued, but unfinished_tasks remains 1!
    assert queue._unfinished_tasks == 1, "Queue must still have 1 unfinished task due to missed task_done"

    # Verifying deadlock risk: queue.join() would hang forever here:
    join_deadlocked = False
    try:
        await asyncio.wait_for(queue.join(), timeout=0.05)
    except asyncio.TimeoutError:
        join_deadlocked = True

    assert join_deadlocked is True, "Buggy worker caused permanent queue.join() deadlock!"


async def test_resilient_cleanup() -> None:
    queue: asyncio.Queue[str] = asyncio.Queue()
    await queue.put("job-202")
    processed: List[str] = []
    failure_log: List[str] = []

    # Launch resilient worker
    task = asyncio.create_task(resilient_worker(queue, processed, failure_log))
    await asyncio.sleep(0.01)  # Allow worker to dequeue

    # Cancel the worker
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    # Verify task_done() was executed in finally block:
    assert queue._unfinished_tasks == 0, "Resilient worker must decrement unfinished_tasks to 0"
    assert failure_log == ["task_cancelled:job-202"]

    # queue.join() unblocks instantly without timing out:
    await asyncio.wait_for(queue.join(), timeout=0.1)


def run_test_suite() -> None:
    asyncio.run(test_cancellation_deadlock())
    asyncio.run(test_resilient_cleanup())
    print("All cancellation resource cleanup assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
