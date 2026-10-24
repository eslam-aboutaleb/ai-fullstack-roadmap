"""Demonstrate 1NF, 2NF, and 3NF normalization eliminating anomalies."""
import sqlite3

with sqlite3.connect(':memory:') as db:
    cursor = db.cursor()
    
    # 1. Unnormalized / De-normalized table with functional dependency issues:
    # (dept_name, dept_building) depends only on dept_name, not on employee_id (violating 3NF).
    cursor.execute('''
    CREATE TABLE employee_unnormalized (
        emp_id INTEGER,
        emp_name TEXT,
        dept_name TEXT,
        dept_building TEXT,
        PRIMARY KEY (emp_id)
    )''')
    cursor.execute("INSERT INTO employee_unnormalized VALUES (1, 'Alice', 'Engineering', 'Building A')")
    cursor.execute("INSERT INTO employee_unnormalized VALUES (2, 'Bob', 'Engineering', 'Building A')")
    
    # Update anomaly demonstration: updating department building requires updating every employee row.
    # If one row is missed, data becomes inconsistent.
    cursor.execute("UPDATE employee_unnormalized SET dept_building = 'Building C' WHERE emp_id = 1")
    buildings = cursor.execute("SELECT DISTINCT dept_building FROM employee_unnormalized WHERE dept_name = 'Engineering'").fetchall()
    assert len(buildings) > 1, "Anomaly demonstrated: conflicting building records for same department"
    
    # 2. Decompose into 3NF: Department table + Employee table with Foreign Key
    cursor.execute('''
    CREATE TABLE departments (
        dept_id INTEGER PRIMARY KEY,
        dept_name TEXT UNIQUE NOT NULL,
        dept_building TEXT NOT NULL
    )''')
    cursor.execute('''
    CREATE TABLE employees (
        emp_id INTEGER PRIMARY KEY,
        emp_name TEXT NOT NULL,
        dept_id INTEGER NOT NULL REFERENCES departments(dept_id)
    )''')
    
    cursor.execute("INSERT INTO departments VALUES (10, 'Engineering', 'Building A')")
    cursor.execute("INSERT INTO employees VALUES (1, 'Alice', 10)")
    cursor.execute("INSERT INTO employees VALUES (2, 'Bob', 10)")
    
    # Now an update touches exactly ONE row in departments, with zero risk of inconsistency:
    cursor.execute("UPDATE departments SET dept_building = 'Building B' WHERE dept_id = 10")
    
    # Insertion anomaly eliminated: we can add a new department before hiring any employee
    cursor.execute("INSERT INTO departments VALUES (20, 'Research', 'Building D')")
    
    # Deletion anomaly eliminated: deleting all employees in dept 10 does not erase the department entity
    cursor.execute("DELETE FROM employees WHERE dept_id = 10")
    remaining_dept = cursor.execute("SELECT dept_name FROM departments WHERE dept_id = 10").fetchone()[0]
    
    print(f"3NF verified: dept={remaining_dept} intact after employee deletion, anomalies eliminated")

