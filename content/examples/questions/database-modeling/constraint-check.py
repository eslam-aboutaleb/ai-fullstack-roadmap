import sqlite3
with sqlite3.connect(':memory:') as db:
    db.execute('CREATE TABLE quota (remaining INTEGER CHECK(remaining >= 0))')
    try:
        db.execute('INSERT INTO quota VALUES (?)', (-1,))
    except sqlite3.IntegrityError:
        print('rejected')
