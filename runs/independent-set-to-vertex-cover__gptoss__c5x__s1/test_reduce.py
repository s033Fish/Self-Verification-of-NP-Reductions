"""Independent verification of reduce.py: IndependentSet -> VertexCover.

We compare brute-force answers on many small source instances against
brute-force answers on their reductions.
"""
from itertools import combinations

from problems import IndependentSet, VertexCover
from reduce import reduce
from solvers import solve_independent_set, solve_vertex_cover

tests_run = 0
tests_passed = 0
failures = []


def check(instance):
    global tests_run, tests_passed
    tests_run += 1
    IndependentSet.validate(instance)
    reduced = reduce(instance)
    VertexCover.validate(reduced)
    src = solve_independent_set(instance)
    tgt = solve_vertex_cover(reduced)
    ok = (src == tgt)
    if ok:
        tests_passed += 1
    else:
        failures.append((instance, reduced, src, tgt))
    return ok


def all_graphs(n):
    """All simple undirected graphs on n vertices (each edge present or not)."""
    possible = list(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if (mask >> i) & 1]
        yield edges


def main():
    # Exhaustive over all graphs for n = 0..5 and all k in -2..n+2
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # A few larger random-ish structured graphs (n=6,7) with all k
    import random
    random.seed(12345)
    for n in (6, 7):
        for _ in range(60):
            edges = []
            for u, v in combinations(range(n), 2):
                if random.random() < 0.4:
                    edges.append([u, v])
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Edge-case specific checks
    # no edges, large k
    check({"n": 5, "edges": [], "k": 5})
    check({"n": 5, "edges": [], "k": 6})
    check({"n": 5, "edges": [], "k": 0})
    check({"n": 5, "edges": [], "k": -3})
    # complete graph
    comp = [[u, v] for u, v in combinations(range(5), 2)]
    for k in range(-2, 8):
        check({"n": 5, "edges": comp, "k": k})
    # n = 0
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": 1})
    check({"n": 0, "edges": [], "k": -1})

    # Verify reduce does not mutate input and returns a new dict
    inst = {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}
    import copy
    snapshot = copy.deepcopy(inst)
    out = reduce(inst)
    assert inst == snapshot, "reduce mutated its input!"
    assert out is not inst, "reduce returned the same object!"

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:10]:
        print("FAIL:", f)
    assert not failures, "some reductions disagreed with brute force"


if __name__ == "__main__":
    main()
