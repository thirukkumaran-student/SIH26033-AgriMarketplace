from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw/quantities")
OUTPUT_FILE = Path("data/processed/forecasting_dataset.csv")

FILES = {
    "paddy": [
        "quantity_paddy_2024.csv",
        "quantity_paddy_2025.csv",
    ],
    "tomato": [
        "quantity_tomato_2024.csv",
        "quantity_tomato_2025.csv",
    ],
    "onion": [
        "quantity_onion_2024.csv",
        "quantity_onion_2025.csv",
    ],
}


def load_file(path, crop):
    df = pd.read_csv(path)

    df.columns = df.columns.str.strip().str.lower()

    required = {
        "t",
        "cmdty",
        "state_id",
        "state",
        "market_id",
        "market_name",
        "state_name",
        "district_id",
        "district_name",
        "qty",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"{path.name} is missing columns: {sorted(missing)}"
        )

    df["date"] = pd.to_datetime(df["t"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["qty"], errors="coerce")

    df["crop"] = crop

    return df[
        [
            "date",
            "crop",
            "state_id",
            "state",
            "market_id",
            "market_name",
            "state_name",
            "district_id",
            "district_name",
            "quantity",
        ]
    ]


def main():
    frames = []

    for crop, filenames in FILES.items():
        for filename in filenames:
            path = RAW_DIR / filename

            if not path.exists():
                raise FileNotFoundError(
                    f"Missing file: {path}"
                )

            print(f"Loading {path}...")

            df = load_file(path, crop)

            print(f"  Rows: {len(df):,}")

            frames.append(df)

    data = pd.concat(
        frames,
        ignore_index=True
    )

    # Keep valid observations
    data = data.dropna(
        subset=[
            "date",
            "crop",
            "district_id",
            "quantity",
        ]
    )

    data = data[data["quantity"] >= 0]

    # Keep only Tamil Nadu
    data = data[
        (data["state_id"] == 33)
        | (data["state"].str.lower() == "tamil nadu")
        | (data["state_name"].str.lower() == "tamil nadu")
    ]

    # Keep only our three crops
    data = data[
        data["crop"].isin(
            ["paddy", "tomato", "onion"]
        )
    ]

    # Sort chronologically
    data = data.sort_values(
        [
            "crop",
            "district_name",
            "market_name",
            "date",
        ]
    ).reset_index(drop=True)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    data.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n========================================")
    print("Forecasting dataset created")
    print("========================================")

    print(f"Rows: {len(data):,}")
    print(f"Output: {OUTPUT_FILE}")

    print("\nRows by crop:")
    print(
        data.groupby("crop")
        .size()
        .sort_values(ascending=False)
    )

    print("\nRows by year:")
    print(
        data.assign(
            year=data["date"].dt.year
        )
        .groupby(["crop", "year"])
        .size()
        .unstack(fill_value=0)
        .to_string()
    )

    print("\nDate range:")
    print(
        data.groupby("crop")["date"]
        .agg(["min", "max"])
        .to_string()
    )

    print("\nDistrict coverage:")
    print(
        data.groupby("crop")["district_name"]
        .nunique()
        .sort_values(ascending=False)
    )


if __name__ == "__main__":
    main()