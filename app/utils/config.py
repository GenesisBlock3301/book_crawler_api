from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    MONGO_URL: str
    DB_NAME: str
    BASE_URL: str
    API_KEY: str
    REDIS_URL: str

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
        extra = "allow"


settings = Settings()