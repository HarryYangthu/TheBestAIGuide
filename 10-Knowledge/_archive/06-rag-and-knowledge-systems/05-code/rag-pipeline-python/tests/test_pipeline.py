import unittest
from dataclasses import replace
from rag_pipeline import Document, Index, answer, verify_citation, rrf, retrieval_metrics, bm25
from rag_pipeline.chunking import chunk_document


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.idx=Index()
        for d in [Document("fan","ALM-12003 fan check supply", "a", "X", "2", ("ALM-12003",)),
                  Document("near","ALM-12030 supply alarm", "a", "X", "2", ("ALM-12030",)),
                  Document("fan","ALM-12003 SECRET", "b", "X", "2", ("ALM-12003",)),
                  Document("wrong","ALM-12003 wrong product", "a", "Y", "2", ("ALM-12003",))]:
            self.idx.upsert(d)

    def test_acl_product_version_identifier(self):
        hits=self.idx.search("ALM-12003",tenant="a",product="X",version="2")
        self.assertEqual([h.chunk.doc_id for h in hits],["fan"])
        self.assertNotIn("SECRET",str(hits))
        self.assertEqual(self.idx.search("ALM-12003",tenant="a",product="X",version="1"),[])
        self.assertEqual(self.idx.search("ALM-12003",tenant="unknown"),[])

    def test_update_delete_and_stale_citation(self):
        old=answer(self.idx,"ALM-12003",tenant="a",product="X").citations[0]
        self.idx.upsert(Document("fan","ALM-12003 updated", "a", "X", "3", ("ALM-12003",)))
        self.assertFalse(verify_citation(self.idx,old,tenant="a"))
        new=answer(self.idx,"ALM-12003",tenant="a",product="X").citations[0]
        self.assertTrue(verify_citation(self.idx,new,tenant="a"))
        self.assertFalse(verify_citation(self.idx,replace(new,quote="fabricated"),tenant="a"))
        self.assertTrue(self.idx.delete("fan",tenant="a"))
        self.assertTrue(answer(self.idx,"ALM-12003",tenant="a",product="X").abstained)
        self.assertFalse(verify_citation(self.idx,new,tenant="a"))
        self.assertTrue(self.idx.search("ALM-12003",tenant="b"))

    def test_chunk_offsets_and_long_block(self):
        doc=Document("d","# Title\n\nalpha beta\n\nlongparagraph")
        chunks=chunk_document(doc,8)
        self.assertTrue(any(c.split for c in chunks))
        for c in chunks:
            self.assertEqual(doc.text[c.start:c.end],c.text)
        with self.assertRaises(ValueError): chunk_document(doc,0)

    def test_unknown_empty_no_answer(self):
        self.assertTrue(answer(self.idx,"ALM-99999",tenant="a").abstained)
        self.assertEqual(self.idx.search("",tenant="a"),[])
        with self.assertRaises(ValueError): self.idx.search("fan",tenant="a",mode="dense")

    def test_rank_fusion_and_metrics(self):
        scores=rrf([["a","b"],["b","a"]],constant=60)
        self.assertAlmostEqual(scores["a"],1/61+1/62)
        self.assertEqual(rrf([["a","a"]]),rrf([["a"]]))
        m=retrieval_metrics(["bad","good","okay"],{"good":2,"okay":1},3)
        self.assertEqual(m["recall"],1)
        self.assertEqual(m["mrr"],.5)
        self.assertAlmostEqual(m["ndcg"],0.6590018048024133)
        self.assertIsNone(retrieval_metrics([],{})["recall"])

    def test_bm25_tf_saturates_and_empty(self):
        a,b,c=bm25("fan",["fan","fan fan","fan fan fan"],b=0)
        self.assertGreater(b,a)
        self.assertLess(c-b,b-a)
        self.assertEqual(bm25("x",[""]),[0])

    def test_callbacks_see_only_authorized_candidates(self):
        seen=[]
        def embed(texts):
            seen.extend(texts)
            return [[1.,0.] for _ in texts]  # shape fixture, not semantic quality claim
        self.idx.embedder=embed
        self.idx.reranker=lambda q,ts:list(range(len(ts)))
        self.idx.search("fan",tenant="a",product="X")
        self.assertNotIn("SECRET"," ".join(seen))
        self.idx.embedder=lambda ts:[[1.]]
        with self.assertRaises(ValueError): self.idx.search("fan",tenant="a")

    def test_multicode_document_does_not_mix_sections(self):
        idx=Index()
        idx.upsert(Document("manual","ALM-12030: Replace fan.\n\nALM-12003: Reconnect cable.",tenant="a"))
        for mode in ("bm25","exact","hybrid"):
            hits=idx.search("ALM-12003",tenant="a",mode=mode)
            self.assertEqual(len(hits),1)
            self.assertEqual(hits[0].chunk.text,"ALM-12003: Reconnect cable.")

    def test_document_top_k_deduplicates_before_cutoff(self):
        idx=Index()
        idx.upsert(Document("a","fan\n\nfan\n\nfan"))
        idx.upsert(Document("b","fan second"))
        hits=idx.search("fan",tenant="public",k=2,unit="document")
        self.assertEqual(len({h.chunk.doc_id for h in hits}),2)


if __name__ == "__main__": unittest.main()
