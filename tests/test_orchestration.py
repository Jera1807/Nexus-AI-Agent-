from src.channels.message import UnifiedMessage
from src.orchestration.budget import BudgetAgent
from src.orchestration.coordinator import Coordinator
from src.orchestration.guardian import GuardianAgent, GuardianOutcome
from src.orchestration.manager import ManagerAgent
from src.routing.models import RiskLevel, RoutingDecision, Tier


def test_guardian_blocks_rm_rf() -> None:
    guardian = GuardianAgent()
    verdict = guardian.review("terminal", {"command": "rm -rf /"}, "critical")
    assert verdict.outcome == GuardianOutcome.BLOCKED


def test_guardian_approves_ls_workspace() -> None:
    guardian = GuardianAgent()
    verdict = guardian.review("terminal", {"command": "ls /home/nexus/workspace"}, "low")
    assert verdict.outcome == GuardianOutcome.APPROVED


def test_guardian_requires_confirmation_for_apt_install() -> None:
    guardian = GuardianAgent()
    verdict = guardian.review("terminal", {"command": "apt install nginx"}, "medium")
    assert verdict.outcome == GuardianOutcome.NEEDS_CONFIRMATION


def test_budget_agent_selects_tier_1() -> None:
    budget = BudgetAgent()
    selection = budget.select_model("tier_1", "hello")
    assert selection.max_tokens == 400


def test_budget_agent_blocks_when_cap_exceeded() -> None:
    budget = BudgetAgent()
    budget.track_usage(model="x", tokens_in=1, tokens_out=1, cost=3.0)
    assert budget.check_budget() == "exceeded"


def test_coordinator_routes_simple_without_delegation() -> None:
    coordinator = Coordinator()
    message = UnifiedMessage(channel="web", sender_id="u1", tenant_id="t1", text="hello")
    result = coordinator.process(message)
    assert result.intent == "general"


def test_coordinator_delegates_complex_request() -> None:
    coordinator = Coordinator()
    message = UnifiedMessage(channel="web", sender_id="u1", tenant_id="t1", text="check mails and create workflow")
    result = coordinator.process(message)
    assert result.intent == "automation"


def test_manager_decomposes_multi_step_task() -> None:
    manager = ManagerAgent()
    decision = RoutingDecision(
        intent="automation",
        tier=Tier.TIER_2,
        risk_level=RiskLevel.MEDIUM,
        confidence=0.6,
        rationale="x",
        should_delegate=True,
    )
    tasks = manager.decompose("check mails and create workflow", decision, request_id="r1")
    assert len(tasks) == 2
