"""Demonstrate job queue selection vs durable ownership lease and crash recovery."""
import time

class DistributedTaskQueue:
    def __init__(self):
        self.tasks = {
            "task_1": {
                "id": "task_1",
                "status": "queued",
                "payload": "reindex_vectors",
                "owner_id": None,
                "lease_expires_at": 0,
                "attempts": 0
            }
        }

    def claim_task(self, worker_id, current_time, lease_duration=30):
        """
        Durable Lease Claim:
        A task is eligible if its status is 'queued', OR if its lease has expired without completion
        (indicating the previous worker node died or timed out).
        """
        task = self.tasks.get("task_1")
        if task is None:
            return None

        is_available = (task["status"] == "queued") or (
            task["status"] == "processing" and task["lease_expires_at"] < current_time
        )

        if not is_available:
            return None # Locked by an active worker

        # Atomically lease the task:
        task["status"] = "processing"
        task["owner_id"] = worker_id
        task["lease_expires_at"] = current_time + lease_duration
        task["attempts"] += 1
        return task

    def complete_task(self, task_id, worker_id, current_time):
        """Complete task only if caller is still the authoritative leaseholder."""
        task = self.tasks.get(task_id)
        if not task or task["owner_id"] != worker_id or task["lease_expires_at"] < current_time:
            raise RuntimeError("Lease lost or expired! Cannot commit task completion.")
        task["status"] = "completed"
        task["owner_id"] = None

queue = DistributedTaskQueue()

# Worker A claims task at t=100 with 30s lease (expires at t=130)
task_a = queue.claim_task("worker_node_A", current_time=100, lease_duration=30)
assert task_a is not None and task_a["owner_id"] == "worker_node_A"

# Worker B attempts to claim at t=110 while Worker A is still working -> rejected
task_b = queue.claim_task("worker_node_B", current_time=110)
assert task_b is None, "Worker B rejected because lease is active"

# Worker A crashes without completing. At t=135, lease has expired.
# Worker C polls and recovers the abandoned task:
task_c = queue.claim_task("worker_node_C", current_time=135, lease_duration=30)
assert task_c is not None and task_c["owner_id"] == "worker_node_C"
assert task_c["attempts"] == 2

queue.complete_task("task_1", "worker_node_C", current_time=140)
assert queue.tasks["task_1"]["status"] == "completed"

print(f"Task lease recovery verified: claimed by {task_c['owner_id']}, attempts={task_c['attempts']}")

