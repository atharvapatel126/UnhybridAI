# Prompt execution log

## Phase 08 user acceptance and closeout

2026-11-24 (Asia/Calcutta): after receiving the selected 20-answer list, the user
confirmed, "they are perfect build the next phase". Recorded this as blanket user
acceptance, transcribed into the existing draft claim rows; preserved the original
blank artifacts and the unchanged answer/dataset hashes. Scorer exit 0: 20 answers,
28/28 supported factual rows and 28/28 cited rows accepted. This is not independent
agent scoring or separate per-claim human commentary. Updated Phase 08 to Passed
and synchronized release/progress/results documents. The roadmap ends at Phase 08;
requested clarification of scope for the next phase while completing this closeout.

The original PDF contains prepared prompts. After the user authorized building,
the entries below record actual execution; remaining Prepared entries are unexecuted.
Full entries retain the applied phase briefs and actual outcomes, including fixes.

## Phase 08 continuation — P15, P17

Date: 2026-11-24 (Asia/Calcutta). User request: "start building the remaining part".
Applied scope: `phases/PHASE_08_RELEASE.md` with shared implementation, Docker,
testing and reporting rules. Found completed offline/live evaluations and earlier
release artifacts; preserved the original responses and the user's claim worksheet.

Implemented `scripts.verify_release` and `scripts.release_probe`; built final
runtime/test images, ran 170 host and 170 final-container tests, verified isolated
fresh initialization, all four missing-key routes, uploads/rejection, HTTP health,
restart persistence and archive export/checksum/load/image identity/smoke. Live
Gemini smoke passed in 790.606 ms. Actual Chrome rehearsal passed three main chats,
history clearing, local evidence and overdue fees. Docker initially needed starting;
a transient browser rerender required repeating the browser run.

Updated measured results, release instructions, progress, checklist and
`reports/PHASE_08_REPORT.md`. Historical 40-query measurements retain their original
image/source provenance; final-image checks are recorded separately. Human support
and citation judgments remain pending, with scores N/A. Phase 08 stays In progress;
agent/browser inspection cannot satisfy its human-review requirement.

| Category | Prompt ID | Source | Phase | Status |
| --- | --- | --- | --- | --- |
| Requirement analysis | RA-01 | Supplied brief | Planning | Prepared |
| Architecture | AR-01 | Supplied architecture | Planning | Prepared |
| Code generation | CG-01 | P01 | 00 | Executed 2026-11-23 |
| Code generation | CG-02 | P02 | 00 | Executed 2026-11-23 |
| Code generation | CG-03 | P03 | 01 | Executed 2026-11-23 |
| Code generation | CG-04 | P04 | 02 | Executed 2026-11-23 |
| Code generation | CG-05 | P05 | 02 | Executed 2026-11-23 |
| Code generation | CG-06 | P06 | 02 | Executed 2026-11-23 |
| Code generation | CG-07 | P07 | 02 | Executed 2026-11-23 |
| Code generation | CG-08 | P08 | 01 | Executed 2026-11-23 |
| Code generation | CG-09 | P09 | 04 | Executed 2026-11-23 |
| Code generation | CG-10 | P10 | 04 | Executed 2026-11-23 |
| Code generation | CG-11 | P11 | 03 | Executed 2026-11-23 |
| Code generation | CG-12 | P12 | 05 | Executed 2026-11-23 |
| Code generation | CG-13 | P13 | 06 | Executed 2026-11-24 |
| Code generation | CG-14 | P14 | 07 | Executed 2026-11-24 |
| Testing | TS-01 | P15 | 08 | Executed 2026-11-24 |
| Presentation | PR-01 | P17 | 08 | Executed 2026-11-24 |

## Entry template (repeat under the appropriate category)

### ID — Title

- Category: RA / AR / CG / DB / TS / IN / PR
- Status: Prepared / Executed (date, actual model)
- Purpose:
- Source prompt and phase:
- Exact prompt text, including applied shared instructions:

```text
Paste the exact executed prompt here.
```

