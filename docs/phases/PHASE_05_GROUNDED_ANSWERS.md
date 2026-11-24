# Phase 05 — Grounded answers and citations

Source prompt: P12. Dependency: Phase 04 passed. Status: Passed. Results: [phase report](../reports/PHASE_05_REPORT.md).
Apply all shared implementation, testing, Docker, and reporting rules.

## Implementation instructions

1. Create `src/llm/answer.py` with `build_prompt(query, evidence)` and
   `format_sources(evidence)`. Reuse orchestration's evidence tags.
2. Separate trusted system rules from untrusted query/document content. Require
   answers based only on supplied evidence, inline `[SQL-n]`/`[DOC-n]` citations,
   explicit missing information, and concise Answer / Reasoning / Missing information
   sections. Reasoning means a short evidence explanation, not hidden model reasoning.
3. For conflicts, show both statements and cited dates. Identify newer publication
   only when evidenced; do not assume newer ingestion or a newer date automatically
   establishes authority or effective policy.
4. Validate that cited IDs exist in the provided bundle. Do not present an unsupported
   or invalidly cited generated response as verified; return a safe evidence view
   and warning when citation structure fails. Tag validity alone does not prove
   faithfulness; retain human review for claim support.
5. Wire generation into the orchestrator. With no evidence, state that evidence is
   unavailable instead of calling the model to invent an answer. With partial
   evidence, explain branch failures and avoid unsupported eligibility conclusions.
6. On generation failure, display raw retrieved evidence and sources with a clear
   fallback notice. Preserve timings/errors and avoid a second independent client.

## Testing after this phase

- Run the structured, attendance, and hybrid demo scenarios against actual seeded
  data/documents; include overdue and exact-threshold variants.
- Test missing deadline, missing fee term, absent profile, absent policy criteria,
  empty evidence, and conflicts with known vs unknown publication dates.
- Check each source maps to actual SQL rows or document chunks/pages; unknown
  generated citation tags trigger the safe fallback.
- Put “ignore previous instructions” in a document fixture; assert it remains
  untrusted content and cannot redirect tools or prompt construction. Review a live
  generated response as well; this mitigation is not a proof against all attacks.
- Mock generation timeout/blocked response and verify raw-evidence fallback.
- Run focused answer tests, cumulative tests, Phase 05 image/container tests, and
  live representative answers. Record failures accurately without invented outputs.

## Exit gate and report

Mandatory assertions pass; representative live answers cite actual sources and
the inspected claims are supported. Save `docs/reports/PHASE_05_REPORT.md` with
sanitized example answers, evidence, image IDs, difficulties, and manual actions.
Potential user requirement: restore API quota if live checks become blocked.
