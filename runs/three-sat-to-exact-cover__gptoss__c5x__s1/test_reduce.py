"""Independent tests for reduce.py: 3-SAT -> Exact Cover.

We implement our own brute-force solvers from the problem definitions in
problems.py, generate many small source instances, and compare the answer of
each source instance with the answer of its reduction.  We also validate the
reduced instance and test the polynomial-time requirement.
"""

from __future__ import annotations

import itertools
import random
import time

from problems import ThreeSat, ExactCover
import reduce as reduce_module


# ----------------------------------------------------------------------
# Brute-force solvers, written directly from the problem definitions.

def solve_three_sat(instance):
    """Return True iff the 3-SAT instance is satisfiable."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1]
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance):
    """Return True iff an exact cover of the universe exists."""
    ExactCover.validate(instance)
    u = instance["universe_size"]
    sets = instance["sets"]
    target = (1 << u) - 1
    reachable = {0}
    for s in sets:
        mask = 0
        for e in s:
            mask |= 1 << e
        if mask == 0:
            continue
        new = set(reachable)
        for cur in reachable:
            if cur & mask:
                continue
            new.add(cur | mask)
        reachable = new
    return target in reachable


# ----------------------------------------------------------------------
# Instance generators (small).

def random_three_sat(rng, max_vars=6, max_clauses=8):
    m = rng.randint(0, max_vars)
    if m < 3:
        clauses = []
    else:
        n_clauses = rng.randint(0, max_clauses)
        clauses = []
        for _ in range(n_clauses):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def exhaustive_small_three_sat():
    instances = []
    for m in (0, 1, 2):
        instances.append({"num_vars": m, "clauses": []})
    all_clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        all_clauses.append([s * v for s, v in zip(signs, (1, 2, 3))])
    for r in range(0, 4):
        for combo in itertools.combinations(all_clauses, r):
            instances.append({"num_vars": 3, "clauses": [list(c) for c in combo]})
    return instances


# ----------------------------------------------------------------------
# Tests

def test_solvers_agree_with_reduction():
    rng = random.Random(12345)
    instances = exhaustive_small_three_sat()
    for _ in range(400):
        instances.append(random_three_sat(rng))

    tests_run = 0
    tests_passed = 0
    failures = []
    for inst in instances:
        src = solve_three_sat(inst)
        reduced = reduce_module.reduce(inst)
        try:
            ExactCover.validate(reduced)
            valid = True
        except Exception as exc:  # noqa: BLE001
            valid = False
            failures.append((inst, "invalid reduced instance: %r" % (exc,)))
        tgt = solve_exact_cover(reduced) if valid else None
        tests_run += 1
        if valid and src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, reduced, src, tgt))
    return tests_run, tests_passed, failures


def test_edge_cases():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst):
        nonlocal tests_run, tests_passed
        tests_run += 1
        src = solve_three_sat(inst)
        reduced = reduce_module.reduce(inst)
        try:
            ExactCover.validate(reduced)
        except Exception as exc:  # noqa: BLE001
            failures.append((inst, "invalid: %r" % (exc,)))
            return
        tgt = solve_exact_cover(reduced)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, reduced, src, tgt))

    for m in (0, 1, 2, 3, 5):
        check({"num_vars": m, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3],
                                       [1, -2, 3], [-1, 2, -3],
                                       [1, 2, -3], [-1, -2, 3],
                                       [1, -2, -3], [-1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 6, "clauses": [[1, 2, 3]]})
    return tests_run, tests_passed, failures


def test_polynomial_time():
    """The reduction must run in polynomial time.

    We hold the number of clauses fixed and grow num_vars.  A polynomial-time
    reduction cannot have its output size (and runtime) double with every
    extra variable.  Returns (passed, times, ratios).
    """
    times = {}
    sizes = {}
    for m in (14, 16, 18, 20):
        inst = {"num_vars": m, "clauses": [[1, 2, 3], [-1, -2, -3]]}
        t0 = time.perf_counter()
        r = reduce_module.reduce(inst)
        times[m] = time.perf_counter() - t0
        sizes[m] = len(r["sets"])
    ratios = [times[b] / times[a] for a, b in ((14, 16), (16, 18), (18, 20))]
    size_ratios = [sizes[b] / sizes[a] for a, b in ((14, 16), (16, 18), (18, 20))]
    # Poly would keep these roughly constant; exponential doubles them.
    passed = all(r < 3.0 for r in ratios) and all(r < 3.0 for r in size_ratios)
    return passed, times, ratios, sizes, size_ratios


if __name__ == "__main__":
    tr1, tp1, f1 = test_solvers_agree_with_reduction()
    tr2, tp2, f2 = test_edge_cases()
    poly_passed, times, ratios, sizes, size_ratios = test_polynomial_time()

    tests_run = tr1 + tr2 + 1
    tests_passed = tp1 + tp2 + (1 if poly_passed else 0)
    failures = f1 + f2

    print("random+exhaustive: run=%d passed=%d" % (tr1, tp1))
    print("edge cases:        run=%d passed=%d" % (tr2, tp2))
    print("poly-time check:   passed=%s" % poly_passed)
    for f in failures[:20]:
        print("FAIL:", f)
    print("output sizes:", sizes)
    print("size ratios: ", [round(r, 2) for r in size_ratios])
    print("time ratios: ", [round(r, 2) for r in ratios])
    print("TOTAL run=%d passed=%d" % (tests_run, tests_passed))

    import json
    with open("verdict.json", "w") as fh:
        json.dump({"verified": bool(tests_run == tests_passed),
                   "tests_run": tests_run,
                   "tests_passed": tests_passed}, fh)
