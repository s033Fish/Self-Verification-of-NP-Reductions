"""Independent tests for reduce.py: Clique -> SAT.

We implement brute-force solvers for both problems from the definitions in
problems.py, then compare the source answer with the answer to the reduced
instance on many small instances (exhaustive for tiny graphs, random for
slightly larger ones).

Run:  python3 test_reduce.py
Writes verdict.json.
"""

from __future__ import annotations

import itertools
import json
import random

import problems
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)

def brute_clique(instance: dict) -> bool:
    """Yes iff graph has a clique of AT LEAST k vertices."""
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

    # Enumerate subsets of size exactly k (a k-clique exists iff some k-subset
    # is a clique; a larger clique contains a k-subset).
    for subset in itertools.combinations(range(n), k):
        ok = True
        for a, b in itertools.combinations(subset, 2):
            if not adj[a][b]:
                ok = False
                break
        if ok:
            return True
    return False


def brute_sat(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]

    for bits in itertools.product((False, True), repeat=m):
        # bits[v-1] is the truth value of variable v.
        good = True
        for clause in clauses:
            sat = False
            for lit in clause:
                val = bits[abs(lit) - 1]
                if (lit > 0 and val) or (lit < 0 and not val):
                    sat = True
                    break
            if not sat:
                good = False
                break
        if good:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def all_graphs(n: int):
    """Yield every simple undirected graph on n vertices as an edge list."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield edges


def random_graph(n: int, p: float, rng: random.Random):
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < p:
            edges.append([u, v])
    return edges


# ----------------------------------------------------------------------
# Test driver

def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance: dict) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        problems.Clique.validate(instance)
        reduced = reduce_mod.reduce(instance)
        problems.Sat.validate(reduced)

        want = brute_clique(instance)
        got = brute_sat(reduced)
        if want == got:
            tests_passed += 1
        else:
            failures.append((instance, reduced, want, got))

    # 1) Exhaustive over all graphs for n = 0..4 and a range of k values.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                # keep brute-force SAT cheap
                if 1 <= k <= n and k * n > 20:
                    continue
                check({"n": n, "edges": edges, "k": k})

    # 2) Random graphs for n = 0..6, small k.
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 6)
        p = rng.choice([0.0, 0.15, 0.35, 0.6, 1.0])
        edges = random_graph(n, p, rng)
        k = rng.randint(-2, n + 2)
        if 1 <= k <= n and k * n > 18:
            continue
        check({"n": n, "edges": edges, "k": k})

    # 3) A few hand-picked structured cases.
    structured = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3},   # triangle
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 3},           # path, no triangle
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]], "k": 4},
        {"n": 5, "edges": [], "k": 1},
        {"n": 5, "edges": [], "k": 2},
    ]
    for inst in structured:
        check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for inst, reduced, want, got in failures[:5]:
        print("FAIL", inst, "want", want, "got", got)

    verified = (tests_run > 0 and tests_run == tests_passed)
    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )
    print("verdict:", {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed})
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
