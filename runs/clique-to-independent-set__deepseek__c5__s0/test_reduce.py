"""Independent tests for reduce.py (Clique -> Independent Set).

We write our own brute-force solvers from the definitions in problems.py and
compare answers on many small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written directly from the docstrings)
# ----------------------------------------------------------------------

def _adjacency(n, edges):
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    return adj


def _has_set_of_size_at_least(n, edges, k, want_clique):
    """True iff there is a subset of size >= k that is a clique (want_clique)
    or an independent set (not want_clique)."""
    if k <= 0:
        return True
    if k > n:
        return False
    adj = _adjacency(n, edges)
    # Search for any subset of size exactly k with the required property.
    # (If a larger one exists, some k-subset of it also works, so checking
    # size exactly k is sufficient for an "at least" condition.)
    for subset in itertools.combinations(range(n), k):
        ok = True
        for a, b in itertools.combinations(subset, 2):
            if want_clique and not adj[a][b]:
                ok = False
                break
            if not want_clique and adj[a][b]:
                ok = False
                break
        if ok:
            return True
    return False


def clique_solver(instance):
    return _has_set_of_size_at_least(
        instance["n"], instance["edges"], instance["k"], want_clique=True
    )


def independent_set_solver(instance):
    return _has_set_of_size_at_least(
        instance["n"], instance["edges"], instance["k"], want_clique=False
    )


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def random_instance(rng, max_n=7, allow_neg_k=True):
    n = rng.randint(0, max_n)
    all_pairs = list(itertools.combinations(range(n), 2))
    rng.shuffle(all_pairs)
    m = rng.randint(0, len(all_pairs))
    edges = [list(e) for e in all_pairs[:m]]
    rng.shuffle(edges)
    if allow_neg_k:
        k = rng.randint(-2, n + 2)
    else:
        k = rng.randint(0, n + 2)
    return {"n": n, "edges": edges, "k": k}


def exhaustive_instances(max_n=5):
    """All graphs on n <= max_n vertices (edge subsets) with a range of k."""
    for n in range(0, max_n + 1):
        all_pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(all_pairs)):
            edges = [list(all_pairs[i]) for i in range(len(all_pairs)) if mask >> i & 1]
            for k in range(-1, n + 2):
                yield {"n": n, "edges": edges, "k": k}


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def check_instance(instance, verbose=False):
    """Return True iff reduce preserves the answer and output is valid."""
    Clique.validate(instance)
    out = reduce(instance)
    IndependentSet.validate(out)
    expected = clique_solver(instance)
    got = independent_set_solver(out)
    if expected != got:
        if verbose:
            print("MISMATCH", instance, "->", out, "expected", expected, "got", got)
        return False
    return True


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    # 1. Exhaustive small instances.
    for instance in exhaustive_instances(max_n=5):
        tests_run += 1
        if check_instance(instance):
            tests_passed += 1
        else:
            failures.append(("exhaustive", instance))

    # 2. Random instances.
    rng = random.Random(12345)
    for _ in range(3000):
        instance = random_instance(rng, max_n=8)
        tests_run += 1
        if check_instance(instance):
            tests_passed += 1
        else:
            failures.append(("random", instance))

    # 3. Edge cases explicitly.
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 0, "edges": [], "k": -5},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 5, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 6},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 4},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 3},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 0},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": -3},
    ]
    for instance in edge_cases:
        tests_run += 1
        if check_instance(instance):
            tests_passed += 1
        else:
            failures.append(("edge", instance))

    # 4. Check the output is exactly the complement graph (structure check).
    rng = random.Random(999)
    for _ in range(500):
        instance = random_instance(rng, max_n=9)
        out = reduce(instance)
        tests_run += 1
        in_edges = {frozenset(e) for e in instance["edges"]}
        out_edges = {frozenset(e) for e in out["edges"]}
        expected = {
            frozenset((u, v))
            for u in range(instance["n"])
            for v in range(u + 1, instance["n"])
            if frozenset((u, v)) not in in_edges
        }
        ok = (
            out["n"] == instance["n"]
            and out["k"] == instance["k"]
            and out_edges == expected
            and len(out["edges"]) == len(expected)
        )
        if ok:
            tests_passed += 1
        else:
            failures.append(("structure", instance))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for kind, inst in failures[:10]:
            print(" ", kind, inst)
    assert not failures, f"{len(failures)} failures"

    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)
    print("verdict written")


if __name__ == "__main__":
    main()
