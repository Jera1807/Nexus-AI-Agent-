from __future__ import annotations

from typing import Any


def _tool_cfg(tool_name: str, tenant_tools_config: dict[str, Any]) -> dict[str, Any]:
    return tenant_tools_config.get("tools", {}).get(tool_name, {})


def check_scope(tool_name: str, granted_scopes: set[str], tenant_tools_config: dict[str, Any]) -> bool:
    required = set(_tool_cfg(tool_name, tenant_tools_config).get("scopes", []))
    return required.issubset(granted_scopes)


def check_channel(tool_name: str, channel: str, tenant_tools_config: dict[str, Any]) -> bool:
    allowed = _tool_cfg(tool_name, tenant_tools_config).get("allowed_channels", [])
    return channel in allowed if allowed else True


def check_confirmation(tool_name: str, confirmed: bool, risk_level: str, tenant_tools_config: dict[str, Any]) -> bool:
    cfg = _tool_cfg(tool_name, tenant_tools_config)

    per_tool_required = cfg.get("require_confirmation")
    if isinstance(per_tool_required, bool):
        return confirmed if per_tool_required else True

    require_confirm_for_high_risk = tenant_tools_config.get("global", {}).get("require_confirm_for_high_risk", True)
    if require_confirm_for_high_risk and risk_level == "high":
        return confirmed
    return True
