import unittest
from eval_harness import EvalTask,run_suite,summarize,compare,wilson,pass_at_k
from eval_harness.graders import matches


class HarnessTests(unittest.TestCase):
    def task(self,**kwargs):
        return EvalTask("t",{"request":"x"},{"output":{"ok":True},"state":{"count":1}},
                        {"count":0},critical=True,**kwargs)

    def test_fixture_isolation_labels_private(self):
        t=self.task()
        def system(request,state,emit):
            self.assertNotIn("expected",request)
            state["count"]+=1
            emit("work",count=state["count"])
            return {"ok":True}
        rows=run_suite([t],system,3)
        self.assertTrue(all(r.success for r in rows))
        self.assertEqual(t.fixture["count"],0)
        self.assertEqual(rows[0].events[1]["type"],"work")

    def test_final_state_not_self_report(self):
        rows=run_suite([self.task()],lambda req,state,emit:{"ok":True})
        self.assertFalse(rows[0].success)
        self.assertFalse(rows[0].checks["state:count"])

    def test_errors_counted_not_excluded(self):
        def fail(*args): raise TimeoutError("do not print secret traceback")
        rows=run_suite([self.task()],fail)
        self.assertEqual(summarize(rows)["system_errors"],1)
        self.assertEqual(rows[0].error,"TimeoutError")
        self.assertFalse(rows[0].success)

    def test_forbidden_exact_string_and_type(self):
        task=EvalTask("leak",{}, {"output":{"ok":True},"forbidden_strings":["SECRET"]})
        r=run_suite([task],lambda *args:{"ok":True,"text":"SECRET"})[0]
        self.assertFalse(r.success)
        self.assertFalse(matches(1,True))
        self.assertFalse(matches({}, {"missing":None}))

    def test_gate_detects_regression_and_mismatch(self):
        t=EvalTask("x",{}, {"output":{"ok":True}},critical=True)
        good=run_suite([t],lambda *a:{"ok":True})
        bad=run_suite([t],lambda *a:{"ok":False})
        self.assertFalse(compare(good,bad)["passed"])
        self.assertEqual(compare(good,bad)["regressed_tasks"],["x"])
        self.assertTrue(compare(bad,good)["passed"])
        with self.assertRaises(ValueError):compare(good,[])
        with self.assertRaises(ValueError):run_suite([t,t],lambda *a:{})

    def test_statistical_examples_and_boundaries(self):
        low,high=wilson(8,10)
        self.assertAlmostEqual(low,.4901624715366417)
        self.assertAlmostEqual(high,.9433178485456247)
        self.assertAlmostEqual(pass_at_k(10,2,3),.5333333333333333)
        self.assertGreater(wilson(0,10)[1],0)
        self.assertLess(wilson(10,10)[0],1)
        for args in [(0,0,1),(2,3,1),(2,1,3)]:
            with self.assertRaises(ValueError):pass_at_k(*args)
        with self.assertRaises(ValueError):wilson(0,0)

    def test_bad_grader_configuration_rejected_before_run(self):
        for expected in ({"output":["ok"]},{"state":[]},
                         {"forbidden_strings":"SECRET"},{"forbidden_strings":[None]},
                         {"forbidden_strings":[""]},[]):
            with self.assertRaises(ValueError):EvalTask("bad",{},expected)


if __name__ == "__main__": unittest.main()