- Expected output:
- Actual outcome: Not run
- Changes after review:
- Files changed and test evidence:

## Debugging — DB-xx

Add one entry per actual bug using P16: reproduction, root cause, smallest fix,
regression test, and result. No bugs recorded yet.

## Integration — IN-xx

Add entries for actual integration work, including Docker work that has no original
P01–P17 code-generation ID. No integration work executed yet.

## Phase 00 execution ? CG-01, CG-02, IN-01

Date: 2026-11-23 (Asia/Calcutta). Agent: Codex; exact model identifier not exposed.
Status: Executed.

Exact user instruction:

```text
start building the project
```

Applied implementation brief (phase instructions, with the shared rules in `docs/IMPLEMENTATION_RULES.md`, `docs/TESTING.md`, and `docs/DOCKER.md`):

```markdown
# Phase 00 — Foundation, environment, and Docker

Source prompts: P01, P02. Dependency: none. Status: Prepared.
Read `../IMPLEMENTATION_RULES.md`, `../TESTING.md`, and `../DOCKER.md` first.

## Implementation instructions

1. Use this repository root as `unihybrid-ai/`; preserve the planning documents.
   Create `src/{db,ingest,rag,router,llm,utils}`, package initializers, `data/raw_docs`,
   `tests`, `scripts`, and ignored runtime directories for logs and artifacts.
2. Add `config.py`, `.env.example`, `.gitignore`, application requirements, and
   test requirements. Select compatible pinned versions after consulting current
   official package documentation. Record the tested Python version and platform.
3. Configure API key, Gemini model, data/log/cache paths, top-k, similarity threshold,
   chunk size/overlap, upload size, timeouts, retry bounds, and current fee term.
   Validate ranges and paths. `import config` must work without credentials.
4. Add the result types described in the shared rules and a minimal redacting log
   adapter, so subsequent modules can depend on stable interfaces.
5. Implement `scripts/check_env.py` to import installed dependencies and print
   versions without leaking environment values. Document host venv setup for
   PowerShell and Linux, plus the recommended Docker workflow.
6. Create Docker targets, Compose services, volumes, and build exclusions per
   `../DOCKER.md`. Keep the app service's future entry point documented; Phase 0
   runtime verification uses a config import, not a nonexistent Streamlit app.
7. Document embedding-model first download/cache behavior. Report actual dependency
   problems and fixes; do not guess a download size or claim compatibility untested.

## Required outputs

`config.py`, `src/contracts.py`, package skeleton, `requirements.txt`,
`requirements-dev.txt`, `.env.example`, `.gitignore`, `scripts/check_env.py`,
`Dockerfile`, `compose.yaml`, `.dockerignore`, setup README, and configuration tests.

## Testing after this phase

- Run `python -c "import config"` with no API key: success, no network request.
- Run `python scripts/check_env.py` on the intended host and in the test image;
  document a host limitation if the Docker environment is the only supported path.
- Test invalid numeric configuration and lazy missing-key validation.
- Confirm `.env` and runtime outputs are ignored by Git where initialized, and
  excluded from Docker context; use a dummy secret sentinel for inspection.
- Run `docker compose config --quiet`, build both Phase 00 images, and run the
  configuration tests in the test image. Smoke-import config in the runtime image.
- Confirm runtime user is non-root and writable mounted paths work.

## Exit gate and report

All required configuration/container checks pass. Save
`docs/reports/PHASE_00_REPORT.md`, record real image IDs and tested dependencies,
then update progress and send the boundary report. Do not proceed with a broken
container toolchain.

Potential user requirement: install/start Docker Desktop or resolve virtualization
if unavailable. No Gemini key is needed to pass this phase.

```

Expected: validated skeleton and verified Docker environment.
Actual: 15 host tests and 15 container tests passed, all seven imports passed on both platforms, images built and runtime permissions verified.
Review changes: start stopped Docker engine; propagate native process exit codes explicitly in PowerShell verification commands. See `reports/PHASE_00_REPORT.md`.

## Phase 01 execution ? CG-03, CG-08, IN-02

