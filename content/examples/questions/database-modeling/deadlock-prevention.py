"""Demonstrate database deadlocks caused by asymmetric lock ordering and prevention via canonical ordering."""
import threading
import time

lock_a = threading.Lock()
lock_b = threading.Lock()

execution_log = []

def transfer_with_canonical_ordering(account_first, account_second, amount, worker_name):
    """Prevent deadlock by acquiring locks in global lexicographical order regardless of transfer direction."""
    # Enforce canonical lock ordering:
    first_lock, second_lock = (lock_a, lock_b) if account_first < account_second else (lock_b, lock_a)
    
    with first_lock:
        execution_log.append(f"{worker_name} acquired first lock")
        time.sleep(0.01) # Simulate transactional I/O
        with second_lock:
            execution_log.append(f"{worker_name} acquired second lock; transferred {amount}")

# Worker 1 transfers from A to B: wants lock A then B
t1 = threading.Thread(target=transfer_with_canonical_ordering, args=('A', 'B', 100, 'Tx1'))
# Worker 2 transfers from B to A: without canonical ordering, it would lock B then A causing deadlock!
# With canonical ordering, Worker 2 sorts locks and also attempts lock A first, waiting safely behind Tx1.
t2 = threading.Thread(target=transfer_with_canonical_ordering, args=('B', 'A', 50, 'Tx2'))

t1.start()
t2.start()
t1.join(timeout=2.0)
t2.join(timeout=2.0)

assert not t1.is_alive() and not t2.is_alive(), "Deadlock occurred! Threads timed out"
print(f"Deadlock prevented: {len(execution_log)} operations completed safely")

