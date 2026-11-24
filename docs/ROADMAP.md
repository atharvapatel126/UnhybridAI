# Phased roadmap

Follow phases in order. A phase ends only after implementation, phase tests,
Docker verification, regression checks, and a written report. Report the result to
the user at each boundary; passing phases can proceed without routine approval.
Failures must be fixed and retested before proceeding. A missing required external
dependency is recorded as Blocked, with work resumed when it becomes available.

| Phase | PDF prompts | Deliverable | Exit evidence |
| --- | --- | --- | --- |
| 0 | P01, P02 | Skeleton, configuration, pinned environment, Docker build/test workflow | Host/container imports, no-key config import, image ID, test container exit code |
| 1 | P03, P08 | Seeded synthetic SQLite and whitelisted reads | Integrity, idempotency, correct results, read-only and injection tests |
| 2 | P04–P07 | Synthetic policies and persistent retrieval pipeline | Extraction edges, chunk invariants, real embeddings, relevant top-3, persistence |
| 3 | P11 | Single bounded Gemini client | Mocked failure suite plus live credentialed smoke call |
| 4 | P09, P10 | Validated routing and CLI evidence pipeline | 20-query labeled set, all routes, branch failures, keyless fallback |
| 5 | P12 | Grounded cited answers | Demo scenarios, missing/conflicting evidence, citation and injection tests |
| 6 | P13 | Streamlit chat and ingestion UI | UI smoke tests plus manual browser checklist and persistence restart |
| 7 | P14 | Redacted execution/prompt logging and rotation | JSONL validation, traceability, secret redaction, write-failure tests |
| 8 | P15, P17 | Full evaluation, demo materials, final Docker images | 40+ queries, measured CSV, 20-answer manual review, clean release smoke |

P16 applies during every phase: reproduce the issue, identify the cause, implement
the smallest fix, and add an appropriate regression test. Do not rewrite unrelated
modules. List unresolved issues and their impact in the phase report.

## Reporting and execution loop

1. Read the phase file and dependencies; identify any required user input early.
2. Implement its listed scope and update prompt execution records accurately.
3. Run phase tests and the cumulative applicable regression suite.
4. Build phase Docker image; run tests and applicable smoke checks inside it.
5. Save test evidence, image identity, and a report using the shared template.
6. Update `docs/PROGRESS.md` and send the user a boundary report covering what
   works, actual difficulties, test results, and exact manual requirements.
7. Continue only when this phase's gate is satisfied. Do not silently skip checks.

Phases 00–08 passed, with the Phase 08 review based on the user's recorded chat
acceptance. The original roadmap ends here; no Phase 09 scope has been defined.
See `PROGRESS.md`. The PDF's example results are not test evidence.