Date: 2026-11-23. Agent: Codex (exact model identifier not exposed).
Status: Executed under the same user instruction and shared rules as Phase 00.
Exact applied phase brief:

```markdown
# Phase 01 — Synthetic database and safe SQL

Source prompts: P03, P08. Dependency: Phase 00 passed. Status: Prepared.
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

```

Expected: synthetic schema and safe SQL. Actual: 25 cumulative host and container tests passed; repeat-container persistence and local seed verified. Review: improved boundary/overdue demo fixtures. See `reports/PHASE_01_REPORT.md`.

## Phase 02 execution ? CG-04 to CG-07, IN-03, DB-01

Date: 2026-11-23. Agent: Codex (exact model identifier not exposed).
Status: Executed under the same user instruction and shared rules as Phase 00.
Exact applied phase brief:

```markdown
# Phase 02 — Document ingestion, embeddings, and retrieval

Source prompts: P04, P05, P06, P07. Dependency: Phase 01 passed. Status: Prepared.
Apply all shared implementation, testing, Docker, and reporting rules.

## Implementation instructions

1. Create `src/ingest/extract.py`, `chunk.py`, `embed_store.py`, and
   `src/rag/retriever.py`. Add a reproducible script for synthetic PDF/TXT fixtures.
2. Create `Scholarship_Policy.pdf`, `Academic_Regulations.pdf`,
   `Student_Handbook.txt`, and `Notices_2026.txt`, clearly labeled
   `SYNTHETIC – DEMO ONLY`. Include merit criteria, academic rules, and dated
   conflicting deadline statements. Record actual page locations for tests.
3. Extract PDF through PyMuPDF and UTF-8 TXT/MD. Return page text and provenance
   in the extraction envelope. Reject unsupported types and files over 20 MB;
   skip empty pages and report no-extractable-text for scanned/empty documents.
   Corrupt/encrypted files return errors without crashing or partial ingestion.
4. Split within pages at paragraph/sentence boundaries, approximately 500 characters
   with 80 overlap. Bound long unbroken text, drop chunks under 30 characters,
   and avoid infinite loops. Document how overlap behaves near short boundaries.
5. Preserve source file, 1-based page, stable chunk ID, document type, ingestion
   timestamp, and available publication/effective dates. Distinguish TXT's logical
   page 1 from physical PDF pages. Hash canonical document identity + page + index.
6. Cache one local `all-MiniLM-L6-v2` model; batch size 32; normalized 384-dimensional
   embeddings. Empty input returns an empty result. Explain download failures.
7. Use one persistent cosine Chroma collection. Ingest through validated staging:
   unchanged re-ingestion keeps counts stable, replacement removes stale chunks,
   and failed replacement preserves the previously usable document. Add list/delete.
8. Retrieve using the same embedding model, configurable top-k and threshold;
   similarity = 1 - distance. Return sorted matches with chunk ID, text, file,
   page, score, dates, and structured empty-store/failure state.
9. Add an ingestion CLI/script and connect Compose init to seed then ingest fixtures.
   Keep real vector/model tests separate from fast mocked tests.

## Testing after this phase

- Extraction: valid multi-page PDF, TXT/MD, blank page, empty file, scanned PDF,
  corrupt/encrypted PDF, wrong type, oversized upload, unsafe filename/path.
- Chunking: stable IDs, page boundaries, metadata, short text, long paragraph,
  unbroken text, configured overlap, empty input, and invalid size/overlap values.
- Real embeddings: dimension 384, normalization, semantic similarity ordering,
  cached model reuse, and offline reuse after initial download.
- Real retrieval: scholarship-deadline query finds the expected source in top 3;
  fixed irrelevant query is rejected at the documented threshold. No fabricated scores.
- Test empty store, re-ingest stability, shorter changed-document replacement,
  deletion, per-file failure isolation, and persistence after container restart.
- Run focused ingestion/retrieval tests plus cumulative tests. Build Phase 02
  images and run real embedding/retrieval checks with the mounted model cache.

## Exit gate and report

All required tests, including real embedding and persistence checks, pass. Record
threshold/configuration and actual retrieval results in
`docs/reports/PHASE_02_REPORT.md`, with image IDs and actual difficulties.

Potential user requirement: network/disk availability for the first model download;
subsequent cached checks should work without downloading it again.

```

