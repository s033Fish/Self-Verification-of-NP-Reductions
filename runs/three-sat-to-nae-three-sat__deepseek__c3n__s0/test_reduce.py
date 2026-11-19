"""Tests comparing brute-force answers of 3-SAT and its reduction to NAE-3-SAT."""

from __future__ import annotations

import itertools
import json
import random

import problems
from reduce import reduce


def solve_three_sat(instance):
    """Brute force 3-SAT."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=num_vars):
        if all(
            any((literal > 0) == bits[abs(literal) - 1] for literal in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_nae_three_sat(instance):
    """Brute force NAE-3-SAT."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=num_vars):
        if all(
            len({(literal > 0) == bits[abs(literal) - 1] for literal in clause}) == 2
            for clause in clauses
        ):
            return True
    return False


def random_instance(rng, max_vars=5, max_clauses=8):
    num_vars = rng.randint(0, max_vars)
    if num_vars < 3:
        clauses = []
    else:
        clauses = []
        for _ in range(rng.randint(0, max_clauses)):
            variables = rng.sample(range(1, num_vars + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in variables]
            clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        problems.ThreeSat.validate(instance)
        reduced = reduce(instance)
        problems.NaeThreeSat.validate(reduced)
        expected = solve_three_sat(instance)
        got = solve_nae_three_sat(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, instance, reduced, expected, got))

    # Hand-picked edge cases.
    check({"num_vars": 0, "clauses": []}, "empty m=0")
    check({"num_vars": 5, "clauses": []}, "empty m=5")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single positive clause")
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]}, "single negative clause")
    check({"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]}, "contradictory pair")
    check(
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
        "duplicate clauses",
    )
    check(
        {
            "num_vars": 3,
            "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3],
                        [-1, -2, 3], [-1, 2, -3], [1, -2, -3], [-1, -2, -3]],
        },
        "all 8 clauses (unsat)",
    )
    check(
        {
            "num_vars": 4,
            "clauses": [[1, 2, 3], [-1, -2, 4], [2, -3, -4], [-1, 3, 4]],
        },
        "mixed 4 vars",
    )

    # Exhaustive small instances: all formulas with m=3 vars, up to 3 clauses
    # drawn from the 8 possible clauses (with repetition allowed).
    all_clauses = []
    for variables in itertools.combinations(range(1, 4), 3):
        for signs in itertools.product((1, -1), repeat=3):
            all_clauses.append([v * s for v, s in zip(variables, signs)])
    for num_clauses in range(0, 4):
        for combo in itertools.combinations_with_replacement(all_clauses, num_clauses):
            check(
                {"num_vars": 3, "clauses": [list(c) for c in combo]},
                f"exhaustive m=3 k={num_clauses}",
            )

    # Random tests.
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_instance(rng), "random")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for failure in failures[:10]:
        print("FAILURE:", failure)

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as handle:
        json.dump(verdict, handle)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
