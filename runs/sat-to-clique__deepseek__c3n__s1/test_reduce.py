"""Tests for the SAT -> Clique reduction in reduce.py.

Includes brute-force solvers written directly from the problem definitions,
plus exhaustive / randomized comparisons on small instances and a validation
check that every produced Clique instance is well formed.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, Sat, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the docstring definitions)
# ----------------------------------------------------------------------

def solve_sat(instance):
    """True iff some assignment satisfies every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
        # variable v (1..num_vars) -> bits[v-1]
        ok = True
        for clause in clauses:
            if not any(
                (bits[lit - 1] if lit > 0 else not bits[-lit - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def solve_clique(instance):
    """True iff the graph has a clique of at least k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for subset in itertools.combinations(range(n), k):
        if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def random_sat(rng, max_vars=4, max_clauses=5, max_len=3, allow_empty=True):
    num_vars = rng.randint(0, max_vars)
    clauses = []
    for _ in range(rng.randint(0, max_clauses)):
        if num_vars == 0:
            # No literals are legal; only the empty clause is allowed.
            clauses.append([])
            continue
        length = rng.randint(0 if allow_empty else 1, max_len)
        clause = []
        for _ in range(length):
            v = rng.randint(1, num_vars)
            clause.append(v if rng.random() < 0.5 else -v)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def all_small_sats():
    """Exhaustive-ish family of tiny SAT instances."""
    instances = []
    # No clauses / no vars edge cases.
    instances.append({"num_vars": 0, "clauses": []})
    instances.append({"num_vars": 0, "clauses": [[]]})
    instances.append({"num_vars": 1, "clauses": []})
    instances.append({"num_vars": 1, "clauses": [[]]})
    # All clause subsets over literals of 1..2 (including empty clause).
    literals = [1, -1, 2, -2]
    for r in range(0, 4):
        for combo in itertools.combinations(literals, r):
            instances.append({"num_vars": 2, "clauses": [list(combo)]})
    # Pairs of clauses over 1..2.
    clause_pool = [list(c) for r in range(0, 4) for c in itertools.combinations(literals, r)]
    for c1 in clause_pool:
        for c2 in clause_pool:
            instances.append({"num_vars": 2, "clauses": [list(c1), list(c2)]})
    return instances


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_exhaustive_small():
    count = 0
    for inst in all_small_sats():
        Sat.validate(inst)
        out = reduce(inst)
        Clique.validate(out)
        assert solve_sat(inst) == solve_clique(out), (inst, out)
        count += 1
    return count


def test_random():
    rng = random.Random(12345)
    count = 0
    for _ in range(4000):
        inst = random_sat(rng)
        Sat.validate(inst)
        out = reduce(inst)
        Clique.validate(out)
        assert solve_sat(inst) == solve_clique(out), (inst, out)
        count += 1
    return count


def test_known_cases():
    cases = [
        ({"num_vars": 0, "clauses": []}, True),
        ({"num_vars": 0, "clauses": [[]]}, False),
        ({"num_vars": 1, "clauses": [[1]]}, True),
        ({"num_vars": 1, "clauses": [[-1]]}, True),
        ({"num_vars": 1, "clauses": [[1], [-1]]}, False),
        ({"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2]]}, True),
        ({"num_vars": 2, "clauses": [[1], [-1], [2]]}, False),
        ({"num_vars": 3, "clauses": [[1, 1], [1, -1]]}, True),
        ({"num_vars": 3, "clauses": [[1, -1], [2, -2], [3, -3]]}, True),
        ({"num_vars": 1, "clauses": [[1], [1], [1]]}, True),
    ]
    for inst, expected in cases:
        Sat.validate(inst)
        out = reduce(inst)
        Clique.validate(out)
        assert solve_sat(inst) == expected, inst
        assert solve_clique(out) == expected, (inst, out)
    return len(cases)


def test_repeated_clauses_and_literals():
    rng = random.Random(999)
    count = 0
    for _ in range(1000):
        base = random_sat(rng, max_vars=3, max_clauses=3, max_len=3)
        clauses = list(base["clauses"])
        # Duplicate some clauses and literals.
        for clause in list(clauses):
            if clause and rng.random() < 0.5:
                clauses.append(list(clause))
            if clause and rng.random() < 0.5:
                clauses.append([clause[0]] + list(clause))
        inst = {"num_vars": base["num_vars"], "clauses": clauses}
        Sat.validate(inst)
        out = reduce(inst)
        Clique.validate(out)
        assert solve_sat(inst) == solve_clique(out), (inst, out)
        count += 1
    return count


def main():
    tests = [
        ("exhaustive_small", test_exhaustive_small),
        ("random", test_random),
        ("known_cases", test_known_cases),
        ("repeated", test_repeated_clauses_and_literals),
    ]
    total = 0
    passed = 0
    for name, fn in tests:
        try:
            n = fn()
            total += n
            passed += n
            print(f"PASS {name}: {n} cases")
        except AssertionError as exc:
            total += 1
            print(f"FAIL {name}: {exc}")
        except InvalidInstance as exc:
            total += 1
            print(f"FAIL {name} (invalid instance): {exc}")
    print(f"TOTAL {passed}/{total}")
    return passed, total


if __name__ == "__main__":
    main()
