"""
Environment configuration and secrets management for TravelSync.

Uses Pydantic BaseSettings to securely load environment variables
from .env file, ensuring sensitive data like JWT secrets are
never hardcoded into the source code.
"""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Validates and stores application-wide settings.
    Will crash the server on startup if the required .env variables are missing.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    max_upload_size_bytes: int = 5 * 1024 * 1024

    base_url: str = "http://127.0.0.1:8000"


settings = Settings()
