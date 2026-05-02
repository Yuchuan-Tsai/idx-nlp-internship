"""Week 9 evaluation: precision/recall on a labeled compliance test set."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .compliance_checker import ComplianceChecker

DEFAULT_GOLD_PATH = Path("data/processed/gold_compliance.jsonl")


def load_gold(path: str | Path = DEFAULT_GOLD_PATH) -> List[Dict[str, object]]:
    """Load gold compliance records from a JSONL file."""
    records: List[Dict[str, object]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if "text" not in row or "violating" not in row:
                raise ValueError(f"Invalid record at line {line_no}: expected text and violating fields")
            records.append(row)
    return records


def evaluate(checker: ComplianceChecker, records: List[Dict[str, object]]) -> Dict[str, float]:
    """Run checker over labeled records and return precision/recall."""
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    total_violating = 0
    total_compliant = 0

    for row in records:
        expected_violating = bool(row["violating"])
        result = checker.check_listing(str(row["text"]))
        predicted_violating = not bool(result["compliant"])

        if expected_violating:
            total_violating += 1
            if predicted_violating:
                true_positives += 1
            else:
                false_negatives += 1
        else:
            total_compliant += 1
            if predicted_violating:
                false_positives += 1

    recall = true_positives / total_violating if total_violating else 0.0
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) else 0.0

    return {
        "recall": recall,
        "precision": precision,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "total_violating": total_violating,
        "total_compliant": total_compliant,
    }


def main(gold_path: str | Path = DEFAULT_GOLD_PATH) -> Dict[str, float]:
    records = load_gold(gold_path)
    checker = ComplianceChecker()
    metrics = evaluate(checker, records)
    print("Week 9 compliance evaluation")
    print(f"  total violating : {metrics['total_violating']}")
    print(f"  total compliant : {metrics['total_compliant']}")
    print(f"  true positives  : {metrics['true_positives']}")
    print(f"  false positives : {metrics['false_positives']}")
    print(f"  false negatives : {metrics['false_negatives']}")
    print(f"  recall          : {metrics['recall']:.3f}")
    print(f"  precision       : {metrics['precision']:.3f}")
    return metrics


if __name__ == "__main__":
    main()
