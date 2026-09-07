"""Two-session memory exercise reusing the repository's SQLite MemoryStore."""
from dataclasses import asdict
import re
from state_memory import MemoryStore


FORMAT_PATTERNS = {
    'table': r'表格|\btables?\b',
    'bullets': r'分条|列表|\bbullets?\b',
    'paragraph': r'段落|\bparagraphs?\b',
}
DURABLE_FORMATS = (
    r'(?:我以后|我一直|以后请给我)\s*(?:希望|喜欢|习惯)?\s*(?:用|使用)?\s*'
    r'(?:表格|分条|列表|段落)(?:回答|回复|作答)?[。.!！]?',
    r'(?:I always|For future replies)[ ,]*(?:prefer|use)?\s*'
    r'(?:tables?|bullets?|paragraphs?)[.!]?',
)
CURRENT_FORMATS = (
    r'(?:这次|本次)?\s*请?\s*(?:用|使用)\s*(?:表格|分条|列表|段落)'
    r'(?:回答|回复|作答|解释\s*State\s*和\s*Memory)?[。.!！]?',
    r'(?:please\s+)?use\s+(?:tables?|bullets?|paragraphs?)'
    r'(?:\s+to explain State and Memory)?[.!]?',
)


def preference(text):
    """Recognize one affirmative format; reject rather than invert a negation.

    Only complete affirmative templates are accepted. Any format mention in
    another sentence is unsupported: do not infer intent from a keyword or a
    list of negation words. The caller must expose that limitation.
    """
    matches = [name for name, pattern in FORMAT_PATTERNS.items()
               if re.search(pattern, text, re.I)]
    if not matches:
        return None
    if len(matches) != 1 or not any(
            re.fullmatch(pattern, text.strip(), re.I)
            for pattern in (*DURABLE_FORMATS, *CURRENT_FORMATS)):
        raise ValueError('unsupported format expression; use one complete affirmative template')
    return matches[0]


def extract_preference(text, *, subject, source):
    # Limited, inspectable grammar. A statement about another person never
    # inherits the authenticated subject merely because a model suggested it.
    text = text.strip()
    persistent = re.search(r'^(我以后|我一直|以后请给我|I always|For future replies)', text, re.I)
    transient = any(x in text for x in ['这次', '今天', '临时', 'this time', 'today'])
    try:
        value = preference(text)
    except ValueError as error:
        return {'accepted': False, 'reason': str(error)}
    if not persistent or transient or value is None:
        return {'accepted': False, 'reason': 'not an explicit durable self-preference'}
    if not any(re.fullmatch(pattern, text, re.I) for pattern in DURABLE_FORMATS):
        return {'accepted': False, 'reason': 'unsupported preference grammar; use one direct self-preference'}
    return {'accepted': True, 'subject': subject, 'key': 'answer_format',
            'value': value, 'source': source}


class MemoryAssistant:
    def __init__(self, db): self.store = MemoryStore(str(db))
    def close(self): self.store.close()

    def remember(self, text, *, subject, source, now, ttl=None):
        candidate = extract_preference(text, subject=subject, source=source)
        if not candidate['accepted']: return candidate
        old = self.store.get(subject, candidate['key'], now)
        # A deletion/expiry may leave a tombstone: require a new explicit
        # user preference and use the stored version rather than overwriting.
        row = self.store.db.execute('SELECT version FROM memories WHERE subject=? AND key=?',
                                    (subject, candidate['key'])).fetchone()
        version = row[0] if row else 0
        saved = self.store.put(subject, candidate['key'], candidate['value'], source=source,
                                now=now, ttl=ttl, expected_version=version)
        return {'accepted': True, 'memory': asdict(saved), 'replaced': old is not None}

    def reply(self, task, *, subject, now, use_memory=True):
        # An unsupported current instruction must not silently fall back to an
        # older table preference that the user has just negated.
        current = preference(task)
        saved = self.store.get(subject, 'answer_format', now) if use_memory else None
        style = current or (saved.value if saved else 'paragraph')
        facts = [('State', '当前任务事实'), ('Memory', '供以后任务检索的信息')]
        if style == 'table':
            text = '| 概念 | 含义 |\n| --- | --- |\n' + '\n'.join('| '+a+' | '+b+' |' for a,b in facts)
        elif style == 'bullets': text = '\n'.join('- '+a+'：'+b for a,b in facts)
        else: text = '；'.join(a+'是'+b for a,b in facts)+'。'
        context = {'task': task, 'selected_memory': asdict(saved) if saved else None,
                   'current_instruction_wins': current is not None}
        return {'format': style, 'text': text, 'context': context,
                'policy': 'rule-based format rendering; not a general conversational model'}


def evaluate_memory(tasks, directory):
    """Each JSONL task is independent; data labels never enter the assistant."""
    from pathlib import Path
    results=[]
    for task in tasks:
        assistant=MemoryAssistant(Path(directory)/(task['id']+'.sqlite'))
        events=[]
        try:
            for event in task['events']:
                if event['kind']=='remember':
                    args={k:v for k,v in event.items() if k!='kind'}
                    events.append(assistant.remember(**args))
                elif event['kind']=='forget':
                    events.append({'forgotten':assistant.store.forget(event['subject'],'answer_format')})
            answers={name:assistant.reply(**task['request'],use_memory=flag)
                     for name,flag in [('without_memory',False),('with_memory',True)]}
            expected=task['expected_format']
            results.append({'id':task['id'],'events':events,'answers':answers,'expected':expected,
                            'correct':answers['with_memory']['format']==expected,
                            'baseline_correct':answers['without_memory']['format']==expected})
        finally: assistant.close()
    return results
