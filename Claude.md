# DermScan — AI Skin Health Analysis App

## What is this?
A consumer mobile-first web app that lets users photograph skin concerns
and get instant AI-powered assessments. Think "Cal AI but for skin health."

## Tech Stack
- React (CRA) + Tailwind CSS for web MVP
- Claude API (claude-sonnet-4-20250514) with vision for skin analysis
- No backend needed for MVP — API calls from client
- AsyncStorage or localStorage for scan history persistence

## Architecture
- Single page app with screen-based navigation (home, preview, result, history, bodymap)
- Image captured via camera or file upload → sent as base64 to Claude vision API
- AI returns structured JSON with condition assessment, severity, next steps
- All scan history stored locally on device

## Key Files
- `PROMPT.md` — The system prompt for skin analysis. This is the core IP. Edit carefully.
- `PRD.md` — Full product requirements. Read before building any new feature.
- `src/components/DermScan.jsx` — Main app component
- `src/services/analyzeImage.js` — Claude API integration
- `tests/prompt-eval/` — Prompt accuracy testing

## Commands
- `npm start` — Run dev server
- `npm test` — Run tests
- `npm run build` — Production build

## Rules
1. NEVER claim to diagnose. Always use "appears consistent with" or "may resemble"
2. Every response MUST include a medical disclaimer
3. Severity 4-5 MUST always recommend seeing a doctor
4. Test across diverse skin tones — this is non-negotiable
5. Keep the UI clean, medical-feeling (blues/whites), trustworthy
6. Mobile-first — everything must work on a phone screen
7. API key is in .env, never commit it

## Current Status
- [x] Core scan flow (capture → analyze → results)
- [x] Severity rating system
- [x] Skin journal / history
- [x] Body map
- [ ] Scan history persistence (localStorage)
- [ ] Onboarding flow
- [ ] Paywall (3 free scans, then subscription)
- [ ] Photo comparison (same body part over time)
- [ ] Push notification reminders to re-scan
- [ ] Teledermatology referral integration
- [ ] Dark mode
- [ ] React Native port

## When adding features
1. Read PRD.md first
2. Keep components small and focused
3. All AI interactions go through src/services/analyzeImage.js
4. Test with real skin images before marking complete
5. Ensure all new UI works on 375px width (iPhone SE)
