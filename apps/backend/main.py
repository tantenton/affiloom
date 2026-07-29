from fastapi import FastAPI

from config import settings
from routers.health import router as health_router

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
app.include_router(health_router)
