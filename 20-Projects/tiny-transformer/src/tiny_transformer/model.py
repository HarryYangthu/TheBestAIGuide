from dataclasses import asdict, dataclass
import math
import torch
from torch import nn
from torch.nn import functional as F


class CharacterTokenizer:
    """Explicit special IDs; unknown characters never silently disappear."""
    def __init__(self, text='', vocabulary=None):
        self.vocabulary = vocabulary or ['<pad>', '<bos>', '<eos>', '<unk>'] + sorted(set(text))
        self.ids = {t: i for i, t in enumerate(self.vocabulary)}
    def encode(self, text, bos=False, eos=False):
        return ([1] if bos else []) + [self.ids.get(c, 3) for c in text] + ([2] if eos else [])
    def decode(self, ids):
        return ''.join(self.vocabulary[i] if i > 3 else ('�' if i == 3 else '') for i in ids)


@dataclass
class Config:
    vocab: int
    width: int = 32
    heads: int = 4
    layers: int = 2
    max_length: int = 128


class Attention(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        if cfg.width % cfg.heads: raise ValueError('width must divide into heads')
        self.heads, self.depth = cfg.heads, cfg.width // cfg.heads
        self.qkv = nn.Linear(cfg.width, 3 * cfg.width)
        self.projection = nn.Linear(cfg.width, cfg.width)

    def forward(self, x, past=None):
        batch, length, width = x.shape
        q, k, v = self.qkv(x).chunk(3, dim=-1)
        def split(t): return t.view(batch, length, self.heads, self.depth).transpose(1, 2)
        q, k, v = map(split, (q, k, v))
        prefix = 0 if past is None else past[0].shape[-2]
        if past is not None:
            k = torch.cat([past[0], k], dim=-2)
            v = torch.cat([past[1], v], dim=-2)
        scores = q @ k.transpose(-2, -1) / math.sqrt(self.depth)
        query_positions = torch.arange(prefix, prefix + length, device=x.device)[:, None]
        key_positions = torch.arange(k.shape[-2], device=x.device)[None, :]
        scores = scores.masked_fill(key_positions > query_positions, float('-inf'))
        # Last dimension enumerates candidate keys for each query position.
        weights = scores.softmax(dim=-1)
        joined = (weights @ v).transpose(1, 2).contiguous().view(batch, length, width)
        return self.projection(joined), (k, v)


class Block(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.norm1 = nn.LayerNorm(cfg.width)
        self.attention = Attention(cfg)
        self.norm2 = nn.LayerNorm(cfg.width)
        self.ffn = nn.Sequential(nn.Linear(cfg.width, cfg.width * 4), nn.GELU(),
                                 nn.Linear(cfg.width * 4, cfg.width))
    def forward(self, x, past=None):
        value, present = self.attention(self.norm1(x), past)
        x = x + value
        return x + self.ffn(self.norm2(x)), present


class Decoder(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.tokens = nn.Embedding(cfg.vocab, cfg.width)
        self.positions = nn.Embedding(cfg.max_length, cfg.width)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.layers)])
        self.norm = nn.LayerNorm(cfg.width)
        self.head = nn.Linear(cfg.width, cfg.vocab, bias=False)

    def forward(self, ids, past=None):
        prefix = 0 if past is None else past[0][0].shape[-2]
        if prefix + ids.shape[1] > self.cfg.max_length: raise ValueError('context window exceeded')
        positions = torch.arange(prefix, prefix + ids.shape[1], device=ids.device)
        x = self.tokens(ids) + self.positions(positions)
        present = []
        for i, block in enumerate(self.blocks):
            x, kv = block(x, None if past is None else past[i]); present.append(kv)
        return self.head(self.norm(x)), present

    @torch.no_grad()
    def generate(self, ids, max_new_tokens=24):
        """Greedy decoding for nonempty, equal-length, unpadded prompts.

        Return [B, <= max_length]. Each row stops at its first generated EOS;
        rows that finish early receive PAD while the other rows continue.
        """
        if ids.ndim != 2 or not ids.shape[0] or not ids.shape[1]:
            raise ValueError('ids must be a nonempty [batch, length] tensor')
        if not isinstance(max_new_tokens, int) or isinstance(max_new_tokens, bool) or max_new_tokens < 0:
            raise ValueError('max_new_tokens must be a nonnegative integer')
        if ids.shape[1] > self.cfg.max_length:
            raise ValueError('context window exceeded')
        if bool((ids == 0).any()):
            raise ValueError('generate expects unpadded prompts; run unequal lengths separately')
        self.eval()
        remaining = min(max_new_tokens, self.cfg.max_length - ids.shape[1])
        finished = ids[:, -1] == 2
        if remaining == 0 or bool(finished.all()):
            return ids.clone()
        logits, cache = self(ids)
        out = ids
        for step in range(remaining):
            nxt = logits[:, -1].argmax(-1, keepdim=True)
            # Finished rows stay finished even when the next model argmax is not EOS.
            nxt = nxt.masked_fill(finished[:, None], 0)
            out = torch.cat([out, nxt], dim=1)
            finished |= nxt[:, 0] == 2
            if bool(finished.all()) or step + 1 == remaining:
                break
            logits, cache = self(nxt, cache)
        return out


