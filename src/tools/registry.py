from __future__ import annotations

from copy import deepcopy
from typing import Any

CORE_TOOLS = {"human_escalation", "kb_search"}


class ToolRegistry:
    def __init__(self, tenant_tools_config: dict[str, Any]) -> None:
        self.tenant_tools_config = tenant_tools_config

    def enabled_tools(self) -> dict[str, dict[str, Any]]:
        tool_cfg = deepcopy(self.tenant_tools_config.get("tools", {}))
        enabled = {name: cfg for name, cfg in tool_cfg.items() if cfg.get("enabled", True)}

        for core_tool in CORE_TOOLS:
            # Only auto-add when tool is truly absent; respect explicit tenant disable.
            if core_tool not in tool_cfg:
                enabled[core_tool] = {"enabled": True, "description": f"Implicit core tool: {core_tool}"}

        return enabled

    def get_tools_for_intent(self, intent: str) -> list[dict[str, Any]]:
        enabled = self.enabled_tools()
        intent_map = self.tenant_tools_config.get("intent_tools", {})
        configured_names = intent_map.get(intent)

        if configured_names:
            selected_names = [name for name in configured_names if name in enabled]
        else:
            selected_names = list(enabled.keys())

        return [{"name": name, **enabled[name]} for name in selected_names]
