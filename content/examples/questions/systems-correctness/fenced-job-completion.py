"""SQLite attempt fencing, including stale and duplicate completion."""
import sqlite3
with sqlite3.connect(':memory:') as db:
    db.executescript("CREATE TABLE jobs (id INTEGER PRIMARY KEY, attempt INTEGER, owner TEXT, state TEXT); INSERT INTO jobs VALUES (1, 5, 'B', 'processing');")
    def complete(owner, attempt):
        with db:
            return db.execute("UPDATE jobs SET state='completed' WHERE id=1 AND owner=? AND attempt=? AND state='processing'", (owner, attempt)).rowcount == 1
    assert complete('A', 4) is False
    assert complete('B', 5) is True
    assert complete('B', 5) is False
print('stale rejected; current completed; duplicate ignored')
