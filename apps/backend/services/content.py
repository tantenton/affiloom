"""SEO content service: drafts, internal-link suggestions, publishing."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.ai import ContentDraft, get_content_ai_adapter
from config import settings
from db.models import (
    Article,
    ArticleCategory,
    ArticleProduct,
    ArticleStatus,
    Product,
    Site,
)


def _slugify(text: str) -> str:
    """Make a URL-safe lowercase slug from Indonesian or English text."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:200].strip("-")


def _tokenize(text: str) -> set[str]:
    """Lower-case token set for simple overlap scoring."""
    return set(re.findall(r"[a-z]+", text.lower()))


@dataclass(frozen=True, slots=True)
class LinkScore:
    product_id: str
    title: str
    category: str | None
    score: float
    reason: str


async def resolve_site(session: AsyncSession, slug: str) -> Site:
    """Get or create the site row."""
    site = (
        await session.execute(select(Site).where(Site.slug == slug))
    ).scalar_one_or_none()
    if site is None:
        site = Site(
            slug=slug,
            domain="localhost:3000",
            name=slug.capitalize(),
            language="id-ID",
            default_locale="id_ID",
        )
        session.add(site)
        await session.flush()
    return site


async def generate_draft(
    session: AsyncSession,
    *,
    site_slug: str,
    category_slug: str,
    title: str,
    target_keyword: str,
    related_product_ids: list[str],
    use_ai: bool = False,
) -> Article:
    site = await resolve_site(session, site_slug)
    category: ArticleCategory | None = None
    if category_slug:
        category = (
            await session.execute(
                select(ArticleCategory).where(
                    ArticleCategory.site_id == site.id,
                    ArticleCategory.slug == category_slug,
                )
            )
        ).scalar_one_or_none()

    slug = _slugify(title)

    ai = await get_content_ai_adapter(
        provider=settings.CONTENT_AI_PROVIDER or None,
        model=settings.CONTENT_AI_MODEL or None,
        enabled=use_ai and settings.CONTENT_AI_ENABLED,
    )

    if use_ai:
        draft = await ai.generate_draft(
            f"Tulis artikel SEO bahasa Indonesia tentang {title}. "
            f"Kata kunci target: {target_keyword}. Tautkan ke produk terkait."
        )
    else:
        draft = await _deterministic_draft(title, target_keyword, related_product_ids)

    article = Article(
        site_id=site.id,
        category_id=category.id if category else None,
        slug=slug,
        title=draft.title,
        excerpt=draft.excerpt,
        body_md=draft.body_md,
        meta_title=draft.meta_title,
        meta_description=draft.meta_description,
        canonical_path=draft.canonical_path,
        language=draft.language,
        status=ArticleStatus.DRAFT,
        ai_provider=ai.provider if use_ai else None,
        ai_model=ai.model if use_ai else None,
    )
    session.add(article)
    await session.flush()

    # Link related products if they exist. Callers may pass either the
    # internal Product UUID or the partner-issued external_id — resolve both
    # so the admin UI can hand us whichever it has.
    if related_product_ids:
        for pos, pid in enumerate(related_product_ids):
            product = await session.get(Product, pid)
            if product is None:
                product = (
                    await session.execute(
                        select(Product).where(Product.external_id == pid)
                    )
                ).scalar_one_or_none()
            if product is None:
                continue
            session.add(
                ArticleProduct(
                    article_id=article.id,
                    product_id=product.id,
                    position=pos,
                    score=1.0,
                )
            )

    await session.commit()
    await session.refresh(article)
    return article


