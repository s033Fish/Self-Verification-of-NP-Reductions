"""Brute-force solvers and tests comparing 3-SAT answers with reductions."""

from __future__ import annotations

import itertools
import random

from problems import ThreeSat, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the problem definitions.

def solve_three_sat(instance: dict) -> bool:
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
    return False


def _min_vertex_cover(edges: tuple, cache: dict) -> int:
    """Exact minimum vertex cover size via branching (small graphs)."""
    if not edges:
        return 0
    if edges in cache:
        return cache[edges]
    u, v = tuple(edges[0])
    rest_u = tuple(e for e in edges if u not in e)
    rest_v = tuple(e for e in edges if v not in e)
    result = 1 + min(_min_vertex_cover(rest_u, cache), _min_vertex_cover(rest_v, cache))
    cache[edges] = result
    return result


def solve_vertex_cover(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    edge_set = tuple(sorted(frozenset(e) for e in edges))
    return _min_vertex_cover(edge_set, {}) <= k


# ----------------------------------------------------------------------
# Instance generators.

def random_three_sat(rng: random.Random, max_vars: int = 5, max_clauses: int = 5) -> dict:
    m = rng.randint(0, max_vars)
    clauses = []
    for _ in range(rng.randint(0, max_clauses)):
        if m < 3:
            break
        vars_chosen = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vars_chosen]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_small_three_sat():
    """Exhaustively enumerate small formulas."""
    instances = []
    for m in range(0, 3):
        instances.append({"num_vars": m, "clauses": []})
    m = 3
    sign_patterns = list(itertools.product([1, -1], repeat=3))
    single_clauses = []
    for perm in itertools.permutations([1, 2, 3]):
        for signs in sign_patterns:
            single_clauses.append([perm[i] * signs[i] for i in range(3)])
    for c in single_clauses:
        instances.append({"num_vars": m, "clauses": [c]})
    seen = set()
    for c1 in single_clauses:
        for c2 in single_clauses:
            key = frozenset(
                tuple(sorted((abs(l), l > 0) for l in c)) for c in (c1, c2)
            )
            if key in seen:
                continue
            seen.add(key)
            instances.append({"num_vars": m, "clauses": [c1, c2]})
    return instances


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def check(inst: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeSat.validate(inst)
        target = reduce(inst)
        VertexCover.validate(target)
        src = solve_three_sat(inst)
        tgt = solve_vertex_cover(target)
        if src == tgt:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "->", target, "src", src, "tgt", tgt)

    for inst in all_small_three_sat():
        check(inst)

    rng = random.Random(12345)
    for _ in range(600):
        check(random_three_sat(rng))

    # Larger random instances.
    rng2 = random.Random(999)
    for _ in range(200):
        m = rng2.randint(3, 7)
        nc = rng2.randint(1, 6)
        clauses = []
        for _ in range(nc):
            vs = rng2.sample(range(1, m + 1), 3)
            clauses.append([v if rng2.random() < 0.5 else -v for v in vs])
        check({"num_vars": m, "clauses": clauses})

    # Edge cases.
    check({"num_vars": 0, "clauses": []})
    check({"num_vars": 5, "clauses": []})
    check({"num_vars": 3, "clauses": [[1, 2, 3]]})
    check({"num_vars": 3, "clauses": [[-1, -2, -3]]})
    check({"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]})
    check({"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 4]]})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
