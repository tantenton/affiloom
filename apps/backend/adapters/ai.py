"""Provider-abstracted SEO content generation.

AI generation must remain opt-in. Without credentials the null adapter raises a
clear error so callers can keep the feature disabled rather than silently
calling a vendor. A deterministic adapter is available for local drafting and
tests.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ContentDraft:
    title: str
    excerpt: str
    body_md: str
    meta_title: str
    meta_description: str
    canonical_path: str
    language: str = "id-ID"


class ContentAIAdapter(ABC):
    @property
    @abstractmethod
    def provider(self) -> str: ...

    @property
    @abstractmethod
    def model(self) -> str: ...

    @abstractmethod
    async def generate_draft(self, prompt: str) -> ContentDraft: ...


class NullContentAIAdapter(ContentAIAdapter):
    """Disabled adapter when no provider credentials are configured."""

    @property
    def provider(self) -> str:
        return "disabled"

    @property
    def model(self) -> str:
        return "disabled"

    async def generate_draft(self, prompt: str) -> ContentDraft:
        raise RuntimeError("AI content generation is disabled without credentials")


class DeterministicContentAIAdapter(ContentAIAdapter):
    """Deterministic fallback used for tests and local development."""

    def __init__(self, provider: str = "deterministic", model: str = "seed-1") -> None:
        self._provider = provider
        self._model = model

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def model(self) -> str:
        return self._model

    async def generate_draft(self, prompt: str) -> ContentDraft:
        title = prompt.strip()[:72] or "Draf SEO Affiloom"
        return ContentDraft(
            title=title,
            excerpt=f"Draf deterministik untuk {title}.",
            body_md=(
                f"# {title}\n\n"
                "Draf ini dibuat secara deterministik untuk menjaga konsistensi "
                "konten SEO selama milestone pengembangan.\n"
            ),
            meta_title=title,
            meta_description=f"Draf SEO deterministik untuk {title}.",
            canonical_path="/artikel/draft-seo",
        )


async def get_content_ai_adapter(
    *,
    provider: str | None = None,
    model: str | None = None,
    enabled: bool = False,
) -> ContentAIAdapter:
    if not enabled:
        return NullContentAIAdapter()
    return DeterministicContentAIAdapter(
        provider=provider or "deterministic",
        model=model or "seed-1",
    )


__all__ = [
    "ContentAIAdapter",
    "ContentDraft",
    "DeterministicContentAIAdapter",
    "NullContentAIAdapter",
    "get_content_ai_adapter",
]
