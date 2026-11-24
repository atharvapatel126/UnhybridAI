"""Only fixed SQL and bound parameters; application connections are read-only."""
from pathlib import Path
import re
import sqlite3

from config import settings


def connect_readonly(path=None):
    uri = Path(path or settings.db_path).resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True, timeout=.5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    return connection


def _query(sql, args, source, valid, db_path=None):
    result = {"found": False, "rows": [], "source": source, "error": None}
    if not valid:
        result["error"] = "Invalid identifier. Select a valid synthetic student or department."
        return result
    try:
        db = connect_readonly(db_path)
        try:
            result["rows"] = [dict(row) for row in db.execute(sql, args).fetchall()]
            result["found"] = bool(result["rows"])
        finally:
            db.close()
    except (sqlite3.Error, OSError, ValueError):
        result["error"] = "Database unavailable. Initialize it and check file access or locks."
    return result


def _valid_student(student_id):
    return isinstance(student_id, str) and re.fullmatch(r"S-\d{3}", student_id, re.ASCII) is not None


def get_student_profile(student_id, *, db_path=None):
    return _query("""SELECT s.student_id, s.name, s.dept_id, d.name AS department,
                     s.year, s.gpa, s.email FROM students s
                     JOIN departments d ON s.dept_id=d.dept_id WHERE s.student_id=?""",
                  (student_id,), "SQL:students,departments", _valid_student(student_id), db_path)


def get_fee_status(student_id, *, db_path=None, term=None):
    return _query("""SELECT student_id, term, amount_due, amount_paid,
                     amount_due-amount_paid AS outstanding, status, due_date
                     FROM fees WHERE student_id=? AND term=?""",
                  (student_id, term or settings.current_term), "SQL:fees", _valid_student(student_id), db_path)


def get_enrollments(student_id, *, db_path=None):
    return _query("""SELECT e.student_id, c.course_id, c.name, c.credits, e.grade
                     FROM enrollments e JOIN courses c ON e.course_id=c.course_id
                     WHERE e.student_id=? ORDER BY c.course_id""",
                  (student_id,), "SQL:enrollments,courses", _valid_student(student_id), db_path)


def get_department_stats(dept_id, *, db_path=None):
    valid = isinstance(dept_id, str) and re.fullmatch(r"[A-Z]{2,5}", dept_id, re.ASCII) is not None
    return _query("""SELECT d.dept_id, d.name, COUNT(s.student_id) AS student_count,
                     ROUND(AVG(s.gpa), 2) AS average_gpa FROM departments d
                     LEFT JOIN students s ON s.dept_id=d.dept_id
                     WHERE d.dept_id=? GROUP BY d.dept_id, d.name""",
                  (dept_id,), "SQL:departments,students", valid, db_path)


def list_students(*, db_path=None):
    return _query("SELECT student_id, name FROM students ORDER BY student_id", (), "SQL:students", True, db_path)


TOOLS = {function.__name__: function for function in (
    get_student_profile, get_fee_status, get_enrollments, get_department_stats,
)}
