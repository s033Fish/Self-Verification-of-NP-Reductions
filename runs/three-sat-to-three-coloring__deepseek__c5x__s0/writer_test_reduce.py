"""Brute-force solvers and tests for the 3-SAT -> 3-Coloring reduction."""

from __future__ import annotations

import itertools
import json
import random

import problems
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)

def brute_sat(instance: dict) -> bool:
    """Decide 3-SAT by trying every assignment of variables 1..m."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        # bits[v-1] is the value of variable v
        if all(
            any((bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1])
                for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def brute_color(instance: dict) -> bool:
    """Decide 3-colourability by backtracking."""
    n = instance["n"]
    edges = instance["edges"]
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    color = [-1] * n

    def backtrack(i: int) -> bool:
        if i == n:
            return True
        for c in range(3):
            ok = True
            for j in adj[i]:
                if color[j] == c:
                    ok = False
                    break
            if ok:
                color[i] = c
                if backtrack(i + 1):
                    return True
                color[i] = -1
        return False

    return backtrack(0)


# ----------------------------------------------------------------------
# Instance generators

def random_sat(rng: random.Random) -> dict:
    m = rng.randint(0, 4)
    nclauses = rng.randint(0, 5)
    clauses = []
    for _ in range(nclauses):
        if m < 3:
            break
        variables = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in variables]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def edge_key(u: int, v: int):
    return (u, v) if u < v else (v, u)


def check_valid_reduction(inst: dict) -> None:
    problems.ThreeSat.validate(inst)
    out = reduce(inst)
    problems.ThreeColoring.validate(out)
    # no duplicate undirected edges
    seen = set()
    for u, v in out["edges"]:
        key = edge_key(u, v)
        assert key not in seen, f"duplicate edge {key}"
        seen.add(key)


# ----------------------------------------------------------------------
# Tests

def run() -> None:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    def record(ok: bool, label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        if ok:
            tests_passed += 1
        else:
            print(f"FAIL: {label}")

    # Fixed edge cases.
    fixed = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 2, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 5, "clauses": []},
        # all 8 clauses over 3 variables -> unsatisfiable
        {"num_vars": 3, "clauses": [
            [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
            [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3],
        ]},
        # trivially satisfiable
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        # duplicate clause
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        # variable not appearing
        {"num_vars": 4, "clauses": [[1, 2, 3]]},
    ]

    for inst in fixed:
        check_valid_reduction(inst)
        expected = brute_sat(inst)
        got = brute_color(reduce(inst))
        record(expected == got, f"fixed {inst} expected {expected} got {got}")

    # Random tests.
    for _ in range(300):
        inst = random_sat(rng)
        check_valid_reduction(inst)
        expected = brute_sat(inst)
        got = brute_color(reduce(inst))
        record(expected == got, f"random {inst} expected {expected} got {got}")

    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    print("verdict:", verdict)


if __name__ == "__main__":
    run()
