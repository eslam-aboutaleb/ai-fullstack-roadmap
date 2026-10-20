"""Python 3.11+: two local SQLite connections contend for one unique slot."""
from contextlib import closing
import queue
import sqlite3
import tempfile
import threading
from pathlib import Path


def run_race():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'reservations.db'
        with closing(sqlite3.connect(path)) as db:
            db.execute('CREATE TABLE reservations (slot TEXT PRIMARY KEY, owner TEXT)')
        barrier = threading.Barrier(2, timeout=5)
        outcomes = queue.Queue()

        def reserve(owner):
            # Each thread owns its connection; :memory: would create separate DBs.
            try:
                with closing(sqlite3.connect(path, timeout=5)) as connection:
                    barrier.wait()
                    try:
                        connection.execute('INSERT INTO reservations VALUES (?, ?)', ('slot-1', owner))
                        connection.commit()
                        outcomes.put('reserved')
                    except sqlite3.IntegrityError:
                        outcomes.put('conflict')
            except Exception as error:
                outcomes.put(type(error).__name__)

        workers = [threading.Thread(target=reserve, args=(owner,)) for owner in ('alice', 'bob')]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(timeout=10)
            assert not worker.is_alive(), 'Worker did not finish'
        result = sorted(outcomes.get_nowait() for _ in workers)
        with closing(sqlite3.connect(path)) as db:
            count = db.execute('SELECT count(*) FROM reservations').fetchone()[0]
        assert result == ['conflict', 'reserved'], result
        assert count == 1, count
        return result, count


if __name__ == '__main__':
    result, count = run_race()
    print(f'outcomes={result}; rows={count}')
