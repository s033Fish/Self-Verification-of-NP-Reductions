"""Tests for reduce.py: brute-force solvers + comparison on many small instances."""

from __future__ import annotations

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_three_coloring(instance: dict) -> bool:
    """True iff the graph is 3-colourable."""
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    for coloring in itertools.product(range(3), repeat=n):
        if all(coloring[u] != coloring[v] for u, v in edges):
            return True
    return False


def solve_independent_set(instance: dict) -> bool:
    """True iff the graph has an independent set of size >= k.

    Only subsets of size exactly k need checking: any superset of an
    independent set is not necessarily independent, but any subset of an
    independent set of size >= k contains an independent subset of size k.
    """
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    edges = [(u, v) for u, v in instance["edges"]]
    for subset in itertools.combinations(range(n), k):
        chosen = set(subset)
        if all(u not in chosen or v not in chosen for u, v in edges):
            return True
    return False


# ----------------------------------------------------------------------
# Instance helpers.

def random_graph(n: int, p: float, rng: random.Random) -> dict:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def all_graphs(n: int):
    """All labelled simple graphs on n vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests.

def test_validate_outputs():
    """The reduction output must be a valid Independent Set instance."""
    from problems import IndependentSet
    rng = random.Random(0)
    count = 0
    for _ in range(200):
        n = rng.randint(0, 6)
        src = random_graph(n, rng.random(), rng)
        out = reduce(src)
        IndependentSet.validate(out)
        count += 1
    return count


def test_exhaustive_small():
    """Exhaustively check all graphs up to 5 vertices."""
    checked = 0
    for n in range(0, 6):
        for src in all_graphs(n):
            out = reduce(src)
            assert solve_three_coloring(src) == solve_independent_set(out), (
                f"mismatch on {src} -> {out}"
            )
            checked += 1
    return checked


def test_random():
    """Random comparison on slightly larger graphs."""
    rng = random.Random(12345)
    checked = 0
    for _ in range(300):
        n = rng.randint(0, 7)
        p = rng.choice([0.0, 0.1, 0.3, 0.5, 0.8, 1.0])
        src = random_graph(n, p, rng)
        out = reduce(src)
        assert solve_three_coloring(src) == solve_independent_set(out), (
            f"mismatch on {src} -> {out}"
        )
        checked += 1
    return checked


def test_edge_cases():
    count = 0
    # n = 0 is yes.
    assert solve_three_coloring({"n": 0, "edges": []}) is True
    assert solve_independent_set(reduce({"n": 0, "edges": []})) is True

    # Any graph with at most 3 vertices is yes.
    for n in range(0, 4):
        for src in all_graphs(n):
            assert solve_three_coloring(src) is True
            assert solve_independent_set(reduce(src)) is True
            count += 1

    # K4 is no.
    k4 = {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
    assert solve_three_coloring(k4) is False
    assert solve_independent_set(reduce(k4)) is False
    count += 1

    # K3 is yes.
    k3 = {"n": 3, "edges": [[0, 1], [0, 2], [1, 2]]}
    assert solve_three_coloring(k3) is True
    assert solve_independent_set(reduce(k3)) is True
    count += 1
    return count


def test_known_small():
    count = 0
    # C5 is 3-colourable (chromatic number 3).
    c5 = {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]}
    assert solve_three_coloring(c5) is True
    assert solve_independent_set(reduce(c5)) is True
    count += 1

    # K5 is not 3-colourable.
    k5 = {"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)]}
    assert solve_three_coloring(k5) is False
    assert solve_independent_set(reduce(k5)) is False
    count += 1

    # Petersen graph has chromatic number 3, so it IS 3-colourable.
    petersen = {
        "n": 10,
        "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0],
                  [5, 7], [7, 9], [9, 6], [6, 8], [8, 5],
                  [0, 5], [1, 6], [2, 7], [3, 8], [4, 9]],
    }
    assert solve_three_coloring(petersen) is True
    assert solve_independent_set(reduce(petersen)) is True
    count += 1
    return count


def main():
    tests = [
        ("test_validate_outputs", test_validate_outputs),
        ("test_exhaustive_small", test_exhaustive_small),
        ("test_random", test_random),
        ("test_edge_cases", test_edge_cases),
        ("test_known_small", test_known_small),
    ]
    passed = 0
    total_checks = 0
    for name, fn in tests:
        try:
            checks = fn()
        except AssertionError as exc:
            print(f"FAIL {name}: {exc}")
        else:
            passed += 1
            total_checks += checks or 0
            print(f"PASS {name} ({checks} checks)")
    print(f"{passed}/{len(tests)} tests passed, {total_checks} instance checks")

    import json
    verdict = {
        "verified": passed == len(tests),
        "tests_run": total_checks,
        "tests_passed": total_checks if passed == len(tests) else 0,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh, indent=2)
        fh.write("\n")
    print("wrote verdict.json:", verdict)
    return passed, len(tests)


if __name__ == "__main__":
    main()
