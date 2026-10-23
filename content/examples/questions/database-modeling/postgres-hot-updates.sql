-- PostgreSQL Heap-Only Tuple (HOT) Update Mechanics and Table Design

-- 1. Create table with reduced fillfactor (e.g. 70%) to reserve 30% page space for in-place tuple updates
CREATE TABLE connection_heartbeats (
    session_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    status TEXT NOT NULL,
    ping_count INT NOT NULL,
    last_seen_at TIMESTAMPTZ NOT NULL
) WITH (fillfactor = 70);

-- 2. Indexes: Only index columns that are queried and rarely mutated
-- user_id is queried to find active sessions for a user:
CREATE INDEX idx_heartbeats_user ON connection_heartbeats (user_id);

-- Note: We deliberately DO NOT index 'last_seen_at' or 'ping_count' on this high-frequency update table!

-- 3. HOT Update Scenario (Successful HOT):
-- An UPDATE that modifies ONLY unindexed columns (last_seen_at, ping_count) allows PostgreSQL to:
--   a) Store the new tuple version directly in the spare 30% space of the SAME heap page.
--   b) Chain the old tuple pointer to the new tuple (HOT chain).
--   c) Zero index modification: existing B-Tree pointers continue pointing to the root tuple.
UPDATE connection_heartbeats 
SET last_seen_at = clock_timestamp(), ping_count = ping_count + 1 
WHERE session_id = 'c1b48b7a-9e1f-4b09-b42e-6bc8adfa9901';

-- 4. Broken HOT Optimization (Write Amplification):
-- If an UPDATE modifies an indexed column (e.g., user_id or status if status is indexed):
--   PostgreSQL CANNOT use HOT. It must write a new heap tuple AND insert new entries into EVERY index,
--   causing index page splits, WAL write amplification, and table/index bloat.
