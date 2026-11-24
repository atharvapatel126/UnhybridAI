# Phase 04 report — Routing and CLI orchestration

Status: Passed
Date: 2026-11-23 (Asia/Calcutta)
Source prompts: P09, P10

## Implemented

- Strict JSON classifier for STRUCTURED, UNSTRUCTURED, HYBRID, OUT_OF_SCOPE;
  registered-tool checks, route consistency checks, no identity/SQL arguments from
  the model, and deterministic keyword fallback on any LLM/parse/validation failure.
- Twenty labeled routing questions in `tests/eval_set.json` (tuning set).
- Orchestrator binds selected student identity, derives department context from an
  allowed profile query, isolates failed branches, and labels evidence/sources.
- Thin CLI supports a true no-Gemini `--offline` mode and returns route, reason,
  method, SQL/document evidence, sources, errors, request ID, and stage timings.
- Shared evidence helpers prevent duplicating tag/source/fallback logic in Phase 05.

## Testing performed after implementation

| Check | Command | Result | Evidence |
| --- | --- | --- | --- |
| Host cumulative suite | `.venv/Scripts/python.exe -m pytest -q` | 122 passed, exit 0 | `artifacts/phase04-host-tests.log` |
| Docker cumulative suite | `docker compose run --rm -e HF_HUB_OFFLINE=1 test` | 122 passed, exit 0 | `artifacts/phase04-container-tests.log` |
| Runtime/test builds | `docker build --target runtime/test ...:phase-04 .` | Both passed, exit 0 | `artifacts/phase04-*-build.log` |
| Four actual CLI routes | Four subprocess invocations of `python -m src.cli ... --student S-012 --offline` in runtime Compose container | All expected routes and branch counts, no errors, exit 0 | `artifacts/phase04-cli-smoke.log` |

Fallback route/tool assertions: 20/20 on this fixed tuning fixture. Separately,
20 mocked LLM outputs passed schema/route contract tests; this is not a live LLM
accuracy measurement. Other cases cover invalid JSON/schema/tool/identity fields,
API failure, branch isolation, unknown/missing student, no documents, selected-tool
call counts, identity binding, department resolution, and out-of-scope short circuit.

Actual offline CLI timings: structured 1.95 ms, documents 3849.42 ms, hybrid
3592.06 ms, out-of-scope 0.27 ms. Document paths include cold process/model startup;
these four samples are not latency percentiles. Generation is not yet implemented.

## Docker images

- Runtime `unihybrid-ai:phase-04`:
  `sha256:5a9db2ea40d75e94350d08c75165ef3eddf211c98e2dc5fd9a27f9bd4eeddfc0`.
- Test `unihybrid-ai-test:phase-04`:
  `sha256:9ca4b86f638b619932ddbac8995636a6dd128bf6d4bbd78feefe9826be87b7a8`.
- Linux amd64, non-root, pinned base unchanged.

## Difficulties faced

No new failing tests observed. Ambiguity handling deliberately distinguishes a
policy GPA threshold from a request for the selected student's GPA. Department
stats require an explicit profile tool dependency so hidden additional tools are
not run. Rules remain coarse outside the tested questions.

## Manual requirements from the user

None.

## Phase gate

Passed. Phase 05 eligible. CLI currently shows transparent raw evidence, not a
generated eligibility conclusion. No live routing accuracy claim is made.
