# Mandatory Docker deliverables

Docker packaging is required by the user, overriding its optional status in the PDF.
Phase images and final 1.0.0 images are implemented. Automated release verification
and portable archive instructions are in `RELEASE.md`; user review acceptance is
recorded in the Phase 08 report. The requirements below remain applicable.

## Image design

Create these files in Phase 0: `Dockerfile`, `compose.yaml`, `.dockerignore`, and
`requirements-dev.txt` alongside the pinned application dependencies.

- Use a compatible Linux Python base selected after package compatibility checks;
  pin the base version and record its digest for the final release.
- Build a common `base` stage and separate `test` and `runtime` targets. The test
  target includes pytest and evaluation tooling; runtime omits test-only packages.
- Install compatible pinned dependencies in a cacheable layer before copying source.
- Run as a non-root user and verify write access to mounted runtime directories.
- Do not copy `.env`, host virtual environments, logs, SQLite/vector runtime stores,
  downloaded model cache, or image archives into the image.
- Use a shared cache for the embedding model; document first download separately
  from offline reuse. Do not claim cold startup is offline-capable.

## Compose services and storage

| Service | Role | Contract |
| --- | --- | --- |
| `app` | Streamlit runtime | Bind container port 8501 to local host `127.0.0.1:8501`; configured health check |
| `test` | Test image | Execute pytest and explicitly selected verification commands; propagate exit codes |
| `init` | One-shot data setup | Seed synthetic database and ingest fixtures once commands exist; safe to rerun |

SQLite and ChromaDB are embedded libraries in this design; they do not require
separate database server images. Add server services only if the architecture changes.

Use named volumes for data, logs, and model cache; keep raw committed fixtures
available in the image or a distinct read-only fixture mount. Bootstrap writes
`data/university.db`; application SQL connections open it with `mode=ro`.
Run the app only after successful initialization. Keep one application instance
for this local demo; avoid concurrent ingestion from separate processes.

Pass `GEMINI_API_KEY` through a runtime environment configuration. Loading a missing
optional `.env` must not prevent the no-key tests or local fallback from starting.
Document all paths and make them work without Windows-specific paths inside Linux.

## Required image names and checkpoints

After each phase `NN`, build local images:

- `unihybrid-ai:phase-NN` using target `runtime`.
- `unihybrid-ai-test:phase-NN` using target `test`.

Record build command, exit code, architecture, base digest when resolved, local
image IDs, and smoke command in that phase report. Local IDs are available before
publishing; do not call them registry digests. Each tag must correspond to an actual
successful build, and container tests must run against that phase's source.

Example command pattern (replace `NN` with the actual two-digit phase):

```text
docker version
docker compose config --quiet
docker build --target runtime -t unihybrid-ai:phase-NN .
docker build --target test -t unihybrid-ai-test:phase-NN .
docker run --rm unihybrid-ai-test:phase-NN python -m pytest -q
docker image inspect unihybrid-ai:phase-NN
```

Keep Compose service builds/tags consistent with the active checkpoint through a
non-secret phase variable or documented overrides. `docker compose run --rm test`
must test the active image, not a stale `latest` tag. Container test fixtures use
isolated temporary storage, not the demo database volume.

Before Streamlit exists, use configuration imports, dependency verification, and
then the CLI as runtime smoke commands. Introduce the app health check in Phase 6;
do not configure a nonexistent HTTP service as healthy in Phase 0.

## Final release

In Phase 8, build `unihybrid-ai:1.0.0` and `unihybrid-ai-test:1.0.0` from final source.
Validate a fresh setup and a restart retaining indexed data. Check local health at
`http://localhost:8501/_stcore/health` after the app starts. Verify the process user
is non-root and that missing credentials produce the documented fallback.

Create a portable runtime image archive and checksum, for example:

```text
docker save -o artifacts/unihybrid-ai-1.0.0.tar unihybrid-ai:1.0.0
docker load -i artifacts/unihybrid-ai-1.0.0.tar
```

Ensure `artifacts/` exists first. Calculate SHA-256 using the host platform's tool
and save it beside the archive. Verify the loaded image ID and run a smoke check.
The image alone does not contain mutable volumes or a downloaded model cache;
provide reproducible init instructions and document the first-run network need.
Keep the archive out of Git. Registry publication is unnecessary for this local
deliverable and needs a chosen registry/account if requested later.

Never remove volumes as a routine stop step. Document `docker compose down` for
stopping; clearly identify any separate destructive reset command and its scope.

## Potential manual requirements

If unavailable, the user must install/start Docker Desktop with Linux containers
and any required Windows virtualization support. First builds and model downloads
need network access and sufficient local disk space. Record actual requirements
or failures when encountered rather than assuming Docker has been verified.
