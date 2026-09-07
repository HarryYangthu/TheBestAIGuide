import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rag_lab.retrieval import Index,chunks,assemble,fuse
from rag_lab.metrics import answer_score,evidence_score,score_prediction
from rag_lab.pipeline import read_data,run
from verify import verify


class RAGTests(unittest.TestCase):
    def test_official_style_answer_scoring(self):
        self.assertEqual(answer_score('The United States.','United States'),{'em':1,'f1':1.0})
        self.assertEqual(answer_score('yes indeed','yes')['f1'],0)
        self.assertAlmostEqual(answer_score('red blue','red green')['f1'],.5)

    def test_support_requires_both_documents(self):
        score=evidence_score([['A',0],['A',0]],[['A',0],['B',2]])
        self.assertEqual(score['recall'],.5);self.assertEqual(score['complete'],0)

    def test_source_mapping_chunking_and_budget(self):
        docs=chunks({'title':['A'],'sentences':[['one','two','three','four']]},3)
        self.assertEqual(docs[1]['facts'],[['A',3]])
        selected,used=assemble(docs,[(0,1),(1,0)],budget=1)
        self.assertEqual(selected,[]);self.assertEqual(used,0)

    def test_bm25_finds_rare_term(self):
        docs=[{'title':'a','text':'cat dog'},{'title':'b','text':'rarekeyword'}]
        self.assertEqual(Index(docs).rank('rarekeyword')[0][0],1)
        self.assertEqual(fuse([(0,1),(1,0)],[(1,1),(0,0)])[0][0],0)

    def test_wrong_answer_with_real_citation_is_not_correct(self):
        context={'title':['A'],'sentences':[['Paris is in France.']]}
        selected=chunks(context)
        score=score_prediction({'answer':'Germany','citations':[['A',0]]},'France',[['A',0]],context,selected)
        self.assertEqual(score['em'],0);self.assertEqual(score['citation_validity'],1)
        score=score_prediction({'answer':'France','citations':[['fake',0]]},'France',[['A',0]],context,selected)
        self.assertEqual(score['citation_validity'],0)

    def test_data_disjoint_with_valid_support(self):
        dev,ev=read_data('dev'),read_data('eval')
        self.assertEqual((len(dev),len(ev)),(20,100))
        self.assertFalse({r['id'] for r in dev}&{r['id'] for r in ev})
        for row in dev+ev:
            available=dict(zip(row['context']['title'],row['context']['sentences']))
            for title,i in zip(row['supporting_facts']['title'],row['supporting_facts']['sent_id']):
                self.assertTrue(0<=i<len(available[title]))

    def test_generation_wire_contract_and_bad_planner(self):
        from unittest.mock import patch
        from io import BytesIO
        from rag_lab.model import Model
        with patch.dict('os.environ', {'RAG_MODEL':'test-model','RAG_API_KEY':'test-only'}):
            model=Model()
            payload={'choices':[{'message':{'content':'{}'}}]}
            with patch('urllib.request.urlopen',return_value=BytesIO(json.dumps(payload).encode())) as transport:
                with self.assertRaises(ValueError): model.ask('Question?',[],plan=True)
            body=json.loads(transport.call_args.args[0].data)
            user=json.loads(body['messages'][1]['content'])
            self.assertEqual(set(user),{'question','evidence'})
            self.assertEqual(model.calls,1)
            self.assertEqual(model.events[0]['response_text'],'{}')
            self.assertNotIn('test-only',json.dumps(model.events))

    def test_active_iteration_budget_and_retained_failure(self):
        from unittest.mock import patch
        class FakeModel:
            name='test-only-not-a-real-model'
            calls=0
            tokens=0
            def ask(self,question,selected,plan=False):
                self.calls+=1
                if plan: return {'query':'follow-up query'}
                raise ValueError('deliberate invalid output')
        with tempfile.TemporaryDirectory() as temp, patch('rag_lab.pipeline.Model',FakeModel):
            result=run(Path(temp)/'active',split='dev',methods=('active',),generation='live',limit=1)
            self.assertEqual(result['rows'][0]['calls'],3)
            self.assertEqual(len(result['rows'][0]['rounds']),3)
            self.assertEqual(result['summary']['active']['answer_em'],0)
            self.assertEqual(result['summary']['active']['errors'],1)
            self.assertFalse(result['acceptance']['passed'])
            checked=verify(Path(temp)/'active')
            self.assertTrue(checked['passed'])
            self.assertFalse(checked['experiment_passed'])

    def test_acceptance_and_coherent_tampering(self):
        import copy
        from rag_lab.report import render
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'run'
            original=run(path,split='dev',methods=('bm25','tfidf'),limit=1)
            def save(bundle):
                (path/'summary.json').write_text(json.dumps({k:v for k,v in bundle.items() if k!='rows'}))
                (path/'results.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in bundle['rows']))
                render(bundle,path)
            mutations=[
                lambda b:b['acceptance'].update(passed=False),
                lambda b:b['rows'][0].update(context_chars=0),
                lambda b:b['rows'][0].update(question='forged question'),
                lambda b:b['rows'][0]['recall'].update({'5':float('nan')}),
                lambda b:b['rows'][0]['ranking'].append(b['rows'][0]['ranking'][0]),
            ]
            for mutate in mutations:
                with self.subTest(mutation=mutate):
                    changed=copy.deepcopy(original);mutate(changed);save(changed)
                    self.assertFalse(verify(path)['passed'])
            save(original)
            (path/'paired-recall.json').write_text('{}')
            self.assertIn('paired_comparison_mismatch',verify(path)['errors'])

    def test_reference_comparison_and_configuration_guard(self):
        from compare import compare
        with tempfile.TemporaryDirectory() as temp:
            a,b=Path(temp)/'a',Path(temp)/'b'
            run(a,split='dev',methods=('bm25',),limit=1)
            run(b,split='dev',methods=('bm25',),limit=1)
            self.assertTrue(compare(a,b)['passed'])
            c=Path(temp)/'c'
            run(c,split='dev',methods=('bm25',),limit=1,top_k=10)
            result=compare(c,a)
            self.assertFalse(result['passed'])
            self.assertEqual(result['fields'],['top_k'])
            from unittest.mock import patch
            original_rank=Index.rank
            def reversed_rank(index,query,method='bm25'):
                return list(reversed(original_rank(index,query,method)))
            d=Path(temp)/'d'
            with patch.object(Index,'rank',reversed_rank):
                run(d,split='dev',methods=('bm25',),limit=1)
            self.assertTrue(verify(d)['passed'])
            changed=compare(d,a)
            self.assertFalse(changed['passed'])
            self.assertEqual(changed['reason'],'different_scores')
            self.assertGreater(changed['changed_rows'],0)


    def test_end_to_end_and_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'run'
            result=run(path,split='dev',limit=2)
            self.assertTrue(result['acceptance']['passed'])
            self.assertTrue(verify(path)['passed'])
            rows=[json.loads(line) for line in (path/'results.jsonl').read_text().splitlines()]
            rows[0]['ranking'][0]['text']='forged source'
            (path/'results.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
            self.assertFalse(verify(path)['passed'])

if __name__=='__main__': unittest.main()
