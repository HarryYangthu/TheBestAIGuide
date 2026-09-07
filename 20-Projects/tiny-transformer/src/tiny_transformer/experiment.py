"""Run actual pretraining, LoRA/SFT, DPO and a tiny clipped policy update on CPU."""
import argparse
from copy import deepcopy
from pathlib import Path
import json
import torch
from torch.nn import functional as F
from .model import CharacterTokenizer, Config, Decoder, LoRAHead, supervised_batch, sequence_logprob, save, load


def experiment(directory, steps=100):
    torch.manual_seed(7); torch.set_num_threads(2)
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    corpus = 'red means stop.\ngreen means go.\nblue means calm.\nQ: red?\nA: stop.\n'
    tokenizer = CharacterTokenizer(corpus + 'Q: green?\nA: go.\n')
    model = Decoder(Config(len(tokenizer.vocabulary)))
    ids = torch.tensor([tokenizer.encode(corpus, bos=True, eos=True)])
    x, y = ids[:, :-1], ids[:, 1:]
    optimizer = torch.optim.AdamW(model.parameters(), lr=.01)
    history = []
    for _ in range(steps):
        logits, _ = model(x); loss = F.cross_entropy(logits.flatten(0,1), y.flatten())
        optimizer.zero_grad(); loss.backward(); optimizer.step(); history.append(loss.item())
    assert history[-1] < history[0]
    model.eval()
    with torch.no_grad():
        full, _ = model(x)
        _, cache = model(x[:, :-1]); last, _ = model(x[:, -1:], cache)
    cache_error = (full[:, -1] - last[:, -1]).abs().max().item()
    assert cache_error < 2e-5
    save(directory/'pretrained.pt', model, tokenizer)
    restored, _ = load(directory/'pretrained.pt')
    assert torch.allclose(restored(x)[0], model(x)[0])
    pretrained_sample = tokenizer.decode(model.generate(torch.tensor([tokenizer.encode('red',bos=True)]))[0].tolist())

    # Freeze the entire pretrained decoder. Only low-rank head parameters move.
    for p in model.parameters(): p.requires_grad_(False)
    model.head = LoRAHead(model.head, rank=4)
    frozen = {n:p.detach().clone() for n,p in model.named_parameters() if not p.requires_grad}
    sx, sy = supervised_batch(tokenizer, [('Q: red?\nA:', ' stop.\n'), ('Q: green?\nA:', ' go.\n')])
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=.03)
    sft = []
    prediction_before=model(sx)[0].detach().argmax(-1).tolist()
    trainable=[{"name":n,"shape":list(p.shape),"numel":p.numel()} for n,p in model.named_parameters() if p.requires_grad]
    for _ in range(50):
        logits, _ = model(sx)
        loss = F.cross_entropy(logits.flatten(0,1), sy.flatten(), ignore_index=-100)
        optimizer.zero_grad(); loss.backward(); optimizer.step(); sft.append(loss.item())
    assert all(torch.equal(frozen[n],p) for n,p in model.named_parameters() if n in frozen)
    assert model.head.b.detach().abs().sum() > 0
    probe=model(sx)[0].detach()
    save(directory/'sft-lora.pt',model,tokenizer)
    reloaded,_=load(directory/'sft-lora.pt')
    assert torch.allclose(reloaded(sx)[0],probe)
    merged=deepcopy(model);merged.head=merged.head.merged()
    merge_error=(merged(sx)[0]-probe).abs().max().item();assert merge_error<2e-5

    # Reference policy is a frozen snapshot, not an independently hand-filled logprob.
    reference=deepcopy(model).eval()
    for p in reference.parameters():p.requires_grad_(False)
    chosen=supervised_batch(tokenizer,[('Q: red?\nA:',' stop.\n')])
    rejected=supervised_batch(tokenizer,[('Q: red?\nA:',' go.\n')])
    with torch.no_grad():ref_gap=sequence_logprob(reference,*chosen)-sequence_logprob(reference,*rejected)
    dpo=[]
    for _ in range(12):
        gap=sequence_logprob(model,*chosen)-sequence_logprob(model,*rejected)
        loss=-F.logsigmoid(.1*(gap-ref_gap)).mean()
        optimizer.zero_grad();loss.backward();optimizer.step();dpo.append(loss.item())
    assert dpo[-1]<dpo[0]

    # Enumerated two-action policy: actual gradient and parameter update. This is
    # a one-step exercise, not an implementation of a long-horizon PPO trainer.
    policy=torch.nn.Parameter(torch.tensor([0.,0.]));old=policy.detach().softmax(-1)
    advantages=torch.tensor([1.,-1.]);before=policy.detach().clone()
    ratio=policy.softmax(-1)/old
    unclipped=ratio*advantages;clipped=ratio.clamp(.8,1.2)*advantages
    ppo=-torch.minimum(unclipped,clipped).mean()
    ppo.backward()
    with torch.no_grad():policy-=.2*policy.grad
    assert not torch.equal(before,policy.detach())
    # Explicit negative-advantage clipping differs from clipping the final loss.
    ratios=torch.tensor([1.5,.5]);advs=torch.tensor([1.,-1.])
    clipped_terms=torch.minimum(ratios*advs,ratios.clamp(.8,1.2)*advs)
    assert torch.allclose(clipped_terms,torch.tensor([1.2,-.8]))
    result={'seed':7,'device':'cpu','torch':torch.__version__,'parameters':sum(p.numel() for p in model.parameters()),
            'pretraining_loss':[history[0],history[-1]],'sft_loss':[sft[0],sft[-1]],
            'sft_trainable_parameters':trainable,'sft_prediction_ids_before':prediction_before,
            'sft_prediction_ids_after':probe.argmax(-1).tolist(),
            'dpo_loss':[dpo[0],dpo[-1]],'cache_max_error':cache_error,'lora_merge_max_error':merge_error,
            'frozen_weights_unchanged':True,'checkpoint_reload_equal':True,
            'sample':pretrained_sample,'policy_probabilities_before':old.tolist(),
            'policy_probabilities_after':policy.detach().softmax(-1).tolist(),
            'positive_negative_clipped_terms':clipped_terms.tolist(),
            'evidence_boundary':'tiny constructed corpus and toy preference; no general language or heldout benchmark claim'}
    (directory/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='.runs/tiny-transformer')
    args=parser.parse_args();print(json.dumps(experiment(args.output),ensure_ascii=False,indent=2))
