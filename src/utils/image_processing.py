"""Image processing utilities for dermatological image analysis."""

import io

import numpy as np
from PIL import Image

# Accepted image formats
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


def allowed_file(filename: str) -> bool:
    """Check if the file has an allowed extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def load_image(file_bytes: bytes) -> Image.Image:
    """Load an image from bytes."""
    return Image.open(io.BytesIO(file_bytes)).convert("RGB")


def extract_features(image: Image.Image) -> dict:
    """Extract visual features from a skin lesion image.

    Analyzes the image for color distribution, shape characteristics,
    texture, and size-related features used in triage scoring.
    """
    img_array = np.array(image)

    features = {}
    features["dimensions"] = {"width": image.width, "height": image.height}

    # Color analysis
    features["color"] = _analyze_color(img_array)

    # Shape analysis
    features["shape"] = _analyze_shape(img_array)

    # Texture analysis
    features["texture"] = _analyze_texture(img_array)

    return features


def _analyze_color(img_array: np.ndarray) -> dict:
    """Analyze color distribution of the image."""
    r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]

    color_info = {
        "mean_rgb": {
            "r": float(np.mean(r)),
            "g": float(np.mean(g)),
            "b": float(np.mean(b)),
        },
        "std_rgb": {
            "r": float(np.std(r)),
            "g": float(np.std(g)),
            "b": float(np.std(b)),
        },
    }

    # Determine dominant color characteristics
    mean_r, mean_g, mean_b = color_info["mean_rgb"].values()
    color_info["is_dark"] = (mean_r + mean_g + mean_b) / 3 < 100
    color_info["is_red_dominant"] = mean_r > mean_g * 1.3 and mean_r > mean_b * 1.3
    color_info["is_brown"] = mean_r > mean_g > mean_b and mean_r < 180

    # Color variance (high variance may indicate multi-colored lesion)
    total_std = (
        color_info["std_rgb"]["r"]
        + color_info["std_rgb"]["g"]
        + color_info["std_rgb"]["b"]
    )
    color_info["color_variance"] = "high" if total_std > 120 else (
        "moderate" if total_std > 60 else "low"
    )

    return color_info


def _analyze_shape(img_array: np.ndarray) -> dict:
    """Analyze shape characteristics of the image."""
    gray = np.mean(img_array, axis=2)

    # Simple threshold-based segmentation
    threshold = np.mean(gray) - np.std(gray) * 0.5
    mask = gray < threshold

    shape_info = {
        "lesion_area_ratio": float(np.sum(mask) / mask.size),
    }

    # Estimate symmetry by comparing left/right halves
    mid = mask.shape[1] // 2
    left = mask[:, :mid]
    right = np.fliplr(mask[:, mid: mid + left.shape[1]])
    if left.shape == right.shape and left.size > 0:
        symmetry = float(np.sum(left == right) / left.size)
    else:
        symmetry = 0.5
    shape_info["symmetry_score"] = symmetry

    # Estimate border regularity
    shape_info["border_regularity"] = _estimate_border_regularity(mask)

    return shape_info


def _estimate_border_regularity(mask: np.ndarray) -> str:
    """Estimate how regular the border of a lesion is."""
    # Simple edge detection via difference between mask and eroded mask
    eroded = np.zeros_like(mask)
    if mask.shape[0] > 2 and mask.shape[1] > 2:
        eroded[1:-1, 1:-1] = (
            mask[:-2, 1:-1] & mask[2:, 1:-1]
            & mask[1:-1, :-2] & mask[1:-1, 2:]
        )
    border = mask ^ eroded
    border_pixels = np.sum(border)
    area_pixels = max(np.sum(mask), 1)

    # Compactness ratio: higher means less regular border
    ratio = border_pixels / np.sqrt(area_pixels)
    if ratio > 15:
        return "irregular"
    elif ratio > 8:
        return "somewhat_irregular"
    return "regular"


def _analyze_texture(img_array: np.ndarray) -> dict:
    """Analyze texture characteristics."""
    gray = np.mean(img_array, axis=2)

    # Local variance as texture measure
    h, w = gray.shape
    if h > 4 and w > 4:
        # Compute local variance in 4x4 blocks
        block_size = 4
        trimmed_h = (h // block_size) * block_size
        trimmed_w = (w // block_size) * block_size
        trimmed = gray[:trimmed_h, :trimmed_w]
        blocks = trimmed.reshape(trimmed_h // block_size, block_size,
                                 trimmed_w // block_size, block_size)
        local_var = np.var(blocks, axis=(1, 3))
        mean_local_var = float(np.mean(local_var))
    else:
        mean_local_var = float(np.var(gray))

    texture_info = {
        "mean_local_variance": mean_local_var,
    }

    if mean_local_var > 1500:
        texture_info["texture_type"] = "rough"
    elif mean_local_var > 500:
        texture_info["texture_type"] = "moderate"
    else:
        texture_info["texture_type"] = "smooth"

    return texture_info
