"""Tests for the Subset Sum -> SAT reduction.

Contains independent solvers for both problems:
  * brute_subset_sum : exhaustive search over subsets
  * dp_subset_sum    : exact pseudo-polynomial bitset DP (cross-check)
  * solve_sat        : a small CDCL SAT solver (watched literals + learning)

Compares the answers on many small/medium/large instances plus edge cases.
"""

import json
import random

from problems import Sat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solver for Subset Sum
# ----------------------------------------------------------------------
def brute_subset_sum(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    n = len(numbers)
    for mask in range(1 << n):
        total = 0
        for i in range(n):
            if (mask >> i) & 1:
                total += numbers[i]
        if total == target:
            return True
    return False


# ----------------------------------------------------------------------
# Exact pseudo-polynomial DP for Subset Sum (bitset)
# ----------------------------------------------------------------------
def dp_subset_sum(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    reachable = 1
    for a in numbers:
        reachable |= reachable << a
    return (reachable >> target) & 1 == 1


# ----------------------------------------------------------------------
# CDCL SAT solver
# ----------------------------------------------------------------------
def solve_sat(instance):
    raw = instance["clauses"]
    m = instance["num_vars"]

    clauses = []
    for c in raw:
        s = set(c)
        if any(-l in s for l in s):
            continue  # tautology
        if not s:
            return False  # empty clause
        clauses.append(list(s))
    if not clauses:
        return True

    watches = {}

    def watch(lit, ci):
        watches.setdefault(lit, []).append(ci)

    assign = [0] * (m + 1)   # 0 unassigned, 1 true, -1 false
    level = [0] * (m + 1)
    reason = [None] * (m + 1)
    trail = []
    trail_lim = []
    qhead = 0
    activity = [0.0] * (m + 1)
    var_inc = 1.0
    var_decay = 0.95

    def value(lit):
        a = assign[abs(lit)]
        if a == 0:
            return 0
        return a if lit > 0 else -a

    def enqueue(lit, r):
        v = abs(lit)
        assign[v] = 1 if lit > 0 else -1
        level[v] = len(trail_lim)
        reason[v] = r
        trail.append(lit)

    def propagate():
        nonlocal qhead
        while qhead < len(trail):
            p = trail[qhead]
            qhead += 1
            neg = -p
            ws = watches.get(neg, [])
            watches[neg] = []
            i = 0
            while i < len(ws):
                ci = ws[i]
                i += 1
                c = clauses[ci]
                if c[0] == neg:
                    c[0], c[1] = c[1], c[0]
                first = c[0]
                if value(first) > 0:
                    watches[neg].append(ci)
                    continue
                found = False
                for k in range(2, len(c)):
                    if value(c[k]) >= 0:
                        c[1] = c[k]
                        c[k] = neg
                        watches.setdefault(c[1], []).append(ci)
                        found = True
                        break
                if found:
                    continue
                watches[neg].append(ci)
                if value(first) < 0:
                    return ci
                enqueue(first, ci)
        return None

    def bump(v):
        nonlocal var_inc
        activity[v] += var_inc
        if activity[v] > 1e100:
            for i in range(1, m + 1):
                activity[i] *= 1e-100
            var_inc *= 1e-100

    def analyze(confl):
        nonlocal var_inc
        learnt = [0]
        seen = [False] * (m + 1)
        counter = 0
        p = None
        idx = len(trail) - 1
        while True:
            c = clauses[confl]
            for q in c:
                if p is not None and q == p:
                    continue
                v = abs(q)
                if not seen[v] and level[v] > 0:
                    seen[v] = True
                    var_inc *= 1.0 / var_decay
                    bump(v)
                    if level[v] == len(trail_lim):
                        counter += 1
                    else:
                        learnt.append(q)
            while not seen[abs(trail[idx])]:
                idx -= 1
            p = trail[idx]
            idx -= 1
            seen[abs(p)] = False
            counter -= 1
            if counter == 0:
                break
            confl = reason[abs(p)]
        learnt[0] = -p
        if len(learnt) == 1:
            return learnt, 0
        maxlev = 0
        maxi = 1
        for i in range(1, len(learnt)):
            lv = level[abs(learnt[i])]
            if lv > maxlev:
                maxlev = lv
                maxi = i
        learnt[1], learnt[maxi] = learnt[maxi], learnt[1]
        return learnt, maxlev

    def backtrack(bt):
        nonlocal qhead
        if len(trail_lim) <= bt:
            return
        lim = trail_lim[bt]
        for i in range(len(trail) - 1, lim - 1, -1):
            v = abs(trail[i])
            assign[v] = 0
            reason[v] = None
        del trail[lim:]
        del trail_lim[bt:]
        qhead = len(trail)

    # root-level unit clauses
    for ci, c in enumerate(clauses):
        if len(c) == 1:
            if value(c[0]) < 0:
                return False
            if value(c[0]) == 0:
                enqueue(c[0], None)
    if propagate() is not None:
        return False

    while True:
        confl = propagate()
        if confl is not None:
            if not trail_lim:
                return False
            learnt, bt = analyze(confl)
            backtrack(bt)
            ci = len(clauses)
            clauses.append(learnt)
            watch(learnt[0], ci)
            if len(learnt) >= 2:
                watch(learnt[1], ci)
            enqueue(learnt[0], ci)
        else:
            # pick unassigned variable with highest activity
            best = 0
            best_act = -1.0
            for v in range(1, m + 1):
                if assign[v] == 0 and activity[v] > best_act:
                    best_act = activity[v]
                    best = v
            if best == 0:
                return True
            trail_lim.append(len(trail))
            enqueue(best, None)  # try True first


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------
def run_tests():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, expected):
        nonlocal tests_run, tests_passed
        tests_run += 1
        SubsetSum.validate(instance)
        reduced = reduce(instance)
        Sat.validate(reduced)
        got = solve_sat(reduced)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((instance, expected, got, reduced))

    # --- explicit edge cases ---
    edge = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 5},
        {"numbers": [], "target": -3},
        {"numbers": [1, 2, 3], "target": 0},
        {"numbers": [1, 2, 3], "target": -1},
        {"numbers": [0, 0, 0], "target": 0},
        {"numbers": [0, 0, 0], "target": 1},
        {"numbers": [5], "target": 5},
        {"numbers": [5], "target": 4},
        {"numbers": [2, 2], "target": 4},
        {"numbers": [2, 2], "target": 3},
        {"numbers": [1, 2, 3, 4, 5], "target": 15},
        {"numbers": [1, 2, 3, 4, 5], "target": 14},
        {"numbers": [1, 2, 3, 4, 5], "target": 16},
        {"numbers": [10 ** 18, 1], "target": 10 ** 18},
        {"numbers": [10 ** 18, 1], "target": 10 ** 18 + 1},
        {"numbers": [10 ** 18, 1], "target": 10 ** 18 - 1},
        {"numbers": [7, 7, 7, 7], "target": 21},
        {"numbers": [7, 7, 7, 7], "target": 22},
        {"numbers": [0, 5, 0], "target": 5},
        {"numbers": [3, 3, 3], "target": 9},
        {"numbers": [3, 3, 3], "target": 10},
    ]
    for inst in edge:
        check(inst, brute_subset_sum(inst))

    rng = random.Random(12345)

    # --- random small instances (brute force reference) ---
    for _ in range(300):
        n = rng.randint(0, 5)
        numbers = [rng.randint(0, 7) for _ in range(n)]
        target = rng.randint(-2, 20)
        inst = {"numbers": numbers, "target": target}
        check(inst, brute_subset_sum(inst))

    # --- more random instances with tiny values ---
    for n in range(0, 5):
        for _ in range(50):
            numbers = [rng.randint(0, 3) for _ in range(n)]
            target = rng.randint(0, 12)
            inst = {"numbers": numbers, "target": target}
            check(inst, brute_subset_sum(inst))

    return tests_run, tests_passed, failures


