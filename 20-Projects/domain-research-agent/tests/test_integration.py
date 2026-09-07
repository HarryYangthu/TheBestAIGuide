from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from agent_loop import Action, ScriptedModel
from rag_pipeline import load_jsonl
from domain_research import ResearchService, InjectedCrash

CORPUS = Path(__file__).resolve().parents[1] / "fixtures/corpus.jsonl"


class IntegrationTests(unittest.TestCase):
    def service(self, directory, **kwargs):
        return ResearchService(directory, load_jsonl(CORPUS), tenant="demo", **kwargs)

    def test_citation_memory_and_request_binding(self):
        with TemporaryDirectory() as directory:
            service = self.service(directory)
            try:
                result = service.run("normal", "ERR-12003")
                self.assertFalse(result["abstained"])
                self.assertEqual([c["doc_id"] for c in result["citations"]], ["timeout-guide"])
                memory = service.memory.get("demo", "normal", now=0)
                self.assertEqual(memory.value["citations"], result["citations"])
                with self.assertRaises(ValueError):
                    service.run("normal", "ERR-12030")
            finally:
                service.close()

    def test_no_evidence_and_cross_tenant_are_not_memorized(self):
        with TemporaryDirectory() as directory:
            service = self.service(directory)
            try:
                for run_id, query in [("unknown", "ERR-88888"), ("private", "ERR-99999")]:
                    result = service.run(run_id, query)
                    self.assertTrue(result["abstained"])
                    self.assertEqual(result["citations"], [])
                    self.assertNotIn("PRIVATE_FIXTURE_ONLY", str(result))
                    self.assertIsNone(service.memory.get("demo", run_id, now=0))
            finally:
                service.close()

    def test_model_cannot_choose_tenant_or_publish_unsupported_prose(self):
        with TemporaryDirectory() as directory:
            service = self.service(directory)
            try:
                bad = ScriptedModel([Action("tool", "lookup", {"query":"ERR-99999", "tenant":"private"}),
                                     Action("finish", answer="Made-up answer")])
                with self.assertRaises(ValueError):
                    service.run("bad", "ERR-99999", model=bad)
                model = ScriptedModel([Action("tool", "lookup", {"query":"ERR-12003"}),
                                       Action("finish", answer="UNSUPPORTED_CLAIM")])
                result = service.run("safe", "ERR-12003", model=model)
                self.assertNotIn("UNSUPPORTED_CLAIM", result["text"])
            finally:
                service.close()

    def test_reopen_after_each_crash_point_without_retrieving_again(self):
        for crash_at in ("after_prepare", "after_report"):
            with self.subTest(crash_at=crash_at), TemporaryDirectory() as directory:
                service = self.service(directory)
                with self.assertRaises(InjectedCrash):
                    service.run("resume", "ERR-12003", crash_at=crash_at)
                service.close()
                service = self.service(directory)
                try:
                    # Empty scripted model would fail immediately if recovery reran it.
                    result = service.run("resume", "ERR-12003", model=ScriptedModel([]))
                    self.assertEqual(service.run("resume", "ERR-12003"), result)
                    self.assertEqual(service.memory.get("demo", "resume", now=0).version, 1)
                    self.assertEqual(service.checkpoints.load("resume")[1]["stage"], "completed")
                    self.assertEqual(len(list(Path(directory).glob("*.report.json"))), 1)
                finally:
                    service.close()

    def test_source_change_rejects_stale_resume(self):
        with TemporaryDirectory() as directory:
            service = self.service(directory)
            service.run("bound", "ERR-12003")
            service.close()
            service = self.service(directory, version="2")
            try:
                with self.assertRaises(ValueError):
                    service.run("bound", "ERR-12003")
            finally:
                service.close()

    def test_model_cannot_substitute_another_error_code(self):
        with TemporaryDirectory() as directory:
            service = self.service(directory)
            try:
                wrong = ScriptedModel([Action("tool", "lookup", {"query":"ERR-12030"}),
                                       Action("finish", answer="different question")])
                with self.assertRaises(ValueError):
                    service.run("wrong-code", "ERR-12003", model=wrong)
                self.assertEqual(list(Path(directory).glob("*.report.json")), [])
            finally:
                service.close()


if __name__ == "__main__":
    unittest.main()
