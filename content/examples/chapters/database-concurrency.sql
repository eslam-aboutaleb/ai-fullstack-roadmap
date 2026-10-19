UPDATE service_request
SET description = :description, version = version + 1
WHERE id = :id AND owner_id = :trusted_owner AND version = :expected
RETURNING id, version;
-- A zero-row result is not success: distinguish inaccessible, missing,
-- and conflicting state according to the API's disclosure policy.
