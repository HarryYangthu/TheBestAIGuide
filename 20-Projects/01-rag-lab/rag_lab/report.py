import json
import html
from pathlib import Path


def render(bundle, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    output = Path(output)
    summaries = bundle['summary']
    names = list(summaries)
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 3, figsize=(15, 4), constrained_layout=True)
    for name, summary in summaries.items():
        axes[0].plot([1, 3, 5, 10, 20], [summary['recall'][str(k)] for k in [1,3,5,10,20]], marker='o', label=name)
    axes[0].set(xlabel='Retrieved chunks (K)', ylabel='Supporting-fact recall', ylim=(0,1), title='Evidence recall @ K')
    axes[0].legend(fontsize=8)
    axes[1].bar(names, [summaries[n]['context_complete'] for n in names], color='#277c8e')
    axes[1].set(ylabel='Fraction of questions', ylim=(0,1), title='All gold evidence in context')
    axes[1].tick_params(axis='x', rotation=25)
    axes[2].boxplot([[r['retrieval_ms'] for r in bundle['rows'] if r['method']==n] for n in names], tick_labels=names)
    axes[2].set(ylabel='Milliseconds / question', title='Measured retrieval latency')
    axes[2].tick_params(axis='x', rotation=25)
    for ext in ('svg','png'):
        fig.savefig(output / ('retrieval.' + ext), dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9,4), constrained_layout=True)
    stages = ['candidate@20', 'selected@K', 'context budget']
    for name in names:
        ax.plot(stages,[summaries[name]['candidate_complete'], summaries[name]['selected_complete'], summaries[name]['context_complete']],marker='o',label=name)
    ax.set(ylim=(0,1),ylabel='Questions with complete evidence',title='Where evidence is lost')
    ax.legend()
    for ext in ('svg','png'): fig.savefig(output / ('evidence-loss.' + ext),dpi=160)
    plt.close(fig)
    if 'bm25' in names and len(names) > 1:
        baseline = {r['id']: r for r in bundle['rows'] if r['method'] == 'bm25'}
        comparison = {}
        for name in names:
            if name == 'bm25': continue
            deltas = [r['recall']['5'] - baseline[r['id']]['recall']['5'] for r in bundle['rows'] if r['method'] == name]
            comparison[name] = {'improved': sum(x > 1e-10 for x in deltas),
                                'same': sum(abs(x) <= 1e-10 for x in deltas),
                                'regressed': sum(x < -1e-10 for x in deltas)}
        fig, ax = plt.subplots(figsize=(9,4), constrained_layout=True)
        left = [0] * len(comparison)
        for key, color in [('improved','#238b78'),('same','#a8b3bf'),('regressed','#c45d4c')]:
            values = [v[key] for v in comparison.values()]
            ax.barh(list(comparison), values, left=left, label=key, color=color)
            left = [a+b for a,b in zip(left,values)]
        ax.set(xlabel='Number of questions',title='Paired Recall@5 changes versus BM25')
        ax.legend()
        for ext in ('svg','png'): fig.savefig(output / ('paired-recall.' + ext),dpi=160)
        plt.close(fig)
        (output/'paired-recall.json').write_text(json.dumps(comparison,indent=2)+'\n')
    extra = '<p>尚未执行真实模型生成：不展示虚构的准确率、调用成本或引用质量图。</p>'
    if bundle['config']['generation'] == 'live':
        fig, axes = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
        for name in names:
            group = [r for r in bundle['rows'] if r['method'] == name]
            accuracy = summaries[name]['answer_em']
            latency = sum(r['elapsed_ms'] for r in group) / len(group)
            calls = sum(r['calls'] for r in group) / len(group)
            axes[0].scatter(latency, accuracy); axes[0].annotate(name, (latency, accuracy))
            axes[1].scatter(calls, accuracy); axes[1].annotate(name, (calls, accuracy))
        axes[0].set(xlabel='Mean end-to-end latency (ms)', ylabel='Answer EM', ylim=(0,1))
        axes[1].set(xlabel='Mean model requests / question', ylabel='Answer EM', ylim=(0,1))
        for ext in ('svg','png'): fig.savefig(output / ('quality-cost.' + ext), dpi=160)
        plt.close(fig)
        extra = '<img src="quality-cost.svg" alt="回答准确率与耗时、调用量对比">'
    encoded = json.dumps(bundle,ensure_ascii=False).replace('<','\\u003c')
    page = '''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>RAG 实验验收</title><style>
body{font:16px system-ui;margin:0;background:#f4f7fa;color:#182839}main{max-width:1280px;margin:auto;padding:32px}h1{font-size:32px}small{color:#516577}.cards{display:flex;gap:16px;flex-wrap:wrap}.card,section{background:white;padding:20px;border-radius:12px;margin:12px 0;border:1px solid #dae3eb}.card{flex:1;min-width:150px}.card b{display:block;font-size:27px;color:#167485}img{width:100%}select,input{padding:10px;margin:8px;border:1px solid #aebfca;border-radius:6px;max-width:95%}table{width:100%;border-collapse:collapse}td,th{padding:10px;text-align:left;border-bottom:1px solid #e5ebf0}mark{background:#fff0b5}.cols{display:grid;grid-template-columns:1fr 1fr;gap:20px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f7fa;padding:15px} .scroll{overflow:auto;max-height:500px}@media(max-width:750px){.cols{grid-template-columns:1fr}main{padding:12px}}</style>
<main><small>项目 01 · HOTPOTQA · 可追溯实验</small><h1>答案之前，先看证据有没有找齐</h1><p id="scope"></p><div class="cards" id="cards"></div>
<section><h2>检索质量与实际耗时</h2><img src="retrieval.svg" alt="召回曲线、上下文完整率与耗时"><p>TF-IDF 是词项向量，不是预训练语义向量。图表仅包含本次实际执行的方案。</p><img src="evidence-loss.svg" alt="证据丢失阶段"></section>
<section><h2>逐题收益与退化</h2>PAIRED<p>对同一道题比较 Recall@5；改进和退化同时保留，不能只挑成功案例。</p></section><section><h2>方案结果</h2><div class="scroll"><table id="metrics"></table></div><p>未运行生成时答案指标为 N/A；异常任务仍计入分母，不能靠丢弃失败提高成绩。</p></section>
<section><h2>效果与调用成本</h2>EXTRA</section><section><h2>逐题复盘</h2><label>方案<select id="method"></select></label><label>筛选<select id="filter"><option value="all">全部</option><option value="missing">上下文缺证据</option><option value="complete">上下文证据齐全</option></select></label><label>问题<select id="question"></select></label><div id="detail"></div></section>
<section><h2>验收说明</h2><pre id="accept"></pre><p>PASS 表示数据、结果文件和指标计算满足工程检查，不表示模型答对全部题目，也不代表独立学习者已经掌握方法。</p></section>
</main><script id="data" type="application/json">BUNDLE</script><script>
const D=JSON.parse(document.getElementById('data').textContent),$=id=>document.getElementById(id),esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),pct=x=>x==null?'N/A':(100*x).toFixed(1)+'%';
$('scope').textContent=`${D.config.split} · ${D.config.scope} · 每题 ${D.config.chunk_size} 句/块 · Top-${D.config.top_k} · ${D.config.budget} 字符预算 · ${D.config.generation}`;
$('cards').innerHTML=`<div class="card">题目数<b>${D.config.questions}</b></div><div class="card">实际方案数<b>${Object.keys(D.summary).length}</b></div><div class="card">工程验收<b>${D.acceptance.passed?'PASS':'FAIL'}</b></div><div class="card">模型生成<b>${D.config.generation==='none'?'未运行':'已请求'}</b></div>`;
$('metrics').innerHTML='<tr><th>方案</th><th>Recall@5</th><th>上下文证据齐全</th><th>答案 EM</th><th>答案 F1</th><th>调用数</th><th>异常数</th></tr>'+Object.entries(D.summary).map(([n,s])=>`<tr><td>${esc(n)}</td><td>${pct(s.recall['5'])}</td><td>${pct(s.context_complete)}</td><td>${pct(s.answer_em)}</td><td>${pct(s.answer_f1)}</td><td>${s.calls}</td><td>${s.errors}</td></tr>`).join('');
$('accept').textContent=JSON.stringify(D.acceptance,null,2);
$('method').innerHTML=Object.keys(D.summary).map(n=>`<option>${esc(n)}</option>`).join('');
function choose(){const rows=D.rows.filter(r=>r.method===$('method').value&&($('filter').value==='all'||Boolean(r.context_complete)===($('filter').value==='complete')));$('question').innerHTML=rows.map(r=>`<option value="${esc(r.id)}">${esc(r.question)}</option>`).join('');detail()}
function detail(){const r=D.rows.find(r=>r.method===$('method').value&&r.id===$('question').value);if(!r){$('detail').textContent='此筛选下没有题目';return}const gold=new Set(r.gold_facts.map(x=>JSON.stringify(x)));const docs=r.ranking.map((d,i)=>`<tr><td>${i+1} ← ${d.initial_rank}</td><td>${esc(d.title)} [${d.sent_ids.join(',')}]</td><td>${d.facts.some(f=>gold.has(JSON.stringify(f)))?'标注证据':''}</td><td>${d.in_context?'已入上下文':''}</td><td>${esc(d.text)}</td></tr>`).join('');$('detail').innerHTML=`<h3>${esc(r.question)}</h3><p>${esc(r.diagnosis)}；检索 ${r.retrieval_ms.toFixed(2)} ms</p><div class="cols"><div><h4>标准答案与证据（仅验收使用）</h4><pre>${esc(r.gold_answer)}</pre>${r.gold_evidence.map(x=>`<p><mark>${esc(x.title)} [${x.sent_id}]</mark> ${esc(x.text)}</p>`).join('')}</div><div><h4>模型预测与引用</h4><pre>${esc(r.prediction?JSON.stringify(r.prediction,null,2):'未运行模型，不以标准答案代替预测')}</pre><h4>每轮查询</h4><pre>${esc(JSON.stringify(r.rounds,null,2))}</pre><h4>评分</h4><pre>${esc(JSON.stringify(r.answer_metrics,null,2))}</pre></div></div><h4>实际检索排名（最多展示 20 块）</h4><div class="scroll"><table><tr><th>现排名 ← 原排名</th><th>来源</th><th>标注</th><th>上下文</th><th>内容</th></tr>${docs}</table></div>`}
$('method').onchange=choose;$('filter').onchange=choose;$('question').onchange=detail;choose();
</script></html>'''.replace('PAIRED','<img src="paired-recall.svg" alt="逐题召回变化">' if 'bm25' in names and len(names)>1 else '<p>当前方案组合没有 BM25 配对基线。</p>').replace('EXTRA',extra).replace('BUNDLE',encoded)
    (output/'index.html').write_text(page,encoding='utf-8')
