import unittest
from copy import deepcopy
from evidence import CELLS, structured_answer, verify_claim, demo

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.q=dict(doc_id='latency',version=1,row='B',column='p95')
        self.a=structured_answer(CELLS,**self.q)
    def test_valid_and_wrong_units(self):
        self.assertTrue(verify_claim(CELLS,self.a,self.q))
        self.assertFalse(verify_claim(CELLS,{**self.a,'unit':'s'},self.q))
        self.assertFalse(verify_claim(CELLS,{**self.a,'value':60},self.q))
    def test_location_and_version(self):
        bad=deepcopy(self.a);bad['citation']['page']=2
        self.assertFalse(verify_claim(CELLS,bad,self.q))
        self.assertFalse(verify_claim(CELLS,self.a,{**self.q,'version':2}))
    def test_missing_and_ambiguous(self):
        with self.assertRaises(ValueError): structured_answer(CELLS,**{**self.q,'row':'C'})
        with self.assertRaises(ValueError): structured_answer(CELLS+CELLS,**self.q)
    def test_demo(self):
        result=demo()
        self.assertEqual(result['baseline_correct'],2)
        self.assertEqual(result['structured_correct'],3)

if __name__ == '__main__': unittest.main()
