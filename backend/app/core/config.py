from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    UPLOAD_DIR: str = os.path.abspath("uploads")


settings = Settings()