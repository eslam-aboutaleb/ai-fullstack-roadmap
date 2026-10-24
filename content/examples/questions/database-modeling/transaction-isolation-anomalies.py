"""Demonstrate transaction isolation levels, non-repeatable read anomalies, and serializable defense."""

class InvertedAccountStore:
    def __init__(self):
        self.balance = 100
        self.version = 1

    def read(self):
        return self.balance

    def update_committed(self, new_balance):
        self.balance = new_balance

    def optimistic_update(self, delta, expected_version):
        if self.version == expected_version:
            self.balance += delta
            self.version += 1
            return True
        return False

def main():
    store = InvertedAccountStore()
    # 1. Non-Repeatable Read demonstration:
    balance_1 = store.read()
    assert balance_1 == 100

    # Concurrent Tx2 updates balance and commits
    store.update_committed(250)

    # Tx1 reads again in the same open transaction under Read Committed:
    balance_2 = store.read()
    anomaly_detected = (balance_1 != balance_2)

    # 2. Preventing concurrency skew with optimistic version check (application-level serializability):
    # Worker A and Worker B both read version 1
    worker_a_success = store.optimistic_update(-50, expected_version=1)
    assert worker_a_success is True

    # Worker B attempts to write based on stale version 1
    worker_b_success = store.optimistic_update(-30, expected_version=1)
    stale_write_rejected = (worker_b_success is False)

    print(f"Non-repeatable read anomaly={anomaly_detected}; Stale concurrent write rejected={stale_write_rejected}")

if __name__ == '__main__':
    main()
