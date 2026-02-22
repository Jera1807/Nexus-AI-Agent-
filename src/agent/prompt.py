from __future__ import annotations

from src.channels.base import build_disclosure
from src.tenant.models import TenantContext


def build_system_prompt(
    context: TenantContext,
    plugin_schemas: list[str] | None = None,
    personal_facts: list[str] | None = None,
    language: str | None = None,
    grounding_mode: str = "open",
) -> str:
    tenant = context.config.tenant
    style = context.config.prompt_template.get("style", {})
    tone = style.get("tone", "freundlich")
    selected_language = language or style.get("language", tenant.language)

    plugins = ", ".join(plugin_schemas or []) or "none"
    facts = "; ".join(personal_facts or []) or "none"

    nexus_block = (
        "You are Nexus, a personal AI agent. You act on behalf of your user. "
        "You can read emails, manage calendars, create automations, search the web, "
        "control servers, and much more."
    )

    return (
        f"{nexus_block} Available tools: {plugins}. User facts: {facts}. "
        f"Language: {selected_language}. Grounding mode: {grounding_mode}. "
        f"Tenant: {tenant.business_name}. Tone: {tone}. "
        f"{build_disclosure(tenant.business_name)}"
    )
