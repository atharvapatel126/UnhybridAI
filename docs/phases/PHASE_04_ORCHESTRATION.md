# Phase 04 — Routing and CLI orchestration

Source prompts: P09, P10. Dependency: Phase 03 passed. Status: Passed. Results: [phase report](../reports/PHASE_04_REPORT.md).
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