Expected: safe extraction and persistent semantic retrieval. Actual: 47 cumulative tests passed on host and offline Docker, four files/nine chunks persisted, actual top-3 scores recorded in Phase 02 report.
DB-01: regression caught paragraph boundary priority bug; fixed splitter to prefer paragraph boundaries, retaining the failing case and an exact overlap reconstruction assertion. Fixture generator syntax corrected before ingestion. See `reports/PHASE_02_REPORT.md`.

## Phase 03 execution ? CG-11, IN-04, DB-02

Date: 2026-11-23. Agent: Codex (exact model identifier not exposed).
Status: Executed under the same user instruction and shared rules as Phase 00.
Exact applied phase brief:

```markdown
# Phase 03 — Reliable Gemini client

Source prompt: P11. Dependency: Phase 02 passed. Status: Prepared.
Apply all shared implementation, testing, Docker, and reporting rules.

## Implementation instructions

1. Consult current official Gemini `google-genai` documentation before coding;
   record the SDK version, valid configured model, timeout units, JSON mode, and
   retry behavior actually verified. Avoid obsolete SDK examples.
2. Implement one `src/llm/gemini_client.py` wrapper with
   `generate(prompt, system=None, json_mode=False, temperature=0.1)` and typed
   `LLMUnavailable`/`LLMBadResponse` exceptions.
3. Validate credentials lazily. Bound each attempt to 15 seconds and permit at most
   two application retries with bounded backoff for retryable 429/5xx errors.
   Configure or account for SDK retries so they do not multiply attempts silently.
4. Distinguish missing/invalid key, quota, network, timeout, blocked/empty response,
   and malformed output. Do not retry permanent validation/authentication errors.
5. State the maximum client budget including backoff, and the later two-call
   classification/generation budget. Keep the approximate 10-second target separate
   from these failure bounds. Expose measured latency and retry count.
6. Record redacted latency, model, and token usage when returned. The minimal log
   adapter supports later full logging without duplicating wrapper code.
7. Add `scripts/smoke_gemini.py` or an equivalent live test entry point. Read runtime
   secrets from the local environment; do not print them or bake them into images.

## Testing after this phase

- Mock success, JSON mode, absent key, invalid key, 429, 5xx, timeout, network loss,
  blocked/empty response, and malformed response. Assert types and clear messages.
- Use a fake clock/sleeper to verify retry counts and backoff without slow tests.
- Verify permanent errors do not retry and default SDK retries are accounted for.
- Check prompt/exception logs using a dummy key sentinel; key must not appear.
- Run focused wrapper tests and cumulative tests. Build Phase 03 images and run
  deterministic tests in the test image without credentials.
- Run one live smoke call in the container with a locally supplied key, recording
  sanitized result, model, timestamp, and elapsed time. Do not label a mock live.

## Exit gate and report

Mocked failure tests and the live smoke must pass before this phase is Passed.
If credentials/quota/network are unavailable, report Blocked after completing
independent work; do not silently omit the live gate. Save
`docs/reports/PHASE_03_REPORT.md` with image IDs, measured timings, difficulties,
and the exact unblock action.

Potential user requirement: set `GEMINI_API_KEY` locally and enable valid model
access/quota. Never request the secret value in chat.

```

Expected: reliable SDK wrapper with live smoke and safe failures. Actual: 65 cumulative host/container tests passed; final live JSON smoke passed at 27597.610 ms. DB-02: metadata endpoints worked but generation failed; sanitized provider diagnosis identified 3.8 high demand, switched default to live-verified 3.6. Provider also rejected a 5-second diagnostic deadline; config now requires >=10 seconds. See `reports/PHASE_03_REPORT.md`.

## Phase 04 execution ? CG-09, CG-10, IN-05

