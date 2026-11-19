"""Independent verification of reduce.py for Clique -> Vertex Cover.

We implement brute-force solvers directly from the problem definitions, then
compare SOURCE answers with TARGET answers on the reductions over many small
instances (including all edge cases).
"""

from __future__ import annotations

import itertools
import random

import problems
from problems import Clique, VertexCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions
# ----------------------------------------------------------------------

def clique_yes(instance: dict) -> bool:
    """Yes iff the graph has a clique of AT LEAST k vertices."""
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

    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(adj[u][v] for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def vertex_cover_yes(instance: dict) -> bool:
    """Yes iff the graph has a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if k >= n:
        return True
    if not edges:
        return k >= 0

    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------

def all_graphs(n: int):
    """Yield every simple graph on n vertices as a list of edges."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]


def make_instances():
    """Exhaustive small instances plus random larger ones."""
    instances = []
    # Exhaustive over all graphs for n = 0..4 and a range of k values.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                instances.append({"n": n, "edges": edges, "k": k})

    # Random instances with n = 5..7.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(5, 7)
        edges = []
        for u, v in itertools.combinations(range(n), 2):
            if rng.random() < 0.5:
                edges.append([u, v])
        k = rng.randint(-2, n + 2)
        instances.append({"n": n, "edges": edges, "k": k})
    return instances


def main() -> None:
    instances = make_instances()
    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in instances:
        # Both input and output must be valid instances.
        Clique.validate(inst)
        out = reduce(inst)
        VertexCover.validate(out)

        src = clique_yes(inst)
        tgt = vertex_cover_yes(out)
        tests_run += 1
        if src == tgt:
            tests_passed += 1
        else:
            failures.append((inst, out, src, tgt))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:10]:
            print("  input :", f[0])
            print("  output:", f[1])
            print("  clique_yes=", f[2], "vc_yes=", f[3])
    else:
        print("ALL PASSED")

    # Also confirm reduce is not calling any brute force: it only uses
    # polynomial loops.  (Static check: no itertools/combinations import.)
    src_text = open("reduce.py").read()
    assert "combinations" not in src_text, "reduce.py uses brute force"
    assert "itertools" not in src_text, "reduce.py uses brute force"


if __name__ == "__main__":
    main()
