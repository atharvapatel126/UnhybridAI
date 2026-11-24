# Phase 07 report — Logs and operational verification

Status: Passed
Verified: 2026-11-24 (Asia/Calcutta)
Source prompts: P14, P16 regression repair

## Implemented

- UTF-8 execution/prompt JSONL with schema version, timezone-aware UTC timestamps,
  shared request IDs, selected tools, chunk provenance/scores, stage timings,
  completion state, model/configuration, exact redacted prompts/responses, token
  usage when supplied, and retry attempt/error metadata.
- Per-request context is reset safely; query/LLM records correlate across stages.
  Execution summaries avoid duplicating entire source text. No environment dump.
- Nested/string secret redaction before disk writes. Size-bounded rotation retains
  configured backups without cutting JSON records. Thread-safe writes in one process.
- Logging failures preserve answers and surface warnings through orchestration/UI.
  All automated tests isolate logs from the active demo state.
- Non-destructive document bootstrap: a persistent completion marker prevents
  startup from undoing uploaded replacements or intentional deletions. Explicit
  `--refresh-fixtures` can restore bundled document names when requested.

## Testing performed after implementation

| Check | Command/procedure | Result | Evidence |
| --- | --- | --- | --- |
| Host cumulative suite | `.venv/Scripts/python.exe -m pytest -q` | 157 passed, exit 0 | `artifacts/phase07-host-tests-final.log` |
| Docker cumulative suite | `docker compose run --rm -e HF_HUB_OFFLINE=1 test` | 157 passed, exit 0 | `artifacts/phase07-container-tests-final.log` |
| Final image builds | `docker build --target runtime/test ...:phase-07 .` | Both passed, exit 0 | `artifacts/phase07-*-build-final.log` |
| Real query/trace | Runtime CLI GPA/fees question with configured key | Completed; 1 execution and 2 correlated prompt records; attempts [3,1] | `artifacts/phase07-live-query.json`; persisted Docker logs |
| Real key redaction scan | Compare configured key against all persisted log text without printing key | Passed | Runtime assertion/output |
| Restart/log/data persistence | Recreate app and inspect prior trace, marker, docs/students | Trace retained; 4 policies, 25 students; app healthy | Runtime assertions and Compose health |
| Bootstrap regression before fix | `pytest tests/test_bootstrap.py -q` | Reproduced replacement overwrite and missing completion marker | `artifacts/phase07-bootstrap-regression-before.log` |
| Real replacement/deletion restart | Dedicated scratch volume; initialize, replace policy with a synthetic GPA 9.0 rule, delete handbook; initialize in a second container | Both changes preserved; 3 scratch documents remain | Terminal assertions/output; `dellproject_phase07_bootstrap_check` volume |

Logging tests cover UTF-8/JSON/timestamps, two-call vs no-call cardinality, context
correlation/reset, current/rotated dummy-key redaction, usage counts, provenance
projection, 80 concurrent writes, rotation/retention, oversized records, unavailable
directories, and propagation of a simulated prompt-sink failure without answer loss.

## Difficulties faced

Code review found that repeated fixture ingestion could overwrite a user's same-name
policy replacement and recreate deleted seeded documents. A regression test first
demonstrated the overwrite. Added one-time bootstrap plus missing-file retry and an
explicit refresh option; unit and actual cross-container tests now pass. No active
user replacement was lost: reproduction used isolated test data.

Provider retries occurred during the live trace (classification required three
attempts), and both calls still correlated correctly. This reinforces the existing
availability/latency limitation; it is not recorded as a first-attempt success.

## Docker images

- Runtime `unihybrid-ai:phase-07`:
  `sha256:ab03be9fc33a19acf1f255a559c2b9908198f38a58f6164c8ac5973d3701a1ae`.
- Test `unihybrid-ai-test:phase-07`:
  `sha256:9605bd50f419d9c71c82c184760c12587f879cf35a241be61213eda3d70bd0c9`.
- Linux amd64, non-root. App on http://localhost:8501 is healthy.
- Actual log files live in the Compose `logs` named volume at `/app/logs`.

## Manual requirements from the user

None for Phase 07. Do not change log permissions or API credentials; actual writes
and redaction passed. The permission/disk failures above were deliberately simulated.

## Gate and limitations

Passed. Phase 08 eligible. Rotation is synchronized within a single application
process, matching this local demo; distributed/multiple-writer logging is outside
scope. Oversized records are rejected with a warning rather than truncated or
partially recorded. Formal evaluation and human faithfulness review remain pending.
