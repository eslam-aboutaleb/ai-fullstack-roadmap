BEGIN;
SELECT revision FROM document_head
WHERE tenant_id = :tenant AND document_id = :document FOR UPDATE;
-- Application verifies that the active revision is still the expected one.
-- Prepared chunks were created before this lock window.
UPDATE document_head SET revision = :new_revision
WHERE tenant_id = :tenant AND document_id = :document
  AND revision = :expected_revision;
-- Require exactly one updated row, or handle a conflict.
COMMIT;
