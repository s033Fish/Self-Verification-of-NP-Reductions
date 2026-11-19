"""Independent tests for reduce.py: Vertex Cover -> Clique.

We write brute-force solvers directly from the problem definitions in
problems.py, then compare source answers against reduced-target answers on
an exhaustive family of small instances plus randomized instances.
"""

import json
import random
from itertools import combinations

from problems import VertexCover, Clique, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (from the docstring definitions)
# ----------------------------------------------------------------------

def vertex_cover_yes(instance):
    """Yes iff there is a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True  # all vertices cover everything
    for size in range(0, k + 1):
        for subset in combinations(range(n), size):
            covered = set(subset)
            if all(u in covered or v in covered for u, v in edges):
                return True
    return False


def clique_yes(instance):
    """Yes iff there is a clique of AT LEAST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    best = 0
    for size in range(n, 0, -1):
        found = False
        for subset in combinations(range(n), size):
            ok = True
            for a, b in combinations(subset, 2):
                if not adj[a][b]:
                    ok = False
                    break
            if ok:
                found = True
                break
        if found:
            best = size
            break
    return best >= k


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n):
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def check(src, failures):
    VertexCover.validate(src)
    expected = vertex_cover_yes(src)
    tgt = reduce(src)
    Clique.validate(tgt)
    got = clique_yes(tgt)
    if got != expected:
        failures.append((src, tgt, expected, got))
    return got == expected


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    # Exhaustive: all graphs on 0..5 vertices, all k in [-2, n+2].
    for n in range(0, 6):
        for graph in all_graphs(n):
            for k in range(-2, n + 3):
                src = {"n": n, "edges": [list(e) for e in graph["edges"]], "k": k}
                tests_run += 1
                tests_passed += check(src, failures)

    # Randomized: graphs on 0..9 vertices.
    random.seed(12345)
    for _ in range(3000):
        n = random.randint(0, 9)
        pairs = list(combinations(range(n), 2))
        edges = [list(p) for p in pairs if random.random() < 0.5]
        k = random.randint(-2, n + 2)
        src = {"n": n, "edges": edges, "k": k}
        tests_run += 1
        tests_passed += check(src, failures)

    # Malformed source instances must be rejected.
    for bad in (
        {"n": 2, "edges": [[0, 1]], "k": 0, "extra": 1},
        {"n": 2, "edges": [[0, 1]], "k": 0.5},
        {"n": 2, "edges": [[0, 0]], "k": 0},
        {"n": 2, "edges": [[0, 1], [1, 0]], "k": 0},
    ):
        tests_run += 1
        try:
            reduce(bad)
        except InvalidInstance:
            tests_passed += 1
        else:
            failures.append((bad, None, "InvalidInstance", "no error"))

    # Solver sanity checks on known edge cases.
    assert vertex_cover_yes({"n": 0, "edges": [], "k": 0}) is True
    assert vertex_cover_yes({"n": 0, "edges": [], "k": -1}) is False
    assert vertex_cover_yes({"n": 3, "edges": [[0, 1], [1, 2]], "k": 1}) is True
    assert vertex_cover_yes({"n": 3, "edges": [[0, 1], [1, 2]], "k": 0}) is False
    assert clique_yes({"n": 3, "edges": [], "k": 1}) is True
    assert clique_yes({"n": 3, "edges": [], "k": 2}) is False
    assert clique_yes({"n": 3, "edges": [], "k": 0}) is True
    assert clique_yes({"n": 0, "edges": [], "k": 1}) is False

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for src, tgt, expected, got in failures[:20]:
            print(f"  src={src} -> tgt={tgt} expected={expected} got={got}")
    else:
        print("All tests passed.")

    verified = tests_run == tests_passed
    with open("verdict.json", "w") as f:
        json.dump(
            {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed},
            f,
        )
        f.write("\n")


if __name__ == "__main__":
    main()
