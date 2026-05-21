import numpy as np
from PIL import Image, ImageDraw

from image_processing import is_blank_canvas, preprocess_canvas_image


def test_blank_canvas_detects_transparent_and_white_images():
    transparent = np.zeros((120, 120, 4), dtype=np.uint8)
    white = np.full((120, 120, 4), 255, dtype=np.uint8)

    assert is_blank_canvas(transparent)
    assert is_blank_canvas(white)


def test_preprocess_canvas_image_returns_mnist_tensor_and_preview():
    image = Image.new("RGBA", (280, 280), "white")
    draw = ImageDraw.Draw(image)
    draw.line([(130, 40), (130, 230)], fill="black", width=34)
    draw.line([(92, 78), (130, 40), (168, 78)], fill="black", width=30)

    tensor, preview = preprocess_canvas_image(np.array(image))

    assert tensor.shape == (1, 1, 28, 28)
    assert tensor.dtype == np.float32
    assert 0.0 <= float(tensor.min()) <= float(tensor.max()) <= 1.0
    assert float(tensor.max()) > 0.8
    assert preview.size == (28, 28)
    assert preview.mode == "L"
