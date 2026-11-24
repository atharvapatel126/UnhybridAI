"""Run only permitted retrieval branches; a failed branch never hides the other."""
import time
from uuid import uuid4

from src.db import queries
from src.evidence import label_evidence, sources
from src.llm.answer import generate_answer
from src.rag.retriever import retrieve
from src.router.classifier import classify
from src.utils.logger import event, request_context, current_request_id, log_warnings


def _sql(tool_names, student_id, errors):
    if not student_id:
        errors.append("Select a synthetic student for student-specific records.")
        return []
    results = []
    profile = None
    # Profile comes first if department statistics depend on it.
    ordered = sorted(tool_names, key=lambda name: name != "get_student_profile")
    for name in ordered:
        try:
            if name == "get_department_stats":
                if not profile or not profile["rows"]:
                    errors.append("Department statistics require an available student profile.")
                    continue
                argument = profile["rows"][0]["dept_id"]
            else:
                argument = student_id
            result = queries.TOOLS[name](argument)
            if name == "get_student_profile":
                profile = result
            if result["error"]:
                errors.append(f"{name}: {result['error']}")
            elif not result["found"]:
                errors.append(f"No record found for {name} and the selected student/context.")
            else:
                results.append(result)
        except Exception:
            errors.append(f"{name}: structured retrieval unavailable.")
    return results


def answer_query(query, student_id=None, *, use_llm=True):
    with request_context(str(uuid4())):
        return _answer_query(query, student_id, use_llm=use_llm)


def _answer_query(query, student_id=None, *, use_llm=True):
    started = time.perf_counter()
    route_start = time.perf_counter()
    classification = classify(query, use_llm=use_llm)
    result = {"route": classification["route"], "reason": classification["reason"],
              "method": classification["method"], "sql_tools": classification["sql_tools"],
              "evidence": {"sql": [], "docs": []}, "answer": "", "sources": [], "errors": [],
              "timings": {"classification_ms": (time.perf_counter() - route_start) * 1000},
              "request_id": current_request_id()}
    route = result["route"]
    if route == "OUT_OF_SCOPE":
        result["answer"] = "I can help with synthetic university records and university policy documents. This question is outside that scope."
    else:
        if route in ("STRUCTURED", "HYBRID"):
            stage = time.perf_counter()
            result["evidence"]["sql"] = _sql(classification["sql_tools"], student_id, result["errors"])
            result["timings"]["sql_ms"] = (time.perf_counter() - stage) * 1000
        if route in ("UNSTRUCTURED", "HYBRID"):
            stage = time.perf_counter()
            try:
                documents = retrieve(classification["doc_query"])
                result["evidence"]["docs"] = documents["matches"]
                result["errors"].extend(documents["errors"])
                if documents["state"] == "empty":
                    result["errors"].append("No documents are available. Ingest synthetic policies first.")
                elif documents["state"] == "no_match":
                    result["errors"].append("No document evidence matched the question above the similarity threshold.")
            except Exception:
                result["errors"].append("Document retrieval unavailable; structured evidence is preserved.")
            result["timings"]["retrieval_ms"] = (time.perf_counter() - stage) * 1000
        label_evidence(result["evidence"])
        result["sources"] = sources(result["evidence"])
        stage = time.perf_counter()
        generated = generate_answer(query, result["evidence"], result["errors"], use_llm=use_llm)
        result["answer"] = generated["answer"]
        result["generation_method"] = generated["mode"]
        result["errors"].extend(generated["errors"])
        result["timings"]["generation_ms"] = (time.perf_counter() - stage) * 1000
    result["timings"]["total_ms"] = (time.perf_counter() - started) * 1000
    result["errors"].extend(warning for warning in log_warnings() if warning not in result["errors"])
    warning = event("execution", **result, student_id=student_id, query=query)
    if warning and warning not in result["errors"]:
        result["errors"].append(warning)
    return result
