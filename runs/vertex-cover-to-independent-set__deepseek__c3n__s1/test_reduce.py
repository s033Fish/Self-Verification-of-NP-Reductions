"""Tests comparing brute-force answers of source and reduced instances."""

from __future__ import annotations

import itertools
import random

from reduce import reduce
from solvers import independent_set_yes, vertex_cover_yes
from problems import VertexCover, IndependentSet


def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask & (1 << i)]
        yield edges


def run_tests():
    tests_run = 0
    tests_passed = 0
    failures = []

    # Exhaustive over all graphs on n=0..4 and all k in -2..n+2.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                src = {"n": n, "edges": [list(e) for e in edges], "k": k}
                VertexCover.validate(src)
                tgt = reduce(src)
                IndependentSet.validate(tgt)
                a = vertex_cover_yes(src)
                b = independent_set_yes(tgt)
                tests_run += 1
                if a == b:
                    tests_passed += 1
                else:
                    failures.append((src, tgt, a, b))

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.4]
        k = rng.randint(-3, n + 3)
        src = {"n": n, "edges": edges, "k": k}
        VertexCover.validate(src)
        tgt = reduce(src)
        IndependentSet.validate(tgt)
        a = vertex_cover_yes(src)
        b = independent_set_yes(tgt)
        tests_run += 1
        if a == b:
            tests_passed += 1
        else:
            failures.append((src, tgt, a, b))

    for f in failures[:5]:
        print("FAIL", f)
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    tests_run, tests_passed, failures = run_tests()
    assert not failures, "some tests failed"
    print("ALL TESTS PASSED")
