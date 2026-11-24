# Phase 01 report — Synthetic database and safe queries

Status: Passed
Date: 2026-11-23 (Asia/Calcutta)
Source prompts: P03, P08

## Implemented

- Constrained SQLite schema: departments, students, fees, courses, enrollments.
- Idempotent, non-destructive seed: 3 departments, 25 fictional students, 50 fee
  records across two terms, 6 courses, and 48 enrollments. Includes GPA 8.0 boundary,
  a high-GPA overdue-fee student, and a student without enrollments.
- Four whitelisted tools, read-only connections, bound parameters, strict ASCII
  identifiers, explicit term selection, readable missing/locked database outcomes.
- Student-list helper for the future UI and Compose init seeding command.
- Actual local synthetic DB created at `data/university.db` (ignored by Git).

## Testing performed after implementation

| Check | Command/procedure | Result | Evidence |
| --- | --- | --- | --- |
| Host cumulative suite | `.venv/Scripts/python.exe -m pytest -q` | 25 passed, exit 0 | `artifacts/phase01-host-tests.log` |
| Docker cumulative suite | `docker run --rm unihybrid-ai-test:phase-01 python -m pytest -q` | 25 passed, exit 0 | `artifacts/phase01-container-tests.log` |
| Image builds | `docker build --target runtime/test -t ...:phase-01 .` | Both passed, exit 0 | `artifacts/phase01-runtime-build.log`, `artifacts/phase01-test-build.log` |
| Compose schema | `docker compose config --quiet` | Passed, exit 0 | Terminal output |
| Persistence | Seed in one runtime container, query and reseed in another using dedicated `dellproject_phase01_check` volume | 25 students retained, no duplicates, GPA 8.4 | Terminal output |
| Host smoke | Seed local DB, query profile/fees for S-012 | GPA 8.4, year 3, Mechanical, current-term Paid, zero outstanding | Terminal output |

Assertions cover counts, foreign keys, ranges, every query, empty/unknown IDs,
invalid/Unicode/injection IDs, multi-term fees, read-only write rejection, locked
and missing databases, repeat seeding, and preservation of edited fixture records.

## Docker images

- Runtime `unihybrid-ai:phase-01`:
  `sha256:90349d351d128aa97d827430a6de918833f35de7ea3c7e1260a1995398e727c0`.
- Test `unihybrid-ai-test:phase-01`:
  `sha256:04cad67686be5e15e49f7af96a38125ba94309f3f7c716c40402efe7afbeeef2`.
- Linux amd64, non-root `app`; base digest unchanged from Phase 00.

## Difficulties faced

No new implementation failures observed. Fixture review improved the GPA-boundary
student to meet year criteria and made a high-GPA student's overdue fees independently
demonstrable. The updated fixtures passed the host/container suites.

## Manual requirements from the user

None for Phase 01. Gemini credentials are needed only for the later live API gate.

## Phase gate

Passed. Phase 02 eligible. SQL tools are implemented; query classification,
retrieval, generated answers, and the UI are still pending.
