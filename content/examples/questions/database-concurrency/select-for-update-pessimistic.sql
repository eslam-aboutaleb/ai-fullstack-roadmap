-- Pessimistic Concurrency Control with SELECT FOR UPDATE and SKIP LOCKED in PostgreSQL

-- 1. Preventing Double-Confirmation in Transactional Workflows:
-- Two concurrent worker processes try to claim and confirm the same pending reservation.

BEGIN;
-- Transaction 1 acquires an exclusive row-level lock on the target row:
-- Any other transaction attempting to SELECT ... FOR UPDATE or UPDATE this row will BLOCK
-- until Transaction 1 issues COMMIT or ROLLBACK.
SELECT id, status, customer_id 
FROM flight_reservations 
WHERE id = 'res_90210' AND status = 'pending'
FOR UPDATE;

-- Having secured exclusive lock, Transaction 1 safely confirms the seat:
UPDATE flight_reservations 
SET status = 'confirmed', confirmed_at = clock_timestamp() 
WHERE id = 'res_90210';

COMMIT;

-- 2. Lock-Free Work Queue Worker Pattern using FOR UPDATE SKIP LOCKED:
-- When multiple background worker pods poll a shared tasks table, standard FOR UPDATE causes
-- all workers to queue behind the first locked row, destroying throughput.
-- SKIP LOCKED instructs PostgreSQL to immediately bypass already-locked rows and grab the next free task.

BEGIN;
SELECT id, task_type, payload 
FROM background_jobs 
WHERE status = 'queued' 
ORDER BY priority DESC, created_at ASC 
LIMIT 1 
FOR UPDATE SKIP LOCKED;

-- Worker atomically updates status to 'running' with its worker_id:
UPDATE background_jobs 
SET status = 'running', locked_by = 'worker_pod_3', locked_at = clock_timestamp() 
WHERE id = 'job_7718';

COMMIT;
