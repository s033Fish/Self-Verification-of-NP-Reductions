"""Tests for the 3-SAT -> NAE-3-SAT reduction in reduce.py.

problems.py provides no solvers, so we implement brute-force solvers for both
problems directly from their definitions, generate many small source
instances, and check that each source instance and its reduction agree.
"""

from __future__ import annotations

import itertools
import random

import problems
from problems import ThreeSat, NaeThreeSat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def _assignments(num_vars):
    for bits in itertools.product([False, True], repeat=num_vars):
        yield bits


def _lit_value(lit, bits):
    val = bits[abs(lit) - 1]
    return val if lit > 0 else not val


def solve_3sat(instance):
    """True iff some assignment makes every clause have >= 1 true literal."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in _assignments(num_vars):
        if all(any(_lit_value(l, bits) for l in clause) for clause in clauses):
            return True
    return False


def solve_nae_3sat(instance):
    """True iff some assignment makes every clause not all equal."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in _assignments(num_vars):
        ok = True
        for clause in clauses:
            vals = [_lit_value(l, bits) for l in clause]
            if all(vals) or not any(vals):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators (small, valid 3-SAT instances).

def random_3sat(num_vars, num_clauses, rng):
    clauses = []
    if num_vars < 3:
        assert num_clauses == 0
    for _ in range(num_clauses):
        vs = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def all_3sat_up_to(num_vars, max_clauses):
    """Enumerate many small instances: all single clauses + random mixes."""
    rng = random.Random(12345)
    instances = []
    # no clauses
    instances.append({"num_vars": num_vars, "clauses": []})
    if num_vars >= 3:
        # every possible single clause
        for vs in itertools.combinations(range(1, num_vars + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                instances.append(
                    {"num_vars": num_vars,
                     "clauses": [[v * s for v, s in zip(vs, signs)]]}
                )
        # random instances with several clauses
        for _ in range(300):
            k = rng.randint(1, max_clauses)
            instances.append(random_3sat(num_vars, k, rng))
    return instances


def main():
    tests_run = 0
    tests_passed = 0

    def check(cond, msg):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if cond:
            tests_passed += 1
        else:
            print("FAIL:", msg)

    # --- edge case: empty formula, m = 0
    inst = {"num_vars": 0, "clauses": []}
    ThreeSat.validate(inst)
    red = reduce(inst)
    NaeThreeSat.validate(red)
    check(solve_3sat(inst) is True, "empty m=0 source should be yes")
    check(solve_nae_3sat(red) is True, "empty m=0 reduction should be yes")

    # --- edge case: empty formula, m = 5
    inst = {"num_vars": 5, "clauses": []}
    ThreeSat.validate(inst)
    red = reduce(inst)
    NaeThreeSat.validate(red)
    check(solve_3sat(inst) is True, "empty m=5 source should be yes")
    check(solve_nae_3sat(red) is True, "empty m=5 reduction should be yes")

    # --- many small instances
    for num_vars in range(3, 7):
        for inst in all_3sat_up_to(num_vars, max_clauses=5):
            ThreeSat.validate(inst)
            red = reduce(inst)
            NaeThreeSat.validate(red)
            a = solve_3sat(inst)
            b = solve_nae_3sat(red)
            check(a == b, f"mismatch {inst} -> {red}: {a} vs {b}")

    # --- larger random instances (still brute-forceable: few vars)
    rng = random.Random(999)
    for _ in range(400):
        num_vars = rng.randint(3, 8)
        num_clauses = rng.randint(0, 8)
        inst = random_3sat(num_vars, num_clauses, rng)
        ThreeSat.validate(inst)
        red = reduce(inst)
        NaeThreeSat.validate(red)
        a = solve_3sat(inst)
        b = solve_nae_3sat(red)
        check(a == b, f"mismatch {inst} -> {red}: {a} vs {b}")

    # --- structural checks
    inst = {"num_vars": 4, "clauses": [[1, 2, 3], [-1, 2, -4], [3, -2, 4]]}
    red = reduce(inst)
    check(len(red["clauses"]) == 2 * len(inst["clauses"]), "clause count")
    check(red["num_vars"] == 4 + 1 + 3, "var count")
    # every target clause has 3 distinct variables
    for clause in red["clauses"]:
        check(len(clause) == 3 and len({abs(l) for l in clause}) == 3,
              f"bad target clause {clause}")

    # --- known satisfiable / unsatisfiable examples
    # (x1 or x2 or x3) & (x1 or x2 or ~x3) & ... classic small UNSAT over 3 vars
    unsat = {"num_vars": 3, "clauses": [
        [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
        [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3],
    ]}
    ThreeSat.validate(unsat)
    check(solve_3sat(unsat) is False, "all-8-clauses should be UNSAT")
    red = reduce(unsat)
    NaeThreeSat.validate(red)
    check(solve_nae_3sat(red) is False, "reduction of UNSAT should be UNSAT")

    sat = {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, 3]]}
    check(solve_3sat(sat) is True, "sat example should be SAT")
    red = reduce(sat)
    NaeThreeSat.validate(red)
    check(solve_nae_3sat(red) is True, "reduction of SAT should be SAT")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"

    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": tests_run == tests_passed,
                   "tests_run": tests_run,
                   "tests_passed": tests_passed}, f)
    print("wrote verdict.json")


if __name__ == "__main__":
    main()
