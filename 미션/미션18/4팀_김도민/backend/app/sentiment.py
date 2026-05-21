import os
from functools import lru_cache
from typing import Any

from app.schemas import SentimentResult


DEFAULT_MODEL_NAME = "cringepnh/koelectra-korean-sentiment"
POSITIVE_KEYWORDS = (
    "좋",
    "재미",
    "뛰어",
    "훌륭",
    "몰입",
    "감동",
    "최고",
    "추천",
    "만족",
)
NEGATIVE_KEYWORDS = (
    "아쉬",
    "지루",
    "별로",
    "실망",
    "나쁘",
    "최악",
    "부족",
    "답답",
)


def get_model_name() -> str:
    return os.getenv("MISSION18_HF_MODEL", DEFAULT_MODEL_NAME)


@lru_cache(maxsize=1)
def get_huggingface_pipeline():
    from transformers import pipeline

    model_name = get_model_name()
    return pipeline("text-classification", model=model_name, tokenizer=model_name, device=-1)


def map_huggingface_output(output: dict[str, Any] | list[dict[str, Any]]) -> SentimentResult:
    if isinstance(output, list):
        if not output:
            return SentimentResult(sentiment_label="neutral", sentiment_score=0.5, confidence=0.0)
        output = output[0]

    raw_label = str(output.get("label", "")).upper()
    confidence = round(float(output.get("score", 0.0)), 4)

    if raw_label in {"LABEL_1", "1", "POSITIVE", "POS", "긍정"}:
        return SentimentResult(
            sentiment_label="positive",
            sentiment_score=confidence,
            confidence=confidence,
        )
    if raw_label in {"LABEL_0", "0", "NEGATIVE", "NEG", "부정"}:
        return SentimentResult(
            sentiment_label="negative",
            sentiment_score=round(1 - confidence, 4),
            confidence=confidence,
        )
    return SentimentResult(sentiment_label="neutral", sentiment_score=0.5, confidence=confidence)


def analyze_with_huggingface(content: str) -> SentimentResult:
    classifier = get_huggingface_pipeline()
    output = classifier(content, truncation=True, max_length=128)
    return map_huggingface_output(output)


def analyze_with_rules(content: str) -> SentimentResult:
    positive_hits = sum(keyword in content for keyword in POSITIVE_KEYWORDS)
    negative_hits = sum(keyword in content for keyword in NEGATIVE_KEYWORDS)

    if positive_hits > negative_hits:
        return SentimentResult(sentiment_label="positive", sentiment_score=0.85, confidence=0.8)
    if negative_hits > positive_hits:
        return SentimentResult(sentiment_label="negative", sentiment_score=0.2, confidence=0.8)
    return SentimentResult(sentiment_label="neutral", sentiment_score=0.5, confidence=0.5)


def analyze_sentiment(content: str) -> SentimentResult:
    backend = os.getenv("MISSION18_SENTIMENT_BACKEND", "huggingface").lower()
    if backend in {"rule", "rules", "keyword", "keywords"}:
        return analyze_with_rules(content)

    try:
        return analyze_with_huggingface(content)
    except Exception:
        if os.getenv("MISSION18_SENTIMENT_FALLBACK", "rules").lower() in {"rule", "rules"}:
            return analyze_with_rules(content)
        raise
