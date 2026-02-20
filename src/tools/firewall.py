from __future__ import annotations

import re
from typing import Any

PROMPT_INJECTION_PATTERNS = [
    re.compile(r"\b(ignore|disregard|override)\b.{0,40}\b(instruction|previous|system)\b", re.IGNORECASE),
    re.compile(r"\byou are now\b", re.IGNORECASE),
]

SHELL_INJECTION_PATTERN = re.compile(r"(?:;|&&|\|\||`|\$\(|\n)")
SHELL_LIKE_ARG_KEYS = {"command", "cmd", "script", "query"}


def _looks_like_injection(value: str) -> bool:
    return any(pattern.search(value) for pattern in PROMPT_INJECTION_PATTERNS)


def validate_tool_call(tool_name: str, args: dict[str, Any], tenant_tools_config: dict[str, Any]) -> bool:
    if not isinstance(args, dict):
        return False

    tool_cfg = tenant_tools_config.get("tools", {}).get(tool_name)
    if not tool_cfg or not tool_cfg.get("enabled", True):
        return False

    for key, value in args.items():
        if not isinstance(value, str):
            continue

        if _looks_like_injection(value):
            return False

        # command injection checks are scoped to shell-like fields only
        if key.lower() in SHELL_LIKE_ARG_KEYS and SHELL_INJECTION_PATTERN.search(value):
            return False

    return True
