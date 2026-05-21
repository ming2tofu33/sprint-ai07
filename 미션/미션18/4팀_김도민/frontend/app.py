import os
from datetime import date

import requests
import streamlit as st

from api_client import MovieReviewAPI, format_score, sentiment_badge, sentiment_class


DEFAULT_API_URL = os.getenv("MISSION18_API_BASE_URL", "http://127.0.0.1:8000")


st.set_page_config(
    page_title="한국 영화 리뷰 감성 분석",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2.5rem;
        max-width: 1280px;
    }
    .main-title {
        font-size: 2rem;
        font-weight: 760;
        letter-spacing: 0;
        margin: 0 0 .2rem;
        color: #111827;
    }
    .subtle {
        color: #64748b;
        font-size: .92rem;
    }
    .metric-row {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: .75rem;
        margin: 1rem 0 1.3rem;
    }
    .metric-box {
        border: 1px solid #d9e2ec;
        border-radius: 8px;
        padding: .8rem .9rem;
        background: #f8fafc;
    }
    .metric-label {
        color: #64748b;
        font-size: .78rem;
        margin-bottom: .2rem;
    }
    .metric-value {
        color: #0f172a;
        font-size: 1.35rem;
        font-weight: 720;
    }
    .movie-title {
        color: #0f172a;
        font-size: 1.05rem;
        font-weight: 750;
        margin-bottom: .2rem;
    }
    .movie-meta {
        color: #475569;
        font-size: .86rem;
        line-height: 1.55;
    }
    .score-pill {
        display: inline-flex;
        border-radius: 999px;
        border: 1px solid #cbd5e1;
        padding: .18rem .55rem;
        margin-top: .55rem;
        color: #0f172a;
        font-size: .78rem;
        background: #f8fafc;
    }
    .review-item {
        border-bottom: 1px solid #e2e8f0;
        padding: .65rem 0;
    }
    .review-meta {
        color: #64748b;
        font-size: .78rem;
        margin-bottom: .25rem;
    }
    .review-content {
        color: #111827;
        font-size: .92rem;
        line-height: 1.5;
    }
    .sentiment-positive,
    .sentiment-negative,
    .sentiment-neutral {
        display: inline-flex;
        border-radius: 999px;
        padding: .12rem .5rem;
        font-size: .75rem;
        font-weight: 700;
        margin-left: .35rem;
    }
    .sentiment-positive {
        color: #065f46;
        background: #d1fae5;
    }
    .sentiment-negative {
        color: #991b1b;
        background: #fee2e2;
    }
    .sentiment-neutral {
        color: #334155;
        background: #e2e8f0;
    }
    div[data-testid="stButton"] > button {
        border-radius: 6px;
        min-height: 2.35rem;
    }
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        border-radius: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_api() -> MovieReviewAPI:
    return MovieReviewAPI(st.session_state["api_base_url"])


def safe_call(label: str, callback):
    try:
        return callback()
    except requests.RequestException as error:
        st.error(f"{label} 실패: 백엔드 서버 연결 또는 API 응답을 확인하세요.")
        st.caption(str(error))
        return None
    except RuntimeError as error:
        st.error(f"{label} 실패")
        st.caption(str(error))
        return None


def render_metrics(movies: list[dict]) -> None:
    review_count = sum(movie.get("review_count", 0) for movie in movies)
    scored_movies = [movie for movie in movies if movie.get("average_sentiment_score") is not None]
    if scored_movies:
        average_score = sum(movie["average_sentiment_score"] for movie in scored_movies) / len(scored_movies)
        average_text = format_score(average_score)
    else:
        average_text = "리뷰 없음"

    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-box">
                <div class="metric-label">등록 영화</div>
                <div class="metric-value">{len(movies)}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">전체 리뷰</div>
                <div class="metric-value">{review_count}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">평균 감성 점수</div>
                <div class="metric-value">{average_text}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_movie_card(movie: dict) -> None:
    image_col, text_col = st.columns([0.34, 0.66], vertical_alignment="top")
    with image_col:
        st.image(movie["poster_url"], width="stretch")
    with text_col:
        st.markdown(
            f"""
            <div class="movie-title">{movie['title']}</div>
            <div class="movie-meta">
                {movie['release_date']}<br>
                감독 {movie['director']}<br>
                {movie['genre']}<br>
                리뷰 {movie['review_count']}개
            </div>
            <div class="score-pill">{format_score(movie.get('average_sentiment_score'))}</div>
            """,
            unsafe_allow_html=True,
        )


