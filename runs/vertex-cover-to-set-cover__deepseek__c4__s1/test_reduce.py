"""Compare brute-force answers on small Vertex Cover instances and their reductions."""

from __future__ import annotations

import itertools

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import solve_set_cover, solve_vertex_cover

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    SOURCE.validate(instance)
    reduced = reduce(instance)
    TARGET.validate(reduced)
    expected = solve_vertex_cover(instance)
    got = solve_set_cover(reduced)
    assert expected == got, (instance, reduced, expected, got)
    tests_passed += 1


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield edges


def main():
    # Exhaustive over all graphs on 0..4 vertices, k from -2 to n+2.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # A few larger random-ish structured cases (still small enough to brute force).
    extra = [
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 3},
        {"n": 6, "edges": [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5]], "k": 1},
        {"n": 6, "edges": [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5]], "k": 0},
        {"n": 4, "edges": [], "k": -1},
        {"n": 4, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 7, "edges": [[0, 1], [2, 3], [4, 5]], "k": 3},
        {"n": 7, "edges": [[0, 1], [2, 3], [4, 5]], "k": 2},
    ]
    for instance in extra:
        check(instance)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
