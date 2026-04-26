"""Week 7 intent classification utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def load_intent_dataset(dataset_path: str | Path) -> Tuple[List[str], List[str]]:
    """Load `query` + `label` pairs from a JSONL file."""
    path = Path(dataset_path)
    queries: List[str] = []
    labels: List[str] = []

    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if "query" not in row or "label" not in row:
                raise ValueError(f"Invalid record at line {line_no}: expected query and label fields")
            queries.append(str(row["query"]))
            labels.append(str(row["label"]))

    return queries, labels


@dataclass
class IntentPrediction:
    intent: str
    confidence: float
    is_uncertain: bool
    probabilities: Dict[str, float]


class IntentClassifier:
    """Starter-code based classifier with minimal Week 7 extensions."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=500)
        self.model = LogisticRegression()
        self.labels = ["browsing", "researching", "ready_to_buy"]

    def train(self, queries: Sequence[str], labels: Sequence[str]) -> None:
        X = self.vectorizer.fit_transform(queries)
        self.model.fit(X, labels)

    def predict(self, query: str) -> Tuple[str, float]:
        X = self.vectorizer.transform([query])
        probas = self.model.predict_proba(X)[0]
        intent = self.labels[int(probas.argmax())]
        confidence = float(probas.max())
        return intent, confidence

    def predict_proba(self, query: str) -> Dict[str, float]:
        X = self.vectorizer.transform([query])
        probas = self.model.predict_proba(X)[0]
        return {label: float(probas[idx]) for idx, label in enumerate(self.labels)}

    def classify(self, query: str, uncertainty_threshold: float = 0.60) -> IntentPrediction:
        intent, confidence = self.predict(query)
        probs = self.predict_proba(query)
        return IntentPrediction(
            intent=intent,
            confidence=confidence,
            is_uncertain=confidence < uncertainty_threshold,
            probabilities=probs,
        )

    def evaluate(self, queries: Sequence[str], labels: Sequence[str]) -> float:
        X = self.vectorizer.transform(queries)
        pred_labels = self.model.predict(X)
        correct = sum(1 for p, t in zip(pred_labels, labels) if p == t)
        return correct / len(labels) if labels else 0.0
