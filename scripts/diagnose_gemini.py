"""Read-only connection diagnosis; emit types/statuses, never raw errors or keys."""
import json
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from google import genai
from google.genai import types
from config import settings


def main():
    key = settings.require_api_key()
    start = time.perf_counter()
    with genai.Client(api_key=key, http_options=types.HttpOptions(
            api_version="v1", timeout=5000, retry_options=types.HttpRetryOptions(attempts=1))) as client:
        try:
            page = client.models.list(config={"page_size": 5})
            print("SDK model endpoint OK:", [model.name for model in page.page])
        except Exception as exc:
            print("SDK failure:", type(exc).__name__, "status:", getattr(exc, "code", None),
                  "cause:", type(exc.__cause__).__name__)
        try:
            model = client.models.get(model=settings.model_name)
            print("Configured model available:", model.name)
        except Exception as exc:
            print("Configured model lookup:", type(exc).__name__, "status:", getattr(exc, "code", None))
    print("SDK elapsed seconds:", round(time.perf_counter() - start, 2))
    try:
        request = Request("https://generativelanguage.googleapis.com/v1/models?pageSize=5",
                          headers={"x-goog-api-key": key})
        with urlopen(request, timeout=8) as response:
            models = json.load(response).get("models", [])
            print("Standard-library model endpoint OK:", [model["name"] for model in models])
    except HTTPError as exc:
        print("Standard-library endpoint HTTP status:", exc.code)
    except Exception as exc:
        print("Standard-library endpoint failure:", type(exc).__name__)


if __name__ == "__main__":
    main()
