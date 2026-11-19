"""Independent tests for reduce.py: SubsetSum -> SAT.

We implement our own solvers for both problems directly from the definitions
in problems.py, then compare the answers on many small instances.

Subset Sum is solved by exact DP over achievable sums.  SAT is solved by a
complete DPLL search with unit propagation (the reduced formulas are large, so
enumerating all 2^m assignments is infeasible).
"""

import itertools
import random
import json
import sys

from problems import SubsetSum, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force / exact solvers (from the problem definitions)

def subset_sum_solve(instance):
    """Return True iff some sub-list sums to target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True  # empty sub-list
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return target in reachable


def sat_solve(instance):
    """Complete DPLL SAT solver. Return True iff the CNF is satisfiable."""
    num_vars = instance["num_vars"]
    raw = instance["clauses"]

    # Normalise: drop duplicate literals and tautological clauses.
    clauses = []
    for c in raw:
        s = set(c)
        if any(-l in s for l in s):
            continue  # tautology -> always true
        clauses.append(frozenset(s))

    def simplify(clauses, assignment):
        """Apply assignment. Return (ok, new_clauses, units)."""
        new_clauses = []
        units = []
        for c in clauses:
            sat = False
            rem = []
            for l in c:
                v = abs(l)
                if v in assignment:
                    if (l > 0) == assignment[v]:
                        sat = True
                        break
                else:
                    rem.append(l)
            if sat:
                continue
            if not rem:
                return False, None, None
            new_clauses.append(frozenset(rem))
            if len(rem) == 1:
                units.append(rem[0])
        return True, new_clauses, units

    def propagate(clauses, assignment):
        while True:
            ok, clauses, units = simplify(clauses, assignment)
            if not ok:
                return False, clauses, assignment
            if not units:
                return True, clauses, assignment
            for unit in units:
                v = abs(unit)
                val = unit > 0
                if v in assignment:
                    if assignment[v] != val:
                        return False, clauses, assignment
                else:
                    assignment[v] = val

    sys.setrecursionlimit(100000)

    def dpll(clauses, assignment):
        ok, clauses, assignment = propagate(clauses, assignment)
        if not ok:
            return False
        if not clauses:
            return True
        # branch on a literal from the shortest clause
        c = min(clauses, key=len)
        lit = next(iter(c))
        v = abs(lit)
        for val in (True, False):
            a2 = dict(assignment)
            a2[v] = val
            if dpll(clauses, a2):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Test harness

tests_run = 0
tests_passed = 0
failures = []


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    SubsetSum.validate(instance)
    src = subset_sum_solve(instance)
    red = reduce(instance)
    Sat.validate(red)
    tgt = sat_solve(red)
    if src == tgt:
        tests_passed += 1
    else:
        failures.append((label, instance, src, red, tgt))


def random_instance(rng, max_n=7, max_val=16):
    n = rng.randint(0, max_n)
    numbers = [rng.randint(0, max_val) for _ in range(n)]
    total = sum(numbers)
    target = rng.randint(-2, total + 2)
    return {"numbers": numbers, "target": target}


def main():
    rng = random.Random(12345)

    # --- explicit edge cases ---
    edge = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 1},
        {"numbers": [], "target": -5},
        {"numbers": [0], "target": 0},
        {"numbers": [0], "target": 1},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [0, 0, 0], "target": 1},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 0},
        {"numbers": [5], "target": 4},
        {"numbers": [5], "target": -1},
        {"numbers": [1, 2, 3], "target": 6},
        {"numbers": [1, 2, 3], "target": 5},
        {"numbers": [1, 2, 3], "target": 7},
        {"numbers": [2, 2, 2], "target": 6},
        {"numbers": [2, 2, 2], "target": 5},
        {"numbers": [3, 3], "target": 6},
        {"numbers": [1, 1, 1, 1], "target": 4},
        {"numbers": [1, 1, 1, 1], "target": 3},
        {"numbers": [7, 0, 7], "target": 14},
        {"numbers": [7, 0, 7], "target": 7},
        {"numbers": [1000000000], "target": 1000000000},
        {"numbers": [1000000000], "target": 999999999},
        {"numbers": [2**40, 2**40], "target": 2**41},
        {"numbers": [2**40, 2**40], "target": 2**41 - 1},
        {"numbers": [1, 2, 4, 8, 16], "target": 31},
        {"numbers": [1, 2, 4, 8, 16], "target": 30},
        {"numbers": [1, 2, 4, 8, 16], "target": 32},
        {"numbers": [1, 1, 1, 1, 1, 1, 1, 1], "target": 8},
        {"numbers": [1, 1, 1, 1, 1, 1, 1, 1], "target": 9},
    ]
    for inst in edge:
        check(inst, "edge")

    # --- targets beyond the total sum / exactly the total sum ---
    for _ in range(400):
        n = rng.randint(0, 8)
        numbers = [rng.randint(0, 12) for _ in range(n)]
        total = sum(numbers)
        for target in (total, total + 1, total + 7, total - 1):
            check({"numbers": numbers, "target": target}, "beyond")

    # --- larger values (multi-bit numbers) ---
    for _ in range(400):
        n = rng.randint(0, 6)
        numbers = [rng.randint(0, 1000) for _ in range(n)]
        total = sum(numbers)
        target = rng.randint(-1, total + 1)
        check({"numbers": numbers, "target": target}, "largeval")

    # --- huge values (big integers) ---
    for _ in range(200):
        n = rng.randint(1, 5)
        numbers = [rng.randint(0, 2 ** 60) for _ in range(n)]
        total = sum(numbers)
        target = rng.choice([total, total + 1, total // 2, 0, -1,
                             rng.randint(0, total)])
        check({"numbers": numbers, "target": target}, "bigint")

    # --- random small instances ---
    for _ in range(3000):
        check(random_instance(rng), "random")

    # --- random instances biased toward zeros / duplicates ---
    for _ in range(1500):
        n = rng.randint(0, 8)
        pool = [0, 1, 2, 3, 3, 5]
        numbers = [rng.choice(pool) for _ in range(n)]
        total = sum(numbers)
        target = rng.randint(-1, total + 1)
        check({"numbers": numbers, "target": target}, "biased")

    # --- exhaustive over small value multisets ---
    for n in range(0, 6):
        for combo in itertools.product(range(0, 4), repeat=n):
            numbers = list(combo)
            total = sum(numbers)
            for target in range(-1, total + 2):
                check({"numbers": numbers, "target": target}, "exhaustive")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for label, inst, src, red, tgt in failures[:10]:
            print("----")
            print("label:", label)
            print("instance:", inst)
            print("source answer:", src)
            print("reduced:", red)
            print("target answer:", tgt)

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
