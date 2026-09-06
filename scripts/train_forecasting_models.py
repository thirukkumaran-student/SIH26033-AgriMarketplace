from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ============================================================
# CONFIG
# ============================================================

DATA_PATH = Path("data/processed/ml_forecasting_dataset.csv")
MODEL_PATH = Path("data/processed/best_forecasting_model.joblib")

RANDOM_STATE = 42


# ============================================================
# FEATURES
# ============================================================

TARGET = "quantity"

CATEGORICAL_FEATURES = [
    "crop",
    "district_name",
]

NUMERICAL_FEATURES = [
    "month",
    "day_of_week",
    "day_of_year",
    "days_since_previous",
    "lag_1",
    "lag_2",
]

FEATURES = CATEGORICAL_FEATURES + NUMERICAL_FEATURES


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))

    return {
        "MAE": mae,
        "RMSE": rmse,
    }


def print_metrics(name, y_true, y_pred):
    metrics = calculate_metrics(y_true, y_pred)

    print(
        f"{name:<25} "
        f"MAE: {metrics['MAE']:>10.4f}   "
        f"RMSE: {metrics['RMSE']:>10.4f}"
    )

    return metrics


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("LOADING DATA")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(
    ["crop", "date", "district_name"]
).reset_index(drop=True)

print(f"Total rows: {len(df)}")
print(f"Crops: {df['crop'].unique().tolist()}")
print(
    f"Date range: "
    f"{df['date'].min().date()} -> {df['date'].max().date()}"
)


# ============================================================
# 2024 / 2025 SPLIT
# ============================================================

df_2024 = df[df["date"].dt.year == 2024].copy()
df_2025 = df[df["date"].dt.year == 2025].copy()

print("\n2024 rows:", len(df_2024))
print("2025 rows:", len(df_2025))


# ============================================================
# CHRONOLOGICAL VALIDATION SPLIT
#
# For EACH crop:
#
#     earliest 80% -> training
#     latest 20%   -> validation
#
# 2025 remains completely untouched.
# ============================================================

print("\n" + "=" * 70)
print("CREATING CHRONOLOGICAL VALIDATION SPLIT")
print("=" * 70)

train_parts = []
validation_parts = []

for crop in sorted(df_2024["crop"].unique()):

    crop_data = (
        df_2024[df_2024["crop"] == crop]
        .sort_values("date")
        .reset_index(drop=True)
    )

    split_index = int(len(crop_data) * 0.80)

    train_crop = crop_data.iloc[:split_index].copy()
    validation_crop = crop_data.iloc[split_index:].copy()

    train_parts.append(train_crop)
    validation_parts.append(validation_crop)

    print(
        f"{crop:<10} "
        f"total={len(crop_data):<5} "
        f"train={len(train_crop):<5} "
        f"validation={len(validation_crop):<5}"
    )

train_df = pd.concat(train_parts, ignore_index=True)
validation_df = pd.concat(validation_parts, ignore_index=True)

print("\nTrain rows:", len(train_df))
print("Validation rows:", len(validation_df))
print("Test rows:", len(df_2025))


# ============================================================
# DISPLAY SPLIT DATES
# ============================================================

print("\nValidation boundaries:")

for crop in sorted(df_2024["crop"].unique()):

    crop_train = train_df[train_df["crop"] == crop]
    crop_validation = validation_df[
        validation_df["crop"] == crop
    ]

    print(
        f"{crop:<10} "
        f"train: {crop_train['date'].min().date()} "
        f"-> {crop_train['date'].max().date()} | "
        f"validation: {crop_validation['date'].min().date()} "
        f"-> {crop_validation['date'].max().date()}"
    )


# ============================================================
# PREPARE X / y
# ============================================================

X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_validation = validation_df[FEATURES]
y_validation = validation_df[TARGET]

X_test = df_2025[FEATURES]
y_test = df_2025[TARGET]


# ============================================================
# PREPROCESSOR
# ============================================================

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent"),
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False,
            ),
        ),
    ]
)

numerical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median"),
        ),
        (
            "scaler",
            StandardScaler(),
        ),
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            categorical_pipeline,
            CATEGORICAL_FEATURES,
        ),
        (
            "numerical",
            numerical_pipeline,
            NUMERICAL_FEATURES,
        ),
    ]
)


# ============================================================
# MODELS
# ============================================================

models = {
    "Ridge": Ridge(
        alpha=10.0
    ),

    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=3,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=2,
        min_samples_leaf=5,
        random_state=RANDOM_STATE,
    ),

    "Hist Gradient Boosting": HistGradientBoostingRegressor(
        max_iter=100,
        learning_rate=0.05,
        max_leaf_nodes=15,
        min_samples_leaf=10,
        l2_regularization=1.0,
        random_state=RANDOM_STATE,
    ),
}


# ============================================================
# NAIVE BASELINE
# ============================================================

print("\n" + "=" * 70)
print("VALIDATION RESULTS")
print("=" * 70)

print("\nNaive baseline:")
print("Prediction = lag_1")

naive_validation_pred = validation_df["lag_1"].values

naive_validation_metrics = print_metrics(
    "Naive Baseline",
    y_validation,
    naive_validation_pred,
)


# ============================================================
# TRAIN + VALIDATE ML MODELS
# ============================================================

validation_results = {}

