# DermScan — Product Requirements Document

## Vision
The "Cal AI" of skin health. One photo, instant AI assessment, clear next steps.

## Target User
- 18-35 year olds who find something on their skin and want instant answers
- Don't have a dermatologist or can't get an appointment for weeks
- Health-conscious but not hypochondriacs
- Comfortable with AI tools

## Core User Flow
1. Open app → tap "Take Photo" or "Upload"
2. Snap photo of skin concern
3. Select body location (optional but improves accuracy)
4. Tap "Analyze"
5. See results: top 3 possible conditions, severity score, doctor recommendation, next steps
6. Scan saved to journal automatically

## Feature Requirements

### P0 — MVP (Week 1-2)
- Camera capture + file upload
- AI skin analysis via Claude vision API
- Structured results display (condition, severity, confidence, next steps)
- "See a doctor?" recommendation
- Scan history / journal
- Body location selector
- Medical disclaimer on every result
- Mobile-responsive (works on phone browser)

### P1 — Post-MVP (Week 3-4)
- Body map visualization of all scans
- Photo comparison (same area over time, side by side)
- Scan history persistence (localStorage → eventually cloud)
- Onboarding flow (3 screens explaining the app)
- Freemium paywall: 3 free scans/month, $4.99/month unlimited
- Share results (export as image or PDF)

### P2 — Growth (Month 2-3)
- React Native mobile app (iOS + Android)
- User accounts + cloud sync
- Teledermatology: "Talk to a real dermatologist" button (referral partnership)
- Notification reminders: "Time to re-check that mole"
- Skin health score (aggregate of all scans)
- Community features (anonymized — "others with similar concerns")

### P3 — Scale (Month 4+)
- Custom fine-tuned model on dermatology datasets
- Insurance/HSA payment integration for teledermatology
- B2B: license to clinics for patient pre-screening
- International: multi-language support (Hindi, Spanish, Mandarin priority)
- Hardware: dedicated skin scanning attachment with controlled lighting

## Monetization
- Freemium: 3 scans/month free
- Pro: $4.99/month or $29.99/year (unlimited scans, full history, photo comparison)
- Teledermatology referral: $35-75 per consultation, 20-30% revenue share
- Future: B2B licensing to clinics

## Regulatory Notes
- Position as "informational/educational" NOT "diagnostic"
- Never use language like "you have X" — always "this appears consistent with"
- Prominent disclaimer on every result screen
- No FDA clearance needed if we don't claim to diagnose
- HIPAA: encrypt all stored images, minimize PII collection
- Terms of service must include medical disclaimer

## Success Metrics
- Week 1: 100 beta users at Berkeley
- Week 4: 1,000 users, 50%+ Day 7 retention
- Month 2: 5,000 users, first paid subscribers
- Month 3: $5K MRR, apply to YC

## Competitive Landscape
- Skinive, Cureskin, AI Dermatologist — exist but none have Cal AI-level UX/virality
- Most AI skin tools are B2B (for beauty brands to sell products)
- Nobody owns the consumer "should I worry about this?" use case
- Closest analog: Cal AI's approach but applied to skin health instead of calories
