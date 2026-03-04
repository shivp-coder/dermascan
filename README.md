# DermScan AI

Dermatological triage assistant that analyzes skin lesion images and provides structured triage results including condition matches, severity scoring, and next-step recommendations.

**This is not a medical device or diagnostic tool.** All results are for informational triage purposes only. Always consult a qualified healthcare professional.

## Features

- **Image analysis** — Extracts color, shape, symmetry, border, and texture features from uploaded skin images
- **ABCDE assessment** — Applies the ABCDE rule (Asymmetry, Border, Color, Diameter, Evolution) for pigmented lesion evaluation
- **Condition matching** — Scores against 12 common dermatological conditions and returns top 3 matches with confidence percentages
- **Severity scoring** — 5-level severity scale (Very Mild to Urgent) with tailored recommendations
- **Web interface** — Drag-and-drop image upload with real-time results display

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000` in your browser.

## API

### `GET /api/health`
Returns service health status.

### `POST /api/analyze`
Upload a skin image for triage analysis.

**Request:** `multipart/form-data` with field `image` (PNG, JPG, JPEG, BMP, or TIFF, max 10MB)

**Response:**
```json
{
  "top_conditions": [
    {"condition": "...", "confidence_percent": 45.2, "description": "..."},
    {"condition": "...", "confidence_percent": 30.1, "description": "..."},
    {"condition": "...", "confidence_percent": 24.7, "description": "..."}
  ],
  "severity_score": 3,
  "severity_label": "Moderate",
  "next_steps": ["..."],
  "doctor_recommendation": "...",
  "abcde_assessment": {
    "asymmetry": "normal",
    "border": "normal",
    "color": "mild",
    "diameter": "normal",
    "evolution": "unable_to_assess_from_single_image"
  },
  "disclaimer": "..."
}
```

## Testing

```bash
pytest tests/ -v
```

## Project Structure

```
dermascan/
├── app.py                          # Application entry point
├── src/
│   ├── api/routes.py               # Flask routes and API endpoints
│   ├── engine/triage.py            # Core triage analysis engine
│   ├── models/
│   │   ├── analysis.py             # Result data models
│   │   └── conditions.py           # Condition definitions database
│   └── utils/image_processing.py   # Image feature extraction
├── templates/index.html            # Web UI
├── static/
│   ├── style.css
│   └── app.js
├── tests/
│   ├── test_api.py
│   ├── test_image_processing.py
│   └── test_triage.py
└── requirements.txt
```

## Disclaimer

DermScan AI is for **informational triage purposes only**. It does not provide medical diagnoses. Results should never replace professional medical evaluation. Always consult a qualified healthcare professional for skin concerns.
