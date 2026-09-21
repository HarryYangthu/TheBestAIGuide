import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from builder import build_context, select_documents, trim_action_groups
from context import ROOT, initial_messages, measure, read_fixture
from context_strategies import cache_identity, evidence_metrics, offload, read_back, refresh_policy, scoped_summary
from engineering_experiments import action_group, inputs, run
from live_evaluate import grade, make_request, run as run_live


class EngineeringTests(unittest.TestCase):
    def setUp(self):
        self.task, self.index, self.history = inputs()

    def test_denied_body_is_never_opened(self):
        denied = dict(self.index[0], tenant="beta", id="denied", path="does-not-exist")
        selected, dropped, reads = select_documents(self.task, [denied], "alpha")
        self.assertEqual(selected, [])
        self.assertEqual(reads, [])
        self.assertEqual(dropped, [{"id": "denied", "reason": "permission"}])

    def test_wrong_scope_expired_and_duplicates_are_explained(self):
        envelope = build_context(self.task, self.index, self.history, "alpha")
        reasons = {d["id"]: d["reason"] for d in envelope["dropped"]}
        self.assertEqual(reasons["scratch-note"], "wrong_scope")
        self.assertEqual(reasons["policy-v2"], "superseded")
        self.assertEqual(reasons["expired-note"], "expired")
        self.assertEqual(reasons["policy-copy"], "duplicate")
        self.assertTrue(envelope["ready_for_review"])
        self.assertEqual(envelope, build_context(self.task, self.index, self.history, "alpha"))

    def test_same_version_conflict_stops_before_request(self):
        conflict = dict(self.index[0], id="conflict", path="engineering/conflicting-policy.txt")
        with self.assertRaisesRegex(ValueError, "unresolved_conflict"):
            build_context(self.task, self.index + [conflict], self.history, "alpha")
        self.assertEqual(refresh_policy(self.task, self.index + [conflict], "alpha")["status"], "UNKNOWN")

    def test_path_escape_and_missing_policy_fail(self):
        bad = dict(self.index[0], path="../README.md")
        with self.assertRaisesRegex(ValueError, "invalid_source_path"):
            build_context(self.task, [bad], self.history, "alpha")
        with self.assertRaisesRegex(ValueError, "missing_policy"):
            build_context(self.task, [], self.history, "alpha")

    def test_budget_includes_tools_and_output_schema(self):
        envelope = build_context(self.task, self.index, self.history, "alpha")
        self.assertGreater(envelope["budget"]["serialized_request_tokens"], measure(envelope["request"]["messages"]))
        with self.assertRaisesRegex(ValueError, "mandatory_overflow"):
            build_context(self.task, self.index, self.history, "alpha", window=901)

    def test_trim_keeps_all_results_and_rejects_broken_groups(self):
        old = action_group("old", "noise " * 1000)
        latest = action_group("one", "failed")
        latest[0]["tool_calls"].extend(action_group("two", "ok")[0]["tool_calls"])
        latest.append(action_group("two", "ok")[1])
        prefix = initial_messages(self.task)
        result = trim_action_groups(prefix, [old, latest], 300)
        self.assertEqual(result["removed_groups"], 1)
        self.assertEqual([x["tool_call_id"] for x in result["messages"] if x["role"] == "tool"], ["one", "two"])
        with self.assertRaisesRegex(ValueError, "incomplete_action_group"):
            trim_action_groups(prefix, [latest[:-1]], 1000)
        with self.assertRaisesRegex(ValueError, "latest_complete_group_overflow"):
            trim_action_groups(prefix, [latest], 5)

    def test_scoped_summary_preserves_negative_pending_and_provenance(self):
        summary = scoped_summary(read_fixture("engineering/events.json"), "report-17")
        self.assertIs(summary["facts"]["verification_passed"]["value"], False)
        self.assertEqual(summary["facts"]["verification_passed"]["source_id"], "s3")
        self.assertEqual(summary["facts"]["next_step"]["kind"], "pending")
        self.assertIs(summary["facts"]["allow_report"]["value"], False)

    def test_offload_read_back_permissions_and_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            ref = offload(directory, {"id": "log", "version": "r1", "body": "a\nfailed\nc\n"}, "alpha")
            self.assertEqual(read_back(directory, ref, "alpha", 2, 1)["lines"], [{"line": 2, "text": "failed"}])
            with self.assertRaises(PermissionError):
                read_back(directory, ref, "beta")
            (directory / ref["file"]).write_text("changed")
            with self.assertRaisesRegex(ValueError, "source_changed"):
                read_back(directory, ref, "alpha")

    def test_refresh_does_not_return_stale_fallback(self):
        self.assertEqual(refresh_policy(self.task, self.index, "alpha")["version"], "v3")
        self.assertEqual(refresh_policy({**self.task, "policy_version": "v4"}, self.index, "alpha")["status"], "UNKNOWN")
        expired = [dict(self.index[0], valid_until="2020-01-01T00:00:00+00:00")]
        self.assertEqual(refresh_policy(self.task, expired, "alpha")["status"], "UNKNOWN")

    def test_cache_scope_and_metric_empty_sets(self):
        key = cache_identity("model", "alpha", "v3", "t1", "prefix")
        self.assertNotEqual(key, cache_identity("model", "beta", "v3", "t1", "prefix"))
        self.assertNotEqual(key, cache_identity("model", "alpha", "v4", "t1", "prefix"))
        self.assertIsNone(evidence_metrics([], ["noise"])["recall"])
        self.assertIsNone(evidence_metrics(["needed"], [])["precision"])
        self.assertEqual(evidence_metrics(["a"], ["a", "a"])["recall"], 1)

    def test_position_probe_only_reorders_same_evidence(self):
        bodies = []
        for position in ("head", "middle", "tail"):
            request = make_request("model", position, 8)
            blocks = request["messages"][1]["content"].splitlines()[1:]
            bodies.append(sorted(blocks))
        self.assertEqual(bodies[0], bodies[1])
        self.assertEqual(bodies[1], bodies[2])
        self.assertTrue(grade('{"decision":"BLOCKED","allowed_workspaces":["alpha"],"evidence_ids":["report-evidence"]}')["passed"])
        self.assertFalse(grade('{"decision":"APPROVED"}')["passed"])

    def test_live_failures_and_skips_remain_in_denominator(self):
        def create(**kwargs):
            raise TimeoutError("test-only")
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            failed = run_live(client, "test-model", Path(tmp) / "failed", 1, (0,), 10000)
            self.assertEqual((failed["completed"], failed["passed"], failed["scheduled"]), (0, 0, 6))
            skipped = run_live(client, "test-model", Path(tmp) / "skipped", 1, (0,), 1)
            self.assertTrue(all(r["status"] == "skipped_budget" for r in skipped["rows"]))

    def test_live_success_saves_response_usage_and_grades(self):
        captured = []
        answer = '{"decision":"BLOCKED","allowed_workspaces":["alpha"],"evidence_ids":["report-evidence"]}'
        def create(**kwargs):
            captured.append(kwargs)
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=answer))],
                model="test-model-version", usage=SimpleNamespace(model_dump=lambda: {"prompt_tokens": 10}),
                model_dump=lambda: {"test_only": True, "content": answer})
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            out = Path(tmp) / "success"
            result = run_live(client, "test-model", out, 1, (0,), 10000)
            self.assertEqual((result["completed"], result["passed"], result["scheduled"]), (6, 6, 6))
            self.assertEqual(len(list(out.glob('trial-*/response.json'))), 6)
            self.assertEqual(result["rows"][0]["usage"], {"prompt_tokens": 10})
            self.assertTrue(all(r["model"] == "test-model" and r["max_completion_tokens"] == 300 for r in captured))

    def test_integrated_artifact_checks(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            result = run(Path(tmp))
            self.assertTrue(all(result["checks"].values()))
            self.assertEqual(result["compression"]["structured_preserved"], 3)
            self.assertEqual(result["real_model_trials"], 0)


if __name__ == "__main__":
    unittest.main()
