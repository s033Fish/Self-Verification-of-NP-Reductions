"""Tests for reduce.py: brute-force solvers + randomized/exhaustive checks."""

from __future__ import annotations

import itertools
import random

import problems
from reduce import reduce


def solve_one_in_three(instance):
    """Brute-force solver for 1-in-3-SAT."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for a, b, c in clauses:
            if bits[a - 1] + bits[b - 1] + bits[c - 1] != 1:
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False


def solve_three_sat(instance):
    """Brute-force solver for 3-SAT."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return True if not clauses else False


def random_source_instance(rng):
    m = rng.randint(0, 6)
    max_clauses = 0 if m < 3 else 5
    n_clauses = rng.randint(0, max_clauses)
    clauses = [rng.sample(range(1, m + 1), 3) for _ in range(n_clauses)]
    return {"num_vars": m, "clauses": clauses}


def check(inst, results):
    """Validate, reduce, validate, compare solvers. Record into results."""
    results["run"] += 1
    problems.OneInThreeSat.validate(inst)
    reduced = reduce(inst)
    problems.ThreeSat.validate(reduced)
    if solve_one_in_three(inst) == solve_three_sat(reduced):
        results["passed"] += 1
    else:
        print("MISMATCH", inst, "->", reduced)


def main():
    rng = random.Random(12345)
    results = {"run": 0, "passed": 0}

    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 2, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]},
        {"num_vars": 3, "clauses": [[1, 2, 3]] * 3},
        {"num_vars": 5, "clauses": [[1, 2, 3], [3, 4, 5]]},
    ]
    for inst in edge_cases:
        check(inst, results)

    for _ in range(500):
        check(random_source_instance(rng), results)

    # Exhaustive over all subsets of clauses for m <= 4.
    for m in range(0, 5):
        all_clauses = list(itertools.combinations(range(1, m + 1), 3))
        for r in range(len(all_clauses) + 1):
            for subset in itertools.combinations(all_clauses, r):
                inst = {"num_vars": m, "clauses": [list(c) for c in subset]}
                check(inst, results)

    print(f"tests_run={results['run']} tests_passed={results['passed']}")
    return results


if __name__ == "__main__":
    r = main()
    assert r["run"] == r["passed"], "some tests failed"
