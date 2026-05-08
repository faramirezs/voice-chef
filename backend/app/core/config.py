from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    PICTURES_API_KEY: str | None = None
    PICTURES_API_URL: str | None = None

    UPLOAD_DIR: str = "/code/uploads"
    UPLOAD_URL_PREFIX: str = "/uploads"
    # File-backed API keys (path in container). Mount a volume here for persistence.
    API_KEYS_FILE: str = "/data/api_keys.json"

    class Config:
        env_file = ".env"


settings = Settings()