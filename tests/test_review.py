from src.evaluation.review import draft_claims, score_claims


def row(identifier="Q1", supported="yes", citation="yes"):
    return {"answer_id":identifier, "kind":"factual", "supported":supported,
            "citation_correct":citation, "cited_tags":"[SQL-1]"}


def test_pending_review_never_fabricates_scores():
    result = score_claims([row()], ["Q1"], "", "")
    assert result["human_review_status"] == "pending" and result["answer_faithfulness"] is None
    result = score_claims([row(supported="")], ["Q1"], "Unit test reviewer", "2026-11-24T00:00:00+05:30")
    assert result["human_review_status"] == "pending"


def test_completed_claim_ratios_and_nonfactual_exclusion():
    rows = [row(), row("Q2", "no", "no"), dict(row("Q2", "n/a", "n/a"), kind="nonfactual")]
    result = score_claims(rows, ["Q1", "Q2"], "Unit test reviewer", "2026-11-24T00:00:00+05:30")
    assert result["human_review_status"] == "complete" and result["reviewed_factual_claims"] == 2
    assert result["answer_faithfulness"] == .5 and result["source_attribution_correctness"] == .5
    assert result["reviewed_answers"] == 2


def test_missing_answer_or_unzoned_date_stays_pending():
    assert score_claims([row()], ["Q1", "Q2"], "Reviewer", "2026-11-24T00:00:00+05:30")["human_review_status"] == "pending"
    assert score_claims([row()], ["Q1"], "Reviewer", "2026-11-24T00:00:00")["human_review_status"] == "pending"


def test_draft_claim_rows_are_never_judgments():
    claims = draft_claims({"generation_method":"generated", "answer":"**Answer**\n\nGPA 8.4 [SQL-1].\n\n**Reasoning**\n\nRecord [SQL-1].\n\n**Missing information**\n\nNone identified."})
    assert claims[0][0] == "factual" and claims[0][2] == "[SQL-1]"
    assert claims[-1][0] == "nonfactual"
