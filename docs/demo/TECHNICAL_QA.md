# Ten likely technical questions

1. **Why use SQL and RAG?** SQL retrieves exact typed records; semantic retrieval
   finds policy passages. Eligibility may require both; each source remains visible.
2. **Can the model execute SQL?** No. It selects names from four registered tools.
   Student identity comes from the selector/CLI; queries use `?` parameters and a
   read-only connection. Seeding is a separate write path.
3. **Why no LangChain?** Plain modules keep routing, storage, prompt construction,
   failures, and tests inspectable for this small demo.
4. **How are answers grounded?** Prompts receive only selected evidence, enforce
   structured sections, and request source tags. Local validation rejects invalid
   tags/schema. This does not prove semantic faithfulness; human review is separate.
5. **What if Gemini fails?** Bounded retries for 429/5xx, readable errors, keyword
   routing fallback, and a source-evidence view. No-key/local mode remains usable
   after local stores/model weights have been initialized.
6. **How are conflicts handled?** Preserve both dated statements. Ingestion time
   does not establish policy recency; a newer publication does not prove authority
   without supersession/effective-policy evidence. Keep eligibility and timing distinct.
7. **How do updates avoid duplicate/stale chunks?** Stable public chunk IDs plus
   revision-qualified internal vectors; an atomic manifest publishes the active
   version only after staging. Queries filter inactive revisions. Startup preserves
   replacements/deletions unless an explicit fixture refresh is requested.
8. **Why MiniLM/Chroma?** The configured CPU model produces normalized 384-dimensional
   vectors; Chroma persists a cosine collection. Top-k and threshold are configurable
   and must be assessed on measured examples, not assumed universally accurate.
9. **How is it evaluated?** Forty labeled synthetic questions, separate tuning/held-out
   figures, route/tool comparisons, eligible file hit@3, valid/invalid ingestion,
   wall/stage latency, and a separate 20-answer human claim/source review.
10. **Is it production-ready?** It is a local synthetic demo. Real student records
    require authentication and row-level authorization. Retrieval, policy authority,
    API availability, and prompt injection need broader testing. Images/volume setup
    are reproducible, but a model/API dependency is not an availability guarantee.
