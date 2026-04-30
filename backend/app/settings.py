"""Typed configuration loaded from the environment.

Engineering standard: all configuration goes through ONE Settings class
built on `pydantic-settings`. Required keys are validated at startup.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal
import secrets

from pydantic import Field, model_validator
import os

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    _HAVE_PYDANTIC_SETTINGS = True
except ImportError:  # pragma: no cover
    from pydantic import BaseModel as BaseSettings

    class SettingsConfigDict(dict):
        pass

    _HAVE_PYDANTIC_SETTINGS = False

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Strongly-typed application settings, sourced from env / ``.env``."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- LLM ----------------------------------------------------
    llm_provider: Literal["openai", "groq", "mock"] = "groq"
    groq_api_key: str = ""
    groq_model: str = "llama3-8b-8192"
    groq_embedding_model: str = "text-embedding-ada-002"  # or use sentence-transformers

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # --- Database ------------------------------------------------
    database_url: str = "postgresql+asyncpg://user:password@localhost/travel_db"

    # --- Auth ---------------------------------------------------
    secret_key: str = ""  # Generated at runtime if not provided
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # --- Runtime -------------------------------------------------
    max_agent_steps: int = 10
    agent_timeout_seconds: int = 60
    llm_request_timeout_seconds: int = 30

    # --- Caching -------------------------------------------------
    tool_cache_ttl_seconds: int = 300
    tool_cache_maxsize: int = 512

    # --- Storage paths ------------------------------------------
    model_path: Path = Field(
        default=PROJECT_ROOT / "models" / "classifier.joblib",
        description="Path to the trained ML model.",
    )
    data_path: Path = Field(
        default=PROJECT_ROOT / "data",
        description="Directory for data files.",
    )

    # --- APIs ---------------------------------------------------
    weather_api_url: str = "https://api.open-meteo.com/v1/forecast"
    exchange_api_url: str = "https://api.exchangerate-api.com/v4/latest/USD"
    flight_api_url: str = "https://api.example.com/flights"  # placeholder

    # --- Webhook ------------------------------------------------
    webhook_url: str = ""
    webhook_retries: int = 3
    webhook_timeout: int = 10

    # --- Observability ------------------------------------------
    log_level: str = "INFO"
    log_json: bool = True

    @model_validator(mode="after")
    def _validate_and_generate_secrets(self) -> Settings:
        # Generate SECRET_KEY if not provided
        if not self.secret_key or self.secret_key == "your-secret-key":
            self.secret_key = secrets.token_urlsafe(32)
        
        if self.llm_provider == "groq" and not self.groq_api_key:
            raise ValueError("LLM_PROVIDER=groq but GROQ_API_KEY is empty.")
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("LLM_PROVIDER=openai but OPENAI_API_KEY is empty.")
        return self

    def model_name(self) -> str:
        return {
            "groq": self.groq_model,
            "openai": self.openai_model,
            "mock": self.openai_model,
        }[self.llm_provider]

    def embedding_model_name(self) -> str:
        return {
            "groq": self.groq_embedding_model,
            "openai": self.openai_embedding_model,
            "mock": self.openai_embedding_model,
        }[self.llm_provider]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    if _HAVE_PYDANTIC_SETTINGS:
        return Settings()

    # Fallback for environments where pydantic-settings is not installed.
    from dotenv import load_dotenv

    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=False)

    env_values = {
        key: value
        for key, value in os.environ.items()
        if key.isupper()
    }
    return Settings.model_validate(env_values)