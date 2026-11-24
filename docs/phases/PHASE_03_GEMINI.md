# Phase 03 — Reliable Gemini client

Source prompt: P11. Dependency: Phase 02 passed. Status: Passed. Results: [phase report](../reports/PHASE_03_REPORT.md).
Apply all shared implementation, testing, Docker, and reporting rules.

## Implementation instructions

1. Consult current official Gemini `google-genai` documentation before coding;
   record the SDK version, valid configured model, timeout units, JSON mode, and
   retry behavior actually verified. Avoid obsolete SDK examples.
2. Implement one `src/llm/gemini_client.py` wrapper with
   `generate(prompt, system=None, json_mode=False, temperature=0.1)` and typed
   `LLMUnavailable`/`LLMBadResponse` exceptions.
3. Validate credentials lazily. Bound each attempt to 15 seconds and permit at most
   two application retries with bounded backoff for retryable 429/5xx errors.
   Configure or account for SDK retries so they do not multiply attempts silently.
4. Distinguish missing/invalid key, quota, network, timeout, blocked/empty response,
   and malformed output. Do not retry permanent validation/authentication errors.
5. State the maximum client budget including backoff, and the later two-call
   classification/generation budget. Keep the approximate 10-second target separate
   from these failure bounds. Expose measured latency and retry count.
6. Record redacted latency, model, and token usage when returned. The minimal log
   adapter supports later full logging without duplicating wrapper code.
7. Add `scripts/smoke_gemini.py` or an equivalent live test entry point. Read runtime
   secrets from the local environment; do not print them or bake them into images.

## Testing after this phase

- Mock success, JSON mode, absent key, invalid key, 429, 5xx, timeout, network loss,
  blocked/empty response, and malformed response. Assert types and clear messages.
- Use a fake clock/sleeper to verify retry counts and backoff without slow tests.
- Verify permanent errors do not retry and default SDK retries are accounted for.
- Check prompt/exception logs using a dummy key sentinel; key must not appear.
- Run focused wrapper tests and cumulative tests. Build Phase 03 images and run
  deterministic tests in the test image without credentials.
- Run one live smoke call in the container with a locally supplied key, recording
  sanitized result, model, timestamp, and elapsed time. Do not label a mock live.

## Exit gate and report

Mocked failure tests and the live smoke must pass before this phase is Passed.
If credentials/quota/network are unavailable, report Blocked after completing
independent work; do not silently omit the live gate. Save
`docs/reports/PHASE_03_REPORT.md` with image IDs, measured timings, difficulties,
and the exact unblock action.

Potential user requirement: set `GEMINI_API_KEY` locally and enable valid model
access/quota. Never request the secret value in chat.
