from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    API_URL: str = "http://web:8000"

    class Config:
        env_file = ".env"

settings = Settings()
