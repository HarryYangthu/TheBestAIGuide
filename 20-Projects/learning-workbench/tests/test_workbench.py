import asyncio
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from learning_workbench.providers import parse_object,ProviderError,ChatAPI
from learning_workbench.cli import read_jsonl,corpus
from learning_workbench.documents import markdown_blocks,parent_evidence
from learning_workbench.experiments import context_experiment,statistics_experiment,queue_experiment


class WorkbenchTests(unittest.TestCase):
    def test_context_and_stats(self):
        self.assertEqual(len(context_experiment()['refused_cases']),2)
        report=statistics_experiment()['report']
        self.assertGreater(report['task_bootstrap_95'][1]-report['task_bootstrap_95'][0],report['naive_trial_bootstrap_95'][1]-report['naive_trial_bootstrap_95'][0])
    def test_blocks_keep_preconditions(self):
        text='# A\n\nPower off.\n\n| M | C |\n| - | - |\n| A | 70 |\n\n```py\nx=1\n```\n'
        blocks=markdown_blocks(text)
        for b in blocks:self.assertEqual(text[b.start:b.end],b.text)
        table=next(b for b in blocks if b.kind=='table')
        self.assertIn('Power off.',''.join(b.text for b in parent_evidence(table,blocks)))
        self.assertEqual(len([b for b in blocks if b.kind=='code']),1)
    def test_generation_citation_contract(self):
        from learning_workbench.retrieval import generated_answer
        from learning_workbench.providers import Completion
        from rag_pipeline import Index
        index=Index()
        for doc in corpus():index.upsert(doc)
        class Provider:
            corrupt=False
            def complete(self,messages,**kwargs):
                evidence=json.loads(messages[-1]['content'])['evidence'][0]
                claim={'text':'Inspect only after disconnecting power.','source_id':evidence['id'],'quote':evidence['text'] if not self.corrupt else 'fabricated quotation'}
                return Completion(json.dumps({'abstained':False,'reason':'fixture','claims':[claim]}),'contract-fixture',1,1,0,'test-only')
        provider=Provider()
        answer=generated_answer(index,'FAN-01',provider,tenant='alpha',version='1')
        self.assertTrue(answer['citation_identity_valid'])
        self.assertEqual(answer['semantic_support'],'requires independent grading')
        provider.corrupt=True
        with self.assertRaises(ProviderError):generated_answer(index,'FAN-01',provider,tenant='alpha',version='1')

    def test_memory_tasks(self):
        from learning_workbench.memory import evaluate_memory
        with tempfile.TemporaryDirectory() as d:rows=evaluate_memory(read_jsonl('memory-tasks.jsonl'),d)
        self.assertTrue(all(r['correct'] for r in rows),rows)
    def test_negated_memory_never_becomes_a_positive_preference(self):
        from learning_workbench.memory import MemoryAssistant, extract_preference, preference
        for text in ['我以后不要用表格', '我以后用表格或段落', 'I always avoid tables',
                     '我以后希望小王用表格', '我以后转述“用表格回答”']:
            with self.subTest(text=text):
                candidate=extract_preference(text,subject='alice',source='chat:negative')
                self.assertFalse(candidate['accepted'])
                self.assertIn('unsupported',candidate['reason'])
        self.assertIsNone(preference('a stable explanation'))
        for text in ['这次无需使用表格', 'I cannot use tables', '取消表格，正常解释']:
            with self.subTest(current=text):
                with self.assertRaisesRegex(ValueError,'unsupported'):
                    preference(text)
        for text,expected in [('这次用表格','table'), ('这次用段落解释State和Memory','paragraph'),
                              ('请用列表回答','bullets'), ('Use tables','table'),
                              ('Please use bullets to explain State and Memory','bullets')]:
            with self.subTest(current=text):
                self.assertEqual(preference(text),expected)
        with tempfile.TemporaryDirectory() as d:
            assistant=MemoryAssistant(Path(d)/'memory.sqlite')
            try:
                assistant.remember('我以后希望用表格',subject='alice',source='chat:1',now=1)
                rejected=assistant.remember('我以后不要用表格',subject='alice',source='chat:2',now=2)
                self.assertFalse(rejected['accepted'])
                self.assertEqual(assistant.store.get('alice','answer_format',2).version,1)
                # Unsupported current language must be surfaced, not silently
                # answered in the old table style the user just rejected.
                for task in ['这次不要用表格','这次无需使用表格','I cannot use tables','取消表格，正常解释']:
                    with self.subTest(task=task), self.assertRaisesRegex(ValueError,'unsupported'):
                        assistant.reply(task,subject='alice',now=3)
            finally:assistant.close()
    def test_replan(self):
        from learning_workbench.planning import research_demo,Plan,Task
        report=asyncio.run(research_demo())
        self.assertEqual(report['invalidated'],['research-a','reviewer','writer'])
        with self.assertRaises(ValueError):Plan([Task('a',('a',),None)])
    def test_queue_load(self):
        unlimited=asyncio.run(queue_experiment(max_queue=0))
        bounded=asyncio.run(queue_experiment(max_queue=3))
        self.assertEqual(unlimited['completed'],30)
        self.assertGreater(len(bounded['rejected']),0)
        self.assertLessEqual(bounded['max_depth'],3)
        self.assertEqual(bounded['completed']+len(bounded['rejected']),30)
    def test_strict_provider_json(self):
        for text in ['[]','{"x":NaN}','{"a":1} extra']:
            with self.assertRaises(ProviderError):parse_object(text)
        self.assertEqual(parse_object('```json\n{"x":1}\n```'),{'x':1})
        with self.assertRaises(ValueError):ChatAPI('http://example.com','model','key')
    def test_coding_repair(self):
        from learning_workbench.practice import repair
        with tempfile.TemporaryDirectory() as d:r=repair(d)
        self.assertTrue(r['baseline_failed'] and r['repaired'])
    def test_a2a_over_http(self):
        from learning_workbench.a2a_demo import demo,Agent,RPCError
        r=demo();self.assertEqual(len(r['trace']),7)
        a=Agent('test');msg={'message':{'kind':'message','role':'user','messageId':'a','parts':[{'kind':'text','text':'NEED_INPUT'}]}}
        first=a.call('message/send',msg);msg['message']['parts'][0]['text']='other'
        with self.assertRaises(RPCError):a.call('message/send',msg)
        a.call('tasks/cancel',{'id':first['id']})
        with self.assertRaises(RPCError):a.call('tasks/cancel',{'id':first['id']})
    @unittest.skipUnless(importlib.util.find_spec('pypdf') and importlib.util.find_spec('reportlab'),'optional PDF dependencies absent')
    def test_pdf_source_to_evidence(self):
        from learning_workbench.practice import media
        with tempfile.TemporaryDirectory() as d:r=media(d)
        self.assertTrue(r['checks']['empty_page_requires_ocr'])
        self.assertTrue(r['checks']['wrong_row']['abstained'])
        self.assertIn('68 C',r['checks']['v2']['evidence'][0]['text'])


