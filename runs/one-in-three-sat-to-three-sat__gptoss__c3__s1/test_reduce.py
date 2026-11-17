import unittest
import random
import problems
from reduce import reduce

class TestReduction(unittest.TestCase):
    def test_random_instances(self):
        rng = random.Random(0)
        for scale in range(0, 6):
            for _ in range(50):
                inst = problems.SOURCE.random_instance(rng, scale)
                problems.SOURCE.validate(inst)
                red = reduce(inst)
                problems.TARGET.validate(red)
                self.assertEqual(
                    problems.SOURCE.is_yes(inst),
                    problems.TARGET.is_yes(red),
                    msg=f"Mismatch on instance {inst} reduced to {red}",
                )
    def test_empty_formula(self):
        for m in range(0, 5):
            inst = {"num_vars": m, "clauses": []}
            problems.SOURCE.validate(inst)
            red = reduce(inst)
            problems.TARGET.validate(red)
            self.assertTrue(problems.SOURCE.is_yes(inst))
            self.assertTrue(problems.TARGET.is_yes(red))

if __name__ == '__main__':
    unittest.main()
