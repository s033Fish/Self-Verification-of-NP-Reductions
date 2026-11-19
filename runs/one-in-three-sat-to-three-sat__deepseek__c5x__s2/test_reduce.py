import itertools
import unittest
from typing import List, Dict, Any

from solver import solve_one_in_three, solve_three_sat
import reduce

class TestReduction(unittest.TestCase):
    def generate_instances(self) -> List[Dict[str, Any]]:
        instances = []
        for m in range(0, 5):  # 0..4 variables
            if m >= 3:
                vars_range = list(range(1, m + 1))
                all_clauses = list(itertools.combinations(vars_range, 3))
                for k in range(0, 4):  # up to 3 clauses
                    for combo in itertools.combinations_with_replacement(all_clauses, k):
                        clauses = [list(c) for c in combo]
                        instances.append({"num_vars": m, "clauses": clauses})
            else:
                instances.append({"num_vars": m, "clauses": []})
        return instances

    def test_reduction_correctness(self):
        instances = self.generate_instances()
        for inst in instances:
            src_ans = solve_one_in_three(inst)
            tgt_inst = reduce.reduce(inst)
            tgt_ans = solve_three_sat(tgt_inst)
            self.assertEqual(src_ans, tgt_ans, msg=f"Mismatch on {inst} -> {tgt_inst}")
        # Record counts for verdict
        self.__class__.tests_run = len(instances)
        self.__class__.tests_passed = len(instances)

if __name__ == "__main__":
    unittest.main()
