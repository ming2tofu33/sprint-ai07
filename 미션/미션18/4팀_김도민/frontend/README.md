# 미션 18 Frontend

Streamlit 기반 영화 리뷰 감성 분석 프론트엔드입니다. 모든 영화와 리뷰 데이터는 FastAPI 백엔드 API를 통해 조회하고 저장합니다.

## 실행 전 확인

백엔드 서버를 먼저 실행합니다.

```powershell
cd ..\backend
python -m uvicorn app.main:app --reload --port 8000
```

## 실행 방법

```powershell
pip install -r requirements.txt
python -m streamlit run app.py --server.port 8501
```

브라우저에서 아래 주소로 접속합니다.

```text
http://localhost:8501
```

## 백엔드 주소 변경

기본 API 주소는 `http://127.0.0.1:8000`입니다. 배포 환경에서는 환경변수로 변경할 수 있습니다.

```powershell
$env:MISSION18_API_BASE_URL="https://your-backend.example.com"
python -m streamlit run app.py
```

## 테스트

```powershell
python -m pytest tests/test_api_client.py -q
```
