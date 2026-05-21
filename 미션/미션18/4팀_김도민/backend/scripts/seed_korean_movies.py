import sys
from pathlib import Path

from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.database import get_connection
from app.main import app


client = TestClient(app)


MOVIES = [
    {
        "title": "파묘",
        "release_date": "2024-02-22",
        "director": "장재현",
        "genre": "오컬트, 미스터리",
        "poster_url": "https://image.tmdb.org/t/p/w500/tw0i3kkmOTjDjGFZTLHKhoeXVvA.jpg",
        "reviews": [
            ("도민", "배우들의 연기가 좋고 긴장감이 끝까지 이어졌다."),
            ("서연", "오컬트 분위기가 뛰어나고 몰입감이 좋았다."),
            ("민준", "소재가 신선하고 장면마다 긴장감이 훌륭했다."),
            ("지우", "후반부 전개가 조금 아쉬웠지만 전체적으로 재미있었다."),
            ("하린", "캐릭터들이 매력적이고 연출이 강렬해서 만족스러웠다."),
            ("현우", "음향과 분위기가 좋고 극장에서 보기 좋은 영화였다."),
            ("유진", "이야기가 독특하고 배우들의 호흡이 뛰어났다."),
            ("준서", "중간에 살짝 지루한 부분이 있었지만 결말은 좋았다."),
            ("수아", "한국적인 소재를 잘 살려서 인상 깊고 추천하고 싶다."),
            ("태윤", "긴장감과 미스터리 요소가 잘 어울려서 재미있게 봤다."),
        ],
    },
    {
        "title": "서울의 봄",
        "release_date": "2023-11-22",
        "director": "김성수",
        "genre": "드라마, 역사",
        "poster_url": "https://image.tmdb.org/t/p/w500/ukVVnY9ovwl78WE5KndcpA6SnAm.jpg",
        "reviews": [
            ("도민", "배우들의 연기가 뛰어나고 몰입감이 정말 좋았다."),
            ("서연", "긴장감 있는 전개가 훌륭했고 메시지도 강했다."),
            ("민준", "역사적 사건을 힘 있게 보여줘서 인상 깊었다."),
            ("지우", "러닝타임이 길지만 지루하지 않고 집중해서 봤다."),
            ("하린", "연출과 연기가 모두 좋고 감정적으로도 강하게 남았다."),
            ("현우", "답답한 장면도 있었지만 영화적 완성도는 높았다."),
            ("유진", "배우들의 에너지가 좋아서 끝까지 몰입할 수 있었다."),
            ("준서", "무거운 소재지만 전개가 탄탄해서 추천하고 싶다."),
            ("수아", "긴장감과 분노가 잘 전달되어 기억에 남는 영화였다."),
            ("태윤", "전체적으로 훌륭했고 보고 나서 생각할 거리가 많았다."),
        ],
    },
    {
        "title": "기생충",
        "release_date": "2019-05-30",
        "director": "봉준호",
        "genre": "드라마, 스릴러",
        "poster_url": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
        "reviews": [
            ("도민", "연출이 훌륭하고 장면마다 의미가 살아 있어서 좋았다."),
            ("서연", "재미와 메시지를 모두 잡은 뛰어난 영화였다."),
            ("민준", "전개가 예측하기 어렵고 몰입감이 매우 좋았다."),
            ("지우", "블랙코미디와 스릴러가 자연스럽게 섞여 인상 깊었다."),
            ("하린", "배우들의 연기가 좋고 계급 문제를 강렬하게 보여줬다."),
            ("현우", "중반 이후 긴장감이 뛰어나고 결말도 오래 남았다."),
            ("유진", "상징이 많아서 다시 보고 싶은 훌륭한 작품이다."),
            ("준서", "재미있지만 불편한 감정도 남기는 힘 있는 영화였다."),
            ("수아", "완성도가 높고 추천할 만한 한국 영화라고 생각한다."),
            ("태윤", "연출, 각본, 연기가 모두 좋아서 만족스러웠다."),
        ],
    },
]


def get_or_create_movie(movie: dict) -> dict:
    response = client.get("/movies")
    response.raise_for_status()
    for existing in response.json():
        if existing["title"] == movie["title"]:
            with get_connection() as connection:
                connection.execute(
                    """
                    UPDATE movies
                    SET release_date = ?,
                        director = ?,
                        genre = ?,
                        poster_url = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        movie["release_date"],
                        movie["director"],
                        movie["genre"],
                        movie["poster_url"],
                        existing["id"],
                    ),
                )
            refreshed = client.get(f"/movies/{existing['id']}")
            refreshed.raise_for_status()
            return refreshed.json()

    payload = {key: movie[key] for key in ("title", "release_date", "director", "genre", "poster_url")}
    response = client.post("/movies", json=payload)
    response.raise_for_status()
    return response.json()


def seed_reviews(movie_id: int, reviews: list[tuple[str, str]]) -> int:
    response = client.get(f"/movies/{movie_id}/reviews")
    response.raise_for_status()
    existing_reviews = response.json()
    existing_contents = {review["content"] for review in existing_reviews}

    added_count = 0
    for author_name, content in reviews:
        if len(existing_reviews) + added_count >= 10:
            break
        if content in existing_contents:
            continue
        response = client.post(
            f"/movies/{movie_id}/reviews",
            json={"author_name": author_name, "content": content},
        )
        response.raise_for_status()
        added_count += 1

    return added_count


def main() -> None:
    for movie in MOVIES:
        created_movie = get_or_create_movie(movie)
        added_reviews = seed_reviews(created_movie["id"], movie["reviews"])
        rating = client.get(f"/movies/{created_movie['id']}/rating").json()
        print(
            f"{created_movie['title']}: movie_id={created_movie['id']}, "
            f"added_reviews={added_reviews}, total_reviews={rating['review_count']}, "
            f"average_sentiment_score={rating['average_sentiment_score']}"
        )


if __name__ == "__main__":
    main()
