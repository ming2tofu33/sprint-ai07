# Mission 16 Result

## 기본 미션

- `modeling.ipynb`: MNIST MLP 모델 학습, 기본 `.pth` 저장, 양자화 `.pth` 저장, ONNX 변환
- `inference.ipynb`: 저장된 세 모델을 다시 불러와 추론 검증
- `models`: 생성된 모델 파일 3개

## 생성 모델

- `models/mission_16_mnist_mlp.pth`
- `models/mission_16_mnist_mlp_quantized.pth`
- `models/mission_16_mnist_mlp.onnx`

## 심화 미션

`advanced-js` 폴더에는 `mnist_cnn.onnx`를 Node.js에서 실행하는 코드가 있습니다.

ONNX 모델 파일은 심화 제출 안내에 따라 코드 폴더에 포함하지 않았습니다. 실행 시 `미션/content/16/mnist_cnn.onnx` 위치의 모델을 사용하거나, `MODEL_PATH` 환경 변수로 직접 지정합니다.
