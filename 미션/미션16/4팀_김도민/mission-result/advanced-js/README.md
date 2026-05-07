# Mission 16 Advanced ONNX Inference

이 폴더는 심화 미션용 JavaScript/Node.js ONNX 추론 코드입니다.

## 개요

- 사용 언어: JavaScript, Node.js
- 사용 라이브러리: `onnxruntime-node`, `pngjs`
- 모델: `mnist_cnn.onnx`
- 입력 이미지: 28x28 흑백 PNG 이미지 3장

## 파일 준비

심화 제출 안내에 따라 ONNX 모델 파일은 코드 제출물에 포함하지 않습니다.

실행할 때는 `mnist_cnn.onnx` 파일을 아래 기본 위치에 두거나, `MODEL_PATH` 환경 변수로 직접 지정합니다.

기본 위치:

```text
미션/content/16/mnist_cnn.onnx
```

타겟 이미지는 `images` 폴더에 있습니다.

## 설치

```bash
npm install
```

## 실행

```bash
npm start
```

다른 위치의 모델 파일을 사용하려면 다음처럼 실행합니다.

```bash
MODEL_PATH=/path/to/mnist_cnn.onnx npm start
```

Windows PowerShell에서는 다음처럼 실행합니다.

```powershell
$env:MODEL_PATH="C:\path\to\mnist_cnn.onnx"; npm start
```

## 출력

실행하면 각 이미지의 예측 label과 confidence가 터미널에 출력됩니다. 같은 내용은 `screenshots/advanced_inference_output.txt`에도 저장됩니다.

제출용 캡처는 터미널에 출력된 결과 화면을 캡처해서 `screenshots` 폴더에 저장하면 됩니다.
