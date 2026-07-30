"""Public SEO content endpoints: sites, categories, articles."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    Article,
    ArticleCategory,
    ArticleProduct,
    ArticleStatus,
    Offer,
    Product,
    Site,
)
from db.session import get_session
from schemas.content import (
    ArticleListItem,
    ArticleListResponse,
    ArticleOut,
    ArticleProductOut,
    CategoryListResponse,
    CategoryOut,
    SiteOut,
)

router = APIRouter(prefix="/api", tags=["content"])


async def _get_active_site(session: AsyncSession) -> Site | None:
    """Return the current active site or ``None`` when the DB is empty.

    Reads are cheap and never mutate: seeding a fallback site is the admin's
    job (``POST /api/admin/content/sites``). When no site exists we return
    empty envelopes so the frontend can still render placeholder shells.
    """
    return (
        await session.execute(select(Site).where(Site.is_active.is_(True)).limit(1))
    ).scalar_one_or_none()


async def _serialize_category(
    session: AsyncSession, category: ArticleCategory
) -> CategoryOut:
    count_stmt = (
        select(func.count())
        .select_from(Article)
        .where(
            Article.category_id == category.id,
            Article.status == ArticleStatus.PUBLISHED,
        )
    )
    count = (await session.execute(count_stmt)).scalar_one()
    return CategoryOut(
        id=category.id,
        slug=category.slug,
        name=category.name,
        description=category.description,
        article_count=int(count),
    )


def _default_site_payload() -> SiteOut:
    return SiteOut(
        id="",
        slug="affiloom",
        domain="localhost:3000",
        name="Affiloom",
        tagline=None,
        language="id-ID",
        default_locale="id_ID",
    )


@router.get("/sites/current", response_model=SiteOut)
async def get_current_site(
    session: AsyncSession = Depends(get_session),
) -> SiteOut:
    site = await _get_active_site(session)
    if site is None:
        return _default_site_payload()
    return SiteOut(
        id=site.id,
        slug=site.slug,
        domain=site.domain,
        name=site.name,
        tagline=site.tagline,
        language=site.language,
        default_locale=site.default_locale,
    )


@router.get("/categories", response_model=CategoryListResponse)
async def list_categories(
    session: AsyncSession = Depends(get_session),
) -> CategoryListResponse:
    site = await _get_active_site(session)
    if site is None:
        return CategoryListResponse(items=[], total=0)
    stmt = (
        select(ArticleCategory)
        .where(
            ArticleCategory.site_id == site.id,
            ArticleCategory.is_active.is_(True),
        )
        .order_by(ArticleCategory.name.asc())
    )
    rows = (await session.execute(stmt)).scalars().all()
    items = [await _serialize_category(session, c) for c in rows]
    return CategoryListResponse(items=items, total=len(items))


@router.get("/categories/{slug}", response_model=CategoryOut)
async def get_category(
    slug: str = Path(..., min_length=1, max_length=128),
    session: AsyncSession = Depends(get_session),
) -> CategoryOut:
    site = await _get_active_site(session)
    if site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    cat = (
        await session.execute(
            select(ArticleCategory).where(
                ArticleCategory.site_id == site.id,
                ArticleCategory.slug == slug,
                ArticleCategory.is_active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if cat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return await _serialize_category(session, cat)


@router.get("/articles", response_model=ArticleListResponse)
async def list_articles(
    category: str | None = Query(default=None, max_length=128),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> ArticleListResponse:
    site = await _get_active_site(session)
    if site is None:
        return ArticleListResponse(
            items=[], total=0, limit=limit, offset=offset, category=category
        )

    base = (
        select(Article, ArticleCategory)
        .outerjoin(ArticleCategory, ArticleCategory.id == Article.category_id)
        .where(
            Article.site_id == site.id,
            Article.status == ArticleStatus.PUBLISHED,
        )
    )
    count_base = (
        select(func.count())
        .select_from(Article)
        .where(
            Article.site_id == site.id,
            Article.status == ArticleStatus.PUBLISHED,
        )
    )

    if category:
        base = base.where(ArticleCategory.slug == category)
        count_base = count_base.join(
            ArticleCategory, ArticleCategory.id == Article.category_id
        ).where(ArticleCategory.slug == category)

    total = (await session.execute(count_base)).scalar_one()
    rows = (
        await session.execute(
            base.order_by(
                Article.published_at.desc().nullslast(),
                Article.created_at.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
    ).all()

    items: list[ArticleListItem] = []
    for article, cat in rows:
        category_out = (
            CategoryOut(
                id=cat.id,
                slug=cat.slug,
                name=cat.name,
                description=cat.description,
                article_count=0,
            )
            if cat
            else None
        )
        items.append(
            ArticleListItem(
                id=article.id,
                slug=article.slug,
                title=article.title,
                excerpt=article.excerpt,
                meta_title=article.meta_title,
                meta_description=article.meta_description,
                canonical_path=article.canonical_path or f"/artikel/{article.slug}",
                language=article.language,
                status=article.status.value,
                category=category_out,
                published_at=article.published_at,
                updated_at=article.updated_at,
            )
        )

    return ArticleListResponse(
        items=items,
        total=int(total),
        limit=limit,
        offset=offset,
        category=category,
    )


@router.get("/articles/{slug}", response_model=ArticleOut)
async def get_article(
    slug: str = Path(..., min_length=1, max_length=200),
    session: AsyncSession = Depends(get_session),
) -> ArticleOut:
    site = await _get_active_site(session)
    if site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    stmt = (
        select(Article, ArticleCategory)
        .outerjoin(ArticleCategory, ArticleCategory.id == Article.category_id)
        .where(
            Article.site_id == site.id,
            Article.slug == slug,
        )
    )
    row = (await session.execute(stmt)).one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    article, cat = row

    category_out = (
        CategoryOut(
            id=cat.id,
            slug=cat.slug,
            name=cat.name,
            description=cat.description,
            article_count=0,
        )
        if cat
        else None
    )

    prod_stmt = (
        select(ArticleProduct, Product, Offer)
        .join(Product, Product.id == ArticleProduct.product_id)
        .outerjoin(
            Offer,
            (Offer.product_id == Product.id) & (Offer.is_active.is_(True)),
        )
        .where(ArticleProduct.article_id == article.id)
        .order_by(ArticleProduct.position.asc())
    )
    prod_rows = (await session.execute(prod_stmt)).all()

    products: list[ArticleProductOut] = []
    for ap, prod, offer in prod_rows:
        products.append(
            ArticleProductOut(
                id=ap.id,
                product_id=prod.id,
                external_id=prod.external_id,
                title=prod.title,
                url=(  # type: ignore[arg-type]
                    offer.url
                    if offer is not None
                    else f"https://example.com/products/{prod.id}"
                ),
                image_url=prod.image_url,  # type: ignore[arg-type]
                category=prod.category,
                score=ap.score,
                position=ap.position,
            )
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
        category=category_out,
        products=products,
        published_at=article.published_at,
        updated_at=article.updated_at,
    )


__all__ = ["router"]
