"""Real conditional SQL update; sequential schedule, not a concurrency benchmark."""
import sqlite3
with sqlite3.connect(':memory:') as db:
    db.executescript("CREATE TABLE jobs (id INTEGER PRIMARY KEY, state TEXT, owner TEXT); INSERT INTO jobs VALUES (7, 'pending', NULL);")
    def claim(owner):
        with db:
            return db.execute("UPDATE jobs SET state='processing', owner=? WHERE id=7 AND state='pending'", (owner,)).rowcount == 1
    assert claim('A') is True
    assert claim('B') is False
    assert db.execute('SELECT owner FROM jobs').fetchone()[0] == 'A'
print('A owns job; B must skip')
