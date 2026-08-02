"""Article generation service — M3-001.

Orchestrates the AI adapter to produce buying-guide articles from product data.
Uses a deterministic fallback when credentials are absent so the pipeline stays
testable even when the real provider is offline or disabled.
"""

from __future__ import annotations

from datetime import datetime, timezone

from adapters.ai import (
    ContentAIAdapter,
    ContentDraft,
    NullContentAIAdapter,
)
from adapters.provider import DeterministicDemoAdapter
from schemas.content import ArticleCreate


class GenerationService:
    """Business logic for generating SEO-optimised buying guides."""

    def __init__(
        self,
        ai_adapter: ContentAIAdapter,
        catalog: DeterministicDemoAdapter | None = None,
    ) -> None:
        self._ai = ai_adapter
        self._catalog = catalog

    @property
    def enabled(self) -> bool:
        return not isinstance(self._ai, NullContentAIAdapter)

    async def draft_from_products(
        self,
        keyword: str,
        product_ids: list[str],
    ) -> ContentDraft:
        """Generate a buying-guide draft centred on *keyword* and its related products.

        When ``product_ids`` are provided the prompt is augmented with actual
        product titles so the draft is contextual. Otherwise the draft stays
        generic (keyword-only).
        """
        product_titles = []
        if self._catalog and product_ids:
            for pid in product_ids:
                item = await self._catalog.detail(pid)
                if item is not None:
                    product_titles.append(f"- *{item.title}* (Rp{item.price:,.0f})")
        product_block = "\n".join(product_titles) if product_titles else (
            "_Tidak ada produk terkait._"
        )

        prompt = (
            f"Buat artikel panduan belanja SEO bahasa Indonesia untuk kata kunci "
            f"\"{keyword}\".\n\n"
            "Gunakan gaya ramah, informatif, dan persuasif. Tulis dalam bahasa "
            "Indonesia formal namun ringan.\n\n"
            "## Produk yang direkomendasikan\n"
            f"{product_block}\n\n"
            "Format:\n"
            "# {Judul}\n"
            "{Pendahuluan — 2-3 paragraf}\n"
            "## Tips memilih {kata kunci}\n"
            "{poin-poin penting}\n"
            "## Rekomendasi {kata kunci} terbaik\n"
            "{ulasan setiap produk}\n"
            "## Kesimpulan\n"
            "Tutup dengan ajakan bertindak yang relevan."
        )
        draft = await self._ai.generate_draft(prompt)
        # Use keyword in the canonical path so it's SEO-friendly.
        slug = keyword.lower().replace(" ", "-")[:80]
        canonical = f"/artikel/{slug}"
        return ContentDraft(
            title=draft.title,
            excerpt=draft.excerpt,
            body_md=draft.body_md,
            meta_title=draft.meta_title,
            meta_description=draft.meta_description,
            canonical_path=canonical,
        )

    async def publish_draft(
        self,
        draft: ContentDraft,
        db_session,
    ) -> ArticleCreate:
        """Persist a draft to the database as a published article.

        Returns an ArticleCreate schema ready for the repo layer.
        """
        slug = draft.canonical_path.strip("/").split("/")[-1]
        return ArticleCreate(
            slug=slug,
            title=draft.title,
            excerpt=draft.excerpt,
            body_md=draft.body_md,
            meta_title=draft.meta_title,
            meta_description=draft.meta_description,
            canonical_path=draft.canonical_path,
            language=draft.language,
            status="published",
            published_at=datetime.now(timezone.utc),
        )
