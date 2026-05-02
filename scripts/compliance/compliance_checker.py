"""Week 9 Fair Housing Act compliance checker.

See ``docs/week9_fair_housing_compliance.md`` for background on the Fair
Housing Act, the protected classes covered, and severity-level semantics.
"""

from __future__ import annotations

from typing import Dict, List


class ComplianceChecker:
    """Detect prohibited Fair Housing language in listing remarks."""

    def __init__(self):
        self.prohibited_patterns: Dict[str, List[Dict[str, str]]] = {
            "familial": [
                {"pattern": "no children", "severity": "error"},
                {"pattern": "adults only", "severity": "error"},
                {"pattern": "perfect for singles", "severity": "warning"},
            ],
            "disability": [
                {"pattern": "no wheelchairs", "severity": "error"},
                {"pattern": "must be able-bodied", "severity": "error"},
            ],
            "race": [
                {"pattern": "white neighborhood", "severity": "error"},
                {"pattern": "ethnic", "severity": "warning"},
                {"pattern": "diverse area", "severity": "info"},
            ],
            "religion": [
                {"pattern": "christian community", "severity": "error"},
                {"pattern": "jewish neighborhood", "severity": "error"},
            ],
        }

    def check_listing(self, text: str) -> Dict[str, object]:
        violations: List[Dict[str, str]] = []
        text_lower = str(text).lower()

        for category, entries in self.prohibited_patterns.items():
            for entry in entries:
                pattern = entry["pattern"]
                if pattern in text_lower:
                    violations.append({
                        "category": category,
                        "pattern": pattern,
                        "severity": entry["severity"],
                        "message": f"Prohibited language: {pattern} (Fair Housing violation)",
                    })

        return {"compliant": len(violations) == 0, "violations": violations}
