from __future__ import annotations


def check_scope(tool_name: str, user_scopes: set[str], tenant_tools_config: dict) -> bool:
    required = set(tenant_tools_config.get("tools", {}).get(tool_name, {}).get("scopes", []))
    return required.issubset(user_scopes)


def check_channel(tool_name: str, channel: str, tenant_tools_config: dict) -> bool:
    allowed = tenant_tools_config.get("tools", {}).get(tool_name, {}).get("allowed_channels", [])
    return channel in allowed


def check_confirmation(tool_name: str, confirmed: bool, risk_level: str, tenant_tools_config: dict) -> bool:
    require_confirm = tenant_tools_config.get("global", {}).get("require_confirm_for_high_risk", True)
    if require_confirm and risk_level == "high":
        return confirmed
    return True
