# 미션 17 - MNIST ONNX 손글씨 숫자 인식 서비스

Streamlit 캔버스에 손으로 숫자를 그리면 MNIST ONNX 모델로 0부터 9까지의 예측 확률을 계산하고 결과를 보여주는 웹 서비스입니다.

## 주요 기능

- 손글씨 숫자 입력 캔버스
- 모델 입력용 28x28 흑백 전처리 이미지 표시
- ONNX Runtime 기반 MNIST 모델 추론
- 예측 숫자와 class별 확률 차트 표시
- 예측 이미지 저장소
- Docker 이미지 빌드 및 Docker Hub 배포 준비

## 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속합니다.

## 테스트

```bash
pytest -q
```

## Docker 실행

```bash
docker build -t ming2tofu33/mission17-mnist-streamlit:latest .
docker run --rm -p 8501:8501 ming2tofu33/mission17-mnist-streamlit:latest
```

## Docker Hub

보고서에는 아래 형식의 Docker Hub URL을 넣으면 됩니다.

```text
https://hub.docker.com/r/ming2tofu33/mission17-mnist-streamlit
```

업로드 명령은 다음과 같습니다.

```bash
docker push ming2tofu33/mission17-mnist-streamlit:latest
```

## 파일 구조

```text
.
├── app.py
├── image_processing.py
├── inference_utils.py
├── models/
│   └── mnist_cnn.onnx
├── saved_images/
├── report/
├── tests/
├── requirements.txt
├── Dockerfile
└── README.md
```
