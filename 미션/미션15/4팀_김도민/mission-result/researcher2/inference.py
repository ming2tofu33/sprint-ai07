from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


PREDICTION_COLUMN = "Predicted Performance Index"


def run_inference(
    model_path: str | Path,
    test_path: str | Path,
    result_path: str | Path,
    prediction_column: str = PREDICTION_COLUMN,
) -> pd.DataFrame:
    model_path = Path(model_path)
    test_path = Path(test_path)
    result_path = Path(result_path)
    result_path.parent.mkdir(parents=True, exist_ok=True)

    model = joblib.load(model_path)
    test_df = pd.read_csv(test_path)
    predictions = model.predict(test_df)

    result_df = test_df.copy()
    result_df[prediction_column] = np.round(predictions, 4)
    result_df.to_csv(result_path, index=False)
    return result_df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run inference for the Mission 15 model.")
    parser.add_argument("--model-path", default="/shared/model.pkl")
    parser.add_argument("--test-path", default="/shared/test.csv")
    parser.add_argument("--result-path", default="/shared/result.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result_df = run_inference(
        model_path=args.model_path,
        test_path=args.test_path,
        result_path=args.result_path,
    )
    print(f"Saved {len(result_df)} predictions to {args.result_path}")


if __name__ == "__main__":
    main()
