from typing import Any

import requests


class MovieReviewAPI:
    def __init__(self, base_url: str, session: requests.Session | None = None, timeout: int = 5):
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        response = self.session.request(
            method,
            f"{self.base_url}{path}",
            timeout=self.timeout,
            json=json,
            params=params,
        )
        response.raise_for_status()
        return response.json()

    def health(self) -> dict[str, str]:
        return self._request("GET", "/health")

    def list_movies(self) -> list[dict[str, Any]]:
        return self._request("GET", "/movies")

    def create_movie(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/movies", json=payload)

    def delete_movie(self, movie_id: int) -> dict[str, Any]:
        return self._request("DELETE", f"/movies/{movie_id}")

    def list_movie_reviews(self, movie_id: int) -> list[dict[str, Any]]:
        return self._request("GET", f"/movies/{movie_id}/reviews")

    def create_review(self, movie_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", f"/movies/{movie_id}/reviews", json=payload)

    def list_reviews(self, movie_id: int | None = None, limit: int = 10) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"limit": limit}
        if movie_id is not None:
            params["movie_id"] = movie_id
        return self._request("GET", "/reviews", params=params)

    def delete_review(self, review_id: int) -> dict[str, Any]:
        return self._request("DELETE", f"/reviews/{review_id}")

    def get_rating(self, movie_id: int) -> dict[str, Any]:
        return self._request("GET", f"/movies/{movie_id}/rating")

    def analyze_sentiment(self, content: str) -> dict[str, Any]:
        return self._request("POST", "/sentiment/analyze", json={"content": content})


def format_score(score: float | None) -> str:
    if score is None:
        return "리뷰 없음"
    return f"{score * 100:.1f}점"


def sentiment_badge(label: str) -> str:
    labels = {
        "positive": "긍정",
        "negative": "부정",
        "neutral": "중립",
    }
    return labels.get(label, label)


def sentiment_class(label: str) -> str:
    classes = {
        "positive": "sentiment-positive",
        "negative": "sentiment-negative",
        "neutral": "sentiment-neutral",
    }
    return classes.get(label, "sentiment-neutral")
