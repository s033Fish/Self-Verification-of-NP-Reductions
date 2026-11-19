"""Tests for reduce.py: compare brute-force answers on small instances."""

from __future__ import annotations

import itertools
import random

import problems
from problems import DominatingSet, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_dominating_set(instance: dict) -> bool:
    """Yes iff there is a dominating set of size <= k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True

    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Try all subsets of size at most k.
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(v in chosen or (adj[v] & chosen) for v in range(n)):
                return True
    return False


def solve_sat(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    if any(len(c) == 0 for c in clauses):
        return False

    for bits in itertools.product([False, True], repeat=num_vars):
        # bits[v-1] is the value of variable v.
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

def random_graph(n: int, p: float, rng: random.Random) -> list[list[int]]:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def check(instance: dict) -> None:
    """Validate, reduce, validate the result, and compare answers."""
    DominatingSet.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    expected = solve_dominating_set(instance)
    got = solve_sat(reduced)
    assert expected == got, (
        f"MISMATCH\ninstance={instance}\nreduced={reduced}\n"
        f"expected(DS)={expected} got(SAT)={got}"
    )


def main() -> int:
    tests_run = 0
    tests_passed = 0

    def run(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        check(instance)
        tests_passed += 1

    # --- Hand-picked edge cases -------------------------------------
    run({"n": 0, "edges": [], "k": 0})
    run({"n": 0, "edges": [], "k": 5})
    run({"n": 0, "edges": [], "k": -1})
    run({"n": 1, "edges": [], "k": 0})   # isolated vertex, need it
    run({"n": 1, "edges": [], "k": 1})
    run({"n": 1, "edges": [], "k": -3})
    run({"n": 3, "edges": [], "k": 2})   # 3 isolated vertices, need 3
    run({"n": 3, "edges": [], "k": 3})
    run({"n": 3, "edges": [[0, 1], [1, 2]], "k": 1})  # path, 1 dominates
    run({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 1})  # path 4
    run({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 2})
    run({"n": 4, "edges": [[0, 1], [0, 2], [0, 3]], "k": 1})  # star
    run({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2})
    run({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 1})
    run({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 0})
    run({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1})
    run({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2})
    run({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": -1})
    run({"n": 2, "edges": [[0, 1]], "k": 5})  # k >= n

    # --- Exhaustive small graphs ------------------------------------
    for n in range(0, 5):
        all_pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(all_pairs)):
            edges = [list(p) for i, p in enumerate(all_pairs) if mask >> i & 1]
            for k in range(-1, n + 2):
                run({"n": n, "edges": edges, "k": k})

    # --- Random graphs ----------------------------------------------
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(0, 5)
        p = rng.choice([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        edges = random_graph(n, p, rng)
        k = rng.randint(-2, n + 1)
        run({"n": n, "edges": edges, "k": k})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
