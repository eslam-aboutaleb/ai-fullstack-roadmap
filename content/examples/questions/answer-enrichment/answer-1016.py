import sqlite3
with sqlite3.connect(":memory:") as db:
    db.execute("CREATE TABLE records(id INTEGER PRIMARY KEY, revision INTEGER, value TEXT)")
    db.execute("INSERT INTO records VALUES (1, 5, 'old')")
    first = db.execute("UPDATE records SET revision=6, value='A' WHERE id=1 AND revision=5").rowcount
    stale = db.execute("UPDATE records SET revision=6, value='B' WHERE id=1 AND revision=5").rowcount
    current = db.execute("SELECT revision, value FROM records WHERE id=1").fetchone()
assert first == 1 and stale == 0 and current == (6, "A")
print("accepted=1; stale=0; current=(6, 'A')")
