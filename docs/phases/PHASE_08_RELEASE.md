# Phase 08 — Evaluation, release images, and demo

Source prompts: P15, P17. P16 remains the repair workflow.
Dependency: Phase 07 passed. Status: Passed; automated checks passed and the user
accepted the 20 listed answers. See `../PROGRESS.md` and `../reports/PHASE_08_REPORT.md`.
Apply all shared implementation, testing, Docker, and reporting rules.

## Implementation instructions

1. Complete module/integration tests and expand `tests/eval_set.json` to at least
   40 labeled questions, including four routes, expected tools, applicable sources,
   key facts, ambiguous cases, and negative cases. Separate tuning/held-out splits.
2. Implement `scripts/evaluate.py` using the definitions in `../TESTING.md`.
   Write per-query and aggregate CSVs, configuration/snapshot metadata, failure
   counts, routing accuracy, tool correctness, retrieval hit@3, actual source
   attribution review results, ingestion success, and p50/p95 stage/total latency.
3. Run fallback and live modes separately. Separate cold downloads/initialization
   from warm responses. Do not estimate a missing metric or hide failed calls.
4. Manually score 20 answers by supported factual claims, documenting claim,
   citation, supporting evidence, and judgment. Optional LLM judge scores must be
   identified as optional automated judgments, not substituted for manual review.
5. Finish README with Windows/Linux/Docker setup, runtime configuration, init,
   upload/use, expected fallback, troubleshooting, model cache, and safe stop steps.
6. Create `docs/demo/DEMO_SCRIPT.md` for five minutes and three core scenarios plus
   overdue-fee variant, `SLIDE_OUTLINE.md` with ten slides, `TECHNICAL_QA.md` with
   ten likely technical answers, and `PRE_DEMO_CHECKLIST.md`.
7. Use only actual evaluated results in the slides. Explain synthetic-data scope,
   no authentication, retrieval limits, API quotas/latency, and injection limits.
   Select demo examples matching actual fixtures rather than copying PDF numbers.
8. Build final runtime/test images and export the runtime archive/checksum per
   `../DOCKER.md`. Record source identity, local image IDs, base digest, platform,
   pinned environment, file location, SHA-256, and verification results.

## Testing after this phase

- Run the full deterministic suite in the final test image; all mandatory assertions
  must pass. Run real-model retrieval, live API, and failure integration checks.
- Execute evaluation and verify CSV totals, denominator handling, percentile
  calculations, N/A cases, split labels, and reproducible configuration metadata.
- Complete the 20-answer human review and inspect every flagged unsupported claim.
  Fix critical defects and repeat affected tests/evaluation after code changes.
- Test a fresh Compose setup with isolated volumes, init, UI health, all demo
  routes, upload, missing-key fallback, and persistence through restart.
- Export/load the final image archive, verify checksum/image identity, and smoke
  the loaded image. Document first-run network/model-cache prerequisites honestly.
- Rehearse the five-minute demo and complete the pre-demo checklist. A recorded
  backup, if created, must show actual behavior and use synthetic data.

## Exit gate and report

All mandatory suites, live/manual checks, archive checks, and clean-start tests
pass. Evaluation artifacts and limitations are complete; no invented score appears
in documentation. Both final images exist and the portable runtime archive is
verified. Save `docs/reports/PHASE_08_REPORT.md`, update progress, and send the final
phase report with implementation, test/metric evidence, image/archive locations,
difficulties, remaining limitations, and manual requirements.

Potential user requirements: live API quota, manual answer review/browser checks
if unavailable to the implementer, and sufficient disk for the image archive.
No registry account is required for a local image/archive deliverable.
