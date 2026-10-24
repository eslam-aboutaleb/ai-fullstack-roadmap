# /// script
# dependencies = []
# ///
"""
Disentangling WebSocket Transport Heartbeats (Ping/Pong) from Application Task Progress.

Demonstrates:
1. Transport-level liveness: WebSocket ping/pong checks if the TCP connection
   and socket are responsive.
2. Application-level task progress: tracks whether the AI agent model loop
   is actively emitting progress or is deadlocked/stalled.
3. Proves that a healthy transport ping does NOT mean an agent task is healthy.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class ConnectionHealthStatus:
    is_socket_alive: bool
    is_task_progressing: bool
    is_task_stalled: bool


class DuplexHealthMonitor:
    def __init__(self, transport_timeout_seconds: float = 10.0, task_stall_seconds: float = 30.0) -> None:
        self.transport_timeout = transport_timeout_seconds
        self.task_stall_timeout = task_stall_seconds

    def evaluate_health(
        self,
        current_time: float,
        last_pong_time: float,
        last_progress_time: float,
    ) -> ConnectionHealthStatus:
        # Transport check: has client responded to ping within 10 seconds?
        socket_alive = (current_time - last_pong_time) < self.transport_timeout

        # Application task check: has the agent produced output within 30 seconds?
        task_stalled = (current_time - last_progress_time) > self.task_stall_timeout
        task_progressing = not task_stalled

        return ConnectionHealthStatus(
            is_socket_alive=socket_alive,
            is_task_progressing=task_progressing,
            is_task_stalled=task_stalled,
        )


def main() -> None:
    monitor = DuplexHealthMonitor(transport_timeout_seconds=10.0, task_stall_seconds=30.0)
    now = 100.0

    # --- Scenario 1: Transport is healthy, but Agent Task is STALLED ---
    # Client sent pong 1 second ago (transport is completely healthy)
    # BUT agent has emitted zero tokens for 45 seconds (model deadlock or hung tool)
    last_pong_healthy = 99.0
    last_progress_stalled = 55.0  # 45s ago

    status_1 = monitor.evaluate_health(
        current_time=now,
        last_pong_time=last_pong_healthy,
        last_progress_time=last_progress_stalled,
    )

    # Invariant: Transport ping/pong succeeds, but task is flagged STALLED!
    assert status_1.is_socket_alive is True, "Transport should be alive"
    assert status_1.is_task_stalled is True, "Agent task should be detected as stalled"
    connection_alive = status_1.is_socket_alive
    task_stalled = status_1.is_task_stalled

    # --- Scenario 2: Transport Connection Dropped ---
    # No pong for 25 seconds (exceeds 10s transport timeout)
    last_pong_dead = 75.0
    status_2 = monitor.evaluate_health(
        current_time=now,
        last_pong_time=last_pong_dead,
        last_progress_time=now - 5.0,
    )
    assert status_2.is_socket_alive is False, "Transport should be detected as dead"
    transport_timeout_detected = not status_2.is_socket_alive

    print(
        f"Heartbeat vs task monitor verified: connection_alive={connection_alive}, "
        f"task_stalled={task_stalled}, transport_timeout_detected={transport_timeout_detected}"
    )


if __name__ == "__main__":
    main()
