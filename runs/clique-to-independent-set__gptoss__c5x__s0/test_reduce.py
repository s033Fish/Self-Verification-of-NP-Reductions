"""Independent verification of reduce.py (Clique -> IndependentSet).

We implement brute-force solvers for both problems directly from the
definitions in problems.py, then compare answers on many small source
instances and their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import Clique, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.
# ----------------------------------------------------------------------

def _has_clique(n, edges, k):
    """True iff graph has a clique of AT LEAST k vertices."""
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if not adj[a][b]:
                    ok = False
                    break
            if ok:
                return True
    return False


def _has_independent_set(n, edges, k):
    """True iff graph has an independent set of AT LEAST k vertices."""
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for a, b in itertools.combinations(subset, 2):
                if adj[a][b]:
                    ok = False
                    break
            if ok:
                return True
    return False


def solve_clique(instance):
    return _has_clique(instance["n"], instance["edges"], instance["k"])


def solve_independent_set(instance):
    return _has_independent_set(instance["n"], instance["edges"], instance["k"])


# ----------------------------------------------------------------------
# Instance generation helpers.
# ----------------------------------------------------------------------

def all_graphs(n):
    """Yield every simple graph on n vertices as a list of edges."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        yield [list(p) for i, p in enumerate(pairs) if mask & (1 << i)]


def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return edges


# ----------------------------------------------------------------------
# Tests.
# ----------------------------------------------------------------------

tests_run = 0
tests_passed = 0
failures = []


def check(instance, label=""):
    global tests_run, tests_passed
    tests_run += 1
    try:
        Clique.validate(instance)
    except Exception as exc:  # malformed generated instance: our bug
        failures.append(f"source invalid {label}: {exc}")
        return
    src = solve_clique(instance)
    target = reduce(instance)
    try:
        IndependentSet.validate(target)
    except Exception as exc:
        failures.append(f"target invalid {label}: {exc}")
        return
    tgt = solve_independent_set(target)
    if src == tgt:
        tests_passed += 1
    else:
        failures.append(
            f"mismatch {label}: src={src} tgt={tgt} instance={instance} "
            f"reduced={target}"
        )


def main():
    global tests_run, tests_passed
    # 1. Exhaustive: all graphs on 0..5 vertices, all k in a wide range.
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k},
                      f"exhaustive n={n} edges={edges} k={k}")

    # 2. Random larger graphs.
    rng = random.Random(12345)
    for trial in range(3000):
        n = rng.randint(0, 9)
        p = rng.random()
        edges = random_graph(n, p, rng)
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k}, f"random trial={trial}")

    # 3. Edge cases explicitly.
    check({"n": 0, "edges": [], "k": 0}, "empty k=0")
    check({"n": 0, "edges": [], "k": 1}, "empty k=1")
    check({"n": 0, "edges": [], "k": -5}, "empty k=-5")
    check({"n": 1, "edges": [], "k": 1}, "single k=1")
    check({"n": 5, "edges": [], "k": 5}, "no edges k=n")
    check({"n": 5, "edges": [], "k": 6}, "no edges k>n")
    complete = [[u, v] for u in range(5) for v in range(u + 1, 5)]
    check({"n": 5, "edges": complete, "k": 5}, "complete k=n")
    check({"n": 5, "edges": complete, "k": 6}, "complete k>n")

    # 4. Reduction must not mutate the input instance.
    inst = {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}
    import copy
    snapshot = copy.deepcopy(inst)
    reduce(inst)
    tests_run += 1
    if inst == snapshot:
        tests_passed += 1
    else:
        failures.append("reduce mutated its input")

    # 5. Reduction output shape checks.
    out = reduce({"n": 3, "edges": [[0, 1]], "k": 2})
    tests_run += 1
    if set(out) == {"n", "edges", "k"} and out["n"] == 3 and out["k"] == 2:
        tests_passed += 1
    else:
        failures.append(f"bad output shape: {out}")

    # 6. Malformed source should raise.
    tests_run += 1
    try:
        reduce({"n": 3, "edges": [[0, 1], [0, 1]], "k": 1})
        failures.append("duplicate edge not rejected")
    except Exception:
        tests_passed += 1

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures[:20]:
            print("  ", f)
    else:
        print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
