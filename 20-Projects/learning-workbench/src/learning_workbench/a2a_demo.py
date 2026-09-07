"""Loopback teaching subset of A2A 0.3.0 JSON-RPC, not a conformance SDK."""
from copy import deepcopy
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import threading
from urllib.request import Request,urlopen
from uuid import uuid4


class RPCError(ValueError):
    def __init__(self,code,message):self.code,self.message=code,message


class Agent:
    def __init__(self,name):self.name=name;self.tasks={};self.messages={};self.lock=threading.Lock()
    def call(self,method,params):
        with self.lock:
            if method in {'tasks/get','tasks/cancel'}:
                task=self.tasks.get(params.get('id'))
                if task is None:raise RPCError(-32001,'Task not found')
                if method=='tasks/cancel':
                    if task['status']['state'] in {'completed','canceled','failed'}:raise RPCError(-32002,'Task cannot be canceled')
                    task['status']={'state':'canceled'}
                return deepcopy(task)
            if method!='message/send':raise RPCError(-32601,'Method not found')
            msg=params.get('message')
            if not isinstance(msg,dict) or msg.get('kind')!='message' or msg.get('role')!='user' or not isinstance(msg.get('messageId'),str) or not msg['messageId']:
                raise RPCError(-32602,'Expected a user Message with messageId')
            parts=msg.get('parts')
            if not isinstance(parts,list) or not parts or any(not isinstance(p,dict) or p.get('kind')!='text' or not isinstance(p.get('text'),str) for p in parts):
                raise RPCError(-32005,'Only TextPart supported')
            fingerprint=json.dumps(msg,sort_keys=True)
            if msg['messageId'] in self.messages:
                old,task_id=self.messages[msg['messageId']]
                if old!=fingerprint:raise RPCError(-32602,'messageId reused with different content')
                return deepcopy(self.tasks[task_id])
            task_id=msg.get('taskId')
            if task_id:
                task=self.tasks.get(task_id)
                if task is None:raise RPCError(-32001,'Task not found')
                if task['status']['state']!='input-required':raise RPCError(-32602,'Task is not accepting more input')
                if msg.get('contextId') not in {None,task['contextId']}:raise RPCError(-32602,'contextId mismatch')
            else:
                task_id=str(uuid4());task={'kind':'task','id':task_id,'contextId':msg.get('contextId') or str(uuid4()),'status':{'state':'submitted'},'history':[]}
                self.tasks[task_id]=task
            task['history'].append(deepcopy(msg));text='\n'.join(p['text'] for p in parts)
            if text=='NEED_INPUT':task['status']={'state':'input-required'}
            else:
                task['status']={'state':'completed'}
                task['artifacts']=[{'artifactId':str(uuid4()),'name':self.name+'-evidence',
                                    'parts':[{'kind':'text','text':self.name+': '+text}]}]
            self.messages[msg['messageId']]=(fingerprint,task_id)
            return deepcopy(task)


def endpoint(name,port=0):
    agent=Agent(name)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def reply(self,value,code=200):
            raw=json.dumps(value).encode();self.send_response(code);self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        def do_GET(self):
            if self.path!='/.well-known/agent-card.json':self.reply({'error':'not_found'},404);return
            self.reply({'protocolVersion':'0.3.0','name':name,'description':'Local text handoff teaching subset',
                        'url':f'http://127.0.0.1:{self.server.server_port}/','preferredTransport':'JSONRPC','version':'0.1.0',
                        'capabilities':{'streaming':False,'pushNotifications':False},'defaultInputModes':['text/plain'],
                        'defaultOutputModes':['text/plain'],'skills':[{'id':'echo-evidence','name':'Echo evidence','description':'Carry text as a task artifact','tags':['teaching']}]})
        def do_POST(self):
            request={}
            try:
                size=int(self.headers.get('Content-Length',0))
                if not 0<size<=16384:raise RPCError(-32600,'Invalid request size')
                request=json.loads(self.rfile.read(size))
                if not isinstance(request,dict):request={};raise RPCError(-32600,'Invalid request')
                if request.get('jsonrpc')!='2.0' or 'id' not in request:raise RPCError(-32600,'Request id required by this subset')
                if not isinstance(request.get('params'),dict):raise RPCError(-32602,'params must be object')
                result=agent.call(request.get('method'),request['params'])
                self.reply({'jsonrpc':'2.0','id':request['id'],'result':result})
            except json.JSONDecodeError:self.reply({'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Parse error'}})
            except RPCError as e:self.reply({'jsonrpc':'2.0','id':request.get('id'),'error':{'code':e.code,'message':e.message}})
            except (ValueError,TypeError):self.reply({'jsonrpc':'2.0','id':request.get('id'),'error':{'code':-32602,'message':'Invalid params'}})
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler);server.agent=agent
    return server


def demo():
    servers=[endpoint('researcher'),endpoint('reviewer')];threads=[];trace=[]
    for s in servers:
        t=threading.Thread(target=s.serve_forever,daemon=True);t.start();threads.append(t)
    def call(n,method,params):
        request={'jsonrpc':'2.0','id':str(uuid4()),'method':method,'params':params}
        with urlopen(Request(f'http://127.0.0.1:{servers[n].server_port}/',data=json.dumps(request).encode(),headers={'Content-Type':'application/json'}),timeout=5) as r:result=json.load(r)
        trace.append({'endpoint':n,'request':request,'response':result});return result
    def message(text,**kw):return {'message':{'kind':'message','role':'user','messageId':str(uuid4()),'parts':[{'kind':'text','text':text}],**kw}}
    try:
        pending=message('NEED_INPUT');first=call(0,'message/send',pending)['result']
        replay=call(0,'message/send',pending)['result'];assert replay['id']==first['id']
        completed=call(0,'message/send',message('Evidence: DEMO-A limit=70 C',taskId=first['id'],contextId=first['contextId']))['result']
        call(0,'tasks/get',{'id':first['id']})
        review=call(1,'message/send',message(completed['artifacts'][0]['parts'][0]['text']))['result']
        other=call(0,'message/send',message('NEED_INPUT'))['result'];cancelled=call(0,'tasks/cancel',{'id':other['id']})['result']
        assert completed['status']['state']=='completed' and cancelled['status']['state']=='canceled'
        return {'protocol':'A2A 0.3.0 text JSON-RPC subset','trace':trace,'handoff_artifact':review['artifacts'],
                'boundary':'Echo workers, in-memory tasks, local messageId dedup extension. No model reasoning, auth, push, streaming or full conformance claim.'}
    finally:
        for s in servers:s.shutdown();s.server_close()
        for t in threads:t.join()


if __name__=='__main__':print(json.dumps(demo(),ensure_ascii=False,indent=2))
