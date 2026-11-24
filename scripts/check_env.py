"""Import dependencies without creating clients, downloading weights, or printing secrets."""
from importlib import import_module, metadata
import platform
import sys

PACKAGES = {
    "streamlit": "streamlit", "python-dotenv": "dotenv", "google-genai": "google.genai",
    "sentence-transformers": "sentence_transformers", "chromadb": "chromadb",
    "pymupdf": "pymupdf", "torch": "torch",
}


def main():
    print(f"Python {platform.python_version()} ({platform.system()} {platform.machine()})")
    failed = False
    for package, module in PACKAGES.items():
        try:
            import_module(module)
            print(f"OK {package}=={metadata.version(package)}")
        except Exception as exc:
            print(f"FAIL {package}: {type(exc).__name__}; check installation and platform compatibility")
            failed = True
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
