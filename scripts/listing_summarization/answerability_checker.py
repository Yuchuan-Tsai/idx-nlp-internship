"""Week 9 answerability checks for user queries and query results."""

from __future__ import annotations


class AnswerabilityChecker:
    """Check whether a question can be answered before/after SQL execution."""

    def __init__(self, taxonomy, schema_validator, parser):
        self.taxonomy = taxonomy
        self.validator = schema_validator
        self.parser = parser
        self.real_estate_keywords = [
            "house",
            "home",
            "bed",
            "bath",
            "property",
            "listing",
            "price",
            "sqft",
            "pool",
            "garage",
        ]

    def check_pre_query(self, query):
        query_lower = str(query).lower()
        has_re_terms = any(kw in query_lower for kw in self.real_estate_keywords)
        if not has_re_terms:
            return False, "This doesn't appear to be a real estate question"

        filters = self.parser.parse(query)
        valid, errors = self.validator.validate_query(filters)
        if not valid:
            return False, f"Query references invalid data: {'; '.join(errors)}"

        return True, "Query is answerable"

    def check_post_query(self, query, results_df):
        _ = query
        if len(results_df) == 0:
            return False, "No listings match your criteria"
        if results_df.isnull().all().all():
            return False, "Query returned no meaningful data"
        return True, "Results found"
