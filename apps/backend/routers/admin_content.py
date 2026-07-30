"""Admin content endpoints: manage sites, categories, articles, publish, link-suggestions."""  # noqa: E501

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Article, ArticleCategory, ArticleStatus, Site
from db.session import get_session
from routers.admin import _require_admin_token
from schemas.content import (
    ArticleCreate,
    ArticleOut,
    CategoryCreate,
    CategoryOut,
    DraftRequest,
    LinkSuggestionOut,
    LinkSuggestionResponse,
    PublishResponse,
    SiteCreate,
    SiteOut,
)
from services.content import (
    generate_draft,
    generate_internal_links,
    publish_article,
    upsert_category,
)

router = APIRouter(prefix="/api/admin/content", tags=["admin-content"])


# ─── Sites ──────────────────────────────────────────────────────────────


@router.post(
    "/sites", response_model=SiteOut, dependencies=[Depends(_require_admin_token)]
)
async def create_site(
    data: SiteCreate, session: AsyncSession = Depends(get_session)
) -> SiteOut:
    existing = (
        await session.execute(select(Site).where(Site.slug == data.slug))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Site slug already exists"
        )
    site = Site(
        slug=data.slug,
        domain=data.domain,
        name=data.name,
        tagline=data.tagline,
        language=data.language,
        default_locale=data.default_locale,
    )
    session.add(site)
    await session.commit()
    await session.refresh(site)
    return SiteOut(
        id=site.id,
        slug=site.slug,
        domain=site.domain,
        name=site.name,
        tagline=site.tagline,
        language=site.language,
        default_locale=site.default_locale,
    )


# ── Categories ───────────────────────────────────────────────────────────


@router.post(
    "/categories",
    response_model=CategoryOut,
    dependencies=[Depends(_require_admin_token)],
)
async def create_category(
    data: CategoryCreate, session: AsyncSession = Depends(get_session)
) -> CategoryOut:
    cat = await upsert_category(
        session,
        site_slug=data.site_slug,
        slug=data.slug,
        name=data.name,
        description=data.description,
    )
    return CategoryOut(
        id=cat.id,
        slug=cat.slug,
        name=cat.name,
        description=cat.description,
        article_count=0,
    )


@router.get(
    "/categories",
    response_model=list[CategoryOut],
    dependencies=[Depends(_require_admin_token)],
)
async def list_categories_admin(
    session: AsyncSession = Depends(get_session),
) -> list[CategoryOut]:
    stmt = select(ArticleCategory).order_by(ArticleCategory.name.asc())
    rows = (await session.execute(stmt)).scalars().all()
    return [
        CategoryOut(
            id=c.id,
            slug=c.slug,
            name=c.name,
            description=c.description,
            article_count=0,
        )
        for c in rows
    ]


# ── Articles ─────────────────────────────────────────────────────────────


@router.post(
    "/drafts", response_model=ArticleOut, dependencies=[Depends(_require_admin_token)]
)
async def create_article_draft(
    data: DraftRequest, session: AsyncSession = Depends(get_session)
) -> ArticleOut:
    # Fail closed when AI is requested without a configured provider so we
    # never silently swap the caller onto the deterministic path (or worse,
    # fabricate content).
    from config import settings as _settings

    if data.use_ai and not _settings.CONTENT_AI_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI content generation is disabled (CONTENT_AI_ENABLED=false)",
        )
    article = await generate_draft(
        session,
        site_slug=data.site_slug,
        category_slug=data.category_slug,
        title=data.title,
        target_keyword=data.target_keyword,
        related_product_ids=data.related_product_ids,
        use_ai=data.use_ai,
    )
    return ArticleOut(
        id=article.id,
        slug=article.slug,
        title=article.title,
        excerpt=article.excerpt,
        body_md=article.body_md,
        meta_title=article.meta_title,
        meta_description=article.meta_description,
        canonical_path=article.canonical_path or f"/artikel/{article.slug}",
        language=article.language,
        status=article.status.value,
        category=None,
        products=[],
        published_at=article.published_at,
        updated_at=article.updated_at,
    )


@router.post(
    "/articles", response_model=ArticleOut, dependencies=[Depends(_require_admin_token)]
)
async def create_article(
    data: ArticleCreate, session: AsyncSession = Depends(get_session)
) -> ArticleOut:
    from services.content import resolve_site

    site = await resolve_site(session, data.site_slug)
    category_id: str | None = None
    if data.category_slug:
        cat = (
            await session.execute(
                select(ArticleCategory).where(
                    ArticleCategory.site_id == site.id,
                    ArticleCategory.slug == data.category_slug,
                )
            )
        ).scalar_one_or_none()
        if cat:
            category_id = cat.id

    article = Article(
        site_id=site.id,
        category_id=category_id,
        slug=data.slug,
        title=data.title,
        excerpt=data.excerpt,
        body_md=data.body_md,
        meta_title=data.meta_title,
        meta_description=data.meta_description,
        canonical_path=data.canonical_path or f"/artikel/{data.slug}",
        status=ArticleStatus(data.status),
    )
    session.add(article)
    await session.commit()
    await session.refresh(article)
    return ArticleOut(
        id=article.id,
        slug=article.slug,
        title=article.title,
        excerpt=article.excerpt,
        body_md=article.body_md,
        meta_title=article.meta_title,
        meta_description=article.meta_description,
        canonical_path=article.canonical_path or f"/artikel/{article.slug}",
        language=article.language,
        status=article.status.value,
        category=None,
        products=[],
        published_at=article.published_at,
        updated_at=article.updated_at,
    )


@router.post(
    "/articles/{article_id}/publish",
    response_model=PublishResponse,
    dependencies=[Depends(_require_admin_token)],
)
async def admin_publish_article(
    article_id: str, session: AsyncSession = Depends(get_session)
) -> PublishResponse:
    article = await publish_article(session, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found or not in draft status",
        )
    return PublishResponse(
        id=article.id,
        slug=article.slug,
        status=article.status.value,
        published_at=article.published_at,
    )


@router.get(
    "/articles/{article_id}/link-suggestions",
    response_model=LinkSuggestionResponse,
    dependencies=[Depends(_require_admin_token)],
)
async def article_link_suggestions(
    article_id: str,
    limit: int = Query(default=5, ge=1, le=20),
    session: AsyncSession = Depends(get_session),
) -> LinkSuggestionResponse:
    suggestions = await generate_internal_links(
        session, article_id=article_id, limit=limit
    )
    return LinkSuggestionResponse(
        suggestions=[
            LinkSuggestionOut(
                product_id=s.product_id,
                title=s.title,
                category=s.category,
                reason=s.reason,
                score=s.score,
            )
            for s in suggestions
        ],
    )


__all__ = ["router"]
