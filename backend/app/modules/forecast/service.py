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


ROOT_PATH = Path(__file__).resolve().parents[4]

DATA_PATH = ROOT_PATH / "data" / "processed" / "ml_forecasting_dataset.csv"
MODEL_PATH = ROOT_PATH / "data" / "processed" / "best_forecasting_model.joblib"

RANDOM_STATE = 42

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


class ForecastService:

    def __init__(self):
        self.model_package = None
        self.model = None

    # ========================================================
    # MODEL LOADING
    # ========================================================

    def load_model(self):
        if self.model is None:

            if not MODEL_PATH.exists():
                raise FileNotFoundError(
                    f"Forecasting model not found: {MODEL_PATH}"
                )

            self.model_package = joblib.load(MODEL_PATH)
            self.model = self.model_package["model"]

        return self.model

    # ========================================================
    # PREDICTION
    # ========================================================

    def predict(
        self,
        crop: str,
        district_name: str,
        date: str,
        lag_1: float,
        lag_2: float,
        days_since_previous: int,
    ) -> float:

        model = self.load_model()

        prediction_date = pd.to_datetime(date)

        input_data = pd.DataFrame(
            [
                {
                    "crop": crop,
                    "district_name": district_name,
                    "month": prediction_date.month,
                    "day_of_week": prediction_date.dayofweek,
                    "day_of_year": prediction_date.dayofyear,
                    "days_since_previous": days_since_previous,
                    "lag_1": lag_1,
                    "lag_2": lag_2,
                }
            ]
        )

        prediction = model.predict(input_data)[0]

        return max(0.0, float(prediction))

    # ========================================================
    # TRAINING
    # ========================================================

    def train(self):

        if not DATA_PATH.exists():
            raise FileNotFoundError(
                f"Training dataset not found: {DATA_PATH}"
            )

        df = pd.read_csv(DATA_PATH)

        df["date"] = pd.to_datetime(df["date"])

        df = df.sort_values(
            ["crop", "date", "district_name"]
        ).reset_index(drop=True)

        df_2024 = df[df["date"].dt.year == 2024].copy()
        df_2025 = df[df["date"].dt.year == 2025].copy()

        if df_2024.empty:
            raise ValueError("No 2024 training data found.")

        if df_2025.empty:
            raise ValueError("No 2025 test data found.")

        # ----------------------------------------------------
        # Chronological validation split
        # ----------------------------------------------------

        train_parts = []
        validation_parts = []

        for crop in sorted(df_2024["crop"].unique()):

            crop_data = (
                df_2024[df_2024["crop"] == crop]
                .sort_values("date")
                .reset_index(drop=True)
            )

            split_index = int(len(crop_data) * 0.80)

            train_parts.append(
                crop_data.iloc[:split_index].copy()
            )

            validation_parts.append(
                crop_data.iloc[split_index:].copy()
            )

        train_df = pd.concat(
            train_parts,
            ignore_index=True,
        )

        validation_df = pd.concat(
            validation_parts,
            ignore_index=True,
        )

        X_train = train_df[FEATURES]
        y_train = train_df[TARGET]

        X_validation = validation_df[FEATURES]
        y_validation = validation_df[TARGET]

        X_test = df_2025[FEATURES]
        y_test = df_2025[TARGET]

        # ----------------------------------------------------
        # Preprocessor
        # ----------------------------------------------------

        categorical_pipeline = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(
                        strategy="most_frequent"
                    ),
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
                    SimpleImputer(
                        strategy="median"
                    ),
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

        # ----------------------------------------------------
        # Candidate models
        # ----------------------------------------------------

        models = {
            "Ridge": Ridge(alpha=10.0),

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

        # ----------------------------------------------------
        # Naive baseline
        # ----------------------------------------------------

        naive_prediction = validation_df["lag_1"].values

        naive_mae = mean_absolute_error(
            y_validation,
            naive_prediction,
        )

        naive_rmse = np.sqrt(
            mean_squared_error(
                y_validation,
                naive_prediction,
            )
        )

        validation_results = {
            "Naive Baseline": {
                "MAE": naive_mae,
                "RMSE": naive_rmse,
                "pipeline": None,
            }
        }

        # ----------------------------------------------------
        # Train candidate models
        # ----------------------------------------------------

        for name, model in models.items():

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

            mae = mean_absolute_error(
                y_validation,
                predictions,
            )

            rmse = np.sqrt(
                mean_squared_error(
                    y_validation,
                    predictions,
                )
            )

            validation_results[name] = {
                "MAE": mae,
                "RMSE": rmse,
                "pipeline": pipeline,
            }

        # ----------------------------------------------------
        # Select best strategy
        # ----------------------------------------------------

        best_name = min(
            validation_results,
            key=lambda name: (
                validation_results[name]["MAE"],
                validation_results[name]["RMSE"],
            ),
        )

        best_validation_mae = validation_results[
            best_name
        ]["MAE"]

        best_validation_rmse = validation_results[
            best_name
        ]["RMSE"]

        # ----------------------------------------------------
        # Retrain selected ML model on all 2024 data
        # ----------------------------------------------------

        if best_name == "Naive Baseline":

            final_test_prediction = df_2025[
                "lag_1"
            ].values

            final_pipeline = None

        else:

            final_pipeline = Pipeline(
                steps=[
                    (
                        "preprocessor",
                        preprocessor,
                    ),
                    (
                        "model",
                        models[best_name],
                    ),
                ]
            )

            final_pipeline.fit(
                df_2024[FEATURES],
                df_2024[TARGET],
            )

            final_test_prediction = final_pipeline.predict(
                X_test
            )

        # ----------------------------------------------------
        # Final test metrics
        # ----------------------------------------------------

        test_mae = mean_absolute_error(
            y_test,
            final_test_prediction,
        )

        test_rmse = np.sqrt(
            mean_squared_error(
                y_test,
                final_test_prediction,
            )
        )

        # ----------------------------------------------------
        # Save model
        # ----------------------------------------------------

        if final_pipeline is not None:

            model_package = {
                "model": final_pipeline,
                "model_name": best_name,
                "features": FEATURES,
                "categorical_features": CATEGORICAL_FEATURES,
                "numerical_features": NUMERICAL_FEATURES,
                "target": TARGET,
                "validation_mae": best_validation_mae,
                "validation_rmse": best_validation_rmse,
                "test_mae": test_mae,
                "test_rmse": test_rmse,
                "random_state": RANDOM_STATE,
                "training_period": "2024",
                "test_period": "2025",
                "forecasting_note": (
                    "Target quantity represents market "
                    "activity/arrival proxy rather than "
                    "direct consumer demand."
                ),
            }

            MODEL_PATH.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            joblib.dump(
                model_package,
                MODEL_PATH,
            )

            # Refresh in-memory model
            self.model_package = model_package
            self.model = final_pipeline

        return {
            "model_name": best_name,
            "validation_mae": float(best_validation_mae),
            "validation_rmse": float(best_validation_rmse),
            "test_mae": float(test_mae),
            "test_rmse": float(test_rmse),
            "training_period": "2024",
            "test_period": "2025",
        }


forecast_service = ForecastService()