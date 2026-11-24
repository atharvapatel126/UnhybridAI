# Phase 08 report — Evaluation and release

Status: Passed; user accepted the 20 listed answers in chat.
Verified: 2026-11-24 (Asia/Calcutta). Source prompts: P15, P17.

## Implementation

The 40-case labeled dataset, evaluation runner, per-query/aggregate CSVs, ingestion
probe, metadata, review worksheet and human-review scorer are implemented. Offline
and live runs are complete. Demo script, ten-slide outline, technical Q&A and
checklist are available. Results documentation now includes the completed live run.

Added `scripts.verify_release` for reproducible builds, uniquely isolated Compose
storage, container tests, runtime checks, and archive export/checksum/load/identity
verification. Added `scripts.release_probe` for actual missing-key routes, synthetic
fixture checks, uploads/rejection and restart preservation. Scratch data/log volumes
are separate from the working demo. Existing model cache reuse is read-only.
See `../RELEASE.md` for reproduction and portable-image startup instructions.

## Verification evidence

| Check | Actual command/procedure and result | Evidence |
| --- | --- | --- |
| Host suite | `.venv/Scripts/python.exe -m pytest -q`: 170 passed, exit 0; 101.23 s | `artifacts/phase08-host-tests-current.log` |
| Release workflow | `.venv/Scripts/python.exe -m scripts.verify_release --output artifacts/release --model-cache-volume dellproject_models`: exit 0, all 20 recorded checks passed | `artifacts/phase08-release-verification.log`, `artifacts/release/verification.json` |
| Final container suite | Isolated Compose test service, `HF_HUB_OFFLINE=1`: 170 passed, exit 0; 9.71 s, including real embeddings | `artifacts/release/container-tests.log` |
| Fresh initialization | New data/log volumes; existing read-only model cache: four policies and 25 students | `artifacts/release/fresh-init.log` |
| Runtime integration | `scripts.release_probe initial`: non-root; structured, document, hybrid, overdue and out-of-scope routes; missing-key fallback; upload/corrupt-file checks passed | `artifacts/release/runtime-probe.log` |
| UI/restart | Scratch UI on 8502: HTTP 200 before/after restart; repeated init retained database and manifest hashes including the uploaded fifth document | `artifacts/release/persistence-probe.log`, `verification.json` |
| Permissions | `scripts.check_container` in unmounted runtime: non-root, writable stores/cache/logs, no embedded `.env` | `artifacts/release/runtime-permissions.log` |
| Final-image live smoke | `docker compose run --no-deps --rm app python -m scripts.smoke_gemini`: exit 0, JSON success, 790.606 ms | `artifacts/phase08-live-smoke-current.log` |
| Browser rehearsal | Actual isolated Chrome: GPA/fees, attendance, hybrid, history clearing, local evidence and overdue variant passed; three primary chats generated answers | `artifacts/phase08-browser-rehearsal.log`, `artifacts/release/browser/` |
| Archive | Save, hash, re-read/hash, load, image ID comparison, loaded-image persistence smoke: all passed | `artifacts/release/verification.json`, archive logs |
| User-confirmed review scorer | `python -m scripts.score_review artifacts/evaluation/live`: exit 0; 20 answers, 28/28 supported factual rows and 28/28 accepted cited rows | `artifacts/evaluation/live/summary.json`, `review_status.json` |

Scratch project `unihybrid-release-a529fcad` was stopped with `compose down`; its
volumes remain. Working app is healthy at http://localhost:8501 on original volumes.

## Measured results

Offline: 40/40 routes, 40/40 exact tools, 19/20 retrieval hit@3, warm wall p50/p95
25.3/36.3 ms. Live: 40/40 routes, 39/40 tools, 18/20 retrieval hit@3, warm wall
p50/p95 7,144.6/24,959.1 ms. Both runs have 20 tuning and 20 held-out cases, each
with 20/20 routing correctness. Valid ingestion was 4/4; all three invalid controls
were rejected in each mode.

