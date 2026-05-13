"""CSV and audit helpers for support email classification."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Iterable
import json

from .classifier import Classification, classify_email


REQUIRED_COLUMNS = {"subject", "body"}


def classify_csv(input_path: Path, output_path: Path) -> list[dict[str, str]]:
    rows = read_rows(input_path)
    classified: list[dict[str, str]] = []
    for row in rows:
        result = classify_email(row.get("subject", ""), row.get("body", ""))
        classified.append(merge_result(row, result))
    write_rows(output_path, classified)
    return classified


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            raise ValueError(f"missing required column(s): {', '.join(sorted(missing))}")
        return [dict(row) for row in reader]


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def merge_result(row: dict[str, str], result: Classification) -> dict[str, str]:
    merged = dict(row)
    merged.update(
        {
            "category": result.category,
            "urgency": result.urgency,
            "confidence": f"{result.confidence:.2f}",
            "tags": ";".join(result.tags),
            "needs_review": str(result.needs_review).lower(),
            "rationale": result.rationale,
        }
    )
    return merged


def write_audit(path: Path, rows: Iterable[dict[str, str]]) -> None:
    materialized = list(rows)
    category_counts = Counter(row["category"] for row in materialized)
    urgency_counts = Counter(row["urgency"] for row in materialized)
    review_rows = [row for row in materialized if row["needs_review"] == "true"]

    payload = {
        "total": len(materialized),
        "category_counts": dict(sorted(category_counts.items())),
        "urgency_counts": dict(sorted(urgency_counts.items())),
        "needs_review": len(review_rows),
        "low_confidence_examples": review_rows[:10],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

