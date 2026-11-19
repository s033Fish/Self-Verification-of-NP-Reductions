"""Independent verification of reduce.py (Independent Set -> Vertex Cover).

We implement brute-force solvers for both problems straight from the
docstrings in problems.py, then compare:

    solve_source(inst)  ==  solve_target(reduce(inst))

on many small instances (exhaustive over all graphs for n <= 5, plus
random graphs for larger n), over a wide range of k including all edge
cases (k <= 0, k > n, k < 0 for target, k >= n for target).
"""

import itertools
import random

from problems import IndependentSet, VertexCover
import reduce as reduce_module


# ----------------------------------------------------------------------
# Brute-force solvers, written directly from the problem definitions.

def solve_independent_set(instance):
    """Yes iff there is an independent set of size AT LEAST k."""
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

    best = 0
    for mask in range(1 << n):
        m = mask
        ok = True
        while m:
            i = (m & -m).bit_length() - 1
            m &= m - 1
            if adj[i] & mask:
                ok = False
                break
        if ok:
            size = bin(mask).count("1")
            if size > best:
                best = size
    return best >= k


def solve_vertex_cover(instance):
    """Yes iff there is a vertex cover of size AT MOST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if k >= n:
        return True

    for mask in range(1 << n):
        if bin(mask).count("1") > k:
            continue
        if all((mask >> u) & 1 or (mask >> v) & 1 for u, v in edges):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation.

def all_graphs(n):
    """All simple undirected graphs on n vertices (as edge lists)."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for r in range(len(pairs) + 1):
        for chosen in itertools.combinations(pairs, r):
            yield [list(e) for e in chosen]


def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        IndependentSet.validate(instance)
        expected = solve_independent_set(instance)
        reduced = reduce_module.reduce(instance)
        # The reduction must produce a valid target instance.
        VertexCover.validate(reduced)
        got = solve_vertex_cover(reduced)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, instance, expected, reduced, got))

    # Exhaustive: all graphs with n <= 5, all relevant k values.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                inst = {"n": n, "edges": [e[:] for e in edges], "k": k}
                check(inst, f"exhaustive n={n} k={k} edges={edges}")

    # Random larger graphs.
    rng = random.Random(12345)
    for trial in range(4000):
        n = rng.randint(0, 9)
        p = rng.choice([0.0, 0.1, 0.3, 0.5, 0.8, 1.0])
        edges = random_graph(n, p, rng)
        k = rng.randint(-3, n + 3)
        inst = {"n": n, "edges": edges, "k": k}
        check(inst, f"random trial={trial}")

    # Explicit edge-case checks.
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 0, "edges": [], "k": -5},
        {"n": 5, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 6},
        {"n": 5, "edges": [], "k": 0},
        {"n": 5, "edges": [], "k": -1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
    ]
    for inst in edge_cases:
        check(inst, f"edgecase {inst}")

    # Input must not be mutated by reduce.
    inst = {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}
    snapshot = {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}
    reduce_module.reduce(inst)
    tests_run += 1
    if inst == snapshot:
        tests_passed += 1
    else:
        failures.append(("mutation", inst, snapshot, None, None))

    # Invalid source instances should be rejected.
    bad = [
        {"n": 3, "edges": [[0, 1]], "k": 1, "extra": 1},
        {"n": 3, "edges": [[0, 0]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 0]], "k": 1},
        {"n": 3, "edges": [[0, 3]], "k": 1},
        {"n": -1, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": 1.5},
    ]
    for inst in bad:
        tests_run += 1
        try:
            reduce_module.reduce(inst)
        except Exception:
            tests_passed += 1
        else:
            failures.append(("invalid-not-rejected", inst, None, None, None))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:10]:
            print(f)
    else:
        print("ALL TESTS PASSED")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()
