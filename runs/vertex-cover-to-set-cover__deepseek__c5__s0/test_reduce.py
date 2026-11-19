"""Independent tests for reduce.py (Vertex Cover -> Set Cover).

We implement our own brute-force solvers straight from the problem
docstrings, generate many small source instances (including all the edge
cases), reduce them, and compare answers.
"""

from __future__ import annotations

import itertools
import random

from problems import VertexCover, SetCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written from the definitions.

def vertex_cover_solve(instance: dict) -> bool:
    """Yes iff some set of at most k vertices hits every edge."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if not edges:
        return True  # empty set covers, valid for any k >= 0
    if k >= n:
        return True  # all vertices cover everything

    vertices = range(n)
    for size in range(0, k + 1):
        for subset in itertools.combinations(vertices, size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def set_cover_solve(instance: dict) -> bool:
    """Yes iff at most k of the sets cover the whole universe."""
    u = instance["universe_size"]
    sets = instance["sets"]
    k = instance["k"]

    if k < 0:
        return False
    if u == 0:
        return True  # empty universe covered by no sets

    universe = set(range(u))
    # If some element is in no set, impossible.
    available = set()
    for s in sets:
        available.update(s)
    if not universe <= available:
        return False

    if k >= len(sets):
        return True  # all sets definitely cover (already checked coverage)

    for size in range(0, k + 1):
        for combo in itertools.combinations(range(len(sets)), size):
            covered = set()
            for idx in combo:
                covered.update(sets[idx])
            if covered >= universe:
                return True
    return False


# ----------------------------------------------------------------------
# Test harness.

tests_run = 0
tests_passed = 0
failures = []


def check(instance: dict, label: str = "") -> None:
    global tests_run, tests_passed
    tests_run += 1

    # Both instances must be valid according to the provided validators.
    try:
        VertexCover.validate(instance)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"[{label}] source invalid: {exc}")
        return

    try:
        reduced = reduce(instance)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"[{label}] reduce raised: {exc!r}")
        return

    try:
        SetCover.validate(reduced)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"[{label}] reduced instance invalid: {exc}")
        return

    src = vertex_cover_solve(instance)
    tgt = set_cover_solve(reduced)
    if src != tgt:
        failures.append(
            f"[{label}] MISMATCH source={src} target={tgt}\n"
            f"    source={instance}\n    reduced={reduced}"
        )
        return

    tests_passed += 1


def all_graphs(n, max_edges=None):
    """Yield all simple graphs on n vertices (all edge subsets)."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    if max_edges is not None:
        possible = possible[:max_edges]
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield edges


def main() -> None:
    # --- Exhaustive small graphs -------------------------------------
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k}, f"exhaustive n={n}")

    # --- Explicit edge cases -----------------------------------------
    check({"n": 0, "edges": [], "k": 0}, "empty n=0 k=0")
    check({"n": 0, "edges": [], "k": -1}, "empty n=0 k=-1")
    check({"n": 3, "edges": [], "k": 0}, "no edges k=0")
    check({"n": 3, "edges": [], "k": -5}, "no edges k<0")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1}, "triangle k=1")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2}, "triangle k=2")
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1}, "two disjoint edges k=1")
    check({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}, "two disjoint edges k=2")
    check({"n": 5, "edges": [[0, 1]], "k": 0}, "one edge k=0")
    check({"n": 5, "edges": [[0, 1]], "k": 1}, "one edge k=1")

    # --- Randomized small instances ----------------------------------
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(0, 6)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in possible if rng.random() < 0.5]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k}, "random")

    # --- Randomized with larger k range / denser graphs --------------
    for _ in range(2000):
        n = rng.randint(0, 7)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in possible if rng.random() < 0.8]
        k = rng.randint(-1, n)
        check({"n": n, "edges": edges, "k": k}, "random dense")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures[:20]:
            print(f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
