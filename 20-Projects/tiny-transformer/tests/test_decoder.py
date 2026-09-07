import importlib.util
import unittest


@unittest.skipUnless(importlib.util.find_spec('torch'), 'optional CPU torch dependency not installed')
class DecoderTests(unittest.TestCase):
    def test_causal_cache_and_mask_shift(self):
        import torch
        from tiny_transformer.model import CharacterTokenizer, Config, Decoder, supervised_batch
        torch.set_num_threads(2);torch.manual_seed(1)
        tokenizer=CharacterTokenizer('hello answer')
        model=Decoder(Config(len(tokenizer.vocabulary))).eval()
        x,y=supervised_batch(tokenizer,[('hello',' answer')])
        logits,_=model(x)
        changed=x.clone();changed[0,-1]=3
        self.assertTrue(torch.allclose(logits[:,:-1],model(changed)[0][:,:-1]))
        _,cache=model(x[:,:-2]);last,_=model(x[:,-2:],cache)
        self.assertTrue(torch.allclose(logits[:,-2:],last,atol=2e-6))
        self.assertEqual(y[0,:5].tolist(),[-100]*5)
        self.assertEqual(y[0,5].item(),tokenizer.ids[' '])
        logits.retain_grad()
        torch.nn.functional.cross_entropy(logits.flatten(0,1),y.flatten(),ignore_index=-100).backward()
        self.assertEqual(logits.grad[0,:5].abs().sum().item(),0)
        self.assertGreater(logits.grad[0,5:].abs().sum().item(),0)

    def test_batch_generation_keeps_finished_rows_finished(self):
        import torch
        from tiny_transformer.model import Config, Decoder
        # Real decoder with explicit weights: token 4 -> EOS, token 5 -> 4 -> EOS.
        # A zero-output residual block isolates termination from attention/training.
        model = Decoder(Config(vocab=6, width=2, heads=1, layers=1, max_length=5))
        with torch.no_grad():
            model.tokens.weight.zero_(); model.positions.weight.zero_(); model.head.weight.zero_()
            for parameter in model.blocks.parameters():
                parameter.zero_()
            model.tokens.weight[4] = torch.tensor([1., -1.])
            model.tokens.weight[5] = torch.tensor([-1., 1.])
            model.head.weight[2] = torch.tensor([1., 0.])
            model.head.weight[4] = torch.tensor([-1., 0.])
        result = model.generate(torch.tensor([[4], [5]]), max_new_tokens=4)
        self.assertEqual(result.tolist(), [[4, 2, 0], [5, 4, 2]])

    def test_generation_budget_and_input_boundaries(self):
        import torch
        from tiny_transformer.model import Config, Decoder
        model = Decoder(Config(vocab=6, max_length=3))
        full = torch.tensor([[1, 4, 5]])
        self.assertTrue(torch.equal(model.generate(full, 2), full))
        short = full[:, :1]
        self.assertTrue(torch.equal(model.generate(short, 0), short))
        self.assertLessEqual(model.generate(short, 100).shape[1], 3)
        for ids, budget in [(torch.tensor([[1, 0]]), 1), (short, -1),
                            (torch.tensor([[1, 4, 5, 4]]), 1), (torch.empty((1, 0), dtype=torch.long), 1)]:
            with self.assertRaises(ValueError):
                model.generate(ids, budget)

    def test_right_padding_leaves_supervised_logits_unchanged(self):
        import torch
        from tiny_transformer.model import CharacterTokenizer, Config, Decoder, supervised_batch
        torch.manual_seed(3)
        tokenizer = CharacterTokenizer('Qxy')
        model = Decoder(Config(len(tokenizer.vocabulary))).eval()
        pairs = [('Q', 'x'), ('Q', 'xy')]
        batch_x, batch_y = supervised_batch(tokenizer, pairs)
        batched, _ = model(batch_x)
        for i, pair in enumerate(pairs):
            x, y = supervised_batch(tokenizer, [pair])
            individual, _ = model(x)
            self.assertTrue(torch.allclose(batched[i, :x.shape[1]], individual[0], atol=2e-6))
            self.assertEqual(batch_y[i, x.shape[1]:].tolist(), [-100] * (batch_x.shape[1] - x.shape[1]))
        with self.assertRaisesRegex(ValueError, 'at least one'):
            supervised_batch(tokenizer, [])

    def test_lora_first_step_gradient_and_scale(self):
        import torch
        from tiny_transformer.model import LoRAHead
        torch.manual_seed(4)
        base = torch.nn.Linear(3, 2, bias=False)
        head = LoRAHead(base, rank=2)
        x = torch.tensor([[1., 2., 3.]])
        self.assertTrue(torch.equal(head(x), base(x)))
        head(x).sum().backward()
        self.assertEqual(head.a.grad.abs().sum().item(), 0.)
        self.assertGreater(head.b.grad.abs().sum().item(), 0.)
        with torch.no_grad():
            head.b.add_(-0.1 * head.b.grad)
        expected = torch.nn.functional.linear(x, base.weight + head.b @ head.a)
        self.assertTrue(torch.allclose(head(x), expected))
        self.assertTrue(torch.allclose(head.merged()(x), expected))

    def test_train_reload_and_update(self):
        import tempfile
        from tiny_transformer.experiment import experiment
        with tempfile.TemporaryDirectory() as directory:
            report=experiment(directory,steps=65)
        self.assertLess(report['pretraining_loss'][1],report['pretraining_loss'][0])
        self.assertTrue(report['frozen_weights_unchanged'])


if __name__=='__main__':unittest.main()
