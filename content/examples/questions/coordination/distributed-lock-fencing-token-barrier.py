"""
distributed-lock-fencing-token-barrier.py

Production-grade Distributed Locking and Monotonic Fencing Token Barrier Suite.
Demonstrates:
1. The classic Martin Kleppmann distributed lock failure:
   - Worker A acquires a leased lock (token 33) and enters a GC pause / network delay.
   - Lease expires; Worker B acquires the lock with an incremented token (token 34) and writes to storage.
   - Worker A wakes up and attempts to commit its stale write.
2. Receiver-side Fencing Token Enforcement:
   - The storage layer acts as the authoritative gatekeeper, rejecting any write where
     incoming_token <= current_storage_token.
3. Verifying that time-bounded leases alone do not prevent split-brain writes without fencing tokens.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import time


class StaleFencingTokenError(Exception):
    """Raised when an operation presents an obsolete or superseded fencing token."""
    pass


@dataclass
class LockLease:
    lock_name: str
    owner_id: str
    fencing_token: int
    expires_at_monotonic: float

    def is_expired(self, current_time: float) -> bool:
        return current_time >= self.expires_at_monotonic


class DistributedLockCoordinator:
    """Simulates a distributed lock manager (e.g. Redis Redlock or ZooKeeper/etcd)."""
    def __init__(self):
        self.current_token = 30
        self.active_locks: Dict[str, LockLease] = {}

    def acquire_lock(self, lock_name: str, owner_id: str, ttl_seconds: float, current_time: float) -> LockLease:
        active = self.active_locks.get(lock_name)
        if active and not active.is_expired(current_time):
            raise TimeoutError(f"Lock '{lock_name}' is currently held by '{active.owner_id}'")

        self.current_token += 1
        lease = LockLease(
            lock_name=lock_name,
            owner_id=owner_id,
            fencing_token=self.current_token,
            expires_at_monotonic=current_time + ttl_seconds
        )
        self.active_locks[lock_name] = lease
        return lease


class AuthoritativeStorageEngine:
    """
    Simulates the database or object storage service.
    Enforces atomic conditional writes using monotonic fencing tokens:
    UPDATE record SET val = :val, fencing_token = :token WHERE id = :id AND fencing_token < :token
    """
    def __init__(self):
        self.records: Dict[str, Dict[str, Any]] = {}

    def write_record(self, record_id: str, payload: str, fencing_token: int, writer_id: str) -> Dict[str, Any]:
        existing = self.records.get(record_id)
        if existing:
            current_token = existing["fencing_token"]
            if fencing_token <= current_token:
                raise StaleFencingTokenError(
                    f"Write REJECTED for writer '{writer_id}'. Presented token {fencing_token} "
                    f"is not greater than current storage token {current_token}. "
                    f"State was already committed by a newer owner!"
                )

        record = {
            "record_id": record_id,
            "payload": payload,
            "fencing_token": fencing_token,
            "last_writer": writer_id
        }
        self.records[record_id] = record
        return record


def main() -> None:
    print("=== Testing Distributed Lock Lease & Fencing Token Barrier ===")

    coordinator = DistributedLockCoordinator()
    storage = AuthoritativeStorageEngine()

    simulated_clock = 100.0  # Monotonic seconds

    # 1. Worker A acquires the lock for 2.0 seconds
    lease_a = coordinator.acquire_lock(
        lock_name="doc_sync_lock",
        owner_id="worker_A",
        ttl_seconds=2.0,
        current_time=simulated_clock
    )
    print(f"Worker A acquired lock: token={lease_a.fencing_token}, expires_at={lease_a.expires_at_monotonic:.1f}")
    assert lease_a.fencing_token == 31

    # 2. Worker A experiences a severe garbage collection pause or network freeze (3.0 seconds)
    print("Simulating 3.0s GC pause for Worker A (lease expires during pause)...")
    simulated_clock += 3.0
    assert lease_a.is_expired(simulated_clock) is True

    # 3. Worker B acquires the expired lock at t=103.0s with incremented fencing token
    lease_b = coordinator.acquire_lock(
        lock_name="doc_sync_lock",
        owner_id="worker_B",
        ttl_seconds=2.0,
        current_time=simulated_clock
    )
    print(f"Worker B acquired lock: token={lease_b.fencing_token}, expires_at={lease_b.expires_at_monotonic:.1f}")
    assert lease_b.fencing_token == 32

    # 4. Worker B successfully commits its write to storage
    commit_b = storage.write_record(
        record_id="doc_42",
        payload="Payload written by Worker B (Version 2.0)",
        fencing_token=lease_b.fencing_token,
        writer_id="worker_B"
    )
    print("Worker B committed:", commit_b)
    assert commit_b["fencing_token"] == 32
    assert commit_b["last_writer"] == "worker_B"

    # 5. Worker A wakes up from the pause!
    # Worker A thinks it still holds the lock because its local thread was paused.
    # It attempts to write its stale payload with token 31.
    print("\nWorker A wakes up and attempts to commit with stale token 31...")
    try:
        storage.write_record(
            record_id="doc_42",
            payload="Stale payload from Worker A (Version 1.0)",
            fencing_token=lease_a.fencing_token,
            writer_id="worker_A"
        )
        assert False, "Storage should have rejected Worker A's stale write"
    except StaleFencingTokenError as e:
        print("Successfully intercepted stale write at storage boundary:")
        print(" ", str(e))
        assert "Write REJECTED" in str(e)

    # 6. Verify final storage state remains untainted by Worker A
    final_record = storage.records["doc_42"]
    assert final_record["payload"] == "Payload written by Worker B (Version 2.0)"
    assert final_record["fencing_token"] == 32
    assert final_record["last_writer"] == "worker_B"

    print("\nAll distributed lock fencing token invariants verified successfully.")


if __name__ == "__main__":
    main()
