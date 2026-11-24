"""One Gemini boundary: explicit SDK timeout, one SDK attempt, bounded app retries."""
import json
import time

from google import genai
from google.genai import types

from config import settings
from src.utils.logger import event, redact


class LLMUnavailable(RuntimeError):
    """Credential, quota, network, or upstream availability problem."""


class LLMBadResponse(RuntimeError):
    """Blocked, empty, or malformed model output."""


def _message(code):
    if code in (401, 403):
        return "Gemini credentials or access rejected. Check the local API key and model permissions."
    if code == 400:
        return "Gemini rejected the request. Check credentials, model, and SDK configuration."
    if code == 404:
        return "Configured Gemini model is unavailable. Set MODEL_NAME to a model enabled for your account."
    if code == 429:
        return "Gemini quota or rate limit reached. Check quota and retry later."
    if isinstance(code, int) and 500 <= code <= 599:
        return f"Gemini service temporarily unavailable (HTTP {code}). Retry later or configure an available Flash model."
    return "Gemini unavailable or request timed out. Check network access and try again."


def _checked_text(response, json_mode):
    feedback = getattr(response, "prompt_feedback", None)
    block_reason = str(getattr(feedback, "block_reason", "") or "")
    blocked = bool(block_reason and "UNSPECIFIED" not in block_reason)
    for candidate in getattr(response, "candidates", None) or []:
        reason = str(getattr(candidate, "finish_reason", "") or "")
        blocked |= any(code in reason for code in ("SAFETY", "RECITATION", "BLOCKLIST", "PROHIBITED_CONTENT"))
    if blocked:
        raise LLMBadResponse("Gemini blocked this response. Retrieved evidence can still be displayed.")
    text = response.text
    if not isinstance(text, str) or not text.strip():
        raise LLMBadResponse("Gemini returned an empty response.")
    if json_mode:
        try:
            json.loads(text)
        except (ValueError, TypeError):
            raise LLMBadResponse("Gemini returned invalid JSON.") from None
    return text.strip()


def generate(prompt, system=None, json_mode=False, temperature=.1, *, response_schema=None):
    try:
        key = settings.require_api_key()
    except ValueError as exc:
        raise LLMUnavailable(str(exc)) from None
    started = time.perf_counter()
    options = types.HttpOptions(api_version="v1", timeout=int(settings.timeout_seconds * 1000),
                                retry_options=types.HttpRetryOptions(attempts=1))
    config = types.GenerateContentConfig(system_instruction=system, temperature=temperature,
                                         response_mime_type="application/json" if json_mode else "text/plain",
                                         response_json_schema=response_schema,
                                         max_output_tokens=2048,
                                         thinking_config=types.ThinkingConfig(thinking_level="low")
                                         if "gemini-3." in settings.model_name else None)
    raw_text = None
    usage = None
    attempts = 0
    attempt_errors = []
    error = None
    try:
        with genai.Client(api_key=key, http_options=options) as client:
            for attempt in range(settings.max_retries + 1):
                attempts += 1
                try:
                    response = client.models.generate_content(model=settings.model_name, contents=prompt, config=config)
                    raw_text = getattr(response, "text", None)
                    metadata = getattr(response, "usage_metadata", None)
                    usage = metadata.model_dump(exclude_none=True) if metadata else None
                    return _checked_text(response, json_mode)
                except LLMBadResponse:
                    raise
                except Exception as exc:
                    code = getattr(exc, "code", None)
                    attempt_errors.append({"attempt": attempts, "code": code if isinstance(code, int) else None,
                                           "category": type(exc).__name__})
                    retryable = code == 429 or isinstance(code, int) and 500 <= code <= 599
                    if retryable and attempt < settings.max_retries:
                        time.sleep(min(settings.backoff_seconds * 2 ** attempt, 5))
                        continue
                    raise LLMUnavailable(_message(code)) from None
    except (LLMUnavailable, LLMBadResponse) as exc:
        error = str(exc)
        raise
    except Exception:
        error = "Gemini client configuration failed. Check SDK and runtime settings."
        raise LLMUnavailable(error) from None
    finally:
        fields = {"model": settings.model_name, "prompt": prompt, "system": system,
                  "response": raw_text, "usage": usage, "attempts": attempts,
                  "attempt_errors": attempt_errors, "json_mode": json_mode,
                  "response_schema": response_schema, "temperature": temperature,
                  "timeout_ms": options.timeout, "retry_limit": settings.max_retries,
                  "latency_ms": round((time.perf_counter() - started) * 1000, 3), "error": error}
        event("llm_call", **redact(fields, [key]))
