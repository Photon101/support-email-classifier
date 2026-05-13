"""Deterministic support email classifier."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .rules import CATEGORY_KEYWORDS, URGENCY_KEYWORDS


@dataclass(frozen=True)
class Classification:
    category: str
    urgency: str
    confidence: float
    tags: tuple[str, ...]
    needs_review: bool
    rationale: str


def classify_email(subject: str, body: str) -> Classification:
    """Classify one support email into category, urgency, and review state."""
    text = normalize_text(f"{subject}\n{body}")
    category_scores = score_categories(text)
    category, category_score = pick_category(category_scores)
    urgency, urgency_score = pick_urgency(text)

    confidence = calculate_confidence(category_score, urgency_score, category == "general")
    tags = tuple(build_tags(category_scores, urgency, urgency_score))
    needs_review = confidence < 0.55 or category == "general" or conflicting_billing_cancel(category_scores)
    rationale = build_rationale(category, urgency, category_score, urgency_score, needs_review)

    return Classification(
        category=category,
        urgency=urgency,
        confidence=round(confidence, 2),
        tags=tags,
        needs_review=needs_review,
        rationale=rationale,
    )


def normalize_text(value: str) -> str:
    value = value.lower()
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def score_categories(text: str) -> dict[str, int]:
    return {
        category: sum(1 for keyword in keywords if keyword in text)
        for category, keywords in CATEGORY_KEYWORDS.items()
    }


def pick_category(scores: dict[str, int]) -> tuple[str, int]:
    best_category = "general"
    best_score = 0
    for category, score in scores.items():
        if score > best_score:
            best_category = category
            best_score = score
    return best_category, best_score


def pick_urgency(text: str) -> tuple[str, int]:
    critical_score = sum(1 for keyword in URGENCY_KEYWORDS["critical"] if keyword in text)
    if critical_score:
        return "critical", critical_score

    high_score = sum(1 for keyword in URGENCY_KEYWORDS["high"] if keyword in text)
    if high_score:
        return "high", high_score

    low_score = sum(1 for keyword in URGENCY_KEYWORDS["low"] if keyword in text)
    if low_score:
        return "low", low_score

    return "normal", 0


def calculate_confidence(category_score: int, urgency_score: int, is_general: bool) -> float:
    if is_general:
        return 0.35
    base = min(0.85, 0.42 + category_score * 0.14)
    if urgency_score:
        base += min(0.1, urgency_score * 0.04)
    return min(0.95, base)


def build_tags(scores: dict[str, int], urgency: str, urgency_score: int) -> list[str]:
    tags: list[str] = []
    for category, score in sorted(scores.items()):
        if score:
            tags.append(f"{category}:{score}")
    if urgency_score:
        tags.append(f"urgency:{urgency}")
    return tags


def conflicting_billing_cancel(scores: dict[str, int]) -> bool:
    return scores.get("billing", 0) > 0 and scores.get("cancellation", 0) > 0


def build_rationale(
    category: str,
    urgency: str,
    category_score: int,
    urgency_score: int,
    needs_review: bool,
) -> str:
    review_note = " review recommended" if needs_review else " route directly"
    return (
        f"category={category} matched {category_score} keyword(s); "
        f"urgency={urgency} matched {urgency_score} keyword(s);{review_note}"
    )

