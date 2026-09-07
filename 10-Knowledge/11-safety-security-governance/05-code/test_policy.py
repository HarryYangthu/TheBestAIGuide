import unittest
from policy_lab import Principal,Proposal,PolicyRuntime,Denied,fixture,injection_cases

class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.rt=fixture();self.user=Principal('learner','A',frozenset({'read','delete'}))

    def test_positive_and_injection_proposals(self):
        for name,text,proposal,allowed in injection_cases():
            with self.subTest(name=name):
                if allowed: self.assertIn('text',self.rt.execute(self.user,'r',proposal))
                else:
                    with self.assertRaises(Denied): self.rt.execute(self.user,'r',proposal)
        self.assertIn('a1',self.rt.records)
        self.assertNotIn('fixture-secret-A',str(self.rt.audit))

    def test_approved_delete_and_reuse_rejected(self):
        proposal=Proposal('delete_record','a2')
        token=self.rt.approve(self.user,'r',proposal)
        self.assertEqual(self.rt.execute(self.user,'r',Proposal('delete_record','a2',token)),{'deleted':'a2'})
        with self.assertRaises(Denied): self.rt.execute(self.user,'r',Proposal('delete_record','a2',token))
        # 先重新放回同 ID 的资源，排除“只是因为对象已消失才拒绝”的假阳性。
        self.rt.records['a2'] = {'tenant': 'A', 'text': '新创建的草稿'}
        with self.assertRaises(Denied):
            self.rt.execute(self.user, 'r', Proposal('delete_record', 'a2', token))
        self.assertIn('a2', self.rt.records)

    def test_approval_bound_to_run_resource_and_user(self):
        token=self.rt.approve(self.user,'r',Proposal('delete_record','a2'))
        for user,run,target in [(self.user,'r2','a2'),(self.user,'r','a1'),
                                (Principal('other','A',self.user.scopes),'r','a2')]:
            with self.assertRaises(Denied): self.rt.execute(user,run,Proposal('delete_record',target,token))
        self.assertIn('a2',self.rt.records)

    def test_scope_and_expiry(self):
        readonly=Principal('reader','A',frozenset({'read'}))
        with self.assertRaises(Denied): self.rt.approve(readonly,'r',Proposal('delete_record','a1'))
        token=self.rt.approve(self.user,'r',Proposal('delete_record','a1'))
        binding,_=self.rt.approvals[token]
        self.rt.approvals[token]=(binding,0)
        with self.assertRaises(Denied): self.rt.execute(self.user,'r',Proposal('delete_record','a1',token))

    def test_projection_redacts_secret(self):
        out=self.rt.execute(self.user,'r',Proposal('read_record','a1'))
        self.assertEqual(set(out),{'id','text'})
        self.assertNotIn('fixture-secret-A',str(out))

if __name__=='__main__': unittest.main()
