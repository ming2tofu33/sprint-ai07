# 미션 18 Backend 설계 문서

이 문서는 영화 리뷰 감성 분석 서비스의 데이터베이스 구조와 FastAPI API 목록을 고정하기 위한 설계 문서입니다. 구현할 때는 이 문서를 기준으로 백엔드 코드를 작성합니다.

## 설계 방향

- 프론트엔드 Streamlit은 화면과 사용자 입력만 담당합니다.
- 백엔드 FastAPI는 영화, 리뷰, 감성 분석 결과를 관리합니다.
- 모든 데이터 저장은 백엔드에서 처리합니다.
- 데이터베이스는 과제 구현 난이도를 고려해 SQLite를 기본으로 사용합니다.
- 영화 1개에 리뷰 여러 개가 연결되는 1:N 구조로 설계합니다.
- 리뷰 등록 시 Hugging Face 한국어 감성 분석 모델을 자동 실행하고, 결과를 리뷰와 함께 저장합니다.

## 데이터베이스 테이블

### movies

영화 기본 정보를 저장하는 테이블입니다.

| 컬럼 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| id | INTEGER | 예 | 영화 고유 ID, 기본키 |
| title | TEXT | 예 | 영화 제목 |
| release_date | TEXT | 예 | 개봉일, `YYYY-MM-DD` 형식 |
| director | TEXT | 예 | 감독 |
| genre | TEXT | 예 | 장르, 여러 개면 쉼표로 구분 |
| poster_url | TEXT | 예 | 포스터 이미지 URL |
| created_at | TEXT | 예 | 등록일시 |
| updated_at | TEXT | 예 | 수정일시 |

### reviews

사용자 리뷰와 감성 분석 결과를 저장하는 테이블입니다.

| 컬럼 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| id | INTEGER | 예 | 리뷰 고유 ID, 기본키 |
| movie_id | INTEGER | 예 | 리뷰가 연결된 영화 ID, `movies.id` 외래키 |
| author_name | TEXT | 예 | 리뷰 작성자 이름 |
| content | TEXT | 예 | 리뷰 내용 |
| sentiment_label | TEXT | 예 | 감성 분석 결과 label, 예: `positive`, `negative`, `neutral` |
| sentiment_score | REAL | 예 | 감성 점수, 0.0부터 1.0 사이 값 |
| sentiment_confidence | REAL | 아니오 | 모델의 확신도, 모델이 제공할 경우 저장 |
| created_at | TEXT | 예 | 리뷰 등록일시 |

## 테이블 관계

- `movies.id` 1개는 `reviews.movie_id` 여러 개와 연결됩니다.
- 영화가 삭제되면 해당 영화의 리뷰도 함께 삭제되도록 설계합니다.
- 리뷰별 감성 점수의 평균을 계산해서 영화별 평균 감성 점수로 보여줍니다.

## 평균 점수 기준

별도 별점 입력을 받지 않으므로, Hugging Face 모델의 감성 분석 점수를 평균 내어 영화별 평균 점수처럼 사용합니다.

- `sentiment_score`는 긍정에 가까울수록 1.0에 가까운 값으로 저장합니다.
- 영화의 평균 점수는 해당 영화에 달린 리뷰들의 `sentiment_score` 평균입니다.
- 리뷰가 없으면 평균 점수는 `null` 또는 `0` 대신 `리뷰 없음`으로 화면에 표시하는 것이 좋습니다.

## 감성 분석 모델

기본 모델은 `cringepnh/koelectra-korean-sentiment`입니다. 이 모델은 한국어 영화 리뷰 데이터셋인 NSMC로 학습된 KoELECTRA 기반 긍정/부정 분류 모델입니다.

백엔드의 `app/sentiment.py`는 Hugging Face `transformers`의 `pipeline("text-classification")`으로 모델을 lazy-load합니다. 리뷰 등록 API가 `analyze_sentiment()`를 호출하면 모델 출력 label과 score를 프로젝트의 `sentiment_label`, `sentiment_score`, `sentiment_confidence` 형식으로 변환합니다.

모델 출력이 긍정이면 `sentiment_score`는 confidence와 같은 높은 값으로 저장합니다. 모델 출력이 부정이면 평균 점수 계산을 위해 `1 - confidence`를 저장합니다.

