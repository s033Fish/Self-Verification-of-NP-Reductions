"""Tests for the Hamiltonian Cycle -> SAT reduction in reduce.py."""

from __future__ import annotations

import itertools
import random

from problems import HamiltonianCycle, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written directly from the problem definitions.

def solve_hamiltonian(instance) -> bool:
    """True iff the graph has a Hamiltonian cycle."""
    n = instance["n"]
    if n <= 2:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u][v] = True
        adj[v][u] = True
    start = 0
    rest = list(range(1, n))
    for perm in itertools.permutations(rest):
        order = (start,) + perm
        ok = True
        for i in range(n):
            if not adj[order[i]][order[(i + 1) % n]]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance) -> bool:
    """True iff the CNF formula is satisfiable."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        # bits[v-1] is the value of variable v
        if all(any(bits[abs(lit) - 1] == (lit > 0) for lit in clause)
               for clause in clauses):
            return True
    return False


# ----------------------------------------------------------------------
# Test helpers

def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def check(instance, counter):
    HamiltonianCycle.validate(instance)
    out = reduce(instance)
    Sat.validate(out)
    src = solve_hamiltonian(instance)
    tgt = solve_sat(out)
    counter[0] += 1
    if src == tgt:
        counter[1] += 1
    else:
        print("MISMATCH", instance, "->", out, "src", src, "tgt", tgt)
    assert src == tgt, (instance, src, tgt)


def main():
    counter = [0, 0]  # [tests_run, tests_passed]

    # ---- exhaustive small graphs -------------------------------------
    # n = 0, 1, 2 (always no)
    for n in range(0, 3):
        check({"n": n, "edges": []}, counter)

    # n = 3: all 2^3 possible edge subsets
    pairs3 = [(0, 1), (0, 2), (1, 2)]
    for mask in range(1 << len(pairs3)):
        edges = [list(pairs3[i]) for i in range(len(pairs3)) if mask >> i & 1]
        check({"n": 3, "edges": edges}, counter)

    # n = 4: all 2^6 possible edge subsets
    pairs4 = [(u, v) for u in range(4) for v in range(u + 1, 4)]
    for mask in range(1 << len(pairs4)):
        edges = [list(pairs4[i]) for i in range(len(pairs4)) if mask >> i & 1]
        check({"n": 4, "edges": edges}, counter)

    # ---- random graphs -----------------------------------------------
    rng = random.Random(12345)
    for n in range(5, 8):
        for p in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
            for _ in range(30):
                check(random_graph(n, p, rng), counter)

    # a few larger random graphs
    for _ in range(20):
        check(random_graph(8, 0.5, rng), counter)
    for _ in range(10):
        check(random_graph(9, 0.6, rng), counter)

    # ---- known structured cases --------------------------------------
    # complete graph K5 -> yes
    check({"n": 5, "edges": [[u, v] for u in range(5) for v in range(u + 1, 5)]}, counter)
    # cycle C5 -> yes
    check({"n": 5, "edges": [[i, (i + 1) % 5] for i in range(5)]}, counter)
    # path P5 -> no
    check({"n": 5, "edges": [[i, i + 1] for i in range(4)]}, counter)
    # star K1,4 -> no
    check({"n": 5, "edges": [[0, i] for i in range(1, 5)]}, counter)
    # cycle C6 -> yes
    check({"n": 6, "edges": [[i, (i + 1) % 6] for i in range(6)]}, counter)
    # C6 plus a chord -> yes
    check({"n": 6, "edges": [[i, (i + 1) % 6] for i in range(6)] + [[0, 3]]}, counter)
    # two triangles sharing a vertex -> no
    check({"n": 5, "edges": [[0, 1], [1, 2], [0, 2], [0, 3], [3, 4], [0, 4]]}, counter)

    tests_run, tests_passed = counter
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed

    # write verdict.json
    import json
    with open("verdict.json", "w") as f:
        json.dump({"verified": True, "tests_run": tests_run,
                   "tests_passed": tests_passed}, f)
    print("verdict.json written")


if __name__ == "__main__":
    main()
