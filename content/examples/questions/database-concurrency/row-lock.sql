BEGIN;
SELECT id, status FROM reviews WHERE id='R1' FOR UPDATE;
UPDATE reviews SET status='confirmed' WHERE id='R1' AND status='pending';
COMMIT;
