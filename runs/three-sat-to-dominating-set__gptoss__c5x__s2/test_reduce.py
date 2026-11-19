"""Independent tests for reduce.py: 3-SAT -> Dominating Set.

Brute-force solvers for both problems are implemented directly from the
definitions in problems.py, then compared on many small source instances
and their reductions.  The test suite also records a verdict.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import ThreeSat, DominatingSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions)


def solve_three_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_dominating_set(instance: dict) -> bool:
    """True iff there is a dominating set of size at most k."""
    DominatingSet.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True

    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    for size in range(0, k + 1):
        for combo in itertools.combinations(range(n), size):
            dom = set(combo)
            for u in combo:
                dom |= adj[u]
            if len(dom) == n:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators


def gen_instances():
    """Yield a variety of small 3-SAT instances."""
    instances = []

    # No clauses, various m (including m = 0).
    for m in range(0, 5):
        instances.append({"num_vars": m, "clauses": []})

    # m = 3, all single clauses.
    for clause in itertools.permutations([1, 2, 3]):
        instances.append({"num_vars": 3, "clauses": [list(clause)]})

    # m = 3, all 8 clauses (unsatisfiable) and all 4-clause subsets.
    patterns = list(itertools.product([1, -1], repeat=3))
    all_clauses = [[s * (i + 1) for i, s in enumerate(p)] for p in patterns]
    instances.append({"num_vars": 3, "clauses": [list(c) for c in all_clauses]})
    for combo in itertools.combinations(range(8), 4):
        instances.append(
            {"num_vars": 3, "clauses": [list(all_clauses[i]) for i in combo]}
        )

    # Random instances for m = 3..5.
    rng = random.Random(12345)
    for _ in range(400):
        m = rng.randint(3, 5)
        t = rng.randint(0, 6)
        clauses = []
        for _ in range(t):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
        instances.append({"num_vars": m, "clauses": clauses})

    # Duplicated clauses.
    instances.append({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [-1, -2, -3]]})

    return instances


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in gen_instances():
        src = solve_three_sat(inst)
        red = reduce(inst)
        tgt = solve_dominating_set(red)
        tests_run += 1
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, src, red, tgt))

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for inst, src, red, tgt in failures[:10]:
        print("FAIL")
        print("  source:", inst, "->", src)
        print("  target k =", red["k"], "n =", red["n"], "->", tgt)

    verified = len(failures) == 0
    with open("verdict.json", "w") as f:
        json.dump(
            {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed},
            f,
        )
    print("verdict.json written:", {"verified": verified,
                                    "tests_run": tests_run,
                                    "tests_passed": tests_passed})
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
