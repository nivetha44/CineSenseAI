"""
Application Configuration for CineSenseAI
"""

import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "CineSenseAI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DATA_DIR: str = os.getenv("DATA_DIR", "data/processed")
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    class Config:
        case_sensitive = True


settings = Settings()
