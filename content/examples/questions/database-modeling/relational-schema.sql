PRAGMA foreign_keys = ON;
CREATE TABLE documents (id TEXT PRIMARY KEY, owner_id TEXT NOT NULL);
CREATE TABLE revisions (
  document_id TEXT REFERENCES documents(id), revision INTEGER CHECK(revision > 0),
  UNIQUE(document_id, revision)
);
INSERT INTO documents VALUES ('D1', 'A');
INSERT INTO revisions VALUES ('D1', 2);
SELECT d.id, d.owner_id, r.revision FROM documents d
JOIN revisions r ON r.document_id=d.id;
