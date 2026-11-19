"""Tests for the Independent Set -> Vertex Cover reduction."""

from __future__ import annotations

from itertools import combinations

from problems import IndependentSet, VertexCover
from reduce import reduce
from solvers import independent_set_yes, vertex_cover_yes


def all_graphs(n):
    possible = list(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        yield [[u, v] for i, (u, v) in enumerate(possible) if mask >> i & 1]


def main():
    tests_run = 0
    tests_passed = 0
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                src = {"n": n, "edges": edges, "k": k}
                IndependentSet.validate(src)
                tgt = reduce(src)
                VertexCover.validate(tgt)
                a = independent_set_yes(src)
                b = vertex_cover_yes(tgt)
                tests_run += 1
                if a == b:
                    tests_passed += 1
                else:
                    print("MISMATCH", src, "->", tgt, "IS:", a, "VC:", b)
                    raise SystemExit(1)
    print(f"all {tests_run} tests passed")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()


def random_tests(seed=12345):
    import random
    rng = random.Random(seed)
    tests_run = tests_passed = 0
    for _ in range(300):
        n = rng.randint(0, 8)
        possible = list(combinations(range(n), 2))
        edges = [list(e) for e in possible if rng.random() < 0.4]
        k = rng.randint(-3, n + 3)
        src = {"n": n, "edges": edges, "k": k}
        IndependentSet.validate(src)
        tgt = reduce(src)
        VertexCover.validate(tgt)
        a = independent_set_yes(src)
        b = vertex_cover_yes(tgt)
        tests_run += 1
        if a == b:
            tests_passed += 1
        else:
            print("MISMATCH", src, "->", tgt, a, b)
            raise SystemExit(1)
    return tests_run, tests_passed
