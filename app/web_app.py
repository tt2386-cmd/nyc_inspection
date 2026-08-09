from flask import Flask, render_template, request
from dotenv import load_dotenv
import pandas as pd
from sodapy import Socrata
import os

app = Flask(__name__)

load_dotenv()

# --------------------------------------------------
# CONNECT TO NYC OPENDATA
# --------------------------------------------------

client = Socrata(
    "data.cityofnewyork.us",
    os.getenv("SOCRATA_APP_TOKEN")
)

print("Loading NYC restaurant inspection data...")

results = client.get("43nn-pn8j", limit=50000)
df = pd.DataFrame.from_records(results)

# --------------------------------------------------
# CLEAN DATA
# --------------------------------------------------

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


# --------------------------------------------------
# HOME / SEARCH PAGE
# --------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():

    locations = []
    error = None
    restaurant_name = ""

    if request.method == "POST":

        restaurant_name = request.form.get(
            "restaurant_name",
            ""
        ).strip().upper()

        if not restaurant_name:

            error = "Please enter a restaurant name."

        else:

            matches = df[
                df["dba"].str.contains(
                    restaurant_name,
                    case=False,
                    na=False
                )
            ]

            if matches.empty:

                error = (
                    f"No restaurants found matching "
                    f"'{restaurant_name}'."
                )

            else:

                locations = (
                    matches[
                        ["dba", "address", "boro"]
                    ]
                    .drop_duplicates()
                    .sort_values("address")
                    .to_dict("records")
                )

    return render_template(
        "index.html",
        locations=locations,
        error=error,
        restaurant_name=restaurant_name
    )


# --------------------------------------------------
# RESTAURANT DETAILS PAGE
# --------------------------------------------------

@app.route("/restaurant")
def restaurant_details():

    address = request.args.get(
        "address",
        ""
    )

    boro = request.args.get(
        "boro",
        ""
    )

    restaurant = df[
        (df["address"] == address) &
        (df["boro"] == boro)
    ].copy()

    if restaurant.empty:

        return (
            "Restaurant location not found.",
            404
        )

    # Only inspections with scores
    scored_inspections = restaurant[
        restaurant["score"].notna()
    ].copy()

    if scored_inspections.empty:

        return (
            "No inspection score history found.",
            404
        )

    # Sort newest inspection first
    scored_inspections = scored_inspections.sort_values(
        "inspection_date",
        ascending=False
    )

    # Most recent inspection
    latest = scored_inspections.iloc[0]

    latest_date = latest["inspection_date"]
    latest_score = latest["score"]
    latest_grade = latest.get(
        "grade",
        ""
    )

    # All violations from the latest inspection
    latest_inspection_rows = restaurant[
        restaurant["inspection_date"] == latest_date
    ]

    violations = []

    for _, row in latest_inspection_rows.iterrows():

        violation_description = row.get(
            "violation_description",
            "No description recorded."
        )

        critical_flag = str(
            row.get(
                "critical_flag",
                ""
            )
        ).upper()

        is_critical = (
            "CRITICAL" in critical_flag
            and "NOT CRITICAL" not in critical_flag
        )

        violations.append({
            "description": violation_description,
            "critical": is_critical
        })

    # --------------------------------------------------
    # INSPECTION HISTORY
    # --------------------------------------------------

    history = scored_inspections.copy()

    history = history[
        history["inspection_date"].dt.year > 1900
    ]

    history = (
        history
        .groupby("inspection_date")["score"]
        .max()
        .reset_index()
        .sort_values("inspection_date")
    )

    # Convert history to records for Flask/Jinja
    history_records = []

    for _, row in history.iterrows():

        history_records.append({
            "date": row["inspection_date"].strftime(
                "%Y-%m-%d"
            ),
            "score": row["score"]
        })

    return render_template(
        "restaurant.html",
        restaurant_name=restaurant["dba"].iloc[0],
        selected_address=address,
        boro=boro,
        latest_date=latest_date,
        latest_score=latest_score,
        latest_grade=latest_grade,
        violations=violations,
        history=history_records
    )


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