Date: 2026-11-23. Agent: Codex (exact model identifier not exposed).
Status: Executed under the same user instruction and shared rules as Phase 00.
Exact applied phase brief:

```markdown
# Phase 04 — Routing and CLI orchestration

Source prompts: P09, P10. Dependency: Phase 03 passed. Status: Prepared.
Apply all shared implementation, testing, Docker, and reporting rules.

## Implementation instructions

1. Implement `src/router/classifier.py` using the single Gemini wrapper. A strict
   JSON/few-shot prompt produces route, requested tool names, document query, and
   reason. Expose the shared `sql_tools` field even if upstream uses `needs_sql_tools`.
2. Validate schema, route enum, tool names, and route/tool consistency. Reject
   hallucinated tools and malformed output. Return `method=llm` or `fallback`.
3. Add deterministic keyword fallback for GPA/records/fees, rules/policies/deadlines,
   hybrid combinations, and irrelevant queries. Test ambiguous phrases explicitly.
   HYBRID scholarship eligibility must fetch profile and fees plus policy evidence.
4. Create a labeled 20-query `tests/eval_set.json` with all four routes, expected
   tools, document sources where applicable, and edge cases.
5. Implement `answer_query(query, student_id)` in `src/orchestrator.py`. Bind identity
   from the UI/CLI, call only registered tools, resolve department context safely,
   and use a policy-focused document query for hybrid questions.
6. Label SQL/document evidence once, isolate branch failures, and collect route,
   evidence, sources, readable errors, request ID, and per-stage/total timings.
   Until Phase 5, return a clearly labeled deterministic evidence summary.
7. OUT_OF_SCOPE returns without answer generation or retrieval/SQL tools. A missing
   selected student prevents student-specific reads but need not block a valid
   document branch. Unknown IDs never produce a fabricated profile.
8. Add a thin `src/cli.py` so all routes can run before implementing the UI.

## Testing after this phase

- Test valid/malformed JSON, unknown route/tool, timeout, and no-key fallback.
- Run the labeled set in deterministic fallback mode and separately with mocked
  LLM outputs. Report measured counts; fix required fixture misroutes, rather than
  relaxing expectations or reporting mocked routing as live accuracy.
- Test one full CLI query for each route, call counts/selected tools, missing
  student, unknown student, empty vectors, and failure of each hybrid branch.
- Assert LLM content cannot change selected student ID or execute arbitrary SQL.
- Assert OUT_OF_SCOPE avoids answer generation and evidence retrieval; classification
  itself may use Gemini unless deterministic short-circuiting is implemented.
- Run focused router/orchestrator tests, cumulative suite, and Phase 04 container
  tests. Smoke the runtime CLI in all four modes and with credentials disabled.

## Exit gate and report

All four routes execute through the CLI and required failure paths pass. Save
`docs/reports/PHASE_04_REPORT.md`, including route counts, image IDs, difficulties,
and any manual requirements. No new user input is normally needed.

```

Expected: four-route CLI evidence pipeline. Actual: 122 cumulative host/container tests passed; 20/20 deterministic routing fixtures, separate mocked JSON contract checks, and all four actual offline CLI scenarios passed. No new failures observed. See `reports/PHASE_04_REPORT.md`.

## Phase 05 execution ? CG-12, IN-06, DB-03 to DB-06

Date: 2026-11-23. Agent: Codex (exact model identifier not exposed).
Status: Executed under the same user instruction and shared rules as Phase 00.
Exact applied phase brief:

```markdown
# Phase 05 — Grounded answers and citations

Source prompt: P12. Dependency: Phase 04 passed. Status: Prepared.
Apply all shared implementation, testing, Docker, and reporting rules.

## Implementation instructions

1. Create `src/llm/answer.py` with `build_prompt(query, evidence)` and
   `format_sources(evidence)`. Reuse orchestration's evidence tags.
2. Separate trusted system rules from untrusted query/document content. Require
   answers based only on supplied evidence, inline `[SQL-n]`/`[DOC-n]` citations,
   explicit missing information, and concise Answer / Reasoning / Missing information
   sections. Reasoning means a short evidence explanation, not hidden model reasoning.
3. For conflicts, show both statements and cited dates. Identify newer publication
   only when evidenced; do not assume newer ingestion or a newer date automatically
   establishes authority or effective policy.
4. Validate that cited IDs exist in the provided bundle. Do not present an unsupported
   or invalidly cited generated response as verified; return a safe evidence view
   and warning when citation structure fails. Tag validity alone does not prove
   faithfulness; retain human review for claim support.
5. Wire generation into the orchestrator. With no evidence, state that evidence is
   unavailable instead of calling the model to invent an answer. With partial
   evidence, explain branch failures and avoid unsupported eligibility conclusions.
6. On generation failure, display raw retrieved evidence and sources with a clear
   fallback notice. Preserve timings/errors and avoid a second independent client.

## Testing after this phase

- Run the structured, attendance, and hybrid demo scenarios against actual seeded
  data/documents; include overdue and exact-threshold variants.
- Test missing deadline, missing fee term, absent profile, absent policy criteria,
  empty evidence, and conflicts with known vs unknown publication dates.
- Check each source maps to actual SQL rows or document chunks/pages; unknown
  generated citation tags trigger the safe fallback.
- Put “ignore previous instructions” in a document fixture; assert it remains
  untrusted content and cannot redirect tools or prompt construction. Review a live
  generated response as well; this mitigation is not a proof against all attacks.
- Mock generation timeout/blocked response and verify raw-evidence fallback.
- Run focused answer tests, cumulative tests, Phase 05 image/container tests, and
  live representative answers. Record failures accurately without invented outputs.

## Exit gate and report

Mandatory assertions pass; representative live answers cite actual sources and
the inspected claims are supported. Save `docs/reports/PHASE_05_REPORT.md` with
sanitized example answers, evidence, image IDs, difficulties, and manual actions.
Potential user requirement: restore API quota if live checks become blocked.

```

Expected: grounded cited answers with failure fallback. Actual: 139 cumulative host/container tests passed; seven successful live scenarios inspected across baseline and targeted retests, failures preserved. DB-03: schema/nonempty missing field. DB-04: grouped/unknown/bare citations. DB-05: omitted fee-tool dependency. DB-06: absent excerpt vs whole-document claims and eligibility vs deadline distinction. Provider instability prompted a verified default change to 3.5 Flash-Lite. Full causes, fixes, artifacts, and limitations: `reports/PHASE_05_REPORT.md`.

## Phase 06 execution ? CG-13, IN-07

Started 2026-11-23; verified 2026-11-24 (Asia/Calcutta). Agent: Codex (exact model identifier not exposed).
Status: Executed under the same user instruction and shared rules as Phase 00.
Exact applied phase brief:

```markdown
# Phase 06 — Streamlit application

Source prompt: P13. Dependency: Phase 05 passed. Status: Prepared.
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

```

Expected: usable Streamlit demo with uploads and evidence panels. Actual: 147 host/container tests passed; Chrome observed three live generated routes, actual facts/panels, history isolation, local mode, valid/invalid uploads, no-key and empty states. Restart retained original data. Fixed stale Compose test tag and browser viewport/rerender readiness issues. See `reports/PHASE_06_REPORT.md`.

## Phase 07 execution ? CG-14, IN-08, DB-07

Date: 2026-11-24 (Asia/Calcutta). Agent: Codex (exact model identifier not exposed).
Status: Executed under the same user instruction and shared rules as Phase 00.
Exact applied phase brief:

```markdown
# Phase 07 — Logging and operational verification

Source prompt: P14. Dependency: Phase 06 passed. Status: Prepared.
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

```

Expected: bounded redacted trace logs. Actual: 157 host/container tests passed; a real request correlated one execution with two prompt records, key scan passed, logs persisted after restart. DB-07: reproduced initializer overwriting replacements/recreating deletions; implemented one-time bootstrap and explicit refresh, then verified preserved changes in a second real container using a scratch volume. See `reports/PHASE_07_REPORT.md`.