## FastAPI API 목록

### 상태 확인

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/health` | 백엔드 서버 상태 확인 |

### 영화 관리

| Method | Path | 설명 | 요청 데이터 | 응답 데이터 |
| --- | --- | --- | --- | --- |
| POST | `/movies` | 영화 등록 | title, release_date, director, genre, poster_url | 등록된 영화 정보 |
| GET | `/movies` | 전체 영화 목록 조회 | 없음 | 영화 목록, 리뷰 수, 평균 감성 점수 |
| GET | `/movies/{movie_id}` | 특정 영화 조회 | movie_id | 영화 상세 정보 |
| DELETE | `/movies/{movie_id}` | 특정 영화 삭제 | movie_id | 삭제 결과 |

### 리뷰 관리

| Method | Path | 설명 | 요청 데이터 | 응답 데이터 |
| --- | --- | --- | --- | --- |
| POST | `/movies/{movie_id}/reviews` | 특정 영화에 리뷰 등록 | author_name, content | 감성 분석 결과가 포함된 리뷰 정보 |
| GET | `/movies/{movie_id}/reviews` | 특정 영화의 리뷰 목록 조회 | movie_id | 해당 영화의 리뷰 목록 |
| GET | `/reviews` | 최근 리뷰 목록 조회 | 선택: movie_id, limit | 최근 리뷰 목록 |
| DELETE | `/reviews/{review_id}` | 특정 리뷰 삭제 | review_id | 삭제 결과 |

### 평점과 감성 분석

| Method | Path | 설명 | 요청 데이터 | 응답 데이터 |
| --- | --- | --- | --- | --- |
| GET | `/movies/{movie_id}/rating` | 특정 영화의 평균 감성 점수 조회 | movie_id | review_count, average_sentiment_score |
| POST | `/sentiment/analyze` | 감성 분석 단독 테스트 | content | sentiment_label, sentiment_score, confidence |

`/sentiment/analyze`는 필수 화면 기능은 아니지만, FastAPI Docs에서 모델 동작을 따로 확인하고 보고서에 설명하기 좋기 때문에 추가 후보로 둡니다.

## 요청/응답 스키마 초안

### MovieCreate

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| title | string | 영화 제목 |
| release_date | string | 개봉일, `YYYY-MM-DD` |
| director | string | 감독 |
| genre | string | 장르 |
| poster_url | string | 포스터 URL |

### MovieRead

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 영화 ID |
| title | string | 영화 제목 |
| release_date | string | 개봉일 |
| director | string | 감독 |
| genre | string | 장르 |
| poster_url | string | 포스터 URL |
| review_count | integer | 리뷰 개수 |
| average_sentiment_score | number or null | 평균 감성 점수 |
| created_at | string | 등록일시 |
| updated_at | string | 수정일시 |

### ReviewCreate

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| author_name | string | 작성자 이름 |
| content | string | 리뷰 내용 |

### ReviewRead

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 리뷰 ID |
| movie_id | integer | 영화 ID |
| author_name | string | 작성자 이름 |
| content | string | 리뷰 내용 |
| sentiment_label | string | 감성 label |
| sentiment_score | number | 감성 점수 |
| sentiment_confidence | number or null | 모델 확신도 |
| created_at | string | 등록일시 |

## 구현 우선순위

1. SQLite 연결과 테이블 생성
2. 영화 등록 API
3. 영화 목록/상세 조회 API
4. 영화 삭제 API
5. 리뷰 등록 API
6. 특정 영화 리뷰 조회 API
7. 감성 분석 함수 연결
8. 평균 감성 점수 계산 API
9. 최근 리뷰 조회 API
10. FastAPI Docs 설명 확인

## 검증 기준

- 영화 3개 이상을 등록할 수 있어야 합니다.
- 각 영화에 리뷰 10개 이상을 등록할 수 있어야 합니다.
- 리뷰 등록 시 감성 분석 결과가 자동 저장되어야 합니다.
- 영화 목록 조회 시 리뷰 수와 평균 감성 점수가 함께 보여야 합니다.
- FastAPI Docs에서 주요 API 요청과 응답을 확인할 수 있어야 합니다.
