"""Demonstrate transactional ACID authority vs external vector store dual-write split brain."""
import sqlite3

class MockVectorStore:
    def __init__(self):
        self.vectors = {}
    def upsert(self, doc_id, embedding):
        self.vectors[doc_id] = embedding
    def delete(self, doc_id):
        self.vectors.pop(doc_id, None)

vector_db = MockVectorStore()

with sqlite3.connect(':memory:') as rdb:
    cursor = rdb.cursor()
    # Authoritative relational schema with audit trail and outbox table
    cursor.execute('''
    CREATE TABLE documents (
        id TEXT PRIMARY KEY,
        owner_id TEXT NOT NULL,
        content TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('draft', 'indexed', 'archived'))
    )''')
    cursor.execute('''
    CREATE TABLE outbox_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        aggregate_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        payload TEXT NOT NULL,
        dispatched_at TIMESTAMP
    )''')

    # FAILURE CASE: Uncoordinated Dual Write
    # Attempting to write directly to vector store then DB without outbox
    doc_id = "doc_99"
    vector_db.upsert(doc_id, [0.12, 0.45, 0.88]) # Vector store updated!
    
    # DB transaction fails due to constraint error or network crash:
    try:
        cursor.execute("INSERT INTO documents VALUES (?, ?, ?, ?)", (doc_id, "user_1", "Secret draft", "invalid_status"))
        rdb.commit()
    except sqlite3.IntegrityError:
        rdb.rollback()
        # DUAL-WRITE ANOMALY: vector_db now holds orphan data that does not exist in authoritative DB!
        assert doc_id in vector_db.vectors, "Split-brain: orphan vector exists without database record"

    # SUCCESS CASE: Transactional Outbox Pattern
    # Authoritative change + outbox event commit ATOMICALLY in one database transaction
    valid_id = "doc_100"
    with rdb:
        cursor.execute("INSERT INTO documents VALUES (?, ?, ?, ?)", (valid_id, "user_1", "Published guide", "draft"))
        cursor.execute(
            "INSERT INTO outbox_events (aggregate_id, event_type, payload) VALUES (?, ?, ?)",
            (valid_id, "DOCUMENT_CREATED", "{\"chunk\": \"Published guide\"}")
        )
    
    # Outbox worker reads un-dispatched events and safely syncs to vector DB
    events = cursor.execute("SELECT event_id, aggregate_id, payload FROM outbox_events WHERE dispatched_at IS NULL").fetchall()
    for ev_id, agg_id, payload in events:
        vector_db.upsert(agg_id, [0.01, 0.02, 0.03])
        cursor.execute("UPDATE outbox_events SET dispatched_at = CURRENT_TIMESTAMP WHERE event_id = ?", (ev_id,))
    rdb.commit()

    print(f"Authoritative ACID outbox synced: event_count={len(events)}, doc_id={valid_id} verified")

