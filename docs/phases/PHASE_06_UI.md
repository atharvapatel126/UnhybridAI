# Phase 06 — Streamlit application

Source prompt: P13. Dependency: Phase 05 passed. Status: Passed. Results: [phase report](../reports/PHASE_06_REPORT.md).
Apply all shared implementation, testing, Docker, and reporting rules.

## Implementation instructions

1. Implement `app.py` as presentation only; call existing ingestion, orchestration,
   configuration, and document-list APIs rather than duplicating business logic.
2. Add sidebar synthetic student selector, PDF/TXT uploader, ingestion progress,
   indexed-document list, and readable upload status. Reuse size/type/path checks.
3. Add chat input and session history, route badge/reason, final answer, sources,
   expandable SQL rows, and document chunks with file/page/score.
4. Show missing-key, missing DB/document, partial-data, and API-failure notices.
   Avoid exposing stack traces or secrets. Do not answer for an unselected student.
5. Use `st.cache_resource` to delegate to the core model cache. Prevent duplicate
   ingestion, repeated initialization, or repeated calls caused solely by rerenders.
   Switching student must not present old history as the new student's answer;
   clear or partition history by student identity.
6. Configure the runtime image to launch Streamlit on container interface 0.0.0.0,
   port 8501, with host binding and health check defined in `../DOCKER.md`.

## Testing after this phase

- Use Streamlit's supported testing tooling for startup/widgets if compatible with
  the pinned version; mock external calls for deterministic UI checks.
- Manually run GPA/fees, attendance, and scholarship scenarios in the browser;
  verify route, source panels, actual page numbers, and displayed warnings.
- Upload valid TXT/PDF, invalid/corrupt PDF, empty file, and oversized file; verify
  the app stays usable and failed uploads do not create indexed-document entries.
- Check no-key mode, no student, empty database, no documents, student switching,
  session history, and generation failure behavior.
- Run cumulative automated tests, build Phase 06 images, and run the test image.
- Start via Compose after init; verify health endpoint, browser reachability, and
  persisted documents/student data after stopping/restarting without deleting volumes.

## Exit gate and report

Automated and mandatory manual scenarios pass in Docker. Save
`docs/reports/PHASE_06_REPORT.md` with browser checklist, sanitized observations,
image IDs, difficulties, and manual actions. If browser access is unavailable,
request the exact user checks and keep the manual gate pending until observed.
