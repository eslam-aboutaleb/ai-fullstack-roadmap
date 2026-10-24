"""Business update and notification intent share a real SQLite transaction."""
import sqlite3
with sqlite3.connect(':memory:') as db:
    db.executescript("CREATE TABLE tasks (id INTEGER PRIMARY KEY, status TEXT); CREATE TABLE outbox (event_id TEXT PRIMARY KEY, task_id INTEGER); INSERT INTO tasks VALUES (1, 'pending');")
    try:
        with db:
            db.execute("UPDATE tasks SET status='approved' WHERE id=1")
            db.execute("INSERT INTO outbox VALUES ('event-1', 1)")
            raise ValueError('reject transition')
    except ValueError:
        pass
    assert db.execute('SELECT status FROM tasks').fetchone()[0] == 'pending'
    assert db.execute('SELECT count(*) FROM outbox').fetchone()[0] == 0
print('business change rolled back; notification intent rolled back')
