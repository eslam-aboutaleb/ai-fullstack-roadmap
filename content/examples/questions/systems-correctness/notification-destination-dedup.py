"""Destination-side feed deduplication under a lost-ack replay."""
import sqlite3
with sqlite3.connect(':memory:') as db:
    db.execute('CREATE TABLE feed (event_id TEXT PRIMARY KEY, message TEXT)')
    def deliver(event_id, message):
        with db:
            return db.execute('INSERT INTO feed VALUES (?, ?) ON CONFLICT(event_id) DO NOTHING', (event_id, message)).rowcount
    assert deliver('event-7', 'Task approved') == 1
    # The destination committed, but imagine the outbox acknowledgment was lost.
    assert deliver('event-7', 'Task approved') == 0
    assert db.execute('SELECT count(*) FROM feed').fetchone()[0] == 1
print('lost acknowledgment replay: one feed item')
