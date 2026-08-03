# Confidence & Approval Gates (M6)

## 1. Confidence Scoring
Every AI-generated claim carries a confidence score 0.0–1.0:
- `>= 0.90` → auto-accept for non-regulated content
- `0.70–0.89` → review queue (admin)
- `< 0.70` → reject, fall back to deterministic data or manual draft

## 2. Approval Workflows
- **Content publish**: draft → AI draft (confidence >= 0.90) → auto-publish with `ai_generated=true` label; else → admin review.
- **Spec extraction**: confidence < 0.85 → human verification of the extracted fields.
- **Affiliate destination change**: ALWAYS requires admin approval (revenue-affecting).
- **Mass publish / bulk mutations**: requires explicit admin token + dry-run mode.

## 3. Circuit Breakers
- Model error rate > 20% over 10 minutes → disable model, fall back to deterministic provider.
- Cost ceiling reached → all AI calls fail closed, manual fallback only.
