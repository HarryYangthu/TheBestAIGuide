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