Live generated 21/29 answers with evidence available. Thirteen of 34 in-scope
cases showed evidence only: eight provider failures, five without evidence. Six
questions were out of scope. Structural citations were valid in 21/21 generated
answers. User-confirmed support/attribution are 28/28 existing draft factual rows
across 20 answers. These judgments reflect blanket chat acceptance, transcribed by
Codex, rather than separate per-claim comments. See `../EVALUATION_RESULTS.md` for
failures, denominators and provenance.

Preserved evaluation runs belong to their recorded image/source hashes. Final
release source identity differs; these are historical benchmark results, not a
new 40-query run of the final image. Final-image tests, real-model integration,
live smoke and browser rehearsal are recorded separately. A new benchmark must
use a new output directory and its own review cohort; preserve the user's worksheet.

## Images and portable artifact

- Runtime `unihybrid-ai:1.0.0` / `unihybrid-ai:phase-08`:
  `sha256:1060d0edbeaa179a45d8e5376a061f37002e72837750509530b62cf725d4f666`.
- Test `unihybrid-ai-test:1.0.0` / `unihybrid-ai-test:phase-08`:
  `sha256:074fb0cdff3b5a82d9ce965768ed956e2a88c96015644748a5e7f7c16d0337a2`.
- Linux amd64; user `app`; Python 3.13.14. Dependency freeze:
  `artifacts/release/dependencies.log`; source/config hashes: `source-identity.log`.
- Base `python:3.13.14-slim@sha256:9662417aace5ae7b8e2609cce472b72a8958e134ba372808abe9cc1a0c0125e6`.
- Runtime source SHA-256:
  `bd1444c4387cd20142472943e820589138d38f6a8426d6033480b63252ddbfef`.
- Archive `artifacts/release/unihybrid-ai-1.0.0.tar`: 722,785,280 bytes.
- SHA-256 `f0227ac77afc9c6e3d5d6ee2e091a294f9a6c0cf93a436f479cc51061aaae8b9`;
  checksum beside archive; loaded image identity matched the runtime above.

Archive/cache/runtime files are ignored by Git. The earlier archive directly under
`artifacts/` is historical; use `artifacts/release/`. No registry publication needed.

## Difficulties and limitations

Docker was initially stopped. Starting the installed Docker Desktop restored the
engine; builds and checks then passed. The first browser attempt encountered a
transient Streamlit rerender while finding Clear conversation. Repeating after
initialization passed the complete sequence.

Live provider 503/504/quota failures reduced generation availability; raw evidence
was preserved. Warm p95 exceeded the approximate ten-second goal. Broad/short
retrieval questions missed evidence. Synthetic fixtures and hand-authored labels
do not establish production accuracy. Authentication, OCR, conversational retrieval
and complete injection protection are outside scope. Scratch initialization reused
cached weights; no cold-download timing is claimed. The archive excludes credentials,
runtime data and model weights.

## User confirmation and exit gate

On 2026-11-24 the user said, "they are perfect build the next phase", after being
given the exact 20-answer review list. Codex transcribed that blanket acceptance
into the existing draft claim rows: factual support/citations yes, nonfactual and
evidence-only rows n/a. The reviewer alias is `User (chat confirmation)`; actual
timezone-aware recording time and the original confirmation are preserved in
`review_status.json`. No independent agent judgment or separate per-claim human
commentary is claimed. Compound draft rows were retained, so the 28-row count is
not an independently segmented count of atomic facts.

The original blank worksheet/status/summary were backed up under
`artifacts/evaluation/live/before-user-confirmation/`. Original answer snapshots
and dataset/results hashes were preserved. The scorer returned exit 0 with review
complete and no negative judgments. Phase 08 is Passed on this documented basis.

Required user action for the original roadmap: None. That roadmap ends at Phase
08; the requested next phase needs a feature scope before implementation begins.
