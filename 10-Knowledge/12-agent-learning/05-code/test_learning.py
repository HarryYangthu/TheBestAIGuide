import unittest
import math
from learning import validate_splits, masked_nll, dpo_loss, group_advantages, weak_reward, guarded_reward

class LearningTests(unittest.TestCase):
    def test_leakage(self):
        with self.assertRaises(ValueError):
            validate_splits([{'task_group':'a','split':'train'}, {'task_group':'a','split':'test'}])
        self.assertEqual(validate_splits([{'task_group':'a','split':'train'}]), 1)
    def test_mask_ignores_context_probabilities(self):
        self.assertAlmostEqual(masked_nll([.8,.5,.25],[0,1,1]), masked_nll([.1,.5,.25],[0,1,1]))
        with self.assertRaises(ValueError): masked_nll([.9],[0])
    def test_dpo_and_equal_groups(self):
        self.assertAlmostEqual(dpo_loss(-2,-3,-2,-3), math.log(2))
        self.assertLess(dpo_loss(-1,-4,-2,-3), math.log(2))
        self.assertEqual(group_advantages([1,1,1]), [0,0,0])
    def test_false_positive(self):
        fake = {'answer':'PASS','policy_allowed':True,'external_tests_passed':False}
        self.assertEqual(weak_reward(fake),1)
        self.assertEqual(guarded_reward(fake),0)
        fake.update(policy_allowed=False,external_tests_passed=True)
        self.assertEqual(guarded_reward(fake),-1)

if __name__ == '__main__': unittest.main()
