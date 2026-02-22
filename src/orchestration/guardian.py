from __future__ import annotations

from enum import Enum
from pathlib import Path

import yaml
from pydantic import BaseModel

from src.tools.firewall import validate_tool_call


class GuardianOutcome(str, Enum):
    APPROVED = "approved"
    NEEDS_CONFIRMATION = "needs_confirmation"
    BLOCKED = "blocked"


class GuardianVerdict(BaseModel):
    outcome: GuardianOutcome
    reason: str


class GuardianAgent:
    def __init__(self, policy_path: Path = Path("configs/policies/guardian.yaml")) -> None:
        raw = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
        self.rules = raw.get("rules", {})

    def review(self, tool_name: str, args: dict, risk_level: str) -> GuardianVerdict:
        if not validate_tool_call(tool_name, args, {"tools": {tool_name: {"enabled": True}}}):
            return GuardianVerdict(outcome=GuardianOutcome.BLOCKED, reason="Firewall rejected tool call")

        command = str(args.get("command") or args.get("cmd") or "")
        blocked = self.rules.get("shell_commands", {}).get("blocked", [])
        if any(item in command for item in blocked):
            return GuardianVerdict(outcome=GuardianOutcome.BLOCKED, reason="Blocked shell command pattern")

        require_confirmation = self.rules.get("shell_commands", {}).get("require_confirmation", [])
        if any(item in command for item in require_confirmation):
            return GuardianVerdict(
                outcome=GuardianOutcome.NEEDS_CONFIRMATION,
                reason="Command requires user confirmation",
            )

        if risk_level in {"high", "critical"}:
            return GuardianVerdict(
                outcome=GuardianOutcome.NEEDS_CONFIRMATION,
                reason="High risk action requires confirmation",
            )

        return GuardianVerdict(outcome=GuardianOutcome.APPROVED, reason="Policy checks passed")
