import sqlite3
with sqlite3.connect(':memory:') as db:
    db.execute('CREATE TABLE records(owner TEXT)')
    db.execute('INSERT INTO records VALUES (?)', ('A',))
    attack = "A' OR 1=1 --"
    print(db.execute('SELECT owner FROM records WHERE owner=?', (attack,)).fetchall())
