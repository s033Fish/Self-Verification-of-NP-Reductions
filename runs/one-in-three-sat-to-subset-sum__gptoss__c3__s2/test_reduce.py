import unittest
import random
from problems import OneInThreeSat, SubsetSum
from reduce import reduce

class TestReduction(unittest.TestCase):
    def test_exhaustive_small(self):
        # Enumerate all instances with up to 3 variables (scale=3)
        for instance in OneInThreeSat.enumerate_instances(scale=3):
            src_yes = OneInThreeSat.is_yes(instance)
            tgt_instance = reduce(instance)
            tgt_yes = SubsetSum.is_yes(tgt_instance)
            self.assertEqual(src_yes, tgt_yes,
                f"Mismatch for instance {instance}, reduced to {tgt_instance}")

    def test_random(self):
        rng = random.Random(0)
        for _ in range(200):
            # random scale up to 5 variables
            scale = rng.randint(0,5)
            inst = OneInThreeSat.random_instance(rng, scale)
            src_yes = OneInThreeSat.is_yes(inst)
            tgt_inst = reduce(inst)
            tgt_yes = SubsetSum.is_yes(tgt_inst)
            self.assertEqual(src_yes, tgt_yes,
                f"Random mismatch for {inst} -> {tgt_inst}")

if __name__ == "__main__":
    unittest.main()
