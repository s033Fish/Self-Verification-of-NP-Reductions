"""Independent verification of reduce.py (3-Coloring -> Independent Set).

We write our own brute-force solvers directly from the problem
definitions in problems.py, then compare solver answers on many small
source instances with solver answers on their reductions.

Brute force is exponential, so the comparison tests use small graphs
(n <= 6).  Polynomial running time of reduce() itself is checked
separately on larger graphs.
"""

from __future__ import annotations

import itertools
import random
import time

from problems import ThreeColoring, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (independent of reduce.py)

def solve_three_coloring(instance: dict) -> bool:
    """True iff the graph is 3-colourable. Tries all 3^n colourings."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colouring[u] == colouring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_independent_set(instance: dict) -> bool:
    """True iff there is an independent set of size >= k. Tries all subsets."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            mask = 0
            for x in subset:
                mask |= 1 << x
            if all((adj[x] & mask) == 0 for x in subset):
                return True
    return False


# ----------------------------------------------------------------------
# Helpers

def make_instance(n, edges):
    return {"n": n, "edges": [list(e) for e in edges]}


def all_graphs(n):
    """All simple undirected graphs on n vertices."""
    possible = list(itertools.combinations(range(n), 2))
    for r in range(len(possible) + 1):
        for chosen in itertools.combinations(possible, r):
            yield make_instance(n, chosen)


def random_graph(n, rng, p=0.5):
    edges = [list(e) for e in itertools.combinations(range(n), 2) if rng.random() < p]
    return make_instance(n, edges)


def check_instance(inst, label):
    """Validate source, reduce, validate target, compare solver answers."""
    ThreeColoring.validate(inst)
    out = reduce(inst)
    IndependentSet.validate(out)
    src = solve_three_coloring(inst)
    tgt = solve_independent_set(out)
    assert src == tgt, (
        f"MISMATCH on {label}: source={inst} -> {src}, "
        f"reduced={out} -> {tgt}"
    )
    return src


# ----------------------------------------------------------------------
# Tests

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def run(inst, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            check_instance(inst, label)
            tests_passed += 1
        except AssertionError as exc:
            failures.append(str(exc))

    # 1. Exhaustive: every graph on 0..4 vertices.
    for n in range(0, 5):
        for inst in all_graphs(n):
            run(inst, f"exhaustive n={n}")

    # 2. Random graphs on 0..6 vertices.
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(0, 6)
        run(random_graph(n, rng, p=rng.choice([0.1, 0.3, 0.5, 0.7, 0.9])),
            f"random n={n}")

    # 3. Hand-picked edge cases.
    run(make_instance(0, []), "n=0")
    run(make_instance(1, []), "n=1")
    run(make_instance(3, [(0, 1), (1, 2), (0, 2)]), "K3")
    run(make_instance(4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]), "K4")
    run(make_instance(5, [(u, v) for u in range(5) for v in range(u + 1, 5)]), "K5")
    run(make_instance(6, [(i, i + 1) for i in range(5)]), "path P6")
    run(make_instance(6, [(i, (i + 1) % 6) for i in range(6)]), "cycle C6")
    run(make_instance(5, [(i, (i + 1) % 5) for i in range(5)]), "cycle C5 (odd)")
    run(make_instance(4, [(0, 1), (2, 3)]), "disjoint edges")
    run(make_instance(6, []), "empty graph n=6")

    # 4. Check the reduction output shape / k value directly.
    inst = make_instance(4, [(0, 1), (1, 2), (2, 3), (3, 0)])
    out = reduce(inst)
    assert out["n"] == 12, f"expected n=12, got {out['n']}"
    assert out["k"] == 4, f"expected k=4, got {out['k']}"
    assert len(out["edges"]) == 4 * 3 + 4 * 3, f"unexpected edge count {len(out['edges'])}"
    tests_run += 1
    tests_passed += 1

    # 5. Polynomial-time sanity: reduce() on large graphs must be fast.
    rng2 = random.Random(7)
    t0 = time.time()
    for _ in range(20):
        inst = random_graph(200, rng2, p=0.1)
        out = reduce(inst)
        IndependentSet.validate(out)
        assert out["n"] == 600 and out["k"] == 200
    elapsed = time.time() - t0
    tests_run += 1
    if elapsed < 10.0:
        tests_passed += 1
    else:
        failures.append(f"reduce too slow: {elapsed:.2f}s for 20 graphs of n=200")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:20]:
            print(" ", f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
