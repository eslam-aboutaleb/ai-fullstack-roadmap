"""Demonstrate transaction isolation levels, non-repeatable read anomalies, and serializable defense."""
import sqlite3
import tempfile
import os

db_path = os.path.join(tempfile.gettempdir(), 'isolation_demo.db')
if os.path.exists(db_path):
    os.remove(db_path)

try:
    # Setup initial state
    init_conn = sqlite3.connect(db_path)
    init_conn.execute("CREATE TABLE account (id INT PRIMARY KEY, balance INT)")
    init_conn.execute("INSERT INTO account VALUES (1, 100)")
    init_conn.commit()
    init_conn.close()

    # Session 1 starts reading under READ COMMITTED behavior
    conn1 = sqlite3.connect(db_path, isolation_level=None)
    conn2 = sqlite3.connect(db_path, isolation_level=None)

    # 1. Non-Repeatable Read demonstration:
    # Tx1 reads balance = 100
    conn1.execute("BEGIN")
    balance_1 = conn1.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    assert balance_1 == 100

    # Concurrent Tx2 updates balance and commits
    conn2.execute("BEGIN IMMEDIATE")
    conn2.execute("UPDATE account SET balance = 250 WHERE id = 1")
    conn2.execute("COMMIT")

    # Tx1 reads again in the same open transaction:
    # In Read Committed, Tx1 sees the new committed value (250), violating repeatable read invariant!
    balance_2 = conn1.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    conn1.execute("COMMIT")

    anomaly_detected = (balance_1 != balance_2)
    
    # 2. Preventing concurrency skew with optimistic version check (application-level serializability):
    conn3 = sqlite3.connect(db_path)
    conn3.execute("ALTER TABLE account ADD COLUMN version INT DEFAULT 1")
    conn3.commit()

    # Worker A and Worker B both read version 1
    # Worker A writes and increments version
    cursor = conn3.cursor()
    cursor.execute("UPDATE account SET balance = balance - 50, version = version + 1 WHERE id = 1 AND version = 1")
    assert cursor.rowcount == 1, "Worker A successfully updated"

    # Worker B attempts to write based on stale version 1
    cursor.execute("UPDATE account SET balance = balance - 30, version = version + 1 WHERE id = 1 AND version = 1")
    stale_write_rejected = (cursor.rowcount == 0)

    print(f"Non-repeatable read anomaly={anomaly_detected}; Stale concurrent write rejected={stale_write_rejected}")
finally:
    if os.path.exists(db_path):
        os.remove(db_path)

