"""Application configuration.

All secrets / environment-specific values come from environment variables
or from the ``.env`` file at the project root (see ``.env.example``).
Nothing secret is hardcoded here.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# This file lives at <project_root>/app/core/config.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Typed access to configuration values.

    Field names map automatically to environment variables
    (e.g. ``DATABASE_URL`` -> ``database_url``). Values in the ``.env`` file
    are read too, but real environment variables always win.
    """

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Database -------------------------------------------------------
    # e.g. postgresql+psycopg://postgres:postgres@localhost:5432/sih26033
    database_url: str

    # --- JWT ------------------------------------------------------------
    # Copy .env.example to .env and fill these in before running the app.
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # --- Browser frontend ------------------------------------------------
    frontend_origin: str = "http://localhost:5173"

    # --- CEDA Agri Market API --------------------------------------------
    ceda_api_key: str | None = None
    ceda_api_base_url: str = "https://api.ceda.ashoka.edu.in/v1"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    If required values are missing (database_url / jwt_secret_key), a
    pydantic ValidationError is raised telling you exactly which fields
    are missing -> copy .env.example to .env and fill in the values.
    """
    return Settings()
