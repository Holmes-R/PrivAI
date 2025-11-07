# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    chroma_path: str = "./chroma_db"

    class Config:
        env_file = ".env"

settings = Settings()