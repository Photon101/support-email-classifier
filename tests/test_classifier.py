from support_email_classifier import classify_email


def test_billing_refund_high_urgency():
    result = classify_email(
        "Refund request",
        "I was charged twice and need this fixed today.",
    )

    assert result.category == "billing"
    assert result.urgency == "high"
    assert result.confidence >= 0.65
    assert result.needs_review is False


def test_account_login_problem():
    result = classify_email(
        "Cannot log in",
        "Password reset fails and I cannot access my account.",
    )

    assert result.category == "account"
    assert result.urgency == "critical"
    assert "account" in result.rationale


def test_general_low_confidence_requires_review():
    result = classify_email("Hello", "Can someone help me understand this?")

    assert result.category == "general"
    assert result.confidence == 0.35
    assert result.needs_review is True


def test_billing_cancellation_conflict_requires_review():
    result = classify_email(
        "Cancel subscription",
        "Please cancel my subscription and refund the last invoice.",
    )

    assert result.category in {"billing", "cancellation"}
    assert result.needs_review is True

