from typing import Any

from pydantic import BaseModel, Field


class TenantMembership(BaseModel):
    sender_id: str
    tenant_id: str
    channel: str


class Tenant(BaseModel):
    tenant_id: str
    business_name: str
    language: str = "de"
    timezone: str = "Europe/Berlin"
    active_channels: list[str] = Field(default_factory=lambda: ["web"])


class TenantConfig(BaseModel):
    tenant: Tenant
    intents: dict[str, Any] = Field(default_factory=dict)
    tools: dict[str, Any] = Field(default_factory=dict)
    channels: dict[str, Any] = Field(default_factory=dict)
    prompt_template: dict[str, Any] = Field(default_factory=dict)


class TenantContext(BaseModel):
    tenant_id: str
    config: TenantConfig
    metadata: dict[str, Any] = Field(default_factory=dict)
