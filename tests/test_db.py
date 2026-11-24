import sqlite3

import pytest
from src.db import queries
from src.db.seed import seed_database


@pytest.fixture
def database(tmp_path):
    path = tmp_path / "demo.db"
    assert seed_database(path)["ok"]
    return path


def test_integrity_and_seed_idempotency(database):
    with sqlite3.connect(database) as db:
        before = list(db.iterdump())
        assert db.execute("SELECT count(*) FROM students").fetchone()[0] == 25
        assert db.execute("SELECT count(*) FROM departments").fetchone()[0] == 3
        assert db.execute("SELECT count(*) FROM courses").fetchone()[0] == 6
        assert db.execute("SELECT count(*) FROM enrollments").fetchone()[0] == 48
        assert db.execute("SELECT count(*) FROM fees").fetchone()[0] == 50
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        assert db.execute("SELECT min(gpa),max(gpa),min(year),max(year) FROM students").fetchone() == (5.5, 9.8, 1, 4)
    assert seed_database(database)["ok"]
    with sqlite3.connect(database) as db:
        assert before == list(db.iterdump())
        db.execute("PRAGMA foreign_keys=ON")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO enrollments VALUES ('S-999','CSE-001','A')")


def test_queries_and_edge_cases(database):
    assert queries.get_student_profile("S-012", db_path=database)["rows"][0]["gpa"] == 8.4
    assert queries.get_student_profile("S-001", db_path=database)["rows"][0]["gpa"] == 8.0
    fees = queries.get_fee_status("S-005", db_path=database)["rows"][0]
    assert fees["status"] == "Pending" and fees["outstanding"] == 30000
    assert queries.get_fee_status("S-002", db_path=database)["rows"][0]["status"] == "Overdue"
    assert queries.get_fee_status("S-002", term="2026-SPRING", db_path=database)["rows"][0]["status"] == "Paid"
    assert not queries.get_fee_status("S-002", term="unknown", db_path=database)["found"]
    assert len(queries.get_enrollments("S-001", db_path=database)["rows"]) == 2
    assert not queries.get_enrollments("S-025", db_path=database)["found"]
    assert queries.get_department_stats("CSE", db_path=database)["rows"][0]["student_count"] == 9
    assert not queries.get_department_stats("XYZ", db_path=database)["found"]
    assert len(queries.list_students(db_path=database)["rows"]) == 25


@pytest.mark.parametrize("student_id", ["S001'; DROP TABLE students;--", "S-001' OR 1=1--", "S001", None, "S-٠٠١"])
def test_injection_and_invalid_ids(database, student_id):
    result = queries.get_student_profile(student_id, db_path=database)
    assert not result["found"] and result["error"]
    assert len(queries.list_students(db_path=database)["rows"]) == 25


def test_unknown_id_and_readonly(database):
    result = queries.get_student_profile("S-999", db_path=database)
    assert not result["found"] and result["error"] is None
    db = queries.connect_readonly(database)
    try:
        with pytest.raises(sqlite3.OperationalError):
            db.execute("DELETE FROM students")
    finally:
        db.close()


def test_missing_and_locked_database(database, tmp_path):
    missing = tmp_path / "missing.db"
    assert queries.get_student_profile("S-001", db_path=missing)["error"]
    assert not missing.exists()
    with sqlite3.connect(database) as lock:
        lock.execute("BEGIN EXCLUSIVE")
        assert queries.get_student_profile("S-001", db_path=database)["error"]
        assert not seed_database(database)["ok"]


def test_seed_preserves_existing_records(database):
    with sqlite3.connect(database) as db:
        db.execute("UPDATE students SET gpa=7.7 WHERE student_id='S-012'")
    assert seed_database(database)["ok"]
    assert queries.get_student_profile("S-012", db_path=database)["rows"][0]["gpa"] == 7.7
