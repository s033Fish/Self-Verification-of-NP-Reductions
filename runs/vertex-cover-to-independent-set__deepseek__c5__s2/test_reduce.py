"""Independent verification of reduce.py (Vertex Cover -> Independent Set).

We write brute-force solvers for both problems directly from the docstrings
in problems.py, then compare solver answers on many small source instances
with the answers of the target instances produced by reduce.reduce.

Run:  python3 test_reduce.py
"""

from __future__ import annotations

import itertools
import random

import problems
import reduce as reduce_module

reduce = reduce_module.reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the definitions in problems.py)

def brute_force_vertex_cover(instance) -> bool:
    """Yes iff there is a vertex cover of size AT MOST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
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


def brute_force_independent_set(instance) -> bool:
    """Yes iff there is an independent set of size AT LEAST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    edge_set = {frozenset((u, v)) for u, v in edges}
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            s = set(subset)
            if all(frozenset((u, v)) not in edge_set
                   for u, v in itertools.combinations(subset, 2)):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def random_graph(n, max_edges=None, rng=None):
    rng = rng or random
    all_pairs = list(itertools.combinations(range(n), 2))
    rng.shuffle(all_pairs)
    if max_edges is None:
        max_edges = len(all_pairs)
    m = rng.randint(0, min(max_edges, len(all_pairs)))
    chosen = all_pairs[:m]
    # Randomize endpoint order, as the format allows [u, v] either way.
    edges = []
    for u, v in chosen:
        edges.append([u, v] if rng.random() < 0.5 else [v, u])
    return {"n": n, "edges": edges}


def all_graphs(n):
    """All labeled simple graphs on n vertices (as edge lists)."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield edges


# ----------------------------------------------------------------------
# Tests

TESTS_RUN = 0
TESTS_PASSED = 0


def check(condition, message):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    if condition:
        TESTS_PASSED += 1
    else:
        raise AssertionError("FAILED: " + message)


def check_reduction(source):
    """Validate source, reduce, validate target, compare answers."""
    problems.VertexCover.validate(source)
    target = reduce(source)
    problems.IndependentSet.validate(target)
    expected = brute_force_vertex_cover(source)
    got = brute_force_independent_set(target)
    check(
        expected == got,
        f"mismatch for {source} -> {target}: VC={expected}, IS={got}",
    )
    return expected, got


def main():
    # 1) Exhaustive: all graphs on n=0..4 vertices, all k in a wide range.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check_reduction({"n": n, "edges": edges, "k": k})
    print("exhaustive n<=4 done:", TESTS_RUN, "checks")

    # 2) Exhaustive over all graphs on n=5 (2^10 = 1024 graphs) and all k.
    for edges in all_graphs(5):
        for k in range(-2, 8):
            check_reduction({"n": 5, "edges": edges, "k": k})
    print("exhaustive n=5 done:", TESTS_RUN, "checks")

    # 3) Random larger instances, including sparse and dense graphs.
    rng = random.Random(12345)
    for trial in range(4000):
        n = rng.randint(0, 9)
        max_edges = rng.choice([0, 1, 2, 3, None])
        g = random_graph(n, max_edges=max_edges, rng=rng)
        k = rng.randint(-3, n + 3)
        check_reduction({"n": n, "edges": g["edges"], "k": k})
    print("random tests done:", TESTS_RUN, "checks")

    # 4) Explicit edge cases from the docstrings.
    cases = [
        ({"n": 0, "edges": [], "k": -1}, False),
        ({"n": 0, "edges": [], "k": 0}, True),
        ({"n": 0, "edges": [], "k": 5}, True),
        ({"n": 3, "edges": [], "k": 0}, True),
        ({"n": 3, "edges": [], "k": 2}, True),
        ({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1}, False),
        ({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2}, True),
        ({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1}, False),
        ({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}, True),
        ({"n": 5, "edges": [[0, 1]], "k": 0}, False),
        ({"n": 5, "edges": [[0, 1]], "k": 1}, True),
    ]
    for source, expected in cases:
        got, _ = check_reduction(source)
        check(got == expected, f"edge case {source}: expected {expected}, got {got}")
    print("edge cases done:", TESTS_RUN, "checks")

    # 5) Reduction output structure / independence from input mutation.
    src = {"n": 4, "edges": [[0, 1], [1, 2]], "k": 1}
    tgt = reduce(src)
    check(tgt == {"n": 4, "edges": [[0, 1], [1, 2]], "k": 3}, f"unexpected output {tgt}")
    tgt["edges"][0][0] = 99
    check(src["edges"][0][0] == 0, "reduce output must not share edge state with input")
    # reduce must not mutate the input
    src2 = {"n": 3, "edges": [[0, 1]], "k": 2}
    reduce(src2)
    check(src2 == {"n": 3, "edges": [[0, 1]], "k": 2}, "reduce mutated its input")

    # 6) Sanity: solvers agree with the documented simple edge-case rules
    #    on a sample of instances.
    for n in range(0, 6):
        for edges in all_graphs(n):
            inst = {"n": n, "edges": edges, "k": -1}
            check(brute_force_vertex_cover(inst) is False, "k<0 VC must be no")
            inst = {"n": n, "edges": edges, "k": n}
            check(brute_force_vertex_cover(inst) is True, "k>=n VC must be yes")
            inst = {"n": n, "edges": edges, "k": 0}
            check(brute_force_independent_set(inst) is True, "k<=0 IS must be yes")
            inst = {"n": n, "edges": edges, "k": n + 1}
            check(brute_force_independent_set(inst) is False, "k>n IS must be no")

    print(f"ALL TESTS PASSED: {TESTS_PASSED}/{TESTS_RUN}")
    return TESTS_RUN, TESTS_PASSED


if __name__ == "__main__":
    main()
