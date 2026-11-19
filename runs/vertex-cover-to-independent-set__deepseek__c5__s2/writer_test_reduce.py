"""Tests for the Vertex Cover -> Independent Set reduction.

problems.py has no solvers, so we implement brute-force solvers from the
definitions and compare answers on many small instances.
"""

from __future__ import annotations

import itertools

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions in problems.py)

def vertex_cover_answer(instance) -> bool:
    """Yes iff there is a vertex cover of size AT MOST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    vertices = range(n)
    for size in range(0, k + 1):
        for subset in itertools.combinations(vertices, size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def independent_set_answer(instance) -> bool:
    """Yes iff there is an independent set of size AT LEAST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    vertices = range(n)
    for size in range(k, n + 1):
        for subset in itertools.combinations(vertices, size):
            chosen = set(subset)
            if all(not (u in chosen and v in chosen) for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def all_graphs(n):
    """All simple undirected graphs on n vertices, as edge lists."""
    possible = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield edges


def gen_instances():
    """Yield (instance, description) pairs covering many small cases."""
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                yield {"n": n, "edges": edges, "k": k}, (n, edges, k)


# ----------------------------------------------------------------------
# Tests

def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    # 1. Exhaustive comparison of answers on small instances.
    for instance, desc in gen_instances():
        SOURCE.validate(instance)
        reduced = reduce(instance)
        TARGET.validate(reduced)

        src = vertex_cover_answer(instance)
        tgt = independent_set_answer(reduced)

        tests_run += 1
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((desc, src, tgt, reduced))

    # 2. Structural checks: reduction must not mutate its input.
    sample = {"n": 4, "edges": [[0, 1], [1, 2]], "k": 1}
    snapshot = {"n": 4, "edges": [[0, 1], [1, 2]], "k": 1}
    out = reduce(sample)
    tests_run += 1
    if sample == snapshot and out == {"n": 4, "edges": [[0, 1], [1, 2]], "k": 3}:
        tests_passed += 1
    else:
        failures.append(("mutation/shape", sample, out, None))

    # 3. Returned edges are independent copies of the input edges.
    out["edges"][0][0] = 99
    tests_run += 1
    if sample["edges"][0][0] == 0:
        tests_passed += 1
    else:
        failures.append(("edge aliasing", sample, out, None))

    # 4. Polynomial / linear-size sanity: output size is O(input size).
    big_edges = [[i, i + 1] for i in range(999)]
    big = {"n": 1000, "edges": big_edges, "k": 500}
    SOURCE.validate(big)
    big_out = reduce(big)
    TARGET.validate(big_out)
    tests_run += 1
    if big_out["n"] == 1000 and big_out["k"] == 500 and big_out["edges"] == big_edges:
        tests_passed += 1
    else:
        failures.append(("big instance", None, big_out["k"], None))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES (first 10):")
        for f in failures[:10]:
            print("  ", f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
