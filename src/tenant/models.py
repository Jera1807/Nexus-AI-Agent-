from __future__ import annotations

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
    risk_mapping: dict[str, str] = Field(default_factory=dict)


class TenantContext(BaseModel):
    tenant_id: str
    config: TenantConfig
    prompt_variables: dict[str, Any] = Field(default_factory=dict)
    active_tools: list[str] = Field(default_factory=list)
    intent_clusters: dict[str, Any] = Field(default_factory=dict)
    risk_mapping: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
