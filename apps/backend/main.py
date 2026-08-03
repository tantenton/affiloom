import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from config import settings
from db.session import dispose_engine
from middlewares.admin_audit import AdminAuditMiddleware  # M1-005
from routers.admin import router as admin_router
from routers.admin_content import router as admin_content_router
from routers.admin_dashboard import router as admin_dashboard_router
from routers.content import router as content_router
from routers.health import router as health_router
from routers.outbound import router as outbound_router
from routers.products import router as products_router
from routers.sitemap import router as sitemap_router
from routers.track import router as track_router
from routers.outbound import router as outbound_router
from routers.collections import router as collections_router
from services.logging import setup_logging

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """Add security-related HTTP headers to every response."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "0"  # noqa: E501
        # Relaxed CSP for local dev; tighten for production.
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' https: data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'"
        )
        referrer_policy = request.headers.get("Referrer-Policy")
        if not referrer_policy:
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # M1-004: Validate security settings at startup.
    setup_logging()
    security_warnings = settings.validate_security()
    for warning in security_warnings:
        log.warning(warning)
    try:
        yield
    finally:
        await dispose_engine()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SecureHeadersMiddleware)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(AdminAuditMiddleware)  # M1-005

# CORS is intentionally scoped to the configured frontend origin. Wildcards are
# avoided because affiliate deep-links are public but the client is not.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(products_router)
app.include_router(content_router)
app.include_router(sitemap_router)
app.include_router(track_router)
app.include_router(outbound_router)
app.include_router(collections_router)
app.include_router(admin_router)
app.include_router(admin_content_router)
app.include_router(admin_dashboard_router)
