from __future__ import annotations

from dataclasses import dataclass
from typing import Any

CORE_TOOLS = {"human_escalation", "kb_search"}


@dataclass(frozen=True)
class ToolSpec:
    name: str
    config: dict[str, Any]


def _is_enabled(tool_cfg: dict[str, Any]) -> bool:
    return tool_cfg.get("enabled", True) is True


def list_enabled_tools(tools_config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    configured_tools = tools_config.get("tools", {})
    return {name: cfg for name, cfg in configured_tools.items() if _is_enabled(cfg)}


def get_tools_for_intent(intent: str, tenant_config: dict[str, Any]) -> list[ToolSpec]:
    """Return enabled tools for an intent plus required core tools."""
    tools_cfg = tenant_config.get("tools", {})
    intents_cfg = tenant_config.get("intents", {}).get("intents", {})
    enabled = list_enabled_tools(tools_cfg)

    allowed_from_intent = set(intents_cfg.get(intent, {}).get("tools", []))
    allowed = allowed_from_intent | CORE_TOOLS

    specs: list[ToolSpec] = []
    for tool_name in sorted(allowed):
        cfg = enabled.get(tool_name)
        if cfg is None and tool_name in CORE_TOOLS:
            cfg = {"enabled": True}
        if cfg is not None:
            specs.append(ToolSpec(name=tool_name, config=cfg))

    return specs
