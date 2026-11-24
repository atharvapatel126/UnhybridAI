# Phase 02 report — Documents and semantic retrieval

Status: Passed
Date: 2026-11-23 (Asia/Calcutta)
Source prompts: P04–P07

## Implemented

- Four reproducible synthetic documents: two PDFs, handbook TXT, and dated
  conflicting scholarship notices. Attendance evidence is on PDF page 4.
- Validated PDF/TXT/MD extraction, upload name/type/20 MB checks, readable corrupt,
  encrypted, scanned, empty, and unreadable-document errors.
- Page-bounded paragraph/sentence chunking, 500-character target, exact 80-character
  overlap, stable provenance IDs, publication dates, and ingestion timestamps.
- Cached CPU MiniLM embeddings, normalized 384-dimensional vectors, revision
  `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.
- Persistent cosine Chroma retrieval, score threshold 0.35, document listing/deletion,
  idempotent indexing, and atomic active-revision manifest for safe replacement.
- Host and Compose initialization pipeline: seed DB and ingest each file independently.
  Both demo stores contain four documents and nine chunks. Named model cache seeded
  from the downloaded host cache; test containers share only read-only weights.

## Testing performed after implementation

| Check | Command/procedure | Result | Evidence |
| --- | --- | --- | --- |
| Host cumulative suite including real model | `.venv/Scripts/python.exe -m pytest -q` | 47 passed, exit 0 | `artifacts/phase02-host-all-tests.log` |
| Final Docker suite, offline cache | `docker compose run --rm -e HF_HUB_OFFLINE=1 test` | 47 passed, exit 0 | `artifacts/phase02-container-tests-final.log` |
| Runtime/test builds | `docker build --target runtime/test ...:phase-02 .` | Both passed, exit 0 | `artifacts/phase02-runtime-build.log`, `artifacts/phase02-test-build-final.log` |
| Host ingestion | `python -m scripts.ingest_docs` | All 4 files succeeded | `artifacts/phase02-host-ingestion.log` |
| Offline Compose init | `docker compose run --rm -e HF_HUB_OFFLINE=1 init` | All 4 files succeeded | `artifacts/phase02-container-init.log` |
| Restart/persisted retrieval | Query from a separate fresh runtime container | 4 documents retained; expected policy in top 3 | `artifacts/phase02-persistence.log` |

Real deadline query top three: Scholarship_Policy.pdf page 2 (0.7173),
Notices_2026.txt page 1 (0.6735), Notices_2026.txt page 1 (0.6375).
These are measured fixture similarities, not general accuracy metrics. The fixed
unrelated astronomy query returned no matches above 0.35. Real embedding dimension,
normalization, semantic ordering, and attendance-page retrieval also passed.

Failure tests cover partial vector writes, failed manifest commit, failed stale
cleanup, invalid replacement, and visibility of only the active document version.
Re-ingestion count stability, shorter replacements, deletion, metadata, overlap,
page boundaries, and upload edge cases passed.

## Docker images

- Runtime `unihybrid-ai:phase-02`:
  `sha256:5ec00d79d49aeae923ce3d5b46e17b83342cf7ae0a81dfef4b11a714673a74a4`.
- Test `unihybrid-ai-test:phase-02`:
  `sha256:f31907b8c73013f9137cfd247a0e18606489804e23faa7654372c25e2c5386c4`.
- Linux amd64; pinned base and non-root user unchanged.

## Difficulties faced

- Fixture generator initially had a string concatenation syntax error; corrected
  before generation. Tests now generate and parse all fixtures successfully.
- A regression test caught sentence splitting taking precedence over paragraphs.
  Fixed boundary priority and verified overlap reconstruction and page integrity.
- Windows warned that its model cache could not use symlinks. Regular-file caching
  worked; offline Linux reuse was verified. No elevated permissions are required.
- Chroma upsert/delete is not a multi-operation transaction. Staged content uses
  revision-qualified internal vector IDs while preserving stable public chunk IDs;
  an atomically replaced manifest controls visibility. Failed cleanup cannot expose
  obsolete or incomplete revisions. Tests exercise this behavior.

## Manual requirements from the user

None for Phase 02. Initial model download is complete. Optional Windows symlink
optimization is unnecessary for correctness. A local Gemini key is now detected;
its value was not printed or copied into any image.

## Phase gate

Passed. Phase 03 eligible. Retrieval is implemented; classifier, generated answers,
and Streamlit remain pending. Multiple writing processes are outside this demo's
single-process ingestion design.

Implementation references:
[Chroma collection configuration](https://docs.trychroma.com/docs/collections/configure),
[SentenceTransformer API](https://sbert.net/docs/package_reference/sentence_transformer/model.html),
[PyMuPDF Page API](https://pymupdf.readthedocs.io/en/latest/page.html).
