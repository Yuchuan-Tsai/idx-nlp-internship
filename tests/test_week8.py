import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.listing_summarization import (
    AnswerabilityChecker,
    ListingSummarizer,
    evaluate_summary,
    load_gold_summaries,
    rouge_l,
)


class _DummyParser:
    def parse(self, query):
        return {"query": query}


class _DummyValidator:
    def __init__(self, valid=True):
        self.valid = valid

    def validate_query(self, filters):
        _ = filters
        if self.valid:
            return True, []
        return False, ["invalid city"]


def test_week8_summary_returns_non_empty_text():
    summarizer = ListingSummarizer()
    remarks = (
        "Beautiful 3 bed home in Irvine with lots of natural light. "
        "The backyard includes a pool and patio for entertaining. "
        "Close to schools and shopping with updated kitchen."
    )
    entities = {"bedrooms": 3}

    summary = summarizer.extractive_summary(remarks, entities, num_sentences=2)

    assert isinstance(summary, str)
    assert len(summary) > 0
    assert "3 bed" in summary or "pool" in summary.lower()


def test_week8_summary_handles_empty_remarks():
    summarizer = ListingSummarizer()
    summary = summarizer.extractive_summary("", {"bedrooms": 2})
    assert summary == ""


def test_week8_summary_uses_amenities_and_location():
    summarizer = ListingSummarizer()
    remarks = (
        "Spacious living area with a fireplace. "
        "Updated kitchen with stainless steel appliances. "
        "Walking distance to top schools and shopping."
    )
    entities = {"bedrooms": None, "amenities": ["fireplace"]}

    summary = summarizer.extractive_summary(remarks, entities, num_sentences=2)

    assert "fireplace" in summary.lower()
    assert "walking distance" in summary.lower()


def test_week8_rouge_l_basic():
    score = rouge_l("3 bed home in irvine with pool", "3 bed home in irvine")
    assert 0.0 < score <= 1.0
    assert rouge_l("", "anything") == 0.0


def test_week8_summary_meets_rouge_l_target():
    records = load_gold_summaries()
    summarizer = ListingSummarizer()
    metrics = evaluate_summary(summarizer, records)
    assert metrics["count"] >= 10
    assert metrics["mean_rouge_l"] > 0.4


def test_week8_pre_query_rejects_non_real_estate_question():
    checker = AnswerabilityChecker({}, _DummyValidator(valid=True), _DummyParser())
    ok, message = checker.check_pre_query("what is the weather today")
    assert not ok
    assert "real estate" in message.lower()


def test_week8_pre_query_uses_validator():
    checker = AnswerabilityChecker({}, _DummyValidator(valid=False), _DummyParser())
    ok, message = checker.check_pre_query("3 bed house in irvine")
    assert not ok
    assert "invalid data" in message.lower()


def test_week8_post_query_checks_empty_and_all_null():
    checker = AnswerabilityChecker({}, _DummyValidator(valid=True), _DummyParser())

    ok_empty, _ = checker.check_post_query("query", pd.DataFrame())
    assert not ok_empty

    ok_null, _ = checker.check_post_query("query", pd.DataFrame([{"a": None, "b": None}]))
    assert not ok_null

    ok_valid, message = checker.check_post_query("query", pd.DataFrame([{"a": 1, "b": None}]))
    assert ok_valid
    assert "results found" in message.lower()
