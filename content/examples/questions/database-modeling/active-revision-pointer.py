"""Demonstrate immutable document revisions and an atomic active-pointer swap for zero-downtime ingestion."""
import sqlite3

with sqlite3.connect(':memory:') as db:
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE document_revisions (
        revision_id INTEGER PRIMARY KEY,
        doc_id TEXT NOT NULL,
        revision_num INTEGER NOT NULL,
        content TEXT NOT NULL,
        embedding_status TEXT NOT NULL CHECK(embedding_status IN ('pending', 'indexing', 'ready')),
        UNIQUE(doc_id, revision_num)
    )''')
    cursor.execute('''
    CREATE TABLE active_document_pointers (
        doc_id TEXT PRIMARY KEY,
        active_revision_id INTEGER NOT NULL REFERENCES document_revisions(revision_id)
    )''')
    
    # 1. Initial State: Document D1 has revision 1 active and serving queries
    cursor.execute("INSERT INTO document_revisions VALUES (101, 'D1', 1, 'Policy v1 text', 'ready')")
    cursor.execute("INSERT INTO active_document_pointers VALUES ('D1', 101)")
    db.commit()

    # User query routes through the active pointer:
    active_rev = cursor.execute("""
    SELECT r.revision_num, r.content 
    FROM active_document_pointers p
    JOIN document_revisions r ON r.revision_id = p.active_revision_id
    WHERE p.doc_id = 'D1'
    """).fetchone()
    assert active_rev[0] == 1, "Queries serve Revision 1"

    # 2. Ingestion pipeline prepares Revision 2 in the background:
    # Notice: chunking, embedding, and indexing happen while queries continue serving Revision 1!
    cursor.execute("INSERT INTO document_revisions VALUES (102, 'D1', 2, 'Policy v2 updated terms', 'indexing')")
    db.commit()

    # Query still serves Revision 1 safely:
    active_during_indexing = cursor.execute("""
    SELECT r.revision_num FROM active_document_pointers p
    JOIN document_revisions r ON r.revision_id = p.active_revision_id
    WHERE p.doc_id = 'D1'
    """).fetchone()[0]
    assert active_during_indexing == 1

    # 3. Embedding completes -> Atomic Pointer Swap:
    cursor.execute("UPDATE document_revisions SET embedding_status = 'ready' WHERE revision_id = 102")
    cursor.execute("UPDATE active_document_pointers SET active_revision_id = 102 WHERE doc_id = 'D1'")
    db.commit()

    # Queries immediately switch to Revision 2 atomically without downtime or partial-read anomalies:
    active_after_swap = cursor.execute("""
    SELECT r.revision_num, r.content FROM active_document_pointers p
    JOIN document_revisions r ON r.revision_id = p.active_revision_id
    WHERE p.doc_id = 'D1'
    """).fetchone()
    
    print(f"Revision lifecycle verified: active switched from rev {active_during_indexing} to rev {active_after_swap[0]}")

