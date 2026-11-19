"""Tests for the Vertex Cover -> SAT reduction in reduce.py.

Contains independent brute-force solvers for both problems (written from the
problem definitions) and compares their answers on many small instances.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import Sat, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (independent of the reduction)

def solve_vertex_cover(instance: dict) -> bool:
    """Yes iff there is a vertex cover of size at most k."""
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


def solve_sat(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if any(len(c) == 0 for c in clauses):
        return False
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0) == bits[abs(lit) - 1] for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Helpers

def check(instance: dict) -> bool:
    """Validate, reduce, validate target, compare answers."""
    VertexCover.validate(instance)
    target = reduce(instance)
    Sat.validate(target)
    src = solve_vertex_cover(instance)
    tgt = solve_sat(target)
    assert src == tgt, (
        f"MISMATCH src={src} tgt={tgt}\ninstance={instance}\ntarget={target}"
    )
    return src


def random_graph(rng: random.Random, n: int, edge_prob: float):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < edge_prob:
                edges.append([u, v])
    return edges


def main() -> None:
    tests_run = 0
    tests_passed = 0

    def run(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    # ---- Explicit edge cases -------------------------------------
    run({"n": 0, "edges": [], "k": -1})
    run({"n": 3, "edges": [[0, 1]], "k": -5})
    for k in range(0, 6):
        run({"n": 4, "edges": [], "k": k})
    run({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3})
    run({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 100})
    run({"n": 2, "edges": [[0, 1]], "k": 0})
    run({"n": 2, "edges": [[0, 1]], "k": 1})
    run({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1})
    run({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2})
    run({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 0})
    run({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 1})
    run({"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 2})
    run({"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 3})
    run({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 2})
    run({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "k": 1})
    run({"n": 0, "edges": [], "k": 0})
    run({"n": 0, "edges": [], "k": -1})

    # ---- Exhaustive small graphs ---------------------------------
    # Keep the reduced formula small enough for brute force SAT
    # (num_vars = n + n*k must stay modest).
    rng = random.Random(12345)
    for n in range(0, 5):
        all_pairs = list(itertools.combinations(range(n), 2))
        if n <= 3:
            masks = range(1 << len(all_pairs))
        else:
            masks = [rng.randrange(1 << len(all_pairs)) for _ in range(60)]
        for mask in masks:
            edges = [list(all_pairs[i]) for i in range(len(all_pairs)) if mask >> i & 1]
            for k in range(-1, n + 1):
                if n + n * max(k, 0) <= 12:
                    run({"n": n, "edges": edges, "k": k})

    # ---- Random small instances ----------------------------------
    for _ in range(300):
        n = rng.randint(0, 7)
        edges = random_graph(rng, n, rng.choice([0.1, 0.3, 0.5, 0.7, 1.0]))
        k = rng.randint(-2, n + 2)
        if n + n * max(k, 0) <= 12:
            run({"n": n, "edges": edges, "k": k})

    # ---- Direct sanity checks of the target format ----------------
    t = reduce({"n": 3, "edges": [[0, 1], [1, 2]], "k": 1})
    assert t["num_vars"] >= 3
    assert all(isinstance(c, list) for c in t["clauses"])
    assert reduce({"n": 2, "edges": [[0, 1]], "k": -1})["clauses"] == [[]]
    assert reduce({"n": 2, "edges": [[0, 1]], "k": 5})["clauses"] == []

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)
    print("verdict.json written")


if __name__ == "__main__":
    main()
