# /// script
# dependencies = []
# ///
"""
Cross-Process Durable Task State Store with Optimistic Concurrency and Heartbeats.

Contrasts process-local state (which fails across replicas and restarts) with
a shared durable task store featuring:
1. Multi-replica cross-node visibility.
2. Optimistic locking via version counters.
3. Heartbeat lease renewal and zombie task reconciliation for crashed workers.
"""

from __future__ import annotations

import sqlite3
import time
from typing import Any, Dict, Optional


class ProcessLocalRegistry:
    """Anti-Pattern: In-memory dictionary state tied to a single process heap."""

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        self.state: Dict[str, Dict[str, Any]] = {}

    def save(self, task_id: str, data: Dict[str, Any]) -> None:
        self.state[task_id] = data

    def get(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.state.get(task_id)

    def restart(self) -> None:
        """Simulates container pod restart or crash."""
        self.state.clear()


class DurableSharedStore:
    """Production Pattern: Shared relational repository with optimistic locking and heartbeats."""

    def __init__(self, db_conn: sqlite3.Connection) -> None:
        self.conn = db_conn
        self._init_schema()

    def _init_schema(self) -> None:
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_tasks (
                    task_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    progress REAL NOT NULL DEFAULT 0.0,
                    version INTEGER NOT NULL DEFAULT 1,
                    worker_id TEXT,
                    heartbeat_at REAL NOT NULL,
                    result_payload TEXT
                )
                """
            )

    def create_task(self, task_id: str, tenant_id: str) -> None:
        now = time.time()
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO agent_tasks (task_id, tenant_id, state, progress, version, heartbeat_at)
                VALUES (?, ?, 'PENDING', 0.0, 1, ?)
                """,
                (task_id, tenant_id, now),
            )

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT task_id, tenant_id, state, progress, version, worker_id, heartbeat_at
            FROM agent_tasks WHERE task_id = ?
            """,
            (task_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "task_id": row[0],
            "tenant_id": row[1],
            "state": row[2],
            "progress": row[3],
            "version": row[4],
            "worker_id": row[5],
            "heartbeat_at": row[6],
        }

    def claim_task(self, task_id: str, worker_id: str) -> bool:
        now = time.time()
        with self.conn:
            cursor = self.conn.execute(
                """
                UPDATE agent_tasks
                SET state = 'RUNNING', worker_id = ?, heartbeat_at = ?, version = version + 1
                WHERE task_id = ? AND state = 'PENDING'
                """,
                (worker_id, now, task_id),
            )
            return cursor.rowcount == 1

    def update_progress_optimistic(
        self,
        task_id: str,
        expected_version: int,
        progress: float,
        worker_id: str,
    ) -> bool:
        """Updates progress guarded by optimistic version check and worker lease."""
        now = time.time()
        with self.conn:
            cursor = self.conn.execute(
                """
                UPDATE agent_tasks
                SET progress = ?, version = version + 1, heartbeat_at = ?
                WHERE task_id = ? AND version = ? AND worker_id = ?
                """,
                (progress, now, task_id, expected_version, worker_id),
            )
            return cursor.rowcount == 1

    def reconcile_zombie_tasks(self, timeout_seconds: float) -> int:
        """Sweeper job: recovers tasks whose workers crashed (missing heartbeats)."""
        cutoff = time.time() - timeout_seconds
        with self.conn:
            cursor = self.conn.execute(
                """
                UPDATE agent_tasks
                SET state = 'FAILED_RETRYABLE',
                    result_payload = 'Worker heartbeat expired. Task marked for reconciliation.'
                WHERE state = 'RUNNING' AND heartbeat_at < ?
                """,
                (cutoff,),
            )
            return cursor.rowcount


def main() -> None:
    # --- Part 1: Failure Mode of Process-Local State ---
    node_a = ProcessLocalRegistry(node_id="pod-node-alpha")
    node_b = ProcessLocalRegistry(node_id="pod-node-bravo")

    task_id = "tsk-local-101"
    node_a.save(task_id, {"status": "RUNNING", "progress": 0.4})

    # Cross-node poll to Node B fails because memory is unshared
    local_cross_node_found = node_b.get(task_id) is not None
    assert not local_cross_node_found, "Process-local state should not be visible on Replica B"

    # Pod restart wipes Node A memory
    node_a.restart()
    assert node_a.get(task_id) is None, "Pod restart should wipe process-local state"

    # --- Part 2: Shared Durable Store Resilience ---
    # Shared database connection simulating durable Postgres/Redis cluster
    shared_db = sqlite3.connect(":memory:", check_same_thread=False)
    store = DurableSharedStore(shared_db)

    durable_task_id = "tsk-durable-202"
    store.create_task(durable_task_id, tenant_id="tenant-core")

    # Node B queries Node A's newly created task from shared store
    node_b_view = store.get_task(durable_task_id)
    assert node_b_view is not None, "Durable task must be visible across all replicas"
    assert node_b_view["state"] == "PENDING"
    assert node_b_view["version"] == 1
    durable_cross_node_found = True

    # Worker on Node A claims the task
    worker_alpha = "worker-pod-alpha-proc-1"
    claimed = store.claim_task(durable_task_id, worker_id=worker_alpha)
    assert claimed, "Task claim should succeed"

    current = store.get_task(durable_task_id)
    assert current["state"] == "RUNNING"
    assert current["version"] == 2

    # Optimistic concurrency: update progress with correct version
    updated = store.update_progress_optimistic(
        task_id=durable_task_id,
        expected_version=2,
        progress=0.5,
        worker_id=worker_alpha,
    )
    assert updated, "Optimistic update should succeed with matching version"

    # Stale update collision: attempting update with old version 2 fails
    stale_update = store.update_progress_optimistic(
        task_id=durable_task_id,
        expected_version=2,
        progress=0.75,
        worker_id=worker_alpha,
    )
    assert not stale_update, "Stale optimistic update should be rejected"

    # --- Part 3: Zombie Worker Crash and Heartbeat Reconciliation ---
    # Simulate worker crash: heartbeat ceases for 15 seconds
    # Manually backdate heartbeat_at to simulate missed lease renewals
    with shared_db:
        shared_db.execute(
            "UPDATE agent_tasks SET heartbeat_at = ? WHERE task_id = ?",
            (time.time() - 30.0, durable_task_id),
        )

    # Sweeper runs with a 10-second timeout threshold
    reconciled_count = store.reconcile_zombie_tasks(timeout_seconds=10.0)
    assert reconciled_count == 1, "Zombie task should be detected and reconciled"

    reconciled_task = store.get_task(durable_task_id)
    assert reconciled_task["state"] == "FAILED_RETRYABLE"
    zombie_reconciled = True

    print(
        f"Distributed task store verified: local_cross_node_found={local_cross_node_found}, "
        f"durable_cross_node_found={durable_cross_node_found}, zombie_reconciled={zombie_reconciled}"
    )


if __name__ == "__main__":
    main()
