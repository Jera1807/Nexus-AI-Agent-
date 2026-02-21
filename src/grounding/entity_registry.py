from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EntityRegistry:
    tenant_id: str
    valid_citations: set[str] = field(default_factory=set)

    def register(self, citation_id: str) -> None:
        self.valid_citations.add(citation_id)

    def register_many(self, citation_ids: list[str]) -> None:
        self.valid_citations.update(citation_ids)

    def contains(self, citation_id: str) -> bool:
        return citation_id in self.valid_citations
