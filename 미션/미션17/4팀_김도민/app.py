from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

from image_processing import is_blank_canvas, preprocess_canvas_image, save_preview_image
from inference_utils import create_session, run_prediction, top_prediction

try:
    from streamlit_drawable_canvas import st_canvas
except ImportError:
    st_canvas = None


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "mnist_cnn.onnx"
SAVED_DIR = BASE_DIR / "saved_images"


st.set_page_config(page_title="MNIST ONNX Digit Service", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: #f6f7f9;
        color: #17202a;
    }
    h1, h2, h3 {
        letter-spacing: 0;
    }
    div[data-testid="stMetric"] {
        border-left: 4px solid #0f766e;
        background: #ffffff;
        padding: 0.85rem 1rem;
    }
    div[data-testid="stButton"] button {
        border-radius: 8px;
        border: 1px solid #0f766e;
        background: #0f766e;
        color: white;
        font-weight: 700;
    }
    div[data-testid="stButton"] button:hover {
        border-color: #115e59;
        background: #115e59;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def load_model(model_path: str):
    return create_session(model_path)


def probability_frame(probabilities):
    return pd.DataFrame(
        {
            "digit": [str(i) for i in range(10)],
            "probability": [float(value) for value in probabilities],
        }
    ).set_index("digit")


def saved_samples():
    SAVED_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(SAVED_DIR.glob("digit_*.png"), reverse=True)


st.title("MNIST ONNX Digit Service")

if st_canvas is None:
    st.error("streamlit-drawable-canvas is not installed.")
    st.stop()

if not MODEL_PATH.exists():
    st.error(f"Model file not found: {MODEL_PATH}")
    st.stop()

session = load_model(str(MODEL_PATH))

input_col, preview_col, result_col = st.columns([1.05, 0.8, 1.2], gap="large")

with input_col:
    st.subheader("입력 캔버스")
    canvas = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=22,
        stroke_color="#111827",
        background_color="#ffffff",
        width=280,
        height=280,
        drawing_mode="freedraw",
        key="digit_canvas",
    )
    run_clicked = st.button("예측 실행", use_container_width=True)

with preview_col:
    st.subheader("전처리 이미지")
    preview_slot = st.empty()

with result_col:
    st.subheader("모델 추론 결과")
    result_slot = st.empty()
    chart_slot = st.empty()

if canvas.image_data is not None and not is_blank_canvas(canvas.image_data):
    try:
        input_tensor, preview = preprocess_canvas_image(canvas.image_data)
        preview_slot.image(preview.resize((140, 140), Image.Resampling.NEAREST), width=140)
    except ValueError:
        input_tensor, preview = None, None
else:
    input_tensor, preview = None, None
    preview_slot.info("대기 중")

if run_clicked:
    if input_tensor is None or preview is None:
        result_slot.warning("숫자를 먼저 그려주세요.")
    else:
        probabilities = run_prediction(session, input_tensor)
        label, confidence = top_prediction(probabilities)
        save_preview_image(preview, SAVED_DIR, label, confidence)

        result_slot.metric("예측 숫자", label, f"{confidence:.1%}")
        chart_slot.bar_chart(probability_frame(probabilities), height=260)

st.divider()
st.subheader("이미지 저장소")

samples = saved_samples()
if not samples:
    st.info("저장된 이미지가 없습니다.")
else:
    columns = st.columns(5)
    for index, image_path in enumerate(samples[:10]):
        with columns[index % 5]:
            st.image(str(image_path), caption=image_path.stem, width=100)
