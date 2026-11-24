# Testing instructions and acceptance gates

Testing is mandatory after every phase, including Docker execution. Use fixtures
and temporary paths for database, vectors, uploads, and logs; never modify the
developer's active demo state during tests. Actual measurements are recorded in
`EVALUATION_RESULTS.md`; the definitions below remain applicable.

## Standard verification loop

1. Run the phase's focused tests and capture command, date, exit code, and summary.
2. Run all applicable tests from earlier phases to detect integration regressions.
3. Build the phase's runtime and test images and execute the suite in the test image.
4. Run a suitable runtime smoke check, including mounted persistence once present.
5. Complete any phase-specific live or manual checks and save sanitized evidence.
6. Fix failures using P16, retest the affected behavior, and complete the phase report.

Use `python -m pytest -q` as the cumulative automated suite after tests exist.
Use explicit markers such as `live`, `model`, and `manual` to distinguish tests that
need Gemini credentials, real downloaded embeddings, or browser interaction.
Show skipped tests and reasons; never silently convert them into passes.

Mocks verify deterministic control flow. Real model tests verify embedding and
retrieval integration. A live Gemini smoke verifies SDK, credential, and network
integration. Manual review verifies answer faithfulness and the demo experience.
All four kinds have separate evidence; they cannot substitute for each other.

## Core acceptance scenarios

| Scenario | Required behavior |
| --- | --- |
| GPA and fee status | STRUCTURED; values match selected synthetic student and term; SQL sources shown |
| Attendance rule | UNSTRUCTURED; correct academic document and actual page cited |
| Scholarship eligibility and deadline | HYBRID; profile, fees, and policy support conclusion and citations |
| Overdue-fee student | Eligibility reflects policy and actual outstanding fees |
| Irrelevant cricket question | OUT_OF_SCOPE; no answer-generation call or invented result |
| Unknown or malformed student | Clear missing/invalid result without guessed data |
| Empty document collection | Explicit missing-document result; structured branch still works |
| Conflicting deadline notices | Both shown; dates compared only when evidenced; ambiguity acknowledged |
| Invalid/oversized/encrypted/empty upload | Readable error; no app crash or partial indexed document |
| No Gemini key, timeout, rate limit, blocked output | Bounded failure; routing fallback and raw evidence notice |
| Missing policy fact | Explicitly unavailable; no outside-knowledge completion |
| Injection in document | Instruction ignored; no secrets, arbitrary tools, or unsupported answer |
| SQL injection in ID | Validation/rejection; tables and rows unchanged |
| Re-ingest and document replacement | No duplicates; stale chunks removed; safe delete |
| Container restart | Database/vector persistence retained; no accidental reseed duplicates |

## Evaluation in Phase 8

Expand the 20-question route set to at least 40 questions, covering four routes,
ambiguity, missing data, and failure paths. Store expected routes, tools, sources,
and key facts. Use null/not-applicable for irrelevant fields instead of inventing
an expected document for SQL-only or out-of-scope questions. Separate tuning examples
from held-out evaluation and record which split each result uses.

| Metric | Definition and evidence |
| --- | --- |
| Routing accuracy | Correct routes / all labeled routing examples; report counts and mode (live/fallback) |
| Tool selection | Exact expected tool set vs actual tool set for applicable queries |
| Retrieval hit@3 | Queries with expected source in first three results / eligible document queries |
| Attribution correctness | Supported cited claims / reviewed cited claims; inspect cited text, not just tag existence |
| Faithfulness | Supported factual claims / factual claims in 20 manually reviewed answers; preserve claim checklist |
| Latency | p50/p95 in ms for total and each stage; report sample count and percentile method |
| Ingestion success | Successful files / attempted files, with deliberate-invalid cases labeled separately |

Write per-query rows and summaries to CSV under ignored `artifacts/evaluation/`.
Include configuration, dataset revision/hash, model identifier, dependency/image
identity, warm/cold state, failures, retries, and measurement timestamps. An optional
LLM judge must be labeled separately from human review. Undefined metrics are N/A
with a reason, never zero or a fabricated score.

Correctness gates require all mandatory deterministic assertions to pass and no
unresolved critical source/safety failure. Report empirical route and retrieval
metrics honestly; agree targets before tuning rather than retroactively lowering
them. The approximate 10-second warm latency goal is assessed with actual results;
record misses and timeout budgets instead of presenting it as a guaranteed limit.