for name, model in models.items():

    print(f"\nTraining {name}...")

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    pipeline.fit(
        X_train,
        y_train,
    )

    predictions = pipeline.predict(
        X_validation
    )

    metrics = print_metrics(
        name,
        y_validation,
        predictions,
    )

    validation_results[name] = {
        "pipeline": pipeline,
        "MAE": metrics["MAE"],
        "RMSE": metrics["RMSE"],
    }


# ============================================================
# SELECT BEST MODEL
#
# MAE is the primary metric because it directly represents
# average absolute forecasting error.
# ============================================================

print("\n" + "=" * 70)
print("MODEL SELECTION")
print("=" * 70)

all_validation_results = {
    "Naive Baseline": {
        "MAE": naive_validation_metrics["MAE"],
        "RMSE": naive_validation_metrics["RMSE"],
        "pipeline": None,
    }
}

all_validation_results.update(validation_results)

best_name = min(
    all_validation_results,
    key=lambda name: (
        all_validation_results[name]["MAE"],
        all_validation_results[name]["RMSE"],
    ),
)

best_validation_mae = all_validation_results[best_name]["MAE"]
best_validation_rmse = all_validation_results[best_name]["RMSE"]

print(f"\nBest validation strategy: {best_name}")
print(f"Validation MAE:  {best_validation_mae:.4f}")
print(f"Validation RMSE: {best_validation_rmse:.4f}")


# ============================================================
# RETRAIN BEST ML MODEL ON ALL 2024 DATA
#
# If the Naive baseline wins, there is no ML pipeline to
# retrain. We still evaluate the baseline on 2025.
# ============================================================

print("\n" + "=" * 70)
print("FINAL 2025 TEST")
print("=" * 70)

if best_name == "Naive Baseline":

    print(
        "\nNaive baseline selected. "
        "No ML retraining required."
    )

    final_test_pred = df_2025["lag_1"].values

else:

    print(
        f"\nRetraining {best_name} on ALL 2024 observations..."
    )

    X_full_train = df_2024[FEATURES]
    y_full_train = df_2024[TARGET]

    best_model = models[best_name]

    final_pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "model",
                best_model,
            ),
        ]
    )

    final_pipeline.fit(
        X_full_train,
        y_full_train,
    )

    final_test_pred = final_pipeline.predict(
        X_test
    )


# ============================================================
# OVERALL TEST METRICS
# ============================================================

overall_test_metrics = print_metrics(
    f"{best_name} - 2025",
    y_test,
    final_test_pred,
)


# ============================================================
# TEST BY CROP
# ============================================================

print("\n" + "-" * 70)
print("2025 TEST RESULTS BY CROP")
print("-" * 70)

test_results_by_crop = {}

for crop in sorted(df_2025["crop"].unique()):

    mask = df_2025["crop"] == crop

    crop_true = y_test[mask]
    crop_pred = final_test_pred[mask]

    metrics = calculate_metrics(
        crop_true,
        crop_pred,
    )

    test_results_by_crop[crop] = metrics

    print(
        f"{crop:<10} "
        f"MAE: {metrics['MAE']:>10.4f}   "
        f"RMSE: {metrics['RMSE']:>10.4f}   "
        f"Rows: {mask.sum()}"
    )


# ============================================================
# ALSO CALCULATE 2025 NAIVE BASELINE
#
# This gives us a direct comparison against the simplest
# forecasting strategy on the untouched test period.
# ============================================================

naive_test_pred = df_2025["lag_1"].values

naive_test_metrics = calculate_metrics(
    y_test,
    naive_test_pred,
)

print("\n" + "-" * 70)
print("2025 NAIVE BASELINE")
print("-" * 70)

print(
    f"Naive MAE:  {naive_test_metrics['MAE']:.4f}"
)

print(
    f"Naive RMSE: {naive_test_metrics['RMSE']:.4f}"
)


# ============================================================
# SAVE MODEL
# ============================================================

if best_name != "Naive Baseline":

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_package = {
        "model": final_pipeline,
        "model_name": best_name,
        "features": FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "numerical_features": NUMERICAL_FEATURES,
        "target": TARGET,
        "validation_mae": best_validation_mae,
        "validation_rmse": best_validation_rmse,
        "test_mae": overall_test_metrics["MAE"],
        "test_rmse": overall_test_metrics["RMSE"],
        "random_state": RANDOM_STATE,
        "training_period": "2024",
        "test_period": "2025",
        "forecasting_note": (
            "Target quantity represents market activity/"
            "arrival proxy rather than direct consumer demand."
        ),
    }

    joblib.dump(
        model_package,
        MODEL_PATH,
    )

    print("\n" + "=" * 70)
    print("MODEL SAVED")
    print("=" * 70)

    print(f"Path: {MODEL_PATH}")

else:

    print("\n" + "=" * 70)
    print("MODEL NOT SAVED")
    print("=" * 70)

    print(
        "Naive baseline won validation. "
        "No trained ML model was saved."
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

print(f"Selected strategy : {best_name}")
print(f"Validation MAE    : {best_validation_mae:.4f}")
print(f"Validation RMSE   : {best_validation_rmse:.4f}")
print(
    f"2025 Test MAE     : "
    f"{overall_test_metrics['MAE']:.4f}"
)
print(
    f"2025 Test RMSE    : "
    f"{overall_test_metrics['RMSE']:.4f}"
)

print("\nExperiment completed successfully.")