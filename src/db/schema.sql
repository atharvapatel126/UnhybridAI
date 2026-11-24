-- SYNTHETIC DEMO ONLY. No real university or student records.
CREATE TABLE IF NOT EXISTS departments (
    dept_id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY, name TEXT NOT NULL,
    dept_id TEXT NOT NULL REFERENCES departments(dept_id),
    year INTEGER NOT NULL CHECK (year BETWEEN 1 AND 4),
    gpa REAL NOT NULL CHECK (gpa BETWEEN 0 AND 10), email TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS fees (
    student_id TEXT NOT NULL REFERENCES students(student_id), term TEXT NOT NULL,
    amount_due INTEGER NOT NULL CHECK (amount_due >= 0),
    amount_paid INTEGER NOT NULL CHECK (amount_paid BETWEEN 0 AND amount_due),
    status TEXT NOT NULL CHECK (status IN ('Paid', 'Pending', 'Overdue')),
    due_date TEXT NOT NULL,
    PRIMARY KEY (student_id, term),
    CHECK ((status = 'Paid' AND amount_paid = amount_due)
        OR (status IN ('Pending', 'Overdue') AND amount_paid < amount_due))
);
CREATE TABLE IF NOT EXISTS courses (
    course_id TEXT PRIMARY KEY, name TEXT NOT NULL,
    dept_id TEXT NOT NULL REFERENCES departments(dept_id),
    credits INTEGER NOT NULL CHECK (credits BETWEEN 1 AND 6)
);
CREATE TABLE IF NOT EXISTS enrollments (
    student_id TEXT NOT NULL REFERENCES students(student_id),
    course_id TEXT NOT NULL REFERENCES courses(course_id),
    grade TEXT CHECK (grade IN ('A', 'B', 'C', 'D', 'F') OR grade IS NULL),
    PRIMARY KEY (student_id, course_id)
);
