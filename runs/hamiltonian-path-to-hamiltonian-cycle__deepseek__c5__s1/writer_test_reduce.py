"""Tests for reduce.py: brute-force solvers + exhaustive comparison."""

from __future__ import annotations

import itertools
import random

from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def ham_path_bruteforce(instance) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for perm in itertools.permutations(range(n)):
        if all(adj[perm[i]][perm[i + 1]] for i in range(n - 1)):
            return True
    return False


def ham_cycle_bruteforce(instance) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    # Fix vertex 0 as the start to avoid rotational duplicates.
    for perm in itertools.permutations(range(1, n)):
        cycle = (0,) + perm
        if all(adj[cycle[i]][cycle[(i + 1) % n]] for i in range(n)):
            return True
    return False


def all_graphs(n):
    """Yield every simple undirected graph on n vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def check(instance, counter):
    counter[0] += 1
    src = ham_path_bruteforce(instance)
    out = reduce(instance)
    # Validate target format minimally.
    assert set(out.keys()) == {"n", "edges"}, out
    assert isinstance(out["n"], int) and out["n"] >= 0
    seen = set()
    for e in out["edges"]:
        assert isinstance(e, list) and len(e) == 2
        u, v = e
        assert 0 <= u < out["n"] and 0 <= v < out["n"] and u != v
        key = frozenset((u, v))
        assert key not in seen, f"duplicate edge in reduction output: {e}"
        seen.add(key)
    tgt = ham_cycle_bruteforce(out)
    if src != tgt:
        counter[1] += 1
        print(f"MISMATCH: {instance} -> {out}: src={src} tgt={tgt}")
    return src == tgt


def main():
    counter = [0, 0]  # [tests_run, failures]

    # Exhaustive over all graphs for n = 0..5
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g, counter)

    # Exhaustive n = 6 (2^15 = 32768 graphs)
    for g in all_graphs(6):
        check(g, counter)

    # Random larger graphs, including structured ones.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 9)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(p) for p in pairs if rng.random() < rng.choice([0.2, 0.5, 0.8])]
        check({"n": n, "edges": edges}, counter)

    # A few specific edge cases.
    specific = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 2, "edges": [[0, 1]]},
        {"n": 3, "edges": []},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]},  # path yes
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},  # cycle yes
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]]},  # path yes
    ]
    for g in specific:
        check(g, counter)

    tests_run = counter[0]
    tests_passed = tests_run - counter[1]
    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={counter[1]}")
    assert counter[1] == 0, "there were mismatches"

    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run, "tests_passed": tests_passed}, f)
    print("verdict.json written")


if __name__ == "__main__":
    main()
