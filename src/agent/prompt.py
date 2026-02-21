from __future__ import annotations

from src.channels.base import build_disclosure
from src.tenant.models import TenantContext


def build_system_prompt(context: TenantContext) -> str:
    tenant = context.config.tenant
    style = context.config.prompt_template.get("style", {})
    tone = style.get("tone", "freundlich")
    language = style.get("language", tenant.language)

    return (
        f"Du bist der KI-Assistent für {tenant.business_name}. "
        f"Antworte in Sprache '{language}' mit Ton '{tone}'. "
        f"{build_disclosure(tenant.business_name)}"
    )
