# 미션 15 보고서 초안

## Docker Hub URL

https://hub.docker.com/r/ming2tofu33/mission15-researcher1

## 연구자 1 모델링 요약

연구자 1은 `train.csv` 7000행을 사용하여 학생 성취도 지표인 `Performance Index`를 예측하는 회귀 모델을 학습했다. 입력 변수는 `Hours Studied`, `Previous Scores`, `Extracurricular Activities`, `Sleep Hours`, `Sample Question Papers Practiced`를 사용했다.

전처리는 숫자형 변수 표준화와 범주형 변수 원-핫 인코딩으로 구성했다. 전처리와 모델을 하나의 scikit-learn `Pipeline`으로 묶어 저장했기 때문에, 연구자 2 추론 환경에서도 동일한 전처리 과정을 재현할 수 있다.

최종 모델은 `Ridge(alpha=1.0)`을 사용했다. 학습 데이터의 20%를 검증 데이터로 분리하여 RMSE로 평가했으며, 검증 RMSE는 `2.0105`였다. 최종 모델은 전체 학습 데이터로 다시 학습한 뒤 `model.pkl`로 저장했다.

## 코드 아키텍처

```text
researcher1 Docker image
  ├─ data/train.csv
  ├─ data/test.csv
  ├─ train_model.py
  └─ /shared/model.pkl, /shared/test.csv, /shared/metrics.json 생성

shared volume
  ├─ model.pkl
  ├─ test.csv
  ├─ metrics.json
  └─ result.csv

researcher2 Jupyter image
  ├─ inference.py
  ├─ inference.ipynb
  └─ /shared/model.pkl + /shared/test.csv를 읽어 /shared/result.csv 생성
```

## 파일 전달 전략

두 컨테이너는 `docker-compose.yml`에서 같은 `./shared:/shared` 바인드 마운트를 사용한다. 연구자 1 컨테이너는 학습 완료 후 `/shared/model.pkl`과 `/shared/test.csv`를 생성한다. 연구자 2 컨테이너는 같은 `/shared` 경로에서 모델과 테스트 데이터를 읽고 추론 결과를 `/shared/result.csv`로 저장한다.

이 구조에서는 연구자 2가 사전에 데이터나 모델 파일을 직접 보유하지 않아도 된다. 필요한 파일은 연구자 1 Docker 이미지 실행 결과로 공유 폴더에 생성된다.

## 버전 통일 전략

두 연구자 컨테이너 모두 Python 3.11 기반 이미지를 사용하며, 주요 패키지는 requirements 파일에 버전을 고정했다.

- `numpy==1.26.4`
- `pandas==2.2.3`
- `scikit-learn==1.5.2`
- `joblib==1.4.2`

특히 `scikit-learn` 버전을 고정하여 `model.pkl` 저장 및 로드 과정에서 발생할 수 있는 버전 불일치 문제를 줄였다.
