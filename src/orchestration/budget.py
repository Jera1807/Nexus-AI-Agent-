from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class BudgetSelection:
    model_name: str
    max_tokens: int


class BudgetAgent:
    def __init__(self, policy_path: Path = Path("configs/policies/budget.yaml")) -> None:
        raw = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
        self.tiers = raw.get("tiers", {})
        self.daily_cap = float(raw.get("daily_cap_usd", 2.0))
        self._daily_spend = 0.0

    def select_model(self, task_tier: str, task_description: str = "") -> BudgetSelection:
        _ = task_description
        tier_cfg = self.tiers.get(task_tier) or self.tiers.get("tier_2", {})
        models = tier_cfg.get("models", ["openai/gpt-4.1-mini"])
        return BudgetSelection(model_name=models[0], max_tokens=int(tier_cfg.get("max_tokens", 800)))

    def track_usage(self, model: str, tokens_in: int, tokens_out: int, cost: float) -> None:
        _ = (model, tokens_in, tokens_out)
        self._daily_spend += max(0.0, float(cost))

    def get_daily_spend(self) -> float:
        return round(self._daily_spend, 6)

    def check_budget(self) -> str:
        if self._daily_spend > self.daily_cap:
            return "exceeded"
        if self._daily_spend >= 0.8 * self.daily_cap:
            return "warning"
        return "ok"
