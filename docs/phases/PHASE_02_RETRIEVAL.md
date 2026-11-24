# Phase 02 — Document ingestion, embeddings, and retrieval

Source prompts: P04, P05, P06, P07. Dependency: Phase 01 passed. Status: Passed. Results: [phase report](../reports/PHASE_02_REPORT.md).
Apply all shared implementation, testing, Docker, and reporting rules.

## Implementation instructions

1. Create `src/ingest/extract.py`, `chunk.py`, `embed_store.py`, and
   `src/rag/retriever.py`. Add a reproducible script for synthetic PDF/TXT fixtures.
2. Create `Scholarship_Policy.pdf`, `Academic_Regulations.pdf`,
   `Student_Handbook.txt`, and `Notices_2026.txt`, clearly labeled
   `SYNTHETIC – DEMO ONLY`. Include merit criteria, academic rules, and dated
   conflicting deadline statements. Record actual page locations for tests.
3. Extract PDF through PyMuPDF and UTF-8 TXT/MD. Return page text and provenance
   in the extraction envelope. Reject unsupported types and files over 20 MB;
   skip empty pages and report no-extractable-text for scanned/empty documents.
   Corrupt/encrypted files return errors without crashing or partial ingestion.
4. Split within pages at paragraph/sentence boundaries, approximately 500 characters
   with 80 overlap. Bound long unbroken text, drop chunks under 30 characters,
   and avoid infinite loops. Document how overlap behaves near short boundaries.
5. Preserve source file, 1-based page, stable chunk ID, document type, ingestion
   timestamp, and available publication/effective dates. Distinguish TXT's logical
   page 1 from physical PDF pages. Hash canonical document identity + page + index.
6. Cache one local `all-MiniLM-L6-v2` model; batch size 32; normalized 384-dimensional
   embeddings. Empty input returns an empty result. Explain download failures.
7. Use one persistent cosine Chroma collection. Ingest through validated staging:
   unchanged re-ingestion keeps counts stable, replacement removes stale chunks,
   and failed replacement preserves the previously usable document. Add list/delete.
8. Retrieve using the same embedding model, configurable top-k and threshold;
   similarity = 1 - distance. Return sorted matches with chunk ID, text, file,
   page, score, dates, and structured empty-store/failure state.
9. Add an ingestion CLI/script and connect Compose init to seed then ingest fixtures.
   Keep real vector/model tests separate from fast mocked tests.

## Testing after this phase

- Extraction: valid multi-page PDF, TXT/MD, blank page, empty file, scanned PDF,
  corrupt/encrypted PDF, wrong type, oversized upload, unsafe filename/path.
- Chunking: stable IDs, page boundaries, metadata, short text, long paragraph,
  unbroken text, configured overlap, empty input, and invalid size/overlap values.
- Real embeddings: dimension 384, normalization, semantic similarity ordering,
  cached model reuse, and offline reuse after initial download.
- Real retrieval: scholarship-deadline query finds the expected source in top 3;
  fixed irrelevant query is rejected at the documented threshold. No fabricated scores.
- Test empty store, re-ingest stability, shorter changed-document replacement,
  deletion, per-file failure isolation, and persistence after container restart.
- Run focused ingestion/retrieval tests plus cumulative tests. Build Phase 02
  images and run real embedding/retrieval checks with the mounted model cache.

## Exit gate and report

All required tests, including real embedding and persistence checks, pass. Record
threshold/configuration and actual retrieval results in
`docs/reports/PHASE_02_REPORT.md`, with image IDs and actual difficulties.

Potential user requirement: network/disk availability for the first model download;
subsequent cached checks should work without downloading it again.
