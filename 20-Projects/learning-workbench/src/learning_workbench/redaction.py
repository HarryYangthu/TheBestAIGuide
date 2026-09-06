"""Redact credential-like fields in publishable model artifacts, after scoring.

Never treat this narrow filter as a general DLP system. Keep raw untrusted
model text out of public artifacts when it contains a credential-like field.
"""
import re

SECRET_KEY=re.compile(r'(?:api[_-]?key|rapidapi[_-]?key|password|access[_-]?token|authorization)',re.I)
SECRET_ASSIGNMENT=re.compile(r'(?:api[_-]?key|rapidapi[_-]?key|password|access[_-]?token|authorization)[^\n]{0,12}:',re.I)


def publishable(value):
    if isinstance(value,dict):
        return {k:('[REDACTED credential-like field]' if SECRET_KEY.search(k) else publishable(v)) for k,v in value.items()}
    if isinstance(value,list):return [publishable(v) for v in value]
    if isinstance(value,str) and SECRET_ASSIGNMENT.search(value):
        return '[REDACTED model text containing a credential-like field; original text excluded from publication]'
    return value
