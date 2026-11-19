"""Independent tests for reduce.py: 3-SAT -> Clique.

We implement our own brute-force solvers for both problems directly from the
definitions in problems.py, then compare answers on many small instances and
their reductions.  The reduction is also checked to be a valid Clique
instance, and its runtime scaling is sanity-checked (polynomial, no solver
calls).
"""

import itertools
import json
import random
import sys
import time

from problems import ThreeSat, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the definitions, independent of reduce.py)

def solve_three_sat(instance):
    """Return True iff the 3-SAT instance is satisfiable."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if not clauses:                      # empty formula is satisfiable
        return True
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_clique(instance):
    """Return True iff the graph has a clique of AT LEAST k vertices."""
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
        if all(adj[a][b] for a, b in itertools.combinations(subset, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generator (valid 3-SAT instances)

def gen_three_sat(rng, max_vars=5, max_clauses=6):
    m = rng.randint(0, max_vars)
    nclauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(nclauses):
        if m < 3:                        # a clause needs 3 distinct variables
            break
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    inst = {"num_vars": m, "clauses": clauses}
    ThreeSat.validate(inst)
    return inst


def main():
    rng = random.Random(20240607)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            ThreeSat.validate(inst)
        except Exception as e:
            failures.append((label, "source invalid", repr(e), inst))
            return
        expected = solve_three_sat(inst)
        out = reduce(inst)
        try:
            Clique.validate(out)
        except Exception as e:
            failures.append((label, "target invalid", repr(e), inst, out))
            return
        got = solve_clique(out)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((label, "answer mismatch", inst, expected, out, got))

    # --- Explicit edge cases ---
    check({"num_vars": 0, "clauses": []}, "empty m=0")
    check({"num_vars": 5, "clauses": []}, "empty m=5")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single positive")
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]}, "single all-neg")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "contradiction")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}, "duplicate clause")
    check({"num_vars": 3,
           "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3]]},
          "all sign combos")
    check({"num_vars": 4,
           "clauses": [[1, 2, 3], [-1, 2, 4], [1, -2, -4]]}, "mixed")
    check({"num_vars": 10, "clauses": [[1, 2, 3]]}, "unused vars")
    check({"num_vars": 6,
           "clauses": [[1, 2, 3], [4, 5, 6], [-1, -4, 2],
                       [-2, -5, 3], [-3, -6, 1]]}, "5-clause unsat")

    # unsat classic: all 8 clauses over 3 vars (every assignment falsifies one)
    allc = [[s[i] * (i + 1) for i in range(3)]
            for s in itertools.product([1, -1], repeat=3)]
    check({"num_vars": 3, "clauses": allc}, "unsat 8 clauses")

    # --- Random tests ---
    for i in range(4000):
        inst = gen_three_sat(rng, max_vars=rng.randint(0, 5),
                             max_clauses=rng.randint(0, 6))
        check(inst, f"random {i}")

    # --- Exhaustive small structured tests ---
    base_clauses = allc  # the 8 clauses over 3 vars
    for r in range(0, 3):
        for combo in itertools.combinations(range(len(base_clauses)), r):
            check({"num_vars": 3,
                   "clauses": [base_clauses[j] for j in combo]},
                  f"exhaustive {combo}")

    # --- Polynomial-time sanity check (no brute force here) ---
    for nc in [100, 500, 1000]:
        inst = {"num_vars": 50, "clauses": [[1, 2, 3] for _ in range(nc)]}
        t = time.time()
        out = reduce(inst)
        dt = time.time() - t
        Clique.validate(out)
        assert out["n"] == 3 * nc and out["k"] == nc
        assert dt < 30, f"reduction too slow: {dt}s for {nc} clauses"
        tests_run += 1
        tests_passed += 1

    # --- reduce.py must not import/call any solver ---
    src = open("reduce.py").read()
    for bad in ["itertools", "combinations", "product", "solve", "brute"]:
        tests_run += 1
        if bad not in src:
            tests_passed += 1
        else:
            failures.append(("no-solver-check", bad, src))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures[:10]:
            print("  ", f)

    verified = (len(failures) == 0 and tests_run == tests_passed)
    verdict = {"verified": verified,
               "tests_run": tests_run,
               "tests_passed": tests_passed}
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)
    return 0 if verified else 1


if __name__ == "__main__":
    sys.exit(main())
