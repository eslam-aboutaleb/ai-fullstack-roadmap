-- Demonstrate INNER vs LEFT vs FULL OUTER JOIN and SQL three-valued logic (NULL handling)
PRAGMA foreign_keys = ON;

CREATE TABLE departments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    bonus REAL
);

INSERT INTO departments VALUES (1, 'Platform'), (2, 'Security'), (3, 'Observability');
INSERT INTO employees VALUES (101, 'Ada', 1, 5000.0), (102, 'Grace', 2, NULL), (103, 'Linus', NULL, 3000.0);

-- 1. INNER JOIN: returns only matched pairs (excludes Linus who has no dept, and Observability which has no employees)
-- Output: Ada, Grace
SELECT e.name, d.name FROM employees e INNER JOIN departments d ON e.department_id = d.id;

-- 2. LEFT JOIN: preserves all employees even if department_id is NULL
-- Output: Ada (Platform), Grace (Security), Linus (NULL)
SELECT e.name, COALESCE(d.name, 'Unassigned') AS dept FROM employees e LEFT JOIN departments d ON e.department_id = d.id;

-- 3. SQL Three-Valued Logic (TRUE, FALSE, UNKNOWN):
-- In SQL, NULL = NULL evaluates to UNKNOWN, not TRUE.
-- WHERE clause only accepts expressions that evaluate to TRUE (UNKNOWN is treated as false for filtering).
-- Demonstrating the pitfall: WHERE bonus != 5000 does NOT include Grace (bonus IS NULL)!
SELECT name FROM employees WHERE bonus != 5000.0; -- Only Linus returned; Grace silently dropped!

-- Correct pattern to include NULLs when filtering:
SELECT name FROM employees WHERE bonus != 5000.0 OR bonus IS NULL; -- Returns Grace and Linus
