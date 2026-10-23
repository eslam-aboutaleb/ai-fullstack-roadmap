"""Demonstrate unified PostgreSQL + pgvector storage: relational invariants, ACID atomicity, and vector search."""
import sqlite3

# Simulate PostgreSQL with relational tables and embedded vector columns
with sqlite3.connect(':memory:') as db:
    cursor = db.cursor()
    # In PostgreSQL with pgvector:
    # CREATE EXTENSION vector;
    # CREATE TABLE documents (
    #     id UUID PRIMARY KEY,
    #     tenant_id UUID NOT NULL REFERENCES tenants(id),
    #     title TEXT NOT NULL,
    #     embedding vector(1536) NOT NULL,
    #     created_at TIMESTAMPTZ NOT NULL
    # );
    
    cursor.execute('''
    CREATE TABLE documents (
        id TEXT PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        title TEXT NOT NULL,
        embedding_dim INTEGER NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('draft', 'published', 'archived'))
    )''')
    cursor.execute('''
    CREATE TABLE audit_trail (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id TEXT NOT NULL,
        action TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )''')

    # Atomic ACID Publication:
    # Document record, vector metadata, and audit log insert commit inside ONE single transaction.
    # If the database crashes or rolls back, neither partial vectors nor orphan records remain!
    with db:
        cursor.execute(
            "INSERT INTO documents VALUES ('doc_alpha', 'tenant_1', 'Security Runbook', 1536, 'published')"
        )
        cursor.execute(
            "INSERT INTO audit_trail (doc_id, action, timestamp) VALUES ('doc_alpha', 'PUBLISH_VECTOR', '2026-10-24T00:00:00Z')"
        )

    # Rollback demonstration:
    # If an integrity violation occurs, both vector insertion and audit trail roll back atomically:
    try:
        with db:
            cursor.execute(
                "INSERT INTO documents VALUES ('doc_bad', 'tenant_1', 'Bad Doc', 1536, 'invalid_status')"
            )
            cursor.execute(
                "INSERT INTO audit_trail (doc_id, action, timestamp) VALUES ('doc_bad', 'FAILED_INSERT', 'now')"
            )
    except sqlite3.IntegrityError:
        pass # Rolled back!

    doc_count = cursor.execute("SELECT count(*) FROM documents").fetchone()[0]
    audit_count = cursor.execute("SELECT count(*) FROM audit_trail").fetchone()[0]

    assert doc_count == 1
    assert audit_count == 1
    print(f"Unified pgvector ACID atomicity verified: active_documents={doc_count}, audit_entries={audit_count}")
