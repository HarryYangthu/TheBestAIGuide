"""Loopback-only teaching Run API with persistent events and explicit approvals."""
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import threading
import time
from urllib.parse import urlsplit, parse_qs
from uuid import uuid4


class Conflict(ValueError): pass


class RunStore:
    def __init__(self, directory, provider=None):
        self.provider=provider;self.model_lock=threading.Lock()
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(self.directory/'runs.sqlite',check_same_thread=False)
        self.lock=threading.RLock();self.pool=ThreadPoolExecutor(max_workers=2)
        with self.db:
            self.db.execute('CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, owner TEXT, state TEXT, version INTEGER, request TEXT, result TEXT)')
            self.db.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, event TEXT, payload TEXT)')
        with self.lock:
            interrupted=self.db.execute("SELECT id FROM runs WHERE state IN ('queued','running')").fetchall()
            for (run_id,) in interrupted:
                self._transition(run_id,'queued','process_recovered')
                self.pool.submit(self._work,run_id)

    def close(self):
        self.pool.shutdown(wait=True)
        self.db.close()

    def _read(self, run_id):
        row=self.db.execute('SELECT * FROM runs WHERE id=?',(run_id,)).fetchone()
        if row is None:raise KeyError('run not found')
        return {'id':row[0],'owner':row[1],'state':row[2],'version':row[3],
                'request':json.loads(row[4]),'result':json.loads(row[5]) if row[5] else None}

    def _transition(self, run_id, state, event, result=None):
        with self.db:
            self.db.execute('UPDATE runs SET state=?,version=version+1,result=COALESCE(?,result) WHERE id=?',
                            (state,json.dumps(result,ensure_ascii=False) if result is not None else None,run_id))
            snapshot=self._read(run_id)
            self.db.execute('INSERT INTO events (run_id,event,payload) VALUES (?,?,?)',
                            (run_id,event,json.dumps({'state':state,'version':snapshot['version']},ensure_ascii=False)))
        return snapshot

    def get(self, run_id, owner):
        with self.lock:
            item=self._read(run_id)
            if item['owner']!=owner:raise KeyError('run not found')
            return item

    def create(self, owner, request):
        if set(request)-{'query','requires_approval'} or not isinstance(request.get('query'),str) or not 0<len(request['query'].strip())<=1000:
            raise ValueError('query and optional requires_approval are the only request fields')
        if type(request.get('requires_approval',False)) is not bool:raise ValueError('requires_approval must be boolean')
        run_id=uuid4().hex
        with self.lock,self.db:
            self.db.execute('INSERT INTO runs VALUES (?,?,?,?,?,NULL)',
                            (run_id,owner,'queued',0,json.dumps(request,ensure_ascii=False)))
            self.db.execute('INSERT INTO events (run_id,event,payload) VALUES (?,?,?)',
                            (run_id,'created',json.dumps({'state':'queued','version':0})))
        self.pool.submit(self._work,run_id)
        return self.get(run_id,owner)

    def action(self, run_id, owner, action, version):
        with self.lock:
            item=self.get(run_id,owner)
            if type(version) is not int or item['version']!=version:raise Conflict('stale revision; reload the run')
            if action=='approve':
                if item['state']!='awaiting_approval':raise Conflict('run is not awaiting approval')
                request={**item['request'],'approved':True}
                with self.db:
                    self.db.execute("UPDATE runs SET request=?,state='queued',version=version+1 WHERE id=?",(json.dumps(request),run_id))
                    result=self._read(run_id)
                    self.db.execute("INSERT INTO events (run_id,event,payload) VALUES (?,?,?)",(run_id,"approved",json.dumps({"state":"queued","version":result["version"]})))
                self.pool.submit(self._work,run_id)
            elif action=='cancel':
                if item['state'] in {'completed','failed','cancelled'}:raise Conflict('run is already terminal')
                result=self._transition(run_id,'cancelled','cancelled')
            else:raise ValueError('unsupported action')
            return result

    def events(self, run_id, owner, after):
        with self.lock:
            self.get(run_id,owner)
            rows=self.db.execute('SELECT id,event,payload FROM events WHERE run_id=? AND id>? ORDER BY id',(run_id,after)).fetchall()
            return [{'id':i,'event':e,'data':json.loads(p)} for i,e,p in rows]

    def _work(self, run_id):
        with self.lock:
            item=self._read(run_id)
            if item['state']!='queued':return
            request=item['request']
            if request.get('requires_approval') and not request.get('approved'):
                self._transition(run_id,'awaiting_approval','approval_required');return
            self._transition(run_id,'running','started')
        try:
            # This invokes the actual existing integrated project, not a timer
            # that fabricates a success result. Each run has an isolated directory.
            from domain_research import ResearchService
            from .cli import corpus
            service=ResearchService(self.directory/'artifacts'/run_id,corpus(),tenant=item['owner'],product='GuideDemo',version='1')
            try:result=service.run(run_id,request['query'])
            finally:service.close()
            if self.provider is not None:
                from rag_pipeline import Index
                from .retrieval import generated_answer
                index=Index()
                for document in corpus():index.upsert(document)
                with self.model_lock:
                    result["generation"]=generated_answer(index,request["query"],self.provider,tenant=item["owner"])
            with self.lock:
                if self._read(run_id)['state']=='cancelled':return
                self._transition(run_id,'completed','completed',result)
        except Exception as error:
            with self.lock:
                if self._read(run_id)['state']!='cancelled':
                    self._transition(run_id,'failed','failed',{'error_type':type(error).__name__})


