from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ConsentState:
    tenant_id: str
    user_id: str
    opted_in: bool = False
    frequency_cap_per_day: int = 1


class ConsentStore:
    def __init__(self) -> None:
        self._states: dict[tuple[str, str], ConsentState] = {}

    def set_consent(self, tenant_id: str, user_id: str, opted_in: bool, frequency_cap_per_day: int = 1) -> ConsentState:
        state = ConsentState(
            tenant_id=tenant_id,
            user_id=user_id,
            opted_in=opted_in,
            frequency_cap_per_day=frequency_cap_per_day,
        )
        self._states[(tenant_id, user_id)] = state
        return state

    def get_consent(self, tenant_id: str, user_id: str) -> ConsentState:
        return self._states.get((tenant_id, user_id), ConsentState(tenant_id=tenant_id, user_id=user_id))
