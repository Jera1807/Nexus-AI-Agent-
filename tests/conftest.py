from pathlib import Path

import pytest

from src.tenant.models import Tenant, TenantConfig


@pytest.fixture()
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture()
def mock_tenant_dict() -> dict:
    return {
        "tenant_id": "example_tenant",
        "business_name": "Beauty & Nailschool Bochum",
        "language": "de",
        "timezone": "Europe/Berlin",
        "active_channels": ["web", "telegram"],
    }


@pytest.fixture()
def mock_tenant(mock_tenant_dict: dict) -> Tenant:
    return Tenant(**mock_tenant_dict)


@pytest.fixture()
def mock_config(mock_tenant: Tenant) -> TenantConfig:
    return TenantConfig(tenant=mock_tenant)
