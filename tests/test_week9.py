import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.compliance import (
    ComplianceChecker,
    evaluate_compliance,
    load_gold_compliance,
    submit_listing,
)


def test_week9_compliant_listing_passes():
    checker = ComplianceChecker()
    result = checker.check_listing(
        "Beautiful 3 bed home with pool, updated kitchen, and 2-car garage."
    )
    assert result["compliant"] is True
    assert result["violations"] == []


def test_week9_familial_violation_detected():
    checker = ComplianceChecker()
    result = checker.check_listing("Quiet condo, adults only, no children allowed.")
    assert result["compliant"] is False
    categories = [v["category"] for v in result["violations"]]
    assert "familial" in categories


def test_week9_violation_includes_severity_and_message():
    checker = ComplianceChecker()
    result = checker.check_listing("Christian community welcomes you home.")
    assert result["compliant"] is False
    violation = result["violations"][0]
    assert violation["severity"] == "error"
    assert "Fair Housing" in violation["message"]


def test_week9_warning_and_info_levels():
    checker = ComplianceChecker()

    warning_result = checker.check_listing("This unit is perfect for singles who travel.")
    severities = [v["severity"] for v in warning_result["violations"]]
    assert "warning" in severities

    info_result = checker.check_listing("A diverse area near downtown.")
    severities = [v["severity"] for v in info_result["violations"]]
    assert "info" in severities


def test_week9_recall_and_precision_meet_targets():
    records = load_gold_compliance()
    checker = ComplianceChecker()
    metrics = evaluate_compliance(checker, records)
    assert metrics["total_violating"] >= 15
    assert metrics["recall"] == 1.0
    assert metrics["precision"] > 0.8


def test_week9_submit_listing_workflow_blocks_errors():
    rejected = submit_listing("Adults only retirement community, no children allowed.")
    assert rejected["status"] == "rejected"
    assert rejected["approved"] is False

    review = submit_listing("Studio apartment, perfect for singles working downtown.")
    assert review["status"] == "review"
    assert review["approved"] is False

    approved = submit_listing("Beautiful 3 bed home with pool and updated kitchen.")
    assert approved["status"] == "approved"
    assert approved["approved"] is True
    assert approved["violations"] == []
