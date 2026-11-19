"""Independent verification of reduce.py for 3-SAT -> 1-in-3-SAT.

We implement our own brute-force solvers for both problems directly from the
definitions in problems.py, then compare answers on many small source
instances and their reductions.  We also check the requirement that reduce()
runs in polynomial time without calling a brute-force solver.
"""

from __future__ import annotations

import itertools
import json
import random
import time

from problems import ThreeSat, OneInThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Our own brute-force solvers (written from the definitions).

def solve_three_sat(instance) -> bool:
    """Yes iff some assignment satisfies every 3-SAT clause."""
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        if all(
            any((lit > 0) == bits[abs(lit) - 1] for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_one_in_three_sat(instance) -> bool:
    """Yes iff some assignment makes exactly one var true in every clause."""
    OneInThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        if all(sum(1 for v in clause if bits[v - 1]) == 1 for clause in clauses):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation.

def gen_instances():
    """Yield a variety of small, valid source instances."""
    # Explicit edge cases.
    yield {"num_vars": 0, "clauses": []}
    yield {"num_vars": 1, "clauses": []}
    yield {"num_vars": 3, "clauses": []}
    yield {"num_vars": 3, "clauses": [[1, 2, 3]]}
    yield {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]}  # duplicate clause
    yield {"num_vars": 3, "clauses": [[-1, -2, -3]]}
    yield {"num_vars": 4, "clauses": [[1, 2, 3], [-1, 2, 4], [1, -2, -4]]}

    rng = random.Random(20240517)
    for m in range(0, 6):
        if m < 3:
            continue
        for _ in range(40):
            n_clauses = rng.randint(0, 6)
            clauses = []
            for _ in range(n_clauses):
                vs = rng.sample(range(1, m + 1), 3)
                clause = [v if rng.random() < 0.5 else -v for v in vs]
                clauses.append(clause)
            yield {"num_vars": m, "clauses": clauses}


def main():
    tests_run = 0
    tests_passed = 0
    mismatches = []

    for inst in gen_instances():
        src = solve_three_sat(inst)
        target = reduce(inst)
        # The produced instance must be a valid target instance.
        OneInThreeSat.validate(target)
        tgt = solve_one_in_three_sat(target)
        tests_run += 1
        if src == tgt:
            tests_passed += 1
        else:
            mismatches.append((inst, src, target, tgt))

    print(f"equivalence checks: {tests_passed}/{tests_run} passed")
    if mismatches:
        for mm in mismatches[:5]:
            print("MISMATCH:", mm)

    # ------------------------------------------------------------------
    # Polynomial-time / no-brute-force requirement check.
    #
    # Craft an unsatisfiable 3-SAT instance with many variables so that any
    # exhaustive 2^m search is expensive, then time reduce().  A genuine
    # polynomial reduction returns quickly; a brute-force one does not.
    m = 24
    # Force x1=...=xm=true and false simultaneously via unit-like 3-clauses
    # over fresh helper variables: (x or a or b), (not x or a or b) for each x.
    # Simpler: chain of clauses that is unsat but requires full search.
    clauses = []
    # For each i, clauses (x_i or x_i+1 or x_i+2) and (not x_i or not x_i+1 or not x_i+2)
    # alone are satisfiable; use the classic "all 8 clauses over 3 vars" style
    # contradiction on a block of 3 vars repeated to make it clearly unsat.
    # Contradiction: exactly-one constraints are not expressible in 3-SAT
    # trivially, so use a hard unsat core: for vars 1,2,3 add all 8 clauses?
    # All 8 clauses over 3 vars is unsat.  Add it, then pad with more vars.
    for signs in itertools.product((1, -1), repeat=3):
        clauses.append([signs[0] * 1, signs[1] * 2, signs[2] * 3])
    inst_big = {"num_vars": m, "clauses": clauses}
    t0 = time.time()
    out = reduce(inst_big)
    elapsed = time.time() - t0
    print(f"reduce() on unsat m={m} took {elapsed:.3f}s")
    # A brute-force search over 2^24 assignments must take noticeably long;
    # treat > 2.0s as evidence of exponential brute force.
    brute_force_detected = elapsed > 2.0
    print(f"brute-force behaviour detected: {brute_force_detected}")

    # Also verify the reduction's answer is still correct here.
    assert solve_one_in_three_sat(out) == solve_three_sat(inst_big)

    verified = (tests_passed == tests_run) and not brute_force_detected
    verdict = {
        "verified": bool(verified),
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
