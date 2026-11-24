# Phase 03 report — Gemini client

Status: Passed
Date: 2026-11-23 (Asia/Calcutta)
Source prompt: P11

## Implemented

- One `google-genai` 3.6.1 wrapper with explicit v1 API, JSON mode, system rules,
  configurable model, low temperature, typed unavailable/bad-response failures.
- SDK timeout configured in milliseconds (15000 by default), SDK attempts forced
  to 1, and at most two application retries on 429/5xx with bounded backoff.
- Credential checks are lazy; clients close after success/failure. Missing keys,
  authentication/model errors, quota, timeout/network, blocked/empty/invalid JSON
  responses return sanitized actionable errors.
- Redacted event metadata includes model, prompts/response, attempts, usage and
  elapsed time. Logging adapter now preserves non-secret token counts.
- Live smoke and read-only connection diagnostic scripts; neither prints keys.
- Configured default changed to `gemini-3.6-flash` after live verification; model
  remains overridable. No key was embedded in images or committed files.

## Testing performed after implementation

| Check | Command | Result | Evidence |
| --- | --- | --- | --- |
| Host cumulative suite | `.venv/Scripts/python.exe -m pytest -q` | 65 passed, exit 0 | `artifacts/phase03-host-tests-final.log` |
| Docker cumulative suite, real cached embeddings | `docker compose run --rm -e HF_HUB_OFFLINE=1 test` | 65 passed, exit 0 | `artifacts/phase03-container-tests-final.log` |
| Final image builds | `docker build --target runtime/test ...:phase-03 .` | Both passed, exit 0 | `artifacts/phase03-*-build-final.log` |
| Final live smoke, runtime image | `docker compose run --rm app python -m scripts.smoke_gemini` | Exact expected JSON returned, exit 0; 27597.610 ms | `artifacts/phase03-live-smoke-final.log` |
| Earlier compatible-model live smoke | Runtime MODEL_NAME override | Passed; 17330.549 ms | `artifacts/phase03-compatible-model-smoke.log` |
| Connection/model diagnosis | SDK + standard-library model list, configured-model lookup | Credentials/metadata endpoints reachable on host and Docker | `artifacts/phase03-*-diagnostic.log` |

Mocked cases include retries/exhaustion/recovery, 400/401/403/404, quota/5xx,
network/timeout, empty/invalid JSON, both prompt and candidate safety blocks,
client closure, nested prompt/response redaction, and preservation of usage counts.
Fake sleepers verify backoff without real waiting.

## Docker images

- Runtime `unihybrid-ai:phase-03`:
  `sha256:20b26f4fea117ad281e94aac8c542ab07f052c5072875dc058048023e95cc108`.
- Test `unihybrid-ai-test:phase-03`:
  `sha256:6e56a4ff44aa5a84171746aa96e51e1ccae5511cf046a3288ab4e056c8c8f41c`.
- Linux amd64, non-root; base unchanged from Phase 00.

## Difficulties faced

- Initial 3.8 Flash smoke calls failed with availability/transport outcomes. A
  sanitized direct diagnostic returned provider HTTP 503/high demand. Model metadata
  lookup succeeded, demonstrating that a listed model is not proof generation works.
- A 2.5 Flash generation probe returned 404 despite its listing. No default change
  was made to that model. A 3.6 Flash smoke succeeded, then the final default/image
  smoke succeeded again. Errors are retained in sanitized artifacts.
- A deliberately short diagnostic generation timeout returned HTTP 400: provider
  requires at least 10 seconds. Configuration now validates 10–15 seconds, with
  a regression test rejecting 5 seconds.

## Latency limits

SDK timeout is 15 seconds per request attempt; up to three attempts and default
1+2 second backoff yield a nominal 48-second network/retry budget per wrapper call.
At maximum configured backoff this is nominally 55 seconds. Connection/client setup
and cleanup add overhead, so these are not a hard end-to-end wall-clock guarantee.
Classification plus generation can double that nominal budget. Measured successful
smokes exceeded the approximate 10-second warm goal; no speed claim is made.
Full stage/latency distributions belong to Phase 08 evaluation.

## Manual requirements from the user

None currently. The locally configured key works; do not paste or commit it.
Provider load/quota can still cause later fallback behavior.

## Phase gate

Passed: required mocked and live checks succeeded. Phase 04 eligible.

References: [official SDK](https://googleapis.github.io/python-genai/),
[verified model documentation](https://aistudio.google.com/docs/models/gemini-3.6-flash).
Timeout units and retry-attempt semantics were also checked in the installed SDK.
