"""Independent tests for reduce.py: Clique -> Vertex Cover.

We implement brute-force solvers for both problems straight from the
docstrings in problems.py, then check that for many small source instances
the source answer equals the answer of the reduced target instance.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the definitions, no solver in problems.py)

def clique_answer(instance) -> bool:
    """Yes iff graph has a clique of AT LEAST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from the docstring.
    if k <= 0:
        return True
    if k > n:
        return False

    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True

    # Try every subset of size >= k (only sizes k..n matter).
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if not adj[a][b]:
                    ok = False
                    break
            if ok:
                return True
    return False


def vertex_cover_answer(instance) -> bool:
    """Yes iff graph has a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases from the docstring.
    if k < 0:
        return False
    if k >= n:
        return True

    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            covered = set(subset)
            if all(u in covered or v in covered for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Helpers

def all_graphs(n):
    """Yield every simple undirected graph on n vertices as edge lists."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield edges


def random_graph(n, rng):
    pairs = list(itertools.combinations(range(n), 2))
    edges = [list(p) for p in pairs if rng.random() < 0.5]
    return edges


# ----------------------------------------------------------------------
# Tests

def test_exhaustive_small():
    """Exhaustively test all graphs for n = 0..4 and a range of k values."""
    tests = 0
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                inst = {"n": n, "edges": [list(e) for e in edges], "k": k}
                Clique.validate(inst)
                expected = clique_answer(inst)
                reduced = reduce(inst)
                VertexCover.validate(reduced)
                got = vertex_cover_answer(reduced)
                assert got == expected, (
                    f"mismatch n={n} edges={edges} k={k}: "
                    f"clique={expected} reduced={reduced} vc={got}"
                )
                tests += 1
    return tests


def test_random_small():
    """Random graphs, n up to 7, random k including out-of-range values."""
    rng = random.Random(12345)
    tests = 0
    for _ in range(3000):
        n = rng.randint(0, 7)
        edges = random_graph(n, rng)
        k = rng.randint(-3, n + 3)
        inst = {"n": n, "edges": edges, "k": k}
        Clique.validate(inst)
        expected = clique_answer(inst)
        reduced = reduce(inst)
        VertexCover.validate(reduced)
        got = vertex_cover_answer(reduced)
        assert got == expected, (
            f"mismatch n={n} edges={edges} k={k}: "
            f"clique={expected} reduced={reduced} vc={got}"
        )
        tests += 1
    return tests


def test_reduced_structure():
    """The reduced instance must be the complement graph with k' = n - k."""
    rng = random.Random(999)
    tests = 0
    for _ in range(500):
        n = rng.randint(0, 8)
        edges = random_graph(n, rng)
        k = rng.randint(-3, n + 3)
        inst = {"n": n, "edges": edges, "k": k}
        reduced = reduce(inst)
        assert set(reduced.keys()) == {"n", "edges", "k"}
        assert reduced["n"] == n
        assert reduced["k"] == n - k
        present = {frozenset(e) for e in edges}
        comp = {frozenset(e) for e in reduced["edges"]}
        expected_comp = {
            frozenset((u, v))
            for u in range(n)
            for v in range(u + 1, n)
            if frozenset((u, v)) not in present
        }
        assert comp == expected_comp, f"bad complement for {inst}"
        # No self loops / duplicates / reversed duplicates.
        assert all(len(e) == 2 and e[0] != e[1] for e in reduced["edges"])
        assert len(comp) == len(reduced["edges"])
        tests += 1
    return tests


def test_edge_cases():
    """Explicitly exercise the documented edge cases."""
    cases = [
        ({"n": 0, "edges": [], "k": 0}, True),
        ({"n": 0, "edges": [], "k": 1}, False),
        ({"n": 0, "edges": [], "k": -5}, True),
        ({"n": 1, "edges": [], "k": 1}, True),
        ({"n": 1, "edges": [], "k": 2}, False),
        ({"n": 3, "edges": [], "k": 2}, False),
        ({"n": 3, "edges": [], "k": 1}, True),
        ({"n": 3, "edges": [], "k": 0}, True),
        ({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3}, True),
        ({"n": 3, "edges": [[0, 1], [1, 2]], "k": 3}, False),
        ({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}, True),
        ({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]], "k": 4}, True),
    ]
    tests = 0
    for inst, expected in cases:
        Clique.validate(inst)
        assert clique_answer(inst) == expected, f"solver disagrees on {inst}"
        reduced = reduce(inst)
        VertexCover.validate(reduced)
        assert vertex_cover_answer(reduced) == expected, (
            f"reduction wrong on {inst} -> {reduced}"
        )
        tests += 1
    return tests


def main():
    total = 0
    passed = 0
    for name, fn in [
        ("test_edge_cases", test_edge_cases),
        ("test_exhaustive_small", test_exhaustive_small),
        ("test_random_small", test_random_small),
        ("test_reduced_structure", test_reduced_structure),
        ("test_rejects_invalid_input", test_rejects_invalid_input),
        ("test_no_input_mutation", test_no_input_mutation),
        ("test_larger_random", test_larger_random),
    ]:
        count = fn()
        total += count
        passed += count
        print(f"{name}: {count} checks passed")
    print(f"TOTAL: {passed}/{total} checks passed")
    return passed, total




# ----------------------------------------------------------------------
# Extra robustness tests appended

def test_rejects_invalid_input():
    """reduce should raise InvalidInstance on malformed source instances."""
    from problems import InvalidInstance
    bad = [
        {"n": 3, "edges": [[0, 1]], "k": 1, "extra": 1},
        {"n": 3, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 0]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 0]], "k": 1},
        {"n": 3, "edges": [[0, 3]], "k": 1},
        {"n": -1, "edges": [], "k": 0},
        {"n": 3, "edges": [[0, 1]], "k": 1.5},
    ]
    tests = 0
    for inst in bad:
        try:
            reduce(inst)
        except InvalidInstance:
            pass
        else:
            raise AssertionError(f"reduce accepted invalid instance {inst}")
        tests += 1
    return tests


def test_no_input_mutation():
    """reduce must not mutate the source instance."""
    import copy
    rng = random.Random(7)
    tests = 0
    for _ in range(300):
        n = rng.randint(0, 7)
        edges = random_graph(n, rng)
        k = rng.randint(-2, n + 2)
        inst = {"n": n, "edges": edges, "k": k}
        snapshot = copy.deepcopy(inst)
        reduce(inst)
        assert inst == snapshot, f"input mutated: {snapshot} -> {inst}"
        tests += 1
    return tests


def test_larger_random():
    """Random n up to 9, brute force still feasible for these sizes."""
    rng = random.Random(2024)
    tests = 0
    for _ in range(400):
        n = rng.randint(0, 9)
        edges = random_graph(n, rng)
        k = rng.randint(-2, n + 2)
        inst = {"n": n, "edges": edges, "k": k}
        Clique.validate(inst)
        expected = clique_answer(inst)
        reduced = reduce(inst)
        VertexCover.validate(reduced)
        got = vertex_cover_answer(reduced)
        assert got == expected, f"mismatch n={n} k={k} edges={edges}"
        tests += 1
    return tests


def _extra_main():
    total = 0
    for name, fn in [
        ("test_rejects_invalid_input", test_rejects_invalid_input),
        ("test_no_input_mutation", test_no_input_mutation),
        ("test_larger_random", test_larger_random),
    ]:
        count = fn()
        total += count
        print(f"{name}: {count} checks passed")
    return total


if __name__ == "__main__":
    main()
