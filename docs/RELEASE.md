# Local release 1.0.0

Verified 2026-11-24 (Asia/Calcutta). Automated release checks passed. The user
accepted the 20 review answers in chat; Phase 08 is Passed. The recorded review
uses blanket user acceptance, transcribed into existing draft claim rows.

## Reproduce the release verification

Start Docker Desktop in Linux container mode. From the repository, after the
normal initialization has populated the model cache:

```powershell
.\.venv\Scripts\python.exe -m scripts.verify_release `
  --output artifacts/release-new --model-cache-volume dellproject_models
```

Linux equivalent:

```bash
.venv/bin/python -m scripts.verify_release \
  --output artifacts/release-new --model-cache-volume dellproject_models
```

Adapt the cache volume name if the checkout uses a different Compose project.
An existing verification report is never overwritten. The script builds the
runtime/test `1.0.0` and `phase-08` tags, runs all tests, initializes fresh data/log
volumes, checks non-root permissions, all routes with an explicitly blank key,
uploads, UI health on port 8502, restart preservation, and portable image export,
checksum, load, identity, and loaded-image smoke. It saves per-command logs and
`verification.json`, dependency freeze, and source/configuration hashes.

The cache is mounted read-only when supplied. Omit `--model-cache-volume` to create
a fresh model volume and download weights during init; that requires network.
The verified run reused cached weights, so it does not measure cold downloads.
Choose `--port` if 8502 is occupied. The script stops its uniquely named scratch
Compose project and preserves its volumes. It leaves the normal application/data
volumes intact. Retained scratch volume names derive from the recorded project.

`scripts.release_probe` is an actual runtime integration probe. Its write phase
refuses any data directory whose final component is not `release-check-state`.
Use it only through the isolated verification workflow.

## Portable runtime image

Current verified files:

- `artifacts/release/unihybrid-ai-1.0.0.tar` (722,785,280 bytes).
- `artifacts/release/unihybrid-ai-1.0.0.tar.sha256`.
- `artifacts/release/verification.json` (image IDs, checksum, check results).

SHA-256: `f0227ac77afc9c6e3d5d6ee2e091a294f9a6c0cf93a436f479cc51061aaae8b9`.

Verify before loading on Windows:

```powershell
$archivePath = 'artifacts/release/unihybrid-ai-1.0.0.tar'
$expectedHash = ((Get-Content "$archivePath.sha256") -split '\s+')[0]
if ((Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash -ne $expectedHash) {
    throw 'Archive checksum mismatch'
}
docker load -i $archivePath
```

On Linux, run `sha256sum -c unihybrid-ai-1.0.0.tar.sha256` from `artifacts/release`,
then `docker load -i unihybrid-ai-1.0.0.tar`. Loaded runtime image ID must match
`verification.json`. The archive contains code, pinned dependencies, and synthetic
fixtures. Mutable data, logs, API credentials, and model weights are separate.

To use the loaded image with the repository's normal Compose setup:

```text
docker tag unihybrid-ai:1.0.0 unihybrid-ai:phase-08
docker compose run --no-deps --rm init
docker compose up -d --no-build app
docker compose ps
```

First initialization downloads weights unless the model cache is already populated.
Set credentials in local `.env` for generated answers; without them the application
shows original evidence. Open http://localhost:8501. Stop with `docker compose down`;
named volumes remain. No registry account is needed.

## Review record and repeat scoring

The user's 2026-11-24 chat confirmation is recorded in `review_status.json`.
The scorer reports 28/28 supported factual rows and 28/28 correct cited rows
across 20 answers, based on that blanket acceptance. Original blank files are
preserved under `artifacts/evaluation/live/before-user-confirmation/`.

For a subsequent detailed review, follow `EVALUATION_GUIDE.md` for the answers in
`artifacts/evaluation/live/HUMAN_REVIEW.md`. Enter the judgments in `claims.csv`
and reviewer identity/time in `review_status.json`, then run:

```powershell
.\.venv\Scripts\python.exe -m scripts.score_review artifacts/evaluation/live
```

Exit 2 means pending review. Automated checks and browser inspection cannot fill
this human requirement. Preserve the recorded hashes and original answers.
