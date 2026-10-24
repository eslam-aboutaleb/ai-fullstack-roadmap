"""Decoupled Background Indexing & Distributed Singleton Ownership.

Demonstrates why compute-heavy document indexing must be decoupled from web serving
replicas. Prevents startup thundering herds by enforcing distributed leader election
and singleton batch indexing jobs.
"""

from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional, Set


@dataclass
class IndexingTask:
    dataset_version: str
    documents_count: int
    started_by_replica: Optional[str] = None
    completed: bool = False


class DistributedIndexJobCoordinator:
    """Coordinates singleton indexing execution using distributed lock simulation."""

    def __init__(self) -> None:
        self.active_lock_holder: Optional[str] = None
        self.completed_generations: Set[str] = set()
        self.redundant_work_prevented_count: int = 0
        self.executed_indexing_jobs: List[IndexingTask] = []

    def acquire_indexing_lock(self, replica_id: str, generation_id: str) -> bool:
        if generation_id in self.completed_generations:
            return False  # Already built!
        if self.active_lock_holder is None:
            self.active_lock_holder = replica_id
            return True
        self.redundant_work_prevented_count += 1
        return False  # Another worker holds the lock

    def release_indexing_lock(self, replica_id: str, generation_id: str) -> None:
        if self.active_lock_holder == replica_id:
            self.active_lock_holder = None
            self.completed_generations.add(generation_id)


def test_separate_indexing() -> None:
    coordinator = DistributedIndexJobCoordinator()

    # Scenario: 4 web replicas boot simultaneously in Kubernetes
    web_replicas = ["web_pod_01", "web_pod_02", "web_pod_03", "web_pod_04"]
    target_generation = "gen_docs_2026_q4"

    # Step 1: All 4 replicas attempt to run indexing at startup
    claimed_workers = []
    for pod in web_replicas:
        if coordinator.acquire_indexing_lock(pod, target_generation):
            claimed_workers.append(pod)

    # INVARIANT: Exactly ONE worker wins the distributed claim; 3 redundant jobs prevented!
    assert len(claimed_workers) == 1
    assert claimed_workers[0] == "web_pod_01"
    assert coordinator.redundant_work_prevented_count == 3

    # Step 2: The winning worker executes the heavy indexing job
    task = IndexingTask(dataset_version=target_generation, documents_count=50000, started_by_replica=claimed_workers[0])
    task.completed = True
    coordinator.executed_indexing_jobs.append(task)
    coordinator.release_indexing_lock(claimed_workers[0], target_generation)

    # Step 3: A late-booting 5th pod checks generation
    late_pod_acquired = coordinator.acquire_indexing_lock("web_pod_05", target_generation)
    assert late_pod_acquired is False
    assert target_generation in coordinator.completed_generations
    assert len(coordinator.executed_indexing_jobs) == 1

    print(
        f"Separate indexing verified: web_replicas={len(web_replicas)}, "
        f"executed_index_jobs={len(coordinator.executed_indexing_jobs)}, "
        f"redundant_jobs_prevented={coordinator.redundant_work_prevented_count}"
    )


if __name__ == "__main__":
    test_separate_indexing()
