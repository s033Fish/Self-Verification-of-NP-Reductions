"""Independent verification of reduce.py (SAT -> Clique).

Brute-force solvers for both problems are written directly from the
definitions in problems.py.  We then compare the solvers' answers on many
small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import Sat, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the docstrings.

def sat_solve(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        value = {v: bits[v - 1] for v in range(1, num_vars + 1)}
        if all(
            any(
                (lit > 0 and value[lit]) or (lit < 0 and not value[-lit])
                for lit in clause
            )
            for clause in clauses
        ):
            return True
    return False


def clique_solve(instance: dict) -> bool:
    """Yes iff the graph has a clique of at least k vertices."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    edge_set = {frozenset(e) for e in instance["edges"]}
    for subset in itertools.combinations(range(n), k):
        if all(
            frozenset((u, v)) in edge_set
            for u, v in itertools.combinations(subset, 2)
        ):
            return True
    return False


# ----------------------------------------------------------------------
# Instance helpers / generators

def make_sat(num_vars, clauses):
    return {"num_vars": num_vars, "clauses": [list(c) for c in clauses]}


def exhaustive_sat_instances():
    """Exhaustive small SAT instances: num_vars 0..2, clauses len 0..2, 0..3 clauses."""
    for num_vars in range(0, 3):
        literals = [l for v in range(1, num_vars + 1) for l in (v, -v)]
        clause_pool = []
        for length in range(0, 3):
            clause_pool.extend(itertools.product(literals, repeat=length))
        for num_clauses in range(0, 4):
            for clauses in itertools.product(clause_pool, repeat=num_clauses):
                yield make_sat(num_vars, clauses)


def exhaustive_sat_instances_3var():
    """Exhaustive 3-variable instances with up to 2 short clauses."""
    num_vars = 3
    literals = [1, -1, 2, -2, 3, -3]
    clause_pool = []
    for length in range(0, 3):
        clause_pool.extend(itertools.product(literals, repeat=length))
    for num_clauses in range(0, 3):
        for clauses in itertools.product(clause_pool, repeat=num_clauses):
            yield make_sat(num_vars, clauses)


def random_sat_instances(count, rng):
    for _ in range(count):
        num_vars = rng.randint(0, 5)
        literals = [l for v in range(1, num_vars + 1) for l in (v, -v)]
        num_clauses = rng.randint(0, 5)
        clauses = []
        for _ in range(num_clauses):
            length = rng.randint(0, 3)
            if literals:
                clauses.append([rng.choice(literals) for _ in range(length)])
            else:
                clauses.append([])
        yield make_sat(num_vars, clauses)


# ----------------------------------------------------------------------
# Test driver

def run():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        Sat.validate(instance)                 # source must be valid
        expected = sat_solve(instance)
        target = reduce(instance)
        Clique.validate(target)                # target must be valid
        got = clique_solve(target)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((label, instance, target, expected, got))

    for inst in exhaustive_sat_instances():
        check(inst, "exhaustive-small")
    for inst in exhaustive_sat_instances_3var():
        check(inst, "exhaustive-3var")

    rng = random.Random(12345)
    for inst in random_sat_instances(4000, rng):
        check(inst, "random")

    edge_cases = [
        make_sat(0, []),
        make_sat(0, [[]]),
        make_sat(1, []),
        make_sat(1, [[]]),
        make_sat(1, [[1]]),
        make_sat(1, [[-1]]),
        make_sat(1, [[1, -1]]),
        make_sat(1, [[1, 1]]),
        make_sat(1, [[1], [-1]]),
        make_sat(1, [[], [1]]),
        make_sat(2, [[1, 2], [-1, 2], [1, -2], [-1, -2]]),
        make_sat(2, [[1, 2], [-1, 2], [1, -2], [-1, -2], []]),
        make_sat(3, [[1, 1, 2], [-2, -2], [3], [-3, 1]]),
        make_sat(2, [[1, -1], [2, -2]]),
        make_sat(2, [[1, -1], [2], [-2]]),
        make_sat(4, [[1], [2], [3], [4]]),
        make_sat(4, [[1, 2], [3, 4], [-1, -3], [-2, -4]]),
    ]
    for inst in edge_cases:
        check(inst, "edge")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    tests_run, tests_passed, failures = run()
    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for label, inst, target, expected, got in failures[:20]:
        print("FAIL", label, inst, "->", target, "expected", expected, "got", got)
    assert not failures, "reduction mismatch found"
    print("ALL TESTS PASSED")
