"""Distributed deadline budget propagation vs independent step timeouts.

Demonstrates why independent per-call timeouts cause cascading resource waste:
1. Timeout vs deadline distinction: a timeout bounds a single isolated I/O call; a deadline
   bounds the absolute end-to-end time budget for an entire multi-step operation.
2. The cascading waste pathology: if 4 sequential steps (DNS, TLS, DB query, LLM call) each have
   a 3-second timeout, the backend can execute for 12 seconds. If the client gateway gives up after 5 seconds,
   the backend continues burning expensive database and GPU compute on an abandoned request.
3. Propagated deadline context: propagating an absolute deadline timestamp (e.g. gRPC deadline or
   HTTP trace headers) ensures that each downstream step receives only the remaining time budget,
   and execution short-circuits immediately once the budget is exhausted.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional, Tuple


class DeadlineExceededError(TimeoutError):
    """Raised when an operation's cumulative deadline has expired."""
    pass


@dataclass(frozen=True)
class PipelineStep:
    name: str
    duration_seconds: float
    is_expensive_compute: bool


def execute_with_independent_timeouts(
    steps: List[PipelineStep], step_timeout: float
) -> Tuple[float, List[str], int]:
    """Anti-pattern: resets a fresh timeout for every step."""
    executed_steps: List[str] = []
    expensive_calls_made = 0
    t0 = time.perf_counter()

    for step in steps:
        # Each step allows up to step_timeout independently
        if step.duration_seconds > step_timeout:
            executed_steps.append(f"{step.name}:TIMEOUT")
            break
        # Simulate step execution
        time.sleep(step.duration_seconds)
        executed_steps.append(step.name)
        if step.is_expensive_compute:
            expensive_calls_made += 1

    total_elapsed = time.perf_counter() - t0
    return total_elapsed, executed_steps, expensive_calls_made


def execute_with_propagated_deadline(
    steps: List[PipelineStep], total_budget_seconds: float
) -> Tuple[float, List[str], int]:
    """Production pattern: calculates remaining budget before each step and short-circuits."""
    executed_steps: List[str] = []
    expensive_calls_made = 0
    start_time = time.perf_counter()
    deadline = start_time + total_budget_seconds

    for step in steps:
        now = time.perf_counter()
        remaining_budget = deadline - now

        if remaining_budget <= 0:
            executed_steps.append(f"{step.name}:SKIPPED_DEADLINE_EXCEEDED")
            break

        # Bound current step timeout by remaining budget
        effective_timeout = min(step.duration_seconds, remaining_budget)
        if step.duration_seconds > remaining_budget:
            # Step cannot complete within remaining time; abort before wasting compute
            time.sleep(effective_timeout)
            executed_steps.append(f"{step.name}:DEADLINE_EXCEEDED")
            break

        time.sleep(step.duration_seconds)
        executed_steps.append(step.name)
        if step.is_expensive_compute:
            expensive_calls_made += 1

    total_elapsed = time.perf_counter() - start_time
    return total_elapsed, executed_steps, expensive_calls_made


def run_test_suite() -> None:
    # 4-stage sequential pipeline:
    # Step 1: DNS Lookup (0.015s)
    # Step 2: DB User Fetch (0.025s)
    # Step 3: Expensive Embedding Generation (0.030s)
    # Step 4: Expensive LLM Completion (0.040s)
    pipeline = [
        PipelineStep("dns_resolve", 0.015, False),
        PipelineStep("db_fetch", 0.025, False),
        PipelineStep("embedding_calc", 0.030, True),
        PipelineStep("llm_generate", 0.040, True),
    ]

    client_gateway_budget = 0.050  # Client will abandon connection after 50ms

    # 1. Independent step timeouts (each allows 0.035s):
    # Total duration = 0.015 + 0.025 + 0.030 = 0.070s -> runs into step 3 and 4!
    elapsed_indep, steps_indep, expensive_indep = execute_with_independent_timeouts(
        pipeline, step_timeout=0.035
    )

    # Independent timeouts exceeded client gateway budget and wasted compute on step 3 & 4:
    assert elapsed_indep > client_gateway_budget
    assert expensive_indep >= 1, "Wasted expensive compute on client-abandoned request!"

    # 2. Propagated deadline architecture:
    # Caps total pipeline duration to client_gateway_budget (0.050s):
    elapsed_deadline, steps_deadline, expensive_deadline = execute_with_propagated_deadline(
        pipeline, total_budget_seconds=client_gateway_budget
    )

    # Deadline architecture bounds total time:
    assert elapsed_deadline <= client_gateway_budget + 0.010  # within margin of timer sleep
    # Notice: step 1 (0.015s) and step 2 (0.025s) completed (total 0.040s).
    # Step 3 needed 0.030s but remaining budget was only 0.010s, so it aborted immediately:
    assert any("DEADLINE_EXCEEDED" in s for s in steps_deadline)
    # Crucial: Step 4 was never even attempted (0 expensive compute wasted!):
    assert expensive_deadline == 0, "Propagated deadline prevented all wasted expensive compute!"

    print("All deadline budget propagation assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
