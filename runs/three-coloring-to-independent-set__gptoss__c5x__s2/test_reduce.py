"""Independent verification of reduce.py (3-Coloring -> Independent Set).

We implement our own brute-force solvers directly from the problem
definitions in problems.py, then compare the source answer with the
target answer on many small instances.
"""

from __future__ import annotations

import itertools
import random
from typing import Dict, Any, List

from problems import ThreeColoring, IndependentSet, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions.
# ----------------------------------------------------------------------

def three_coloring_solver(instance: Dict[str, Any]) -> bool:
    """True iff the graph is 3-colourable (brute force over 3^n colourings)."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colouring[u] == colouring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def _max_independent_set(n: int, adj: List[int]) -> int:
    """Maximum independent set size via branch and bound on bitmasks."""
    best = 0

    def rec(candidates: int, count: int) -> None:
        nonlocal best
        if count + bin(candidates).count("1") <= best:
            return
        if candidates == 0:
            if count > best:
                best = count
            return
        # lowest set bit
        v = (candidates & -candidates).bit_length() - 1
        # branch: include v
        rec(candidates & ~adj[v] & ~(1 << v), count + 1)
        # branch: exclude v
        rec(candidates & ~(1 << v), count)

    rec((1 << n) - 1, 0)
    return best


def independent_set_solver(instance: Dict[str, Any]) -> bool:
    """True iff there is an independent set of size at least k."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [0] * n
    for u, v in instance["edges"]:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return _max_independent_set(n, adj) >= k


# ----------------------------------------------------------------------
# Helpers to enumerate / generate source instances.
# ----------------------------------------------------------------------

def all_graphs(n: int):
    """All simple graphs on n labelled vertices (as edge lists)."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask & (1 << i)]
        yield {"n": n, "edges": edges}


def random_graph(n: int, p: float, rng: random.Random) -> Dict[str, Any]:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

tests_run = 0
tests_passed = 0


def check(source: Dict[str, Any]) -> None:
    global tests_run, tests_passed
    tests_run += 1
    # Source must be valid.
    ThreeColoring.validate(source)
    expected = three_coloring_solver(source)

    reduced = reduce(source)

    # The reduction must return a *valid* target instance.
    IndependentSet.validate(reduced)

    got = independent_set_solver(reduced)

    assert got == expected, (
        f"MISMATCH on {source}: source={expected}, reduced={got}, "
        f"reduced_instance={reduced}"
    )
    tests_passed += 1


def main() -> None:
    # 1. Exhaustive over all graphs with up to 5 vertices.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g)

    # 2. Random larger graphs.
    rng = random.Random(12345)
    for n in range(6, 9):
        for _ in range(300):
            p = rng.choice([0.0, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0])
            check(random_graph(n, p, rng))

    # 3. Explicit edge cases from the definitions.
    # n = 0 -> yes
    check({"n": 0, "edges": []})
    # at most 3 vertices -> always yes
    for n in range(0, 4):
        for g in all_graphs(n):
            assert three_coloring_solver(g) is True
            check(g)
    # K4 -> no
    k4 = {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
    check(k4)
    assert three_coloring_solver(k4) is False
    # K5 -> no
    k5_edges = [[u, v] for u in range(5) for v in range(u + 1, 5)]
    check({"n": 5, "edges": k5_edges})
    # triangle -> yes
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})
    # odd cycle C5 -> yes (3-colourable)
    c5 = {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]}
    check(c5)
    # even cycle C4 -> yes
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})

    # 4. Sanity checks of the solvers themselves on target edge cases.
    assert independent_set_solver({"n": 0, "edges": [], "k": 0}) is True
    assert independent_set_solver({"n": 0, "edges": [], "k": 1}) is False
    assert independent_set_solver({"n": 3, "edges": [], "k": 3}) is True
    assert independent_set_solver({"n": 3, "edges": [[0, 1], [1, 2]], "k": 3}) is False
    assert independent_set_solver({"n": 3, "edges": [[0, 1], [1, 2]], "k": 2}) is True
    assert independent_set_solver({"n": 3, "edges": [[0, 1], [1, 2]], "k": -5}) is True

    # 5. Structural properties of the reduction.
    for n in range(0, 7):
        for g in all_graphs(n):
            r = reduce(g)
            assert r["n"] == 3 * n, "reduction must create 3n vertices"
            assert r["k"] == n, "reduction must set k = n"
            # no duplicate edges and no self loops (validate already checks,
            # but assert explicitly for clarity)
            seen = set()
            for u, v in r["edges"]:
                assert u != v
                key = frozenset((u, v))
                assert key not in seen
                seen.add(key)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
