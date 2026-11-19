"""Independent tests for reduce.py (SAT -> Clique).

We implement brute-force solvers for both problems from the definitions in
problems.py and compare, on many small instances, the answer of the source
instance with the answer of its reduction.

Run:  python3 test_reduce.py
Writes verdict.json.
"""

from __future__ import annotations

import itertools
import json
import random
import time

from problems import Sat, Clique, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions
# ----------------------------------------------------------------------

def sat_solve(instance) -> bool:
    """Brute force SAT: try every assignment of variables 1..num_vars."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for mask in range(1 << num_vars):
        satisfied = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                bit = (mask >> (var - 1)) & 1
                val = (bit == 1)          # True if variable is true
                if val == (lit > 0):      # literal is true
                    clause_ok = True
                    break
            if not clause_ok:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def clique_solve(instance) -> bool:
    """Brute force Clique: does the graph have a clique of size >= k?"""
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
    for comb in itertools.combinations(range(n), k):
        if all(adj[a][b] for a, b in itertools.combinations(comb, 2)):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def random_sat(rng, max_vars=4, max_clauses=4, max_len=3):
    num_vars = rng.randint(0, max_vars)
    num_clauses = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        length = rng.randint(0, max_len)
        clause = []
        for _ in range(length):
            if num_vars == 0:
                break
            var = rng.randint(1, num_vars)
            sign = rng.choice([1, -1])
            clause.append(sign * var)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def exhaustive_small_sat():
    """Enumerate a decent set of tiny SAT instances deterministically."""
    instances = []
    # num_vars 0..3, clauses 0..2, clause length 0..3, literals from +/-1..+/-num_vars
    for num_vars in range(0, 4):
        lits = [s * v for v in range(1, num_vars + 1) for s in (1, -1)]
        possible_clauses = [[]]
        for length in (1, 2, 3):
            possible_clauses.extend(list(p) for p in itertools.product(lits, repeat=length))
        for num_clauses in range(0, 3):
            for clauses in itertools.product(possible_clauses, repeat=num_clauses):
                instances.append({"num_vars": num_vars,
                                  "clauses": [list(c) for c in clauses]})
    return instances


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, tag):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            Sat.validate(instance)
            src = sat_solve(instance)
            out = reduce(instance)
            Clique.validate(out)          # reduction must emit a valid instance
            tgt = clique_solve(out)
            if src == tgt:
                tests_passed += 1
            else:
                failures.append((tag, instance, src, out, tgt))
        except Exception as exc:          # any crash is a failure
            failures.append((tag, instance, "EXC", repr(exc), None))

    # 1. Exhaustive tiny instances
    for inst in exhaustive_small_sat():
        check(inst, "exhaustive")

    # 2. Targeted edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},                       # no clauses -> yes
        {"num_vars": 0, "clauses": [[]]},                     # empty clause -> no
        {"num_vars": 3, "clauses": []},                       # no clauses -> yes
        {"num_vars": 3, "clauses": [[]]},                     # empty clause -> no
        {"num_vars": 3, "clauses": [[], [1]]},                # empty clause -> no
        {"num_vars": 1, "clauses": [[1]]},                    # yes
        {"num_vars": 1, "clauses": [[-1]]},                   # yes
        {"num_vars": 1, "clauses": [[1], [-1]]},              # no
        {"num_vars": 1, "clauses": [[1, 1]]},                 # duplicate literal -> yes
        {"num_vars": 1, "clauses": [[1, -1]]},                # tautology -> yes
        {"num_vars": 1, "clauses": [[1, -1], [1], [-1]]},     # no
        {"num_vars": 2, "clauses": [[1, 1], [-1, -1]]},       # no
        {"num_vars": 2, "clauses": [[1, 1], [1, 1]]},         # yes
        {"num_vars": 2, "clauses": [[1, 2], [-1], [-2]]},     # no
        {"num_vars": 2, "clauses": [[1, 2], [-1, 2]]},        # yes
        {"num_vars": 3, "clauses": [[1], [2], [3]]},          # yes
        {"num_vars": 3, "clauses": [[1], [-1], [2]]},         # no
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},# yes
        {"num_vars": 3, "clauses": [[1, 2], [-1, -2], [1, -2], [-1, 2]]},  # no
        {"num_vars": 4, "clauses": [[1, 2], [-1, 3], [-3, 4], [-2, -4]]},  # yes
        {"num_vars": 4, "clauses": [[1, 2], [-1, 3], [-3, 4], [-2, -4], [1], [-1]]},  # no
        {"num_vars": 2, "clauses": [[1], [1], [1]]},          # repeated clause -> yes
        {"num_vars": 2, "clauses": [[1], [-1], [1], [-1]]},   # repeated -> no
        {"num_vars": 5, "clauses": [[1, -1], [2, -2], [3, -3], [4, -4], [5, -5]]},  # yes
    ]
    for inst in edge_cases:
        check(inst, "edge")

    # 3. Random instances (many)
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_sat(rng), "random")

    # 4. Random instances with slightly larger bounds
    rng2 = random.Random(999)
    for _ in range(500):
        check(random_sat(rng2, max_vars=5, max_clauses=5, max_len=4), "random-large")

    # 5. Random instances with more variables (brute force still feasible)
    rng3 = random.Random(2024)
    for _ in range(200):
        check(random_sat(rng3, max_vars=10, max_clauses=8, max_len=5), "random-10var")

    # 6. Sanity: reduction is deterministic
    for seed in range(50):
        inst = random_sat(random.Random(seed), max_vars=4, max_clauses=4, max_len=3)
        tests_run += 1
        if reduce(inst) == reduce(inst):
            tests_passed += 1
        else:
            failures.append(("determinism", inst, None, None, None))

    # 7. Malformed input must be rejected (validate is called)
    bad_inputs = [
        {"num_vars": -1, "clauses": []},
        {"num_vars": 2, "clauses": [[3]]},          # literal out of range
        {"num_vars": 2, "clauses": [[0]]},          # literal 0 not allowed
        {"num_vars": 2, "clauses": "nope"},
        {"num_vars": 2},                            # missing key
        {"num_vars": 2, "clauses": [], "extra": 1},
    ]
    for inst in bad_inputs:
        tests_run += 1
        try:
            reduce(inst)
        except InvalidInstance:
            tests_passed += 1
        except Exception:
            # any rejection is acceptable, but record if it silently succeeds
            tests_passed += 1
        else:
            failures.append(("malformed-not-rejected", inst, None, None, None))

    # 8. Polynomial-time / size sanity on a moderately large instance
    tests_run += 1
    big = {"num_vars": 20, "clauses": [[1, 2, 3], [-1, 4, 5], [-4, -5, 6],
                                      [7, -8, 9], [-7, 8, -9], [10, 11, -12],
                                      [-10, -11, 12], [13, -14, 15], [-13, 14, -15],
                                      [16, 17, 18], [-16, -17, 18], [19, -20, 1],
                                      [-19, 20, -1], [2, -3, 4], [-2, 3, -4],
                                      [5, 6, -7], [-6, 7, 8], [9, -10, 11],
                                      [-11, 12, 13], [14, 15, -16]]}
    start = time.time()
    out = reduce(big)
    elapsed = time.time() - start
    Clique.validate(out)
    if elapsed < 5.0 and out["n"] == 60:
        tests_passed += 1
    else:
        failures.append(("performance", big, elapsed, out["n"], None))

    verified = len(failures) == 0
    verdict = {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print(json.dumps(verdict))
    if failures:
        print("FAILURES (showing up to 10):")
        for f in failures[:10]:
            print(f)
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
