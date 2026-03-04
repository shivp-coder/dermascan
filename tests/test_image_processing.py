"""Tests for image processing utilities."""

import numpy as np
from PIL import Image

from src.utils.image_processing import (
    allowed_file,
    extract_features,
    load_image,
)


class TestAllowedFile:
    def test_valid_extensions(self):
        assert allowed_file("photo.png")
        assert allowed_file("photo.jpg")
        assert allowed_file("photo.jpeg")
        assert allowed_file("photo.bmp")
        assert allowed_file("photo.tiff")

    def test_invalid_extensions(self):
        assert not allowed_file("document.pdf")
        assert not allowed_file("script.py")
        assert not allowed_file("archive.zip")

    def test_no_extension(self):
        assert not allowed_file("noextension")

    def test_case_insensitive(self):
        assert allowed_file("photo.PNG")
        assert allowed_file("photo.JPG")


class TestLoadImage:
    def test_loads_from_bytes(self):
        img = Image.new("RGB", (100, 100), color=(255, 0, 0))
        import io
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        loaded = load_image(buf.getvalue())
        assert loaded.mode == "RGB"
        assert loaded.size == (100, 100)


class TestExtractFeatures:
    def _make_test_image(self, width=100, height=100, color=(128, 100, 80)):
        return Image.new("RGB", (width, height), color=color)

    def test_returns_dict_with_expected_keys(self):
        img = self._make_test_image()
        features = extract_features(img)
        assert "dimensions" in features
        assert "color" in features
        assert "shape" in features
        assert "texture" in features

    def test_dimensions_correct(self):
        img = self._make_test_image(200, 150)
        features = extract_features(img)
        assert features["dimensions"]["width"] == 200
        assert features["dimensions"]["height"] == 150

    def test_color_analysis_has_expected_keys(self):
        img = self._make_test_image()
        features = extract_features(img)
        color = features["color"]
        assert "mean_rgb" in color
        assert "is_dark" in color
        assert "is_red_dominant" in color
        assert "color_variance" in color

    def test_dark_image_detected(self):
        img = self._make_test_image(color=(30, 20, 20))
        features = extract_features(img)
        assert features["color"]["is_dark"]

    def test_bright_image_not_dark(self):
        img = self._make_test_image(color=(200, 200, 200))
        features = extract_features(img)
        assert not features["color"]["is_dark"]

    def test_shape_has_symmetry(self):
        img = self._make_test_image()
        features = extract_features(img)
        assert "symmetry_score" in features["shape"]

    def test_texture_has_type(self):
        img = self._make_test_image()
        features = extract_features(img)
        assert "texture_type" in features["texture"]
