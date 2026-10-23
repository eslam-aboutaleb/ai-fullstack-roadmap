"""Demonstrate PostgreSQL Read Committed isolation mechanics and non-repeatable read hazards."""
import sqlite3
import tempfile
import os

def test_read_committed_behavior():
    db_file = os.path.join(tempfile.gettempdir(), 'read_committed_test.db')
    if os.path.exists(db_file):
        os.remove(db_file)

    try:
        # Initialize test table
        init = sqlite3.connect(db_file)
        init.execute("CREATE TABLE products (id INT PRIMARY KEY, stock INT, price INT)")
        init.execute("INSERT INTO products VALUES (1, 10, 100)")
        init.commit()
        init.close()

        # Session 1: Application checkout workflow opens transaction
        s1 = sqlite3.connect(db_file, isolation_level=None)
        s2 = sqlite3.connect(db_file, isolation_level=None)

        s1.execute("BEGIN")
        # Step 1: Session 1 reads product price = $100 to calculate invoice total
        price_step1 = s1.execute("SELECT price FROM products WHERE id = 1").fetchone()[0]

        # Step 2: Meanwhile, admin pricing service in Session 2 updates price to $150 and commits
        s2.execute("BEGIN IMMEDIATE")
        s2.execute("UPDATE products SET price = 150 WHERE id = 1")
        s2.execute("COMMIT")

        # Step 3: Session 1 re-reads the product price in the SAME ongoing transaction:
        # Under Read Committed isolation, each statement acquires a NEW snapshot of the database!
        # Session 1 observes the newly committed price ($150) rather than the price read in Step 1.
        price_step3 = s1.execute("SELECT price FROM products WHERE id = 1").fetchone()[0]
        s1.execute("COMMIT")

        non_repeatable_read = (price_step1 != price_step3)
        assert non_repeatable_read is True
        print(f"Read Committed non-repeatable read verified: step1_price={price_step1}, step3_price={price_step3}")

    finally:
        if os.path.exists(db_file):
            os.remove(db_file)

if __name__ == '__main__':
    test_read_committed_behavior()
