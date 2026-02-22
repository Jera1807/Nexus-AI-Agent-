from __future__ import annotations

from src.agent.structured import AgentResponse
from src.orchestration.messages import TaskRequest, TaskResult
from src.routing.models import RoutingDecision


class ManagerAgent:
    def decompose(self, message: str, routing_decision: RoutingDecision, request_id: str) -> list[TaskRequest]:
        if routing_decision.should_delegate and " and " in message.lower():
            parts = [part.strip() for part in message.split(" and ") if part.strip()]
        else:
            parts = [message]

        tasks: list[TaskRequest] = []
        for i, part in enumerate(parts, start=1):
            tasks.append(
                TaskRequest(
                    task_id=f"{request_id}-t{i}",
                    from_agent="manager",
                    to_agent="specialist",
                    payload={
                        "text": part,
                        "intent": routing_decision.intent,
                        "tier": routing_decision.tier.value,
                    },
                )
            )
        return tasks

    def assemble(self, results: list[TaskResult], intent: str) -> AgentResponse:
        text = "\n".join(str(r.payload.get("text", "")) for r in results if r.success).strip()
        if not text:
            text = "Ich konnte keine Ergebnisse erzeugen."
        return AgentResponse(text=text, intent=intent, confidence=0.7, citations=[])
