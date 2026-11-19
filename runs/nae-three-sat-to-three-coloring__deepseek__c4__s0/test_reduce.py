"""Tests for the NAE-3-SAT -> 3-Coloring reduction.

Contains independent brute-force solvers for both problems (written from the
definitions in problems.py) and compares their answers on many small source
instances and on the corresponding reduced instances.
"""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers

def nae3sat_solve(instance) -> bool:
    """True iff some assignment makes every clause not-all-equal."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=num_vars):
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
    return False


def three_coloring_solve(instance) -> bool:
    """True iff the graph is 3-colourable (backtracking)."""
    n = instance["n"]
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    colour = [-1] * n

    def bt(i: int) -> bool:
        if i == n:
            return True
        for c in range(3):
            if all(colour[w] != c for w in adj[i]):
                colour[i] = c
                if bt(i + 1):
                    return True
                colour[i] = -1
        return False

    return bt(0)


# ----------------------------------------------------------------------
# Instance generators

def random_nae_instance(num_vars, num_clauses, rng):
    clauses = []
    for _ in range(num_clauses):
        vs = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def all_small_instances():
    """Exhaustive small formulas: all clause sets over variables 1..3."""
    literals = [1, -1, 2, -2, 3, -3]
    # all clauses with 3 distinct variables
    clauses = []
    for combo in itertools.combinations([1, 2, 3], 3):
        for signs in itertools.product([1, -1], repeat=3):
            clauses.append([s * v for s, v in zip(signs, combo)])
    # all subsets of up to 2 clauses (clause order irrelevant, duplicates allowed)
    yield {"num_vars": 3, "clauses": []}
    for c in clauses:
        yield {"num_vars": 3, "clauses": [list(c)]}
    for c1, c2 in itertools.combinations_with_replacement(clauses, 2):
        yield {"num_vars": 3, "clauses": [list(c1), list(c2)]}
    # a few 4-variable instances
    rng = random.Random(12345)
    for _ in range(300):
        yield random_nae_instance(4, rng.randint(0, 6), rng)
    for _ in range(200):
        yield random_nae_instance(5, rng.randint(0, 8), rng)
    # no-clause edge cases
    yield {"num_vars": 0, "clauses": []}
    yield {"num_vars": 1, "clauses": []}
    yield {"num_vars": 7, "clauses": []}


def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in all_small_instances():
        problems.NaeThreeSat.validate(inst)
        expected = nae3sat_solve(inst)
        red = reduce(inst)
        problems.ThreeColoring.validate(red)
        got = three_coloring_solve(red)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            failures.append((inst, expected, red, got))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES (up to 5):")
        for inst, expected, red, got in failures[:5]:
            print("  instance:", inst)
            print("  expected:", expected, "got:", got)
            print("  reduced:", red)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()


def write_verdict(tests_run: int, tests_passed: int) -> None:
    import json
    verdict = {
        "verified": tests_run == tests_passed and tests_run > 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("wrote verdict.json:", verdict)
