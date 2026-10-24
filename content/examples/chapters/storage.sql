CREATE TABLE document_chunk (
    tenant_id uuid NOT NULL,
    document_id uuid NOT NULL,
    revision integer NOT NULL CHECK (revision > 0),
    chunk_id uuid NOT NULL,
    text_content text NOT NULL,
    PRIMARY KEY (tenant_id, document_id, revision, chunk_id)
);
-- Add a vector column with a dimension chosen for the pinned embedding model.
-- Parameterize values and authorize tenant scope before executing queries.
