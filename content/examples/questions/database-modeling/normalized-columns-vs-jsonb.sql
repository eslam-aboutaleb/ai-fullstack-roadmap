-- Relational Architecture: Normalized Structured Columns vs Semi-Structured JSONB

-- 1. Schema Design:
-- Put relational keys, foreign keys, transaction status, financial amounts, and search targets in typed columns.
-- Put schema-variable third-party payloads, telemetry metadata, and custom user attributes in JSONB.
CREATE TABLE customer_orders (
    -- NORMALIZED COLUMNS: Strong types, constraints, foreign keys, and B-Tree indexing
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    status TEXT NOT NULL CHECK(status IN ('pending', 'authorized', 'captured', 'refunded')),
    subtotal_cents BIGINT NOT NULL CHECK(subtotal_cents >= 0),
    currency CHAR(3) NOT NULL DEFAULT 'USD',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    -- JSONB COLUMN: Polymorphic, sparse, or provider-dependent attributes
    -- e.g. payment gateway raw responses, device fingerprints, custom tenant tags
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Indexing normalized columns with B-Tree:
CREATE INDEX idx_orders_customer_created ON customer_orders (customer_id, created_at DESC);

-- Indexing JSONB columns with GIN for fast containment queries (@>):
CREATE INDEX idx_orders_metadata_gin ON customer_orders USING GIN (metadata jsonb_path_ops);

-- 2. Querying Normalized vs JSONB:
-- Fast exact relational filtering:
SELECT id, subtotal_cents, status 
FROM customer_orders 
WHERE customer_id = 'b9c7b411-6df1-4a37-b649-1d4dbdf293a1' 
  AND status = 'captured' 
ORDER BY created_at DESC LIMIT 10;

-- JSONB containment query leveraging GIN index:
SELECT id, metadata->>'gateway_transaction_id' AS gateway_tx
FROM customer_orders
WHERE metadata @> '{"payment_method": {"type": "apple_pay", "risk_level": "normal"}}';
