import json
from pathlib import Path
import tempfile
import unittest
from agent_loop import Action, EvidenceModel, ScriptedModel, Tool, default_tools, run_agent


class LoopTests(unittest.TestCase):
    def test_evidence_and_trace(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / "trace.jsonl")
            state = run_agent(EvidenceModel(), default_tools(), "上下文", trace_path=path)
            self.assertEqual(state.status, "completed")
            self.assertIn("[doc-1]", state.answer)
            events = [json.loads(line) for line in Path(path).read_text().splitlines()]
            self.assertEqual([e['seq'] for e in events], list(range(len(events))))
            self.assertEqual(events[-1]['kind'], 'run_finished')

    def test_invalid_model(self):
        state = run_agent(ScriptedModel([Action("invented")]), {}, "test")
        self.assertEqual(state.stop_reason, "invalid_model_output")

    def test_tool_error_is_observation(self):
        state = run_agent(ScriptedModel([Action("tool", "search", {"query": 2}), Action("finish", answer="invalid")]), default_tools(), "x")
        self.assertEqual(state.observations[0]["error"]["code"], "invalid_arguments")

    def test_no_progress(self):
        actions = [Action("tool", "search", {"query": "上下文"})] * 5
        state = run_agent(ScriptedModel(actions), default_tools(), "x")
        self.assertEqual(state.stop_reason, "no_progress")
        self.assertEqual(state.steps, 2)

    def test_budget(self):
        state = run_agent(ScriptedModel([Action("tool", "search", {"query": "上下文"})]), default_tools(), "x", max_steps=1)
        self.assertEqual(state.stop_reason, "max_steps")

    def test_permission_and_unknown(self):
        for tools, code in [({}, "unknown_tool"), ({"x": Tool(lambda a: 1, allowed=False)}, "permission_denied")]:
            state = run_agent(ScriptedModel([Action("tool", "x"), Action("finish", answer="stop")]), tools, "x")
            self.assertEqual(state.observations[0]["error"]["code"], code)

    def test_model_cannot_mutate_state(self):
        class BadModel:
            def decide(self, state):
                state.observations.append({"fake": True})
                return Action("finish", answer="done")
        self.assertEqual(run_agent(BadModel(), {}, "x").observations, [])

    def test_non_json_arguments_and_output_stay_in_error_boundary(self):
        invalid = Action("tool", "x", {"query": "test", 2: 3})
        state = run_agent(ScriptedModel([invalid]), {}, "x")
        self.assertEqual(state.stop_reason, "invalid_model_output")
        with tempfile.TemporaryDirectory() as folder:
            trace = str(Path(folder) / "trace.jsonl")
            state = run_agent(ScriptedModel([Action("tool", "x"), Action("finish", answer="bad output")]),
                              {"x": Tool(lambda _: {"normal": 1, 2: 3})}, "x", trace_path=trace)
            self.assertEqual(state.observations[0]["error"]["code"], "invalid_output")
            self.assertEqual(json.loads(Path(trace).read_text().splitlines()[-1])["kind"], "run_finished")

    def test_tool_mutation_cannot_rewrite_previous_observations_or_events(self):
        shared = {"value": 1}
        def mutate(_):
            shared["value"] = 9
            return shared
        actions = [Action("tool", "read"), Action("tool", "mutate"), Action("finish", answer="done")]
        with tempfile.TemporaryDirectory() as folder:
            trace = str(Path(folder) / "trace.jsonl")
            state = run_agent(ScriptedModel(actions), {"read": Tool(lambda _: shared), "mutate": Tool(mutate)}, "x", trace_path=trace)
            self.assertEqual([o["data"]["value"] for o in state.observations], [1, 9])
            events = [json.loads(line) for line in Path(trace).read_text().splitlines()]
            results = [e["data"]["data"]["value"] for e in events if e["kind"] == "tool_result"]
            self.assertEqual(results, [1, 9])


if __name__ == "__main__":
    unittest.main()
