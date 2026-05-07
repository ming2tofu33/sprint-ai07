const fs = require("fs");
const path = require("path");
const ort = require("onnxruntime-node");
const { PNG } = require("pngjs");

// 심화 미션용 코드입니다.
// Python이 아닌 Node.js 환경에서 ONNX 모델을 불러와 MNIST 이미지를 추론합니다.
const PROJECT_DIR = path.resolve(__dirname, "..");

// 심화 제출 안내에 따라 onnx 모델 파일은 코드 폴더에 포함하지 않습니다.
// 기본값으로 수업 자료 위치의 mnist_cnn.onnx를 사용하고,
// 필요하면 MODEL_PATH 환경 변수로 다른 모델 경로를 지정할 수 있습니다.
const DEFAULT_MODEL_PATH = path.resolve(PROJECT_DIR, "../../../../content/16/mnist_cnn.onnx");
const MODEL_PATH = process.env.MODEL_PATH
  ? path.resolve(process.env.MODEL_PATH)
  : DEFAULT_MODEL_PATH;

// 추론할 이미지 폴더도 기본값을 두고, 필요하면 IMAGE_DIR 환경 변수로 바꿀 수 있습니다.
const IMAGE_DIR = process.env.IMAGE_DIR
  ? path.resolve(process.env.IMAGE_DIR)
  : path.join(PROJECT_DIR, "images");
const OUTPUT_DIR = path.join(PROJECT_DIR, "screenshots");

// Python modeling/inference에서 사용한 MNIST 정규화 값과 맞춥니다.
// 전처리가 다르면 같은 모델이라도 예측 결과가 달라질 수 있습니다.
const MNIST_MEAN = 0.1307;
const MNIST_STD = 0.3081;

function softmax(logits) {
  // 모델 출력 logits를 사람이 보기 쉬운 확률 형태로 바꿉니다.
  const maxLogit = Math.max(...logits);
  const exps = logits.map((value) => Math.exp(value - maxLogit));
  const sum = exps.reduce((acc, value) => acc + value, 0);
  return exps.map((value) => value / sum);
}

function argmax(values) {
  // 가장 큰 확률을 가진 index가 예측 label입니다.
  let bestIndex = 0;
  let bestValue = values[0];
  for (let i = 1; i < values.length; i += 1) {
    if (values[i] > bestValue) {
      bestIndex = i;
      bestValue = values[i];
    }
  }
  return bestIndex;
}

function loadMnistImage(imagePath) {
  // PNG 이미지를 읽어서 ONNX 모델 입력 shape인 [1, 1, 28, 28]에 맞는 Float32Array로 바꿉니다.
  const png = PNG.sync.read(fs.readFileSync(imagePath));
  if (png.width !== 28 || png.height !== 28) {
    throw new Error(`${path.basename(imagePath)} must be 28x28, got ${png.width}x${png.height}`);
  }

  const data = new Float32Array(1 * 1 * 28 * 28);
  for (let y = 0; y < 28; y += 1) {
    for (let x = 0; x < 28; x += 1) {
      const rgbaOffset = (y * 28 + x) * 4;
      // PNG는 RGBA 4채널로 읽히지만, 타겟 이미지는 흑백이라 R 채널 값만 사용합니다.
      const pixel = png.data[rgbaOffset] / 255.0;
      // 학습 때와 같은 MNIST 평균/표준편차로 정규화합니다.
      data[y * 28 + x] = (pixel - MNIST_MEAN) / MNIST_STD;
    }
  }
  return data;
}

async function main() {
  // 모델과 이미지가 없는 상태에서 조용히 실패하지 않도록 먼저 경로를 확인합니다.
  if (!fs.existsSync(MODEL_PATH)) {
    throw new Error(`Model file not found: ${MODEL_PATH}`);
  }
  if (!fs.existsSync(IMAGE_DIR)) {
    throw new Error(`Image directory not found: ${IMAGE_DIR}`);
  }

  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  const imageFiles = fs
    .readdirSync(IMAGE_DIR)
    .filter((name) => name.toLowerCase().endsWith(".png"))
    .sort();

  if (imageFiles.length === 0) {
    throw new Error(`No PNG images found in ${IMAGE_DIR}`);
  }

  // ONNX Runtime 세션을 만들면 Node.js에서 ONNX 모델을 직접 실행할 수 있습니다.
  const session = await ort.InferenceSession.create(MODEL_PATH);
  const inputName = session.inputNames[0];
  const outputName = session.outputNames[0];

  const lines = [];
  lines.push("Mission 16 advanced ONNX inference");
  lines.push(`model: ${MODEL_PATH}`);
  lines.push(`input: ${inputName}`);
  lines.push(`output: ${outputName}`);
  lines.push("");
  lines.push("image,predicted_label,confidence");

  for (const fileName of imageFiles) {
    const imagePath = path.join(IMAGE_DIR, fileName);
    const inputData = loadMnistImage(imagePath);
    // 모델 입력 shape는 수업 자료의 mnist_cnn.onnx 기준 [1, 1, 28, 28]입니다.
    const inputTensor = new ort.Tensor("float32", inputData, [1, 1, 28, 28]);
    // session.run이 실제 ONNX 추론을 수행하는 부분입니다.
    const outputs = await session.run({ [inputName]: inputTensor });
    const logits = Array.from(outputs[outputName].data);
    const probabilities = softmax(logits);
    const predictedLabel = argmax(probabilities);
    const confidence = probabilities[predictedLabel];
    lines.push(`${fileName},${predictedLabel},${confidence.toFixed(4)}`);
  }

  // 터미널 출력과 동시에 txt 파일로도 남겨 제출 캡처 자료로 활용합니다.
  const outputText = lines.join("\n");
  console.log(outputText);
  fs.writeFileSync(path.join(OUTPUT_DIR, "advanced_inference_output.txt"), `${outputText}\n`, "utf8");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
