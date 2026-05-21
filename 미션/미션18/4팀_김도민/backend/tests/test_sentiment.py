from app.sentiment import map_huggingface_output


def test_maps_positive_huggingface_label_to_project_schema():
    result = map_huggingface_output({"label": "LABEL_1", "score": 0.93})

    assert result.sentiment_label == "positive"
    assert result.sentiment_score == 0.93
    assert result.confidence == 0.93


def test_maps_negative_huggingface_label_to_low_sentiment_score():
    result = map_huggingface_output({"label": "LABEL_0", "score": 0.88})

    assert result.sentiment_label == "negative"
    assert result.sentiment_score == 0.12
    assert result.confidence == 0.88


def test_maps_unknown_huggingface_label_to_neutral():
    result = map_huggingface_output({"label": "NEUTRAL", "score": 0.72})

    assert result.sentiment_label == "neutral"
    assert result.sentiment_score == 0.5
    assert result.confidence == 0.72
