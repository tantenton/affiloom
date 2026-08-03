# Prompt Injection Defense (M6)

## 1. Threat Model
User-generated and third-party content (product titles, descriptions, reviews, article bodies) can contain instructions aimed at overriding the model's system prompt.

## 2. Defenses
- **Delimitation**: All external content is wrapped in XML tags (`<user_content>...</user_content>`) before insertion into prompts.
- **Instruction lock**: System prompt states that content inside user_content is data, never instructions.
- **Output schema enforcement**: Model responses are parsed with Pydantic; unexpected keys are rejected.
- **Egress validation**: Extracted URLs are validated against an allowlist of known merchant domains before being stored.
- **Never trust model for auth/security decisions**: RBAC and token checks are enforced in code, not in prompts.
- **Log redaction**: Secrets, tokens, and API keys are redacted before logs are stored.

## 3. Testing
The safety evaluation set (see EVALUATION_STRATEGY.md) includes adversarial prompts that attempt:
- "Ignore previous instructions"
- Fake source injection
- URL exfiltration
- Claiming the assistant is a merchant support bot
