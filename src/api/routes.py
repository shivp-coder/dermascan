"""Flask app factory — registers blueprints and page routes."""

import os

from flask import Flask, jsonify, render_template, send_from_directory

from src import config, db
from src.api.analysis import analysis_bp
from src.api.conditions import conditions_bp
from src.api.expert import expert_bp
from src.auth import auth_bp


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(
            os.path.dirname(__file__), "..", "..", "templates"
        ),
        static_folder=os.path.join(
            os.path.dirname(__file__), "..", "..", "static"
        ),
    )
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_IMAGE_SIZE

    db.init_app(app)

    # Initialize schema on startup
    try:
        db.init_db()
    except Exception as e:
        app.logger.warning(f"DB init warning: {e}")

    # API blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(expert_bp)
    app.register_blueprint(conditions_bp)

    # Health
    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "dermascan",
            "claude_configured": bool(config.ANTHROPIC_API_KEY),
        })

    # Plans endpoint
    @app.get("/api/plans")
    def plans():
        return jsonify({"plans": config.PLANS})

    # Pages — all SPA-style, render the same shell
    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/login")
    def login_page():
        return render_template("index.html")

    @app.get("/signup")
    def signup_page():
        return render_template("index.html")

    @app.get("/dashboard")
    def dashboard():
        return render_template("index.html")

    @app.get("/conditions")
    def conditions_page():
        return render_template("index.html")

    @app.get("/experts")
    def experts_page():
        return render_template("index.html")

    @app.get("/pricing")
    def pricing_page():
        return render_template("index.html")

    return app
