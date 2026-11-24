# UniHybrid AI

Phases 00–07 are verified: the Docker Streamlit assistant runs at
**http://localhost:8501** with synthetic records, document retrieval, and grounded
answers/source panels and redacted request logs. Final release images, portable
archive, and automated checks are verified. Phase 08 passed after the user's
acceptance of the 20 review answers; provenance is recorded in the report.
The plan analyses **UniHybrid AI – Architecture & Implementation Prompt Pack.pdf**
(12 pages) and adds the user's requirements: mandatory Docker images, testing after
every phase, and a report of implementation, difficulties, and user actions.

Start with [the roadmap](docs/ROADMAP.md), read [the analysis](docs/PROMPT_ANALYSIS.md),
then follow [the implementation rules](docs/IMPLEMENTATION_RULES.md).

| Phase | Instructions | Status |
| --- | --- | --- |
| 0 | [Foundation, environment, Docker](docs/phases/PHASE_00_FOUNDATION.md) | Passed |
| 1 | [Synthetic database and safe queries](docs/phases/PHASE_01_DATABASE.md) | Passed |
| 2 | [Documents, embeddings, and retrieval](docs/phases/PHASE_02_RETRIEVAL.md) | Passed |
| 3 | [Gemini client and dependency failures](docs/phases/PHASE_03_GEMINI.md) | Passed |
| 4 | [Routing and CLI orchestration](docs/phases/PHASE_04_ORCHESTRATION.md) | Passed |
| 5 | [Grounded answers and source validation](docs/phases/PHASE_05_GROUNDED_ANSWERS.md) | Passed |
| 6 | [Streamlit application](docs/phases/PHASE_06_UI.md) | Passed |
| 7 | [Logging and operational checks](docs/phases/PHASE_07_LOGGING.md) | Passed |
| 8 | [Evaluation, release images, and demo](docs/phases/PHASE_08_RELEASE.md) | Passed |

Supporting instructions:

- [Final project report: technologies, architecture, tests, evaluation, and release](FINAL_PROJECT_REPORT.md)
- [Docker strategy and image deliverables](docs/DOCKER.md)
- [Testing and evaluation gates](docs/TESTING.md)
- [Phase report template](docs/reports/PHASE_REPORT_TEMPLATE.md)
- [Progress tracker](docs/PROGRESS.md)
- [Prompt execution log](docs/prompt_log.md)
- [Measured results](docs/EVALUATION_RESULTS.md)
- [Evaluation and human-review instructions](docs/EVALUATION_GUIDE.md)
- [Five-minute demo](docs/demo/DEMO_SCRIPT.md)
- [Release verification and portable image](docs/RELEASE.md)
- [Phase 08 results and review confirmation](docs/reports/PHASE_08_REPORT.md)

## Foundation setup

Use Python 3.13.14 and Docker Desktop in Linux container mode. Direct dependency
versions are pinned; imports and foundation tests pass on Windows and Linux containers.
No API key is required for setup or local configuration tests.

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -c "import config"
.\.venv\Scripts\python.exe scripts/check_env.py
.\.venv\Scripts\python.exe -m pytest -q
```

Linux:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
if [ ! -f .env ]; then cp .env.example .env; fi
.venv/bin/python -c 'import config'
.venv/bin/python scripts/check_env.py
.venv/bin/python -m pytest -q
```

Docker (current Phase 08):

```text
docker compose config --quiet
docker compose build
docker compose run --rm init
docker compose run --rm test
docker compose up -d app
docker compose ps
docker compose down
```

Open http://localhost:8501 after startup. Select a synthetic student for personal
questions; policy questions can run without selection. Upload PDF/TXT/MD and click
Index document. Original upload binaries are temporary; indexed text persists.
Choose Use local evidence only to disable Gemini requests. Student changes clear
history; session history does not survive a server restart.
`docker compose down` preserves named volumes. Do not add `--volumes` unless you
intend to erase demo state. The runtime and test images are tagged by `PHASE`
(default `08`). A missing `.env` is supported; runtime credentials are optional.

Document initialization runs once and preserves uploaded replacements/deletions on
restart. To deliberately restore/re-index the four bundled fixture names, use:

```text
docker compose run --no-deps --rm init python -m scripts.ingest_docs --refresh-fixtures
```

That explicit refresh replaces indexed copies of those bundled names; other
uploaded names remain. Default startup does not perform that replacement.

Execution and redacted prompt/response logs persist in the `logs` named volume
(`/app/logs`). Defaults: 5 MB per active file and three rotated backups. A logging
failure warns without discarding the answer. Avoid multiple application processes
writing the same demo stores/logs concurrently.

Ask through the CLI (remove `--offline` for grounded Gemini answers):

```text
docker compose run --rm app python -m src.cli "What is my GPA and fee status?" --student S-012 --offline
docker compose run --rm app python -m src.cli "What is the minimum attendance?" --offline
docker compose run --rm app python -m src.cli "Am I eligible for a merit scholarship?" --student S-012 --offline
```

Remove `--offline` to allow Gemini classification and answer generation. With it, no Gemini request is
made. Local embeddings still require an initially populated model cache.

For live Gemini verification, set `GEMINI_API_KEY` in local `.env` and run:

```text
docker compose run --rm app python -m scripts.smoke_gemini
```

The current verified default is `gemini-3.5-flash-lite`. Change `MODEL_NAME` locally if needed.
Network/model-list diagnostics: `python -m scripts.diagnose_gemini` in the configured
environment. Earlier 3.6 calls took 17–28 seconds; a Lite smoke took 1.8 seconds.
There is no established latency guarantee. SDK timeout is 10–15 seconds per attempt, with up to two retries on
429/5xx; total call time can exceed a single-attempt timeout.

Seed/query on the host:

```powershell
.\.venv\Scripts\python.exe -m src.db.seed
.\.venv\Scripts\python.exe -c "from src.db.queries import get_student_profile; print(get_student_profile('S-012'))"
```

All seeded records are synthetic. Seeding is safe to rerun and preserves existing
records. Query helpers open SQLite read-only; they never execute model-generated SQL.

Initial ingestion downloads model weights; dependency checking does not. Model
downloads and package installation need network access. The named `models` volume
caches weights for later reuse; tests mount it read-only, so run `init` before the
full suite on a fresh installation. Offline cache reuse is verified. Exact download
size is not measured.

Host document setup (synthetic fixtures are already included):

```powershell
.\.venv\Scripts\python.exe -m scripts.create_demo_docs
.\.venv\Scripts\python.exe -m scripts.ingest_docs
```

Ingestion supports PDF/TXT/MD up to 20 MB, with no OCR. Conflicting notices are
intentional. Vector scores use `1 - cosine distance`; default threshold is 0.35.
Repeated ingestion does not duplicate chunks. Failed replacements keep the active
document usable. Internal vector IDs include revision IDs; public chunk IDs remain
stable. One application process owns ingestion writes.

For dependency errors, use the pinned Python version, a fresh virtual environment,
and `python -m pip check`. Prefer the Docker CPU environment if a host Torch wheel
is unavailable. Chroma requires supported binary wheels; inspect the installation
log before adding build tools or changing versions. Actual fixes belong in reports.

Later phase commands in the planning files become runnable as implemented.
See `docs/PROGRESS.md` and individual reports for actual verification status.
