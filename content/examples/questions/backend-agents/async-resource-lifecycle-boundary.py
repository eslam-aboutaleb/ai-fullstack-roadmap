# /// script
# dependencies = []
# ///
"""
Async Resource Lifecycle Boundary and Database Transaction Hygiene.

Demonstrates:
1. Two-phase database transaction boundaries: never holding an open database
   transaction or checked-out pool connection across an external LLM await.
2. Event loop protection: offloading synchronous blocking / CPU-bound parsing
   to a bounded thread pool executor without freezing concurrent coroutines.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import time
from typing import AsyncGenerator, Dict, List


class DatabaseConnectionPool:
    """Simulated database connection pool with active lease tracking."""

    def __init__(self, capacity: int = 5) -> None:
        self.capacity = capacity
        self.active_count = 0
        self.max_observed = 0

    def acquire(self) -> str:
        if self.active_count >= self.capacity:
            raise RuntimeError("Database connection pool exhausted!")
        self.active_count += 1
        if self.active_count > self.max_observed:
            self.max_observed = self.active_count
        return f"conn_{self.active_count}"

    def release(self, conn_id: str) -> None:
        self.active_count = max(0, self.active_count - 1)


@asynccontextmanager
async def database_session(pool: DatabaseConnectionPool) -> AsyncGenerator[Dict[str, Any], None]:
    """Scoped, short-lived database transaction context manager."""
    conn_id = pool.acquire()
    session = {"conn_id": conn_id, "status": "active"}
    try:
        await asyncio.sleep(0.005)  # Simulate 5ms DB query
        yield session
    finally:
        session["status"] = "released"
        pool.release(conn_id)


def cpu_bound_token_extraction(raw_corpus: str) -> List[str]:
    """Simulates CPU-heavy document parsing, regex cleaning, and tokenization."""
    # Compute intensive transformation
    tokens = []
    for word in raw_corpus.split():
        clean = "".join(ch for ch in word if ch.isalnum()).lower()
        if len(clean) > 3:
            tokens.append(clean)
    return tokens


async def simulate_llm_inference(prompt: str, pool: DatabaseConnectionPool) -> str:
    """Simulates external LLM API streaming call over network."""
    # INVARIANT: Database connection pool MUST be zero while awaiting external provider
    if pool.active_count > 0:
        raise AssertionError("CRITICAL ANTI-PATTERN: Database connection held during LLM call!")
    await asyncio.sleep(0.02)  # Simulate 20ms network inference wait
    return f"Synthesized answer for '{prompt}'"


async def monitor_event_loop_lag(interval: float = 0.005, iterations: int = 4) -> float:
    """Measures event loop responsiveness while worker tasks execute."""
    max_lag = 0.0
    for _ in range(iterations):
        t0 = time.perf_counter()
        await asyncio.sleep(interval)
        lag = (time.perf_counter() - t0 - interval) * 1000.0  # in ms
        if lag > max_lag:
            max_lag = lag
    return max_lag


async def process_agent_request(
    task_id: str,
    prompt: str,
    raw_document: str,
    pool: DatabaseConnectionPool,
    thread_pool: ThreadPoolExecutor,
) -> Dict[str, Any]:
    """Correct Pattern: Two-Phase Transaction with decoupled LLM inference."""
    loop = asyncio.get_running_loop()

    # --- Phase 1: Short-lived DB Transaction to read user permissions & context ---
    async with database_session(pool) as session:
        assert session["status"] == "active"
        tenant_context = {"task_id": task_id, "tier": "enterprise"}
    # Session is completely closed and connection returned to pool here
    assert pool.active_count == 0, "Connection not returned after Phase 1"

    # --- Phase 2: CPU-Bound parsing offloaded to bounded thread executor ---
    parsed_tokens = await loop.run_in_executor(
        thread_pool,
        cpu_bound_token_extraction,
        raw_document,
    )

    # --- Phase 3: External Model Inference (Zero DB connections held) ---
    llm_output = await simulate_llm_inference(prompt, pool)
    assert pool.active_count == 0, "Connection was acquired during LLM call"

    # --- Phase 4: Short-lived DB Transaction to persist audit log & result ---
    async with database_session(pool) as session:
        assert session["status"] == "active"
        persisted_record = {
            "task_id": task_id,
            "tokens_extracted": len(parsed_tokens),
            "output": llm_output,
        }
    assert pool.active_count == 0, "Connection not returned after Phase 4"

    return persisted_record


async def main_async() -> None:
    pool = DatabaseConnectionPool(capacity=5)
    thread_pool = ThreadPoolExecutor(max_workers=2)

    sample_doc = "Enterprise multi-agent architectures require bounded threadpools and strict session scopes. " * 50
    db_held_during_llm = False

    try:
        # Run agent request concurrent with an event loop latency monitor
        agent_task = asyncio.create_task(
            process_agent_request("tsk_boundary_01", "Summarize policy", sample_doc, pool, thread_pool)
        )
        lag_task = asyncio.create_task(monitor_event_loop_lag())

        result, max_lag_ms = await asyncio.gather(agent_task, lag_task)

        assert "Synthesized answer" in result["output"]
        assert pool.active_count == 0
        assert pool.max_observed <= 1, f"Expected at most 1 connection, saw {pool.max_observed}"

        # Assert event loop remained responsive (< 50ms lag)
        assert max_lag_ms < 50.0, f"Event loop lag too high: {max_lag_ms:.2f}ms"

        print(
            f"Resource boundary verified: db_held_during_llm={db_held_during_llm}, "
            f"max_active_connections={pool.max_observed}, loop_lag_ms<50"
        )
    finally:
        thread_pool.shutdown(wait=True)


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

