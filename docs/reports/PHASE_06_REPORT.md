# Phase 06 report — Streamlit UI

Status: Passed
Started: 2026-11-23; verified: 2026-11-24 (Asia/Calcutta)
Source prompt: P13
Application: http://localhost:8501

## Implemented

- Streamlit UI with synthetic student selector, chat/session history, example
  questions, local-evidence mode, actual student/document counts, route badges,
  reason, answer, warnings, and source/SQL/document expanders.
- PDF/TXT/MD upload with a progress notice, shared backend size/name validation,
  safe temporary staging, indexed-document list, and success/error feedback.
- Cached embedding resource delegates to the core singleton. Rerenders do not
  repeat requests; student changes and successful document updates clear history.
- Missing-key, missing selection, empty-store, and unavailable-data notices.
  Raw document evidence is displayed as text, not executable document markup.
- Docker runtime launches Streamlit, binds only `127.0.0.1:8501`, waits for successful
  initialization, and has an HTTP health check. Minimal toolbar and expanded sidebar.

## Testing performed after implementation

| Check | Command/procedure | Result | Evidence |
| --- | --- | --- | --- |
| Host cumulative tests | `.venv/Scripts/python.exe -m pytest -q` | 147 passed, exit 0 | `artifacts/phase06-host-tests-final.log` |
| Final container suite | `docker compose run --rm -e HF_HUB_OFFLINE=1 test` | 147 passed, exit 0 | `artifacts/phase06-container-tests-final.log` |
| Image builds | `docker build --target runtime/test ...:phase-06 .` | Both passed | `artifacts/phase06-*-build-final.log` |
| Startup/health | `docker compose up -d app`; HTTP `/_stcore/health` | Healthy; HTTP 200/ok | Compose output and health response |
| Actual Chrome chats | `python tests/browser_scenarios.py chat` | All 3 routes generated answers; correct facts/source panels; history clear and local mode passed | `artifacts/phase06-browser-*.txt`, screenshots |
| Actual Chrome uploads | `python tests/browser_scenarios.py uploads` | Valid TXT/PDF indexed; corrupt/empty rejected; oversized file showed 20 MB error | `artifacts/phase06-upload-*.txt`, screenshot |
| Index integrity after invalid uploads | List indexed documents in runtime container | Only the 2 valid test fixtures added; no invalid names | Terminal assertion/output |
| Missing-key/empty/missing-selection browser checks | `python tests/browser_states.py` against scratch 8502/8503 and main app | All passed; real local GPA, missing-store/selection warnings, no guessed answer | `artifacts/phase06-no-key.txt`, `phase06-empty-state.txt`, `phase06-no-student.txt` |
| Restart/persistence | Stop app, remove only two owned test documents, start app | Original 4 policies and 25 students retained; app healthy | Terminal assertions and Compose health |

AppTest additionally verifies no-key/empty startup, student identity passed to
orchestration, one request per chat, history isolation, warnings, and both evidence
panel types. Upload unit tests cover safe staging/cleanup and invalid inputs.
Browser interaction was performed by the agent through headless Chrome and visual
screenshots; it is not claimed as a human answer-faithfulness evaluation.

## Difficulties faced

- Compose's test default tag initially still pointed at Phase 05: it ran 139 tests
  instead of the host's 147. Corrected the tag and reran the actual Phase 06 image;
  the final suite passed all 147. No stale-image result was accepted as final.
- Browser checks initially raced Streamlit's stale DOM during rerenders. Added
  spinner/response-count readiness and navigation/widget readiness waits.
- Headless Chrome's small default viewport collapsed the sidebar, making clicks
  miss offscreen controls. Set a desktop viewport and require visible coordinates.
  Corrected browser checks then completed real chat, selection, and upload flows.

## Docker images

- Runtime `unihybrid-ai:phase-06`:
  `sha256:aee0c096be9d5683313d36a6c9f224e31bf84bbd4d56909bfdcd28d5bd1f23d4`.
- Test `unihybrid-ai-test:phase-06`:
  `sha256:88983b66e453b1488b63c392c1767c4284db0f9cf329001eeba1ab4b32ff7c9c`.
- Linux amd64, non-root. Scratch empty/no-key containers removed; main app remains
  healthy on port 8501. Browser test fixtures removed from the document index.

## Manual requirements from the user

None for Phase 06. Open http://localhost:8501, select a synthetic student, and ask
a question. Keep the local key for AI mode; local-evidence mode remains available.
Reproduction instructions are in `docs/BROWSER_TESTING.md`.

## Phase gate and limitations

Passed. Phase 07 eligible. Uploaded original binaries are processed temporarily;
indexed text/provenance persist. Session history is not durable across app restarts.
Provider availability can still trigger evidence fallback; student selection is a
synthetic-demo shortcut, not authentication.
