from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/processed/forecasting_dataset.csv")
OUTPUT_FILE = Path("data/processed/ml_forecasting_dataset.csv")

CROPS = ["paddy", "tomato", "onion"]


def main():
    # --------------------------------
    # 1. Load
    # --------------------------------

    df = pd.read_csv(INPUT_FILE)

    df.columns = df.columns.str.strip().str.lower()

    # --------------------------------
    # 2. Clean
    # --------------------------------

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "date",
            "crop",
            "district_id",
            "quantity",
        ]
    )

    df = df[df["quantity"] >= 0]

    df = df[df["crop"].isin(CROPS)]

    # --------------------------------
    # 3. Aggregate markets
    #    crop + district + date
    # --------------------------------

    daily = (
        df.groupby(
            [
                "date",
                "crop",
                "district_id",
                "district_name",
            ],
            as_index=False,
        )["quantity"]
        .sum()
    )

    # --------------------------------
    # 4. Sort chronologically
    # --------------------------------

    daily = daily.sort_values(
        [
            "crop",
            "district_id",
            "date",
        ]
    ).reset_index(drop=True)

    groups = [
        "crop",
        "district_id",
    ]

    # --------------------------------
    # 5. Calendar features
    # --------------------------------

    daily["month"] = daily["date"].dt.month
    daily["day_of_week"] = daily["date"].dt.dayofweek
    daily["day_of_year"] = daily["date"].dt.dayofyear

    # --------------------------------
    # 6. Historical quantity features
    # --------------------------------

    # Previous observed quantity
    daily["lag_1"] = (
        daily.groupby(groups)["quantity"]
        .shift(1)
    )

    # Quantity two observations back
    daily["lag_2"] = (
        daily.groupby(groups)["quantity"]
        .shift(2)
    )

    # --------------------------------
    # 7. Time gap
    # --------------------------------

    previous_date = (
        daily.groupby(groups)["date"]
        .shift(1)
    )

    daily["days_since_previous"] = (
        daily["date"] - previous_date
    ).dt.days

    # --------------------------------
    # 8. Remove rows without history
    # --------------------------------

    daily = daily.dropna(
        subset=[
            "lag_1",
            "lag_2",
            "days_since_previous",
        ]
    )

    # --------------------------------
    # 9. Keep ML columns
    # --------------------------------

    result = daily[
        [
            "date",
            "crop",
            "district_id",
            "district_name",
            "month",
            "day_of_week",
            "day_of_year",
            "days_since_previous",
            "lag_1",
            "lag_2",
            "quantity",
        ]
    ].copy()

    # --------------------------------
    # 10. Save
    # --------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------
    # 11. Diagnostics
    # --------------------------------

    print("\n========================================")
    print("ML forecasting dataset created")
    print("========================================")

    print(f"Rows: {len(result):,}")
    print(f"Output: {OUTPUT_FILE}")

    print("\nRows by crop:")
    print(
        result.groupby("crop")
        .size()
        .sort_values(ascending=False)
        .to_string()
    )

    print("\nRows by year:")
    print(
        result.assign(
            year=result["date"].dt.year
        )
        .groupby(["crop", "year"])
        .size()
        .unstack(fill_value=0)
        .to_string()
    )

    print("\nDate range:")
    print(
        result.groupby("crop")["date"]
        .agg(["min", "max"])
        .to_string()
    )

    print("\nRows by crop and district:")
    print(
        result.groupby(
            ["crop", "district_name"]
        )
        .size()
        .to_string()
    )


if __name__ == "__main__":
    main()