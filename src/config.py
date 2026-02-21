from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    litellm_base_url: str = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
    litellm_api_key: str = os.getenv("LITELLM_API_KEY", "changeme")

    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    supabase_db_url: str = os.getenv("SUPABASE_DB_URL", "")

    langfuse_host: str = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    langfuse_public_key: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    langfuse_secret_key: str = os.getenv("LANGFUSE_SECRET_KEY", "")

    default_tenant_id: str = os.getenv("DEFAULT_TENANT_ID", "example_tenant")
    runtime_mode: str = os.getenv("RUNTIME_MODE", "local")

    def __post_init__(self) -> None:
        if self.runtime_mode not in {"local", "production"}:
            raise ValueError("RUNTIME_MODE must be either 'local' or 'production'.")

        if self.app_env.lower() in {"prod", "production"}:
            missing: list[str] = []
            if not self.litellm_api_key or self.litellm_api_key == "changeme":
                missing.append("LITELLM_API_KEY")
            if not self.supabase_service_role_key:
                missing.append("SUPABASE_SERVICE_ROLE_KEY")
            if not self.langfuse_secret_key:
                missing.append("LANGFUSE_SECRET_KEY")
            if missing:
                raise ValueError(
                    "Missing/unsafe production credentials: " + ", ".join(missing)
                )


settings = Settings()
