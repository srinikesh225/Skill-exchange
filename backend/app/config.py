"""Application configuration, loaded from environment / .env.

All engine weights and thresholds live here (or in constants.py) so the scoring
models are configurable and never hard-coded deep inside business logic.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "sqlite:///./skillpulse.db"

    # API
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Demo data generation
    demo_seed: int = 20260930
    demo_num_districts: int = 110
    demo_jobs_per_district: int = 110

    # Optional LLM enhancement (provider-agnostic; disabled when blank)
    llm_provider: str = ""
    llm_api_key: str = ""
    llm_model: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_provider and self.llm_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
