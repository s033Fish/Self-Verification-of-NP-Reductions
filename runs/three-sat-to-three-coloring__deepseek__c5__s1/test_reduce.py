"""Independent verification of reduce.py (3-SAT -> 3-Coloring).

Contains brute-force solvers for both problems written from the definitions
in problems.py, plus exhaustive/random tests comparing answers.
"""
from __future__ import annotations

import itertools
import random
import sys

from problems import ThreeSat, ThreeColoring, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the problem definitions)
# ----------------------------------------------------------------------

def sat_solver(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                       for l in clause):
                ok = False
                break
        if ok:
            return True
    return False


def coloring_solver(instance: dict) -> bool:
    """True iff the graph is 3-colourable (backtracking)."""
    n = instance["n"]
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    color = [-1] * n

    def bt(i: int) -> bool:
        if i == n:
            return True
        for c in range(3):
            if all(color[j] != c for j in adj[i] if j < i):
                color[i] = c
                if bt(i + 1):
                    return True
                color[i] = -1
        return False

    return bt(0)


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def random_sat(m: int, k: int, rng: random.Random) -> dict:
    clauses = []
    for _ in range(k):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_clauses(m: int) -> list[list[int]]:
    """All 3-clauses over variables 1..m (canonical, no dup var/sign clash)."""
    out = []
    for vs in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            out.append([s * v for s, v in zip(signs, vs)])
    return out


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def check(instance: dict, label: str, failures: list) -> bool:
    ThreeSat.validate(instance)
    src = sat_solver(instance)
    red = reduce(instance)
    ThreeColoring.validate(red)          # reduction must output valid target
    tgt = coloring_solver(red)
    if src != tgt:
        failures.append((label, instance, src, red, tgt))
        return False
    return True


def main() -> int:
    rng = random.Random(12345)
    tests = 0
    passed = 0
    failures: list = []

    # 1. Exhaustive over all clause subsets for small m (m = 0..3).
    for m in range(0, 4):
        pool = all_clauses(m) if m >= 3 else []
        # all subsets is huge for m=3 (8 clauses -> 256), fine
        for r in range(len(pool) + 1):
            for combo in itertools.combinations(pool, r):
                inst = {"num_vars": m, "clauses": [list(c) for c in combo]}
                tests += 1
                if check(inst, f"exhaustive m={m} r={r}", failures):
                    passed += 1

    # 2. Random instances for m = 3..5.
    for _ in range(4000):
        m = rng.randint(3, 5)
        k = rng.randint(0, 12)
        inst = random_sat(m, k, rng)
        tests += 1
        if check(inst, f"random m={m} k={k}", failures):
            passed += 1

    # 3. Targeted edge cases.
    targeted = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 5, "clauses": []},
        # all 8 clauses on 3 vars: unsatisfiable
        {"num_vars": 3, "clauses": all_clauses(3)},
        # duplicated clause
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        # one clause, satisfiable
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        # clause with all negative literals
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        # variable not appearing
        {"num_vars": 4, "clauses": [[1, 2, 3]]},
    ]
    for inst in targeted:
        tests += 1
        if check(inst, "targeted", failures):
            passed += 1

    # 4. Sanity: target-only checks that the reduction's graph is valid and
    #    the solvers agree with known facts (K4 is not 3-colourable).
    k4 = {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
    assert coloring_solver(k4) is False
    assert coloring_solver({"n": 0, "edges": []}) is True
    assert coloring_solver({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}) is True
    assert sat_solver({"num_vars": 0, "clauses": []}) is True

    print(f"tests_run={tests} tests_passed={passed} failures={len(failures)}")
    for f in failures[:5]:
        print("FAIL:", f)

    with open("results.json", "w") as fh:
        import json
        json.dump({"tests_run": tests, "tests_passed": passed,
                   "failures": len(failures)}, fh)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
