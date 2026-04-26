import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.data_extractor.entity_extractor import EntityExtractor
from scripts.data_loading.meaningful_taxonomy_json_builder import taxonomy_data
from scripts.signal_extractor.signal_extractor import SignalExtractor
from scripts.signal_extractor import run_signal_extractor as week6_runner


@pytest.fixture
def signal_extractor():
    return SignalExtractor(taxonomy_data, EntityExtractor())


STRUCTURED_CASES = [
    {
        "text": "Beautiful 3 bed 2.5 bath home with 2,100 sqft, fireplace, and attached garage.",
        "expected": {
            "bedrooms": 3,
            "bathrooms": 2.5,
            "sqft": 2100,
            "amenities": ["fireplace", "attached garage"],
        },
    },
    {
        "text": "Brand new condo with 4 bedrooms, 3 bathrooms, $850000 price, 1800 sq ft, balcony.",
        "expected": {
            "bedrooms": 4,
            "bathrooms": 3.0,
            "price": 850000,
            "sqft": 1800,
            "amenities": ["condo", "balcony"],
        },
    },
    {
        "text": "Cozy 2bd 1ba cottage has 950 square feet and a walk-in closet.",
        "expected": {
            "bedrooms": 2,
            "bathrooms": 1.0,
            "sqft": 950,
            "amenities": ["walk-in closet", "cottage"],
        },
    },
    {
        "text": "Spacious 5 br 4 bath residence listed at $1250000 with 3200 sqft and swimming pool.",
        "expected": {
            "bedrooms": 5,
            "bathrooms": 4.0,
            "price": 1250000,
            "sqft": 3200,
            "amenities": ["swimming pool"],
        },
    },
    {
        "text": "Townhouse offering 3 bedrooms, 2 baths, 1,650 sq ft, open concept kitchen and fireplace.",
        "expected": {
            "bedrooms": 3,
            "bathrooms": 2.0,
            "sqft": 1650,
            "amenities": ["townhouse", "open concept", "fireplace"],
        },
    },
]


FREE_TEXT_CASES = [
    {
        "text": "Fully renovated and move-in ready home in a quiet neighborhood near schools.",
        "condition": ["renovated", "move-in ready"],
        "financing": [],
        "location": ["quiet neighborhood", "near schools"],
    },
    {
        "text": "As-is fixer upper with seller financing available. Corner lot with freeway access.",
        "condition": ["as-is", "fixer"],
        "financing": ["seller financing"],
        "location": ["corner lot", "close to freeway"],
    },
    {
        "text": "New construction, well maintained, FHA financing and VA loan accepted.",
        "condition": ["new construction", "well maintained"],
        "financing": ["fha", "va"],
        "location": [],
    },
    {
        "text": "Original condition property, cash only, assumable mortgage, close to downtown.",
        "condition": ["original condition"],
        "financing": ["cash", "assumable"],
        "location": ["downtown"],
    },
    {
        "text": "Turn-key home with conventional financing, walking distance to shopping and dining.",
        "condition": ["move-in ready"],
        "financing": ["conventional"],
        "location": ["walking distance", "close to shopping"],
    },
]


def test_extract_signals_schema(signal_extractor):
    record = {
        "L_ListingID": 1001,
        "L_Remarks": "Beautiful 3 bed 2 bath home with fireplace and attached garage."
    }

    out = signal_extractor.extract_signals(record)

    assert set(out.keys()) == {
        "listing_id",
        "entities",
        "amenities",
        "condition_keywords",
        "financing_terms",
        "location_features",
    }
    assert out["listing_id"] == 1001
    assert isinstance(out["entities"], dict)
    assert isinstance(out["amenities"], list)


def test_week6_core_methods(signal_extractor):
    text = (
        "Move-in ready and fully renovated home with seller financing. "
        "Walking distance to shopping and near schools with fireplace and balcony."
    )

    amenities = signal_extractor._match_amenities(text)
    condition = signal_extractor._extract_condition(text)
    financing = signal_extractor._extract_financing(text)
    location = signal_extractor._extract_location(text)

    assert "fireplace" in amenities
    assert "balcony" in amenities
    assert "move-in ready" in condition
    assert "renovated" in condition
    assert "seller financing" in financing
    assert "walking distance" in location
    assert "near schools" in location


def test_structured_accuracy_threshold(signal_extractor):
    checks = 0
    matched = 0

    for case in STRUCTURED_CASES:
        out = signal_extractor.extract_signals({"L_ListingID": 1, "L_Remarks": case["text"]})
        entities = out["entities"]

        for k in ["bedrooms", "bathrooms", "price", "sqft"]:
            if k in case["expected"]:
                checks += 1
                if entities.get(k) == case["expected"][k]:
                    matched += 1

        for amenity in case["expected"].get("amenities", []):
            checks += 1
            if amenity in out["amenities"]:
                matched += 1

    accuracy = matched / checks

    assert checks >= 20
    assert accuracy >= 0.90


def test_free_text_accuracy_threshold(signal_extractor):
    checks = 0
    matched = 0

    for case in FREE_TEXT_CASES:
        condition = set(signal_extractor._extract_condition(case["text"]))
        financing = set(signal_extractor._extract_financing(case["text"]))
        location = set(signal_extractor._extract_location(case["text"]))

        for item in case["condition"]:
            checks += 1
            if item in condition:
                matched += 1

        for item in case["financing"]:
            checks += 1
            if item in financing:
                matched += 1

        for item in case["location"]:
            checks += 1
            if item in location:
                matched += 1

    accuracy = matched / checks

    assert checks >= 15
    assert accuracy >= 0.75


def test_week6_runner_writes_json(monkeypatch, tmp_path):
    fake_rows = [
        {
            "L_ListingID": 1,
            "L_Remarks": "3 bed 2 bath with fireplace and seller financing in a quiet neighborhood.",
        },
        {
            "L_ListingID": 2,
            "L_Remarks": "4 bed 3 bath, newly built condo with balcony and walking distance to downtown.",
        },
    ]

    monkeypatch.setattr(week6_runner, "fetch_all_listings", lambda: iter(fake_rows))

    out_file = tmp_path / "week6_output.json"
    week6_runner.run(str(out_file))

    assert out_file.exists()

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert len(data) == 2
    assert all("listing_id" in row for row in data)
    assert all("entities" in row for row in data)
    assert all("amenities" in row for row in data)
