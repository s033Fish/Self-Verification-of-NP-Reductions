"""Brute-force solvers and randomized tests for the SAT -> IS reduction."""

from __future__ import annotations

import itertools
import json
import random

from problems import Sat, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def sat_solve(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        satisfied = True
        for clause in clauses:
            if not any(
                (bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause
            ):
                satisfied = False
                break
        if satisfied:
            return True
    return False


def is_solve(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(k, n + 1):
        for combo in itertools.combinations(range(n), size):
            if all(b not in adj[a] for a, b in itertools.combinations(combo, 2)):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators.

def random_sat(rng: random.Random) -> dict:
    m = rng.randint(0, 4)
    n_clauses = rng.randint(0, 5)
    clauses = []
    for _ in range(n_clauses):
        length = rng.randint(0, 4)
        clause = []
        for _ in range(length):
            if m == 0:
                break
            var = rng.randint(1, m)
            clause.append(var if rng.random() < 0.5 else -var)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def structured_sat() -> list[dict]:
    return [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 0, "clauses": [[]]},
        {"num_vars": 1, "clauses": [[1]]},
        {"num_vars": 1, "clauses": [[-1]]},
        {"num_vars": 1, "clauses": [[1], [-1]]},
        {"num_vars": 1, "clauses": [[1, -1]]},
        {"num_vars": 2, "clauses": [[1, 2], [-1], [-2]]},
        {"num_vars": 2, "clauses": [[1], [1], [1]]},
        {"num_vars": 2, "clauses": [[1, 1], [-1, -1]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2], [-3]]},
        {"num_vars": 3, "clauses": [[], [1]]},
        {"num_vars": 4, "clauses": [[1, -2], [2, -3], [3, -4], [4, -1]]},
    ]


def main() -> None:
    tests_run = 0
    tests_passed = 0

    instances = structured_sat()
    rng = random.Random(12345)
    for _ in range(3000):
        instances.append(random_sat(rng))

    for inst in instances:
        Sat.validate(inst)
        target = reduce(inst)
        IndependentSet.validate(target)
        expected = sat_solve(inst)
        got = is_solve(target)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "->", target, "sat=", expected, "is=", got)

    # Sanity: the solvers themselves agree with known cases.
    assert sat_solve({"num_vars": 0, "clauses": []}) is True
    assert sat_solve({"num_vars": 0, "clauses": [[]]}) is False
    assert is_solve({"n": 0, "edges": [], "k": 0}) is True
    assert is_solve({"n": 3, "edges": [], "k": 3}) is True
    assert is_solve({"n": 3, "edges": [[0, 1], [1, 2]], "k": 3}) is False

    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print(json.dumps(verdict))
    if tests_run != tests_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
