"""Command line interface for the support email classifier."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .io import classify_csv, write_audit


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "classify":
            rows = classify_csv(args.input, args.output)
            if args.audit:
                write_audit(args.audit, rows)
            print(f"classified {len(rows)} row(s) -> {args.output}")
            return 0
        parser.print_help()
        return 2
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="support-email-classifier",
        description="Classify support email CSV exports into category and urgency fields.",
    )
    subparsers = parser.add_subparsers(dest="command")

    classify = subparsers.add_parser("classify", help="classify a support email CSV")
    classify.add_argument("input", type=Path, help="input CSV with subject and body columns")
    classify.add_argument("--output", "-o", type=Path, required=True, help="output CSV path")
    classify.add_argument("--audit", type=Path, help="optional JSON audit report path")

    return parser


if __name__ == "__main__":
    raise SystemExit(main())