def render_review(review: dict) -> None:
    label = review["sentiment_label"]
    st.markdown(
        f"""
        <div class="review-item">
            <div class="review-meta">
                {review['author_name']} · {review['created_at']}
                <span class="{sentiment_class(label)}">{sentiment_badge(label)} {format_score(review['sentiment_score'])}</span>
            </div>
            <div class="review-content">{review['content']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if "api_base_url" not in st.session_state:
    st.session_state["api_base_url"] = DEFAULT_API_URL
if "selected_movie_id" not in st.session_state:
    st.session_state["selected_movie_id"] = None


with st.sidebar:
    st.header("연결")
    st.text_input("FastAPI 주소", key="api_base_url")
    if st.button("상태 확인", width="stretch"):
        health = safe_call("상태 확인", lambda: get_api().health())
        if health and health.get("status") == "ok":
            st.success("연결됨")
    st.divider()
    st.caption("FastAPI: http://127.0.0.1:8000/docs")


api = get_api()
movies = safe_call("영화 목록 조회", api.list_movies)
movies = movies or []

st.markdown('<h1 class="main-title">한국 영화 리뷰 감성 분석</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtle">FastAPI 백엔드 연결 · SQLite 데이터 저장</div>', unsafe_allow_html=True)
render_metrics(movies)


movie_tab, add_movie_tab, review_tab, recent_tab = st.tabs(
    ["영화 목록", "영화 등록", "리뷰 관리", "최근 리뷰"]
)

with movie_tab:
    if not movies:
        st.info("등록된 영화가 없습니다.")
    else:
        for row_start in range(0, len(movies), 3):
            cols = st.columns(3)
            for col, movie in zip(cols, movies[row_start : row_start + 3]):
                with col:
                    with st.container(border=True):
                        render_movie_card(movie)
                        select_col, delete_col = st.columns([0.58, 0.42])
                        with select_col:
                            if st.button("선택", key=f"select-{movie['id']}", width="stretch"):
                                st.session_state["selected_movie_id"] = movie["id"]
                                st.rerun()
                        with delete_col:
                            if st.button("삭제", key=f"delete-movie-{movie['id']}", width="stretch"):
                                deleted = safe_call("영화 삭제", lambda movie_id=movie["id"]: api.delete_movie(movie_id))
                                if deleted:
                                    if st.session_state["selected_movie_id"] == movie["id"]:
                                        st.session_state["selected_movie_id"] = None
                                    st.rerun()

with add_movie_tab:
    with st.form("movie-form", clear_on_submit=True):
        title = st.text_input("제목")
        release_date = st.date_input("개봉일", value=date(2024, 1, 1))
        director = st.text_input("감독")
        genre = st.text_input("장르")
        poster_url = st.text_input("포스터 URL")
        submitted = st.form_submit_button("영화 등록", width="stretch")
        if submitted:
            payload = {
                "title": title,
                "release_date": release_date.isoformat(),
                "director": director,
                "genre": genre,
                "poster_url": poster_url,
            }
            created = safe_call("영화 등록", lambda: api.create_movie(payload))
            if created:
                st.success(f"{created['title']} 등록 완료")
                st.rerun()

with review_tab:
    if not movies:
        st.info("리뷰를 등록할 영화가 없습니다.")
    else:
        movie_options = {f"{movie['title']} · 리뷰 {movie['review_count']}개": movie["id"] for movie in movies}
        selected_label = st.selectbox("영화 선택", list(movie_options.keys()))
        selected_movie_id = movie_options[selected_label]
        st.session_state["selected_movie_id"] = selected_movie_id

        selected_movie = next(movie for movie in movies if movie["id"] == selected_movie_id)
        st.subheader(selected_movie["title"])
        st.caption(
            f"{selected_movie['release_date']} · {selected_movie['director']} · "
            f"{selected_movie['genre']} · {format_score(selected_movie.get('average_sentiment_score'))}"
        )

        form_col, list_col = st.columns([0.38, 0.62], gap="large")
        with form_col:
            with st.form("review-form", clear_on_submit=True):
                author_name = st.text_input("작성자")
                content = st.text_area("리뷰 내용", height=150)
                submitted = st.form_submit_button("리뷰 등록", width="stretch")
                if submitted:
                    created = safe_call(
                        "리뷰 등록",
                        lambda: api.create_review(
                            selected_movie_id,
                            {"author_name": author_name, "content": content},
                        ),
                    )
                    if created:
                        st.success(
                            f"{sentiment_badge(created['sentiment_label'])} · "
                            f"{format_score(created['sentiment_score'])}"
                        )
                        st.rerun()

        with list_col:
            reviews = safe_call("리뷰 목록 조회", lambda: api.list_movie_reviews(selected_movie_id))
            reviews = reviews or []
            st.markdown(f"#### 리뷰 {len(reviews)}개")
            if not reviews:
                st.info("등록된 리뷰가 없습니다.")
            else:
                for review in reviews:
                    render_review(review)

with recent_tab:
    recent_reviews = safe_call("최근 리뷰 조회", lambda: api.list_reviews(limit=10))
    recent_reviews = recent_reviews or []
    st.markdown("#### 최근 10개 리뷰")
    if not recent_reviews:
        st.info("최근 리뷰가 없습니다.")
    else:
        movie_title_by_id = {movie["id"]: movie["title"] for movie in movies}
        for review in recent_reviews:
            st.caption(movie_title_by_id.get(review["movie_id"], f"영화 ID {review['movie_id']}"))
            render_review(review)
