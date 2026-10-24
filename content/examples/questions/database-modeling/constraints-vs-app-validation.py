"""Demonstrate why database constraints (CHECK, UNIQUE, FK) prevent concurrent race conditions that bypass app checks."""
import sqlite3

with sqlite3.connect(':memory:') as db:
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE subscriptions (
        id INTEGER PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        plan_code TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1,
        max_seats INTEGER NOT NULL CHECK(max_seats > 0),
        UNIQUE(tenant_id, plan_code)
    )''')
    cursor.execute("INSERT INTO subscriptions VALUES (1, 'tenant_alpha', 'PRO_MONTHLY', 1, 10)")
    db.commit()

    # PITFALL: Application-Level Validation Race Condition
    # Two concurrent requests both execute:
    #   if not db.find_subscription(tenant_id, plan_code):
    #       db.insert(...)
    # Both check concurrently, both see 0 records, and both attempt to insert!
    
    # Without database constraints, you get duplicate active plans and corrupted billing state.
    # With UNIQUE(tenant_id, plan_code), the database guarantees atomicity and rejects the second insert:
    duplicate_rejected = False
    try:
        cursor.execute("INSERT INTO subscriptions VALUES (2, 'tenant_alpha', 'PRO_MONTHLY', 1, 15)")
        db.commit()
    except sqlite3.IntegrityError:
        duplicate_rejected = True
        db.rollback()

    # CHECK constraint rejection:
    # Application layer might have a bug allowing negative seats in an API payload:
    negative_seats_rejected = False
    try:
        cursor.execute("INSERT INTO subscriptions VALUES (3, 'tenant_beta', 'ENTERPRISE', 1, -5)")
        db.commit()
    except sqlite3.IntegrityError:
        negative_seats_rejected = True
        db.rollback()

    assert duplicate_rejected and negative_seats_rejected
    print(f"Database constraints enforced: duplicate_rejected={duplicate_rejected}, negative_seats_rejected={negative_seats_rejected}")

