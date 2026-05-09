from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str

    UPLOAD_DIR: str = "/code/data/uploads"
    UPLOAD_URL_PREFIX: str = "/uploads"
    API_KEYS_DIR: str = "/code/data/api_keys"
    API_KEYS_URL_PREFIX: str = "/api_keys"


    class Config:
        env_file = ".env"


settings = Settings()