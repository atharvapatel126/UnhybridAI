"""Import completed human judgments; pending rows never produce fabricated scores."""
import argparse
import json
from pathlib import Path
from src.evaluation.review import score_review
from src.evaluation.reporting import write_summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_directory", type=Path)
    args = parser.parse_args()
    try:
        review = score_review(args.run_directory)
        summary = json.loads((args.run_directory / "summary.json").read_text(encoding="utf-8"))
        if review["human_review_status"] == "complete":
            summary.pop("reason", None)
        summary.update(review)
        write_summary(args.run_directory, summary)
        print(json.dumps(review, indent=2))
        return 0 if review["human_review_status"] == "complete" else 2
    except (ValueError, OSError) as exc:
        print(f"Review could not be scored: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
