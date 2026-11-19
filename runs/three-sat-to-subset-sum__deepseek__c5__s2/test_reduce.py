"""Independent verification of reduce.py (3-SAT -> Subset Sum).

We write our own brute-force solvers for both problems from the docstring
definitions, then compare answers on many small source instances and their
reductions.
"""

import itertools
import random

from problems import ThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.
# ----------------------------------------------------------------------

def solve_three_sat(instance):
    """Yes iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                (lit > 0 and bits[lit - 1]) or (lit < 0 and not bits[-lit - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def _subset_sums(values):
    sums = {0}
    for a in values:
        sums |= {s + a for s in sums}
    return sums


def solve_subset_sum(instance):
    """Yes iff some sub-list sums to exactly target.

    Meet-in-the-middle so it stays fast even when the reduction produces
    many numbers.
    """
    numbers = list(instance["numbers"])
    target = instance["target"]
    if target < 0:
        return False
    half = len(numbers) // 2
    left = _subset_sums(numbers[:half])
    right = _subset_sums(numbers[half:])
    for s in left:
        if (target - s) in right:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def random_three_sat(rng, max_vars=6, max_clauses=8):
    m = rng.randint(0, max_vars)
    k = rng.randint(0, max_clauses)
    clauses = []
    if m >= 3:
        for _ in range(k):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_clauses_for(m):
    """All distinct 3-literal clauses over m variables."""
    out = []
    for vs in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product([1, -1], repeat=3):
            out.append([s * v for s, v in zip(signs, vs)])
    return out


def run_case(instance, label):
    """Validate, reduce, solve both, compare. Return (ok, detail)."""
    ThreeSat.validate(instance)
    reduced = reduce(instance)
    SubsetSum.validate(reduced)
    src = solve_three_sat(instance)
    tgt = solve_subset_sum(reduced)
    if src != tgt:
        return False, f"MISMATCH [{label}] src={src} tgt={tgt}\n  in={instance}\n  out={reduced}"
    return True, ""


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        ok, detail = run_case(instance, label)
        if ok:
            tests_passed += 1
        else:
            failures.append(detail)

    # --- Edge cases -----------------------------------------------------
    check({"num_vars": 0, "clauses": []}, "m=0 no clauses")
    check({"num_vars": 1, "clauses": []}, "m=1 no clauses")
    check({"num_vars": 5, "clauses": []}, "m=5 no clauses")

    unsat3 = all_clauses_for(3)
    check({"num_vars": 3, "clauses": unsat3}, "all 8 clauses m=3 (unsat)")
    check({"num_vars": 3, "clauses": unsat3[:-1]}, "7 clauses m=3 (sat)")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]}, "dup clauses")
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]}, "all negative")
    check({"num_vars": 6, "clauses": [[1, 2, 3]]}, "unused vars")

    # --- Exhaustive over all subsets of clauses for m=3 -----------------
    for r in range(len(unsat3) + 1):
        for combo in itertools.combinations(unsat3, r):
            check({"num_vars": 3, "clauses": [list(c) for c in combo]},
                  f"m=3 subset r={r}")

    # --- Exhaustive small subsets for m=4 -------------------------------
    clauses4 = all_clauses_for(4)
    for r in range(0, 4):
        for combo in itertools.combinations(clauses4, r):
            check({"num_vars": 4, "clauses": [list(c) for c in combo]},
                  f"m=4 subset r={r}")

    # --- Random tests ---------------------------------------------------
    rng = random.Random(12345)
    for i in range(2000):
        check(random_three_sat(rng, max_vars=5, max_clauses=6), f"random {i}")

    for i in range(300):
        check(random_three_sat(rng, max_vars=8, max_clauses=12), f"random-mid {i}")


    # --- More targeted cases --------------------------------------------
    # Embedded unsatisfiable triple among larger variable sets.
    c5 = all_clauses_for(5)
    for triple in itertools.combinations(range(1, 6), 3):
        sub = [c for c in c5 if set(abs(x) for x in c) == set(triple)]
        check({"num_vars": 5, "clauses": sub}, f"embedded unsat {triple}")

    # Random subsets of m=4 clauses (bounded).
    c4 = all_clauses_for(4)
    for i in range(3000):
        r = rng.randint(0, 10)
        combo = rng.sample(c4, r)
        check({"num_vars": 4, "clauses": [list(c) for c in combo]}, f"m4 subset {i}")

    # Duplicated clauses.
    for i in range(500):
        m = rng.randint(3, 6)
        base = random_three_sat(rng, max_vars=m, max_clauses=5)["clauses"]
        clauses = [list(c) for c in base] * rng.randint(1, 4)
        check({"num_vars": m, "clauses": clauses}, f"dups {i}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:10]:
            print(f)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
