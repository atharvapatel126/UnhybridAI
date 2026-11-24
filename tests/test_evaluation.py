import csv
import json
from pathlib import Path
import pytest
from src.evaluation.metrics import aggregate, percentile
from src.evaluation.runner import evaluate, row_for, validate_cases


def case(identifier="Q1", source="policy.txt"):
    return {"id":identifier, "query":"my GPA", "student_id":"S-012", "expected_route":"STRUCTURED",
            "expected_tools":["get_student_profile"], "expected_source_file":source, "key_facts":["8.4"], "split":"tuning"}


def result():
    return {"route":"STRUCTURED", "sql_tools":["get_student_profile"], "method":"fallback",
            "generation_method":"evidence", "answer":"raw evidence", "errors":[], "sources":[],
            "evidence":{"sql":[{"rows":[{"gpa":8.4}]}], "docs":[]}, "timings":{"sql_ms":2.}, "request_id":"test"}


def test_percentiles_and_undefined_metrics():
    assert percentile([1, 2, 3, 4], .5) == 2.5
    assert percentile([1, 2, 3, 4], .95) == pytest.approx(3.85)
    assert percentile([7], .95) == 7
    assert percentile([], .5) is None
    with pytest.raises(ValueError):
        percentile([float("nan")], .5)
    metrics = aggregate([], [])
    assert metrics["routing_accuracy"] is None and metrics["answer_faithfulness"] is None


def test_metric_denominators_hits_and_modes():
    first = row_for(case(), result(), 10., "offline")
    second_case = dict(case("Q2", None), expected_route="OUT_OF_SCOPE", expected_tools=[], split="heldout")
    second = row_for(second_case, result(), 20., "offline")
    third_result = result()
    third_result.update(generation_method="generated", answer="GPA 8.4 [SQL-1]", sources=[{"tag":"[SQL-1]"}])
    third_result["evidence"]["docs"] = [{"source_file":"policy.txt"}]
    third = row_for(case("Q3"), third_result, 30., "live")
    summary = aggregate([first, second, third], [{"expected_valid":True, "ok":True}, {"expected_valid":False, "ok":False}])
    assert summary["routing_accuracy"] == pytest.approx(2/3)
    assert summary["retrieval_eligible_queries"] == 2 and summary["retrieval_hit_at_3"] == .5
    assert summary["ingestion_success_rate"] == .5 and summary["valid_file_ingestion_success_rate"] == 1
    assert summary["invalid_file_rejection_rate"] == 1
    assert summary["generation_success_rate"] == 1 and summary["structural_citation_validity"] == 1
    assert summary["source_attribution_correctness"] is None
    assert summary["latency_ms"]["p50"] == 20 and summary["stages_ms"]["sql_ms"]["samples"] == 3
    assert summary["splits"]["heldout"]["routing_accuracy"] == 0


def test_dataset_has_40_labels_and_separate_splits():
    cases = json.loads(Path(__file__).with_name("eval_set.json").read_text())
    validate_cases(cases)
    assert len(cases) == 40
    assert sum(row["split"] == "tuning" for row in cases) == 20
    assert sum(row["split"] == "heldout" for row in cases) == 20
    with pytest.raises(ValueError):
        validate_cases([case(), case()])


def test_runner_writes_only_measured_data_and_refuses_overwrite(tmp_path):
    dataset = tmp_path / "dataset.json"
    dataset.write_text(json.dumps([case(source=None)]))
    output = tmp_path / "run"
    summary = evaluate(dataset, output, answer_fn=lambda *a, **k: result(), ingestion_fn=lambda _: [])
    assert summary["questions"] == 1 and summary["correct_routes"] == 1
    assert summary["source_attribution_correctness"] is None
    rows = list(csv.DictReader((output / "results.csv").open(encoding="utf-8")))
    assert len(rows) == 1 and rows[0]["expected_source_file"] == "N/A"
    assert json.loads((output / "metadata.json").read_text())["dataset_sha256"]
    assert not (output / "HUMAN_REVIEW.md").exists()  # Offline is not a live answer-quality cohort.
    with pytest.raises(ValueError, match="earlier run"):
        evaluate(dataset, output, answer_fn=lambda *a, **k: result(), ingestion_fn=lambda _: [])


def test_runner_retains_unhandled_failure(tmp_path):
    dataset = tmp_path / "dataset.json"
    dataset.write_text(json.dumps([case(source=None)]))
    def fail(*args, **kwargs):
        raise RuntimeError("not exposed")
    summary = evaluate(dataset, tmp_path / "failed", answer_fn=fail, ingestion_fn=lambda _: [])
    assert summary["routing_accuracy"] == 0 and summary["queries_with_warnings"] == 1


@pytest.mark.parametrize("cases", [None, [{}], [{"id":"Q1"}], [dict(case(), expected_tools=None)]])
def test_malformed_dataset_has_readable_validation(cases):
    with pytest.raises(ValueError):
        validate_cases(cases)
