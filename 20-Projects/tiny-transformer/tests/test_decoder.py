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
    def test_train_reload_and_update(self):
        import tempfile
        from tiny_transformer.experiment import experiment
        with tempfile.TemporaryDirectory() as directory:
            report=experiment(directory,steps=65)
        self.assertLess(report['pretraining_loss'][1],report['pretraining_loss'][0])
        self.assertTrue(report['frozen_weights_unchanged'])


if __name__=='__main__':unittest.main()
