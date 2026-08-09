# NYC Restaurant Inspection Search

A Python application that allows users to search for restaurants in New York City and review their restaurant inspection history, scores, grades, violations, and inspection trends.

The application uses data from the NYC OpenData Restaurant Inspection Results dataset.

## Project Overview

Finding restaurant inspection information in a large public dataset can be difficult for someone who simply wants to check a particular restaurant.

This application simplifies that process by allowing a user to:

1. Enter a restaurant name.
2. View matching restaurant locations.
3. Select a specific address.
4. View the restaurant's most recent inspection.
5. See the inspection score and grade.
6. Review violations from the most recent inspection.
7. Identify critical violations.
8. View the restaurant's inspection score history over time.
9. Search for another restaurant without restarting the application.

## Data Source

The application uses the NYC Department of Health and Mental Hygiene Restaurant Inspection Results dataset provided through NYC OpenData.

Dataset:

https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j/about_data

The application accesses the dataset using the Socrata Open Data API.

## Features

### Restaurant Search

Users can enter a restaurant name and receive a list of matching restaurants.

### Location Selection

Because restaurant chains may have multiple locations, the application displays available addresses and allows the user to select the location they want to investigate.

### Inspection Summary

The application displays:

- Restaurant name
- Address
- Borough
- Most recent inspection date
- Inspection score
- Current grade

### Violation Details

The application identifies violations recorded during the most recent inspection and highlights critical violations.

### Inspection History

A Matplotlib visualization shows the restaurant's inspection scores over time.

Lower inspection scores indicate better inspection results.

### Repeat Searches

Users can search for another restaurant without restarting the Python application.

## Project Structure

```text
nyc_inspection/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── app/
│   ├── __init__.py
│   └── restaurant_search.py
│
├── data/
│   └── README.md
│
├── test/
│   ├── __init__.py
│   └── test_restaurant_search.py
│
├── .gitignore
├── conftest.py
├── LICENSE.md
├── README.md
└── requirements.txt
