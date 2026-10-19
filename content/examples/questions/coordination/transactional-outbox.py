import sqlite3
with sqlite3.connect(':memory:') as db:
    db.executescript('CREATE TABLE requests(id TEXT PRIMARY KEY); CREATE TABLE outbox(id TEXT PRIMARY KEY);')
    with db:
        db.execute('INSERT INTO requests VALUES (?)', ('op1',))
        db.execute('INSERT INTO outbox VALUES (?)', ('op1',))
    print(db.execute('SELECT count(*) FROM requests').fetchone()[0],
          db.execute('SELECT count(*) FROM outbox').fetchone()[0])
