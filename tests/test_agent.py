from src.agent.prompt import build_system_prompt
from src.agent.structured import AgentResponse
from src.main import app
from src.tenant.models import Tenant, TenantConfig, TenantContext


def test_app_exists() -> None:
    assert app.title == "Nexus Agent"


def test_build_system_prompt_contains_tenant_and_style() -> None:
    tenant = Tenant(tenant_id="t1", business_name="Beauty & Nailschool Bochum")
    config = TenantConfig(tenant=tenant, prompt_template={"style": {"tone": "professionell", "language": "de"}})
    ctx = TenantContext(tenant_id="t1", config=config)

    prompt = build_system_prompt(ctx)

    assert "Beauty & Nailschool Bochum" in prompt
    assert "professionell" in prompt
    assert "Language: de" in prompt


def test_agent_response_to_dict() -> None:
    response = AgentResponse(text="Hallo", intent="faq", confidence=0.9, citations=["KB-FAQ-001"])
    as_dict = response.to_dict()
    assert as_dict["intent"] == "faq"
    assert as_dict["confidence"] == 0.9



def test_agent_loop_uses_litellm_call(monkeypatch):
    from src.agent.loop import AgentLoop

    loop = AgentLoop()

    def fake_call(model: str, prompt: str, max_tokens: int) -> str:
        return f"mocked:{model}:{max_tokens}"

    monkeypatch.setattr(loop, "_call_litellm", fake_call)
    out = loop.process({"intent": "general", "tier": "tier_1", "text": "hi", "max_tokens": 777})
    assert out["text"].startswith("mocked:tier_1:777")
