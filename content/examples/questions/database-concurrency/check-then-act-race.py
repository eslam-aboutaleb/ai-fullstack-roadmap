"""Demonstrate Time-of-Check to Time-of-Use (TOCTOU) lost update races and atomic conditional write defense."""
import sqlite3
import threading

def run_lost_update_simulation():
    with sqlite3.connect(':memory:') as db:
        cursor = db.cursor()
        cursor.execute("CREATE TABLE accounts (id INT PRIMARY KEY, balance INT)")
        cursor.execute("INSERT INTO accounts VALUES (1, 100)")
        db.commit()

        # PITFALL: Check-Then-Act Race
        # Client reads balance ($100), performs application check (100 >= 70), then writes new balance ($30).
        # If two clients execute this concurrently:
        # Both read $100.
        # Both calculate 100 - 70 = $30.
        # Both write $30. Total deducted is $140, but balance reflects only one withdrawal!
        
        # DEFENSE: Atomic Conditional Update (Compare-and-Swap / Database-Level Check)
        # Instead of writing a precomputed value, execute atomic decrement with conditional predicate:
        query = "UPDATE accounts SET balance = balance - 70 WHERE id = 1 AND balance >= 70"
        
        # Tx 1 executes atomic withdrawal:
        cursor.execute(query)
        tx1_success = (cursor.rowcount == 1)
        
        # Tx 2 attempts atomic withdrawal immediately after:
        cursor.execute(query)
        tx2_success = (cursor.rowcount == 1) # Fails because balance is now 30, failing the 'balance >= 70' predicate!
        
        final_balance = cursor.execute("SELECT balance FROM accounts WHERE id = 1").fetchone()[0]
        
        assert tx1_success is True
        assert tx2_success is False, "Atomic condition rejected overdraft"
        assert final_balance == 30, f"Expected balance 30, got {final_balance}"
        print(f"Atomic conditional write verified: tx1={tx1_success}, tx2={tx2_success}, final_balance={final_balance}")

if __name__ == '__main__':
    run_lost_update_simulation()
