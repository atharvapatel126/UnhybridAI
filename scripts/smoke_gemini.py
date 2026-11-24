"""One live request. Never print SDK errors or credentials."""
import json
import time
from datetime import datetime, timezone

from config import settings
from src.llm.gemini_client import generate, LLMUnavailable, LLMBadResponse


def main():
    start = time.perf_counter()
    result = {"timestamp": datetime.now(timezone.utc).isoformat(), "model": settings.model_name,
              "mode": "live", "ok": False}
    try:
        answer = json.loads(generate('Return exactly this JSON object: {"status":"ok"}', json_mode=True))
        result["ok"] = answer == {"status": "ok"}
        result["response"] = answer
    except (LLMUnavailable, LLMBadResponse) as exc:
        result["error"] = str(exc)
    result["latency_ms"] = round((time.perf_counter() - start) * 1000, 3)
    print(json.dumps(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
