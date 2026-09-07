import unittest
from application_cases import visible_documents, choose_model, operations_recommendation, correct_price, science_search

class ApplicationCases(unittest.TestCase):
    def test_bug_and_patch(self):
        buggy = lambda amount, discount: amount-discount
        self.assertNotEqual(buggy(100,.1),90)
        self.assertEqual(correct_price(100,.1),90)
        for amount, discount, expected in [(0,.5,0),(100,0,100),(100,1,0)]:
            self.assertEqual(correct_price(amount,discount),expected)
        for amount,discount in [(-1,.1),(100,-.1),(100,1.1),(float("nan"),.1),(float("inf"),.1),(100,float("nan"))]:
            with self.assertRaises(ValueError): correct_price(amount,discount)
    def test_cross_tenant_and_principal(self):
        docs=[{'id':'a','tenant':'A','readers':['alice']},{'id':'b','tenant':'B','readers':['bob']}]
        self.assertEqual([d['id'] for d in visible_documents(docs,'A','alice')],['a'])
        self.assertEqual(visible_documents(docs,'A','bob'),[])
        self.assertEqual(visible_documents(docs,'B','alice'),[])
    def test_capability_before_price(self):
        models=[{'name':'cheap','capabilities':{'text'},'cost':1}, {'name':'tools','capabilities':{'text','tools'},'cost':2}]
        self.assertEqual(choose_model(models,{'tools'},2),'tools')
        with self.assertRaises(ValueError): choose_model(models,{'tools'},1)
    def test_operations_is_a_recommendation(self):
        self.assertEqual(operations_recommendation({'error_rate':.08,'started_after_release':True})['action'],'request_rollback_review')
        self.assertEqual(operations_recommendation({'error_rate':.08,'started_after_release':False})['action'],'collect_more_evidence')
    def test_no_feasible_science_candidate(self):
        with self.assertRaises(ValueError): science_search([16,32],100)
        self.assertEqual(science_search([4,8,16],100)['width'],8)

if __name__=='__main__': unittest.main()
