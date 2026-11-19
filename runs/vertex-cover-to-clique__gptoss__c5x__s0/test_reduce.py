"""Independent tests for reduce.py against brute-force solvers."""

import itertools

from problems import VertexCover, Clique
from solvers import vertex_cover_yes, clique_yes
from reduce import reduce


def all_graphs(n):
    """Yield every simple undirected graph on n vertices as an edge list."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield edges


def run_tests():
    tests_run = 0
    tests_passed = 0
    failures = []

    for n in range(0, 6):
        for edges in all_graphs(n):
            # k range: include negative, 0..n, and beyond n
            for k in range(-2, n + 3):
                inst = {"n": n, "edges": [list(e) for e in edges], "k": k}
                VertexCover.validate(inst)
                src = vertex_cover_yes(inst)
                out = reduce(inst)
                Clique.validate(out)
                tgt = clique_yes(out)
                tests_run += 1
                if src == tgt:
                    tests_passed += 1
                else:
                    failures.append((inst, out, src, tgt))

    # A few larger random-ish / structured instances.
    import random
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-3, n + 3)
        inst = {"n": n, "edges": edges, "k": k}
        VertexCover.validate(inst)
        src = vertex_cover_yes(inst)
        out = reduce(inst)
        Clique.validate(out)
        tgt = clique_yes(out)
        tests_run += 1
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, out, src, tgt))

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    tests_run, tests_passed, failures = run_tests()
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    for f in failures[:10]:
        print("FAIL", f)
    assert not failures, "reduction mismatch found"
    print("ALL TESTS PASSED")
