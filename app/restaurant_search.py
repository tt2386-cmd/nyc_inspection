"""NYC restaurant inspection search application."""

import os

import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from sodapy import Socrata


DATASET_ID = "43nn-pn8j"
SOCRATA_DOMAIN = "data.cityofnewyork.us"
DATA_LIMIT = 50000


def load_data(limit=DATA_LIMIT):
    """Retrieve and clean NYC restaurant inspection data."""

    load_dotenv()

    app_token = os.getenv("SOCRATA_APP_TOKEN")

    client = Socrata(
        SOCRATA_DOMAIN,
        app_token
    )

    print("Loading dataset...")

    results = client.get(
        DATASET_ID,
        limit=limit
    )

    df = pd.DataFrame.from_records(results)

    return clean_data(df)


def clean_data(df):
    """Clean and format restaurant inspection data."""

    df = df.copy()

    df["score"] = pd.to_numeric(
        df["score"],
        errors="coerce"
    )

    df["inspection_date"] = pd.to_datetime(
        df["inspection_date"],
        errors="coerce"
    )

    df["dba"] = (
        df["dba"]
        .fillna("")
        .str.upper()
        .str.strip()
    )

    df["building"] = (
        df["building"]
        .fillna("")
        .str.strip()
    )

    df["street"] = (
        df["street"]
        .fillna("")
        .str.upper()
        .str.strip()
    )

    df["address"] = (
        df["building"] + " " + df["street"]
    ).str.strip()

    return df


def find_restaurants(df, restaurant_name):
    """Find restaurants matching a search term."""

    restaurant_name = restaurant_name.strip().upper()

    if not restaurant_name:
        return pd.DataFrame(columns=df.columns)

    return df[
        df["dba"].str.contains(
            restaurant_name,
            case=False,
            na=False
        )
    ]


def get_addresses(matches):
    """Return unique addresses for matching restaurants."""

    return (
        matches[["address", "boro"]]
        .drop_duplicates()
        .sort_values("address")
        .reset_index(drop=True)
    )


def get_latest_inspection(matches, address):
    """Return the most recent scored inspection."""

    restaurant = matches[
        matches["address"] == address
    ].copy()

    scored = restaurant[
        restaurant["score"].notna()
    ]

    if scored.empty:
        return None

    scored = scored.sort_values(
        "inspection_date",
        ascending=False
    )

    return scored.iloc[0]


def get_inspection_history(matches, address):
    """Return inspection history for a selected restaurant."""

    restaurant = matches[
        matches["address"] == address
    ].copy()

    scored = restaurant[
        restaurant["score"].notna()
    ].copy()

    if scored.empty:
        return pd.DataFrame()

    scored = scored[
        scored["inspection_date"].dt.year > 1900
    ]

    history = (
        scored
        .groupby("inspection_date")["score"]
        .max()
        .reset_index()
        .sort_values("inspection_date")
    )

    return history


def display_summary(restaurant, address):
    """Display the most recent inspection summary."""

    scored_inspections = restaurant[
        restaurant["score"].notna()
    ].copy()

    if scored_inspections.empty:
        print("\nNo inspection score is available.")
        return

    scored_inspections = scored_inspections.sort_values(
        "inspection_date",
        ascending=False
    )

    latest_date = scored_inspections[
        "inspection_date"
    ].iloc[0]

    latest_score = scored_inspections[
        "score"
    ].iloc[0]

    latest_grade = scored_inspections[
        "grade"
    ].iloc[0]

    print("\n" + "=" * 60)
    print("RESTAURANT INSPECTION SUMMARY")
    print("=" * 60)

    print(
        f"Restaurant: {restaurant['dba'].iloc[0]}"
    )

    print(
        f"Address:    {address} "
        f"({restaurant['boro'].iloc[0]})"
    )

    print(
        "Most Recent Inspection: "
        f"{latest_date.strftime('%B %d, %Y')} "
        f"| Score: {latest_score}"
    )

    if pd.notna(latest_grade) and latest_grade != "":
        print(f"Current Grade:          {latest_grade}")
    else:
        print("Current Grade:          Not available")


