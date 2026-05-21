from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageOps


def is_blank_canvas(canvas_data: np.ndarray | None) -> bool:
    if canvas_data is None:
        return True

    array = np.asarray(canvas_data)
    if array.size == 0:
        return True

    if array.ndim == 3 and array.shape[2] == 4:
        alpha = array[..., 3]
        if int(alpha.max()) == 0:
            return True
        rgb = array[..., :3]
    elif array.ndim == 3:
        rgb = array[..., :3]
    else:
        rgb = array

    return bool(rgb.max() < 5 or rgb.min() > 250)


def _to_grayscale_on_white(canvas_data: np.ndarray) -> Image.Image:
    array = np.asarray(canvas_data).astype(np.uint8)
    image = Image.fromarray(array)

    if image.mode == "RGBA":
        background = Image.new("RGBA", image.size, "white")
        image = Image.alpha_composite(background, image).convert("L")
    else:
        image = image.convert("L")

    return image


def _center_digit(image: Image.Image, threshold: int = 20) -> Image.Image:
    digit = ImageOps.invert(image)
    mask = np.asarray(digit) > threshold

    if not mask.any():
        return Image.new("L", (28, 28), 0)

    rows, cols = np.where(mask)
    left, right = int(cols.min()), int(cols.max()) + 1
    upper, lower = int(rows.min()), int(rows.max()) + 1
    cropped = digit.crop((left, upper, right, lower))

    side = max(cropped.size)
    padding = max(6, int(side * 0.25))
    square_side = side + padding * 2
    square = Image.new("L", (square_side, square_side), 0)
    offset = ((square_side - cropped.width) // 2, (square_side - cropped.height) // 2)
    square.paste(cropped, offset)
    return square.resize((28, 28), Image.Resampling.LANCZOS)


def preprocess_canvas_image(canvas_data: np.ndarray) -> tuple[np.ndarray, Image.Image]:
    if is_blank_canvas(canvas_data):
        raise ValueError("Canvas is blank. Draw a digit before running inference.")

    grayscale = _to_grayscale_on_white(canvas_data)
    preview = _center_digit(grayscale)
    normalized = np.asarray(preview, dtype=np.float32) / 255.0
    tensor = normalized.reshape(1, 1, 28, 28).astype(np.float32)
    return tensor, preview


def save_preview_image(preview: Image.Image, output_dir: Path, label: int, confidence: float) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    index = len(list(output_dir.glob("digit_*.png"))) + 1
    filename = f"digit_{index:03d}_pred_{label}_conf_{confidence:.2f}.png"
    path = output_dir / filename
    preview.save(path)
    return path
