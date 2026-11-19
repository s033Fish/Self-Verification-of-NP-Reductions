"""Tests for the 3-Coloring -> Independent Set reduction.

problems.py provides no solvers, so we implement brute-force solvers for both
problems directly from the definitions, then compare answers on many small
source instances (plus edge cases) against the reduced target instances.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.


def solve_three_coloring(instance: dict) -> bool:
    """True iff the graph is 3-colourable (try all 3^n colourings)."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def max_independent_set(n: int, edges: list) -> int:
    """Size of a maximum independent set via branch and bound."""
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    best = 0

    def rec(candidates: int, size: int) -> None:
        nonlocal best
        if size + bin(candidates).count("1") <= best:
            return
        if candidates == 0:
            if size > best:
                best = size
            return
        # Branch on the candidate with the largest degree inside candidates.
        v = max(
            (i for i in range(n) if candidates >> i & 1),
            key=lambda i: bin(candidates & adj[i]).count("1"),
        )
        # Include v.
        rec(candidates & ~adj[v] & ~(1 << v), size + 1)
        # Exclude v.
        rec(candidates & ~(1 << v), size)

    rec((1 << n) - 1, 0)
    return best


def solve_independent_set(instance: dict) -> bool:
    """True iff there is an independent set of size >= k."""
    n = instance["n"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    return max_independent_set(n, instance["edges"]) >= k


# ----------------------------------------------------------------------
# Instance generation.

def random_three_coloring_instance(rng: random.Random, n: int) -> dict:
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(all_edges)
    m = rng.randint(0, len(all_edges))
    edges = [list(e) for e in all_edges[:m]]
    return {"n": n, "edges": edges}


def all_three_coloring_instances(n: int):
    """Every simple graph on n labelled vertices (small n only)."""
    all_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(all_edges)):
        edges = [list(e) for i, e in enumerate(all_edges) if mask >> i & 1]
        yield {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Test driver.

def main() -> None:
    tests_run = 0
    tests_passed = 0
    failures: list[str] = []

    def check(source_instance: dict, label: str) -> None:
        nonlocal tests_run, tests_passed
        tests_run += 1
        SOURCE.validate(source_instance)
        target_instance = reduce(source_instance)
        TARGET.validate(target_instance)
        expected = solve_three_coloring(source_instance)
        got = solve_independent_set(target_instance)
        if expected == got:
            tests_passed += 1
        else:
            failures.append(
                f"{label}: source={source_instance} expected={expected} "
                f"reduced={target_instance} got={got}"
            )

    # Exhaustive over all graphs with up to 5 vertices.
    for n in range(0, 6):
        for inst in all_three_coloring_instances(n):
            check(inst, f"exhaustive n={n}")

    # Random larger instances.
    rng = random.Random(12345)
    for _ in range(300):
        n = rng.randint(0, 8)
        check(random_three_coloring_instance(rng, n), "random")

    # Explicit edge cases from the docstrings.
    check({"n": 0, "edges": []}, "n=0")
    check({"n": 1, "edges": []}, "n=1")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, "triangle")
    # K4 must be no.
    k4 = {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
    assert solve_three_coloring(k4) is False
    check(k4, "K4")
    # K4 minus an edge is 3-colourable.
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3]]}, "K4-e")
    # Disconnected / edgeless graphs.
    check({"n": 6, "edges": []}, "edgeless")
    check({"n": 5, "edges": [[0, 1], [2, 3]]}, "matching")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        for f in failures[:10]:
            print("FAIL:", f)
        raise SystemExit(1)

    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": tests_passed == tests_run, "tests_run": tests_run,
             "tests_passed": tests_passed},
            fh,
        )
    print("verdict.json written")


if __name__ == "__main__":
    main()
