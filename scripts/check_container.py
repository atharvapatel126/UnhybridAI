"""Runtime-only smoke: non-root identity, no embedded secret file, writable state."""
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import ROOT, settings


def main():
    if not hasattr(os, "getuid") or os.getuid() == 0:
        print("FAIL: run this check as the non-root Linux container user.")
        return 1
    if (ROOT / ".env").exists():
        print("FAIL: .env must not be embedded in the image.")
        return 1
    for directory in (settings.data_dir, settings.logs_dir, settings.model_cache):
        directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=directory) as probe:
            probe.write(b"container-write-probe")
        print(f"OK writable {directory.name}")
    print(f"OK non-root uid={os.getuid()}; no embedded .env")
    return 0


if __name__ == "__main__":
    sys.exit(main())
