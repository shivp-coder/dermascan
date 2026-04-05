# DermScan AI

An AI-powered dermatological triage SaaS built on Claude Opus 4.6 vision.
Upload a photo, have a multi-turn conversation with the AI, browse a full
condition library, and escalate to verified dermatologists for serious cases.

> **Not a medical device.** DermScan AI is for informational triage only.
> All results must be reviewed by a qualified healthcare professional.

## Features

- **Claude Opus 4.6 vision analysis** — real image understanding, not toy feature extraction
- **Multi-turn conversational triage** — the AI asks follow-up questions and builds on your answers
- **2–3 options when uncertain** — with confidence scores, each grounded in the ABCDE rule and morphology
- **Disease knowledge base** — 12 common conditions with plain-language info (appearance, causes, self-care, when to see a doctor)
- **Expert chat** — direct consultations with verified dermatologists for Expert+ subscribers, with urgent escalation
- **Tiered SaaS plans** — Free (5 scans/mo), Pro ($19, 100 scans/mo), Expert+ ($49, unlimited + expert chat)
- **User accounts** — signup/login, conversation history, usage tracking
- **Modern dashboard** — dark-mode SPA with landing page, pricing, library, chat UI

## Architecture

```
dermascan/
├── app.py                          # Entry point
├── src/
│   ├── config.py                   # Configuration and plan definitions
│   ├── db.py                       # SQLite schema and connection management
│   ├── auth.py                     # Session-based auth (signup/login/plans)
│   ├── api/
│   │   ├── routes.py               # Flask app factory, blueprint registration
│   │   ├── analysis.py             # Multi-turn vision analysis endpoints
│   │   ├── expert.py               # Expert chat endpoints
│   │   └── conditions.py           # Knowledge base endpoints
│   ├── engine/
│   │   ├── claude_client.py        # Anthropic SDK wrapper with vision
│   │   └── prompts.py              # Triage system prompts (schema enforced)
│   └── models/
│       └── conditions.py           # Detailed condition knowledge base
├── templates/index.html            # SPA shell
├── static/
│   ├── css/style.css               # Modern dark theme
│   └── js/
│       ├── api.js                  # Fetch wrapper
│       ├── views.js                # View renderers
│       └── app.js                  # SPA controller and routing
└── tests/                          # 36 tests, all passing
```

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
python app.py
```

Open `http://localhost:5000`.

## Environment

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Required for AI analysis — get one from console.anthropic.com |
| `SECRET_KEY` | Flask session secret — use a long random string in production |
| `DATABASE_PATH` | SQLite DB path (default: `./dermascan.db`) |

## API Overview

### Auth
- `POST /api/auth/signup` — `{email, password, name}`
- `POST /api/auth/login` — `{email, password}`
- `POST /api/auth/logout`
- `GET  /api/auth/me` — current user
- `POST /api/auth/plan` — `{plan: free|pro|expert}`

### Analysis (auth required)
- `POST /api/analysis/start` — multipart with `image` + optional `text`, creates a new conversation
- `POST /api/analysis/conversations/<id>/message` — follow-up (JSON or multipart with image)
- `GET  /api/analysis/conversations` — list history
- `GET  /api/analysis/conversations/<id>` — conversation + messages

### Expert chat (Expert+ required)
- `GET  /api/expert/chats`
- `POST /api/expert/chats` — `{subject, urgency, conversation_id?}`
- `GET  /api/expert/chats/<id>`
- `POST /api/expert/chats/<id>/message` — `{content}`

### Conditions library (public)
- `GET  /api/conditions` — all conditions
- `GET  /api/conditions/<key>` — specific condition

## Triage Response Schema

Every AI turn returns structured JSON:

```json
{
  "message": "Conversational reply to the user",
  "analysis": {
    "top_conditions": [
      {"name": "...", "confidence_percent": 0-85, "why": "..."}
    ],
    "severity_score": 1-5,
    "severity_label": "Very Mild|Mild|Moderate|Significant|Urgent",
    "abcde": {
      "asymmetry": "normal|mild|concerning|not_applicable",
      "border":    "normal|mild|concerning|not_applicable",
      "color":     "normal|mild|concerning|not_applicable",
      "diameter":  "normal|mild|concerning|not_applicable",
      "evolution": "normal|mild|concerning|unknown"
    },
    "next_steps": ["..."],
    "doctor_recommendation": "...",
    "needs_urgent_care": true|false
  },
  "follow_up_questions": ["...", "..."],
  "escalate_to_expert": true|false,
  "disclaimer": "..."
}
```

## Safety Rules (enforced in the system prompt)

- Never says "you have X" — uses "this appears consistent with"
- Always recommends consulting a healthcare professional
- Escalates melanoma-concerning features to urgent care (within 24-48 hours)
- Caps confidence at 85% to avoid false certainty
- Returns 2-3 options with follow-up questions when uncertain

## Testing

```bash
pytest tests/ -v
```

36 tests covering auth, plan management, conditions API, expert chat gating,
Claude engine JSON parsing, and page rendering.

## Disclaimer

DermScan AI is an informational triage tool. It does not provide medical
diagnoses. Results should never replace professional medical evaluation.
Always consult a qualified healthcare professional for skin concerns.
