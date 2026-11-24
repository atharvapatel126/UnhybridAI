# Pre-demo checklist

- [x] Docker Desktop is running Linux containers; app health is HTTP 200 at port 8501.
- [x] App shows the synthetic banner, 25 students, and the intended four fixture policies.
- [ ] Local `.env` contains the configured API key/model; key is not in Git, images, or screenshots.
- [x] Model weights are cached; first-run downloads completed before the presentation.
- [ ] S-012 shows GPA 8.4/year 3/Paid; S-002 has 30000 overdue; S-001 is the 8.0 boundary.
- [ ] Attendance evidence is on Academic_Regulations.pdf page 4.
- [ ] Both 15/20 December notices remain available; do not claim a single authoritative date.
- [x] Three main scenarios and local-evidence fallback have been rehearsed against the current image.
- [ ] Browser-test uploaded fixtures have been removed from the active index.
- [x] Current evaluation CSVs/metadata are available; results slide uses only measured values.
- [x] Review provenance is explicit: user accepted all 20 answers in chat; existing draft claim rows were transcribed from that confirmation.
- [x] Release image/archive checksum and startup instructions have been verified.
- [ ] Optional backup screenshots/recording are labeled as previously recorded behavior.

Default initialization preserves changed/deleted documents. For a deliberately fresh
demo, use a separate named data volume or explicitly refresh the bundled fixtures;
do not delete the working volumes as a routine stop/reset step. Clear conversation
history before presenting and ask standalone questions; retrieval does not use
earlier chat turns as conversational context.

Checked items reflect 2026-11-24 release verification and browser rehearsal;
recheck before presenting. User acceptance of the 20 review answers is recorded
in `artifacts/evaluation/live/review_status.json`.
