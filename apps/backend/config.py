from __future__ import annotations

import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger(__name__)

# Values that must not appear in non-development environments.
_DEV_DEFAULTS = {
    "S3_ACCESS_KEY": "minioadmin",
    "S3_SECRET_KEY": "minioadmin",
    "MEILI_MASTER_KEY": "masterKey",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "affiloom"
    APP_VERSION: str = "0.1.0"

    # Mark the environment. Keep development by default so local dev is not noisy.
    AFFILOOM_ENV: str = "development"

    DATABASE_URL: str = "postgresql+asyncpg://affiloom:affiloom@localhost:5432/affiloom"
    REDIS_URL: str = "redis://localhost:6379/0"
    RABBITMQ_URL: str = "amqp://guest:***@localhost:5672/"
    MEILI_HOST: str = "http://localhost:7700"
    MEILI_MASTER_KEY: str = "masterKey"
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"  # noqa: S105  # dev-only default; overridden in prod
    S3_BUCKET: str = "affiloom-assets"

    # Comma-separated in the environment; parsed lazily below.
    CORS_ORIGINS: str = "http://localhost:3000"

    # M4 admin + sync knobs.
    ADMIN_API_TOKEN: str = ""
    SYNC_MAX_ITEMS: int = 500
    MEILI_INDEX: str = "products"
    MEILI_ENABLED: bool = False
    # Best-effort event emission; sync stays green when either is unreachable.
    REDIS_ENABLED: bool = False
    RABBITMQ_ENABLED: bool = False
    RABBITMQ_EXCHANGE: str = "affiloom.events"
    RABBITMQ_ROUTING_KEY: str = "sync.completed"

    # M5 content generation. AI stays disabled unless explicitly enabled and
    # credentials are supplied by the deployment.
    CONTENT_AI_ENABLED: bool = False
    CONTENT_AI_PROVIDER: str = ""
    CONTENT_AI_MODEL: str = ""
    CONTENT_AI_API_KEY: str = ""

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]

    @property
    def is_production(self) -> bool:
        return self.AFFILOOM_ENV.lower() in ("production", "prod", "staging")

    def validate_security(self) -> list[str]:
        warnings: list[str] = []

        if not self.is_production:
            return warnings

        for key, dev_val in _DEV_DEFAULTS.items():
            actual = getattr(self, key, "")
            if actual == dev_val:
                warnings.append(
                    f"SECURITY: {key} is still set to dev default '{dev_val}' "
                    f"in {self.AFFILOOM_ENV} environment."
                )

        if not self.ADMIN_API_TOKEN:
            warnings.append(
                "SECURITY: ADMIN_API_TOKEN is empty in "
                f"{self.AFFILOOM_ENV} environment. Admin endpoints will return 503."
            )

        if "guest:guest" in self.RABBITMQ_URL:
            warnings.append(
                "SECURITY: RABBITMQ_URL contains default guest:guest "
                f"credentials in {self.AFFILOOM_ENV} environment."
            )

        return warnings


settings = Settings()
