from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    APP_NAME: str = "affiloom"
    APP_VERSION: str = "0.1.0"

    DATABASE_URL: str = "postgresql+asyncpg://affiloom:affiloom@localhost:5432/affiloom"
    REDIS_URL: str = "redis://localhost:6379/0"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    MEILI_HOST: str = "http://localhost:7700"
    MEILI_MASTER_KEY: str = "masterKey"
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "affiloom-assets"


settings = Settings()
