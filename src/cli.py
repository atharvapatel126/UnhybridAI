"""CLI demo before the UI: python -m src.cli 'question' --student S-012 --offline."""
import argparse
import json
from src.orchestrator import answer_query


def main():
    parser = argparse.ArgumentParser(description="UniHybrid AI - synthetic university evidence assistant")
    parser.add_argument("query")
    parser.add_argument("--student", default=None)
    parser.add_argument("--offline", action="store_true", help="Use deterministic routing; no Gemini requests")
    args = parser.parse_args()
    print(json.dumps(answer_query(args.query, args.student, use_llm=not args.offline), indent=2))


if __name__ == "__main__":
    main()
