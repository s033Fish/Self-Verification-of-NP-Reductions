"""Tests for the Vertex Cover -> Dominating Set reduction.

Independent solvers are written directly from the definitions in problems.py:
  * brute-force solvers for tiny instances,
  * exact branch-and-bound solvers for slightly larger (sparse) instances.
Source answers are compared with the answers of their reductions.
"""

from __future__ import annotations

import itertools
import random

from problems import VertexCover, DominatingSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (tiny instances), straight from the definitions


def vertex_cover_answer_bruteforce(instance: dict) -> bool:
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k < 0:
        return False
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def dominating_set_answer_bruteforce(instance: dict) -> bool:
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k < 0:
        return False
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            dominated = set(chosen)
            for v in chosen:
                dominated |= adj[v]
            if len(dominated) == n:
                return True
    return False


# ----------------------------------------------------------------------
# Exact branch-and-bound solvers (medium, sparse instances)


def min_vertex_cover_size(instance: dict) -> int:
    n, edges = instance["n"], instance["edges"]
    best = [n]

    def rec(chosen, remaining_edges):
        if len(chosen) >= best[0]:
            return
        if not remaining_edges:
            best[0] = len(chosen)
            return
        u, v = remaining_edges[0]
        for pick in (u, v):
            rec(chosen | {pick},
                [e for e in remaining_edges if pick not in e])

    rec(frozenset(), [tuple(e) for e in edges])
    return best[0]


def min_dominating_set_size(instance: dict) -> int:
    n, edges = instance["n"], instance["edges"]
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    best = [n]

    def rec(chosen, dominated):
        if len(chosen) >= best[0]:
            return
        if len(dominated) == n:
            best[0] = len(chosen)
            return
        v = next(x for x in range(n) if x not in dominated)
        for c in [v] + sorted(adj[v]):
            rec(chosen | {c}, dominated | {c} | adj[c])

    rec(frozenset(), frozenset())
    return best[0]


def vertex_cover_answer(instance: dict) -> bool:
    if instance["k"] < 0:
        return False
    return min_vertex_cover_size(instance) <= instance["k"]


def dominating_set_answer(instance: dict) -> bool:
    if instance["k"] < 0:
        return False
    return min_dominating_set_size(instance) <= instance["k"]


# ----------------------------------------------------------------------
# Helpers


def random_graph(n, p, rng):
    return [[u, v] for u in range(n) for v in range(u + 1, n) if rng.random() < p]


def all_small_instances(max_n=5):
    for n in range(0, max_n + 1):
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(possible)):
            edges = [list(possible[i]) for i in range(len(possible)) if mask >> i & 1]
            for k in range(-1, n + 2):
                yield {"n": n, "edges": edges, "k": k}


def check(instance, solver):
    VertexCover.validate(instance)
    reduced = reduce(instance)
    DominatingSet.validate(reduced)
    expected = solver(instance)
    got = dominating_set_answer(reduced)
    assert expected == got, (
        f"MISMATCH\n  source={instance}\n  source_yes={expected}\n"
        f"  reduced={reduced}\n  reduced_yes={got}"
    )
    return reduced


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def run(label, instance, solver):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            check(instance, solver)
            tests_passed += 1
        except AssertionError as exc:
            failures.append(f"FAIL [{label}]: {exc}")

    # 1. Exhaustive tiny instances (all graphs up to 5 vertices), brute force.
    for instance in all_small_instances(max_n=5):
        run("exhaustive", instance, vertex_cover_answer_bruteforce)

    # 2. Random tiny instances, brute force on both sides.
    rng = random.Random(12345)
    for _ in range(3000):
        n = rng.randint(0, 6)
        p = rng.choice([0.0, 0.15, 0.3, 0.5, 0.8, 1.0])
        k = rng.randint(-2, n + 2)
        run("random-small", {"n": n, "edges": random_graph(n, p, rng), "k": k},
            vertex_cover_answer_bruteforce)

    # 3. Random sparse medium instances, exact branch-and-bound on both sides.
    for _ in range(2000):
        n = rng.randint(0, 11)
        possible = [[u, v] for u in range(n) for v in range(u + 1, n)]
        rng.shuffle(possible)
        m = rng.randint(0, min(len(possible), n))
        edges = possible[:m]
        k = rng.randint(-2, n + 2)
        run("random-medium", {"n": n, "edges": edges, "k": k}, vertex_cover_answer)

    # 4. Explicit edge cases.
    edge_cases = [
        ("k<0", {"n": 3, "edges": [[0, 1], [1, 2]], "k": -1}),
        ("no edges k=0", {"n": 4, "edges": [], "k": 0}),
        ("no edges n=0", {"n": 0, "edges": [], "k": 0}),
        ("isolated only k=n", {"n": 3, "edges": [], "k": 3}),
        ("isolated only k=n-1", {"n": 3, "edges": [], "k": 2}),
        ("mixed isolated k=1", {"n": 5, "edges": [[0, 1], [1, 2]], "k": 1}),
        ("mixed isolated k=0", {"n": 5, "edges": [[0, 1], [1, 2]], "k": 0}),
        ("k>=n", {"n": 4, "edges": [[0, 1], [2, 3]], "k": 4}),
        ("star k=1", {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 1}),
        ("triangle k=2", {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2}),
        ("triangle k=1", {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1}),
        ("path4 k=2", {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 2}),
        ("path4 k=1", {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 1}),
    ]
    for label, instance in edge_cases:
        run(label, instance, vertex_cover_answer)

    # 5. Reduction output shape checks.
    inst = {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1}
    red = reduce(inst)
    assert red["n"] == 4 + 2, red
    assert red["k"] == 1, red
    assert len(red["edges"]) == 2 + 2 * 2, red
    tests_run += 1
    tests_passed += 1

    # 6. Isolated-vertex accounting: k must be shifted by #isolated.
    inst = {"n": 5, "edges": [[0, 1]], "k": 1}
    red = reduce(inst)
    assert red["k"] == 1 + 3, red
    tests_run += 1
    tests_passed += 1

    for f in failures[:20]:
        print(f)
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert not failures, f"{len(failures)} tests failed"
    return tests_run, tests_passed


if __name__ == "__main__":
    main()
