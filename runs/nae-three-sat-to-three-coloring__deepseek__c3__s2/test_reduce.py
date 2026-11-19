"""Tests for the NAE-3-SAT -> 3-Coloring reduction in reduce.py.

We compare the brute-force solvers in problems.py on many small source
instances and on their reductions.  Sizes are kept small because the
target brute-force solver is exponential.
"""

import json
import random
from itertools import combinations

import problems
from problems import three_literal_clauses
from reduce import reduce

SOURCE = problems.SOURCE
TARGET = problems.TARGET


def check(instance, results):
    """Validate, reduce, validate, and compare brute-force answers."""
    SOURCE.validate(instance)
    out = reduce(instance)
    TARGET.validate(out)
    expected = SOURCE.is_yes(instance)
    got = TARGET.is_yes(out)
    results["run"] += 1
    if expected == got:
        results["passed"] += 1
    else:
        results["failures"].append((instance, out, expected, got))
    return expected == got


def main():
    results = {"run": 0, "passed": 0, "failures": []}

    # 1. Exhaustive over all formulas with num_vars <= 3 (all subsets of the
    #    8 possible clauses at scale 3, plus smaller scales).
    for scale in range(4):
        for instance in SOURCE.enumerate_instances(scale):
            check(instance, results)

    # 2. All formulas with num_vars == 4 and at most 2 clauses (there are 32
    #    possible clauses, so enumerate combinations rather than 2^32 subsets).
    clauses4 = three_literal_clauses(4)
    for size in range(0, 3):
        for subset in combinations(clauses4, size):
            check({"num_vars": 4, "clauses": list(subset)}, results)

    # 3. Explicit edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 2, "clauses": []},
        {"num_vars": 5, "clauses": []},
        # unsatisfiable NAE instance: x1=x2=x3 forced equal by two clauses
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        # satisfiable with repeated clauses
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3]]},
        # variables not all appearing
        {"num_vars": 6, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]]},
        # single positive clause is satisfiable (e.g. one true, two false)
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
        # larger variable count, few clauses
        {"num_vars": 8, "clauses": [[1, 2, 3], [-1, -2, -3], [4, 5, 6], [-4, -5, -6]]},
    ]
    for instance in edge_cases:
        check(instance, results)

    # 4. Random instances with a bounded number of clauses (small enough for
    #    the target brute-force solver).
    rng = random.Random(12345)
    for _ in range(600):
        m = rng.randint(0, 6)
        count = rng.randint(0, 4) if m >= 3 else 0
        clauses = []
        for _ in range(count):
            variables = sorted(rng.sample(range(1, m + 1), 3))
            clauses.append([v if rng.random() < 0.5 else -v for v in variables])
        check({"num_vars": m, "clauses": clauses}, results)

    # 5. Random instances with more clauses but few variables.
    rng = random.Random(999)
    for _ in range(400):
        m = rng.randint(3, 5)
        count = rng.randint(1, 6)
        clauses = []
        for _ in range(count):
            variables = sorted(rng.sample(range(1, m + 1), 3))
            clauses.append([v if rng.random() < 0.5 else -v for v in variables])
        check({"num_vars": m, "clauses": clauses}, results)

    # 6. Check output shape and polynomial size on larger instances.
    for trial in range(50):
        instance = SOURCE.random_instance(random.Random(trial), 20)
        out = reduce(instance)
        TARGET.validate(out)
        expected_vertices = 3 + 2 * instance["num_vars"] + 3 * len(instance["clauses"])
        assert out["n"] == expected_vertices, (out["n"], expected_vertices)

    print(f"tests_run={results['run']} tests_passed={results['passed']}")
    for failure in results["failures"][:5]:
        print("FAILURE:", failure)

    verified = results["run"] == results["passed"] and results["run"] > 0
    with open("verdict.json", "w") as handle:
        json.dump(
            {
                "verified": verified,
                "tests_run": results["run"],
                "tests_passed": results["passed"],
            },
            handle,
        )
    print("verdict.json written:", verified)
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
