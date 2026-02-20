from pathlib import Path

import pytest

from src.tenant.manager import TenantManager, TenantNotFoundError
from src.tenant.models import TenantConfig, TenantContext, TenantMembership


def test_mock_tenant_fixture(mock_tenant):
    assert mock_tenant.tenant_id == "example_tenant"
    assert "web" in mock_tenant.active_channels


def test_tenant_context_builds(mock_config: TenantConfig):
    context = TenantContext(tenant_id=mock_config.tenant.tenant_id, config=mock_config)
    assert context.config.tenant.business_name


def test_load_tenant_config_merges_defaults_and_overrides(project_root: Path):
    manager = TenantManager(config_root=project_root / "configs")

    config = manager.load_tenant_config("example_tenant")

    assert config.tenant.business_name == "Beauty & Nailschool Bochum"
    assert config.tools["tools"]["calendar"]["enabled"] is False
    assert config.tools["tools"]["kb_search"]["trim"]["top_n"] == 3
    assert config.tools["tools"]["kb_search"]["trim"]["max_bytes"] == 2048


def test_resolve_tenant_from_membership(project_root: Path):
    manager = TenantManager(config_root=project_root / "configs")
    membership = TenantMembership(sender_id="user-1", tenant_id="example_tenant", channel="web")

    context = manager.load_tenant_context(membership=membership)

    assert context.tenant_id == "example_tenant"


def test_missing_tenant_raises(project_root: Path):
    manager = TenantManager(config_root=project_root / "configs")

    with pytest.raises(TenantNotFoundError):
        manager.load_tenant_config("does_not_exist")
