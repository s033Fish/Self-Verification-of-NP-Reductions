"""Independent tests for reduce.py (Independent Set -> Clique).

We implement brute-force solvers for both problems directly from the
docstrings in problems.py, then compare, for many small source instances,
the source answer with the target answer on reduce(instance).

Run:  python3 test_reduce.py
"""

from __future__ import annotations

import itertools
import json
import random

from problems import IndependentSet, Clique
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)


def _has_edge(edge_set, u, v):
    return frozenset((u, v)) in edge_set


def independent_set_solver(instance) -> bool:
    """Yes iff G has an independent set of size >= k."""
    IndependentSet.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k <= 0:
        return True
    if k > n:
        return False

    edge_set = {frozenset(e) for e in edges}
    # brute force over all vertex subsets
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if _has_edge(edge_set, u, v):
                    ok = False
                    break
            if ok:
                return True
    return False


def clique_solver(instance) -> bool:
    """Yes iff G has a clique of size >= k."""
    Clique.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k <= 0:
        return True
    if k > n:
        return False

    edge_set = {frozenset(e) for e in edges}
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if not _has_edge(edge_set, u, v):
                    ok = False
                    break
            if ok:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation


def all_graphs(n):
    """All simple undirected graphs on n labelled vertices."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges, "k": 0}


def random_graph(n, p, rng):
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return edges


# ----------------------------------------------------------------------
# Tests


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        src = independent_set_solver(instance)
        reduced = reduce(instance)
        # reduced instance must be a valid Clique instance
        Clique.validate(reduced)
        tgt = clique_solver(reduced)
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((instance, reduced, src, tgt))

    # Exhaustive over all graphs for small n and a range of k values.
    for n in range(0, 6):
        ks = list(range(-2, n + 3))
        for base in all_graphs(n):
            for k in ks:
                inst = {"n": base["n"], "edges": [list(e) for e in base["edges"]], "k": k}
                check(inst)

    # Random larger instances (still brute-forceable: n <= 12).
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 12)
        p = rng.choice([0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
        edges = random_graph(n, p, rng)
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k})

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:5]:
        print("FAILURE:", f)

    verified = (len(failures) == 0)
    verdict = {
        "verified": verified,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
