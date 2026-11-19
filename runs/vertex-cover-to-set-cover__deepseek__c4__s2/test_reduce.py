"""Brute-force solvers for Vertex Cover and Set Cover plus tests for reduce."""

from __future__ import annotations

import itertools
import random
import sys

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the problem definitions)

def solve_vertex_cover(instance: dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return True
    for size in range(0, k + 1):
        for combo in itertools.combinations(range(n), size):
            chosen = set(combo)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def solve_set_cover(instance: dict) -> bool:
    u = instance["universe_size"]
    sets = instance["sets"]
    k = instance["k"]
    if k < 0:
        return False
    if u == 0:
        return True
    if k > len(sets):
        k = len(sets)
    for size in range(0, k + 1):
        for combo in itertools.combinations(range(len(sets)), size):
            covered = set()
            for i in combo:
                covered.update(sets[i])
            if len(covered) == u:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators

def random_vertex_cover(rng: random.Random) -> dict:
    n = rng.randint(0, 7)
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(all_edges)
    m = rng.randint(0, len(all_edges))
    edges = [list(e) for e in all_edges[:m]]
    k = rng.randint(-2, n + 1)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0
    failures = []

    # Deterministic edge cases.
    fixed = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": -1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 2},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": -1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 1},
        {"n": 2, "edges": [[0, 1]], "k": 5},
    ]

    instances = fixed + [random_vertex_cover(rng) for _ in range(3000)]

    for inst in instances:
        SOURCE.validate(inst)
        red = reduce(inst)
        TARGET.validate(red)

        src_ans = solve_vertex_cover(inst)
        tgt_ans = solve_set_cover(red)

        tests_run += 1
        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            failures.append((inst, red, src_ans, tgt_ans))

    if failures:
        for inst, red, a, b in failures[:5]:
            print("FAIL", inst, "->", red, "source", a, "target", b)
        print(f"{len(failures)} failures")
        sys.exit(1)

    print(f"all {tests_run} tests passed")

    # Write verdict.json
    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)


if __name__ == "__main__":
    main()
