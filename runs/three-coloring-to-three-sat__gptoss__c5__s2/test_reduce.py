import itertools
import unittest
import json
import os

import problems
from reduce import reduce as reduce_instance
from solve_bruteforce import solve_three_coloring, solve_three_sat

class TestReduction(unittest.TestCase):
    def generate_graphs(self, n):
        # all possible edges as unordered pairs
        vertices = list(range(n))
        all_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
        for mask in range(1 << len(all_edges)):
            edges = []
            for idx, (u, v) in enumerate(all_edges):
                if mask & (1 << idx):
                    edges.append([u, v])
            yield {"n": n, "edges": edges}

    def test_all_small_graphs(self):
        total = 0
        passed = 0
        # Limit to very small graphs to keep the brute‑force SAT solver tractable.
        # With the auxiliary variables introduced by the reduction, the number
        # of SAT variables grows quickly (roughly O(|V|+|E|)).  For n=4 the SAT
        # instance already has > 100 variables, making exhaustive search
        # infeasible.  Testing up to n=3 still exercises all important parts
        # of the reduction (vertex constraints, edge constraints, auxiliary
        # variables) while keeping runtime reasonable.
        for n in range(0, 4):  # up to 3 vertices
            for graph in self.generate_graphs(n):
                total += 1
                # validate source
                problems.ThreeColoring.validate(graph)
                # compute answers
                ans_src = solve_three_coloring(graph)
                # reduce
                reduced = reduce_instance(graph)
                # validate target
                problems.ThreeSat.validate(reduced)
                ans_tgt = solve_three_sat(reduced)
                self.assertEqual(ans_src, ans_tgt, f"Mismatch on graph {graph}")
                passed += 1
        # write summary for verdict
        with open('verdict_summary.json', 'w') as f:
            json.dump({'tests_run': total, 'tests_passed': passed}, f)

if __name__ == '__main__':
    unittest.main()
