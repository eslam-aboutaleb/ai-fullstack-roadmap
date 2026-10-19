CREATE TABLE notes(id TEXT PRIMARY KEY, revision INTEGER, text TEXT);
INSERT INTO notes VALUES ('N1', 1, 'original');
UPDATE notes SET text='first', revision=revision+1 WHERE id='N1' AND revision=1;
UPDATE notes SET text='second', revision=revision+1 WHERE id='N1' AND revision=1;
SELECT revision, text FROM notes;
