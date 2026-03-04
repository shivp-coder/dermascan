"""Flask API routes for DermScan."""

import os

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
)

from src.engine.triage import analyze
from src.utils.image_processing import (
    MAX_IMAGE_SIZE,
    allowed_file,
    extract_features,
    load_image,
)


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder=os.path.join(
            os.path.dirname(__file__), "..", "..", "templates"
        ),
        static_folder=os.path.join(
            os.path.dirname(__file__), "..", "..", "static"
        ),
    )
    app.config["MAX_CONTENT_LENGTH"] = MAX_IMAGE_SIZE

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "dermascan"})

    @app.route("/api/analyze", methods=["POST"])
    def analyze_image():
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({
                "error": (
                    "Invalid file type. Accepted formats: "
                    "PNG, JPG, JPEG, BMP, TIFF"
                )
            }), 400

        try:
            file_bytes = file.read()
            if len(file_bytes) > MAX_IMAGE_SIZE:
                return jsonify({"error": "File too large. Max 10MB."}), 400

            image = load_image(file_bytes)
            features = extract_features(image)
            result = analyze(features)

            return jsonify(result.to_dict())

        except Exception:
            return jsonify({
                "error": "Failed to process image. Please try another image."
            }), 500

    return app
