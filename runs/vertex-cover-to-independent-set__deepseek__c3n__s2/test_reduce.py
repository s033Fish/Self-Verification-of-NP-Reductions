"""Tests for reduce.py: compare brute-force answers on small instances."""

import itertools
import random

from reduce import reduce


def brute_vertex_cover(instance):
    """True iff graph has a vertex cover of size AT MOST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            covered = set(subset)
            if all(u in covered or v in covered for u, v in edges):
                return True
    return False


def brute_independent_set(instance):
    """True iff graph has an independent set of size AT LEAST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(not (u in chosen and v in chosen) for u, v in edges):
                return True
    return False


def all_small_graphs(n):
    """All simple graphs on n labelled vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield edges


def run_tests():
    tests_run = 0
    tests_passed = 0

    # Exhaustive over all graphs with n <= 4 and all k in a wide range.
    for n in range(0, 5):
        for edges in all_small_graphs(n):
            for k in range(-2, n + 3):
                src = {"n": n, "edges": [list(e) for e in edges], "k": k}
                tgt = reduce(src)
                # target instance must be well formed
                assert set(tgt) == {"n", "edges", "k"}
                assert tgt["n"] == n
                assert tgt["k"] == n - k
                assert sorted(map(tuple, tgt["edges"])) == sorted(
                    map(tuple, src["edges"])
                )
                expected = brute_vertex_cover(src)
                got = brute_independent_set(tgt)
                tests_run += 1
                if expected == got:
                    tests_passed += 1
                else:
                    raise AssertionError(
                        f"MISMATCH src={src} tgt={tgt} "
                        f"vc={expected} is={got}"
                    )

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 8)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        rng.shuffle(pairs)
        m = rng.randint(0, len(pairs))
        edges = [list(p) for p in pairs[:m]]
        k = rng.randint(-3, n + 3)
        src = {"n": n, "edges": edges, "k": k}
        tgt = reduce(src)
        expected = brute_vertex_cover(src)
        got = brute_independent_set(tgt)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            raise AssertionError(
                f"MISMATCH src={src} tgt={tgt} vc={expected} is={got}"
            )

    return tests_run, tests_passed


if __name__ == "__main__":
    run, passed = run_tests()
    print(f"tests_run={run} tests_passed={passed}")
    assert run == passed
