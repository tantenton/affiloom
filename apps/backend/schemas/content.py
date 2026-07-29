"""SEO content API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class SiteOut(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    slug: str
    domain: str
    name: str
    tagline: str | None = None
    language: str
    default_locale: str


class CategoryOut(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    slug: str
    name: str
    description: str | None = None
    article_count: int = 0


class CategoryListResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: List[CategoryOut]
    total: int


class ArticleProductOut(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    product_id: str
    external_id: str
    title: str
    url: HttpUrl
    image_url: HttpUrl | None = None
    category: str | None = None
    score: float
    position: int


class ArticleOut(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    slug: str
    title: str
    excerpt: str | None = None
    body_md: str
    meta_title: str | None = None
    meta_description: str | None = None
    canonical_path: str
    language: str
    status: str
    category: CategoryOut | None = None
    products: List[ArticleProductOut] = []
    published_at: datetime | None = None
    updated_at: datetime


class ArticleListItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    slug: str
    title: str
    excerpt: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    canonical_path: str
    language: str
    status: str
    category: CategoryOut | None = None
    published_at: datetime | None = None
    updated_at: datetime


class ArticleListResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: List[ArticleListItem]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
    category: str | None = None


class SiteCreate(BaseModel):
    slug: str = Field(min_length=1, max_length=64)
    domain: str = Field(min_length=3, max_length=255)
    name: str = Field(min_length=1, max_length=128)
    tagline: str | None = Field(default=None, max_length=255)
    language: str = "id-ID"
    default_locale: str = "id_ID"


class CategoryCreate(BaseModel):
    site_slug: str = "affiloom"
    slug: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None


class ArticleCreate(BaseModel):
    site_slug: str = "affiloom"
    category_slug: str | None = None
    slug: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=255)
    excerpt: str | None = Field(default=None, max_length=500)
    body_md: str = ""
    meta_title: str | None = Field(default=None, max_length=255)
    meta_description: str | None = Field(default=None, max_length=500)
    canonical_path: str | None = Field(default=None, max_length=512)
    status: str = "draft"


class DraftRequest(BaseModel):
    site_slug: str = "affiloom"
    category_slug: str
    title: str = Field(min_length=1, max_length=255)
    target_keyword: str = Field(min_length=1, max_length=120)
    related_product_ids: list[str] = []
    use_ai: bool = False


class LinkSuggestionOut(BaseModel):
    model_config = ConfigDict(frozen=True)

    product_id: str
    title: str
    category: str | None
    reason: str
    score: float


class LinkSuggestionResponse(BaseModel):
    suggestions: List[LinkSuggestionOut]


class PublishResponse(BaseModel):
    id: str
    slug: str
    status: str
    published_at: datetime | None
