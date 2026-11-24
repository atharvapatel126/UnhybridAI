# Evaluation and human review

The canonical `tests/eval_set.json` contains 40 synthetic university questions:
20 tuning fixtures and 20 additional held-out labels. These are hand-authored
examples, not a representative real-university benchmark. Tuning fixtures run in
router unit tests; held-out measurements are reported separately.

## Run a new measurement

Initialize the demo and model cache first. Use a new output directory for each run;
the evaluator refuses to overwrite recorded responses or an earlier partial run.

```powershell
$evaluationImageId = docker image inspect unihybrid-ai:phase-08 --format '{{.Id}}'
docker compose run --no-deps --rm `
  -v 'D:\Projects\DellProject\artifacts:/app/artifacts' `
  -e HF_HUB_OFFLINE=1 -e LOGS_DIR=/app/artifacts/evaluation/new-run/trace_logs `
  app python -m scripts.evaluate --mode live --pause 1 `
  --output /app/artifacts/evaluation/new-run --image-id $evaluationImageId
```

Use `--mode offline` for deterministic routing and evidence-only answers. That mode
makes no Gemini requests. `HF_HUB_OFFLINE=1` controls only model-cache access, so live
Gemini requests still work. Adapt the host mount to your checkout path on Linux.
On the host, `python -m scripts.evaluate --mode offline --output artifacts/evaluation/new-run`
uses the same implementation and host cache.

## Artifacts and definitions

- `results.jsonl`: every original query, expected label, actual response, evidence,
  error, and outer wall-clock duration. API failures/fallbacks stay in the cohort.
- `results.csv`: per-query route/tool comparisons, top-three sources, warnings,
  generation mode, stage timings, request ID, and measured wall time.
- `ingestion.csv`: four valid fixtures plus corrupt/empty/unsupported controls,
  ingested into a separate probe store. Report valid-file success and invalid-file
  rejection separately from overall successes/attempts.
- `metadata.json`: dataset/source/database/manifest hashes, actual dependency
  versions, embedding revision, configured model, image identity, settings, and
  cache/warmup state. No secrets.
- `summary.json` / `metrics.csv`: actual routing/tool accuracy, eligible retrieval
  hit@3, structural citation validity, generation availability, and p50/p95 latency.
  Percentiles use `(n-1)*q` linear interpolation. Pauses between queries are excluded.
- Query latency is measured after the real ingestion probe, which normally warms
  the embedding model. Startup/download and probe duration are recorded separately.
  Outer wall time includes logging; orchestrator stage totals precede final log I/O.

Expected key facts are reviewer reference annotations, not an automatic faithfulness
score. A valid citation ID proves only that a supplied source was referenced; it
does not prove the source contains the generated claim. Undefined/manual metrics
remain JSON null / CSV N/A rather than fabricated values.

## Required 20-answer human review

The live run produces `HUMAN_REVIEW.md`, `claims.csv`, and `review_status.json` for
the first 20 non-out-of-scope cases in dataset order. This deterministic sample is
limited and includes fallback output if it occurred; it is not selected for success.

1. Read each actual answer and its supplied SQL/document evidence in the Markdown file.
2. In `claims.csv`, confirm the draft sentence boundaries. Split compound factual
   claims/add omitted claims; these draft rows are not an AI judgment of correctness.
3. For each factual claim, enter `yes` or `no` in `supported`. For cited factual
   claims, enter `yes` or `no` in `citation_correct` after inspecting the cited source.
   For uncited factual claims, use `n/a` for citation correctness.
4. For nonfactual or evidence-only rows, verify the output and enter explicit `n/a`
   in both judgment columns. Do not mark unsupported factual claims nonfactual.
5. Fill your reviewer name/alias and actual timezone-aware ISO review time in
   `review_status.json`; leave its dataset/results hashes intact.
6. Run the scorer; it returns exit 2 for pending review and does not invent scores:

```powershell
.\.venv\Scripts\python.exe -m scripts.score_review artifacts/evaluation/live
```

The scorer checks cohort coverage, timestamps, judgments, and the original results
hash before computing supported factual claims / all factual claims and correct
cited claims / reviewed cited claims. Nonfactual/evidence-only rows are excluded
from those ratios. Report the actual claim/sample counts with every score.

Only human-entered judgments satisfy this gate. Agent/browser inspection and an
optional LLM judge must be labeled separately and cannot substitute for it. Resolve
flagged critical unsupported claims before marking Phase 08 complete.
