"""Independent tests for reduce.py: Clique -> SAT.

We implement brute-force solvers for both problems directly from the
definitions in problems.py, generate many small Clique instances, reduce
them, and compare answers.  We also validate every produced SAT instance.
"""

from __future__ import annotations

import itertools
import random
import sys
import time

import problems
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)
# ----------------------------------------------------------------------

def clique_yes(instance: dict) -> bool:
    """True iff graph has a clique of AT LEAST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k <= 0:
        return True
    if k > n:
        return False
    # A clique of size >= k exists iff one of size exactly k exists
    # (any larger clique contains a k-subset, which is also a clique).
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    for subset in itertools.combinations(range(n), k):
        ok = True
        for a, b in itertools.combinations(subset, 2):
            if not adj[a][b]:
                ok = False
                break
        if ok:
            return True
    return False


def sat_yes(instance: dict) -> bool:
    """Brute force over all assignments of variables 1..num_vars."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Empty clause -> unsatisfiable immediately.
    for clause in clauses:
        if len(clause) == 0:
            return False
    # Represent each clause as (positive mask, negative mask) over bits 0..m-1.
    encoded = []
    for clause in clauses:
        pos = 0
        neg = 0
        for lit in clause:
            if lit > 0:
                pos |= 1 << (lit - 1)
            else:
                neg |= 1 << (-lit - 1)
        encoded.append((pos, neg))
    full = (1 << m) - 1
    for assignment in range(1 << m):
        good = True
        for pos, neg in encoded:
            # clause satisfied if some positive lit true or some negative lit false
            if not ((assignment & pos) or ((~assignment) & full & neg)):
                good = False
                break
        if good:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n: int):
    """All simple undirected graphs on n vertices (list of edge lists)."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if mask & (1 << i)]
        yield edges


def random_graph(n: int, rng: random.Random):
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < 0.5:
            edges.append([u, v])
    return edges


def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst: dict, label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        expected = clique_yes(inst)
        try:
            out = reduce_mod.reduce(inst)
        except Exception as exc:  # noqa: BLE001
            failures.append((label, inst, f"reduce raised {exc!r}"))
            return
        # The produced instance must be a valid SAT instance.
        try:
            problems.TARGET.validate(out)
        except Exception as exc:  # noqa: BLE001
            failures.append((label, inst, f"invalid SAT output {out!r}: {exc!r}"))
            return
        got = sat_yes(out)
        if got != expected:
            failures.append(
                (label, inst, f"expected {expected}, reduce gave {got}; sat={out!r}")
            )
            return
        tests_passed += 1

    # 1) Exhaustive: all graphs for n = 0..3, all k in a range around the
    #    interesting values (including k <= 0 and k > n).
    for n in range(0, 4):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                inst = {"n": n, "edges": edges, "k": k}
                problems.SOURCE.validate(inst)
                check(inst, f"exhaustive n={n} k={k} edges={edges}")

    # 2) Exhaustive over k for a few hand-picked graphs on n = 4, 5.
    special = [
        {"n": 4, "edges": [], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]], "k": 2},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2], [1, 3]], "k": 4},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 3},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2},
    ]
    for base in special:
        for k in range(-1, base["n"] + 3):
            inst = {"n": base["n"], "edges": base["edges"], "k": k}
            problems.SOURCE.validate(inst)
            check(inst, f"special n={base['n']} k={k}")

    # 3) Random small graphs, keeping num_vars = k*n small enough for the
    #    brute-force SAT solver (<= 16 variables).
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(0, 6)
        edges = random_graph(n, rng)
        k = rng.randint(-2, n + 2)
        if k > 0 and k * n > 16:
            continue
        inst = {"n": n, "edges": edges, "k": k}
        problems.SOURCE.validate(inst)
        check(inst, f"random n={n} k={k} edges={edges}")

    # 4) A couple of larger reductions: verify validity and that the answer
    #    agrees via a smarter (still exhaustive-ish) check where feasible.
    #    For n=6, k=2 -> 12 vars; n=7,k=2 -> 14 vars; n=8,k=2 -> 16 vars.
    for n, k in [(6, 2), (7, 2), (8, 2)]:
        edges = random_graph(n, rng)
        inst = {"n": n, "edges": edges, "k": k}
        problems.SOURCE.validate(inst)
        check(inst, f"larger n={n} k={k}")


    # 5) Exhaustive: ALL graphs on n = 4 vertices, all k in -1..n+2.
    for edges in all_graphs(4):
        for k in range(-1, 4 + 3):
            inst = {"n": 4, "edges": edges, "k": k}
            problems.SOURCE.validate(inst)
            check(inst, f"exhaustive4 k={k} edges={edges}")

    # 6) Performance / polynomial-time sanity: a moderately large instance
    #    must reduce quickly (no brute force over cliques).
    n_big, k_big = 40, 5
    big_edges = []
    for u in range(n_big):
        for v in range(u + 1, n_big):
            if (u * 7 + v * 3) % 5 == 0:
                big_edges.append([u, v])
    big = {"n": n_big, "edges": big_edges, "k": k_big}
    problems.SOURCE.validate(big)
    t0 = time.time()
    out_big = reduce_mod.reduce(big)
    dt = time.time() - t0
    problems.TARGET.validate(out_big)
    print(f"large reduction n={n_big} k={k_big}: {dt:.3f}s, "
          f"{len(out_big['clauses'])} clauses, {out_big['num_vars']} vars")
    if dt > 30:
        failures.append(("perf", big, f"reduction too slow: {dt:.1f}s"))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for label, inst, msg in failures[:20]:
            print(" -", label, "|", inst, "|", msg)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
