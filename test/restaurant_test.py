import pytest
import pandas as pd
import numpy as np

# Creating a tiny dummy dataset resembling the raw Socrata JSON data
# This enables us to test without relying on querying from the database itself

@pytest.fixture
def sample_raw_data():
    return [
        {"camis": "123456", "dba": " MCDONALD'S", "boro": "MANHATTAN", "building": "125", "street": "AMSTERDAM AVENUE", "inspection date": "3/21/2025", "violation description": "Hot TCS food item not held at or above 140 degrees F", "critical flag": "Critical", "score": "31", "grade": "Z"},
        {"camis": "123456", "dba": "MCDONALD'S ", "boro": "MANHATTAN", "building": "125", "street": "AMSTERDAM AVENUE", "inspection date": "5/15/2026", "violation description": "Live rats and other rodents", "critical flag": "Critical", "score": "30", "grade": "C"},
        {"camis": "123456", "dba": "MCDONALD'S ", "boro": "MANHATTAN", "building": "125", "street": "AMSTERDAM AVENUE", "inspection date": "5/15/2026", "violation description": "Thawing procedure improper", "critical flag": "Not Critical", "score": "12", "grade": "A"},
        {"camis": "555555", "dba": "Chuck E. CHEESE", "boro": "BROOKLYN", "building": "777", "street": "METROPOLITAN AVENUE", "inspection date": "4/4/2024", "violation description": "Live roaches in facility's food or non-food area", "critical flag": "Critical", "score": "None", "grade": "Z"},
        {"camis": "555555", "dba": "APPLEBEE'S", "boro": "MANHATTAN", "building": "777", "street": "W 42 STREET", "inspection date": "7/26/2023", "violation description": "Live roaches in facility's food or non-food area", "critical flag": "Critical", "score": "32", "grade": "C"}
    ]

# First test - verifies that text cleaning and address concantenation works properly
def test_data_address_cleaning(sample_raw_data):
    df = pd.DataFrame.from_records(sample_raw_data)

    # Cleaning logic from the dataset code cell
    df["dba"] = df["dba"].fillna("").str.upper().str.strip()
    df["building"] = df["building"].fillna("").str.strip()
    df["street"] = df["street"].fillna("").str.upper().str.strip()
    df["address"] = (df["building"] + " " + df["street"]).str.strip()

    # Use assert to verify that the output matches what we expect
    assert df["dba"].iloc[0] == "MCDONALD'S" # leading space is removed
    assert df["dba"].iloc[1] == "MCDONALD'S" 
    assert df["dba"].iloc[2] == "CHUCK E. CHEESE" # properly handled lowercase that was in dummy data
    assert df["address"].iloc[0] == "125 AMSTERDAM AVENUE"
    assert df["address"].iloc[2] == "777 METROPOLITAN AVENUE" # properly combines the building number and the street name, with space separating

# Second test - verifies the score datatype transformations and filtering of data
def test_score_processing(sample_raw_data):
    df = pd.DataFrame.from_records(sample_raw_data)

    # Cleaning logic from the dataset code cell
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["inspection_date"] = pd.to_datetime(df["inspection_date"], errors="coerce")

    # Process history dataframe step
    history = df[df["score"].notna()].copy()
    history = history[history["inspection_date"].dt.year > 1900]
    history = history.groupby("inspection_date")["score"].max().reset_index()

    # Use assert to verify that multiple citations on the same day are being correctly collapsed
    assert len(history) == 1
    assert history["score"].iloc[0] == 31
    assert history["score"].iloc[1] == 30 # properly pulls the maximum (worst score) for restaurant w/ multiple citations on the same day
    assert pd.isna(df["score"].iloc[3]) # properly handles when no score was reported 

print("Okay!")
