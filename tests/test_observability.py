from src.agent.loop import AgentLoop
from src.observability.alerts import AlertRule, evaluate_alert
from src.observability.langfuse import InMemoryLangfuseClient
from src.observability.pii import redact_pii


def test_pii_redaction_masks_email_and_phone() -> None:
    result = redact_pii("Kontakt: max@example.com oder +49 151 12345678")
    assert "max@example.com" not in result.text
    assert "+49 151 12345678" not in result.text
    assert "[EMAIL_" in result.text
    assert "[PHONE_" in result.text


def test_decision_log_has_expected_fields() -> None:
    client = InMemoryLangfuseClient()
    entry = client.log_decision(
        {
            "request_id": "r1",
            "tenant_id": "example_tenant",
            "channel": "web",
            "sender_id": "u1",
            "input_text": "mail me at max@example.com",
            "predicted_intent": "faq",
            "tier": "tier_1",
            "risk_level": "low",
            "confidence": 0.9,
            "tools_considered": ["kb_search"],
            "tools_called": [],
            "grounding_passed": True,
            "citations": ["KB-FAQ-001"],
            "response_text": "Hier sind die Infos",
            "latency_ms": 80,
            "token_in": 22,
            "token_out": 30,
        }
    )
    log_dict = client.logs()[0]
    assert len(log_dict.keys()) == 19
    assert entry.tenant_id == "example_tenant"
    assert log_dict["tenant_id"] == "example_tenant"


def test_alerts_trigger_for_latency_and_low_confidence() -> None:
    result = evaluate_alert(7000, 0.2, rule=AlertRule(max_latency_ms=5000, min_confidence=0.4))
    assert result.triggered
    assert "latency_threshold_exceeded" in result.reasons
    assert "confidence_too_low" in result.reasons


def test_agent_loop_logs_decision() -> None:
    logger = InMemoryLangfuseClient()
    loop = AgentLoop(logger=logger)
    loop.process({"request_id": "r2", "tenant_id": "example_tenant", "sender_id": "u2", "text": "Hallo"})
    logs = logger.logs()
    assert len(logs) == 1
    assert logs[0]["tenant_id"] == "example_tenant"
