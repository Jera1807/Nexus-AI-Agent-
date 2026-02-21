from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    log_level: str = "INFO"

    host: str = "0.0.0.0"
    port: int = 8000

    litellm_base_url: str = "http://localhost:4000"
    litellm_api_key: str = "changeme"

    redis_url: str = "redis://localhost:6379/0"

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_db_url: str = ""

    langfuse_host: str = "https://cloud.langfuse.com"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""

    default_tenant_id: str = "example_tenant"

    daily_llm_budget_usd: float = 2.00

    @field_validator("app_env", mode="before")
    @classmethod
    def _normalise_env(cls, v: str) -> str:
        return v.strip().lower()

    def check_production_secrets(self) -> list[str]:
        """Return list of missing/unsafe secrets for production."""
        if self.app_env not in {"prod", "production"}:
            return []
        missing: list[str] = []
        if not self.litellm_api_key or self.litellm_api_key == "changeme":
            missing.append("LITELLM_API_KEY")
        if not self.supabase_service_role_key:
            missing.append("SUPABASE_SERVICE_ROLE_KEY")
        if not self.langfuse_secret_key:
            missing.append("LANGFUSE_SECRET_KEY")
        return missing


settings = Settings()
