from fastapi import FastAPI
from config import settings
from routers import health

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Affiloom backend API",
)

app.include_router(health.router, tags=["health"])


@app.get("/", include_in_schema=False)
async def root():
    return {"service": settings.APP_NAME, "version": settings.APP_VERSION}
