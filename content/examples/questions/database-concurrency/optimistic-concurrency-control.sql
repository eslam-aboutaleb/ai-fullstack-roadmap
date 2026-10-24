-- Optimistic Concurrency Control (OCC) using an Integer Revision / Version Column

CREATE TABLE document_drafts (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    updated_at INTEGER NOT NULL
);

-- Initial State: Document exists at version 1
INSERT INTO document_drafts VALUES ('doc_42', 'Architecture Plan', 'Initial draft text', 1, 1700000000);

-- Client A and Client B both read doc_42 concurrently:
-- Both observe: version = 1, content = 'Initial draft text'

-- 1. Client A submits edit first:
-- The WHERE clause asserts that the database row still matches the version Client A read (version = 1).
-- If true, it atomically updates content and increments version to 2.
UPDATE document_drafts 
SET content = 'Client A additions', version = version + 1, updated_at = 1700000010
WHERE id = 'doc_42' AND version = 1;
-- Result: 1 row affected. Update succeeds! Version is now 2.

-- 2. Client B submits edit second (based on stale version 1):
-- Client B's update statement executes the identical check:
UPDATE document_drafts 
SET content = 'Client B additions', version = version + 1, updated_at = 1700000020
WHERE id = 'doc_42' AND version = 1;
-- Result: 0 rows affected! The database atomically detects that version is now 2, rejecting the stale overwrite.

-- 3. Application layer checks rows_affected:
-- If rows_affected == 0, the application raises StaleObjectError (409 Conflict),
-- prompting Client B to reload the latest version and merge changes rather than silently destroying Client A's work.
SELECT id, version, content FROM document_drafts WHERE id = 'doc_42';

