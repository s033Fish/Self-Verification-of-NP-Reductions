"""Tests comparing brute-force answers on small 3-Coloring instances and their
3-SAT reductions."""

from __future__ import annotations

import itertools
import json
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.


def solve_3col(instance: dict) -> bool:
    """Backtracking 3-colourability solver."""
    n = instance["n"]
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    colours = [-1] * n

    def rec(v: int) -> bool:
        if v == n:
            return True
        for c in range(3):
            if all(colours[u] != c for u in adj[v]):
                colours[v] = c
                if rec(v + 1):
                    return True
                colours[v] = -1
        return False

    return rec(0)


def solve_3sat(instance: dict) -> bool:
    """Backtracking 3-SAT solver with unit propagation."""
    clauses = [list(c) for c in instance["clauses"]]

    def rec(clauses: list[list[int]]) -> bool:
        # Unit propagation.
        while True:
            unit = None
            for c in clauses:
                if len(c) == 0:
                    return False
                if len(c) == 1:
                    unit = c[0]
                    break
            if unit is None:
                break
            new = []
            for c in clauses:
                if unit in c:
                    continue
                new.append([l for l in c if l != -unit])
            clauses = new
        if not clauses:
            return True
        lit = clauses[0][0]
        for val in (lit, -lit):
            new = []
            for c in clauses:
                if val in c:
                    continue
                new.append([l for l in c if l != -val])
            if rec(new):
                return True
        return False

    return rec(clauses)


# ----------------------------------------------------------------------
# Instance generation.

def all_graphs(n: int):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main() -> None:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    instances = []
    # Exhaustive over all graphs with n = 0..5.
    for n in range(6):
        instances.extend(all_graphs(n))
    # Random graphs for slightly larger n.
    for n in range(6, 11):
        for _ in range(300):
            instances.append(random_graph(n, rng.choice([0.1, 0.3, 0.5, 0.8]), rng))

    for inst in instances:
        SOURCE.validate(inst)
        reduced = reduce(inst)
        TARGET.validate(reduced)

        expected = solve_3col(inst)
        got = solve_3sat(reduced)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "->", reduced, expected, got)

    # Explicit edge-case checks.
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]},  # K4
    ]
    for inst in edge_cases:
        SOURCE.validate(inst)
        reduced = reduce(inst)
        TARGET.validate(reduced)
        expected = solve_3col(inst)
        got = solve_3sat(reduced)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("EDGE MISMATCH", inst, expected, got)

    # Sanity: K4 must be a no-instance.
    k4 = {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
    assert solve_3col(k4) is False
    assert solve_3sat(reduce(k4)) is False

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    verdict = {
        "verified": tests_run == tests_passed and tests_run > 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
