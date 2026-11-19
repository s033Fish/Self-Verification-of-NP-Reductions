"""Independent checks for reduce.py (SAT -> Independent Set).

We implement brute-force solvers for both problems directly from the
definitions in problems.py, then compare the source answer with the answer
of the reduced target instance on many small instances (exhaustive where
feasible, plus randomized).

Run:  python3 test_reduce.py
"""

from __future__ import annotations

import itertools
import random
import sys

import problems
from problems import Sat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the docstring definitions)

def brute_sat(instance) -> bool:
    """Yes iff some assignment satisfies every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=num_vars):
        # variable v (1..num_vars) -> bits[v-1]
        ok = True
        for clause in clauses:
            satisfied = False
            for literal in clause:
                value = bits[abs(literal) - 1]
                if (literal > 0 and value) or (literal < 0 and not value):
                    satisfied = True
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def brute_is(instance) -> bool:
    """Yes iff there is an independent set of size >= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(not (adj[u] & chosen) for u in subset):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def all_clauses(num_vars, max_len):
    """All clauses (lists of literals) with length 0..max_len."""
    literals = [l for v in range(1, num_vars + 1) for l in (v, -v)]
    result = [[]]
    for length in range(1, max_len + 1):
        for combo in itertools.product(literals, repeat=length):
            result.append(list(combo))
    return result


def exhaustive_instances():
    """Exhaustive small instances: m<=3, clause length<=3, up to 2 clauses."""
    for num_vars in range(0, 4):
        clauses = all_clauses(num_vars, 3)
        yield {"num_vars": num_vars, "clauses": []}
        for c1 in clauses:
            yield {"num_vars": num_vars, "clauses": [c1]}
            for c2 in clauses:
                yield {"num_vars": num_vars, "clauses": [c1, c2]}


def random_instances(count, seed=12345):
    rng = random.Random(seed)
    for _ in range(count):
        num_vars = rng.randint(0, 4)
        literals = [l for v in range(1, num_vars + 1) for l in (v, -v)]
        num_clauses = rng.randint(0, 5)
        clauses = []
        for _ in range(num_clauses):
            length = rng.randint(0, 4)
            if not literals:
                clauses.append([])
            else:
                clauses.append([rng.choice(literals) for _ in range(length)])
        yield {"num_vars": num_vars, "clauses": clauses}


# ----------------------------------------------------------------------
# Test driver

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            Sat.validate(instance)
            expected = brute_sat(instance)
            target = reduce(instance)
            IndependentSet.validate(target)
            got = brute_is(target)
            assert got == expected, (
                f"mismatch: source={instance} expected={expected} "
                f"target={target} got={got}"
            )
            tests_passed += 1
        except Exception as exc:  # noqa: BLE001
            failures.append((instance, repr(exc)))

    for inst in exhaustive_instances():
        check(inst)
    for inst in random_instances(20000):
        check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for inst, err in failures[:10]:
        print("FAIL", inst, err)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
