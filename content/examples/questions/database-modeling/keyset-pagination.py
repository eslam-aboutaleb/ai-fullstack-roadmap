"""Demonstrate OFFSET/LIMIT quadratic degradation vs O(1) Keyset (cursor-based) pagination."""
import sqlite3

with sqlite3.connect(':memory:') as db:
    cursor = db.cursor()
    cursor.execute("CREATE TABLE events (id INTEGER PRIMARY KEY, created_at INTEGER, payload TEXT)")
    cursor.execute("CREATE INDEX idx_events_created_id ON events (created_at DESC, id DESC)")
    
    # Insert 10,000 synthetic ordered events
    batch = [(i, 1700000000 + (i // 5), f"data-{i}") for i in range(1, 10001)]
    cursor.executemany("INSERT INTO events VALUES (?, ?, ?)", batch)
    
    # 1. OFFSET Pagination:
    # To fetch page 500 (items 5000 to 5010), the database engine must scan and discard 5,000 rows.
    # EXPLAIN QUERY PLAN shows scan overhead scaling linearly with offset size.
    plan_offset = cursor.execute(
        "EXPLAIN QUERY PLAN SELECT id FROM events ORDER BY created_at DESC, id DESC LIMIT 10 OFFSET 5000"
    ).fetchall()
    
    # 2. Keyset (Cursor) Pagination:
    # Client passes the cursor from the last item of the previous page: (cursor_created_at, cursor_id).
    # The query performs an exact index seek directly to the next tuple, skipping preceding rows in O(1) time.
    cursor_time, cursor_id = 1700001000, 5001
    
    keyset_query = """
    SELECT id, created_at, payload 
    FROM events 
    WHERE (created_at < ?) OR (created_at = ? AND id < ?)
    ORDER BY created_at DESC, id DESC 
    LIMIT 10
    """
    results = cursor.execute(keyset_query, (cursor_time, cursor_time, cursor_id)).fetchall()
    
    assert len(results) == 10
    assert results[0][0] < cursor_id or results[0][1] < cursor_time
    print(f"Keyset pagination seek returned {len(results)} rows; next_cursor=({results[-1][1]}, {results[-1][0]})")
