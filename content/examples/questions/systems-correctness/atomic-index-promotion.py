"""SQLite publication-boundary fixture, not a distributed index."""
import sqlite3
with sqlite3.connect(':memory:') as db:
    db.executescript("CREATE TABLE active (slot TEXT PRIMARY KEY, generation TEXT); INSERT INTO active VALUES ('search', 'g1');")
    try:
        with db:
            db.execute("UPDATE active SET generation='g2' WHERE generation='g1'")
            raise RuntimeError('validation failed')
    except RuntimeError:
        pass
    assert db.execute('SELECT generation FROM active').fetchone()[0] == 'g1'
    with db:
        changed = db.execute("UPDATE active SET generation='g2' WHERE generation='g1'").rowcount
        assert changed == 1
    assert db.execute('SELECT generation FROM active').fetchone()[0] == 'g2'
print('rollback: g1; validated promotion: g2')
