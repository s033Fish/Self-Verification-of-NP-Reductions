"""Tests for the SAT -> 3-SAT reduction in reduce.py.

Contains brute-force solvers written directly from the problem
definitions, plus randomized and edge-case tests comparing the source
answer with the reduced answer.  Also validates every reduced instance
against problems.TARGET.validate.

All test instances are kept small enough that brute force over the
reduced formula (which may introduce fresh variables) is feasible.
"""

from __future__ import annotations

import itertools
import json
import random

import problems
from reduce import reduce

# Brute force is 2**num_vars; refuse to run it on larger instances.
MAX_BRUTE_VARS = 18


def sat_brute_force(instance: dict) -> bool:
    """Brute-force SAT solver (source problem)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    assert m <= MAX_BRUTE_VARS, f"too many vars for brute force: {m}"
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for clause in clauses:
            if not any(
                (bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                for l in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


def three_sat_brute_force(instance: dict) -> bool:
    """Brute-force 3-SAT solver (target problem)."""
    return sat_brute_force(instance)


def check(instance: dict) -> bool:
    """Reduce, validate, solve both sides and compare.  Returns agreement."""
    problems.SOURCE.validate(instance)
    reduced = reduce(instance)
    problems.TARGET.validate(reduced)
    assert reduced["num_vars"] <= MAX_BRUTE_VARS, (
        f"reduced instance too big for brute force: {reduced['num_vars']}"
    )
    return sat_brute_force(instance) == three_sat_brute_force(reduced)


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def record(condition: bool) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        if condition:
            tests_passed += 1

    # ---- Deterministic edge cases -------------------------------------
    edge_cases = [
        {"num_vars": 0, "clauses": []},                       # yes
        {"num_vars": 0, "clauses": [[]]},                     # no
        {"num_vars": 1, "clauses": []},                       # yes
        {"num_vars": 1, "clauses": [[]]},                     # no
        {"num_vars": 3, "clauses": [[1]]},                    # yes
        {"num_vars": 3, "clauses": [[-1]]},                   # yes
        {"num_vars": 3, "clauses": [[1], [-1]]},              # no
        {"num_vars": 3, "clauses": [[1, 2]]},                 # yes
        {"num_vars": 3, "clauses": [[1, 2], [-1], [-2]]},     # no
        {"num_vars": 3, "clauses": [[1, 2, 3]]},              # yes
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1], [-2], [-3]]},  # no
        {"num_vars": 4, "clauses": [[1, 2, 3, 4]]},           # yes
        {"num_vars": 4, "clauses": [[1, 2, 3, 4], [-1], [-2], [-3], [-4]]},  # no
        {"num_vars": 5, "clauses": [[1, 2, 3, 4, 5]]},        # yes
        {"num_vars": 5, "clauses": [[1, 2, 3, 4, 5], [-1], [-2], [-3], [-4], [-5]]},  # no
        {"num_vars": 2, "clauses": [[1, -1]]},                # tautology -> yes
        {"num_vars": 2, "clauses": [[1, 1, 1]]},              # repeats -> yes
        {"num_vars": 2, "clauses": [[1, 1], [-1, -1]]},       # no
        {"num_vars": 2, "clauses": [[1, -1], [2, -2]]},       # tautologies -> yes
        {"num_vars": 2, "clauses": [[1, 2, 1, 2]]},           # repeats -> yes
        {"num_vars": 3, "clauses": [[1, 2, 3, -1]]},          # tautology -> yes
        {"num_vars": 3, "clauses": [[1, 2], [2, 3], [-1, -3]]},  # yes
        {"num_vars": 3, "clauses": [[1, 2], [2, 3], [-1, -2], [-2, -3]]},  # no
        {"num_vars": 4, "clauses": [[1, 2, 3, 4], [1, 2], [-3, -4]]},
        {"num_vars": 6, "clauses": [[1, 2, 3, 4, 5, 6]]},
        {"num_vars": 4, "clauses": [[1, 2, 3, 4], [-1], [-2], [-3], [-4]]},
        {"num_vars": 4, "clauses": [[1, 2, 3, 4], [1, 2, 3, 4]]},  # duplicate clause
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},   # duplicate 3-clause
        {"num_vars": 2, "clauses": [[1], [1], [1]]},          # duplicate unit
        {"num_vars": 2, "clauses": [[1, 2], [1, 2]]},         # duplicate pair
    ]
    for instance in edge_cases:
        record(check(instance))

    # ---- Randomized small instances (kept small for brute force) ------
    rng = random.Random(12345)
    for _ in range(3000):
        m = rng.randint(0, 4)
        n_clauses = rng.randint(0, 4)
        clauses = []
        for _ in range(n_clauses):
            if m == 0:
                clauses.append([])  # only valid clause when there are no vars
                continue
            length = rng.randint(0, 4)
            clause = []
            for _ in range(length):
                v = rng.randint(1, m)
                sign = rng.choice((1, -1))
                clause.append(sign * v)
            clauses.append(clause)
        instance = {"num_vars": m, "clauses": clauses}
        record(check(instance))

    # ---- Randomized instances biased toward longer clauses ------------
    for _ in range(800):
        m = rng.randint(3, 4)
        n_clauses = rng.randint(1, 3)
        clauses = []
        for _ in range(n_clauses):
            length = rng.randint(3, 5)
            clause = []
            for _ in range(length):
                v = rng.randint(1, m)
                sign = rng.choice((1, -1))
                clause.append(sign * v)
            clauses.append(clause)
        instance = {"num_vars": m, "clauses": clauses}
        record(check(instance))

    # ---- Exhaustive over all tiny formulas ----------------------------
    # All clauses over variables 1..2 with lengths 0..2, and all pairs of
    # them.
    literals_2 = [1, -1, 2, -2]
    all_clauses_2 = [[]]
    for length in (1, 2):
        all_clauses_2.extend(
            [list(c) for c in itertools.product(literals_2, repeat=length)]
        )
    for c1 in all_clauses_2:
        record(check({"num_vars": 2, "clauses": [c1]}))
        for c2 in all_clauses_2:
            record(check({"num_vars": 2, "clauses": [c1, c2]}))

    # ---- Exhaustive over all 3-literal clauses on 3 vars --------------
    literals_3 = [1, -1, 2, -2, 3, -3]
    for c in itertools.product(literals_3, repeat=3):
        record(check({"num_vars": 3, "clauses": [list(c)]}))

    # ---- Structural checks: output really is valid 3-SAT --------------
    for _ in range(1000):
        m = rng.randint(0, 5)
        clauses = []
        for _ in range(rng.randint(0, 5)):
            if m == 0:
                clauses.append([])
                continue
            clauses.append(
                [rng.choice((1, -1)) * rng.randint(1, m)
                 for _ in range(rng.randint(0, 6))]
            )
        reduced = reduce({"num_vars": m, "clauses": clauses})
        ok = True
        try:
            problems.TARGET.validate(reduced)
        except problems.InvalidInstance:
            ok = False
        if reduced["clauses"]:
            ok = ok and reduced["num_vars"] >= 3
        # Fresh variables must not collide with originals.
        ok = ok and reduced["num_vars"] >= m
        record(ok)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"

    with open("verdict.json", "w") as fh:
        json.dump(
            {
                "verified": tests_run == tests_passed,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
            },
            fh,
        )


if __name__ == "__main__":
    main()
