from __future__ import annotations

from typing import Any

from src.channels.base import build_disclosure
from src.tenant.models import TenantContext


def load_base_template(prompt_config: dict[str, Any]) -> str:
    """Load the base system prompt text from prompt_template config."""
    return str(prompt_config.get(
        "system",
        "Du bist ein hilfreicher, sicherer KI-Assistent. Nutze nur verifizierte Informationen.",
    ))


def inject_tenant_variables(base: str, context: TenantContext) -> str:
    """Inject tenant-specific variables into the prompt."""
    tenant = context.config.tenant
    variables = context.prompt_variables
    tone = variables.get("tone", "freundlich")
    language = variables.get("language", tenant.language)
    domain = variables.get("domain_instructions", "")
    disclosure = build_disclosure(tenant.business_name)

    parts = [
        base,
        f"\n\nDu bist der KI-Assistent für {tenant.business_name}.",
        f"Antworte in Sprache '{language}' mit Ton '{tone}'.",
        disclosure,
    ]

    if domain:
        parts.append(f"\n{domain}")

    # Grounding rules
    parts.append(
        "\n\nGrounding-Regeln:"
        "\n- Hard Facts: NUR aus der Knowledge-Base oder Tools. MÜSSEN eine Citation-ID haben."
        "\n- Soft Content: Darf frei formuliert werden. Keine neuen Fakten erfinden."
        "\n- Citation-Format: [KB-CATEGORY-ID]"
        "\n- Bei Unsicherheit: Ehrlich sagen und an Menschen eskalieren."
    )

    # Escalation rules
    parts.append(
        "\n\nEskalation:"
        "\n- Confidence < 0.5 → Weise darauf hin, dass du unsicher bist."
        "\n- Confidence < 0.3 → Eskaliere an menschlichen Support."
    )

    return "\n".join(parts)


def inject_tools(prompt: str, tool_schemas: list[dict[str, Any]]) -> str:
    """Append loaded tool schemas to the prompt."""
    if not tool_schemas:
        return prompt

    tool_lines = ["\n\nVerfügbare Tools:"]
    for tool in tool_schemas:
        name = tool.get("name", "unknown")
        desc = tool.get("description", "")
        tool_lines.append(f"- {name}: {desc}")

    return prompt + "\n".join(tool_lines)


def inject_context(prompt: str, context_text: str) -> str:
    """Append memory context (turns + summary + RAG) to the prompt."""
    if not context_text:
        return prompt
    return prompt + f"\n\nKontext:\n{context_text}"


def build_system_prompt(
    context: TenantContext,
    tool_schemas: list[dict[str, Any]] | None = None,
    context_text: str = "",
) -> str:
    """Assemble the full system prompt: base + tenant + tools + context."""
    base = load_base_template(context.config.prompt_template)
    prompt = inject_tenant_variables(base, context)

    if tool_schemas:
        prompt = inject_tools(prompt, tool_schemas)

    if context_text:
        prompt = inject_context(prompt, context_text)

    return prompt
