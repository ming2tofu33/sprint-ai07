from api_client import MovieReviewAPI, format_score, sentiment_badge


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.text)


class FakeSession:
    def __init__(self):
        self.calls = []

    def request(self, method, url, timeout, json=None, params=None):
        self.calls.append(
            {
                "method": method,
                "url": url,
                "timeout": timeout,
                "json": json,
                "params": params,
            }
        )
        return FakeResponse({"ok": True})


def test_client_normalizes_base_url_and_sends_json_payload():
    session = FakeSession()
    api = MovieReviewAPI("http://localhost:8000///", session=session)

    result = api.create_movie(
        {
            "title": "파묘",
            "release_date": "2024-02-22",
            "director": "장재현",
            "genre": "오컬트",
            "poster_url": "https://example.com/poster.jpg",
        }
    )

    assert result == {"ok": True}
    assert session.calls == [
        {
            "method": "POST",
            "url": "http://localhost:8000/movies",
            "timeout": 5,
            "json": {
                "title": "파묘",
                "release_date": "2024-02-22",
                "director": "장재현",
                "genre": "오컬트",
                "poster_url": "https://example.com/poster.jpg",
            },
            "params": None,
        }
    ]


def test_list_reviews_can_filter_by_movie_and_limit():
    session = FakeSession()
    api = MovieReviewAPI("http://localhost:8000", session=session)

    api.list_reviews(movie_id=3, limit=20)

    assert session.calls[0]["method"] == "GET"
    assert session.calls[0]["url"] == "http://localhost:8000/reviews"
    assert session.calls[0]["params"] == {"movie_id": 3, "limit": 20}


def test_score_and_sentiment_formatting():
    assert format_score(None) == "리뷰 없음"
    assert format_score(0.815) == "81.5점"
    assert sentiment_badge("positive") == "긍정"
    assert sentiment_badge("negative") == "부정"
    assert sentiment_badge("neutral") == "중립"
