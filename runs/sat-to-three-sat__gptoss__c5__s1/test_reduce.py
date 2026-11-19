import unittest
import random
from typing import List, Dict, Any

from problems import Sat, ThreeSat
from reduce import reduce as reduce_fn
from sat_solver import sat_bruteforce, three_sat_bruteforce

# Global to record number of generated instances
TOTAL_INSTANCES = 0


def generate_random_instance(max_vars: int = 4, max_clauses: int = 5) -> Dict[str, Any]:
    num_vars = random.randint(0, max_vars)
    clauses: List[List[int]] = []
    for _ in range(random.randint(0, max_clauses)):
        # clause length can be 0..(num_vars+2) maybe
        length = random.randint(0, max(1, num_vars + 2))
        clause = []
        for _ in range(length):
            if num_vars == 0:
                # No variables, but we can still add literals? keep empty
                continue
            var = random.randint(1, num_vars)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


class TestReduction(unittest.TestCase):
    def test_random_instances(self):
        global TOTAL_INSTANCES
        for _ in range(200):  # generate 200 random instances
            instance = generate_random_instance()
            # validate source
            Sat.validate(instance)
            # compute answers
            sat_ans = sat_bruteforce(instance)
            reduced = reduce_fn(instance)
            # validate target
            ThreeSat.validate(reduced)
            three_sat_ans = three_sat_bruteforce(reduced)
            self.assertEqual(sat_ans, three_sat_ans, f"Mismatch on instance {instance}\nReduced: {reduced}")
            TOTAL_INSTANCES += 1

if __name__ == "__main__":
    unittest.main()
