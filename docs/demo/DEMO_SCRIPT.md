# Five-minute demo

All names, records, policies, and dates are synthetic. Use the actual seeded store;
do not substitute example values from the original PDF. Keep `Use local evidence
only` available if Gemini is slow or unavailable, and label that mode honestly.

| Time | Action | What to show |
| --- | --- | --- |
| 00:00–00:35 | Open http://localhost:8501; select S-012 | Problem: exact student facts and policy text require different retrieval; show synthetic banner |
| 00:35–01:25 | Ask “What is my GPA and fee status?” | STRUCTURED, GPA 8.4, 2026-FALL Paid, zero outstanding; SQL evidence and citations |
| 01:25–02:10 | Ask “What is the minimum attendance?” | UNSTRUCTURED, 75 percent per course; Academic_Regulations.pdf page 4 and chunk |
| 02:10–03:25 | Ask “Am I eligible for a merit scholarship and what is the deadline?” | HYBRID: GPA/year/fee criteria satisfied; 15 vs 20 December conflict, source publication dates, no unsupported authority claim |
| 03:25–04:05 | Switch to S-002, ask merit eligibility | GPA 8.7/year 2 meet academic criteria, but 30000 overdue balance prevents eligibility; history resets on student change |
| 04:05–04:35 | Toggle local-evidence mode; ask GPA | Original records and sources remain available without generated interpretation |
| 04:35–05:00 | Show measured results and limits | Use `docs/EVALUATION_RESULTS.md`; distinguish synthetic benchmark, fallback mode, and pending/completed human review |

Optional boundary variant: S-001, “Do I meet the merit scholarship GPA, year, and
current-term fee criteria?” GPA exactly 8.0, year 2, and Paid satisfy stated criteria.
Deadline uncertainty is separate from academic/fee eligibility.

Optional upload failure: choose `artifacts/browser-uploads/Corrupt_Example.pdf` if
the browser tests generated it, click Index document, and show readable rejection.
Do not claim a generated answer when the UI says it is showing original evidence.

Useful phrasing: “Every answer is based on these retrieved rows/chunks. The model
cannot author SQL. Missing evidence and unavailable APIs produce visible fallbacks.”

If a remote call stalls, show the earlier verified screenshots/JSON evidence as a
recorded example with its date/model. No backup video has been fabricated or claimed.