class ServiceTests(unittest.TestCase):
    def test_generation_preserves_the_service_source_version(self):
        from learning_workbench.server import RunStore
        from learning_workbench.providers import Completion
        class EvidenceInspector:
            """Inspect the transport contract; this is not a model-quality test."""
            evidence=None
            def complete(self,messages,**kwargs):
                self.evidence=json.loads(messages[-1]['content'])['evidence']
                return Completion(json.dumps({'abstained':True,'reason':'scope inspection','claims':[]}),
                                  'contract-fixture',0,0,0,'test-only')
        with tempfile.TemporaryDirectory() as d:
            provider=EvidenceInspector();store=RunStore(d,provider)
            try:
                row=store.create('alpha',{'query':'FAN-01'})
                deadline=time.monotonic()+4
                while row['state'] not in {'completed','failed'} and time.monotonic()<deadline:
                    time.sleep(.01);row=store.get(row['id'],'alpha')
                self.assertEqual(row['state'],'completed',row)
                self.assertTrue(provider.evidence)
                self.assertEqual({e['version'] for e in provider.evidence},{'1'})
                self.assertEqual({c['version'] for c in row['result']['citations']},{'1'})
            finally:store.close()

    def test_http_approval_replay_owner_and_persistence(self):
        from learning_workbench.server import make_server,RunStore
        with tempfile.TemporaryDirectory() as d:
            server=make_server(d);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            url=f'http://127.0.0.1:{server.server_port}'
            def req(path,body=None,token='demo-alice',headers=None):
                request=Request(url+path,data=json.dumps(body).encode() if body is not None else None,
                    headers={'Authorization':'Bearer '+token,'Content-Type':'application/json',**(headers or {})})
                with urlopen(request,timeout=7) as r:return r.read().decode()
            def wait(run_id,state):
                deadline=time.monotonic()+4
                while time.monotonic()<deadline:
                    row=json.loads(req('/runs/'+run_id))
                    if row['state']==state:return row
                    if row['state']=='failed':self.fail(row)
                    time.sleep(.01)
                self.fail('state timeout: '+str(row))
            try:
                run=json.loads(req('/runs',{'query':'FAN-01','requires_approval':True}));rid=run['id']
                pending=wait(rid,'awaiting_approval')
                with self.assertRaises(HTTPError) as e:req('/runs/'+rid,token='demo-bob')
                self.assertEqual(e.exception.code,404)
                stream=req('/runs/'+rid+'/events');self.assertIn('approval_required',stream)
                last=max(int(x[4:]) for x in stream.splitlines() if x.startswith('id: '))
                self.assertEqual(req('/runs/'+rid+'/events',headers={'Last-Event-ID':str(last)}),'')
                with self.assertRaises(HTTPError) as e:req('/runs/'+rid+'/approve',{'version':-1})
                self.assertEqual(e.exception.code,409)
                req('/runs/'+rid+'/approve',{'version':pending['version']});done=wait(rid,'completed')
                self.assertIsNotNone(done['result'])
                replay=req('/runs/'+rid+'/events',headers={'Last-Event-ID':str(last)})
                self.assertIn('completed',replay);self.assertNotIn('approval_required',replay)
                other=json.loads(req('/runs',{'query':'FAN-01','requires_approval':True}));paused=wait(other['id'],'awaiting_approval')
                req('/runs/'+other['id']+'/cancel',{'version':paused['version']});wait(other['id'],'cancelled')
            finally:server.shutdown();server.server_close();thread.join();server.store.close()
            store=RunStore(d)
            try:self.assertEqual(store.get(rid,'alpha')['state'],'completed')
            finally:store.close()
    def test_chat_api_transport_and_usage(self):
        from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
        received=[]
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_POST(self):
                received.append(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
                raw=json.dumps({'model':'fixture','choices':[{'message':{'content':'{"answer":"ok"}'},'finish_reason':'stop'}],
                                'usage':{'prompt_tokens':3,'completion_tokens':4}}).encode()
                self.send_response(200);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            result=ChatAPI(f'http://127.0.0.1:{server.server_port}/v1','fixture','demo-key').complete([{'role':'user','content':'hello'}],json_mode=True)
            self.assertEqual((result.input_tokens,result.output_tokens),(3,4));self.assertEqual(received[0]['response_format'],{'type':'json_object'})
        finally:server.shutdown();server.server_close();thread.join()


if __name__=='__main__':unittest.main()
