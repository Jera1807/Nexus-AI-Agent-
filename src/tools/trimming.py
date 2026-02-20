from __future__ import annotations

import json
from typing import Any

GLOBAL_MAX_BYTES = 4096


def _truncate_text(value: str, max_bytes: int) -> str:
    raw = value.encode("utf-8")
    if len(raw) <= max_bytes:
        return value
    return raw[:max_bytes].decode("utf-8", errors="ignore")


def trim_result(tool_name: str, raw_result: Any, tenant_tools_config: dict[str, Any]) -> Any:
    tool_cfg = tenant_tools_config.get("tools", {}).get(tool_name, {})
    global_cap = tenant_tools_config.get("global", {}).get("max_result_bytes", GLOBAL_MAX_BYTES)

    trim_cfg = tool_cfg.get("trim", {})
    max_bytes = min(trim_cfg.get("max_bytes", global_cap), global_cap)
    top_n = trim_cfg.get("top_n")
    whitelist = trim_cfg.get("field_whitelist")

    result = raw_result
    if isinstance(result, list) and isinstance(top_n, int):
        result = result[: max(0, top_n)]

    if isinstance(result, list) and whitelist:
        result = [
            {k: item.get(k) for k in whitelist if k in item} if isinstance(item, dict) else item
            for item in result
        ]
    elif isinstance(result, dict) and whitelist:
        result = {k: result.get(k) for k in whitelist if k in result}

    serialized = json.dumps(result, ensure_ascii=False)
    if len(serialized.encode("utf-8")) <= max_bytes:
        return result

    if isinstance(result, str):
        return _truncate_text(result, max_bytes)

    truncated = _truncate_text(serialized, max_bytes)
    return {"truncated": True, "data": truncated}
