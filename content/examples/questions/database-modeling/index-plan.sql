CREATE TABLE tasks (id TEXT PRIMARY KEY, owner_id TEXT, created_at INTEGER);
CREATE INDEX owner_time ON tasks(owner_id, created_at DESC);
EXPLAIN QUERY PLAN
SELECT id FROM tasks WHERE owner_id='A'
ORDER BY created_at DESC LIMIT 20;
