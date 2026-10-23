-- Index Architectures in PostgreSQL / Relational DBs: B-Tree, Hash, and GIN

-- 1. Table with scalar temporal fields and semi-structured metadata
CREATE TABLE security_audit_events (
    id BIGSERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    actor_id TEXT NOT NULL,
    tags TEXT[] NOT NULL,
    payload JSONB NOT NULL
);

-- 2. B-Tree Index: Ideal for range scans, equality, prefix sorting, and composite keys
-- Supports: =, <, <=, >, >=, BETWEEN, and ORDER BY
CREATE INDEX idx_audit_tenant_time ON security_audit_events (tenant_id, created_at DESC);

-- 3. Hash Index: O(1) equality lookup only (no range queries or sorting)
-- Typically used for long random strings where only exact equality (=) is checked
CREATE INDEX idx_audit_actor_hash ON security_audit_events USING HASH (actor_id);

-- 4. GIN (Generalized Inverted Index): Ideal for multi-key composite values (arrays, JSONB)
-- jsonb_path_ops optimizes the @> containment operator with smaller index size
CREATE INDEX idx_audit_payload_gin ON security_audit_events USING GIN (payload jsonb_path_ops);
CREATE INDEX idx_audit_tags_gin ON security_audit_events USING GIN (tags);

-- Query Patterns & Optimizer Selection:
-- A) B-Tree index scan used for range + equality:
EXPLAIN SELECT id FROM security_audit_events 
WHERE tenant_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' 
  AND created_at >= '2026-01-01 00:00:00Z'
ORDER BY created_at DESC LIMIT 25;

-- B) GIN index scan used for JSONB containment and array intersection:
EXPLAIN SELECT id FROM security_audit_events 
WHERE payload @> '{"action": "role_escalation", "status": "blocked"}'
  AND tags && ARRAY['critical', 'compliance'];
