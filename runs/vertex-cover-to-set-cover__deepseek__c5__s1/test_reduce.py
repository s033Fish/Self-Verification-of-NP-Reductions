"""Independent tests for reduce.py: Vertex Cover -> Set Cover.

We implement brute-force solvers for both problems directly from the
definitions in problems.py, then compare:
    solve_vertex_cover(instance)  ==  solve_set_cover(reduce(instance))
on many small source instances (exhaustive small graphs + random graphs).
"""

from __future__ import annotations

import itertools
import random

from problems import VertexCover, SetCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the docstrings)

def solve_vertex_cover(instance: dict) -> bool:
    """Yes iff there is a vertex cover of size AT MOST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if not edges:
        return True  # empty set covers, for any k >= 0
    if k >= n:
        return True  # all vertices cover every edge

    vertices = range(n)
    for size in range(0, k + 1):
        for subset in itertools.combinations(vertices, size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def solve_set_cover(instance: dict) -> bool:
    """Yes iff AT MOST k of the sets cover the whole universe."""
    u = instance["universe_size"]
    sets = instance["sets"]
    k = instance["k"]

    if k < 0:
        return False
    if u == 0:
        return True  # empty universe covered by no sets, for any k >= 0

    # If some element is in no set, impossible.
    present = set()
    for s in sets:
        present.update(s)
    if present != set(range(u)):
        return False

    m = len(sets)
    if k >= m:
        # All sets together cover the universe (checked above).
        return True

    for size in range(0, k + 1):
        for combo in itertools.combinations(range(m), size):
            covered = set()
            for i in combo:
                covered.update(sets[i])
            if len(covered) == u:
                return True
    return False


# ----------------------------------------------------------------------
# Test harness

class Counter:
    def __init__(self):
        self.run = 0
        self.passed = 0

    def check(self, source_instance):
        VertexCover.validate(source_instance)
        target_instance = reduce(source_instance)
        SetCover.validate(target_instance)
        expected = solve_vertex_cover(source_instance)
        got = solve_set_cover(target_instance)
        self.run += 1
        if expected == got:
            self.passed += 1
        else:
            print("MISMATCH")
            print("  source:", source_instance)
            print("  target:", target_instance)
            print("  expected (VC):", expected, " got (SC):", got)
        return expected == got


def all_graphs(n):
    """Yield every simple undirected graph on n vertices as an edge list."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for r in range(len(possible) + 1):
        for combo in itertools.combinations(possible, r):
            yield [list(e) for e in combo]


def main():
    counter = Counter()
    random.seed(12345)

    # 1. Exhaustive: all graphs on n = 0..4 vertices, k = -1..n+1.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-1, n + 2):
                counter.check({"n": n, "edges": edges, "k": k})

    # 2. Random small graphs with n up to 7, random k including negatives.
    for _ in range(3000):
        n = random.randint(0, 7)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        random.shuffle(possible)
        m = random.randint(0, len(possible))
        edges = [list(e) for e in possible[:m]]
        k = random.randint(-2, n + 2)
        counter.check({"n": n, "edges": edges, "k": k})

    # 3. A few hand-picked edge cases.
    edge_cases = [
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 5},
        {"n": 3, "edges": [], "k": -1},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [[0, 1]], "k": 0},
        {"n": 3, "edges": [[0, 1]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 2, "edges": [[0, 1]], "k": 100},
    ]
    for inst in edge_cases:
        counter.check(inst)

    # 4. Sanity-check the solvers themselves on known answers.
    assert solve_vertex_cover({"n": 3, "edges": [[0, 1], [1, 2]], "k": 1}) is True
    assert solve_vertex_cover({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1}) is False
    assert solve_set_cover({"universe_size": 0, "sets": [], "k": 0}) is True
    assert solve_set_cover({"universe_size": 2, "sets": [[0], [1]], "k": 1}) is False
    assert solve_set_cover({"universe_size": 2, "sets": [[0], [1]], "k": 2}) is True
    assert solve_set_cover({"universe_size": 2, "sets": [[0]], "k": 5}) is False

    print(f"tests_run={counter.run} tests_passed={counter.passed}")
    assert counter.run == counter.passed, "some tests failed"
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
