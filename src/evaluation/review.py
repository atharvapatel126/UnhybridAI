"""Prepare draft claim rows; score only explicitly completed human judgments."""
import csv
from datetime import datetime
import hashlib
import json
import re
from src.evaluation.metrics import fraction
from src.evaluation.reporting import write_csv


def draft_claims(result):
    if result.get("generation_method") != "generated":
        return [("evidence_only", "Evidence-only response: verify the displayed source reproduction; mark both judgments n/a.", "")]
    text = re.sub(r"\*\*(Answer|Reasoning|Missing information)\*\*", "\n", result["answer"])
    sentences = re.split(r"\n\s*\n|(?<=[.!?])\s+(?=[A-Z])", text.strip())
    claims = []
    for sentence in dict.fromkeys(s.strip() for s in sentences if s.strip()):
        tags = " ".join(dict.fromkeys(re.findall(r"\[(?:SQL|DOC)-\d+\]", sentence)))
        kind = "nonfactual" if sentence.lower().startswith("none identified") else "factual"
        claims.append((kind, sentence, tags))
    return claims


def prepare_review(directory, snapshots, dataset_hash):
    selected = [record for record in snapshots if record["case"]["expected_route"] != "OUT_OF_SCOPE"][:20]
    markdown = ["# Human faithfulness review — pending", "",
        "These are actual responses and supplied evidence. No human score has been assigned.", "",
        "Read each answer and its evidence. In `claims.csv`, split compound factual claims/add missing claims, confirm each kind, then set `supported` and `citation_correct` to yes/no. Use n/a only for nonfactual or evidence-only rows; factual rows without citations have citation_correct=n/a. Fill reviewer/date in `review_status.json`, then run the scoring command in the project README. Draft sentence rows are not a human judgment.", ""]
    rows = []
    for snapshot in selected:
        case, result = snapshot["case"], snapshot["result"]
        markdown += [f"## {case['id']} — {case['query']}", "", f"Mode: {result.get('generation_method', 'scope refusal')}; student: {case.get('student_id')}", "",
                     "Expected facts for inspection: " + "; ".join(case["key_facts"]), "", result["answer"], "", "### Supplied evidence", "",
                     "```json", json.dumps(result["evidence"], indent=2, ensure_ascii=True), "```", ""]
        for index, (kind, claim, tags) in enumerate(draft_claims(result), 1):
            rows.append({"answer_id":case["id"], "claim_index":index, "kind":kind, "claim_text":claim,
                         "cited_tags":tags, "supported":"", "citation_correct":"", "notes":""})
    write_csv(directory / "claims.csv", rows)
    status = {"reviewer":"", "reviewed_at":"", "dataset_sha256":dataset_hash,
              "results_sha256":hashlib.sha256((directory / "results.jsonl").read_bytes()).hexdigest(),
              "selected_answer_ids":[item["case"]["id"] for item in selected], "required_answers":20}
    (directory / "review_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    (directory / "HUMAN_REVIEW.md").write_text("\n".join(markdown), encoding="utf-8")


def score_claims(rows, expected_ids, reviewer, reviewed_at):
    pending = {"human_review_status":"pending", "answer_faithfulness":None, "source_attribution_correctness":None}
    if not reviewer.strip() or not reviewed_at:
        return {**pending, "reason":"Reviewer and review timestamp are required."}
    try:
        if datetime.fromisoformat(reviewed_at).tzinfo is None:
            raise ValueError
    except ValueError:
        return {**pending, "reason":"Use an ISO timestamp with a timezone offset."}
    if {row["answer_id"] for row in rows} != set(expected_ids):
        return {**pending, "reason":"Review rows must cover every selected answer and no other IDs."}
    for row in rows:
        kind = row["kind"]
        support, attribution = row["supported"].strip().lower(), row["citation_correct"].strip().lower()
        has_citation = bool(re.search(r"\[(?:SQL|DOC)-\d+\]", row["cited_tags"]))
        if kind not in ("factual", "nonfactual", "evidence_only"):
            return {**pending, "reason":"Confirm each claim kind."}
        if kind == "factual" and (support not in ("yes", "no") or attribution not in (("yes", "no") if has_citation else ("n/a",))):
            return {**pending, "reason":"Every factual claim needs an evidence judgment and the appropriate citation judgment."}
        if kind != "factual" and (support != "n/a" or attribution != "n/a"):
            return {**pending, "reason":"Nonfactual/evidence-only rows require explicit n/a judgments."}
    factual = [row for row in rows if row["kind"] == "factual"]
    cited = [row for row in factual if re.search(r"\[(?:SQL|DOC)-\d+\]", row["cited_tags"])]
    return {"human_review_status":"complete", "reviewer":reviewer, "reviewed_at":reviewed_at,
            "reviewed_answers":len(expected_ids), "reviewed_factual_claims":len(factual),
            "supported_claims":sum(row["supported"].strip().lower() == "yes" for row in factual),
            "answer_faithfulness":fraction(sum(row["supported"].strip().lower() == "yes" for row in factual), len(factual)),
            "source_attribution_correctness":fraction(sum(row["citation_correct"].strip().lower() == "yes" for row in cited), len(cited)),
            "cited_claims":len(cited), "uncited_factual_claims":len(factual)-len(cited)}


def score_review(directory):
    status = json.loads((directory / "review_status.json").read_text(encoding="utf-8"))
    digest = hashlib.sha256((directory / "results.jsonl").read_bytes()).hexdigest()
    if digest != status["results_sha256"]:
        raise ValueError("Review results hash does not match; regenerate the review from this run.")
    if status["required_answers"] != 20 or len(status["selected_answer_ids"]) < 20:
        raise ValueError("The required 20-answer review cohort is incomplete.")
    with (directory / "claims.csv").open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    return score_claims(rows, status["selected_answer_ids"], status["reviewer"], status["reviewed_at"])
