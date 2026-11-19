"""Independent tests for reduce.py (3-SAT -> NAE-3-SAT).

We implement our own brute-force solvers from the definitions in problems.py
(which has no solvers), generate many small source instances INCLUDING
unsatisfiable ones, and compare the answer of the source instance with the
answer of its reduction.
"""
import itertools
import json
import random
import time

from problems import ThreeSat, NaeThreeSat
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Independent brute-force solvers
# ----------------------------------------------------------------------
def solve_3sat(instance):
    """True iff some assignment satisfies every clause (>=1 true literal)."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        if all(
            any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1]) for l in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_nae3sat(instance):
    """True iff some assignment makes every clause not-all-equal."""
    NaeThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            vals = [
                (bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                for l in clause
            ]
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------
def all_clauses(m):
    """All valid 3-literal clauses over variables 1..m."""
    out = []
    for vars_ in itertools.permutations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            out.append([s * v for s, v in zip(signs, vars_)])
    return out


def random_instance(rng, m, max_clauses):
    clauses = all_clauses(m)
    k = rng.randint(0, min(max_clauses, len(clauses)))
    return {"num_vars": m, "clauses": [list(c) for c in rng.sample(clauses, k)]}


def unsat_instance(m):
    """A clearly unsatisfiable 3-SAT instance over m variables.

    For every one of the 2^m assignments we add the unique 3-literal clause
    that is falsified exactly by that assignment (all literals false).
    """
    clauses = []
    for bits in itertools.product([False, True], repeat=m):
        # choose 3 variables; clause is false iff all its literals are false
        clause = []
        for v in range(1, 4):
            clause.append(v if bits[v - 1] else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        src = solve_3sat(instance)
        try:
            red = reduce_mod.reduce(instance)
        except Exception as e:
            failures.append((label, instance, "reduce raised %r" % (e,)))
            return
        try:
            NaeThreeSat.validate(red)
        except Exception as e:
            failures.append((label, instance, "invalid target %r: %r" % (red, e)))
            return
        tgt = solve_nae3sat(red)
        if src != tgt:
            failures.append((label, instance, "src=%s tgt=%s red=%r" % (src, tgt, red)))
        else:
            tests_passed += 1

    # --- Edge cases: no clauses, m = 0..4 ---
    for m in range(0, 5):
        check({"num_vars": m, "clauses": []}, "no-clauses m=%d" % m)

    # --- Exhaustive-ish for m=3: all clause multisets of size 0..3 ---
    clauses3 = all_clauses(3)
    for size in range(0, 4):
        for combo in itertools.combinations(clauses3, size):
            check({"num_vars": 3, "clauses": [list(c) for c in combo]},
                  "m=3 size=%d" % size)

    # --- Random instances for m=3..5 ---
    for m in (3, 4, 5):
        for _ in range(400):
            check(random_instance(rng, m, 8), "random m=%d" % m)

    # --- Explicit UNSATISFIABLE sources (the key missing coverage) ---
    for m in (3, 4, 5):
        inst = unsat_instance(m)
        assert solve_3sat(inst) is False, "generator bug: should be unsat"
        check(inst, "unsat m=%d" % m)

    # All 8 clauses over 3 vars (classic unsat 3-SAT).
    check({"num_vars": 3, "clauses": [list(c) for c in clauses3]}, "all-8-clauses m=3")

    # --- Directly probe the two fixed instances returned by reduce.py ---
    sat_fixed = {"num_vars": 3, "clauses": [[1, -2, 3]]}
    unsat_fixed = {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}
    print("fixed sat  instance NAE-solvable:", solve_nae3sat(sat_fixed))
    print("fixed 'unsat' instance NAE-solvable:", solve_nae3sat(unsat_fixed))
    # The reduce() contract: unsat source must map to an unsat target.
    check(unsat_instance(3), "contract: unsat source -> target")

    # --- Complexity probe: reduce is exponential (brute force inside) ---
    print("\nComplexity probe (time for reduce on random large instances):")
    timings = []
    for m in (10, 14, 18, 22):
        inst = random_instance(rng, m, 4 * m)
        t0 = time.time()
        reduce_mod.reduce(inst)
        dt = time.time() - t0
        timings.append((m, dt))
        print("  m=%2d  clauses=%3d  reduce time = %.4fs" % (m, len(inst["clauses"]), dt))

    print("\ntests_run =", tests_run)
    print("tests_passed =", tests_passed)
    print("failures =", len(failures))
    for f in failures[:10]:
        print("  FAIL:", f)

    verified = (tests_run == tests_passed) and not failures
    with open("verdict.json", "w") as fh:
        json.dump({"verified": verified, "tests_run": tests_run,
                   "tests_passed": tests_passed}, fh, indent=2)
    print("\nverdict.json:", {"verified": verified, "tests_run": tests_run,
                              "tests_passed": tests_passed})


if __name__ == "__main__":
    main()
