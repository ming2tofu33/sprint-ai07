from __future__ import annotations

from pathlib import Path

import numpy as np
import onnxruntime as ort


def create_session(model_path: str | Path) -> ort.InferenceSession:
    return ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])


def probabilities_from_logits(logits: np.ndarray) -> np.ndarray:
    values = np.asarray(logits, dtype=np.float32).reshape(-1)
    shifted = values - values.max()
    exp = np.exp(shifted)
    return (exp / exp.sum()).astype(np.float32)


def top_prediction(probabilities: np.ndarray) -> tuple[int, float]:
    values = np.asarray(probabilities, dtype=np.float32).reshape(-1)
    label = int(values.argmax())
    return label, float(values[label])


def run_prediction(session: ort.InferenceSession, input_tensor: np.ndarray) -> np.ndarray:
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    outputs = session.run([output_name], {input_name: input_tensor.astype(np.float32)})
    return probabilities_from_logits(outputs[0])
