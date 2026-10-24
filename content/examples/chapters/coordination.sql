BEGIN;
INSERT INTO service_request (operation_key, owner_id, status)
VALUES (:operation_key, :owner_id, 'accepted');
INSERT INTO outbox (operation_key, event_type, status)
VALUES (:operation_key, 'request.accepted', 'pending');
COMMIT;
-- Add uniqueness constraints appropriate to operation identity.
-- Workers must tolerate retry after effects occur but before completion is recorded.
