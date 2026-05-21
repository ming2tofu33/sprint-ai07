# 미션 18 Backend

FastAPI 기반 영화 리뷰 감성 분석 백엔드입니다. 영화와 리뷰 데이터는 SQLite에 저장하고, 리뷰 등록 시 간단한 감성 분석 결과를 함께 저장합니다.
감성 분석은 기본적으로 Hugging Face의 `cringepnh/koelectra-korean-sentiment` 모델을 사용합니다.

## 실행 방법

```powershell
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

실행 후 아래 주소에서 API 문서를 확인합니다.

```text
http://127.0.0.1:8000/docs
```

## 테스트

```powershell
python -m pytest tests/test_api.py -q
```

## 한국 영화 샘플 데이터 등록

제출 캡처용으로 한국 영화 3개와 각 영화별 리뷰 10개를 등록합니다.

```powershell
python scripts\seed_korean_movies.py
```

## Hugging Face 감성 분석 재계산

이미 저장된 리뷰의 감성 분석 결과를 Hugging Face 모델로 다시 계산합니다. 첫 실행 시 모델 다운로드 때문에 시간이 걸릴 수 있습니다.

```powershell
python scripts\recompute_sentiment.py
```

사용 모델은 환경변수로 바꿀 수 있습니다.

```powershell
$env:MISSION18_HF_MODEL="cringepnh/koelectra-korean-sentiment"
```

테스트처럼 모델 다운로드 없이 규칙 기반 분석기를 쓰고 싶을 때는 다음 환경변수를 사용합니다.

```powershell
$env:MISSION18_SENTIMENT_BACKEND="rules"
```

## 주요 API

- `GET /health`
- `POST /movies`
- `GET /movies`
- `GET /movies/{movie_id}`
- `DELETE /movies/{movie_id}`
- `POST /movies/{movie_id}/reviews`
- `GET /movies/{movie_id}/reviews`
- `GET /reviews`
- `DELETE /reviews/{review_id}`
- `GET /movies/{movie_id}/rating`
- `POST /sentiment/analyze`

## 데이터베이스

기본 DB 파일은 `backend/data/mission18.db`에 생성됩니다. 테스트에서는 `MISSION18_DB_PATH` 환경변수로 임시 DB 경로를 지정합니다.
