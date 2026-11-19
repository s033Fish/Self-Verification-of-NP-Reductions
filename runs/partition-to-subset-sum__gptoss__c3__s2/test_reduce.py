import unittest
import random
from problems import SOURCE, TARGET
from reduce import reduce

class TestReduction(unittest.TestCase):
    def test_exhaustive_small(self):
        # Exhaustively test all instances with up to 4 numbers, values 0..3
        for instance in SOURCE.enumerate_instances(scale=4):
            with self.subTest(instance=instance):
                yes_src = SOURCE.is_yes(instance)
                reduced = reduce(instance)
                yes_tgt = TARGET.is_yes(reduced)
                self.assertEqual(yes_src, yes_tgt,
                                 f"Mismatch for {instance}, reduced {reduced}")

    def test_random(self):
        rng = random.Random(0)
        for _ in range(200):
            scale = rng.randint(0, 6)
            instance = SOURCE.random_instance(rng, scale)
            yes_src = SOURCE.is_yes(instance)
            reduced = reduce(instance)
            yes_tgt = TARGET.is_yes(reduced)
            self.assertEqual(yes_src, yes_tgt,
                             f"Random mismatch for {instance}, reduced {reduced}")

if __name__ == "__main__":
    unittest.main()
