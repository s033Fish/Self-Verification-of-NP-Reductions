"""Tests for the SAT -> Clique reduction in reduce.py."""
import random

import problems
from problems import Sat, Clique
from reduce import reduce


def check(instance, results):
    """Validate the reduction and compare brute-force answers."""
    Sat.validate(instance)
    reduced = reduce(instance)
    Clique.validate(reduced)  # must be a legal Clique instance
    expected = Sat.is_yes(instance)
    got = Clique.is_yes(reduced)
    results["run"] += 1
    if expected == got:
        results["passed"] += 1
    else:
        results["failures"].append((instance, reduced, expected, got))


def main():
    results = {"run": 0, "passed": 0, "failures": []}

    # 1. Exhaustive small instances (all clause subsets over <= 2 variables).
    for scale in (0, 1, 2):
        for instance in Sat.enumerate_instances(scale):
            check(instance, results)

    # 2. Hand-picked edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},                       # no clauses -> yes
        {"num_vars": 0, "clauses": [[]]},                     # empty clause -> no
        {"num_vars": 1, "clauses": []},                       # yes
        {"num_vars": 1, "clauses": [[1]]},                    # yes
        {"num_vars": 1, "clauses": [[-1]]},                   # yes
        {"num_vars": 1, "clauses": [[1], [-1]]},              # no
        {"num_vars": 1, "clauses": [[1, -1]]},                # yes (tautology)
        {"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2]]},   # yes
        {"num_vars": 2, "clauses": [[1], [-1], [2], [-2]]},   # no
        {"num_vars": 2, "clauses": [[1, 1], [-1]]},           # repeated literal
        {"num_vars": 2, "clauses": [[1], [1], [1]]},          # repeated clause
        {"num_vars": 2, "clauses": [[1, -1], [2], [-2]]},     # no
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},  # yes
        {"num_vars": 3, "clauses": [[1], [2], [3], [-1], [-2], [-3]]},  # no
        {"num_vars": 3, "clauses": [[1, 2], [-1, 3], [-2, -3]]},  # yes
        {"num_vars": 4, "clauses": [[1], [2], [3], [4], [-1, -2, -3, -4]]},  # no
    ]
    for instance in edge_cases:
        check(instance, results)

    # 3. Random small instances from the problem generator.
    rng = random.Random(12345)
    for _ in range(2000):
        scale = rng.randint(0, 5)
        instance = Sat.random_instance(rng, scale)
        check(instance, results)

    # 4. Random instances with empty clauses / duplicates injected.
    rng = random.Random(999)
    for _ in range(2000):
        m = rng.randint(0, 4)
        clauses = []
        for _ in range(rng.randint(0, 6)):
            if m == 0 or rng.random() < 0.15:
                clauses.append([])
                continue
            length = rng.randint(0, 4)
            clauses.append([rng.choice([-1, 1]) * rng.randint(1, m) for _ in range(length)])
        instance = {"num_vars": m, "clauses": clauses}
        check(instance, results)

    print(f"tests_run={results['run']} tests_passed={results['passed']}")
    for failure in results["failures"][:5]:
        print("FAILURE:", failure)

    verified = results["run"] == results["passed"]
    import json
    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": verified, "tests_run": results["run"], "tests_passed": results["passed"]},
            fh,
        )
    return verified


if __name__ == "__main__":
    ok = main()
    raise SystemExit(0 if ok else 1)
