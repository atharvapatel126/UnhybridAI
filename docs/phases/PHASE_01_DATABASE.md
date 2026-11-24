# Phase 01 — Synthetic database and safe SQL

Source prompts: P03, P08. Dependency: Phase 00 passed. Status: Passed. Results: [phase report](../reports/PHASE_01_REPORT.md).
Apply all shared implementation, testing, Docker, and reporting rules.

## Implementation instructions

1. Create `src/db/schema.sql`, `seed.py`, and `queries.py` with documented invocation
   `python -m src.db.seed`. Use configuration paths, not the working directory.
2. Define departments, students, fees, courses, and enrollments with primary keys,
   foreign keys, and appropriate constraints. Include explicit fee term and due
   date. Scholarship applications remain optional.
3. Seed at least three departments and 25 fictional students, years 1–4, GPA
   5.5–9.8, canonical IDs `S-001` onward, and Paid/Pending/Overdue fee cases.
   Include merit-boundary, overdue, and unknown-student test cases. All fixtures
   and comments identify data as synthetic.
4. Make seeding repeatable without duplicate rows or destructive resets. Enable
   foreign keys on write connections; handle locks and unavailable paths clearly.
5. Open query connections using SQLite URI `mode=ro`. Implement a `TOOLS` registry
   for `get_student_profile`, `get_fee_status`, `get_enrollments`, and
   `get_department_stats`. Use `?` parameters and fixed SQL only.
6. Validate input formats and return shared result contracts for missing/invalid
   IDs, missing DB, and operational errors. Validate department IDs separately.
   Query results preserve source table identity and relevant term context.
7. Wire the Compose init service to seed the mounted database once this command
   exists. Do not reseed on every Streamlit rerun.

## Testing after this phase

- Use a temporary database: assert table counts, valid GPA/year ranges, fee cases,
  primary-key uniqueness, no orphan rows, and one meaningful query per table.
- Run seed twice; compare counts and fixture values for idempotency.
- Verify each whitelisted tool returns expected rows and source metadata, including
  department stats, multiple fee terms, no enrollments, and unknown IDs.
- Test `S001'; DROP TABLE students;--` and equivalent malformed IDs: readable
  invalid/not-found outcome and unchanged database schema/rows.
- Attempt a write through the read-only query connection: it must fail.
- Test missing/locked DB behavior without an unhandled error.
- Run `python -m pytest tests/test_db.py -q` and earlier applicable tests; build
  Phase 01 runtime/test images and rerun the suite inside the test image.
- Seed a test volume, restart a container, and verify expected persisted records.

## Exit gate and report

All schema, safe-query, idempotency, and container tests pass. Save
`docs/reports/PHASE_01_REPORT.md` with actual sample outputs, difficulties, image
IDs, and manual requirements. Potential user requirement: none beyond a working
Docker setup; use synthetic data without asking for real student records.
