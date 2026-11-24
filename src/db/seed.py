"""Idempotently create SYNTHETIC DEMO ONLY records; never reset existing data."""
from pathlib import Path
import sqlite3

from config import settings


def seed_database(path=None):
    path = Path(path or settings.db_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path, timeout=2) as db:
            db.execute("PRAGMA foreign_keys = ON")
            db.executescript(Path(__file__).with_name("schema.sql").read_text())
            departments = [("CSE", "Computer Science"), ("ECE", "Electronics"), ("ME", "Mechanical")]
            db.executemany("INSERT OR IGNORE INTO departments VALUES (?, ?)", departments)
            for i in range(1, 26):
                sid = f"S-{i:03d}"
                dept = departments[(i - 1) % 3][0]
                gpa = {1: 8.0, 2: 8.7, 12: 8.4, 25: 9.8}.get(i, round(5.5 + (i % 22) * .19, 2))
                year = {1: 2, 12: 3}.get(i, (i - 1) % 4 + 1)
                db.execute("INSERT OR IGNORE INTO students VALUES (?, ?, ?, ?, ?, ?)",
                           (sid, f"Demo Student {i:02d}", dept, year, gpa, f"s{i:03d}@example.invalid"))
                status = {1: "Paid", 2: "Overdue", 12: "Paid"}.get(i, ("Paid", "Overdue", "Pending")[i % 3])
                db.execute("INSERT OR IGNORE INTO fees VALUES (?, ?, ?, ?, ?, ?)",
                           (sid, settings.current_term, 50000, 50000 if status == "Paid" else 20000,
                            status, "2026-10-01" if status == "Overdue" else "2026-12-15"))
                # A previous term proves queries do not silently combine unrelated fees.
                db.execute("INSERT OR IGNORE INTO fees VALUES (?, ?, ?, ?, ?, ?)",
                           (sid, "2026-SPRING", 45000, 45000, "Paid", "2026-04-15"))
            for dept, _ in departments:
                for n in (1, 2):
                    cid = f"{dept}-{n:03d}"
                    db.execute("INSERT OR IGNORE INTO courses VALUES (?, ?, ?, ?)",
                               (cid, f"{dept} Demo Course {n}", dept, 3))
                    db.execute("""INSERT OR IGNORE INTO enrollments
                                  SELECT student_id, ?, 'A' FROM students
                                  WHERE dept_id = ? AND student_id != 'S-025'""", (cid, dept))
        return {"ok": True, "error": None, "path": str(path)}
    except (sqlite3.Error, OSError):
        return {"ok": False, "error": "Cannot initialize database. Check file permissions or another process holding a lock.", "path": str(path)}


def main():
    result = seed_database()
    print(f"SYNTHETIC demo database ready: {result['path']}" if result["ok"] else result["error"])
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
