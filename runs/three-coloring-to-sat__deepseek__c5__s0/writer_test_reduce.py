"""Tests: brute-force solvers vs. the 3-Coloring -> SAT reduction."""

from __future__ import annotations

from problems import ThreeColoring, Sat
from reduce import reduce
from solvers import solve_three_coloring, solve_sat

tests_run = 0
tests_passed = 0


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    ThreeColoring.validate(instance)
    reduced = reduce(instance)
    Sat.validate(reduced)
    expected = solve_three_coloring(instance)
    got = solve_sat(reduced)
    assert expected == got, (instance, reduced, expected, got)
    tests_passed += 1


def all_graphs(n):
    """All simple graphs on n labelled vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def main():
    # Edge cases from the docstring: n = 0 yes, <=3 vertices always yes.
    check({"n": 0, "edges": []})
    for n in range(0, 4):
        for g in all_graphs(n):
            check(g)

    # Exhaustive over all graphs on 4 and 5 vertices.
    for n in (4, 5):
        for g in all_graphs(n):
            check(g)

    # Structured larger graphs.
    check({"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})            # C4 yes
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})    # C5 yes
    check({"n": 6, "edges": [[i, j] for i in range(6) for j in range(i + 1, 6)]})  # K6 no
    check({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})     # K4+iso no
    check({"n": 7, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3],
                             [4, 5], [5, 6], [4, 6]]})                    # K4+tri no
    check({"n": 8, "edges": [[i, j] for i in range(4) for j in range(4, 8)]})      # K4,4 yes

    # Sample graphs on 6 vertices.
    pairs = [(u, v) for u in range(6) for v in range(u + 1, 6)]
    for mask in range(0, 1 << len(pairs), 37):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        check({"n": 6, "edges": edges})

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed


if __name__ == "__main__":
    main()
