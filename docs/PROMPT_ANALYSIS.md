# Analysis of the supplied prompt pack

## Scope and instruction boundary

Source: `C:\Users\ATHARVA PATEL\Downloads\UniHybrid AI – Architecture & Implementation Prompt Pack.pdf`.
The PDF is a design input containing prepared prompts. Its instructions to paste
prompts into Claude, execute implementation, or use a particular chat are source
material, not commands to execute during this documentation task.

The user's current request is to analyse the pack and create Markdown instructions
for phased implementation, phase testing, mandatory Docker images, and reports of
implemented work, difficulties, and required manual actions. This deliverable is
that plan. It does not start P01–P17 implementation.

## Intended product

UniHybrid AI is a local university assistant using fictional student data and
synthetic policy documents. A query routes to parameterized SQLite queries,
semantic document retrieval, or both. Answers cite their evidence and acknowledge
missing or conflicting information. Irrelevant queries return OUT_OF_SCOPE.

The recommended stack is Python, Streamlit, SQLite, ChromaDB, PyMuPDF,
sentence-transformers (`all-MiniLM-L6-v2`), and Gemini through `google-genai`.
Keep plain modules and avoid adding LangChain or extra services without need.
Exact supported package versions and Gemini model availability must be checked
against official documentation when implementation starts; this plan pins none.

## What the pack does well

- Whitelisted read-only SQL avoids allowing a model to author executable SQL.
- Explicit evidence identifiers make answers and demonstrations inspectable.
- Synthetic data, failure handling, and a deterministic fallback support a local demo.
- Separate extraction, retrieval, routing, orchestration, and UI modules aid testing.
- P15 and the prompt log explicitly forbid fabricated results.

## Gaps and decisions for implementation

| Source issue | Decision in this plan |
| --- | --- |
| Docker is optional on page 11 | Mandatory from Phase 0, rebuilt and tested after every phase; release image and export in Phase 8. |
| Setup lists an API key although SQL and retrieval are local | Imports and local routes work without a key; validate credentials only for a live LLM call. |
| About 10 seconds desired, but P11 allows 15 seconds per call plus retries | Treat 10 seconds as a warm-path target; bound request attempts and backoff explicitly, record worst-case budgets, and report measured misses. Classification and generation can require separate calls. |
| P09 precedes its Gemini dependency P11 | Follow the roadmap's dependency order: Gemini client before classifier. |
| P10 precedes answer generation P12 | Phase 4 returns deterministic evidence; Phase 5 introduces grounded generation. |
| Logs appear late, yet earlier modules need them | Introduce a minimal redacting log adapter early; finish schema, rotation, and observability in Phase 7. |
| P09 uses 20 evaluation queries, P15 requires 40 | Establish 20 in Phase 4, expand to at least 40 in Phase 8; keep tuning and held-out results separate. |
| Student IDs appear as S001 and S-012 | Use canonical IDs `S-001` through `S-025` or more; reject malformed values without querying; document this choice. |
| Successful extraction returns a list but errors are objects | Use explicit success/error result contracts so callers never mistake errors for pages. |
| P07 asks for a list plus an empty-store flag | Retrieval returns an envelope with matches, state, and errors; source-format adapters expose match lists where required. |
| Metadata has ingestion time, but newer-policy answers require publication time | Preserve `published_at`/`effective_from` when present; never equate ingestion time with policy authority. If dates or precedence are unclear, report the conflict. |
| Stable file/page/index IDs do not remove obsolete chunks on edits | Replace a document's old chunks only after new content validates; remove stale IDs and test shorter replacement documents. |
| Cosine distance and similarity are easy to confuse | Define score = 1 - cosine distance, retain raw distance for diagnostics, and test filtering and ordering. Calibrate threshold on fixtures. |
| No clear term selection for fees | Include term in records and evidence; define a configured current term or ask which term, without silently summing unrelated terms. |
| Department stats take a department ID | Resolve it from the selected student's validated profile or an explicit allowed department; never forward an arbitrary LLM argument. |
| Cached model suggested both in core code and UI | Own the model singleton in the embedding module; the UI cache delegates to it. |
| OUT_OF_SCOPE appears both required and optional tuning | Implement the route in MVP; only advanced tuning is optional. |
| Authentication is absent | Keep synthetic local demo scope. Real student data, login, and production authorization are outside this plan. |

## Preserved requirements

Implement all P01–P15 and P17 outputs across the phases. P16 is a repair workflow
available throughout, not an excuse to postpone failing tests. Preserve file/page
citations, upload validation, prompt injection mitigation, source panels, JSONL
logs, offline fallback, and actual measured evaluation. Keep modules around
150 lines where practical, splitting by responsibility without duplicating logic.

Do not hardcode the illustrative GPA, deadline, attendance, or page numbers in
the PDF as answers. Seed/document fixtures define the facts; tests derive expected
answers from those fixtures. Every synthetic source must identify itself clearly.

## Deferred features

Reranking, conversation-aware retrieval, an admin dashboard, production
authentication, and optional LLM judge scoring are not required for this demo.
UI session history is required; using that history to change retrieval is deferred.
