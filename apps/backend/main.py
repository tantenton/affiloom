from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from db.session import dispose_engine
from routers.admin import router as admin_router
from routers.health import router as health_router
from routers.products import router as products_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        yield
    finally:
        await dispose_engine()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

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
app.include_router(admin_router)
