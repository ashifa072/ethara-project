from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./ethara.db"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    openai_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
