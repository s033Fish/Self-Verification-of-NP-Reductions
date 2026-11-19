"""Brute-force solvers and tests for the 3-SAT -> Subset Sum reduction."""

from __future__ import annotations

import itertools
import json
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.


def solve_three_sat(instance: dict) -> bool:
    """True iff some assignment satisfies every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=num_vars):
        # variable v (1-indexed) is bits[v-1]
        if all(
            any((lit > 0) == bits[abs(lit) - 1] for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_subset_sum(instance: dict) -> bool:
    """True iff some sub-list sums to the target."""
    target = instance["target"]
    if target < 0:
        return False
    reachable = {0}
    for number in instance["numbers"]:
        reachable |= {s + number for s in reachable}
    return target in reachable


# ----------------------------------------------------------------------
# Random small instance generator (3-SAT).


def random_three_sat(rng: random.Random) -> dict:
    num_vars = rng.randint(0, 6)
    max_clauses = 0 if num_vars < 3 else rng.randint(0, 6)
    num_clauses = rng.randint(0, max_clauses) if max_clauses else 0
    clauses = []
    for _ in range(num_clauses):
        variables = rng.sample(range(1, num_vars + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in variables]
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


# ----------------------------------------------------------------------
# Tests.


def main() -> None:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(source_instance: dict, label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        SOURCE.validate(source_instance)
        reduced = reduce(source_instance)
        TARGET.validate(reduced)
        expected = solve_three_sat(source_instance)
        got = solve_subset_sum(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, source_instance, reduced, expected, got))

    # Hand-picked edge cases.
    check({"num_vars": 0, "clauses": []}, "empty formula m=0")
    check({"num_vars": 5, "clauses": []}, "no clauses m=5")
    check({"num_vars": 3, "clauses": [[1, 2, 3]]}, "single satisfied clause")
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]}, "single clause all false")
    check(
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        "contradictory clauses",
    )
    # Duplicate clauses and repeated structure.
    check(
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 3], [-4, 2, 3]]},
        "duplicate clauses",
    )
    # Unused variables.
    check({"num_vars": 6, "clauses": [[1, 2, 3]]}, "unused variables")

    # Random instances.
    for index in range(3000):
        check(random_three_sat(rng), f"random-{index}")

    # Exhaustive over all small formulas with m in {3,4} and up to 2 clauses.
    for num_vars in (3, 4):
        literals = [v for v in range(1, num_vars + 1)] + [
            -v for v in range(1, num_vars + 1)
        ]
        all_clauses = [
            list(c)
            for c in itertools.combinations(
                [l for l in literals], 3
            )
            if len({abs(x) for x in c}) == 3
        ]
        for clause in all_clauses:
            check({"num_vars": num_vars, "clauses": [clause]}, "exhaustive-1")
        for c1, c2 in itertools.combinations(all_clauses, 2):
            check(
                {"num_vars": num_vars, "clauses": [list(c1), list(c2)]},
                "exhaustive-2",
            )

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as handle:
        json.dump(verdict, handle)

    print("tests_run =", tests_run)
    print("tests_passed =", tests_passed)
    print("failures =", len(failures))
    for failure in failures[:5]:
        print(failure)
    print("verdict =", verdict)


if __name__ == "__main__":
    main()
