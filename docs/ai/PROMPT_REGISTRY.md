# Prompt Registry (M6)

## Overview
All LLM prompts used in Affiloom workflows are version-controlled here. Production only uses pinned prompt versions. Prompt changes go through review and evaluation before promotion.

## Prompt Catalog

| ID | Version | Task | Model Target | Status |
|----|---------|------|-------------|--------|
| PRD-001 | v1.0 | Product normalization | GPT-4o / Llama-3 | Active |
| SUM-001 | v1.0 | Review summary synthesis | GPT-4o | Active |
| GDE-001 | v1.0 | Buying guide first draft | GPT-4o | Active |
| CMP-001 | v1.0 | Comparison narrative | GPT-4o | Active |
| CAT-001 | v1.0 | Category mapping | GPT-4o-mini | Active |

## Rules
- All prompts must include provenance instructions: model must cite its sources.
- Prompts for regulated domains must include a safety prefix.
- No prompt may instruct the model to fabricate specifications, prices, or test results.
- Prompt injection defense: user-provided text is always delimited with XML tags.
