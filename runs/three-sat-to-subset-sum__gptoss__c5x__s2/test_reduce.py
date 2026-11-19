"""Independent tests for reduce.py (3-SAT -> Subset Sum).

We implement our own brute-force solvers for both problems from the
definitions in problems.py, then compare the answers on many small source
instances and their reductions.

We also check the *requirements* on reduce:
  * output must be a valid SubsetSum instance,
  * answers must agree (yes iff yes),
  * reduce must run in polynomial time and must NOT call a brute-force solver.
"""

from __future__ import annotations

import itertools
import random
import time

from problems import ThreeSat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Our own brute-force solvers (from the definitions, independent of reduce.py)
# ----------------------------------------------------------------------

def solve_three_sat(instance) -> bool:
    """Yes iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def solve_subset_sum(instance) -> bool:
    """Yes iff some sub-list (each position at most once) sums to target."""
    numbers = instance["numbers"]
    target = instance["target"]
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Instance generation (only valid instances)
# ----------------------------------------------------------------------

def all_clauses(m):
    """All valid 3-literal clauses over variables 1..m (3 distinct vars)."""
    out = []
    for vars_ in itertools.combinations(range(1, m + 1), 3):
        for signs in itertools.product((1, -1), repeat=3):
            out.append([s * v for s, v in zip(signs, vars_)])
    return out


def source_instances():
    """Yield a deterministic collection of small valid 3-SAT instances."""
    # m = 0, 1, 2 : no clauses allowed (a clause needs m >= 3).
    for m in (0, 1, 2):
        yield {"num_vars": m, "clauses": []}

    # m = 3 : exhaustively every subset of the 8 possible clauses.
    clauses3 = all_clauses(3)
    for r in range(len(clauses3) + 1):
        for combo in itertools.combinations(clauses3, r):
            yield {"num_vars": 3, "clauses": [list(c) for c in combo]}

    # m = 4, 5 : random subsets of clauses (seeded for reproducibility).
    rng = random.Random(12345)
    for m in (4, 5):
        clauses = all_clauses(m)
        for _ in range(400):
            k = rng.randint(0, len(clauses))
            chosen = rng.sample(clauses, k)
            yield {"num_vars": m, "clauses": [list(c) for c in chosen]}

    # Instances with variables that do not appear in any clause.
    rng = random.Random(999)
    for m in (6, 7):
        clauses = all_clauses(m)
        for _ in range(100):
            k = rng.randint(0, min(6, len(clauses)))
            chosen = rng.sample(clauses, k)
            yield {"num_vars": m, "clauses": [list(c) for c in chosen]}


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in source_instances():
        tests_run += 1
        expected = solve_three_sat(inst)
        try:
            out = reduce(inst)
        except Exception as exc:  # noqa: BLE001
            failures.append(("reduce raised", inst, repr(exc)))
            continue
        # Output must be a valid SubsetSum instance.
        try:
            SubsetSum.validate(out)
        except Exception as exc:  # noqa: BLE001
            failures.append(("invalid output", inst, repr(exc)))
            continue
        got = solve_subset_sum(out)
        if got == expected:
            tests_passed += 1
        else:
            failures.append(("answer mismatch", inst, out, expected, got))

    # ---- Requirement: reduce must be polynomial time / no brute force ----
    # A brute-force 3-SAT solver enumerates 2^m assignments.  We detect this
    # behaviourally using an UNSATISFIABLE formula over variables 1..3 embedded
    # in a formula with m variables: a brute-force solver must scan all 2^m
    # assignments before returning "no", so its runtime doubles with each
    # extra variable.  A genuine polynomial reduction is fast for large m.
    unsat_clauses = []
    for vs in itertools.combinations([1, 2, 3], 3):
        for signs in itertools.product((1, -1), repeat=3):
            unsat_clauses.append([s * v for s, v in zip(signs, vs)])
    poly_ok = True
    timing = []
    for m in (18, 20, 22):
        inst = {"num_vars": m, "clauses": [list(c) for c in unsat_clauses]}
        t0 = time.time()
        out = reduce(inst)
        dt = time.time() - t0
        timing.append((m, dt))
        if solve_subset_sum(out) != solve_three_sat(inst):
            poly_ok = False
    # A genuine polynomial reduction should stay well under a second even at
    # m = 22; a 2^m brute-force solver needs ~2^22 = 4M assignment scans.
    slow = any(dt > 1.0 for _, dt in timing)
    if slow:
        poly_ok = False
    tests_run += 1
    if poly_ok:
        tests_passed += 1
    else:
        failures.append(("not polynomial / brute-force", timing))

    # ---- Static check: reduce.py must not contain a brute-force solver ----
    with open("reduce.py") as fh:
        src = fh.read()
    has_brute = ("1 << m" in src) or ("1 << num_vars" in src) or ("range(1 <<" in src)
    tests_run += 1
    if not has_brute:
        tests_passed += 1
    else:
        failures.append(("brute-force solver present in reduce.py",))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    print(f"timing (m, seconds): {timing}")
    print(f"brute-force solver detected in reduce.py: {has_brute}")
    if failures:
        print("FAILURES (first 10):")
        for f in failures[:10]:
            print("  ", f)
    else:
        print("no failures")

    return tests_run, tests_passed, failures, has_brute


if __name__ == "__main__":
    main()
