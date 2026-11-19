"""Independent verification of reduce.py (Vertex Cover -> Dominating Set).

We implement brute-force solvers directly from the problem definitions in
problems.py (which provides no solvers), then exhaustively/randomly compare
the source answer with the target answer on the reduced instance.
"""
from __future__ import annotations

import itertools
import json
import random

from problems import VertexCover, DominatingSet, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written from the definitions.
# ----------------------------------------------------------------------

def vertex_cover_answer(instance) -> bool:
    """Yes iff G has a vertex cover of size AT MOST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        # all vertices cover every edge (also handles n == 0)
        return True
    for r in range(0, min(k, n) + 1):
        for comb in itertools.combinations(range(n), r):
            chosen = set(comb)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def dominating_set_answer(instance) -> bool:
    """Yes iff G has a dominating set of size AT MOST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        # all vertices dominate everything (also handles n == 0)
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for r in range(0, min(k, n) + 1):
        for comb in itertools.combinations(range(n), r):
            dominated = set(comb)
            for x in comb:
                dominated |= adj[x]
            if len(dominated) == n:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def all_graphs(n: int):
    """Yield every simple undirected graph on n labelled vertices."""
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[b]) for b in range(len(pairs)) if (mask >> b) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n: int, rng: random.Random):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    edges = [list(p) for p in pairs if rng.random() < 0.5]
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Test driver
# ----------------------------------------------------------------------

def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance):
        nonlocal tests_run, tests_passed
        tests_run += 1
        src = vertex_cover_answer(instance)
        reduced = reduce(instance)
        # reduction must produce a valid target instance
        try:
            DominatingSet.validate(reduced)
            valid = True
        except InvalidInstance as exc:
            valid = False
            failures.append(("invalid reduced instance", instance, reduced, str(exc)))
        if valid:
            tgt = dominating_set_answer(reduced)
            if src == tgt:
                tests_passed += 1
            else:
                failures.append(("answer mismatch", instance, reduced, (src, tgt)))
        else:
            # count as failed (not passed)
            pass

    # Exhaustive over all graphs for n = 0..5, and all relevant k values.
    for n in range(0, 6):
        for graph in all_graphs(n):
            for k in range(-2, n + 3):
                inst = {"n": graph["n"], "edges": graph["edges"], "k": k}
                check(inst)

    # Random larger graphs (n = 6..8) with random k.
    rng = random.Random(12345)
    for _ in range(4000):
        n = rng.randint(6, 8)
        graph = random_graph(n, rng)
        k = rng.randint(-2, n + 2)
        inst = {"n": graph["n"], "edges": graph["edges"], "k": k}
        check(inst)

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:20]:
        print("FAILURE:", f)

    verified = (tests_passed == tests_run) and (tests_run > 0)
    verdict = {
        "verified": bool(verified),
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
