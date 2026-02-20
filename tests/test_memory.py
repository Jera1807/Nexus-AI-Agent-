import unittest

from src.memory.context import build_context_package
from src.memory.semantic import SemanticMemoryIndex
from src.memory.summary import summarize_turns
from src.memory.working import WorkingMemoryStore


class TestWorkingMemory(unittest.TestCase):
    def test_append_and_truncate(self) -> None:
        store = WorkingMemoryStore(max_turns=2)
        store.append("s1", "user", "hi")
        store.append("s1", "assistant", "hello")
        store.append("s1", "user", "need help")

        turns = store.get("s1")
        self.assertEqual(len(turns), 2)
        self.assertEqual(turns[0].content, "hello")
        self.assertEqual(turns[1].content, "need help")


class TestSummary(unittest.TestCase):
    def test_summarize_compacts_text(self) -> None:
        store = WorkingMemoryStore()
        store.append("s1", "user", "Ich brauche   einen Termin")
        store.append("s1", "assistant", "Klar, wann passt es?")

        summary = summarize_turns(store.get("s1"), max_chars=120)
        self.assertIn("user: Ich brauche einen Termin", summary)


class TestSemanticMemory(unittest.TestCase):
    def test_search_returns_ranked_snippets(self) -> None:
        index = SemanticMemoryIndex()
        index.upsert("a", "Nageldesign Basiskurs in Bochum")
        index.upsert("b", "Öffnungszeiten Montag bis Freitag")

        results = index.search("Wann ist der Nageldesign Kurs in Bochum?", top_k=2)

        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0].snippet_id, "a")


class TestContextPackage(unittest.TestCase):
    def test_context_respects_budget(self) -> None:
        store = WorkingMemoryStore(max_turns=5)
        for i in range(5):
            store.append("s1", "user", f"Nachricht {i} mit etwas Inhalt")

        turns = store.get("s1")
        summary = summarize_turns(turns, max_chars=500)

        index = SemanticMemoryIndex()
        index.upsert("k1", "Sehr langer Wissenseintrag " * 20)
        snippets = index.search("Wissenseintrag", top_k=1)

        package = build_context_package(turns, summary, snippets, max_chars=180)
        total_chars = (
            sum(len(t.role) + len(t.content) for t in package.working_turns)
            + len(package.summary)
            + sum(len(s.text) for s in package.semantic_snippets)
        )
        self.assertLessEqual(total_chars, 180)


if __name__ == "__main__":
    unittest.main()
