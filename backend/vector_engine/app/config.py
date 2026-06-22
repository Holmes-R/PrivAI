import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    chroma_path: str = "./chroma_db"

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")

settings = Settings()