def extra_tests():
    tests_run = 0
    tests_passed = 0
    failures = []
    rng = random.Random(999)

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        SubsetSum.validate(instance)
        expected = dp_subset_sum(instance)
        reduced = reduce(instance)
        Sat.validate(reduced)
        got = solve_sat(reduced)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((instance, expected, got))

    # medium instances
    for _ in range(200):
        n = rng.randint(0, 12)
        numbers = [rng.randint(0, 60) for _ in range(n)]
        target = rng.randint(-3, sum(numbers) + 5)
        check({"numbers": numbers, "target": target})

    # large values
    for _ in range(60):
        n = rng.randint(1, 8)
        numbers = [rng.randint(0, 10 ** 15) for _ in range(n)]
        total = sum(numbers)
        target = rng.choice([0, total, max(0, total - 1), total + 1,
                             rng.randint(0, total + 2)])
        check({"numbers": numbers, "target": target})

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    tr, tp, fails = run_tests()
    er, ep, efails = extra_tests()
    tests_run = tr + er
    tests_passed = tp + ep
    failures = fails + efails
    verified = tests_passed == tests_run and not failures
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for f in failures[:5]:
        print("FAIL:", f)
    with open("verdict.json", "w") as fh:
        json.dump(
            {
                "verified": verified,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
            },
            fh,
        )
    print("verdict:", verified)
