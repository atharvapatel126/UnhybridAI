"""Sequential measured evaluation; each original response/failure is retained."""
import json
from pathlib import Path
import time
from config import settings
from src.db.queries import TOOLS
from src.evaluation.ingestion_probe import measure_ingestion
from src.evaluation.metrics import aggregate, citation_validity
from src.evaluation.reporting import run_metadata, write_csv, write_summary
from src.evaluation.review import prepare_review
from src.orchestrator import answer_query
from src.ingest.embed_store import get_model


def validate_cases(cases):
    if not isinstance(cases, list) or not cases:
        raise ValueError("Evaluation cases must be a nonempty list.")
    seen = set()
    for case in cases:
        required = {"id", "query", "expected_route", "expected_tools", "expected_source_file", "key_facts", "split"}
        if not isinstance(case, dict) or not required <= set(case):
            raise ValueError("Evaluation case is missing required fields.")
        if not isinstance(case["id"], str) or not case["id"] or case["id"] in seen:
            raise ValueError("Evaluation cases must have unique string IDs.")
        seen.add(case["id"])
        if not isinstance(case["expected_tools"], list) or not all(isinstance(tool, str) for tool in case["expected_tools"]):
            raise ValueError("Expected tools must be a list of names.")
        if (case["expected_route"] not in ("STRUCTURED", "UNSTRUCTURED", "HYBRID", "OUT_OF_SCOPE")
            or not set(case["expected_tools"]) <= set(TOOLS) or case["split"] not in ("tuning", "heldout")
            or not isinstance(case["query"], str) or not 0 < len(case["query"]) <= 2000
            or not isinstance(case["key_facts"], list)):
            raise ValueError(f"Invalid labeled evaluation case: {case['id']}")


def row_for(case, result, wall_ms, mode):
    docs = result["evidence"]["docs"]
    top_three = [item["source_file"] for item in docs[:3]]
    return {"id":case["id"], "split":case["split"], "query":case["query"], "student_id":case.get("student_id"),
            "expected_route":case["expected_route"], "actual_route":result["route"],
            "route_correct":result["route"] == case["expected_route"], "expected_tools":case["expected_tools"],
            "actual_tools":result.get("sql_tools", []), "tools_correct":set(result.get("sql_tools", [])) == set(case["expected_tools"]),
            "classification_method":result.get("method", "error"), "expected_source_file":case["expected_source_file"],
            "retrieved_sources_top3":top_three,
            "retrieval_hit_at_3":case["expected_source_file"] in top_three if case["expected_source_file"] else None,
            "citation_valid":citation_validity(result), "generation_method":result.get("generation_method"),
            "generation_applicable":mode == "live" and result["route"] != "OUT_OF_SCOPE" and any(result["evidence"].values()),
            "errors":result["errors"], "wall_ms":wall_ms, "timings":result["timings"], "request_id":result["request_id"]}


def evaluate(dataset, output, mode="offline", pause=0, image_id=None, *, answer_fn=answer_query, ingestion_fn=measure_ingestion):
    dataset, output = Path(dataset), Path(output)
    if mode not in ("offline", "live") or not 0 <= pause <= 10:
        raise ValueError("Use mode offline/live and pause between 0 and 10 seconds.")
    if mode == "live":
        settings.require_api_key()
    cases = json.loads(dataset.read_text(encoding="utf-8"))
    validate_cases(cases)
    if (output / "results.jsonl").exists():
        raise ValueError("Output contains an earlier run. Choose a new output directory.")
    output.mkdir(parents=True, exist_ok=True)
    metadata = run_metadata(dataset, mode, image_id)
    metadata["pause_seconds_between_queries"] = pause
    ingestion_start = time.perf_counter()
    ingestion = ingestion_fn(output)
    metadata["ingestion_probe_ms"] = (time.perf_counter() - ingestion_start) * 1000
    metadata["embedding_cache_initialized_before_queries"] = bool(get_model.cache_info().currsize)
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    write_csv(output / "ingestion.csv", ingestion)
    rows, snapshots = [], []
    with (output / "results.jsonl").open("w", encoding="utf-8") as stream:
        for case in cases:
            start = time.perf_counter()
            try:
                result = answer_fn(case["query"], case.get("student_id"), use_llm=mode == "live")
            except Exception as exc:
                result = {"route":"ERROR", "evidence":{"sql":[],"docs":[]}, "answer":"Evaluation call failed.",
                          "sources":[], "errors":[f"Unhandled {type(exc).__name__}"], "timings":{}, "request_id":""}
            elapsed = (time.perf_counter() - start) * 1000
            row = row_for(case, result, elapsed, mode)
            rows.append(row)
            snapshot = {"case":case, "result":result, "wall_ms":elapsed, "mode":mode}
            snapshots.append(snapshot)
            stream.write(json.dumps(snapshot, ensure_ascii=True) + "\n")
            stream.flush()
            print(f"{case['id']} route={result['route']} expected={case['expected_route']} generation={result.get('generation_method', 'n/a')} wall_ms={elapsed:.1f}", flush=True)
            if pause:
                time.sleep(pause)
    summary = aggregate(rows, ingestion)
    write_csv(output / "results.csv", rows)
    write_summary(output, summary)
    if mode == "live":
        prepare_review(output, snapshots, metadata["dataset_sha256"])
    return summary
