import unittest
import random
from problems import ThreeColoring, IndependentSet
from reduce import reduce as reduction

class TestReduction(unittest.TestCase):
    def test_random_instances(self):
        rng = random.Random(0)
        for scale in range(1, 5):  # small scales
            for _ in range(50):
                inst = ThreeColoring.random_instance(rng, scale)
                src_ans = ThreeColoring.is_yes(inst)
                red = reduction(inst)
                tgt_ans = IndependentSet.is_yes(red)
                self.assertEqual(src_ans, tgt_ans,
                                 f"Mismatch on instance {inst}, reduced {red}")

    def test_edge_cases(self):
        # n = 0
        inst0 = {"n": 0, "edges": []}
        self.assertTrue(ThreeColoring.is_yes(inst0))
        red0 = reduction(inst0)
        self.assertTrue(IndependentSet.is_yes(red0))
        # n <= 3 always yes
        for n in range(1, 4):
            # empty edges
            inst = {"n": n, "edges": []}
            self.assertTrue(ThreeColoring.is_yes(inst))
            red = reduction(inst)
            self.assertTrue(IndependentSet.is_yes(red))
        # K4 is not 3-colorable
        n = 4
        edges = [[i, j] for i in range(n) for j in range(i+1, n)]
        k4 = {"n": n, "edges": edges}
        self.assertFalse(ThreeColoring.is_yes(k4))
        red_k4 = reduction(k4)
        self.assertFalse(IndependentSet.is_yes(red_k4))

if __name__ == '__main__':
    unittest.main()
