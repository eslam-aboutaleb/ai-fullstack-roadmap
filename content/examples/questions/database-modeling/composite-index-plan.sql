-- Composite Index Optimization and the Left-to-Right Index Prefix Rule
CREATE TABLE user_tasks (
    id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    payload TEXT
);

-- 1. Create composite index on (owner_id, created_at DESC)
-- Notice the column order: leading column 'owner_id' matches high-cardinality equality filter,
-- second column 'created_at DESC' provides pre-sorted order for chronological retrieval.
CREATE INDEX idx_tasks_owner_created ON user_tasks (owner_id, created_at DESC);

-- 2. Query 1: Optimal Index Scan (Equality + Order By + Limit)
-- EXPLAIN QUERY PLAN shows that the database engine can seek directly to owner_id
-- and read 20 rows along the index leaf pages WITHOUT executing a temporary B-Tree or in-memory sort.
EXPLAIN QUERY PLAN
SELECT id, status, created_at 
FROM user_tasks 
WHERE owner_id = 'usr_alice'
ORDER BY created_at DESC 
LIMIT 20;

-- 3. Query 2: Left-to-Right Prefix Pitfall
-- If a query filters ONLY on created_at without specifying owner_id:
-- The composite index CANNOT be used for an index seek because the leading key is missing!
-- The query planner falls back to a costly full table scan.
EXPLAIN QUERY PLAN
SELECT id 
FROM user_tasks 
WHERE created_at > 1700000000;
