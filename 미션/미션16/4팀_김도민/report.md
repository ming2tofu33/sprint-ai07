# 미션 16 요약 보고서

## 1. 미션 목표

이번 미션에서는 MNIST 숫자 분류 모델을 학습한 뒤, 같은 모델을 세 가지 형식으로 저장하고 다시 추론 가능한지 검증했다.

- 기본 PyTorch 저장 형식: `.pth`
- 양자화된 PyTorch 저장 형식: `.pth`
- ONNX 저장 형식: `.onnx`

모델은 28x28 MNIST 이미지를 입력받아 0부터 9까지의 숫자 label을 예측하는 MLP 구조로 구성했다. 이번 과제의 핵심은 모델 성능 경쟁이 아니라 모델 저장, 변환, 재로드, 추론 검증이므로 양자화와 ONNX 변환이 안정적인 `Linear` 계층 중심 모델을 선택했다.

## 2. 모델 저장 결과

| 모델 타입 | 파일명 | 용량 | 테스트 정확도 |
| --- | --- | ---: | ---: |
| 기본 PyTorch | `mission_16_mnist_mlp.pth` | 2095.63 KB | 0.9762 |
| 양자화 PyTorch | `mission_16_mnist_mlp_quantized.pth` | 530.24 KB | 0.9761 |
| ONNX | `mission_16_mnist_mlp.onnx` | 2094.22 KB | 0.9762 |

양자화 모델은 기본 PyTorch 모델보다 파일 크기가 크게 줄었고, 테스트 정확도는 거의 동일하게 유지되었다.

보고서 첨부 이미지:

- `report-assets/mission16_model_size_comparison.png`

## 3. 추론 검증 결과

`inference.ipynb`에서는 학습을 다시 수행하지 않고 저장된 모델 파일만 불러와 추론을 진행했다. 세 모델 모두 MNIST 테스트 데이터에서 정상적으로 추론되었다.

| 모델 | 테스트 정확도 |
| --- | ---: |
| 기본 `.pth` | 0.9762 |
| 양자화 `.pth` | 0.9761 |
| `.onnx` | 0.9762 |

샘플 12개 이미지에 대해 세 모델의 예측 label을 비교했으며, 모든 샘플에서 세 모델의 예측이 일치했다.

보고서 첨부 이미지:

- `report-assets/mission16_inference_sample_predictions.png`

## 4. 양자화 정리

양자화는 모델 내부의 가중치 값을 더 작은 표현 방식으로 바꾸어 모델 용량을 줄이는 과정이다. 이번 실습에서는 MLP의 `Linear` 계층에 동적 양자화를 적용했다.

실험 결과 기본 모델은 약 2095.63 KB, 양자화 모델은 약 530.24 KB로 감소했다. 정확도는 0.9762에서 0.9761로 거의 변하지 않았다. 따라서 이번 모델에서는 양자화를 통해 용량을 줄이면서도 추론 성능을 대부분 유지할 수 있었다.

## 5. 디버깅 및 오류 해결 과정

| 상황 | 원인 | 해결 |
| --- | --- | --- |
| `onnx`, `onnxruntime` import 실패 | 패키지가 설치되어 있지 않았음 | `pip install onnx onnxruntime`으로 설치 후 버전 확인 |
| ONNX 모델 입력 확인 필요 | ONNX Runtime은 정확한 입력 이름과 shape가 필요함 | ONNX 그래프를 확인해 입력 이름 `input`, 입력 shape `[1, 1, 28, 28]` 확인 |
| 양자화 모델 로드 방식 확인 필요 | 양자화 모델은 기본 모델과 모듈 구조가 달라질 수 있음 | 같은 MLP 구조에 동적 양자화를 먼저 적용한 뒤 저장된 state dict를 로드 |
| 심화 JavaScript 출력 줄바꿈 문제 | 문자열 조합에서 줄바꿈 문자를 잘못 사용함 | `\\n` 문자열이 아니라 실제 줄바꿈 문자로 수정 |

## 6. 심화 미션 결과

심화 미션에서는 제공된 `mnist_cnn.onnx` 모델을 Python이 아닌 JavaScript/Node.js 환경에서 실행했다. `onnxruntime-node`와 `pngjs`를 사용해 28x28 흑백 PNG 이미지를 읽고, MNIST 평균과 표준편차로 정규화한 뒤 ONNX Runtime에 입력했다.

예측 결과는 다음과 같다.

| 이미지 | 예측 label | confidence |
| --- | ---: | ---: |
| `image1.png` | 8 | 1.0000 |
| `image2.png` | 3 | 1.0000 |
| `image3.png` | 2 | 1.0000 |

심화 결과 파일:

- `mission-result/advanced-js/src/infer.js`
- `mission-result/advanced-js/README.md`
- `mission-result/advanced-js/screenshots/advanced_inference_output.png`