class LoRAHead(nn.Module):
    """Head-only LoRA; alpha=rank, so the usual alpha/rank factor is 1."""
    def __init__(self, base, rank=4):
        super().__init__()
        self.base, self.rank = base, rank
        self.a = nn.Parameter(torch.empty(rank, base.in_features))
        self.b = nn.Parameter(torch.zeros(base.out_features, rank))
        nn.init.kaiming_uniform_(self.a, a=math.sqrt(5))
        for p in base.parameters(): p.requires_grad_(False)
    def forward(self, x): return self.base(x) + F.linear(F.linear(x, self.a), self.b)
    def merged(self):
        out = nn.Linear(self.base.in_features, self.base.out_features, bias=False)
        with torch.no_grad(): out.weight.copy_(self.base.weight + self.b @ self.a)
        return out


def supervised_batch(tokenizer, pairs):
    """Right-pad teacher-forced [B,T] inputs; labels ignore prompt and padding.

    Effective labels precede right padding, so the causal mask prevents them
    from attending to PAD. This does not support left padding or packed rows.
    """
    rows, labels = [], []
    for prompt, answer in pairs:
        prefix = tokenizer.encode(prompt, bos=True)
        ids = prefix + tokenizer.encode(answer, eos=True)
        rows.append(ids[:-1])
        # Logit j predicts token j+1. The first answer label is at len(prefix)-1.
        labels.append([-100] * (len(prefix)-1) + ids[len(prefix):])
    if not rows:
        raise ValueError('at least one prompt/answer pair is required')
    n = max(map(len, rows))
    x = torch.tensor([row + [0]*(n-len(row)) for row in rows])
    y = torch.tensor([row + [-100]*(n-len(row)) for row in labels])
    return x, y


def sequence_logprob(model, x, y):
    logits, _ = model(x)
    mask = y != -100
    safe = y.masked_fill(~mask, 0)
    return (logits.log_softmax(-1).gather(-1, safe[..., None]).squeeze(-1) * mask).sum(-1)


def save(path, model, tokenizer):
    torch.save({'config': asdict(model.cfg), 'vocabulary': tokenizer.vocabulary,
                'rank': model.head.rank if isinstance(model.head, LoRAHead) else None,
                'weights': model.state_dict()}, path)


def load(path):
    data = torch.load(path, map_location='cpu', weights_only=True)
    model = Decoder(Config(**data['config']))
    if data['rank']: model.head = LoRAHead(model.head, data['rank'])
    model.load_state_dict(data['weights'])
    return model.eval(), CharacterTokenizer(vocabulary=data['vocabulary'])
