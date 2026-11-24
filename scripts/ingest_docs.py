"""Non-destructive fixture bootstrap; explicit refresh can replace bundled names."""
import argparse
import sys
from config import settings
from src.ingest.embed_store import ingest_file, list_documents
from src.db.seed import seed_database


def main(argv=()):
    parser = argparse.ArgumentParser(description="Bootstrap synthetic document fixtures once")
    parser.add_argument("--refresh-fixtures", action="store_true", help="Explicitly replace indexed copies of bundled fixtures")
    args = parser.parse_args(argv)
    seed = seed_database()
    if not seed["ok"]:
        print(seed["error"])
        return 1
    try:
        marker = settings.chroma_dir / ".fixtures_initialized"
        if marker.exists() and not args.refresh_fixtures:
            print("Demo already initialized; preserving indexed replacements and deletions.")
            return 0
        files = sorted(path for path in settings.raw_docs_dir.glob("*") if path.suffix.lower() in (".pdf", ".txt", ".md"))
        if not files:
            print("No source fixture documents found. Check RAW_DOCS_DIR.")
            return 1
        existing = set() if args.refresh_fixtures else {doc["source_file"] for doc in list_documents()}
        failed = False
        for path in files:
            if path.name in existing:
                print(f"Preserving existing indexed document: {path.name}")
                continue
            result = ingest_file(path)
            print(path.name, result)
            failed |= not result["ok"]
        if not failed:
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text("SYNTHETIC demo fixtures initialized.\n", encoding="utf-8")
        return int(failed)
    except Exception:
        print("Document bootstrap unavailable. Check source fixtures and vector-store permissions.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
