"""Independent verification of reduce.py (Clique -> Independent Set).

We write our own brute-force solvers for both problems directly from the
definitions in problems.py, generate many small source instances (including
all the documented edge cases), reduce each one, and compare the brute-force
answer of the source instance with the brute-force answer of the reduced
target instance.
"""

from __future__ import annotations

import itertools
import random
from typing import Dict, List

from problems import Clique, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.
# ----------------------------------------------------------------------

def _has_clique(n: int, edges: List[List[int]], k: int) -> bool:
    """Yes iff graph has a clique of at least k vertices."""
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


def _has_independent_set(n: int, edges: List[List[int]], k: int) -> bool:
    """Yes iff graph has an independent set of at least k vertices."""
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


def solve_clique(instance: Dict) -> bool:
    return _has_clique(instance["n"], instance["edges"], instance["k"])


def solve_independent_set(instance: Dict) -> bool:
    return _has_independent_set(instance["n"], instance["edges"], instance["k"])


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

tests_run = 0
tests_passed = 0
failures: List[str] = []


def check(condition: bool, message: str) -> None:
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
    else:
        failures.append(message)


def all_edges(n: int) -> List[List[int]]:
    return [[u, v] for u in range(n) for v in range(u + 1, n)]


def random_instance(rng: random.Random, max_n: int = 7) -> Dict:
    n = rng.randint(0, max_n)
    possible = all_edges(n)
    edges = [e for e in possible if rng.random() < 0.5]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def run_case(instance: Dict, label: str) -> None:
    # Source must be a valid instance.
    Clique.validate(instance)
    source_answer = solve_clique(instance)

    reduced = reduce(instance)

    # The reduction must return a valid target instance.
    try:
        IndependentSet.validate(reduced)
        valid = True
        err = ""
    except Exception as exc:  # noqa: BLE001
        valid = False
        err = repr(exc)
    check(valid, f"{label}: reduced instance invalid: {err}")
    if not valid:
        return

    target_answer = solve_independent_set(reduced)
    check(
        source_answer == target_answer,
        f"{label}: source={source_answer} target={target_answer} "
        f"instance={instance} reduced={reduced}",
    )


def main() -> None:
    rng = random.Random(12345)

    # 1. Exhaustive over all graphs for small n and a range of k.
    for n in range(0, 6):
        possible = all_edges(n)
        for mask in range(1 << len(possible)):
            edges = [possible[i] for i in range(len(possible)) if (mask >> i) & 1]
            for k in range(-2, n + 3):
                run_case({"n": n, "edges": edges, "k": k}, f"exhaustive n={n} mask={mask} k={k}")

    # 2. Documented edge cases explicitly.
    edge_cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 0, "edges": [], "k": -5},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 1, "edges": [], "k": -1},
        {"n": 5, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 6},
        {"n": 5, "edges": all_edges(5), "k": 5},
        {"n": 5, "edges": all_edges(5), "k": 6},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 3},
    ]
    for i, inst in enumerate(edge_cases):
        run_case(inst, f"edge-case {i}")

    # 3. Random instances (larger n).
    for i in range(4000):
        inst = random_instance(rng, max_n=8)
        run_case(inst, f"random {i}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures[:20]:
            print("  " + f)
        raise SystemExit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
