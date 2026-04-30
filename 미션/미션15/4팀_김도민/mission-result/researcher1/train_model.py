from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


FEATURE_COLUMNS = [
    "Hours Studied",
    "Previous Scores",
    "Extracurricular Activities",
    "Sleep Hours",
    "Sample Question Papers Practiced",
]
TARGET_COLUMN = "Performance Index"
NUMERIC_FEATURES = [
    "Hours Studied",
    "Previous Scores",
    "Sleep Hours",
    "Sample Question Papers Practiced",
]
CATEGORICAL_FEATURES = ["Extracurricular Activities"]


def build_model_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", Ridge(alpha=1.0)),
        ]
    )


def validate_columns(data: pd.DataFrame, required_columns: list[str], source_name: str) -> None:
    missing_columns = [column for column in required_columns if column not in data.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"{source_name} is missing required columns: {missing}")


def calculate_rmse(y_true: pd.Series, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def train_and_save_model(
    train_path: str | Path,
    test_path: str | Path,
    output_dir: str | Path,
    random_state: int = 42,
    test_size: float = 0.2,
) -> dict[str, Any]:
    train_path = Path(train_path)
    test_path = Path(test_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    validate_columns(train_df, FEATURE_COLUMNS + [TARGET_COLUMN], str(train_path))
    validate_columns(test_df, FEATURE_COLUMNS, str(test_path))

    x_train, x_valid, y_train, y_valid = train_test_split(
        train_df[FEATURE_COLUMNS],
        train_df[TARGET_COLUMN],
        test_size=test_size,
        random_state=random_state,
    )

    validation_pipeline = build_model_pipeline()
    validation_pipeline.fit(x_train, y_train)
    validation_predictions = validation_pipeline.predict(x_valid)
    rmse = calculate_rmse(y_valid, validation_predictions)

    final_pipeline = build_model_pipeline()
    final_pipeline.fit(train_df[FEATURE_COLUMNS], train_df[TARGET_COLUMN])

    model_path = output_dir / "model.pkl"
    metrics_path = output_dir / "metrics.json"
    shared_test_path = output_dir / "test.csv"

    joblib.dump(final_pipeline, model_path)
    if test_path.resolve() != shared_test_path.resolve():
        shutil.copy2(test_path, shared_test_path)

    metrics = {
        "rmse": round(rmse, 4),
        "train_rows": int(len(train_df)),
        "validation_rows": int(len(x_valid)),
        "test_rows": int(len(test_df)),
        "model_path": str(model_path),
        "test_path": str(shared_test_path),
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "model": "Ridge(alpha=1.0)",
        "random_state": random_state,
    }
    metrics_path.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the Mission 15 student performance model.")
    parser.add_argument("--train-path", default="data/train.csv")
    parser.add_argument("--test-path", default="data/test.csv")
    parser.add_argument("--output-dir", default="/shared")
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metrics = train_and_save_model(
        train_path=args.train_path,
        test_path=args.test_path,
        output_dir=args.output_dir,
        random_state=args.random_state,
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
