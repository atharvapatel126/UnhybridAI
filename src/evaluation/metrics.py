"""Metrics calculated only from measured records; undefined values remain None."""
import math
import re


def percentile(values, quantile):
    if not 0 <= quantile <= 1 or any(not math.isfinite(value) for value in values):
        raise ValueError("Invalid percentile data")
    if not values:
        return None
    data = sorted(values)
    position = (len(data) - 1) * quantile
    low, high = math.floor(position), math.ceil(position)
    return data[low] + (data[high] - data[low]) * (position - low)


def fraction(numerator, denominator):
    return numerator / denominator if denominator else None


def citation_validity(result):
    if result.get("generation_method") != "generated":
        return None
    tags = set(re.findall(r"\[[^\]\n]+\]", result["answer"]))
    allowed = {source["tag"] for source in result["sources"]}
    return bool(tags) and tags <= allowed


def aggregate(rows, ingestion):
    eligible = [row for row in rows if row["expected_source_file"]]
    generated = [row for row in rows if row["citation_valid"] is not None]
    applicable = [row for row in rows if row["generation_applicable"]]
    valid_files = [record for record in ingestion if record["expected_valid"]]
    invalid_files = [record for record in ingestion if not record["expected_valid"]]
    correct_routes = sum(row["route_correct"] for row in rows)
    hits = sum(row["retrieval_hit_at_3"] for row in eligible)
    summary = {
        "questions": len(rows), "correct_routes": correct_routes,
        "routing_accuracy": fraction(correct_routes, len(rows)),
        "tool_set_accuracy": fraction(sum(row["tools_correct"] for row in rows), len(rows)),
        "retrieval_eligible_queries": len(eligible), "retrieval_hits_at_3": hits,
        "retrieval_hit_at_3": fraction(hits, len(eligible)),
        "structural_citation_validity": fraction(sum(row["citation_valid"] for row in generated), len(generated)),
        "generated_answers": len(generated),
        "generation_success_rate": fraction(sum(row["generation_method"] == "generated" for row in applicable), len(applicable)),
        "fallback_routing_queries": sum(row["classification_method"] == "fallback" for row in rows),
        "queries_with_warnings": sum(bool(row["errors"]) for row in rows),
        "ingestion_attempts": len(ingestion), "ingestion_successes": sum(row["ok"] for row in ingestion),
        "ingestion_success_rate": fraction(sum(row["ok"] for row in ingestion), len(ingestion)),
        "valid_file_ingestion_success_rate": fraction(sum(row["ok"] for row in valid_files), len(valid_files)),
        "deliberate_invalid_files": len(ingestion) - len(valid_files),
        "invalid_file_rejection_rate": fraction(sum(not row["ok"] for row in invalid_files), len(invalid_files)),
        "latency_ms": {"samples": len(rows), "p50": percentile([row["wall_ms"] for row in rows], .5),
                       "p95": percentile([row["wall_ms"] for row in rows], .95)},
        "source_attribution_correctness": None, "answer_faithfulness": None,
        "human_review_status": "pending", "stages_ms": {}, "splits": {},
    }
    for stage in sorted({key for row in rows for key in row["timings"]}):
        values = [row["timings"][stage] for row in rows if stage in row["timings"]]
        summary["stages_ms"][stage] = {"samples": len(values), "p50": percentile(values, .5), "p95": percentile(values, .95)}
    for split in sorted({row["split"] for row in rows}):
        subset = [row for row in rows if row["split"] == split]
        summary["splits"][split] = {"questions": len(subset), "routing_accuracy": fraction(sum(row["route_correct"] for row in subset), len(subset))}
    return summary
