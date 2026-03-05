/**
 * DermScan Prompt Evaluation Script
 *
 * Tests the AI prompt against known dermatology images.
 * Place test images in ./test-images/ with filenames like:
 *   eczema_01.jpg, melanoma_02.jpg, acne_03.jpg
 *
 * The expected condition is parsed from the filename prefix.
 *
 * Usage: node eval.js
 *
 * Requires: ANTHROPIC_API_KEY in .env
 */

// TODO: Implement with these steps:
// 1. Load all images from test-images/
// 2. Send each to Claude with the system prompt
// 3. Compare primary condition to expected (from filename)
// 4. Track: accuracy %, avg confidence, severity distribution
// 5. Flag: any melanoma/cancer missed (critical failure)
// 6. Output: results table + overall score
//
// Test image sources (free, open-source):
// - ISIC Archive: https://www.isic-archive.com/
// - DermNet NZ: https://dermnetnz.org/image-library
// - Fitzpatrick17k: https://github.com/mattgroh/fitzpatrick17k
