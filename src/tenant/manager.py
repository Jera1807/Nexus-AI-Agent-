from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None

from src.config import settings
from src.tenant.models import Tenant, TenantConfig, TenantContext, TenantMembership


class TenantNotFoundError(FileNotFoundError):
    """Raised when a tenant config directory does not exist."""


class TenantConfigError(ValueError):
    """Raised when tenant.yaml is malformed for the Tenant model."""


LIST_MERGE_KEYS = {"scopes", "allowed_channels", "keywords"}


class TenantManager:
    """Loads tenant-aware configuration with defaults + override merging."""

    def __init__(self, config_root: Path | None = None, default_tenant_id: str | None = None) -> None:
        self.config_root = config_root or Path("configs")
        self.defaults_root = self.config_root / "defaults"
        self.tenants_root = self.config_root / "tenants"
        self.default_tenant_id = default_tenant_id or settings.default_tenant_id

    def resolve_tenant_id(self, membership: TenantMembership | None = None, tenant_id: str | None = None) -> str:
        if tenant_id:
            return tenant_id
        if membership:
            return membership.tenant_id
        return self.default_tenant_id

    def load_tenant_context(
        self,
        membership: TenantMembership | None = None,
        tenant_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TenantContext:
        resolved_tenant_id = self.resolve_tenant_id(membership=membership, tenant_id=tenant_id)
        tenant_config = self.load_tenant_config(resolved_tenant_id)
        return TenantContext(
            tenant_id=resolved_tenant_id,
            config=tenant_config,
            metadata=metadata or {},
        )

    def load_tenant_config(self, tenant_id: str) -> TenantConfig:
        tenant_root = self.tenants_root / tenant_id
        if not tenant_root.exists():
            raise TenantNotFoundError(f"Tenant '{tenant_id}' not found in {self.tenants_root}")

        tenant_data = self._read_yaml(tenant_root / "tenant.yaml")
        tenant = self._validate_tenant_data(tenant_id, tenant_data)

        intents = self._merge_default_and_tenant("intents.yaml", tenant_root)
        tools = self._merge_default_and_tenant("tools.yaml", tenant_root)
        channels = self._merge_default_and_tenant("channels.yaml", tenant_root)
        prompt_template = self._merge_default_and_tenant("prompt_template.yaml", tenant_root)

        return TenantConfig(
            tenant=tenant,
            intents=intents,
            tools=tools,
            channels=channels,
            prompt_template=prompt_template,
        )

    def _validate_tenant_data(self, tenant_id: str, tenant_data: dict[str, Any]) -> Tenant:
        expected = {f.name for f in fields(Tenant)}
        provided = set(tenant_data.keys())

        required = {"tenant_id", "business_name"}
        missing = required - provided
        unknown = provided - expected

        if missing:
            raise TenantConfigError(f"Tenant '{tenant_id}' missing required keys in tenant.yaml: {sorted(missing)}")
        if unknown:
            raise TenantConfigError(f"Tenant '{tenant_id}' has unknown keys in tenant.yaml: {sorted(unknown)}")

        try:
            return Tenant(**tenant_data)
        except Exception as exc:  # noqa: BLE001
            raise TenantConfigError(f"Invalid tenant.yaml for '{tenant_id}': {exc}") from exc

    def _merge_default_and_tenant(self, filename: str, tenant_root: Path) -> dict[str, Any]:
        default_data = self._read_yaml(self.defaults_root / filename)
        tenant_data = self._read_yaml(tenant_root / filename, allow_missing=True)
        return self._deep_merge(default_data, tenant_data)

    def _read_yaml(self, path: Path, allow_missing: bool = False) -> dict[str, Any]:
        if not path.exists():
            if allow_missing:
                return {}
            raise FileNotFoundError(path)

        raw_text = path.read_text(encoding="utf-8")

        if yaml is not None:
            raw_data = yaml.safe_load(raw_text) or {}
        else:
            # JSON is a YAML subset; this keeps local/dev operation possible without PyYAML.
            raw_data = json.loads(raw_text or "{}")

        if not isinstance(raw_data, dict):
            raise ValueError(f"Expected mapping at {path}, got {type(raw_data)!r}")
        return raw_data

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        merged = dict(base)
        for key, value in override.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge(merged[key], value)
            elif key in LIST_MERGE_KEYS and isinstance(merged.get(key), list) and isinstance(value, list):
                merged[key] = list(dict.fromkeys([*merged[key], *value]))
            else:
                merged[key] = value
        return merged
