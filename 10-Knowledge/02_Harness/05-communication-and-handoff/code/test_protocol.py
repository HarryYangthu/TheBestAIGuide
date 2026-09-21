import asyncio
from copy import deepcopy
import unittest
from unittest.mock import patch
from protocol import Case, LocalBus, exchange, notes_worker, read_fixture
from v1_delegate import check_notes


class ProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def test_changed_snapshot_version_rejected_at_worker_and_receiver(self):
        case, bus = Case(), LocalBus(["coordinator", "notes-reader"])
        request = case.delegate("coordinator", "snapshot-ready.json")
        changed = read_fixture("snapshot-ready.json")
        changed["version"] = "notes-3"
        with patch("protocol.read_fixture", return_value=changed):
            response, _ = await exchange(case, request, bus)
        self.assertEqual(response["kind"], "failure")
        self.assertEqual(response["payload"]["code"], "input_version_changed")
        self.assertNotIn("read-notes", case.results)
        # An independent sender could ignore that guard; receiver checks again.
        case = Case()
        request = case.delegate("coordinator", "snapshot-ready.json")
        payload = check_notes(case.task, changed)
        payload["evidence"]["file"] = "snapshot-ready.json"
        with patch("protocol.read_fixture", return_value=changed):
            decision = case.receive(case.response(request, "result", payload))
        self.assertEqual(decision, "stale_input")
        self.assertFalse(case.merge(["read-notes"])["complete"])

    async def test_pending_handoff_blocks_new_delegation(self):
        case, _, _, _ = await self.ready()
        offer = case.offer_handoff("coordinator", "report-writer")
        with self.assertRaisesRegex(ValueError, "handoff is pending"):
            case.delegate("coordinator", "snapshot-ready.json", task_id="another-check")
        self.assertEqual(set(case.requests), {"read-notes"})
        self.assertEqual(case.accept_handoff("report-writer", offer["handoff_id"], 1), "handoff_accepted")
        self.assertFalse(any(state in {"pending", "running"} for state in case.states.values()))

    async def ready(self):
        case = Case()
        bus = LocalBus(["coordinator", "notes-reader"])
        request = case.delegate("coordinator", "snapshot-ready.json")
        result, _ = await exchange(case, request, bus)
        return case, bus, request, result

    async def test_duplicate_request_does_not_execute_again(self):
        case, bus, request, result = await self.ready()
        copies = await asyncio.gather(notes_worker(case, request, bus), notes_worker(case, request, bus))
        self.assertEqual(bus.worker_executions, 1)
        self.assertEqual(copies, [result, result])
        self.assertEqual(case.receive(await bus.receive("coordinator")), "duplicate")
        self.assertEqual(case.receive(await bus.receive("coordinator")), "duplicate")

    async def test_id_conflict_and_outcome_conflict(self):
        case, _, request, result = await self.ready()
        conflict = deepcopy(result)
        conflict["payload"]["found"] = 10
        self.assertEqual(case.receive(conflict), "conflicting_message")
        self.assertEqual(case.receive(case.response(request, "result", conflict["payload"])), "conflicting_outcome")
        self.assertEqual(case.results["read-notes"]["found"], 2)

    async def test_late_attempt_does_not_overwrite_success(self):
        case, bus = Case(), LocalBus(["coordinator", "notes-reader"])
        old = case.delegate("coordinator", "snapshot-unfound.json")
        failure, _ = await exchange(case, old, bus)
        current = case.delegate("coordinator", "snapshot-ready.json")
        await exchange(case, current, bus)
        self.assertEqual(case.receive(case.response(old, "failure", failure["payload"])), "stale_attempt")
        self.assertEqual(case.states["read-notes"], "completed")
        self.assertEqual(case.receive(case.response(current, "started", {})), "late_progress")

    async def test_reject_wrong_correlation_input_and_participant(self):
        case, _, request, result = await self.ready()
        for key, value, expected in [("correlation_id", "wrong", "wrong_correlation"),
                                      ("input_version", "old", "stale_input"),
                                      ("from", "other", "wrong_participant"),
                                      ("case_id", "other", "wrong_case")]:
            message = case.response(request, "result", result["payload"])
            message[key] = value
            self.assertEqual(case.receive(message), expected)

    async def test_wrong_evidence_cannot_complete_task(self):
        case, bus = Case(), LocalBus(["coordinator", "notes-reader"])
        request = case.delegate("coordinator", "snapshot-ready.json")
        result = await notes_worker(case, request, bus)
        case.receive(await bus.receive("coordinator"))
        true_result = await bus.receive("coordinator")
        false_result = case.response(request, "result", result["payload"])
        false_result["payload"]["missing"] = 0
        self.assertEqual(case.receive(false_result), "invalid_evidence")
        self.assertFalse(case.merge(["read-notes"])["complete"])
        self.assertEqual(case.receive(true_result), "accepted_result")

    async def test_handoff_acceptance_and_stale_owner(self):
        case, _, request, result = await self.ready()
        offer = case.offer_handoff("coordinator", "report-writer")
        self.assertEqual(case.owner, "coordinator")
        self.assertEqual(case.accept_handoff("intruder", offer["handoff_id"], 1), "rejected_handoff")
        self.assertEqual(case.accept_handoff("report-writer", offer["handoff_id"], 1), "handoff_accepted")
        self.assertEqual(case.accept_handoff("report-writer", offer["handoff_id"], 1), "rejected_handoff")
        self.assertEqual(case.act("coordinator", 1, "write_report"), "rejected_stale_owner")
        self.assertEqual(case.act(case.owner, 2, "delete_source"), "rejected_action")
        self.assertEqual(case.act(case.owner, 2, "write_report"), "draft_created")
        self.assertEqual(case.receive(case.response(request, "result", result["payload"])), "stale_owner")

    async def test_handoff_waits_for_work_and_retry_needs_failure(self):
        case = Case()
        case.delegate("coordinator", "snapshot-ready.json")
        with self.assertRaises(ValueError):
            case.offer_handoff("coordinator", "report-writer")
        with self.assertRaises(ValueError):
            case.delegate("coordinator", "snapshot-ready.json")
        with self.assertRaises(PermissionError):
            case.delegate("someone-else", "snapshot-ready.json")

    async def test_merger_tracks_expected_tasks(self):
        case, _, _, _ = await self.ready()
        merged = case.merge(["read-notes", "read-policy"])
        self.assertFalse(merged["complete"])
        self.assertEqual(merged["missing_tasks"], ["read-policy"])
        with self.assertRaises(ValueError):
            case.merge([])

    def test_path_cannot_escape_fixtures(self):
        with self.assertRaises(ValueError):
            read_fixture("../README.md")

    def test_message_shape(self):
        case = Case()
        self.assertEqual(case.receive({"message_id": "x"}), "malformed_message")
        self.assertEqual(case.receive(["bad"]), "malformed_message")
        self.assertIsNone(case.events[-1]["message_id"])


if __name__ == "__main__":
    unittest.main()