def make_server(directory, port=0, tokens=None, provider=None):
    store=RunStore(directory,provider)
    tokens=tokens or {'demo-alice':'alpha','demo-bob':'beta'}
    html=Path(__file__).with_name('workbench.html').read_bytes()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send_json(self,code,data):
            body=json.dumps(data,ensure_ascii=False).encode()
            self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def owner(self):
            token=self.headers.get('Authorization','').removeprefix('Bearer ')
            if token not in tokens:raise PermissionError('demo token required')
            return tokens[token]
        def do_GET(self):
            url=urlsplit(self.path)
            if url.path=='/':
                self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8')
                self.send_header('Content-Length',str(len(html)));self.end_headers();self.wfile.write(html);return
            try:
                owner=self.owner()
                match=re.fullmatch(r'/runs/([a-f0-9]{32})(/events)?',url.path)
                if not match:raise KeyError('route not found')
                run_id=match[1];store.get(run_id,owner)
                if not match[2]:self.send_json(200,store.get(run_id,owner));return
                after=int(self.headers.get('Last-Event-ID',parse_qs(url.query).get('after',['0'])[0]))
                if after<0:raise ValueError('invalid event cursor')
                self.send_response(200);self.send_header('Content-Type','text/event-stream; charset=utf-8')
                self.send_header('Cache-Control','no-cache');self.send_header('Connection','close');self.end_headers()
                deadline=time.monotonic()+5
                while time.monotonic()<deadline:
                    for event in store.events(run_id,owner,after):
                        self.wfile.write(f"id: {event['id']}\nevent: {event['event']}\ndata: {json.dumps(event['data'])}\n\n".encode())
                        self.wfile.flush();after=event['id']
                    if store.get(run_id,owner)['state'] in {'completed','failed','cancelled','awaiting_approval'}:break
                    time.sleep(.02)
                self.close_connection=True
            except PermissionError:self.send_json(401,{'error':'unauthorized'})
            except KeyError:self.send_json(404,{'error':'not_found'})
            except (ValueError,TypeError):self.send_json(400,{'error':'invalid_request'})
            except (BrokenPipeError,ConnectionResetError):pass
        def do_POST(self):
            try:
                owner=self.owner();size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=8192:raise ValueError('body size outside limit')
                body=json.loads(self.rfile.read(size))
                if not isinstance(body,dict):raise ValueError('JSON object required')
                if self.path=='/runs':self.send_json(201,store.create(owner,body));return
                match=re.fullmatch(r'/runs/([a-f0-9]{32})/(approve|cancel)',self.path)
                if not match:raise KeyError('route not found')
                if set(body)!={'version'}:raise ValueError('current version required')
                self.send_json(200,store.action(match[1],owner,match[2],body['version']))
            except PermissionError:self.send_json(401,{'error':'unauthorized'})
            except KeyError:self.send_json(404,{'error':'not_found'})
            except Conflict as error:self.send_json(409,{'error':str(error)})
            except (ValueError,TypeError):self.send_json(400,{'error':'invalid_request'})
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.daemon_threads=True;server.store=store
    return server


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--directory',default='.runs/workbench-service')
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--provider',choices=['api','local']);parser.add_argument('--model');parser.add_argument('--revision');args=parser.parse_args()
    provider=None
    if args.provider=='api':
        from .providers import ChatAPI
        provider=ChatAPI.from_env()
    elif args.provider=='local':
        from .providers import LocalChat
        provider=LocalChat(args.model or 'Qwen/Qwen2.5-0.5B-Instruct',revision=args.revision)
    server=make_server(args.directory,args.port,provider=provider)
    print(f'Open http://127.0.0.1:{server.server_port}; demo token: demo-alice',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close();server.store.close()
