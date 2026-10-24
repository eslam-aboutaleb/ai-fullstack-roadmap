"""Database Connection Capacity Sizing & Pool Exhaustion Prevention.

Calculates total concurrent connection demand across distributed web replicas,
multi-process application servers, connection pool overflows, and asynchronous
background workers, comparing total demand against database server capacity limits.
"""

from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class WebFleetTopology:
    num_replicas: int
    processes_per_replica: int  # Gunicorn / Uvicorn worker count
    pool_size_per_process: int
    max_overflow_per_process: int


@dataclass(frozen=True)
class WorkerFleetTopology:
    num_worker_nodes: int
    concurrency_per_worker: int


@dataclass(frozen=True)
class DatabaseServerConfig:
    max_connections: int
    reserved_superuser_connections: int = 3
    pgbouncer_enabled: bool = False
    pgbouncer_pool_size: int = 40


class ConnectionCapacityCalculator:
    """Evaluates database connection budget against infrastructure topology."""

    @staticmethod
    def calculate_peak_demand(
        web: WebFleetTopology, workers: WorkerFleetTopology
    ) -> Tuple[int, int]:
        """Returns (baseline_connections, peak_overflow_connections)."""
        total_web_processes = web.num_replicas * web.processes_per_replica
        baseline_web = total_web_processes * web.pool_size_per_process
        peak_web = total_web_processes * (web.pool_size_per_process + web.max_overflow_per_process)

        worker_connections = workers.num_worker_nodes * workers.concurrency_per_worker

        total_baseline = baseline_web + worker_connections
        total_peak = peak_web + worker_connections
        return total_baseline, total_peak

    @staticmethod
    def evaluate_capacity(
        db: DatabaseServerConfig, web: WebFleetTopology, workers: WorkerFleetTopology
    ) -> Dict[str, Any]:
        baseline, peak = ConnectionCapacityCalculator.calculate_peak_demand(web, workers)
        usable_db_connections = db.max_connections - db.reserved_superuser_connections

        # If PgBouncer transaction pooling is enabled, application connects to pooler,
        # which multiplexes all traffic across a fixed number of physical server connections.
        effective_physical_db_demand = (
            db.pgbouncer_pool_size if db.pgbouncer_enabled else peak
        )

        is_safe = effective_physical_db_demand <= usable_db_connections

        return {
            "baseline_demand": baseline,
            "peak_demand": peak,
            "usable_db_connections": usable_db_connections,
            "effective_physical_demand": effective_physical_db_demand,
            "is_safe_under_peak": is_safe,
            "pgbouncer_multiplexing": db.pgbouncer_enabled,
        }


def test_connection_capacity() -> None:
    # Scenario: 3 web pods, 2 worker processes per pod, pool=5, overflow=5 (10 max per process)
    # Plus 1 background Celery worker machine with concurrency 10
    web_fleet = WebFleetTopology(
        num_replicas=3,
        processes_per_replica=2,
        pool_size_per_process=5,
        max_overflow_per_process=5,
    )
    worker_fleet = WorkerFleetTopology(num_worker_nodes=1, concurrency_per_worker=10)

    # 1. Unpooled Direct Connection to small PostgreSQL instance (max_connections = 60)
    # Peak demand: (3 * 2 * 10) + 10 = 70 connections!
    db_direct = DatabaseServerConfig(max_connections=60, reserved_superuser_connections=3)
    res_direct = ConnectionCapacityCalculator.evaluate_capacity(db_direct, web_fleet, worker_fleet)

    assert res_direct["baseline_demand"] == 40  # (3*2*5) + 10
    assert res_direct["peak_demand"] == 70  # (3*2*10) + 10
    assert res_direct["usable_db_connections"] == 57  # 60 - 3
    # INVARIANT: Direct connection is UNSAFE because 70 > 57!
    assert res_direct["is_safe_under_peak"] is False

    # 2. Add PgBouncer in Transaction Pooling Mode (pool_size = 35)
    db_pooled = DatabaseServerConfig(
        max_connections=60,
        reserved_superuser_connections=3,
        pgbouncer_enabled=True,
        pgbouncer_pool_size=35,
    )
    res_pooled = ConnectionCapacityCalculator.evaluate_capacity(db_pooled, web_fleet, worker_fleet)

    # INVARIANT: Safe with PgBouncer because 35 <= 57
    assert res_pooled["effective_physical_demand"] == 35
    assert res_pooled["is_safe_under_peak"] is True

    print(
        f"Database connection capacity verified: peak_demand={res_direct['peak_demand']}, "
        f"direct_safe={res_direct['is_safe_under_peak']}, "
        f"pgbouncer_pooled_safe={res_pooled['is_safe_under_peak']}"
    )


if __name__ == "__main__":
    test_connection_capacity()
