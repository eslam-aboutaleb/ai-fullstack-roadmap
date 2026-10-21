import sqlite3
with sqlite3.connect(":memory:") as db:
    db.executescript("""
    CREATE TABLE customers(id INTEGER PRIMARY KEY);
    CREATE TABLE orders(customer_id INTEGER, status TEXT);
    INSERT INTO customers VALUES (1), (2);
    INSERT INTO orders VALUES (1, 'paid');
    """)
    wrong = db.execute("SELECT c.id FROM customers c LEFT JOIN orders o ON c.id=o.customer_id WHERE o.status='paid' ORDER BY c.id").fetchall()
    right = db.execute("SELECT c.id FROM customers c LEFT JOIN orders o ON c.id=o.customer_id AND o.status='paid' ORDER BY c.id").fetchall()
assert wrong == [(1,)]
assert right == [(1,), (2,)]
print("WHERE keeps [1]; ON keeps [1, 2]")
