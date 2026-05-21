import importlib
import sys

from fastapi.testclient import TestClient


def make_client(tmp_path, monkeypatch):
    monkeypatch.setenv("MISSION18_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("MISSION18_SENTIMENT_BACKEND", "rules")
    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            del sys.modules[module_name]
    main = importlib.import_module("app.main")
    return TestClient(main.app)


def test_movie_crud_flow(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    response = client.post(
        "/movies",
        json={
            "title": "파묘",
            "release_date": "2024-02-22",
            "director": "장재현",
            "genre": "오컬트, 미스터리",
            "poster_url": "https://example.com/exhuma.jpg",
        },
    )
    assert response.status_code == 201
    movie = response.json()
    assert movie["id"] == 1
    assert movie["title"] == "파묘"
    assert movie["review_count"] == 0
    assert movie["average_sentiment_score"] is None

    response = client.get("/movies")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get("/movies/1")
    assert response.status_code == 200
    assert response.json()["director"] == "장재현"

    response = client.delete("/movies/1")
    assert response.status_code == 200
    assert response.json()["deleted"] is True

    response = client.get("/movies")
    assert response.status_code == 200
    assert response.json() == []


def test_review_creation_runs_sentiment_and_updates_rating(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    movie = client.post(
        "/movies",
        json={
            "title": "서울의 봄",
            "release_date": "2023-11-22",
            "director": "김성수",
            "genre": "드라마",
            "poster_url": "https://example.com/12-12.jpg",
        },
    ).json()

    response = client.post(
        f"/movies/{movie['id']}/reviews",
        json={"author_name": "도민", "content": "배우들의 연기가 좋고 몰입감이 뛰어났다."},
    )
    assert response.status_code == 201
    review = response.json()
    assert review["movie_id"] == movie["id"]
    assert review["sentiment_label"] == "positive"
    assert 0.5 < review["sentiment_score"] <= 1.0

    response = client.get(f"/movies/{movie['id']}/reviews")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get(f"/movies/{movie['id']}/rating")
    assert response.status_code == 200
    rating = response.json()
    assert rating["review_count"] == 1
    assert rating["average_sentiment_score"] == review["sentiment_score"]


def test_movie_delete_cascades_reviews(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    movie = client.post(
        "/movies",
        json={
            "title": "괴물",
            "release_date": "2006-07-27",
            "director": "봉준호",
            "genre": "스릴러",
            "poster_url": "https://example.com/host.jpg",
        },
    ).json()
    client.post(
        f"/movies/{movie['id']}/reviews",
        json={"author_name": "tester", "content": "지루하고 아쉬운 부분이 많았다."},
    )

    response = client.delete(f"/movies/{movie['id']}")
    assert response.status_code == 200

    response = client.get("/reviews")
    assert response.status_code == 200
    assert response.json() == []