def display_violations(restaurant):
    """Display violations from the most recent inspection."""

    scored_inspections = restaurant[
        restaurant["score"].notna()
    ].sort_values(
        "inspection_date",
        ascending=False
    )

    if scored_inspections.empty:
        return

    latest_date = scored_inspections[
        "inspection_date"
    ].iloc[0]

    latest_rows = restaurant[
        restaurant["inspection_date"] == latest_date
    ]

    print("\n" + "-" * 40)
    print(
        "VIOLATION DETAILS FROM THIS INSPECTION "
        f"({latest_date.strftime('%m/%d/%Y')}):"
    )
    print("-" * 40)

    critical_count = 0

    for _, row in latest_rows.iterrows():

        violation = row.get(
            "violation_description",
            "No description recorded."
        )

        critical_status = str(
            row.get("critical_flag", "")
        ).strip().upper()

        if (
            "CRITICAL" in critical_status
            and "NOT CRITICAL" not in critical_status
        ):
            critical_count += 1

            print("\n[CRITICAL VIOLATION]")
            print(f"  {violation}")

        else:
            print("\n[Standard Violation]")
            print(f"  {violation}")

    if critical_count == 0:
        print(
            "\nClean record! "
            "Zero critical violations were flagged."
        )
    else:
        print(
            f"\nTotal violations: "
            f"{len(latest_rows)} "
            f"({critical_count} critical)."
        )


def display_trend(history, restaurant_name, address):
    """Display the restaurant's inspection score trend."""

    if history.empty:
        print("\nNo inspection history available.")
        return

    print("\nGenerating timeline visualization...")

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        history["inspection_date"],
        history["score"],
        marker="o",
        linestyle="-",
        linewidth=2
    )

    ax.set_xlabel(
        "Inspection Date",
        fontsize=12
    )

    ax.set_ylabel(
        "Inspection Score (Lower is Better)",
        fontsize=12
    )

    ax.set_title(
        "Inspection Score Trend Over Time\n"
        f"{restaurant_name} - {address}",
        fontsize=14
    )

    ax.grid(
        True,
        linestyle="--",
        alpha=0.6
    )

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def run_application():
    """Run the restaurant inspection search application."""

    print("=" * 60)
    print("NYC RESTAURANT INSPECTION SEARCH")
    print("=" * 60)

    df = load_data()

    print("Data loaded and cleaned successfully!")

    while True:

        restaurant_name = input(
            "\nEnter restaurant name "
            "(or type 'quit' to exit): "
        ).strip()

        if restaurant_name.lower() == "quit":
            print("\nThanks for using the application!")
            break

        matches = find_restaurants(
            df,
            restaurant_name
        )

        if matches.empty:
            print(
                f"\nNo restaurants found matching "
                f"'{restaurant_name}'."
            )

            continue_search = input(
                "\nSearch again? (y/n): "
            ).strip().lower()

            if continue_search != "y":
                break

            continue

        addresses = get_addresses(matches)

        print(
            f"\nFound {len(addresses)} location(s) "
            f"matching '{restaurant_name}':\n"
        )

        for i, row in addresses.iterrows():
            print(
                f"{i + 1}. "
                f"{row['address']}, "
                f"{row['boro']}"
            )

        while True:

            try:
                selection = int(
                    input(
                        "\nSelect the address number: "
                    )
                )

                if 1 <= selection <= len(addresses):
                    break

                print(
                    f"Please enter a number between "
                    f"1 and {len(addresses)}."
                )

            except ValueError:
                print("Please enter a valid number.")

        selected_address = addresses.loc[
            selection - 1,
            "address"
        ]

        restaurant = matches[
            matches["address"] == selected_address
        ].copy()

        print(
            f"\nLocation Selected: "
            f"{restaurant['dba'].iloc[0]} "
            f"at {selected_address}"
        )

        display_summary(
            restaurant,
            selected_address
        )

        display_violations(
            restaurant
        )

        history = get_inspection_history(
            matches,
            selected_address
        )

        display_trend(
            history,
            restaurant["dba"].iloc[0],
            selected_address
        )

        continue_search = input(
            "\nWould you like to search another "
            "restaurant? (y/n): "
        ).strip().lower()

        if continue_search != "y":
            print("\nThanks for using the application!")
            break


if __name__ == "__main__":
    run_application()
