"""Real SQLite revision and schema guards for migration replay."""
import sqlite3
with sqlite3.connect(':memory:') as db:
    db.executescript("CREATE TABLE records (id INTEGER PRIMARY KEY, schema_v INTEGER, revision INTEGER, value TEXT); INSERT INTO records VALUES (1, 1, 4, 'legacy');")
    def migrate(expected_revision):
        with db:
            return db.execute("UPDATE records SET schema_v=2, revision=revision+1, value='converted' WHERE id=1 AND schema_v=1 AND revision=?", (expected_revision,)).rowcount
    assert migrate(4) == 1
    assert migrate(4) == 0
    assert db.execute('SELECT schema_v, revision, value FROM records').fetchone() == (2, 5, 'converted')
print('migration committed once; replay and stale revision rejected')
