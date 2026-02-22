from __future__ import annotations

from dataclasses import dataclass, field

from src.agent.loop import AgentLoop
from src.orchestration.messages import TaskRequest, TaskResult


@dataclass
class ContextBundle:
    request_id: str
    tenant_id: str
    channel: str = "web"
    sender_id: str = "system"


@dataclass
class SpecialistAgent:
    name: str
    system_prompt_snippet: str
    allowed_plugins: list[str] = field(default_factory=list)

    def execute(self, task: TaskRequest, context: ContextBundle) -> TaskResult:
        loop = AgentLoop()
        result = loop.process(
            {
                "request_id": context.request_id,
                "tenant_id": context.tenant_id,
                "sender_id": context.sender_id,
                "channel": context.channel,
                "text": str(task.payload.get("text", "")),
                "intent": str(task.payload.get("intent", "general")),
                "tier": str(task.payload.get("tier", "tier_2")),
            }
        )
        return TaskResult(
            task_id=task.task_id,
            from_agent=self.name,
            to_agent="manager",
            payload={"text": result["text"], "intent": result["intent"]},
            success=True,
        )


class ResearchAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__("research", "Research and source synthesis", ["web_search", "knowledge_base"])


class CoderAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__("coder", "Coding and debugging", ["github", "terminal"])


class WriterAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__("writer", "Writing and communication", ["knowledge_base"])


class OpsAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__("ops", "Infrastructure and automations", ["n8n", "terminal"])
