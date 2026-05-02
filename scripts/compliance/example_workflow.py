"""Week 9 example: integrating ComplianceChecker into a listing submission flow."""

from __future__ import annotations

from typing import Dict, Optional

from .compliance_checker import ComplianceChecker


def submit_listing(text: str, checker: Optional[ComplianceChecker] = None) -> Dict[str, object]:
    """Validate listing remarks before publication.

    Block on any error-level violation, surface warnings/info for review,
    and approve otherwise.
    """
    checker = checker or ComplianceChecker()
    result = checker.check_listing(text)
    violations = list(result["violations"])

    has_error = any(v["severity"] == "error" for v in violations)
    has_warning = any(v["severity"] == "warning" for v in violations)

    if has_error:
        status = "rejected"
        message = "Listing rejected: please revise prohibited language before resubmitting."
    elif has_warning:
        status = "review"
        message = "Listing held for manual review by compliance team."
    else:
        status = "approved"
        message = "Listing approved for publication."

    return {
        "status": status,
        "approved": status == "approved",
        "message": message,
        "violations": violations,
    }


def main() -> None:
    samples = [
        "Beautiful 3 bed home with pool and updated kitchen.",
        "Studio apartment, perfect for singles working downtown.",
        "Adults only retirement community, no children allowed.",
    ]
    for text in samples:
        outcome = submit_listing(text)
        print(f"[{outcome['status']}] {text}")
        print(f"  -> {outcome['message']}")
        for v in outcome["violations"]:
            print(f"     - {v['severity']}: {v['pattern']} ({v['category']})")


if __name__ == "__main__":
    main()
