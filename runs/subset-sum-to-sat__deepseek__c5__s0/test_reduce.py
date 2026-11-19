"""Independent verification tests for reduce.py (SubsetSum -> SAT).

We implement our own brute-force/DPLL solvers for both problems directly from
the docstrings in problems.py, then check on many small source instances that

    subset_sum_solve(instance) == sat_solve(reduce(instance))

and that reduce(instance) is a valid Sat instance.  We also check that the
reduction is polynomial-time (no brute force) by timing larger inputs.
"""

from __future__ import annotations

import itertools
import random
import time

from problems import SubsetSum, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the problem definitions
# ----------------------------------------------------------------------

def subset_sum_solve(instance):
    """Exact subset-sum: DP over reachable sums."""
    numbers = instance["numbers"]
    t = instance["target"]
    if t < 0:
        return False
    reachable = {0}
    for a in numbers:
        reachable |= {r + a for r in reachable}
    return t in reachable


def _simplify(clauses, assignment):
    out = []
    for clause in clauses:
        new_clause = []
        satisfied = False
        for lit in clause:
            v = abs(lit)
            if v in assignment:
                val = assignment[v]
                if (lit > 0 and val) or (lit < 0 and not val):
                    satisfied = True
                    break
            else:
                new_clause.append(lit)
        if satisfied:
            continue
        if not new_clause:
            return None
        out.append(new_clause)
    return out


def sat_solve(instance):
    """Exact SAT via DPLL with unit propagation and pure literals."""
    clauses = [list(c) for c in instance["clauses"]]
    if not clauses:
        return True

    def dpll(clauses, assignment):
        clauses = _simplify(clauses, assignment)
        if clauses is None:
            return False
        if not clauses:
            return True
        while True:
            unit = None
            for clause in clauses:
                if len(clause) == 1:
                    unit = clause[0]
                    break
            if unit is None:
                break
            v = abs(unit)
            val = unit > 0
            if v in assignment and assignment[v] != val:
                return False
            assignment = dict(assignment)
            assignment[v] = val
            clauses = _simplify(clauses, assignment)
            if clauses is None:
                return False
            if not clauses:
                return True
        while True:
            pos, neg = set(), set()
            for clause in clauses:
                for lit in clause:
                    (pos if lit > 0 else neg).add(abs(lit))
            pure = None
            for v in pos:
                if v not in neg:
                    pure = v
                    break
            if pure is None:
                for v in neg:
                    if v not in pos:
                        pure = -v
                        break
            if pure is None:
                break
            assignment = dict(assignment)
            assignment[abs(pure)] = pure > 0
            clauses = _simplify(clauses, assignment)
            if clauses is None:
                return False
            if not clauses:
                return True
        v = abs(clauses[0][0])
        for val in (True, False):
            a2 = dict(assignment)
            a2[v] = val
            if dpll(clauses, a2):
                return True
        return False

    return dpll(clauses, {})



