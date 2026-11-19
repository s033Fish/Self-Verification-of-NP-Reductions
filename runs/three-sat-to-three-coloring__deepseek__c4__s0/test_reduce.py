"""Brute-force solvers and tests comparing 3-SAT answers with reductions."""

from __future__ import annotations

import itertools
import json
import random

from problems import ThreeSat, ThreeColoring
from reduce import reduce


def solve_three_sat(instance) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        if all(
            any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1]) for l in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_three_coloring(instance) -> bool:
    """Backtracking 3-colouring."""
    n = instance["n"]
    adj = [[] for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    colours = [-1] * n

    def bt(node: int) -> bool:
        if node == n:
            return True
        used = {colours[w] for w in adj[node] if colours[w] != -1}
        for c in range(3):
            if c not in used:
                colours[node] = c
                if bt(node + 1):
                    return True
                colours[node] = -1
        return False

    return bt(0)


def random_instance(rng, max_vars=4, max_clauses=5):
    m = rng.randint(0, max_vars)
    if m < 3:
        return {"num_vars": m, "clauses": []}
    k = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(k):
        vs = rng.sample(range(1, m + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return {"num_vars": m, "clauses": clauses}


def main() -> None:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 2, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3],
                                    [-1, -2, 3], [-1, 2, -3], [1, -2, -3], [-1, -2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4],
                                    [-1, -2, -3], [-1, -2, -4], [-1, -3, -4], [-2, -3, -4]]},
    ]
    for _ in range(600):
        cases.append(random_instance(rng))

    for inst in cases:
        ThreeSat.validate(inst)
        target = reduce(inst)
        ThreeColoring.validate(target)
        expected = solve_three_sat(inst)
        got = solve_three_coloring(target)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "expected", expected, "got", got, target)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    verified = tests_run == tests_passed
    with open("verdict.json", "w") as fh:
        json.dump({"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}, fh)
    print("verdict.json written:", verified)


if __name__ == "__main__":
    main()
