from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from src.tools.firewall import validate_tool_call


DEFAULT_GUARDIAN_POLICY: dict[str, Any] = {
    "rules": {
        "shell_commands": {
            "blocked": ["rm -rf", "mkfs", "dd", "shutdown", "reboot"],
            "require_confirmation": ["apt install", "pip install", "docker", "systemctl"],
        },
        "http_requests": {
            "blocked_domains": [],
            "require_confirmation_for_new_domains": True,
        },
        "file_operations": {
            "sandboxed_paths": ["/home/nexus/workspace"],
            "blocked_paths": ["/etc", "/usr", "/var", "/root"],
        },
        "risk_levels": {
            "low": "auto_approve",
            "medium": "log_and_approve",
            "high": "require_user_confirmation",
            "critical": "block_and_alert",
        },
    }
}


class GuardianOutcome(str, Enum):
    APPROVED = "approved"
    NEEDS_CONFIRMATION = "needs_confirmation"
    BLOCKED = "blocked"


class GuardianVerdict(BaseModel):
    outcome: GuardianOutcome
    reason: str


class GuardianAgent:
    def __init__(self, policy_path: Path = Path("configs/policies/guardian.yaml")) -> None:
        raw: dict[str, Any] = DEFAULT_GUARDIAN_POLICY
        try:
            loaded = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
            if isinstance(loaded, dict):
                loaded_rules = loaded.get("rules") or {}
                raw_rules = {**DEFAULT_GUARDIAN_POLICY["rules"], **loaded_rules}
                raw_rules["risk_levels"] = {
                    **DEFAULT_GUARDIAN_POLICY["rules"]["risk_levels"],
                    **(loaded_rules.get("risk_levels") or {}),
                }
                raw = {"rules": raw_rules}
        except (FileNotFoundError, OSError, yaml.YAMLError):
            raw = DEFAULT_GUARDIAN_POLICY

        self.rules = raw.get("rules", DEFAULT_GUARDIAN_POLICY["rules"])

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

        risk_action = str(self.rules.get("risk_levels", {}).get(risk_level, "auto_approve"))
        if risk_action == "block_and_alert":
            return GuardianVerdict(outcome=GuardianOutcome.BLOCKED, reason="Critical risk action blocked")
        if risk_action == "require_user_confirmation":
            return GuardianVerdict(
                outcome=GuardianOutcome.NEEDS_CONFIRMATION,
                reason="High risk action requires confirmation",
            )

        return GuardianVerdict(outcome=GuardianOutcome.APPROVED, reason="Policy checks passed")
