from pathlib import Path

from support_email_classifier.io import classify_csv, write_audit


def test_classify_csv_and_audit(tmp_path: Path):
    input_path = tmp_path / "emails.csv"
    output_path = tmp_path / "classified.csv"
    audit_path = tmp_path / "audit.json"
    input_path.write_text(
        "id,subject,body\n"
        "1,Payment failed,My card payment failed and I need a receipt.\n"
        "2,Feature idea,Could you add Slack integration?\n",
        encoding="utf-8",
    )

    rows = classify_csv(input_path, output_path)
    write_audit(audit_path, rows)

    output = output_path.read_text(encoding="utf-8")
    audit = audit_path.read_text(encoding="utf-8")
    assert "category" in output
    assert "billing" in output
    assert "feature_request" in output
    assert '"total": 2' in audit


def test_missing_required_columns(tmp_path: Path):
    input_path = tmp_path / "emails.csv"
    input_path.write_text("subject\nHello\n", encoding="utf-8")

    try:
        classify_csv(input_path, tmp_path / "out.csv")
    except ValueError as exc:
        assert "body" in str(exc)
    else:
        raise AssertionError("expected ValueError")

