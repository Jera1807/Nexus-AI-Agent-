from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _dump_json_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def scaffold_tenant(
    tenant_root: Path,
    tenant_id: str,
    business_name: str,
    language: str = "de",
    timezone: str = "Europe/Berlin",
) -> list[Path]:
    tenant_root.mkdir(parents=True, exist_ok=True)

    files: dict[str, dict[str, Any]] = {
        "tenant.yaml": {
            "tenant_id": tenant_id,
            "business_name": business_name,
            "language": language,
            "timezone": timezone,
            "active_channels": ["web"],
        },
        "intents.yaml": {"intents": {}},
        "tools.yaml": {"tools": {}},
        "channels.yaml": {"channels": {"web": {"enabled": True}}},
        "prompt_template.yaml": {"style": {"language": language, "tone": "freundlich"}},
        "kb_seed.yaml": {"entries": []},
    }

    written: list[Path] = []
    for filename, payload in files.items():
        target = tenant_root / filename
        if not target.exists():
            _dump_json_yaml(target, payload)
            written.append(target)

    return written
