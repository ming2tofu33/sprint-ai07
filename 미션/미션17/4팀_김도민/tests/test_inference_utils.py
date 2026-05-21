import numpy as np

from inference_utils import probabilities_from_logits, top_prediction


def test_probabilities_from_logits_returns_normalized_probabilities():
    logits = np.array([[0.0, 1.0, 8.0, 0.5, -1.0, 0.0, 0.2, 0.1, -0.4, 0.3]], dtype=np.float32)

    probabilities = probabilities_from_logits(logits)

    assert probabilities.shape == (10,)
    assert np.isclose(probabilities.sum(), 1.0)
    assert probabilities.argmax() == 2


def test_top_prediction_returns_label_and_confidence():
    probabilities = np.array([0.01, 0.03, 0.04, 0.70, 0.02, 0.01, 0.01, 0.05, 0.08, 0.05], dtype=np.float32)

    label, confidence = top_prediction(probabilities)

    assert label == 3
    assert confidence == probabilities[3]
