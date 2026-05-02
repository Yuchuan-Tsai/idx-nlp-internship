# Week 9: Fair Housing Compliance

## Goal
Detect prohibited Fair Housing language in listing remarks and flag biased descriptions before publication.

## Main files
- `scripts/compliance/compliance_checker.py`
- `scripts/compliance/evaluate_compliance.py`
- `scripts/compliance/example_workflow.py`
- `data/processed/gold_compliance.jsonl`

## Fair Housing Act background
The federal Fair Housing Act (42 U.S.C. 3601-3619) makes it illegal to make, print, or publish any advertisement that indicates a preference, limitation, or discrimination based on a protected class. Real estate listing remarks qualify as advertisements under HUD enforcement guidance.

## Protected classes covered by this checker
- **familial status**: language excluding or favoring families with children (e.g. `no children`, `adults only`).
- **disability**: language excluding people with disabilities or implying ability requirements (e.g. `no wheelchairs`, `must be able-bodied`).
- **race / color / national origin**: language describing the racial or ethnic makeup of a neighborhood (e.g. `white neighborhood`, `ethnic`, `diverse area`).
- **religion**: language indicating religious preference for occupants (e.g. `christian community`, `jewish neighborhood`).

This module does not cover sex, marital status, or source of income, which are protected by some state laws but require additional patterns to detect reliably.

## Severity levels
- **error**: clear violation; listing must be revised before publication.
- **warning**: likely violation; manual review required.
- **info**: ambiguous phrasing; surface for awareness but do not block.

## Notes
- `ComplianceChecker.check_listing(text)`:
  - Lowercase the text and substring-match each prohibited phrase.
  - Each hit becomes a violation with `category`, `pattern`, `severity`, and `message`.
  - Returns `{"compliant": bool, "violations": [...]}`.
- `evaluate_compliance(checker, records)`:
  - Reports recall / precision against `data/processed/gold_compliance.jsonl` (15 violating + 15 compliant).
  - Current numbers: recall = 1.000, precision = 1.000.
- `submit_listing(text)` integration:
  - Maps `error → rejected`, `warning → review`, otherwise `approved`.
