# Support Email Classification And Triage Skill

Use this skill when a task involves classifying support tickets, customer emails, contact-form messages, or exported helpdesk CSV data into actionable categories and urgency levels.

## What This Skill Provides

- Deterministic classification for common support categories such as billing, technical issue, account access, product feedback, cancellation, and sales lead.
- Urgency scoring with review flags for ambiguous or high-impact messages.
- CSV input/output so the workflow can sit before a helpdesk import, spreadsheet review, or LLM enrichment step.
- JSON audit output summarizing category counts, urgency distribution, and rows needing human review.
- A small Python codebase that can be adapted to client-specific categories, keywords, and routing rules.

## Best Fit

- Historical support-email tagging.
- Lightweight helpdesk triage before Zendesk, Intercom, Freshdesk, Gmail, or spreadsheet workflows.
- Contact-form lead quality review.
- Preparing clean, labeled datasets for later LLM or analytics work.

## Repository

Source and runnable examples:

https://github.com/Photon101/support-email-classifier

## Quick Start

```bash
git clone https://github.com/Photon101/support-email-classifier
cd support-email-classifier
PYTHONPATH=src python3 -m support_email_classifier.cli examples/support_emails.csv /tmp/classified.csv --audit /tmp/classifier-audit.json
```

For development validation:

```bash
uv run --extra dev python -m pytest
```

## Agent Workflow

1. Inspect the client's existing categories, tags, and escalation rules.
2. Run the classifier on a sample CSV export.
3. Review the audit summary for categories with low confidence or high review counts.
4. Add client-specific routing rules only when sample data proves they are needed.
5. Deliver classified CSV output plus an audit summary and suggested routing changes.

## Safety Rules

- Do not paste raw customer emails or private support data into public issues, PRs, or marketplace listings.
- Use synthetic samples in public repos and demos.
- Treat the deterministic classifier as a first-pass triage layer; keep a human review path for low-confidence, legal, safety, payment, or account-access cases.

