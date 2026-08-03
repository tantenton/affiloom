# Evaluation Strategy (M6)

## 1. Purpose
Measure whether AI workflows produce accurate, safe, and useful output before promoting them to production. No AI feature is enabled without passing evaluation.

## 2. Evaluation Sets
- **Accuracy set**: 50 hand-curated product/spec/price items with known ground truth.
- **Safety set**: 20 adversarial prompts covering prompt injection, PII leakage, fabricated claims, and regulated topics.
- **Freshness set**: 20 items where price/stock changed between syncs; model must not invent stale values.

## 3. Metrics
- **Extraction accuracy**: exact match rate on structured fields (category, price, spec).
- **Hallucination rate**: fraction of generated claims lacking source evidence.
- **Gate precision**: how often low-confidence outputs are correctly flagged for review.
- **Cost per task**: token spend per workflow; tracked against ceiling.

## 4. Promotion Gate
A workflow version may promote to production only when:
- Accuracy >= 90% on the accuracy set
- Hallucination rate <= 5%
- Safety set: zero critical failures
- Cost within budget for 3 consecutive runs

## 5. Regression Tracking
Evaluation results are committed to `docs/ai/EVALUATIONS/` after each run, so model/prompt changes never silently degrade quality.
