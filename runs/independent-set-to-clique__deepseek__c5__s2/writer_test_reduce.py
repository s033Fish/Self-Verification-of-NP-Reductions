"""Tests for the Independent Set -> Clique reduction."""

from __future__ import annotations

from itertools import combinations

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import solve_independent_set, solve_clique


def all_graphs(n):
    """Yield every simple undirected graph on n vertices."""
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask & (1 << i)]
        yield edges


def test_exhaustive_small():
    tests_run = 0
    tests_passed = 0
    for n in range(0, 6):
        for edges in all_graphs(n):
            # k range covers negatives, zero, in-range, and k > n.
            for k in range(-2, n + 3):
                src = {"n": n, "edges": edges, "k": k}
                SOURCE.validate(src)
                out = reduce(src)
                TARGET.validate(out)
                expected = solve_independent_set(src)
                got = solve_clique(out)
                tests_run += 1
                if expected == got:
                    tests_passed += 1
                else:
                    raise AssertionError(
                        f"mismatch: src={src} expected={expected} "
                        f"reduced={out} got={got}"
                    )
    return tests_run, tests_passed


def test_orientation_invariance():
    tests_run = 0
    tests_passed = 0
    for n in range(0, 5):
        for edges in all_graphs(n):
            flipped = [[v, u] for u, v in edges]
            src = {"n": n, "edges": edges, "k": 2}
            out1 = reduce(src)
            out2 = reduce({"n": n, "edges": flipped, "k": 2})
            tests_run += 1
            if out1 == out2:
                tests_passed += 1
            else:
                raise AssertionError(f"orientation dependence: {out1} vs {out2}")
    return tests_run, tests_passed


def test_known_examples():
    tests_run = 0
    tests_passed = 0
    cases = [
        # n=4 path 0-1-2-3, independent set size 2 (e.g. {0,2}), no size 3.
        ({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 2}, True),
        ({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 3}, False),
        # Complete graph K4: max independent set size 1.
        ({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]], "k": 2}, False),
        ({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]], "k": 1}, True),
        # Empty graph: independent set of size n.
        ({"n": 3, "edges": [], "k": 3}, True),
        ({"n": 3, "edges": [], "k": 4}, False),
        # k <= 0 always yes.
        ({"n": 0, "edges": [], "k": 0}, True),
        ({"n": 0, "edges": [], "k": -5}, True),
    ]
    for src, expected in cases:
        SOURCE.validate(src)
        out = reduce(src)
        TARGET.validate(out)
        got = solve_clique(out)
        tests_run += 1
        if got == expected:
            tests_passed += 1
        else:
            raise AssertionError(f"known example failed: {src} -> {out}")
    return tests_run, tests_passed


if __name__ == "__main__":
    total_run = 0
    total_passed = 0
    for fn in (test_exhaustive_small, test_orientation_invariance, test_known_examples):
        run, passed = fn()
        print(f"{fn.__name__}: {passed}/{run} passed")
        total_run += run
        total_passed += passed
    print(f"TOTAL: {total_passed}/{total_run} passed")
    assert total_passed == total_run
