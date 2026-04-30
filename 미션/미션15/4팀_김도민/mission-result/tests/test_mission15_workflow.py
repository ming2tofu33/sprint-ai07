from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "researcher1"))
sys.path.insert(0, str(ROOT / "researcher2"))


def make_training_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Hours Studied": [1, 2, 4, 6, 8, 9],
            "Previous Scores": [55, 60, 70, 78, 88, 95],
            "Extracurricular Activities": ["No", "Yes", "No", "Yes", "No", "Yes"],
            "Sleep Hours": [6, 7, 8, 6, 7, 8],
            "Sample Question Papers Practiced": [1, 2, 4, 5, 7, 9],
            "Performance Index": [35.0, 42.0, 55.0, 66.0, 79.0, 90.0],
        }
    )


def make_test_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Hours Studied": [3, 7],
            "Previous Scores": [65, 84],
            "Extracurricular Activities": ["Yes", "No"],
            "Sleep Hours": [7, 6],
            "Sample Question Papers Practiced": [3, 6],
        }
    )


def test_pipeline_accepts_raw_student_columns_and_predicts_finite_values():
    from train_model import FEATURE_COLUMNS, TARGET_COLUMN, build_model_pipeline

    train_df = make_training_frame()
    pipeline = build_model_pipeline()
    pipeline.fit(train_df[FEATURE_COLUMNS], train_df[TARGET_COLUMN])

    predictions = pipeline.predict(make_test_frame())

    assert predictions.shape == (2,)
    assert np.isfinite(predictions).all()


def test_train_and_save_model_writes_artifacts_to_output_directory(tmp_path):
    from train_model import train_and_save_model

    train_path = tmp_path / "train.csv"
    test_path = tmp_path / "test.csv"
    output_dir = tmp_path / "shared"
    make_training_frame().to_csv(train_path, index=False)
    make_test_frame().to_csv(test_path, index=False)

    metrics = train_and_save_model(
        train_path=train_path,
        test_path=test_path,
        output_dir=output_dir,
        random_state=42,
    )

    assert (output_dir / "model.pkl").exists()
    assert (output_dir / "test.csv").exists()
    assert (output_dir / "metrics.json").exists()
    assert metrics["rmse"] >= 0
    assert metrics["validation_rows"] > 0


def test_run_inference_writes_result_csv_with_one_prediction_per_test_row(tmp_path):
    from train_model import train_and_save_model
    from inference import run_inference

    train_path = tmp_path / "train.csv"
    test_path = tmp_path / "test.csv"
    shared_dir = tmp_path / "shared"
    result_path = tmp_path / "result.csv"
    make_training_frame().to_csv(train_path, index=False)
    make_test_frame().to_csv(test_path, index=False)
    train_and_save_model(train_path=train_path, test_path=test_path, output_dir=shared_dir)

    result_df = run_inference(
        model_path=shared_dir / "model.pkl",
        test_path=shared_dir / "test.csv",
        result_path=result_path,
    )

    assert result_path.exists()
    assert len(result_df) == len(make_test_frame())
    assert "Predicted Performance Index" in result_df.columns
    assert np.isfinite(result_df["Predicted Performance Index"]).all()
