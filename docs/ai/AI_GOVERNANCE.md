# AI Governance & Control Plane (M6)

## 1. Objective
Establish safe, deterministic, and bounded AI-operated workflows for content drafting, review summarization, and product normalization while preventing hallucination, prompt injection, and unverified publishing.

## 2. Guardrails & Gates
The following actions REQUIRE human approval or fail closed:
- Low confidence score (< 0.85) on spec extraction or category mapping.
- Regulated products (medical, financial, children, ingestibles).
- Sponsored content / affiliate destination changes.
- Mass publishing or bulk database mutations.
- Secret/auth configuration changes.

## 3. Architecture
- **Provider Abstraction**: Unified interface for LLM endpoints (OpenAI, Anthropic, local GGUF via llama.cpp).
- **Structured Outputs**: Pydantic schema enforcement on all model responses.
- **Cost Ceiling**: Daily and monthly token/cost limits with circuit breakers.
- **Prompt Versioning**: Version-controlled prompts stored in repository.
