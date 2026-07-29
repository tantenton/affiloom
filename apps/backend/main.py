from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers.health import router as health_router
from routers.products import router as products_router

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

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
