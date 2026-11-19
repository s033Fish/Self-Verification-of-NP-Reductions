"""Independent checks of reduce.py: 3-Coloring -> Independent Set.

We implement our own brute-force solvers directly from the problem
definitions in problems.py, then compare the answer of every small source
instance with the answer of its reduction.
"""

import itertools
import json
import random
from functools import lru_cache

from problems import ThreeColoring, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the docstrings, no solvers exist in problems.py)

def three_coloring_solver(instance):
    """Return True iff the graph is 3-colourable (brute force over 3^n)."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def independent_set_solver(instance):
    """Return True iff there is an independent set of size >= k.

    Uses an exact branch-and-bound maximum independent set (bitmask), so it
    is still a brute-force/exact solver but fast enough for the tests.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u

    @lru_cache(maxsize=None)
    def mis(mask):
        if mask == 0:
            return 0
        v = (mask & -mask).bit_length() - 1
        without_v = mask & ~(1 << v)
        with_v = 1 + mis(without_v & ~adj[v])
        return max(with_v, mis(without_v))

    return mis((1 << n) - 1) >= k


# ----------------------------------------------------------------------
# Instance generation

def all_graphs(n):
    """All simple graphs on n labelled vertices."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, rng, p=0.5):
    pairs = list(itertools.combinations(range(n), 2))
    edges = [list(pair) for pair in pairs if rng.random() < p]
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(source_instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        ThreeColoring.validate(source_instance)
        expected = three_coloring_solver(source_instance)
        target_instance = reduce(source_instance)
        IndependentSet.validate(target_instance)
        got = independent_set_solver(target_instance)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((label, source_instance, target_instance,
                             expected, got))

    # Exhaustive: every graph on 0..4 vertices (all 3-colourable).
    for n in range(0, 5):
        for g in all_graphs(n):
            check(g, f"exhaustive n={n}")

    # Exhaustive on 5 vertices: all 2^10 = 1024 graphs.
    for g in all_graphs(5):
        check(g, "exhaustive n=5")

    # Random larger graphs (mix of densities, includes non-3-colourable).
    rng = random.Random(12345)
    for n in range(6, 11):
        for _ in range(150):
            g = random_graph(n, rng, p=rng.choice([0.2, 0.5, 0.8]))
            check(g, f"random n={n}")

    # Explicit edge cases from the definitions.
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]},  # K4
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]},  # C5
        {"n": 6, "edges": [[i, j] for i in range(6) for j in range(i + 1, 6)]},  # K6
        {"n": 7, "edges": [[i, j] for i in range(7) for j in range(i + 1, 7)]},  # K7
    ]
    for g in edge_cases:
        check(g, "edge case")

    # Sanity: solvers agree with the documented edge cases.
    assert three_coloring_solver({"n": 0, "edges": []}) is True
    assert three_coloring_solver(
        {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
    ) is False
    assert independent_set_solver({"n": 3, "edges": [], "k": 0}) is True
    assert independent_set_solver({"n": 3, "edges": [], "k": 4}) is False
    assert independent_set_solver({"n": 3, "edges": [], "k": 3}) is True

    # reduce() must reject malformed source instances.
    bad_instances = [
        {"n": 3, "edges": [[0, 0]]},
        {"n": 2, "edges": [[0, 1], [1, 0]]},
        {"n": 2, "edges": [[0, 5]]},
        {"n": -1, "edges": []},
        {"n": 2},
    ]
    for bad in bad_instances:
        tests_run += 1
        try:
            reduce(bad)
        except Exception:
            tests_passed += 1
        else:
            failures.append(("should reject", bad, None, None, None))

    verdict = {
        "verified": len(failures) == 0,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)

    print("tests_run =", tests_run)
    print("tests_passed =", tests_passed)
    print("failures =", len(failures))
    for failure in failures[:10]:
        print("FAILURE:", failure)
    print(json.dumps(verdict))


if __name__ == "__main__":
    main()
