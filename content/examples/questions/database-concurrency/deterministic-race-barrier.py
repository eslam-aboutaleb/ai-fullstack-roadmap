"""Demonstrate testing concurrent race conditions deterministically using thread synchronization barriers."""
from threading import Barrier, Thread

def test_synchronized_counter_race():
    """
    Using threading.Barrier guarantees that all threads arrive at the critical section simultaneously,
    eliminating arbitrary time.sleep() delays and making race conditions 100% reproducible.
    """
    barrier = Barrier(2)
    state = {"balance": 100}
    lost_update_occurred = False

    def unsafe_worker(worker_id):
        # 1. Thread reads state
        local_read = state["balance"]
        
        # 2. Synchronize both threads at the barrier release point:
        # Both threads wait here until both have reached this line.
        # Once both are ready, both execute the write at the exact same instant!
        barrier.wait()
        
        # 3. Thread writes back without locking:
        # Both threads write (100 - 40 = 60), resulting in a lost update ($40 lost)!
        state["balance"] = local_read - 40

    threads = [Thread(target=unsafe_worker, args=(1,)), Thread(target=unsafe_worker, args=(2,))]
    for t in threads: t.start()
    for t in threads: t.join()

    # If execution were serialized correctly, balance would be 100 - 40 - 40 = 20.
    # Because of the barrier-synchronized race, balance is 60!
    lost_update_occurred = (state["balance"] == 60)
    assert lost_update_occurred is True, "Barrier reproduced exact lost-update concurrency race"
    print(f"Deterministic barrier test verified: expected_serial=20, actual_race={state['balance']}, lost_update={lost_update_occurred}")

if __name__ == '__main__':
    test_synchronized_counter_race()

