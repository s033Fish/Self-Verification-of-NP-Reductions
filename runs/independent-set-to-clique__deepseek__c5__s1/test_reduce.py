"""Independent verification of reduce.py: Independent Set -> Clique.

We brute-force both problems from the definitions in problems.py and compare
answers on many small source instances and their reductions.
"""

from __future__ import annotations

import itertools

from problems import IndependentSet, Clique
from reduce import reduce


def _adjacency(instance):
    n = instance["n"]
    adj = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def brute_independent_set(instance):
    """Yes iff G has an independent set of size >= k."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = _adjacency(instance)
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(v not in adj[u] for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def brute_clique(instance):
    """Yes iff G has a clique of size >= k."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = _adjacency(instance)
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(v in adj[u] for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def all_graphs(n):
    """All simple graphs on n labelled vertices (as edge lists)."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask >> i & 1]
        yield edges


def main():
    tests_run = 0
    tests_passed = 0

    # 1) Exhaustive: all graphs for n = 0..4, all k in -2..n+2.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                src = {"n": n, "edges": [list(e) for e in edges], "k": k}
                IndependentSet.validate(src)
                tgt = reduce(src)
                Clique.validate(tgt)

                expected = brute_independent_set(src)
                reduced_answer = brute_clique(tgt)
                tests_run += 1
                if expected == reduced_answer:
                    tests_passed += 1
                else:
                    print("MISMATCH", src, "->", tgt, expected, reduced_answer)

    # 2) Random-ish larger graphs (n up to 8) with random edge subsets.
    import random
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 8)
        pairs = list(itertools.combinations(range(n), 2))
        edges = [list(p) for p in pairs if rng.random() < 0.5]
        k = rng.randint(-2, n + 2)
        src = {"n": n, "edges": edges, "k": k}
        IndependentSet.validate(src)
        tgt = reduce(src)
        Clique.validate(tgt)
        expected = brute_independent_set(src)
        reduced_answer = brute_clique(tgt)
        tests_run += 1
        if expected == reduced_answer:
            tests_passed += 1
        else:
            print("MISMATCH", src, "->", tgt, expected, reduced_answer)

    # 3) Explicit edge cases.
    cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 0, "edges": [], "k": -5},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 5, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 6},
        {"n": 5, "edges": [], "k": 0},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 3},
    ]
    for src in cases:
        IndependentSet.validate(src)
        tgt = reduce(src)
        Clique.validate(tgt)
        expected = brute_independent_set(src)
        reduced_answer = brute_clique(tgt)
        tests_run += 1
        if expected == reduced_answer:
            tests_passed += 1
        else:
            print("MISMATCH", src, "->", tgt, expected, reduced_answer)

    # 4) Structural checks: reduction must be complement graph, same n and k.
    for n in range(0, 6):
        for edges in all_graphs(n):
            src = {"n": n, "edges": [list(e) for e in edges], "k": 0}
            tgt = reduce(src)
            assert tgt["n"] == n
            assert tgt["k"] == 0
            src_set = {frozenset(e) for e in src["edges"]}
            tgt_set = {frozenset(e) for e in tgt["edges"]}
            all_pairs = {frozenset(p) for p in itertools.combinations(range(n), 2)}
            tests_run += 1
            if src_set.isdisjoint(tgt_set) and src_set | tgt_set == all_pairs:
                tests_passed += 1
            else:
                print("NOT COMPLEMENT", src, "->", tgt)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"

    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": tests_run == tests_passed,
                   "tests_run": tests_run,
                   "tests_passed": tests_passed}, f)
    print("verdict written")


if __name__ == "__main__":
    main()
