ALTER TABLE service_request ENABLE ROW LEVEL SECURITY;
ALTER TABLE service_request FORCE ROW LEVEL SECURITY;
CREATE POLICY request_owner ON service_request TO support_api
USING (owner_id = NULLIF(current_setting('app.owner_id', true), '')::uuid)
WITH CHECK (owner_id = NULLIF(current_setting('app.owner_id', true), '')::uuid);
-- The role must be non-owner without BYPASSRLS.
-- Bind trusted identity transaction-locally and test pooled reuse.
-- Arbitrary SQL capable of setting this variable defeats identity assumptions.
