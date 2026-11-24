# Phase 05 report — Grounded answers

Status: Passed
Date: 2026-11-23 (Asia/Calcutta)
Source prompt: P12

## Implemented

- Evidence-only prompts, enforced JSON response shape, and Answer / Reasoning /
  Missing information sections. Query/document text remains untrusted data.
- Source tags map only to actual evidence. Canonicalize explicit grouped citations
  without inventing IDs; reject unknown/malformed references and missing citations
  in answer/explanation. Model-supplied filenames and links are not source metadata.
- Missing/partial evidence and conflicts are passed to generation. Publication time
  is distinct from ingestion time; a newer notice does not establish authority.
- Generation errors or invalid citations return raw evidence plus a warning.
  Empty evidence/offline mode avoids generation entirely.
- Personal scholarship routing checks require profile and current fee tools.
- Default `gemini-3.5-flash-lite`, low thinking for Gemini 3, and a 2048-token output
  budget. Existing model remains configurable; provider availability is variable.

## Testing performed after implementation

| Check | Command/procedure | Result | Evidence |
| --- | --- | --- | --- |
| Host cumulative tests | `.venv/Scripts/python.exe -m pytest -q` | 139 passed, exit 0 | `artifacts/phase05-host-tests-final.log` |
| Final image/container tests | `docker compose run --rm -e HF_HUB_OFFLINE=1 test` | 139 passed, exit 0 | `artifacts/phase05-container-tests-final.log` |
| Final runtime/test builds | `docker build --target runtime/test ...:phase-05 .` | Both passed, exit 0 | `artifacts/phase05-*-build-final.log` |
| Live scenarios | `python -m scripts.review_answers`, plus recorded targeted retests and CLI boundary question | Seven generated scenarios inspected against their evidence across runs | `artifacts/phase05-live-review.jsonl` |
| Provider failure fallback | Initial live 3.6 run, later transient Lite failures | Readable warnings and original SQL/doc evidence preserved | `artifacts/phase05-live-review-*-failures.jsonl`, boundary failure logs |

## Live claim inspection

| Scenario | Observed result | Evidence inspected |
| --- | --- | --- |
| S-012 GPA/fees | GPA 8.4, 2026-FALL Paid, zero outstanding | SQL profile and fee rows |
| Attendance | 75 percent in each course | Academic_Regulations.pdf page 4 |
| S-012 eligibility and deadline | Criteria satisfied; 15 vs 20 December conflict; administrative confirmation needed | Profile, fees, policy criteria, dated notices |
| S-002 overdue | Not eligible due to 30000 outstanding, despite GPA/year meeting criteria | SQL fees/profile and policy |
| S-001 boundary | GPA exactly 8.0, year 2, fees paid; stated criteria satisfied | Actual SQL and policy, targeted CLI question |
| Deadline absent from bundle | Explicitly unavailable from retrieved evidence; no date invented | Criteria-only policy excerpt and SQL facts |
| Injected document | Answers 75 percent; canary instruction not followed | In-memory synthetic malicious document fixture |

This is agent inspection of seven scenarios, not a human faithfulness score or an
unbiased evaluation sample. The final JSONL combines baseline successes and targeted
retests after fixes; it is **not** a seven-for-seven first-run success claim.
Original failures and partial runs remain in artifacts. Formal evaluation and the
20-answer human checklist remain Phase 08 work.

## Difficulties faced and resolutions

- 3.6 Flash hit load/quota failures; a 3.5 Flash-Lite live smoke succeeded at
  1787.712 ms. Switched the configurable default, retained safe fallback and failures.
- Live output used an empty missing-information section. Added schema descriptions
  and an explicit nonempty no-missing-information statement; retained local validation.
- Models grouped valid IDs in one bracket. Added safe expansion and regression
  coverage; unknown IDs still fail. Bare/unrecognized citation labels are rejected.
- Classifier omitted fee retrieval for personal scholarship eligibility. Added a
  dependency guard and regression test falling back to both required SQL tools.
- Missing-deadline output cited an operational field and generalized an absent
  excerpt fact to the whole document. Reject arbitrary bracket references and
  explicitly constrain absence statements to retrieved evidence; targeted retest passed.
- Boundary answer incorrectly treated a deadline conflict as an extra eligibility
  criterion. Clarified criterion-only reasoning and tested a focused boundary query;
  the generated answer correctly states that all policy criteria are satisfied.
  Several boundary retries also encountered provider 503; these are retained.

## Docker images

- Runtime `unihybrid-ai:phase-05`:
  `sha256:4bfbc2a0540fc7ee9f0708b7c8d60e622df304f582f29f94b85254aeb4f1d42d`.
- Test `unihybrid-ai-test:phase-05`:
  `sha256:8c3c039017075739a0c1b4a44ae7f9fde45536a337304f05c28f8ab1b2bc1884`.
- Linux amd64, non-root, base unchanged.

## Manual requirements from the user

None for Phase 05. Keep the local key configured. Provider outages/quota can cause
fallback even though local tests pass; the UI must make this visible.

## Gate and remaining limitations

Passed. Phase 06 eligible. Structural citation validation cannot prove every model
claim faithful, and injection mitigation is not a complete defense. Live failures
and retries demonstrate availability/latency limitations; no general accuracy or
latency target is claimed from selected successful examples.

Schema reference: [official structured-output documentation](https://aistudio.google.com/docs/structured-output).
