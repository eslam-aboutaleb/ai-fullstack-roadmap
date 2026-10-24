-- Model document identity and revision identity without owner collision or cross-tenant contamination
PRAGMA foreign_keys = ON;

-- 1. Document Entity: Represents the stable conceptual document owned by an organization or user
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL,
    title TEXT NOT NULL,
    created_at INTEGER NOT NULL
);

-- 2. Revision Entity: Represents immutable versions of a document
-- Composite uniqueness rule is scoped strictly to (document_id, revision_num).
-- Notice: We DO NOT place a unique constraint on (owner_id, revision_num) because an owner can create
-- hundreds of documents, each having revision 1, 2, 3...
CREATE TABLE document_revisions (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    revision_num INTEGER NOT NULL CHECK(revision_num > 0),
    content_hash TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    UNIQUE(document_id, revision_num)
);

-- Test Case: Owner 'owner_alpha' creates Document 1 and Document 2
INSERT INTO documents VALUES ('doc_01', 'owner_alpha', 'Incident Runbook', 1700000000);
INSERT INTO documents VALUES ('doc_02', 'owner_alpha', 'Architecture Plan', 1700000100);

-- Both documents can increment their own revision 1 and revision 2 without collision:
INSERT INTO document_revisions VALUES ('rev_01_1', 'doc_01', 1, 'hash_abc', 1700000010);
INSERT INTO document_revisions VALUES ('rev_01_2', 'doc_01', 2, 'hash_def', 1700000020);

INSERT INTO document_revisions VALUES ('rev_02_1', 'doc_02', 1, 'hash_ghi', 1700000110);
INSERT INTO document_revisions VALUES ('rev_02_2', 'doc_02', 2, 'hash_jkl', 1700000120);

-- Output all active revisions across the owner's documents:
SELECT d.owner_id, d.title, r.revision_num, r.content_hash
FROM documents d
JOIN document_revisions r ON r.document_id = d.id
ORDER BY d.id, r.revision_num;

