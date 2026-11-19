"""Independent checks for reduce.py (Subset Sum -> SAT).

We implement solvers for both problems from the docstrings and compare the
answer of every small source instance with the answer of its reduction.  The
SAT solver is a straightforward DPLL search (unit propagation + branching),
which is exact and does not call any external solver.  We also validate that
the produced SAT instances are well formed.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import Sat, SubsetSum
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the problem definitions.
# ----------------------------------------------------------------------


def solve_subset_sum(instance: dict) -> bool:
    """Yes iff some sub-list sums to exactly target."""
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    if target == 0:
        return True  # empty sub-list
    reachable = {0}
    for a in numbers:
        reachable |= {s + a for s in reachable}
    return target in reachable


def _unit_propagate(clauses, assignment):
    """Return (clauses, assignment) after repeated unit propagation.

    Returns None if a conflict is found.
    """
    clauses = [list(c) for c in clauses]
    assignment = dict(assignment)
    changed = True
    while changed:
        changed = False
        new_clauses = []
        for clause in clauses:
            # simplify clause under current assignment
            sat = False
            unassigned = []
            for lit in clause:
                v = abs(lit)
                val = assignment.get(v)
                if val is None:
                    unassigned.append(lit)
                elif (lit > 0) == val:
                    sat = True
                    break
            if sat:
                continue
            if not unassigned:
                return None  # empty clause -> conflict
            if len(unassigned) == 1:
                lit = unassigned[0]
                v = abs(lit)
                val = lit > 0
                if v in assignment and assignment[v] != val:
                    return None
                assignment[v] = val
                changed = True
            else:
                new_clauses.append(unassigned)
        clauses = new_clauses
    return clauses, assignment


def solve_sat(instance: dict) -> bool:
    """Exact DPLL satisfiability check."""
    clauses = [list(c) for c in instance["clauses"]]
    # A clause with both a literal and its negation is a tautology; drop it.
    cleaned = []
    for c in clauses:
        s = set(c)
        if any(-lit in s for lit in s):
            continue
        cleaned.append(c)
    result = _dpll(cleaned, {})
    return result is not None


def _dpll(clauses, assignment):
    prop = _unit_propagate(clauses, assignment)
    if prop is None:
        return None
    clauses, assignment = prop
    if not clauses:
        return assignment
    # choose a variable appearing in the shortest clause
    shortest = min(clauses, key=len)
    lit = shortest[0]
    v = abs(lit)
    for val in (True, False):
        if v in assignment:
            continue
        new_assign = dict(assignment)
        new_assign[v] = val
        res = _dpll(clauses, new_assign)
        if res is not None:
            return res
    return None


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

tests_run = 0
tests_passed = 0
failures = []


def check(condition: bool, message: str) -> None:
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
    else:
        failures.append(message)


def check_instance(instance: dict, label: str) -> None:
    """Reduce one instance and compare answers / validate the result."""
    SubsetSum.validate(instance)
    try:
        out = reduce(instance)
    except Exception as exc:  # noqa: BLE001
        check(False, f"{label}: reduce raised {exc!r} for {instance!r}")
        return
    try:
        Sat.validate(out)
    except Exception as exc:  # noqa: BLE001
        check(False, f"{label}: invalid SAT output {exc!r} for {instance!r}")
        return
    expected = solve_subset_sum(instance)
    got = solve_sat(out)
    check(
        expected == got,
        f"{label}: mismatch for {instance!r}: subset_sum={expected} sat={got}",
    )


def main() -> None:
    rng = random.Random(12345)

    # --- explicit edge cases -------------------------------------------
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
        {"numbers": [1, 2, 3], "target": 6},
        {"numbers": [1, 2, 3], "target": 7},
        {"numbers": [1, 2, 3], "target": -5},
        {"numbers": [2, 2, 2, 2], "target": 4},
        {"numbers": [2, 2, 2, 2], "target": 3},
        {"numbers": [7, 7, 7], "target": 14},
        {"numbers": [1000000, 1], "target": 1000001},
        {"numbers": [1000000, 1], "target": 1000000},
        {"numbers": [2 ** 40, 1], "target": 2 ** 40 + 1},
        {"numbers": [2 ** 40, 1], "target": 2 ** 40 - 1},
        {"numbers": [3, 3, 3], "target": 9},
        {"numbers": [3, 3, 3], "target": 8},
        {"numbers": [8, 8, 8, 8], "target": 16},
        {"numbers": [8, 8, 8, 8], "target": 15},
    ]
    for i, inst in enumerate(edge):
        check_instance(inst, f"edge{i}")

    # --- many small random instances -----------------------------------
    for trial in range(3000):
        n = rng.randint(0, 6)
        numbers = [rng.randint(0, 8) for _ in range(n)]
        target = rng.randint(-2, 20)
        check_instance({"numbers": numbers, "target": target}, f"rand{trial}")

    # --- random instances with larger values ---------------------------
    for trial in range(1500):
        n = rng.randint(0, 5)
        numbers = [rng.randint(0, 40) for _ in range(n)]
        target = rng.randint(-1, 100)
        check_instance({"numbers": numbers, "target": target}, f"big{trial}")

    # --- exhaustive small enumeration ----------------------------------
    for n in range(0, 4):
        for numbers in itertools.product(range(0, 4), repeat=n):
            for target in range(-1, 13):
                check_instance(
                    {"numbers": list(numbers), "target": target},
                    f"exh{n}",
                )

    # --- determinism / repeatability -----------------------------------
    for trial in range(200):
        n = rng.randint(0, 6)
        inst = {
            "numbers": [rng.randint(0, 10) for _ in range(n)],
            "target": rng.randint(-1, 30),
        }
        out1 = reduce(inst)
        out2 = reduce(inst)
        check(out1 == out2, f"nondeterministic reduce for {inst!r}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:20]:
            print("  ", f)
    else:
        print("ALL TESTS PASSED")

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
