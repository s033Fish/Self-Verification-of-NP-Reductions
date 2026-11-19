"""Tests for reduce.py: compare brute-force answers on small instances."""

from __future__ import annotations

import itertools
import json
import random

from problems import Sat, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the problem definitions.

def solve_vertex_cover(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def _dpll(clauses: list[frozenset]) -> bool:
    # Unit propagation.
    while True:
        for c in clauses:
            if len(c) == 0:
                return False
        unit = None
        for c in clauses:
            if len(c) == 1:
                unit = next(iter(c))
                break
        if unit is None:
            break
        new_clauses = []
        for c in clauses:
            if unit in c:
                continue
            if -unit in c:
                reduced = c - {-unit}
                if len(reduced) == 0:
                    return False
                new_clauses.append(reduced)
            else:
                new_clauses.append(c)
        clauses = new_clauses
        if not clauses:
            return True

    if not clauses:
        return True

    # Branch on a literal.
    lit = next(iter(clauses[0]))
    for choice in (lit, -lit):
        new_clauses = []
        ok = True
        for c in clauses:
            if choice in c:
                continue
            if -choice in c:
                reduced = c - {-choice}
                if len(reduced) == 0:
                    ok = False
                    break
                new_clauses.append(reduced)
            else:
                new_clauses.append(c)
        if ok and _dpll(new_clauses):
            return True
    return False


def solve_sat(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = []
    for clause in instance["clauses"]:
        s = set(clause)
        # A clause containing both v and -v is a tautology.
        if any(-lit in s for lit in s):
            continue
        clauses.append(frozenset(s))
    # Empty clause (or formula reduced to one) -> unsat.
    if any(len(c) == 0 for c in clauses):
        return False
    return _dpll(clauses)


# ----------------------------------------------------------------------
# Helpers

def random_vc_instance(rng: random.Random) -> dict:
    n = rng.randint(0, 6)
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(all_edges)
    m = rng.randint(0, len(all_edges))
    edges = [[u, v] for u, v in all_edges[:m]]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def check(instance: dict, tests: list) -> None:
    VertexCover.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    expected = solve_vertex_cover(instance)
    got = solve_sat(out)
    tests.append((instance, expected, got))
    assert expected == got, (
        f"mismatch: expected {expected} got {got}\ninstance={instance}\n"
        f"reduced={out}"
    )


def main() -> None:
    tests: list = []

    # ---- Explicit edge cases -------------------------------------
    explicit = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": -1},
        {"n": 3, "edges": [[0, 1]], "k": -1},
        {"n": 3, "edges": [[0, 1]], "k": -5},
        {"n": 2, "edges": [[0, 1]], "k": 2},
        {"n": 2, "edges": [[0, 1]], "k": 10},
        {"n": 2, "edges": [[0, 1]], "k": 0},
        {"n": 2, "edges": [[0, 1]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3]], "k": 0},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 2},
        {"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 2},
        {"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 3},
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]], "k": 3},
    ]
    for inst in explicit:
        check(inst, tests)

    # ---- Random tests --------------------------------------------
    rng = random.Random(12345)
    for _ in range(3000):
        check(random_vc_instance(rng), tests)

    # ---- Exhaustive small graphs ---------------------------------
    n = 4
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(all_edges)):
        edges = [list(e) for i, e in enumerate(all_edges) if mask & (1 << i)]
        for k in range(-1, n + 2):
            check({"n": n, "edges": edges, "k": k}, tests)

    passed = len(tests)
    print(f"tests_run={len(tests)} tests_passed={passed}")
    assert passed == len(tests)

    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": len(tests), "tests_passed": passed}, f)
    print("verdict.json written")


if __name__ == "__main__":
    main()
