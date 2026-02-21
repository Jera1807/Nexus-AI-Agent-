from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class CustomerProfile:
    customer_id: str
    first_name: str
    last_name: str
    email: str = ""
    phone: str = ""


class CustomerStore:
    def __init__(self) -> None:
        self._profiles: dict[str, CustomerProfile] = {}

    def upsert(self, profile: CustomerProfile) -> None:
        self._profiles[profile.customer_id] = profile

    def get(self, customer_id: str) -> dict[str, Any] | None:
        profile = self._profiles.get(customer_id)
        return asdict(profile) if profile else None
