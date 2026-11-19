"""Test the Independent Set -> Vertex Cover reduction against brute force."""
import random
from itertools import combinations

from problems import IndependentSet, VertexCover
from reduce import reduce
from solvers import solve_independent_set, solve_vertex_cover

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance):
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    IndependentSet.validate(instance)
    reduced = reduce(instance)
    VertexCover.validate(reduced)
    expected = solve_independent_set(instance)
    got = solve_vertex_cover(reduced)
    assert expected == got, (instance, reduced, expected, got)
    TESTS_PASSED += 1


def all_graphs(n):
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield edges


def main():
    # Exhaustive over all small graphs and a range of k values.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": [list(e) for e in edges], "k": k})

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 9)
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if rng.random() < 0.4:
                    edges.append([u, v])
        k = rng.randint(-3, n + 3)
        check({"n": n, "edges": edges, "k": k})

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
