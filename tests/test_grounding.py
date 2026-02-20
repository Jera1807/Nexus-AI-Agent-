import unittest

from src.grounding.entity_registry import EntityRegistry
from src.grounding.repair import FAIL_SAFE_MESSAGE, repair_or_fallback
from src.grounding.validator import validate_grounding


class TestGroundingValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = EntityRegistry(tenant_id="example")
        self.registry.register_many(["KB-POLICY-001", "KB-FAQ-PRICES"]) 

    def test_fact_with_valid_citation_passes(self) -> None:
        result = validate_grounding("Der Preis ist 99 EUR [KB-FAQ-PRICES]", self.registry)
        self.assertTrue(result.passed)

    def test_missing_citation_fails(self) -> None:
        result = validate_grounding("Der Preis ist 99 EUR", self.registry)
        self.assertFalse(result.passed)
        self.assertIn("missing_citation", result.violations)

    def test_invalid_citation_fails(self) -> None:
        result = validate_grounding("Info [KB-UNKNOWN-999]", self.registry)
        self.assertFalse(result.passed)
        self.assertTrue(any(v.startswith("invalid_citation:") for v in result.violations))

    def test_repair_adds_citation(self) -> None:
        repaired, result = repair_or_fallback("Der Preis ist 99 EUR", self.registry)
        self.assertTrue(result.passed)
        self.assertIn("[KB-", repaired)

    def test_repair_fallback_when_registry_empty(self) -> None:
        empty = EntityRegistry(tenant_id="empty")
        repaired, result = repair_or_fallback("Antwort ohne Beleg", empty)
        self.assertEqual(repaired, FAIL_SAFE_MESSAGE)
        self.assertFalse(result.passed)


if __name__ == "__main__":
    unittest.main()
