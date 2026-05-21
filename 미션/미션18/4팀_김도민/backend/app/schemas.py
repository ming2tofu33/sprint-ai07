from pydantic import BaseModel, ConfigDict, Field


class MovieCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(..., min_length=1, examples=["파묘"])
    release_date: str = Field(..., min_length=1, examples=["2024-02-22"])
    director: str = Field(..., min_length=1, examples=["장재현"])
    genre: str = Field(..., min_length=1, examples=["오컬트, 미스터리"])
    poster_url: str = Field(..., min_length=1, examples=["https://example.com/poster.jpg"])


class MovieRead(MovieCreate):
    id: int
    review_count: int = 0
    average_sentiment_score: float | None = None
    created_at: str
    updated_at: str


class ReviewCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    author_name: str = Field(..., min_length=1, examples=["도민"])
    content: str = Field(..., min_length=1, examples=["배우들의 연기가 좋고 몰입감이 뛰어났다."])


class ReviewRead(ReviewCreate):
    id: int
    movie_id: int
    sentiment_label: str
    sentiment_score: float
    sentiment_confidence: float | None = None
    created_at: str


class RatingRead(BaseModel):
    movie_id: int
    review_count: int
    average_sentiment_score: float | None = None


class SentimentRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(..., min_length=1, examples=["정말 재미있고 추천하고 싶은 영화였다."])


class SentimentResult(BaseModel):
    sentiment_label: str
    sentiment_score: float
    confidence: float
