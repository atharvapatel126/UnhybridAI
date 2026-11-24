"""Run a new evaluation; never overwrite a completed or partial earlier run."""
import argparse
from pathlib import Path
import json
from config import ROOT
from src.evaluation.runner import evaluate


def main():
    default = ROOT / "evaluation/eval_set.json"
    if not default.exists():
        default = ROOT / "tests/eval_set.json"
    parser = argparse.ArgumentParser(description="UniHybrid AI measured evaluation")
    parser.add_argument("--dataset", type=Path, default=default)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=["offline", "live"], default="offline")
    parser.add_argument("--pause", type=float, default=0)
    parser.add_argument("--image-id", default=None)
    args = parser.parse_args()
    try:
        print(json.dumps(evaluate(args.dataset, args.output, args.mode, args.pause, args.image_id), indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(f"Evaluation could not complete: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
