"""Real runtime checks, restricted to explicitly designated scratch storage."""
import argparse
import hashlib
import json
import os

from config import settings
from src.db.queries import get_fee_status, get_student_profile, list_students
from src.ingest.embed_store import list_documents
from src.ingest.uploads import ingest_upload
from src.orchestrator import answer_query


def snapshot():
    return {"database_sha256": hashlib.sha256(settings.db_path.read_bytes()).hexdigest(),
            "manifest_sha256": hashlib.sha256((settings.chroma_dir / "documents.json").read_bytes()).hexdigest(),
            "documents": sorted(doc["source_file"] for doc in list_documents())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["initial", "restart"])
    args = parser.parse_args()
    # Never upload a probe into a developer's active demo volume by accident.
    if settings.data_dir.name != "release-check-state":
        raise RuntimeError("Use dedicated /app/state/release-check-state scratch storage.")
    if settings.api_key:
        raise RuntimeError("This probe requires an explicitly empty GEMINI_API_KEY.")
    record = settings.data_dir / "release-check.json"
    if args.stage == "restart":
        expected = json.loads(record.read_text(encoding="utf-8"))
        assert snapshot() == expected, "Database or indexed upload changed across restart"
        print(json.dumps({"restart_persistence": "passed", **expected}))
        return 0
    if record.exists():
        raise RuntimeError("Choose a new scratch volume for the initial check.")
    assert os.getuid() != 0, "Runtime must use a non-root user"
    assert len(list_students()["rows"]) == 25
    assert len(list_documents()) == 4
    assert get_student_profile("S-012")["rows"][0]["gpa"] == 8.4
    assert get_fee_status("S-012")["rows"][0]["status"] == "Paid"
    assert get_fee_status("S-002")["rows"][0]["outstanding"] == 30000
    cases = [
        ("What is my GPA and fee status?", "S-012", "STRUCTURED", "8.4"),
        ("What is the minimum attendance?", None, "UNSTRUCTURED", "75"),
        ("Am I eligible for a merit scholarship and what is the deadline?", "S-012", "HYBRID", "Scholarship_Policy.pdf"),
        ("Am I eligible for a merit scholarship?", "S-002", "HYBRID", "30000"),
        ("Who won the cricket world cup?", None, "OUT_OF_SCOPE", "outside that scope"),
    ]
    for query, student, route, fact in cases:
        result = answer_query(query, student)
        assert result["route"] == route, result["route"]
        assert fact in result["answer"], f"Missing expected evidence: {fact}"
        if route != "OUT_OF_SCOPE":
            assert result["generation_method"] == "evidence"
            assert result["sources"]
        print(json.dumps({"route": route, "missing_key_fallback": "passed"}))
    uploaded = ingest_upload("Release_Check.txt", b"SYNTHETIC RELEASE CHECK. The verification library lends four books for seven days.")
    assert uploaded["ok"], uploaded["errors"]
    assert not ingest_upload("Corrupt_Release.pdf", b"not a PDF")["ok"]
    state = snapshot()
    assert "Release_Check.txt" in state["documents"]
    record.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps({"upload_and_invalid_rejection": "passed", **state}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
