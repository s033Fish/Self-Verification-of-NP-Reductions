"""Tests comparing brute-force answers on Clique instances and their reductions."""

from itertools import combinations

from problems import Clique, Sat
from reduce import reduce
from solvers import clique_solve, sat_solve

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    Clique.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    # Keep brute force tractable.
    assert out["num_vars"] <= 100, out["num_vars"]
    expected = clique_solve(instance)
    got = sat_solve(out)
    assert expected == got, (instance, out, expected, got)
    tests_passed += 1


def all_graphs(n):
    """All simple undirected graphs on vertices 0..n-1."""
    possible = list(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(e) for idx, e in enumerate(possible) if (mask >> idx) & 1]
        yield edges


def main():
    # Exhaustive over all graphs with n = 0..4 and a wide range of k.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Random cases, keeping k*n small enough for the brute-force SAT solver.
    import random
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 7)
        edges = []
        for u, v in combinations(range(n), 2):
            if rng.random() < 0.4:
                edges.append([u, v])
        k = rng.randint(-1, n + 1)
        if k <= 0:
            k = rng.randint(-2, 0)
        elif k * n > 100:
            k = max(1, 100 // max(n, 1))
        check({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": 1})
    check({"n": 1, "edges": [], "k": 1})
    check({"n": 1, "edges": [], "k": 2})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": 3})
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3})
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2]], "k": 3})
    check({"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]], "k": 3})
    check({"n": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]], "k": 4})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
