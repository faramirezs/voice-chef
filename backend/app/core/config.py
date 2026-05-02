from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    PICTURES_API_KEY: str | None = None
    PICTURES_API_URL: str | None = None

    UPLOAD_DIR: str = "/code/uploads"
    UPLOAD_URL_PREFIX: str = "/uploads"

    class Config:
        env_file = ".env"


settings = Settings()