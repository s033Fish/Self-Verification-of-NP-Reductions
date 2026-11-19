"""Tests for reduce.py: compare brute-force answers on many small instances."""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_nae3sat(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            values = []
            for lit in clause:
                v = abs(lit)
                val = bits[v - 1]
                values.append(val if lit > 0 else not val)
            if all(values) or not any(values):
                ok = False
                break
        if ok:
            return True
    return False


def solve_3coloring(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    colour = [-1] * n

    def backtrack(i: int) -> bool:
        if i == n:
            return True
        for c in range(3):
            if all(colour[j] != c for j in adj[i] if j < i):
                colour[i] = c
                if backtrack(i + 1):
                    return True
                colour[i] = -1
        return False

    return backtrack(0)


# ----------------------------------------------------------------------
# Instance generation (small, valid instances).

def random_nae_instance(rng: random.Random, max_vars: int = 5, max_clauses: int = 5):
    m = rng.randint(0, max_vars)
    clauses = []
    if m >= 3:
        for _ in range(rng.randint(0, max_clauses)):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_instances():
    """Exhaustive-ish enumeration of small NAE-3-SAT instances."""
    # m = 0,1,2: only empty clause lists are valid.
    for m in range(0, 3):
        yield {"num_vars": m, "clauses": []}
    # m = 3: enumerate all clauses over variables 1,2,3 (each clause is an
    # ordered triple of signed literals on 3 distinct variables).
    literals = [1, -1, 2, -2, 3, -3]
    all_clauses = []
    for perm in itertools.permutations(literals, 3):
        if len({abs(x) for x in perm}) == 3:
            all_clauses.append(list(perm))
    # dedupe by canonical form
    canon = {}
    for cl in all_clauses:
        key = frozenset(cl)
        canon[key] = cl
    clauses3 = list(canon.values())
    # all subsets of clauses up to size 3 (may repeat clauses too)
    for size in range(0, 4):
        for combo in itertools.combinations_with_replacement(clauses3, size):
            yield {"num_vars": 3, "clauses": [list(c) for c in combo]}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    # 1. Exhaustive small instances.
    for inst in all_small_instances():
        problems.NaeThreeSat.validate(inst)
        expected = solve_nae3sat(inst)
        out = reduce(inst)
        problems.ThreeColoring.validate(out)
        got = solve_3coloring(out)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH (exhaustive):", inst, "expected", expected, "got", got)

    # 2. Random instances.
    rng = random.Random(12345)
    for _ in range(3000):
        inst = random_nae_instance(rng)
        problems.NaeThreeSat.validate(inst)
        expected = solve_nae3sat(inst)
        out = reduce(inst)
        problems.ThreeColoring.validate(out)
        got = solve_3coloring(out)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH (random):", inst, "expected", expected, "got", got)

    # 3. Hand-crafted edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},           # yes (mixed)
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},  # yes
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},  # yes
        # unsatisfiable: all clauses force all-equal patterns
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3]]},
    ]
    for inst in edge_cases:
        problems.NaeThreeSat.validate(inst)
        expected = solve_nae3sat(inst)
        out = reduce(inst)
        problems.ThreeColoring.validate(out)
        got = solve_3coloring(out)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH (edge):", inst, "expected", expected, "got", got)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"

    import json
    with open("verdict.json", "w") as f:
        json.dump(
            {
                "verified": tests_run == tests_passed,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
            },
            f,
        )
    print("verdict.json written")


if __name__ == "__main__":
    main()
