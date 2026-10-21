"""A data edit changes record revision, not its schema version."""
import sqlite3
with sqlite3.connect(':memory:') as db:
    db.executescript("CREATE TABLE records (id INTEGER PRIMARY KEY, schema_version INTEGER, revision INTEGER, label TEXT); INSERT INTO records VALUES (1, 2, 7, 'old');")
    def edit(expected, value):
        with db:
            return db.execute('UPDATE records SET label=?, revision=revision+1 WHERE id=1 AND revision=?', (value, expected)).rowcount
    assert edit(7, 'first') == 1
    assert edit(7, 'stale second') == 0
    assert db.execute('SELECT schema_version, revision, label FROM records').fetchone() == (2, 8, 'first')
print('schema stays 2; revision becomes 8; stale edit rejected')
