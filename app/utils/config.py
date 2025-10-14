from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    MONGO_URL: str
    DB_NAME: str
    BASE_URL: str
    API_KEY: str
    REDIS_URL: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent /".env"
    )


settings = Settings()