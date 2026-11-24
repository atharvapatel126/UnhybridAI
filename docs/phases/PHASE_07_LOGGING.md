# Phase 07 — Logging and operational verification

Source prompt: P14. Dependency: Phase 06 passed. Status: Passed. Results: [phase report](../reports/PHASE_07_REPORT.md).
Apply all shared implementation, testing, Docker, and reporting rules.

## Implementation instructions

1. Complete `src/utils/logger.py` around the existing adapter. Write UTF-8 JSONL
   with timezone-aware timestamps, request IDs, schema version, and bounded
   rotation/retention controlled by configuration.
2. `execution.jsonl`: one execution record per answered query, with query,
   synthetic student ID, route, method, selected tools, chunk IDs/scores,
   stage timings, errors, and completion state.
3. `prompts.jsonl`: one record per Gemini wrapper invocation with the exact
   application-sent prompt/system text and response after mandatory secret
   redaction, plus model, status, latency, usage if present, and retry metadata.
   Preserve traceability for failed calls without exposing exception secrets.
4. Clarify cardinality: a normal answered query may classify and generate, so it
   can create multiple prompt records; no-key/out-of-scope paths may create none.
   Do not force the PDF's “one line per log” wording to lose actual call history.
5. Redact secrets in nested fields, prompts, responses, headers, and errors before
   writing. Never log the entire environment. Test using dummy sentinels.
6. Handle log directory permission/disk errors gracefully: show a useful operational
   warning and retain the answer if possible. Keep runtime logs out of Git/image.
7. Verify writes/rotation in the non-root container using the mounted logs volume.

## Testing after this phase

- Parse every emitted line as JSON and validate required fields and timestamps.
- Verify one execution record per query and correct prompt counts for two-call,
  fallback, failed/retried, and out-of-scope paths; correlate by request ID.
- Inject dummy key values in prompts/responses/nested errors and prove none remain
  in current or rotated logs. Inspect files without printing a real secret.
- Test rotation, retention cap, repeated writes, invalid log directory, and write
  failure; confirm the main answer remains usable with a warning.
- Run focused logging tests, cumulative suite, and Phase 07 image/container checks.
  Execute one full query in Docker and inspect sanitized trace and persistence.

## Exit gate and report

Logs are parseable, bounded, traceable, and free of tested secret sentinels; required
failure tests pass. Save `docs/reports/PHASE_07_REPORT.md` with sample redacted
schema, image IDs, actual difficulties, and manual requirements from the user
(normally none).
