# Phase 00 — Foundation, environment, and Docker

Source prompts: P01, P02. Dependency: none. Status: Passed. Results: [phase report](../reports/PHASE_00_REPORT.md).
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
