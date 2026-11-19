"""Independent verification tests for reduce.py (Subset Sum -> SAT).

We write our own brute-force solvers for both problems from the definitions
in problems.py, then:
  1. compare solver answers on many small source instances against the
     answers of our SAT solver on the reduced instances;
  2. check the edge cases described in the docstrings;
  3. check the *complexity* requirement: reduce must run in polynomial time
     and must not call a brute-force solver.
"""

from __future__ import annotations

import itertools
import random
import subprocess
import sys
import textwrap

from problems import SubsetSum, Sat
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Our own brute-force solvers, written directly from the definitions.

def subset_sum_solve(instance: dict) -> bool:
    """Yes iff some sub-list sums to target.  Non-negative numbers."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True  # empty sub-list
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
        if target in reachable:
            return True
    return target in reachable


def sat_solve(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for clause in clauses:
        if len(clause) == 0:
            return False  # empty clause can never be satisfied
    for bits in range(1 << m):
        values = {v: bool((bits >> (v - 1)) & 1) for v in range(1, m + 1)}
        if all(
            any(values[abs(lit)] == (lit > 0) for lit in clause)
            for clause in clauses
        ):
            return True
    return False


# ----------------------------------------------------------------------
# Test bookkeeping.

tests_run = 0
tests_passed = 0
failures = []


def check(name: str, condition: bool) -> None:
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
    else:
        failures.append(name)


# ----------------------------------------------------------------------
# 1. Many small random source instances compared against their reductions.

def random_source_instance(rng: random.Random) -> dict:
    n = rng.randint(0, 9)
    numbers = [rng.randint(0, 12) for _ in range(n)]
    # Include negative / zero / positive targets and occasionally a
    # reachable target.
    choice = rng.random()
    if choice < 0.2:
        target = rng.randint(-5, -1)
    elif choice < 0.35:
        target = 0
    elif choice < 0.7:
        target = rng.randint(0, sum(numbers) + 3)
    else:
        target = rng.randint(0, 15)
    return {"numbers": numbers, "target": target}


def test_random_comparisons() -> None:
    rng = random.Random(12345)
    for i in range(400):
        inst = random_source_instance(rng)
        SubsetSum.validate(inst)
        expected = subset_sum_solve(inst)
        reduced = reduce_mod.reduce(inst)
        Sat.validate(reduced)
        got = sat_solve(reduced)
        check(
            f"random[{i}] {inst} -> {reduced} expected={expected} got={got}",
            expected == got,
        )


# ----------------------------------------------------------------------
# 2. Explicit edge cases.

def test_edge_cases() -> None:
    cases = [
        {"numbers": [], "target": 0},          # empty list, t=0 -> yes
        {"numbers": [], "target": 1},          # empty list, t>0 -> no
        {"numbers": [], "target": -1},         # empty list, t<0 -> no
        {"numbers": [1, 2, 3], "target": 0},   # t=0 always yes
        {"numbers": [1, 2, 3], "target": -7},  # t<0 always no
        {"numbers": [1, 2, 3], "target": 6},   # whole list -> yes
        {"numbers": [1, 2, 3], "target": 7},   # unreachable -> no
        {"numbers": [0, 0, 0], "target": 0},   # zeros
        {"numbers": [0, 5], "target": 5},      # zero padding
        {"numbers": [2, 2, 2], "target": 4},   # repeats
        {"numbers": [4, 4, 4], "target": 6},   # repeats, no
        {"numbers": [10 ** 6, 1], "target": 10 ** 6},  # big value
        {"numbers": [10 ** 6, 1], "target": 10 ** 6 + 1},
        {"numbers": [10 ** 6, 1], "target": 999999},   # big, no
    ]
    for i, inst in enumerate(cases):
        SubsetSum.validate(inst)
        expected = subset_sum_solve(inst)
        reduced = reduce_mod.reduce(inst)
        Sat.validate(reduced)
        got = sat_solve(reduced)
        check(
            f"edge[{i}] {inst} -> {reduced} expected={expected} got={got}",
            expected == got,
        )


# ----------------------------------------------------------------------
# 3. Complexity / no-brute-force requirement.
#
# A correct polynomial-time reduction must handle a large "no" instance
# quickly.  We run reduce in a subprocess with a hard timeout.  The
# instance below is a no-instance (all numbers even, target odd) with 30
# numbers, so an internal bit-mask brute force would need 2**30 steps.

def test_polynomial_time_no_bruteforce() -> None:
    script = textwrap.dedent(
        """
        from reduce import reduce
        inst = {"numbers": [2] * 30, "target": 1}
        out = reduce(inst)
        print(out)
        """
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", script],
            cwd=".",
            capture_output=True,
            text=True,
            timeout=10,
        )
        ok = proc.returncode == 0
        detail = proc.stderr.strip()[-200:] if not ok else proc.stdout.strip()
    except subprocess.TimeoutExpired:
        ok = False
        detail = "TIMEOUT: reduce did not finish in 10s on a 30-element no-instance"
    check(f"polynomial_time_no_bruteforce ({detail})", ok)


def main() -> None:
    test_random_comparisons()
    test_edge_cases()
    test_polynomial_time_no_bruteforce()
    print(f"TESTS_RUN={tests_run}")
    print(f"TESTS_PASSED={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures:
            print("  -", f)


if __name__ == "__main__":
    main()
