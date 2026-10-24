BEGIN;
SET LOCAL lock_timeout = '500ms';
SET LOCAL statement_timeout = '3s';
SET LOCAL idle_in_transaction_session_timeout = '5s';
ROLLBACK;
