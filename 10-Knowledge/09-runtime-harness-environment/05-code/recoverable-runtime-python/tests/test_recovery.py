import tempfile, unittest
from pathlib import Path
from recoverable_runtime import EventStore,LocalLedger,Runner,InjectedCrash

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)
        self.open()
    def open(self):
        self.store=EventStore(self.path/'events.sqlite')
        self.ledger=LocalLedger(self.path/'ledger.sqlite')
        self.runner=Runner(self.store,self.ledger)
    def close(self): self.store.close();self.ledger.close()
    def tearDown(self): self.close();self.tmp.cleanup()

    def test_crashes_reopen_and_exactly_one_effect(self):
        for point in ['before_effect','after_effect','after_checkpoint']:
            with self.subTest(point=point):
                with self.assertRaises(InjectedCrash): self.runner.execute(point,'charge',10,point)
                self.close();self.open()
                self.runner.execute(point,'charge',10)
                self.runner.execute(point,'charge',10)
                self.assertEqual(self.runner.replay(point)['charge']['status'],'completed')
        self.assertEqual(self.ledger.snapshot()['charge_count'],3)
        self.assertEqual(self.ledger.snapshot()['net'],30)

    def test_changed_input_rejected(self):
        self.runner.execute('r','x',10)
        with self.assertRaises(ValueError): self.runner.execute('r','x',11)
        self.assertEqual(self.ledger.snapshot()['net'],10)

    def test_replay_has_no_effect(self):
        self.runner.execute('r','x',10)
        before=self.ledger.snapshot()
        self.runner.replay('r');self.runner.replay('r')
        self.assertEqual(self.ledger.snapshot(),before)

    def test_compensation_retry_after_crash(self):
        self.runner.execute('r','x',10)
        with self.assertRaises(InjectedCrash): self.runner.compensate('r','x',True)
        self.close();self.open()
        self.runner.compensate('r','x');self.runner.compensate('r','x')
        self.assertEqual(self.ledger.snapshot()['refund_count'],1)
        self.assertEqual(self.ledger.snapshot()['net'],0)
        self.assertEqual(self.runner.replay('r')['x']['status'],'compensated')
        with self.assertRaises(ValueError): self.runner.execute('r','x',10)

    def test_pending_compensation_requires_reconciliation(self):
        with self.assertRaises(InjectedCrash): self.runner.execute('r','x',10,'after_effect')
        with self.assertRaises(ValueError): self.runner.compensate('r','x')
        self.runner.execute('r','x',10)
        self.runner.compensate('r','x')
        self.assertEqual(self.ledger.snapshot()['net'],0)

    def test_key_separates_run_and_step(self):
        self.runner.execute('a:b','c',2);self.runner.execute('a','b:c',3)
        self.assertEqual(self.ledger.snapshot()['charge_count'],2)

if __name__=='__main__': unittest.main()
