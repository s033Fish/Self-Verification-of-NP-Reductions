"""Independent tests for reduce.py (SubsetSum -> Sat).

We implement our own brute-force solvers from the problem definitions in
problems.py, then compare solver answers on many small source instances and
their reductions.

Run:  python3 test_reduce.py
"""

from __future__ import annotations

import itertools
import random

from problems import SubsetSum, Sat
import reduce as R


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.
# ----------------------------------------------------------------------

def solve_subset_sum(instance):
    """Exact subset-sum via reachable-sum DP (correct, not the reduction)."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True
    reach = {0}
    for a in numbers:
        reach |= {s + a for s in reach}
    return target in reach


def solve_sat_enum(instance):
    """Brute force: try every assignment of variables 1..num_vars."""
    clauses = instance["clauses"]
    m = instance["num_vars"]
    for bits in itertools.product((False, True), repeat=m):
        # bits[v-1] is value of variable v
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance):
    """Complete DPLL with unit propagation (used when m is too big to enumerate)."""
    clauses = [tuple(c) for c in instance["clauses"]]

    def dpll(clauses, assign):
        clauses = list(clauses)
        while True:
            units = []
            new = []
            for cl in clauses:
                rem = []
                sat = False
                for lit in cl:
                    v = abs(lit)
                    if v in assign:
                        if (lit > 0) == assign[v]:
                            sat = True
                            break
                    else:
                        rem.append(lit)
                if sat:
                    continue
                if not rem:
                    return False
                if len(rem) == 1:
                    units.append(rem[0])
                new.append(tuple(rem))
            clauses = new
            if not units:
                break
            for u in units:
                v = abs(u)
                val = u > 0
                if v in assign:
                    if assign[v] != val:
                        return False
                else:
                    assign = dict(assign)
                    assign[v] = val
        var = None
        for cl in clauses:
            for lit in cl:
                if abs(lit) not in assign:
                    var = abs(lit)
                    break
            if var is not None:
                break
        if var is None:
            return True
        for val in (True, False):
            a2 = dict(assign)
            a2[var] = val
            if dpll(clauses, a2):
                return True
        return False

    return dpll(clauses, {})


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

TESTS_RUN = 0
TESTS_PASSED = 0
FAILURES = []


def check(instance, note=""):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    try:
        SubsetSum.validate(instance)
        reduced = R.reduce(instance)
        Sat.validate(reduced)
        expected = solve_subset_sum(instance)
        got = solve_sat(reduced)
        if expected == got:
            TESTS_PASSED += 1
            return True
        FAILURES.append(
            f"ANSWER MISMATCH {note}: {instance} -> expected {expected}, got {got}"
        )
        return False
    except Exception as exc:  # noqa: BLE001
        FAILURES.append(f"EXCEPTION {note}: {instance}: {type(exc).__name__}: {exc}")
        return False


def main():
    # 0. Sanity: our two SAT solvers agree with each other on small formulas.
    random.seed(12345)
    for _ in range(500):
        m = random.randint(0, 6)
        nclauses = random.randint(0, 6)
        clauses = []
        for _ in range(nclauses):
            k = random.randint(0, 4)
            clauses.append([random.choice([-1, 1]) * random.randint(1, m) for _ in range(k)] if m else [])
        inst = {"num_vars": m, "clauses": clauses}
        Sat.validate(inst)
        assert solve_sat(inst) == solve_sat_enum(inst), ("solver disagreement", inst)

    # 1. Exhaustive small instances: lists of length 0..3 over {0,1,2,3},
    #    every target from -1 .. sum+1.
    for length in range(0, 4):
        for numbers in itertools.product(range(0, 4), repeat=length):
            numbers = list(numbers)
            total = sum(numbers)
            for target in range(-1, total + 2):
                check({"numbers": numbers, "target": target}, "exhaustive")

    # 2. Random slightly larger instances.
    for _ in range(1500):
        length = random.randint(0, 6)
        numbers = [random.randint(0, 6) for _ in range(length)]
        total = sum(numbers)
        target = random.randint(-2, total + 2)
        check({"numbers": numbers, "target": target}, "random")

    # 3. Explicit edge cases.
    edge = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 1},
        {"numbers": [], "target": -1},
        {"numbers": [0], "target": 0},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [0, 0, 0], "target": 1},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 4},
        {"numbers": [1, 1, 1], "target": 3},
        {"numbers": [1, 1, 1], "target": 2},
        {"numbers": [1, 4, 1, 2], "target": 1},
        {"numbers": [3, 2], "target": 2},
        {"numbers": [2, 3], "target": 5},
        {"numbers": [2, 3], "target": 6},
    ]
    for inst in edge:
        check(inst, "edge")

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED} failures={len(FAILURES)}")
    for f in FAILURES[:20]:
        print("FAIL:", f)
    if len(FAILURES) > 20:
        print(f"... and {len(FAILURES) - 20} more failures")

    return 0 if not FAILURES else 1


if __name__ == "__main__":
    raise SystemExit(main())
