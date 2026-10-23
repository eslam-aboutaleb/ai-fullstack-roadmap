"""Demonstrate programmatic migration management, schema version tracking, and transactional DDL."""
import sqlite3

class MigrationManager:
    def __init__(self, db_conn):
        self.conn = db_conn
        self._init_version_table()

    def _init_version_table(self):
        """Create the alembic_version table to track applied migration revisions."""
        with self.conn:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS alembic_version (
                version_num VARCHAR(32) PRIMARY KEY
            )""")

    def current_version(self):
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT version_num FROM alembic_version").fetchone()
        return row[0] if row else None

    def apply_migration(self, revision_id, upgrade_sql, downgrade_sql):
        """Execute schema change and version update inside a single atomic ACID transaction."""
        curr = self.current_version()
        print(f"Applying migration: {curr} -> {revision_id}")
        with self.conn:
            # Execute transactional DDL
            self.conn.executescript(upgrade_sql)
            # Update migration ledger
            self.conn.execute("DELETE FROM alembic_version")
            self.conn.execute("INSERT INTO alembic_version (version_num) VALUES (?)", (revision_id,))

with sqlite3.connect(':memory:') as conn:
    mgr = MigrationManager(conn)
    assert mgr.current_version() is None, "Fresh database has no version"

    # Migration 001: Initial schema
    m1_upgrade = """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        email TEXT UNIQUE NOT NULL
    );
    """
    mgr.apply_migration("001_create_users", m1_upgrade, "DROP TABLE users;")
    assert mgr.current_version() == "001_create_users"

    # Migration 002: Add column with explicit default and constraint
    m2_upgrade = """
    ALTER TABLE users ADD COLUMN is_verified INTEGER NOT NULL DEFAULT 0;
    CREATE INDEX idx_users_email ON users(email);
    """
    mgr.apply_migration("002_add_verification", m2_upgrade, "ALTER TABLE users DROP COLUMN is_verified;")
    assert mgr.current_version() == "002_add_verification"

    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (email) VALUES ('ada@example.com')")
    user = cursor.execute("SELECT email, is_verified FROM users WHERE id = 1").fetchone()
    print(f"Migration completed safely: current_version={mgr.current_version()}, user={user}")