async def generate_internal_links(
    session: AsyncSession,
    *,
    article_id: str,
    limit: int = 5,
) -> list[LinkScore]:
    """Score known products by token overlap against the article text."""
    article = (
        await session.execute(select(Article).where(Article.id == article_id))
    ).scalar_one_or_none()
    if article is None:
        return []

    article_tokens = _tokenize(article.body_md + " " + article.title)

    stmt = select(Product).where(Product.is_active.is_(True)).limit(200)
    products = (await session.execute(stmt)).scalars().all()

    scored: list[LinkScore] = []
    for prod in products:
        prod_text = prod.title
        if prod.description:
            prod_text += " " + prod.description
        if prod.category:
            prod_text += " " + prod.category
        prod_tokens = _tokenize(prod_text)

        overlap = article_tokens & prod_tokens
        union = article_tokens | prod_tokens
        if not union:
            continue
        jaccard = len(overlap) / len(union)

        if jaccard > 0.05:
            scored.append(
                LinkScore(
                    product_id=prod.id,
                    title=prod.title,
                    category=prod.category,
                    score=round(jaccard, 4),
                    reason=(
                        "kecocokan kata kunci"
                        if jaccard > 0.2
                        else "keterkaitan ringan"
                    ),
                )
            )

    scored.sort(key=lambda x: x.score, reverse=True)
    return scored[:limit]


async def _deterministic_draft(
    title: str,
    keyword: str,
    product_ids: list[str],
) -> ContentDraft:
    slug = _slugify(title)
    products_ref = ""
    if product_ids:
        products_ref = (
            "Referensi produk terkait:\n"
            + "\n".join(f"- Produk `{pid}`" for pid in product_ids[:3])
            + "\n"
        )

    body = (
        f"# {title}\n\n"
        f"Artikel ini membahas topik **{title}** dengan fokus pada kata kunci "
        f"*{keyword}*. Dibuat secara deterministik, teks ini akan diisi oleh "
        f"tim penulis setelah strategi konten disepakati.\n\n"
        f"{products_ref}\n"
        f"## Mengapa topik ini?\n\n"
        f"Kata kunci `{keyword}` relevan dengan audiens Indonesia dan terkait "
        f"dengan katalog produk afiliasi saat ini. Artikel ini menandai posisi "
        f"kosong yang akan segera diisi konten manusi.\n\n"
        f"## Rekomendasi\n\n"
        f"Saat menelan, hubungkan paragraf pertama ke produk unggulan; "
        f"sertakan meta-deskripsi dan judul halaman sesuai pedoman SEO.\n"
    )

    return ContentDraft(
        title=title,
        excerpt=f"Artikel rintisan tentang {title} untuk kata kunci {keyword}.",
        body_md=body,
        meta_title=f"{title} — Panduan Lengkap untuk Pembeli Indonesia",
        meta_description=(
            f"Pelajari tentang {keyword}: panduan lengkap untuk pembeli Indonesia "
            "yang ingin membeli produk terbaik dengan informasi yang jelas."
        ),
        canonical_path=f"/artikel/{slug}",
        language="id-ID",
    )


def _article_text(title: str, body: str, desc: str | None) -> str:
    parts = [title]
    if desc:
        parts.append(desc)
    if body:
        parts.append(body)
    return " ".join(parts)


async def publish_article(
    session: AsyncSession,
    article_id: str,
) -> Article | None:
    article = await session.get(Article, article_id)
    if article is None or article.status != ArticleStatus.DRAFT:
        return None
    article.status = ArticleStatus.PUBLISHED
    article.published_at = datetime.now(timezone.utc)
    await session.commit()
    return article


async def upsert_category(
    session: AsyncSession,
    *,
    site_slug: str,
    slug: str,
    name: str,
    description: str | None = None,
) -> ArticleCategory:
    site = await resolve_site(session, site_slug)
    cat = (
        await session.execute(
            select(ArticleCategory).where(
                ArticleCategory.site_id == site.id,
                ArticleCategory.slug == slug,
            )
        )
    ).scalar_one_or_none()
    if cat is None:
        cat = ArticleCategory(
            site_id=site.id,
            slug=slug,
            name=name,
            description=description,
            is_active=True,
        )
        session.add(cat)
    else:
        cat.name = name
        cat.description = description
        cat.is_active = True
    await session.commit()
    return cat


__all__ = [
    "LinkScore",
    "generate_draft",
    "generate_internal_links",
    "get_content_ai_adapter",
    "publish_article",
    "resolve_site",
    "upsert_category",
]
