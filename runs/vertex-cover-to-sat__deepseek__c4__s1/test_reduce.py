"""Brute-force solvers for both problems plus randomized equivalence tests."""

from __future__ import annotations

import itertools
import json
import random

from problems import Sat, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the problem definitions.


def solve_vertex_cover(instance: dict) -> bool:
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    # Isolated vertices never help, so brute force over non-isolated ones only.
    verts = sorted({v for edge in edges for v in edge})
    if k >= len(verts):
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(verts, size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for (u, v) in edges):
                return True
    return False


def solve_sat(instance: dict) -> bool:
    """DPLL-style search; correct for the general CNF format."""
    m = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]

    def simplify(clauses, var, value):
        new = []
        for clause in clauses:
            if (var if value else -var) in clause:
                continue  # clause satisfied
            reduced = [lit for lit in clause if lit != (-var if value else var)]
            new.append(reduced)
        return new

    def dpll(clauses):
        while True:
            if not clauses:
                return True
            if any(len(c) == 0 for c in clauses):
                return False
            # unit propagation
            unit = None
            for clause in clauses:
                if len(clause) == 1:
                    unit = clause[0]
                    break
            if unit is None:
                break
            clauses = simplify(clauses, abs(unit), unit > 0)
        # pure literal elimination
        lits = {lit for clause in clauses for lit in clause}
        for lit in list(lits):
            if -lit not in lits:
                clauses = simplify(clauses, abs(lit), lit > 0)
        if not clauses:
            return True
        if any(len(c) == 0 for c in clauses):
            return False
        var = abs(clauses[0][0])
        return dpll(simplify(clauses, var, True)) or dpll(simplify(clauses, var, False))

    return dpll(clauses)


# ----------------------------------------------------------------------
# Tests


def check(instance: dict) -> None:
    VertexCover.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    expected = solve_vertex_cover(instance)
    got = solve_sat(reduced)
    assert expected == got, (instance, reduced, expected, got)


def random_instance(rng: random.Random) -> dict:
    n = rng.randint(0, 8)
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(all_edges)
    edges = [list(e) for e in all_edges[: rng.randint(0, len(all_edges))]]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    tests_run = 0
    tests_passed = 0

    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": -1},
        {"n": 3, "edges": [], "k": 5},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 0},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1},
        {"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)], "k": 4},
        {"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)], "k": 3},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 0},
        {"n": 6, "edges": [[u, v] for u in range(6) for v in range(u + 1, 6)], "k": 5},
        {"n": 6, "edges": [[u, v] for u in range(6) for v in range(u + 1, 6)], "k": 4},
    ]
    for inst in edge_cases:
        tests_run += 1
        check(inst)
        tests_passed += 1

    rng = random.Random(12345)
    for _ in range(4000):
        inst = random_instance(rng)
        tests_run += 1
        check(inst)
        tests_passed += 1

    # Exhaustive over all small graphs with n <= 4 and k in -1..n+1.
    for n in range(0, 5):
        all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(all_edges)):
            edges = [list(all_edges[i]) for i in range(len(all_edges)) if mask >> i & 1]
            for k in range(-1, n + 2):
                inst = {"n": n, "edges": edges, "k": k}
                tests_run += 1
                check(inst)
                tests_passed += 1


    # Large-n instances (few edges) must not blow up.
    big_cases = [
        {"n": 10**6, "edges": [[0, 1], [1, 2]], "k": 1},
        {"n": 10**9, "edges": [[0, 1], [1, 2]], "k": 2},
        {"n": 10**9, "edges": [[0, 1], [1, 2]], "k": 0},
        {"n": 10**6, "edges": [], "k": 0},
        {"n": 10**6, "edges": [], "k": -5},
        {"n": 10**6, "edges": [[5, 7]], "k": 1},
        {"n": 10**6, "edges": [[5, 7]], "k": 0},
    ]
    for inst in big_cases:
        tests_run += 1
        check(inst)
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    with open("verdict.json", "w") as fh:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, fh)


if __name__ == "__main__":
    main()
