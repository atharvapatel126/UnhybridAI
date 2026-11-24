# Measured evaluation results

Measured: 2026-11-24 (Asia/Calcutta). Synthetic corpus only.
Both recorded 40-question evaluations are complete. The user accepted the 20
listed review answers as perfect in chat on 2026-11-24. Existing draft claim rows
were filled from that blanket acceptance; no separate per-claim comments were
supplied. These measurements describe the image/source hashes in each
run's metadata; they are not a new benchmark of the final release image.

| Metric | Offline mode: 40 questions | Live mode: 40 questions |
| --- | --- | --- |
| Route correctness | 40/40 | 40/40 |
| Held-out / tuning route correctness | 20/20 / 20/20 | 20/20 / 20/20 |
| Exact selected tool sets | 40/40 | 39/40 |
| Retrieval file hit@3 | 19/20 eligible document questions | 18/20 |
| Valid-file ingestion | 4/4 | 4/4 |
| Deliberately invalid files rejected | 3/3 | 3/3 |
| All ingestion attempts | 4 successes / 7 attempts, including invalid controls | 4/7 |
| Warm query wall latency p50 / p95 | 25.3 / 36.3 ms | 7,144.6 / 24,959.1 ms |
| Generated answers | 0, by design | 21/29 queries with nonempty evidence |
| Evidence-only output for in-scope queries | 34/34 | 13/34 (8 generation failures, 5 without evidence) |
| Routing fallback | 40/40, by design | 2/40 |
| Queries with warnings | 4/40 | 13/40 |
| Structural citation validity | N/A | 21/21 generated answers |
| User-accepted support / citation review | Not measured; N/A | 28/28 / 28/28 draft factual rows across 20 answers |

Sources: `artifacts/evaluation/{offline,live}/summary.json`, `results.csv`,
`results.jsonl`, `ingestion.csv`, and `metadata.json`. Percentiles include all 40 queries after model warmup; they
exclude delays between queries and are not cold-download timings.

The retrieval miss was Q012, “How many books can I borrow?” The short raw query
returned no match above threshold 0.35; the system exposed missing evidence rather
than inventing a lending limit. These hand-authored results do not establish
real-world accuracy.

Live retrieval also missed Q008 (the library-hours question). Q003
selected an extra profile tool, so its exact tool-set label failed even though the
courses answer was available. Eight generation failures preserved raw evidence:
five HTTP 503, one HTTP 504, and two quota/rate-limit responses. The other five
in-scope evidence-only cases had no supplied evidence, including deliberately
missing records/facts. All calls remain in the latency/routing cohorts.

Live warm p95 exceeds the approximate ten-second goal. Bounded per-attempt timeouts
and retries do not guarantee a ten-second end-to-end response. Valid source tags
are structural checks; they do not measure claim support or citation correctness.

Final release verification on 2026-11-24 passed 170 container tests, real-model
scratch initialization, all four missing-key routes, upload/restart checks, and
archive checksum/load/smoke checks. A separate final-image live Gemini smoke took
790.6 ms. Those checks are recorded in `artifacts/release/verification.json` and
`artifacts/phase08-live-smoke-current.log`; the single-call smoke is not a latency
benchmark. The original evaluation source hash differs from the final source hash;
preserved runs must retain their original provenance.
