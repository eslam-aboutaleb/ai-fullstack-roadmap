ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY owner_scope ON tasks
USING (owner_id = current_setting('app.owner_id', true));
-- Inside a trusted, scoped transaction, set the verified principal:
SET LOCAL app.owner_id = 'A';
SELECT id FROM tasks;
