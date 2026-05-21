# 미션 18: 한국 영화 리뷰 감성 분석 서비스

Streamlit 프론트엔드와 FastAPI 백엔드를 분리해 구현한 영화 리뷰 감성 분석 웹 애플리케이션입니다. 리뷰 감성 분석은 Hugging Face `cringepnh/koelectra-korean-sentiment` 모델을 사용합니다.

## 폴더 구조

```text
4팀_김도민/
├─ backend/
├─ frontend/
└─ report/
```

## 백엔드 실행

```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

FastAPI Docs:

```text
http://127.0.0.1:8000/docs
```

## 샘플 데이터 등록 및 재분석

```powershell
python scripts\seed_korean_movies.py
python scripts\recompute_sentiment.py
```

## 프론트엔드 실행

```powershell
cd frontend
pip install -r requirements.txt
python -m streamlit run app.py --server.port 8501
```

Streamlit:

```text
http://127.0.0.1:8501
```

## 보고서

최종 보고서는 `report/미션18_4팀_김도민_보고서.pdf`입니다.
