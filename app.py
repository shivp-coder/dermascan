"""DermScan AI — Dermatological Triage Assistant.

Entry point for running the Flask application.
"""

from src.api.routes import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
