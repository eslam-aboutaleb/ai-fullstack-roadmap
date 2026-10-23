-- Atomic Task Deduplication using INSERT ... ON CONFLICT DO NOTHING

-- Anti-Pattern (Check-Then-Insert Race):
-- Two concurrent requests (e.g. browser double-click or network retry) both execute:
--   SELECT id FROM ingestion_tasks WHERE idempotency_key = 'upload_key_123';
-- Both observe 0 rows because neither has committed yet.
-- Both proceed to execute INSERT, creating duplicate ingestion jobs and duplicate embeddings!

-- Solution: Unique Constraint + Atomic ON CONFLICT
CREATE TABLE ingestion_tasks (
    id SERIAL PRIMARY KEY,
    idempotency_key TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('queued', 'running', 'completed', 'failed')),
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- Client 1 attempts insert:
-- Inserts row and returns generated task ID
INSERT INTO ingestion_tasks (idempotency_key, status, payload)
VALUES ('upload_key_123', 'queued', '{"source_url": "s3://docs/handbook.pdf"}')
ON CONFLICT (idempotency_key) DO NOTHING
RETURNING id, status;
-- Result: 1 row returned (id: 1, status: 'queued')

-- Client 2 attempts identical insert concurrently or as a retry:
-- The unique constraint on idempotency_key atomically halts insertion.
-- 'DO NOTHING' prevents constraint violation error.
INSERT INTO ingestion_tasks (idempotency_key, status, payload)
VALUES ('upload_key_123', 'queued', '{"source_url": "s3://docs/handbook.pdf"}')
ON CONFLICT (idempotency_key) DO NOTHING
RETURNING id, status;
-- Result: 0 rows returned (or query existing task by idempotency_key if empty)

-- Safe lookup query for caller when RETURNING yields empty result:
SELECT id, status, created_at 
FROM ingestion_tasks 
WHERE idempotency_key = 'upload_key_123';
