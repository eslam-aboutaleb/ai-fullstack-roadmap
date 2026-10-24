"""Demonstrate the four phases of an Expand-and-Contract zero-downtime schema migration."""
import sqlite3

with sqlite3.connect(':memory:') as db:
    cursor = db.cursor()
    # Initial table state: users have 'name' as a single column
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
    cursor.execute("INSERT INTO users VALUES (1, 'Ada Lovelace'), (2, 'Grace Hopper')")
    db.commit()

    # PHASE 1: EXPAND
    # Add new nullable columns without breaking existing v1 services that only know about 'name'
    cursor.execute("ALTER TABLE users ADD COLUMN first_name TEXT")
    cursor.execute("ALTER TABLE users ADD COLUMN last_name TEXT")
    db.commit()

    # PHASE 2: DUAL WRITE
    # v2 application services write to BOTH old and new columns.
    # Reads still fall back to old column if new column is empty.
    new_user = {'first_name': 'Margaret', 'last_name': 'Hamilton'}
    cursor.execute(
        "INSERT INTO users (id, name, first_name, last_name) VALUES (?, ?, ?, ?)",
        (3, f"{new_user['first_name']} {new_user['last_name']}", new_user['first_name'], new_user['last_name'])
    )
    db.commit()

    # PHASE 3: ASYNC BACKFILL
    # Background worker backfills existing historical rows that lack first_name/last_name
    cursor.execute("""
    UPDATE users 
    SET first_name = substr(name, 1, instr(name, ' ') - 1),
        last_name = substr(name, instr(name, ' ') + 1)
    WHERE first_name IS NULL
    """)
    db.commit()

    # Verify backfill complete:
    null_count = cursor.execute("SELECT count(*) FROM users WHERE first_name IS NULL OR last_name IS NULL").fetchone()[0]
    assert null_count == 0, "All rows backfilled"

    # PHASE 4: CONTRACT
    # Once all application instances are running v2 (reading only first_name/last_name),
    # drop the old deprecated 'name' column in a final forward migration
    cursor.execute("ALTER TABLE users DROP COLUMN name")
    db.commit()

    # Verify final schema
    final_rows = cursor.execute("SELECT id, first_name, last_name FROM users ORDER BY id").fetchall()
    print(f"Expand-and-contract migration finished: {len(final_rows)} rows migrated with zero downtime")

