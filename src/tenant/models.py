from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TenantMembership:
    sender_id: str
    tenant_id: str
    channel: str


@dataclass
class Tenant:
    tenant_id: str
    business_name: str
    language: str = "de"
    timezone: str = "Europe/Berlin"
    active_channels: list[str] = field(default_factory=lambda: ["web"])


@dataclass
class TenantConfig:
    tenant: Tenant
    intents: dict[str, Any] = field(default_factory=dict)
    tools: dict[str, Any] = field(default_factory=dict)
    channels: dict[str, Any] = field(default_factory=dict)
    prompt_template: dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantContext:
    tenant_id: str
    config: TenantConfig
    metadata: dict[str, Any] = field(default_factory=dict)
