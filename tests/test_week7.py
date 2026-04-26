import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.intent_classifier import IntentClassifier, load_intent_dataset


DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "intent_labeled_queries_week7.jsonl"

def test_week7_dataset_has_200_plus_queries():
    queries, labels = load_intent_dataset(DATASET_PATH)
    assert len(queries) >= 200
    assert len(queries) == len(labels)
    assert set(labels) == {"browsing", "researching", "ready_to_buy"}


def test_week7_classifier_accuracy_reaches_target():
    queries, labels = load_intent_dataset(DATASET_PATH)
    paired = list(zip(queries, labels))
    random.Random(42).shuffle(paired)

    split = int(len(paired) * 0.8)
    train_pairs, test_pairs = paired[:split], paired[split:]
    train_q, train_y = zip(*train_pairs)
    test_q, test_y = zip(*test_pairs)

    clf = IntentClassifier()
    clf.train(train_q, train_y)

    accuracy = clf.evaluate(test_q, test_y)
    assert accuracy >= 0.80


def test_week7_classifier_returns_confidence_and_uncertainty():
    queries, labels = load_intent_dataset(DATASET_PATH)
    clf = IntentClassifier()
    clf.train(queries, labels)

    intent, confidence = clf.predict("i am ready to buy a 3 bed home under 900k in irvine")
    detail = clf.classify("just browsing homes maybe in a city", uncertainty_threshold=0.75)

    assert intent in {"browsing", "researching", "ready_to_buy"}
    assert 0.0 <= confidence <= 1.0
    assert detail.intent in {"browsing", "researching", "ready_to_buy"}
    assert 0.0 <= detail.confidence <= 1.0
    assert detail.is_uncertain == (detail.confidence < 0.75)
    assert set(detail.probabilities.keys()) == {"browsing", "researching", "ready_to_buy"}


def test_week7_prediction_output_is_rich_and_standalone():
    queries, labels = load_intent_dataset(DATASET_PATH)
    clf = IntentClassifier()
    clf.train(queries, labels)
    result = clf.classify("3 bed under 700k in Irvine with pool and garage")

    assert result.intent in {"browsing", "researching", "ready_to_buy"}
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.is_uncertain, bool)
    assert set(result.probabilities.keys()) == {"browsing", "researching", "ready_to_buy"}
