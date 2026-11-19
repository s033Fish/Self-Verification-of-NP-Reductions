"""Independent tests for reduce.py (Hamiltonian Cycle -> Hamiltonian Path).

We implement our own brute-force solvers from the definitions in problems.py,
then compare source answers with target answers on many small instances.

We also test the explicit polynomial-time / no-brute-force requirement.
"""

import itertools
import random
import time
import unittest

from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce


# Counters so the verdict can report how many individual checks were run.
CHECKS = {"run": 0, "passed": 0}


def _record(passed):
    CHECKS["run"] += 1
    if passed:
        CHECKS["passed"] += 1


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def has_hamiltonian_cycle(instance):
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    edge_set = {frozenset(e) for e in edges}
    # fix vertex 0 to remove rotational symmetry
    for perm in itertools.permutations(range(1, n)):
        order = (0,) + perm
        if all(
            frozenset((order[i], order[(i + 1) % n])) in edge_set
            for i in range(n)
        ):
            return True
    return False


def has_hamiltonian_path(instance):
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    edge_set = {frozenset(e) for e in edges}
    for perm in itertools.permutations(range(n)):
        if all(
            frozenset((perm[i], perm[i + 1])) in edge_set
            for i in range(n - 1)
        ):
            return True
    return False


def all_graphs(n):
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


class TestReductionCorrectness(unittest.TestCase):
    def _check(self, instance):
        HamiltonianCycle.validate(instance)
        reduced = reduce(instance)
        HamiltonianPath.validate(reduced)
        source_answer = has_hamiltonian_cycle(instance)
        target_answer = has_hamiltonian_path(reduced)
        ok = source_answer == target_answer
        _record(ok)
        self.assertEqual(
            source_answer,
            target_answer,
            msg=f"mismatch on {instance}: reduced={reduced}",
        )

    def test_all_graphs_up_to_4_vertices(self):
        count = 0
        for n in range(0, 5):
            for instance in all_graphs(n):
                self._check(instance)
                count += 1
        self.assertEqual(count, 76)

    def test_random_graphs_5_to_7_vertices(self):
        rng = random.Random(12345)
        for n in range(5, 8):
            possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
            for _ in range(400):
                edges = [list(e) for e in possible if rng.random() < 0.5]
                self._check({"n": n, "edges": edges})

    def test_known_yes_and_no_cases(self):
        yes_cycle = {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]}
        self._check(yes_cycle)
        no_cycle = {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]}
        self._check(no_cycle)
        self._check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})
        self._check({"n": 3, "edges": [[0, 1], [1, 2]]})
        self._check({"n": 0, "edges": []})
        self._check({"n": 1, "edges": []})
        self._check({"n": 2, "edges": [[0, 1]]})

    def test_output_is_valid_target_instance(self):
        for n in range(0, 5):
            for instance in all_graphs(n):
                HamiltonianPath.validate(reduce(instance))


class TestPolynomialTimeRequirement(unittest.TestCase):
    """The task requires reduce to run in polynomial time and not to call
    brute-force solvers.  A brute-force Hamiltonian-cycle search blows up
    exponentially on hard NO-instances (a bridge between two cliques)."""

    @staticmethod
    def _bridge_graph(n):
        h = n // 2
        edges = []
        for u in range(0, h + 1):
            for v in range(u + 1, h + 1):
                edges.append([u, v])
        for u in range(h + 1, n):
            for v in range(u + 1, n):
                edges.append([u, v])
        edges.append([h, h + 1])
        return {"n": n, "edges": edges}

    def test_reduce_is_fast_on_hard_instances(self):
        # A polynomial reduction should handle these sizes essentially
        # instantly.  The current implementation takes ~5s at n=11 and
        # doubles with every added vertex.
        for n in (11, 13, 15):
            instance = self._bridge_graph(n)
            start = time.time()
            reduce(instance)
            elapsed = time.time() - start
            ok = elapsed < 1.0
            _record(ok)
            self.assertLess(
                elapsed,
                1.0,
                msg=f"reduce took {elapsed:.2f}s on n={n}: not polynomial",
            )


if __name__ == "__main__":
    import sys

    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f"CHECKS_RUN={CHECKS['run']} CHECKS_PASSED={CHECKS['passed']}")
    sys.exit(0 if result.wasSuccessful() else 1)
