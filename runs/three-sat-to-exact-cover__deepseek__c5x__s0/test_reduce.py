import unittest
import random
from typing import List, Dict

from problems import ThreeSat, ExactCover
from reduce import reduce as reduce_instance

# Import solvers
from three_sat_solver import solve_three_sat
from exact_cover_solver import solve_exact_cover


def random_three_sat(m: int, n: int) -> Dict:
    """Generate a random 3‑SAT instance with m variables and n clauses.
    Assumes m >= 3 if n > 0.
    """
    clauses: List[List[int]] = []
    for _ in range(n):
        vars = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


class TestReduction(unittest.TestCase):
    def test_random_instances(self):
        random.seed(0)
        total = 0
        # Use very small sizes to keep exact‑cover brute force tractable.
        for m in range(0, 4):  # include edge cases m=0,1,2,3
            max_clauses = 2
            for n in range(0, max_clauses + 1):
                if n > 0 and m < 3:
                    continue
                for _ in range(10):  # fewer instances per size
                    total += 1
                    instance = random_three_sat(m, n)
                    ThreeSat.validate(instance)
                    ans_src = solve_three_sat(instance)
                    reduced = reduce_instance(instance)
                    ExactCover.validate(reduced)
                    ans_tgt = solve_exact_cover(reduced)
                    self.assertEqual(ans_src, ans_tgt,
                                     f"Mismatch for instance {instance}")
        self.tests_run = total

if __name__ == "__main__":
    unittest.main()
