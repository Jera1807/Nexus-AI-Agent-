from __future__ import annotations

import re
from typing import Any

INJECTION_PATTERNS = [r"ignore\s+all\s+previous\s+instructions", r"system\s+prompt", r"rm\s+-rf"]


def _contains_injection(value: str) -> bool:
    lowered = value.lower()
    return any(re.search(pattern, lowered) for pattern in INJECTION_PATTERNS)


def validate_tool_call(tool_name: str, args: dict[str, Any], tenant_tools_config: dict[str, Any]) -> bool:
    tools = tenant_tools_config.get("tools", {})
    if tool_name not in tools or tools[tool_name].get("enabled", True) is not True:
        return False

    if not isinstance(args, dict):
        return False

    for key, value in args.items():
        if _contains_injection(str(key)):
            return False
        if isinstance(value, str) and _contains_injection(value):
            return False

    return True
