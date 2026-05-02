"""Week 8 evaluation: mean ROUGE-L on a labeled summary test set."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .listing_summarizer import ListingSummarizer, rouge_l

DEFAULT_GOLD_PATH = Path("data/processed/gold_summaries.jsonl")


def load_gold(path: str | Path = DEFAULT_GOLD_PATH) -> List[Dict[str, object]]:
    """Load gold summary records from a JSONL file."""
    records: List[Dict[str, object]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            for key in ("remarks", "reference"):
                if key not in row:
                    raise ValueError(f"Invalid record at line {line_no}: missing {key}")
            records.append(row)
    return records


def evaluate(
    summarizer: ListingSummarizer,
    records: List[Dict[str, object]],
    num_sentences: int = 2,
) -> Dict[str, object]:
    """Score summarizer output against reference summaries with ROUGE-L F1."""
    scores: List[float] = []
    per_record: List[Dict[str, object]] = []

    for row in records:
        remarks = str(row["remarks"])
        entities = row.get("entities") or {}
        reference = str(row["reference"])
        prediction = summarizer.extractive_summary(remarks, entities, num_sentences=num_sentences)
        score = rouge_l(reference, prediction)
        scores.append(score)
        per_record.append({
            "reference": reference,
            "prediction": prediction,
            "rouge_l": score,
        })

    mean_score = sum(scores) / len(scores) if scores else 0.0

    return {
        "mean_rouge_l": mean_score,
        "count": len(scores),
        "per_record": per_record,
    }


def main(gold_path: str | Path = DEFAULT_GOLD_PATH) -> Dict[str, object]:
    records = load_gold(gold_path)
    summarizer = ListingSummarizer()
    metrics = evaluate(summarizer, records)
    print("Week 8 summary evaluation")
    print(f"  records         : {metrics['count']}")
    print(f"  mean ROUGE-L F1 : {metrics['mean_rouge_l']:.3f}")
    return metrics


if __name__ == "__main__":
    main()
