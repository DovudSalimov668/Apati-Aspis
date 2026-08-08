import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "APATI ASPIS API"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    APP_PORT: int = 8000

    # API Keys
    GEMINI_API_KEY: str = ""
    GOOGLE_SAFE_BROWSING_API_KEY: str = ""
    URLHAUS_AUTH_KEY: str = ""
    VIRUSTOTAL_API_KEY: str = ""

    # Database
    DATABASE_URL: str = "sqlite:///./apati_aspis.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
