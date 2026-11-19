"""Tests for reduce.py: compare brute-force answers on many small instances."""

from __future__ import annotations

import itertools
import random

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the problem definitions)

def solve_nae3sat(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = []
            for lit in clause:
                v = abs(lit)
                val = bits[v - 1]
                vals.append(val if lit > 0 else not val)
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False


def solve_three_coloring(instance: dict) -> bool:
    n = instance["n"]
    adj = [[] for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    colour = [-1] * n

    def bt(i: int) -> bool:
        if i == n:
            return True
        for c in range(3):
            if all(colour[j] != c for j in adj[i]):
                colour[i] = c
                if bt(i + 1):
                    return True
                colour[i] = -1
        return False

    return bt(0)


# ----------------------------------------------------------------------
# Random small instance generators

def random_nae_instance(rng: random.Random, max_vars: int = 5, max_clauses: int = 5):
    m = rng.randint(0, max_vars)
    clauses = []
    for _ in range(rng.randint(0, max_clauses)):
        if m < 3:
            break
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_nae_instances():
    """Exhaustively enumerate tiny NAE-3-SAT instances."""
    out = []
    # m = 0,1,2 with no clauses (only valid clause-free instances)
    for m in range(0, 3):
        out.append({"num_vars": m, "clauses": []})
    # m = 3: enumerate subsets of all possible clauses (up to 8 clauses)
    all_clauses = []
    for vs in itertools.permutations(range(1, 4)):
        for signs in itertools.product([1, -1], repeat=3):
            all_clauses.append([s * v for s, v in zip(signs, vs)])
    # dedupe as frozensets of literals
    uniq = []
    seen = set()
    for c in all_clauses:
        key = frozenset(c)
        if key not in seen:
            seen.add(key)
            uniq.append(c)
    # all subsets of size 0..3 of the 8 distinct clauses
    for r in range(0, 4):
        for combo in itertools.combinations(uniq, r):
            out.append({"num_vars": 3, "clauses": [list(c) for c in combo]})
    return out


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        NaeThreeSat.validate(inst)
        target = reduce(inst)
        ThreeColoring.validate(target)
        expected = solve_nae3sat(inst)
        got = solve_three_coloring(target)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, expected, got))

    # 1. Exhaustive tiny instances
    for inst in all_small_nae_instances():
        check(inst)

    # 2. Edge cases
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 10, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, -3], [-1, -2, 3]]})

    # 3. Random instances
    rng = random.Random(12345)
    for _ in range(3000):
        inst = random_nae_instance(rng, max_vars=5, max_clauses=6)
        check(inst)

    # 4. Random larger-but-still-brute-forceable instances
    for _ in range(300):
        inst = random_nae_instance(rng, max_vars=7, max_clauses=8)
        check(inst)

    # 5. Structured satisfiable / unsatisfiable instances
    # All clauses over 3 vars: NAE-3-SAT with all 8 clauses is unsat.
    all8 = []
    for vs in itertools.permutations(range(1, 4)):
        for signs in itertools.product([1, -1], repeat=3):
            all8.append([s * v for s, v in zip(signs, vs)])
    check({"num_vars": 3, "clauses": all8})
    # Single clause is always satisfiable.
    check({"num_vars": 3, "clauses": [[1, -2, 3]]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for inst, exp, got in failures[:10]:
            print("  ", inst, "expected", exp, "got", got)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
