# support-email-classifier

A small, dependency-light starter for classifying support emails into operational tags, urgency, and review queues.

It is intended for teams that have an email export and need a repeatable first pass before moving to a heavier LLM workflow. The classifier is deterministic by default, so outputs are auditable and safe to run on sample data without API keys.

## What It Does

- Reads CSV support exports with `subject` and `body` columns.
- Adds `category`, `urgency`, `confidence`, `tags`, and `needs_review`.
- Produces an optional JSON audit report with category counts, review count, and low-confidence examples.
- Keeps rules in code so clients can see exactly why each label was applied.

## Quick Start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
support-email-classifier classify examples/sample_emails.csv --output /tmp/classified.csv --audit /tmp/audit.json
```

Without installing:

```bash
PYTHONPATH=src python -m support_email_classifier.cli classify examples/sample_emails.csv --output /tmp/classified.csv
```

## Input Format

Required columns:

- `subject`
- `body`

Optional columns are preserved in the output.

Example:

```csv
id,subject,body
1,Refund request,I was charged twice and need this fixed today.
2,Login problem,I cannot reset my password.
```

## Output Fields

- `category`: one of `billing`, `account`, `bug`, `feature_request`, `cancellation`, `sales`, or `general`.
- `urgency`: `low`, `normal`, `high`, or `critical`.
- `confidence`: score from `0.00` to `1.00`.
- `tags`: semicolon-separated rule tags.
- `needs_review`: `true` for low-confidence or risky classifications.

## Why Deterministic First

For 5,000+ support emails, a deterministic pass gives a useful baseline:

- obvious cases can be routed immediately;
- ambiguous cases become a small review queue;
- rules can be reviewed by support leads;
- an LLM can later be used only for the expensive ambiguous slice.

## Development

```bash
pip install -e ".[dev]"
pytest
python -m support_email_classifier.cli classify examples/sample_emails.csv --output /tmp/classified.csv --audit /tmp/audit.json
```

## Extension Points

- Add client-specific terms in `rules.py`.
- Add a new category by defining keywords and tests.
- Send rows with `needs_review=true` to an LLM or human QA workflow.
