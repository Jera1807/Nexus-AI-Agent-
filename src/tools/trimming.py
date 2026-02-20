from __future__ import annotations

import json
from typing import Any


def _json_size_bytes(value: Any) -> int:
    return len(json.dumps(value, ensure_ascii=False).encode("utf-8"))


def trim_result(tool_name: str, raw_result: Any, tenant_tools_config: dict[str, Any]) -> Any:
    global_cap = tenant_tools_config.get("global", {}).get("max_result_bytes", 4096)
    tool_cfg = tenant_tools_config.get("tools", {}).get(tool_name, {})
    trim_cfg = tool_cfg.get("trim", {})

    top_n = trim_cfg.get("top_n")
    field_whitelist = trim_cfg.get("field_whitelist")
    max_bytes = min(trim_cfg.get("max_bytes", global_cap), global_cap)

    trimmed = raw_result

    if isinstance(trimmed, list) and isinstance(top_n, int):
        trimmed = trimmed[:top_n]

    if isinstance(trimmed, list) and field_whitelist:
        trimmed = [
            {k: row.get(k) for k in field_whitelist if k in row}
            for row in trimmed
            if isinstance(row, dict)
        ]

    if _json_size_bytes(trimmed) <= max_bytes:
        return trimmed

    # deterministic fallback when trimmed payload is still too large
    payload = json.dumps(trimmed, ensure_ascii=False)
    keep = max(0, max_bytes - len('{"truncated":true,"data":""}'))
    return {"truncated": True, "data": payload[:keep]}
