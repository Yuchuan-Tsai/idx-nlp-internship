"""Week 8 listing summarization helpers."""

from __future__ import annotations

import re
from typing import Dict, List

import nltk


class ListingSummarizer:
    """Extractive listing summarizer."""

    NUMERIC_ENTITY_KEYS = ("bedrooms", "bathrooms", "price", "sqft")

    LOCATION_KEYWORDS = (
        "near",
        "close to",
        "walking distance",
        "minutes to",
        "schools",
        "shopping",
    )

    def __init__(self):
        pass

    def _sentence_split(self, text: str) -> List[str]:
        try:
            return nltk.sent_tokenize(text)
        except LookupError:
            return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

    def extractive_summary(self, remarks: str, entities: Dict[str, object], num_sentences: int = 2) -> str:
        if not remarks:
            return ""

        sentences = self._sentence_split(str(remarks))
        if not sentences:
            return ""

        scores = []
        for i, sent in enumerate(sentences):
            score = 0
            sent_lower = sent.lower()

            if i == 0:
                score += 2

            for key in self.NUMERIC_ENTITY_KEYS:
                val = entities.get(key)
                if val in (None, ""):
                    continue
                if str(val) in sent:
                    score += 1

            amenities = entities.get("amenities") or []
            for amenity in amenities:
                if str(amenity).lower() in sent_lower:
                    score += 1

            if any(kw in sent_lower for kw in self.LOCATION_KEYWORDS):
                score += 1

            scores.append((score, sent))

        top_sentences = sorted(scores, reverse=True)[:num_sentences]
        ordered = sorted(top_sentences, key=lambda x: sentences.index(x[1]))
        return " ".join(s[1] for s in ordered)


def rouge_l(reference: str, hypothesis: str) -> float:
    """Lightweight ROUGE-L F1 using token-level longest common subsequence."""
    ref_tokens = re.findall(r"\w+", str(reference).lower())
    hyp_tokens = re.findall(r"\w+", str(hypothesis).lower())
    if not ref_tokens or not hyp_tokens:
        return 0.0

    m, n = len(ref_tokens), len(hyp_tokens)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            if ref_tokens[i] == hyp_tokens[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
            else:
                dp[i + 1][j + 1] = max(dp[i + 1][j], dp[i][j + 1])

    lcs = dp[m][n]
    if lcs == 0:
        return 0.0
    precision = lcs / n
    recall = lcs / m
    return 2 * precision * recall / (precision + recall)
