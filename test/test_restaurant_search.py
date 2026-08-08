"""Tests for the NYC restaurant inspection application."""

import pandas as pd

from app.restaurant_search import (
    clean_data,
    find_restaurants,
    get_addresses,
    get_inspection_history,
    get_latest_inspection,
)


def sample_data():
    """Create a small dataset for testing."""

    return pd.DataFrame({
        "camis": [
            "123456",
            "123456",
            "123456",
            "555555",
            "555555",
        ],
        "dba": [
            " MCDONALD'S",
            "MCDONALD'S ",
            "MCDONALD'S ",
            "Chuck E. CHEESE",
            "APPLEBEE'S",
        ],
        "boro": [
            "MANHATTAN",
            "MANHATTAN",
            "MANHATTAN",
            "BROOKLYN",
            "MANHATTAN",
        ],
        "building": [
            "125",
            "125",
            "125",
            "777",
            "777",
        ],
        "street": [
            "AMSTERDAM AVENUE",
            "AMSTERDAM AVENUE",
            "AMSTERDAM AVENUE",
            "METROPOLITAN AVENUE",
            "W 42 STREET",
        ],
        "inspection_date": [
            "2025-03-21",
            "2026-05-15",
            "2026-05-15",
            "2024-04-04",
            "2023-07-26",
        ],
        "violation_description": [
            "Hot TCS food item not held at "
            "or above 140 degrees F",
            "Live rats and other rodents",
            "Thawing procedure improper",
            "Live roaches in facility",
            "Live roaches in facility",
        ],
        "critical_flag": [
            "Critical",
            "Critical",
            "Not Critical",
            "Critical",
            "Critical",
        ],
        "score": [
            "31",
            "30",
            "12",
            "None",
            "32",
        ],
        "grade": [
            "Z",
            "C",
            "A",
            "Z",
            "C",
        ],
    })


def test_clean_data():
    """Restaurant names and addresses should be cleaned."""

    df = clean_data(sample_data())

    assert df["dba"].iloc[0] == "MCDONALD'S"
    assert df["dba"].iloc[1] == "MCDONALD'S"
    assert df["dba"].iloc[3] == "CHUCK E. CHEESE"

    assert (
        df["address"].iloc[0]
        == "125 AMSTERDAM AVENUE"
    )


def test_score_processing():
    """Scores should be converted to numeric values."""

    df = clean_data(sample_data())

    assert df["score"].iloc[0] == 31
    assert df["score"].iloc[1] == 30

    assert pd.isna(
        df["score"].iloc[3]
    )


def test_find_restaurants():
    """Restaurant search should find matching names."""

    df = clean_data(sample_data())

    results = find_restaurants(
        df,
        "mcdonald"
    )

    assert len(results) == 3


def test_search_is_case_insensitive():
    """Restaurant searches should ignore capitalization."""

    df = clean_data(sample_data())

    results = find_restaurants(
        df,
        "McDoNaLd'S"
    )

    assert len(results) == 3


def test_empty_search():
    """An empty restaurant search should return no results."""

    df = clean_data(sample_data())

    results = find_restaurants(
        df,
        ""
    )

    assert results.empty


def test_unknown_restaurant():
    """An unknown restaurant should return no results."""

    df = clean_data(sample_data())

    results = find_restaurants(
        df,
        "Pizza Restaurant That Does Not Exist"
    )

    assert results.empty


def test_get_addresses():
    """Restaurant matches should produce unique addresses."""

    df = clean_data(sample_data())

    matches = find_restaurants(
        df,
        "MCDONALD'S"
    )

    addresses = get_addresses(matches)

    assert len(addresses) == 1
    assert (
        addresses["address"].iloc[0]
        == "125 AMSTERDAM AVENUE"
    )


def test_get_latest_inspection():
    """The most recent scored inspection should be returned."""

    df = clean_data(sample_data())

    matches = find_restaurants(
        df,
        "MCDONALD'S"
    )

    latest = get_latest_inspection(
        matches,
        "125 AMSTERDAM AVENUE"
    )

    assert latest["score"] == 30
    assert latest["grade"] == "C"


def test_inspection_history():
    """Inspection history should group scores by date."""

    df = clean_data(sample_data())

    matches = find_restaurants(
        df,
        "MCDONALD'S"
    )

    history = get_inspection_history(
        matches,
        "125 AMSTERDAM AVENUE"
    )

    assert len(history) == 2
    assert history["score"].max() == 31
    assert history["score"].min() == 30


def test_latest_inspection_handles_missing_scores():
    """Restaurants without scores should return no result."""

    df = clean_data(sample_data())

    matches = find_restaurants(
        df,
        "CHUCK E. CHEESE"
    )

    latest = get_latest_inspection(
        matches,
        "777 METROPOLITAN AVENUE"
    )

    assert latest is None