def brute_sat(instance):
    """Naive enumeration SAT solver for cross-checking sat_solve."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if not clauses:
        return True
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            if not any(
                ((mask >> (abs(l) - 1)) & 1) == (1 if l > 0 else 0)
                for l in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

TESTS_RUN = 0
TESTS_PASSED = 0
FAILURES = []


def check(instance):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    try:
        SubsetSum.validate(instance)
        reduced = reduce(instance)
        Sat.validate(reduced)
        expected = subset_sum_solve(instance)
        got = sat_solve(reduced)
        if expected == got:
            TESTS_PASSED += 1
        else:
            FAILURES.append((instance, expected, got))
    except Exception as exc:  # noqa: BLE001
        FAILURES.append((instance, "exception", repr(exc)))


def main():
    global TESTS_RUN, TESTS_PASSED
    # 1. Exhaustive small instances: n = 0..4, values 0..3, targets -1..10
    for n in range(0, 5):
        for nums in itertools.product(range(0, 4), repeat=n):
            for t in range(-1, 11):
                check({"numbers": list(nums), "target": t})

    # 2. Exhaustive n = 5 with values 0..2
    for nums in itertools.product(range(0, 3), repeat=5):
        for t in range(-1, 9):
            check({"numbers": list(nums), "target": t})

    # 3. Exhaustive n = 6 with values 0..1
    for nums in itertools.product(range(0, 2), repeat=6):
        for t in range(-1, 8):
            check({"numbers": list(nums), "target": t})

    # 4. Edge cases
    edge = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 1},
        {"numbers": [], "target": -1},
        {"numbers": [0], "target": 0},
        {"numbers": [0], "target": 1},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [0, 0, 0], "target": 1},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 4},
        {"numbers": [5], "target": 6},
        {"numbers": [1, 2, 4, 8], "target": 15},
        {"numbers": [1, 2, 4, 8], "target": 16},
        {"numbers": [7, 7, 7], "target": 14},
        {"numbers": [7, 7, 7], "target": 21},
        {"numbers": [7, 7, 7], "target": 22},
        {"numbers": [2 ** 20, 2 ** 20 + 1], "target": 2 ** 21 + 1},
        {"numbers": [2 ** 20, 2 ** 20 + 1], "target": 2 ** 20},
        {"numbers": [10 ** 18, 1], "target": 10 ** 18 + 1},
        {"numbers": [10 ** 18, 1], "target": 10 ** 18},
    ]
    for inst in edge:
        check(inst)

    # 5. Randomised small instances
    rng = random.Random(20240607)
    for _ in range(1500):
        n = rng.randint(0, 6)
        nums = [rng.randint(0, 12) for _ in range(n)]
        total = sum(nums)
        t = rng.randint(-2, total + 3)
        check({"numbers": nums, "target": t})

    # 6. Carry-heavy instances (many 1s / powers of two)
    for _ in range(400):
        n = rng.randint(0, 9)
        nums = [rng.choice([1, 1, 1, 2, 4, 8, 3, 7]) for _ in range(n)]
        total = sum(nums)
        t = rng.randint(-1, total + 2)
        check({"numbers": nums, "target": t})

    # 7. Large-value instances
    for _ in range(200):
        n = rng.randint(0, 4)
        nums = [rng.randint(0, 2 ** 20) for _ in range(n)]
        total = sum(nums)
        t = rng.randint(-1, total + 5)
        check({"numbers": nums, "target": t})

    # 7b. Cross-check DPLL against naive enumeration on reduced instances
    #     that are small enough to enumerate.
    rng2 = random.Random(424242)
    cross_checked = 0
    while cross_checked < 200:
        n = rng2.randint(0, 3)
        nums = [rng2.randint(0, 3) for _ in range(n)]
        total = sum(nums)
        t = rng2.randint(-1, total + 1)
        inst = {"numbers": nums, "target": t}
        reduced = reduce(inst)
        if reduced["num_vars"] <= 18:
            TESTS_RUN += 1
            if sat_solve(reduced) == brute_sat(reduced):
                TESTS_PASSED += 1
            else:
                FAILURES.append((inst, "dpll-vs-brute", reduced))
            cross_checked += 1

    # 8. Polynomial-time / no-brute-force sanity check on larger inputs.
    for n, bits in [(100, 40), (300, 80)]:
        nums = [rng.getrandbits(bits) for _ in range(n)]
        total = sum(nums)
        inst = {"numbers": nums, "target": total // 2}
        start = time.time()
        reduced = reduce(inst)
        elapsed = time.time() - start
        Sat.validate(reduced)
        # A genuinely polynomial reduction must finish quickly here.
        assert elapsed < 30.0, f"reduce too slow: {elapsed}s"
        TESTS_RUN += 1
        TESTS_PASSED += 1

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED} "
          f"failures={len(FAILURES)}")
    for f in FAILURES[:10]:
        print("FAIL:", f)

    import json
    with open("verdict.json", "w") as fh:
        json.dump(
            {
                "verified": len(FAILURES) == 0,
                "tests_run": TESTS_RUN,
                "tests_passed": TESTS_PASSED,
            },
            fh,
        )
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    raise SystemExit(main())
