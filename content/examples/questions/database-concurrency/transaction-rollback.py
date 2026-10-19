import sqlite3
with sqlite3.connect(':memory:') as db:
    db.execute('CREATE TABLE counter(n INTEGER)')
    db.execute('INSERT INTO counter VALUES (1)')
    db.commit()
    try:
        with db:
            db.execute('UPDATE counter SET n=2')
            raise RuntimeError('synthetic failure')
    except RuntimeError:
        pass
    print(db.execute('SELECT n FROM counter').fetchone()[0])
