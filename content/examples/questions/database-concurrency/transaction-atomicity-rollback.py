"""Demonstrate ACID transaction atomicity, multi-table coordination, and rollback integrity."""
import sqlite3

def test_transaction_rollback():
    with sqlite3.connect(':memory:') as db:
        cursor = db.cursor()
        cursor.execute("CREATE TABLE ledger (account_id TEXT PRIMARY KEY, balance INT CHECK(balance >= 0))")
        cursor.execute("CREATE TABLE audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT)")
        
        cursor.execute("INSERT INTO ledger VALUES ('A', 100), ('B', 50)")
        db.commit()

        # Transaction 1: Successful atomic transfer
        with db:
            cursor.execute("UPDATE ledger SET balance = balance - 40 WHERE account_id = 'A'")
            cursor.execute("UPDATE ledger SET balance = balance + 40 WHERE account_id = 'B'")
            cursor.execute("INSERT INTO audit_log (message) VALUES ('Transferred 40 from A to B')")

        balances = dict(cursor.execute("SELECT account_id, balance FROM ledger").fetchall())
        assert balances == {'A': 60, 'B': 90}

        # Transaction 2: Failure mid-stream (overdraft violating CHECK constraint on account A)
        rollback_occurred = False
        try:
            with db:
                # Debit A of $100 -> balance becomes 60 - 100 = -40 (Violates CHECK constraint!)
                cursor.execute("UPDATE ledger SET balance = balance - 100 WHERE account_id = 'A'")
                cursor.execute("UPDATE ledger SET balance = balance + 100 WHERE account_id = 'B'")
                cursor.execute("INSERT INTO audit_log (message) VALUES ('Transferred 100 from A to B')")
        except sqlite3.IntegrityError:
            rollback_occurred = True

        assert rollback_occurred is True
        # Verify that ledger AND audit_log were completely rolled back with zero dirty state:
        final_balances = dict(cursor.execute("SELECT account_id, balance FROM ledger").fetchall())
        audit_count = cursor.execute("SELECT count(*) FROM audit_log").fetchone()[0]

        assert final_balances == {'A': 60, 'B': 90}, "Ledger untouched by failed transaction"
        assert audit_count == 1, "Audit log contains only the first successful transaction"
        print(f"Transaction atomicity verified: rollback={rollback_occurred}, balances={final_balances}")

if __name__ == '__main__':
    test_transaction_rollback()
