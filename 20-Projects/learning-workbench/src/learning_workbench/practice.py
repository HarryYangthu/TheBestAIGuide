"""Real local artifacts for repair, media parsing and a controlled CPU study."""
import argparse
import ast
from dataclasses import asdict
import difflib
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile


def repair(directory):
    """A deterministic coding policy edits an isolated, newly created repository."""
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    trace=[]
    with tempfile.TemporaryDirectory() as scratch:
        root=Path(scratch)
        def command(args):
            p=subprocess.run(args,cwd=root,capture_output=True,text=True,timeout=15)
            return {'argv':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
        trace.append(command(['git','init','--quiet']))
        before='def discounted(price, discount):\n    return price * discount\n'
        source=root/'price.py';source.write_text(before, encoding="utf-8")
        # Tests are fixed outside the writable proposal interface.
        tests='from price import discounted\nassert discounted(100,.2)==80\nassert discounted(100,0)==100\nassert discounted(50,1)==0\n'
        (root/'acceptance.py').write_text(tests, encoding="utf-8")
        trace.append({'event':'read_file','path':'price.py','sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'content':source.read_text(encoding="utf-8")})
        baseline=command([sys.executable,'acceptance.py']);trace.append({'event':'test_before',**baseline})
        assert baseline['returncode']!=0
        expected=hashlib.sha256(before.encode()).hexdigest()
        if hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise RuntimeError('stale patch')
        after=before.replace('price * discount','price * (1 - discount)')
        ast.parse(after);source.write_text(after, encoding="utf-8")
        trace.append({'event':'apply_patch','path':'price.py','expected_sha256':expected})
        final=command([sys.executable,'acceptance.py']);trace.append({'event':'test_after',**final})
        diff=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/price.py',tofile='b/price.py'))
        (directory/'repair.patch').write_text(diff, encoding="utf-8")
        (directory/'price.before.py.txt').write_text(before, encoding="utf-8");(directory/'price.after.py.txt').write_text(after, encoding="utf-8")
        (directory/'acceptance.py.txt').write_text(tests, encoding="utf-8")
    return {'policy':'fixed read-patch-test policy, not model-generated code','baseline_failed':baseline['returncode']!=0,
            'repaired':final['returncode']==0,'trace':trace,'diff':diff,
            'boundary':'Temporary directory is isolation of files, not a sandbox for arbitrary generated code.'}


def science(directory):
    """Actual gradient descent with a locked synthetic train/validation split."""
    import numpy as np
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    config={'seed':7,'n':120,'train_n':80,'steps':400,'learning_rate':.05,
            'question':'Can a linear model recover a linear signal on unseen samples?',
            'data_rule':'y=2*x+1+Normal(0,0.1); x~Uniform(-1,1)',
            'baseline':'training-set mean','candidate':'linear least-squares trained by gradient descent',
            'selection':'fixed before evaluation; no validation-based tuning'}
    rng=np.random.default_rng(7);x=rng.uniform(-1,1,120);y=2*x+1+rng.normal(0,.1,120)
    split=rng.permutation(120);train=split[:80];valid=split[80:]
    data=[{'id':i,'x':float(x[i]),'y':float(y[i]),'split':'train' if i in train else 'validation'} for i in range(120)]
    data_bytes=json.dumps(data,sort_keys=True).encode();(directory/'data.json').write_bytes(data_bytes)
    (directory/'config.json').write_text(json.dumps(config,indent=2)+'\n', encoding="utf-8")
    w=b=0.;history=[]
    for step in range(config['steps']):
        error=w*x[train]+b-y[train]
        history.append({'step':step,'train_mse':float(np.mean(error**2))})
        w-=.05*float(2*np.mean(error*x[train]));b-=.05*float(2*np.mean(error))
    baseline=float(np.mean((y[valid]-np.mean(y[train]))**2));candidate=float(np.mean((w*x[valid]+b-y[valid])**2))
    report={'config':'config.json','data':'data.json','data_sha256':hashlib.sha256(data_bytes).hexdigest(),
            'history':'training.json','baseline_validation_mse':baseline,'candidate_validation_mse':candidate,
            'weights':{'w':w,'b':b},'n_validation':40,'hypothesis_supported_on_this_split':candidate<baseline,
            'boundary':'One constructed linear dataset and one split; not a paper reproduction or evidence of real-world superiority.'}
    (directory/'training.json').write_text(json.dumps(history,indent=2)+'\n', encoding="utf-8")
    return report


def media(directory):
    from reportlab.pdfgen import canvas
    from pypdf import PdfReader
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    path=directory/'comparison.pdf'
    c=canvas.Canvas(str(path),pagesize=(400,300),invariant=1)
    c.setTitle('Original teaching fixture: DEMO thermal limits')
    c.drawString(30,260,'DEMO manual v1. Disconnect power before inspection.')
    c.drawString(30,220,'Model DEMO-A   Maximum 70 C')
    c.drawString(30,180,'Model DEMO-B   Maximum 60 C')
    c.showPage();c.drawString(30,260,'DEMO manual v2. Disconnect power before inspection.')
    c.drawString(30,220,'Model DEMO-A   Maximum 68 C')
    c.drawString(30,180,'Do not transfer limits between versions.')
    c.showPage();c.rect(30,100,200,100);c.showPage();c.save()
    digest=hashlib.sha256(path.read_bytes()).hexdigest();reader=PdfReader(path);cells=[]
    for page_no,page in enumerate(reader.pages,1):
        def visitor(text,cm,tm,font,size):
            if text.strip():cells.append({'source':path.name,'sha256':digest,'page':page_no,'text':text.strip(),
                'origin_pdf_points':[tm[4],tm[5]],'font_size':size,'coordinate_system':'PDF bottom-left points; text origin, not a bounding box'})
        page.extract_text(visitor_text=visitor)
    def lookup(model,version,unit='C'):
        if unit!='C':return {'abstained':True,'reason':'requested unit not represented'}
        hits=[r for r in cells if r['page']==version and f'Model {model} ' in r['text']]
        return {'abstained':not bool(hits),'evidence':hits}
    from .documents import parse_pdf,error_rate
    return {'license':'original fixture authored for this repository; no third-party page reproduced',
            'pages':parse_pdf(path),'regions':cells,'checks':{'v1':lookup('DEMO-A',1),'v2':lookup('DEMO-A',2),
                'wrong_row':lookup('DEMO-C',1),'wrong_unit':lookup('DEMO-A',1,'F'),'empty_page_requires_ocr':parse_pdf(path)[2]['requires_ocr']},
            'transcript_exercise':{'reference':'power off before inspection','hypothesis':'power on before inspection',
                'wer':error_rate('power off before inspection','power on before inspection'),
                'boundary':'manual transcript comparison; no ASR or audio comprehension claimed'}}


def tokenizer_experiment(tokenizer):
    from tiny_transformer.model import CharacterTokenizer,Config,Decoder
    import torch
    texts=['你好，注意力','x = a @ b.T\n','🙂  two spaces','<|im_start|>system']
    char=CharacterTokenizer(''.join(texts));model=Decoder(Config(len(char.vocabulary)))
    rows=[]
    for text in texts:
        ids=tokenizer.encode(text,add_special_tokens=False)
        messages=[{'role':'user','content':text}]
        chat=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True)
        own=char.encode(text)
        rows.append({'text':text,'real_ids':ids,'real_pieces':tokenizer.convert_ids_to_tokens(ids),
                     'raw_tokens':len(ids),'chat_tokens':len(chat),'template_overhead':len(chat)-len(ids),
                     'character_ids':own,'embedding_shape':list(model.tokens(torch.tensor([own])).shape)})
    return {'tokenizer_class':type(tokenizer).__name__,'special_tokens':tokenizer.special_tokens_map,
            'character_special_ids':{k:char.ids[k] for k in ['<pad>','<bos>','<eos>','<unk>']},
            'unknown_character_ids':char.encode('Ω'),'rows':rows,
            'boundary':'literal special-token-looking user text requires host/template policy; never silently treat it as a trusted system message'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('task',choices=['repair','science','media'])
    parser.add_argument('--output',required=True);args=parser.parse_args()
    result=globals()[args.task](args.output)
    Path(args.output,'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n', encoding="utf-8")
    print(json.dumps({'task':args.task,'output':args.output}))
