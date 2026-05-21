from fastapi import FastAPI, HTTPException, Query, status

from app.database import get_connection, init_db
from app.schemas import (
    MovieCreate,
    MovieRead,
    RatingRead,
    ReviewCreate,
    ReviewRead,
    SentimentRequest,
    SentimentResult,
)
from app.sentiment import analyze_sentiment


app = FastAPI(
    title="Mission 18 Movie Review Sentiment API",
    description="영화 정보, 사용자 리뷰, 리뷰 감성 분석 결과를 관리하는 FastAPI 백엔드입니다.",
    version="0.1.0",
)
init_db()


def movie_from_row(row) -> MovieRead:
    return MovieRead(
        id=row["id"],
        title=row["title"],
        release_date=row["release_date"],
        director=row["director"],
        genre=row["genre"],
        poster_url=row["poster_url"],
        review_count=row["review_count"],
        average_sentiment_score=row["average_sentiment_score"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def review_from_row(row) -> ReviewRead:
    return ReviewRead(
        id=row["id"],
        movie_id=row["movie_id"],
        author_name=row["author_name"],
        content=row["content"],
        sentiment_label=row["sentiment_label"],
        sentiment_score=row["sentiment_score"],
        sentiment_confidence=row["sentiment_confidence"],
        created_at=row["created_at"],
    )


def fetch_movie(movie_id: int) -> MovieRead | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                m.*,
                COUNT(r.id) AS review_count,
                AVG(r.sentiment_score) AS average_sentiment_score
            FROM movies AS m
            LEFT JOIN reviews AS r ON r.movie_id = m.id
            WHERE m.id = ?
            GROUP BY m.id
            """,
            (movie_id,),
        ).fetchone()
    return movie_from_row(row) if row else None


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/movies", response_model=MovieRead, status_code=status.HTTP_201_CREATED)
def create_movie(payload: MovieCreate) -> MovieRead:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO movies (title, release_date, director, genre, poster_url)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload.title,
                payload.release_date,
                payload.director,
                payload.genre,
                payload.poster_url,
            ),
        )
        movie_id = cursor.lastrowid
    movie = fetch_movie(movie_id)
    if movie is None:
        raise HTTPException(status_code=500, detail="등록된 영화를 다시 조회하지 못했습니다.")
    return movie


@app.get("/movies", response_model=list[MovieRead])
def list_movies() -> list[MovieRead]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                m.*,
                COUNT(r.id) AS review_count,
                AVG(r.sentiment_score) AS average_sentiment_score
            FROM movies AS m
            LEFT JOIN reviews AS r ON r.movie_id = m.id
            GROUP BY m.id
            ORDER BY m.id
            """
        ).fetchall()
    return [movie_from_row(row) for row in rows]


@app.get("/movies/{movie_id}", response_model=MovieRead)
def get_movie(movie_id: int) -> MovieRead:
    movie = fetch_movie(movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")
    return movie


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int) -> dict[str, bool | int]:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")
    return {"deleted": True, "movie_id": movie_id}


@app.post(
    "/movies/{movie_id}/reviews",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
)
def create_review(movie_id: int, payload: ReviewCreate) -> ReviewRead:
    if fetch_movie(movie_id) is None:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")

    sentiment = analyze_sentiment(payload.content)
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO reviews (
                movie_id,
                author_name,
                content,
                sentiment_label,
                sentiment_score,
                sentiment_confidence
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                movie_id,
                payload.author_name,
                payload.content,
                sentiment.sentiment_label,
                sentiment.sentiment_score,
                sentiment.confidence,
            ),
        )
        review_id = cursor.lastrowid
        row = connection.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()
    return review_from_row(row)


@app.get("/movies/{movie_id}/reviews", response_model=list[ReviewRead])
def list_movie_reviews(movie_id: int) -> list[ReviewRead]:
    if fetch_movie(movie_id) is None:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM reviews
            WHERE movie_id = ?
            ORDER BY id DESC
            """,
            (movie_id,),
        ).fetchall()
    return [review_from_row(row) for row in rows]


@app.get("/reviews", response_model=list[ReviewRead])
def list_reviews(
    movie_id: int | None = None,
    limit: int = Query(default=10, ge=1, le=100),
) -> list[ReviewRead]:
    query = "SELECT * FROM reviews"
    params: tuple[int, ...] | tuple[int, int] = ()
    if movie_id is not None:
        query += " WHERE movie_id = ?"
        params = (movie_id,)
    query += " ORDER BY id DESC LIMIT ?"
    params = (*params, limit)

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return [review_from_row(row) for row in rows]


@app.delete("/reviews/{review_id}")
def delete_review(review_id: int) -> dict[str, bool | int]:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다.")
    return {"deleted": True, "review_id": review_id}


@app.get("/movies/{movie_id}/rating", response_model=RatingRead)
def get_movie_rating(movie_id: int) -> RatingRead:
    if fetch_movie(movie_id) is None:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(id) AS review_count,
                AVG(sentiment_score) AS average_sentiment_score
            FROM reviews
            WHERE movie_id = ?
            """,
            (movie_id,),
        ).fetchone()
    return RatingRead(
        movie_id=movie_id,
        review_count=row["review_count"],
        average_sentiment_score=row["average_sentiment_score"],
    )


@app.post("/sentiment/analyze", response_model=SentimentResult)
def analyze_sentiment_endpoint(payload: SentimentRequest) -> SentimentResult:
    return analyze_sentiment(payload.content)
