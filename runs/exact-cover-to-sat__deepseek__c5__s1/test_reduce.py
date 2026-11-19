"""Independent verification of reduce.py: Exact Cover -> SAT.

We implement brute-force solvers for both problems from the definitions in
problems.py (which provides no solvers), then compare the source answer with
the answer to the reduced SAT instance on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import ExactCover, Sat, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_exact_cover(instance: dict) -> bool:
    """True iff some subfamily of the given sets is pairwise disjoint and
    covers the whole universe exactly once."""
    u = instance["universe_size"]
    sets = instance["sets"]
    full = (1 << u) - 1
    n = len(sets)

    masks = []
    for s in sets:
        m = 0
        for e in s:
            m |= 1 << e
        masks.append(m)

    # Try every subset of the sets.
    for chosen in range(1 << n):
        union = 0
        ok = True
        for i in range(n):
            if chosen & (1 << i):
                if union & masks[i]:   # overlap -> not disjoint
                    ok = False
                    break
                union |= masks[i]
        if ok and union == full:
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        # variable v (1..m) is true iff bit (v-1) set
        sat = True
        for clause in clauses:
            if not any(((bits >> (abs(lit) - 1)) & 1) == (1 if lit > 0 else 0)
                       for lit in clause):
                sat = False
                break
        if sat:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators.

def all_subsets(u):
    elems = list(range(u))
    for r in range(u + 1):
        for combo in itertools.combinations(elems, r):
            yield list(combo)


def enumerate_instances(max_u=3, max_sets=3):
    """Exhaustively enumerate small Exact Cover instances (lists of sets)."""
    for u in range(max_u + 1):
        pool = list(all_subsets(u))
        for k in range(max_sets + 1):
            for sets in itertools.product(pool, repeat=k):
                yield {"universe_size": u, "sets": [list(s) for s in sets]}


def random_instance(rng, max_u=5, max_sets=6):
    u = rng.randint(0, max_u)
    k = rng.randint(0, max_sets)
    sets = []
    for _ in range(k):
        size = rng.randint(0, u)
        elems = rng.sample(range(u), size)
        sets.append(elems)
    return {"universe_size": u, "sets": sets}


# ----------------------------------------------------------------------
# Tests.

def run():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        # validate source instance
        ExactCover.validate(inst)
        expected = solve_exact_cover(inst)
        out = reduce(inst)
        # reduction must produce a valid target instance
        Sat.validate(out)
        got = solve_sat(out)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((inst, expected, out, got))

    # Exhaustive small enumeration
    for inst in enumerate_instances(max_u=3, max_sets=3):
        check(inst)

    # A few slightly larger exhaustive-ish cases
    for inst in enumerate_instances(max_u=4, max_sets=2):
        check(inst)

    # Random tests
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_instance(rng, max_u=6, max_sets=7))

    # Targeted edge cases
    edge = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[], [], []]},
        {"universe_size": 1, "sets": []},
        {"universe_size": 1, "sets": [[]]},
        {"universe_size": 1, "sets": [[0]]},
        {"universe_size": 1, "sets": [[0], [0]]},
        {"universe_size": 2, "sets": [[0], [1]]},
        {"universe_size": 2, "sets": [[0, 1], [0], [1]]},
        {"universe_size": 2, "sets": [[0, 1], [0, 1]]},
        {"universe_size": 3, "sets": [[0, 1], [1, 2], [0, 2]]},
        {"universe_size": 3, "sets": [[0, 1, 2]]},
        {"universe_size": 3, "sets": [[0], [1], [2], []]},
        {"universe_size": 3, "sets": [[0], [0, 1], [1, 2], [2]]},
        {"universe_size": 4, "sets": [[0, 1], [2, 3], [0], [1], [2], [3]]},
    ]
    for inst in edge:
        check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for inst, expected, out, got in failures[:10]:
            print("  inst:", inst)
            print("    expected:", expected, "got:", got, "sat:", out)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    run()


# ----------------------------------------------------------------------
# Additional, stronger exact solvers for larger random instances.

def dpll_sat(num_vars, clauses):
    def simplify(cls, assign):
        new = []
        for cl in cls:
            sat = False
            rem = []
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
                return None
            new.append(rem)
        return new

    def solve(cls, assign):
        cls = simplify(cls, assign)
        if cls is None:
            return False
        if not cls:
            return True
        while True:
            unit = next((cl[0] for cl in cls if len(cl) == 1), None)
            if unit is None:
                break
            assign = dict(assign)
            assign[abs(unit)] = unit > 0
            cls = simplify(cls, assign)
            if cls is None:
                return False
            if not cls:
                return True
        v = abs(cls[0][0])
        for val in (True, False):
            a = dict(assign)
            a[v] = val
            if solve(cls, a):
                return True
        return False

    return solve(clauses, {})


def backtrack_exact_cover(u, sets):
    masks = []
    for s in sets:
        m = 0
        for e in s:
            m |= 1 << e
        masks.append(m)
    full = (1 << u) - 1
    order = sorted(range(len(sets)), key=lambda i: -bin(masks[i]).count("1"))

    def rec(idx, covered):
        if covered == full:
            return True
        if idx == len(order):
            return False
        m = masks[order[idx]]
        if m & covered == 0 and rec(idx + 1, covered | m):
            return True
        return rec(idx + 1, covered)

    return rec(0, 0)


def run_larger(n=4000, seed=999):
    rng = random.Random(seed)
    tr = tp = 0
    fails = []
    for _ in range(n):
        inst = random_instance(rng, max_u=8, max_sets=10)
        tr += 1
        ExactCover.validate(inst)
        exp = backtrack_exact_cover(inst["universe_size"], inst["sets"])
        out = reduce(inst)
        Sat.validate(out)
        got = dpll_sat(out["num_vars"], out["clauses"])
        if exp == got:
            tp += 1
        else:
            fails.append((inst, exp, got))
    print(f"larger tests_run={tr} tests_passed={tp}")
    return tr, tp, fails


def run_all():
    a = run()
    b = run_larger()
    total_run = a[0] + b[0]
    total_pass = a[1] + b[1]
    print(f"TOTAL tests_run={total_run} tests_passed={total_pass}")
    return total_run, total_pass, a[2] + b[2]
