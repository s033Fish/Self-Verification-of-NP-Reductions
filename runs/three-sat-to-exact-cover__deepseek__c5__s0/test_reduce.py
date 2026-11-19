"""Independent tests for reduce.py (3-SAT -> Exact Cover).

We implement brute-force solvers for both problems from the definitions in
problems.py, generate many small valid 3-SAT instances, reduce them, and
compare answers.  We also validate that every produced instance is a valid
Exact Cover instance.
"""

import itertools
import random

import problems
from problems import ThreeSat, ExactCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions).

def solve_three_sat(instance):
    """Return True iff the 3-SAT instance is satisfiable."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        # variable v (1..m) is bits[v-1]
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance):
    """Return True iff the exact-cover instance has a solution.

    Backtracking: pick the smallest uncovered element, try every set that
    contains it and is disjoint from the current partial cover.
    """
    u = instance["universe_size"]
    full = (1 << u) - 1

    # represent each set as a bitmask; drop empty sets (never useful)
    masks = []
    for s in instance["sets"]:
        mask = 0
        for e in s:
            mask |= (1 << e)
        if mask:
            masks.append(mask)

    # by_elem[e] = list of set masks containing element e
    by_elem = [[] for _ in range(u)]
    for mask in masks:
        for e in range(u):
            if mask & (1 << e):
                by_elem[e].append(mask)

    import sys
    sys.setrecursionlimit(100000)

    def rec(covered):
        if covered == full:
            return True
        # first uncovered element
        remaining = full & ~covered
        e = (remaining & -remaining).bit_length() - 1
        for mask in by_elem[e]:
            if covered & mask:
                continue  # overlap
            if rec(covered | mask):
                return True
        return False

    return rec(0)


# ----------------------------------------------------------------------
# Instance generators (valid instances only).

def random_three_sat(rng, max_vars=6, max_clauses=4):
    m = rng.randint(0, max_vars)
    if m < 3:
        clauses = []
    else:
        n = rng.randint(0, max_clauses)
        clauses = []
        for _ in range(n):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_clauses_over(m):
    """All 3-clauses over variables 1..m (as tuples of literals)."""
    out = []
    for vs in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            out.append(tuple(s * v for s, v in zip(signs, vs)))
    return out


def make_instances():
    insts = []
    # Explicit edge cases.
    insts.append({"num_vars": 0, "clauses": []})
    insts.append({"num_vars": 5, "clauses": []})
    # Unsatisfiable: all 8 clauses over 3 variables.
    insts.append({"num_vars": 3, "clauses": [list(c) for c in all_clauses_over(3)]})
    # Duplicate clauses.
    insts.append({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
    # A clearly satisfiable one.
    insts.append({"num_vars": 3, "clauses": [[1, 2, 3]]})
    # Variables that do not appear.
    insts.append({"num_vars": 6, "clauses": [[1, 2, 3]]})

    rng = random.Random(12345)
    for _ in range(400):
        insts.append(random_three_sat(rng))

    # Small exhaustive-ish random over 3-4 vars with many clauses.
    rng2 = random.Random(999)
    for _ in range(200):
        m = rng2.randint(3, 4)
        n = rng2.randint(0, 8)
        clauses = []
        for _ in range(n):
            vs = rng2.sample(range(1, m + 1), 3)
            clause = [v if rng2.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
        insts.append({"num_vars": m, "clauses": clauses})

    # Exhaustive: every subset of the 8 clauses over variables 1..3.
    base = [list(c) for c in all_clauses_over(3)]
    for mask in range(1 << len(base)):
        clauses = [base[i] for i in range(len(base)) if (mask >> i) & 1]
        insts.append({"num_vars": 3, "clauses": clauses})

    # Exhaustive: every subset of clauses over variables 1..4 using only
    # clauses with a fixed variable set, to keep it small but varied.
    base4 = [list(c) for c in all_clauses_over(4)]
    rng3 = random.Random(7)
    for _ in range(300):
        n = rng3.randint(0, 6)
        clauses = [rng3.choice(base4) for _ in range(n)]
        insts.append({"num_vars": 4, "clauses": clauses})

    # Random 5-6 var formulas with more clauses (harder satisfiability mix).
    rng4 = random.Random(2024)
    for _ in range(300):
        m = rng4.randint(5, 6)
        n = rng4.randint(0, 12)
        clauses = []
        for _ in range(n):
            vs = rng4.sample(range(1, m + 1), 3)
            clause = [v if rng4.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
        insts.append({"num_vars": m, "clauses": clauses})

    return insts


def large_instance_checks():
    """Validity + timing checks on larger instances (no brute force)."""
    import time
    results = []
    rng = random.Random(4242)
    for m, n in [(10, 30), (50, 150), (200, 600)]:
        clauses = []
        for _ in range(n):
            vs = rng.sample(range(1, m + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
        inst = {"num_vars": m, "clauses": clauses}
        ThreeSat.validate(inst)
        t0 = time.time()
        red = reduce(inst)
        dt = time.time() - t0
        ExactCover.validate(red)  # must be a valid target instance
        # expected universe size from the construction
        assert red["universe_size"] == m + 3 * n + n + 3 * n
        assert len(red["sets"]) == 2 * m + 3 * n * 3
        results.append((m, n, dt))
    return results


def main():
    insts = make_instances()
    tests_run = 0
    tests_passed = 0
    failures = []
    for inst in insts:
        tests_run += 1
        ThreeSat.validate(inst)  # ensure our generator makes valid instances
        src = solve_three_sat(inst)
        red = reduce(inst)
        # reduction must produce a valid Exact Cover instance
        try:
            ExactCover.validate(red)
            valid = True
        except problems.InvalidInstance as exc:
            valid = False
            failures.append((inst, "invalid reduction output: %s" % exc))
        if not valid:
            continue
        tgt = solve_exact_cover(red)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, red, src, tgt))

    # larger-instance validity/timing checks count as tests too
    for (m, n, dt) in large_instance_checks():
        tests_run += 1
        tests_passed += 1
        print("large instance m=%d n=%d reduce_time=%.4fs valid" % (m, n, dt))

    print("tests_run =", tests_run)
    print("tests_passed =", tests_passed)
    if failures:
        print("FAILURES:")
        for f in failures[:10]:
            print(f)
    else:
        print("ALL TESTS PASSED")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
