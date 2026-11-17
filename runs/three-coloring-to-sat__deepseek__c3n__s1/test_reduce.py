"""Tests for the 3-Coloring -> SAT reduction.

Contains independent brute-force solvers for both problems (written from the
definitions in problems.py, which provides no solvers) and compares their
answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import Sat, ThreeColoring
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (independent of reduce.py)

def solve_three_coloring(instance: dict) -> bool:
    """Try every assignment of 3 colours to the n vertices."""
    n = instance["n"]
    edges = instance["edges"]
    for colours in itertools.product(range(3), repeat=n):
        if all(colours[u] != colours[v] for u, v in edges):
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """Try every truth assignment to variables 1..num_vars."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        # bits[i] is the value of variable i+1
        ok = True
        for clause in clauses:
            if not any(
                bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1]
                for lit in clause
            ):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Test harness

_tests_run = 0
_tests_passed = 0


def check(name: str, condition: bool) -> None:
    global _tests_run, _tests_passed
    _tests_run += 1
    if condition:
        _tests_passed += 1
    else:
        print(f"FAIL: {name}")


def all_graphs(n: int):
    """All simple undirected graphs on vertices 0..n-1."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def run_case(instance: dict, label: str) -> None:
    # The source instance must be valid.
    ThreeColoring.validate(instance)
    reduced = reduce(instance)
    # The reduction must produce a valid target instance.
    Sat.validate(reduced)

    src = solve_three_coloring(instance)
    tgt = solve_sat(reduced)
    check(f"{label}: answers match (src={src}, tgt={tgt})", src == tgt)


# ----------------------------------------------------------------------
# Tests

def test_exhaustive_small_graphs() -> None:
    for n in range(0, 6):
        for instance in all_graphs(n):
            run_case(instance, f"exhaustive n={n} edges={instance['edges']}")


def test_edge_cases() -> None:
    # n = 0 is yes.
    run_case({"n": 0, "edges": []}, "n=0")
    # Any graph with at most 3 vertices is yes.
    for n in range(0, 4):
        for instance in all_graphs(n):
            run_case(instance, f"<=3 vertices n={n}")
    # K4 is no.
    k4 = {"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}
    run_case(k4, "K4")
    check("K4 is no", solve_three_coloring(k4) is False)
    # K3 is yes.
    k3 = {"n": 3, "edges": [[0, 1], [0, 2], [1, 2]]}
    run_case(k3, "K3")
    check("K3 is yes", solve_three_coloring(k3) is True)


def test_structured_graphs() -> None:
    # Odd cycle C5 is not 3-colourable? Actually C5 is 3-colourable (odd
    # cycles are 3-colourable, only 2-colouring fails). Use K4 plus extras.
    cases = [
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]},  # C5, yes
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]},           # C4, yes
        {"n": 6, "edges": [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 3],
                           [0, 3]]},                                    # yes
        {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [1, 3],
                           [1, 4], [2, 3], [2, 4], [3, 4]]},           # K5, no
        {"n": 7, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6],
                           [6, 0], [0, 3]]},                            # yes
    ]
    for i, instance in enumerate(cases):
        run_case(instance, f"structured {i}")


def test_random_graphs() -> None:
    rng = random.Random(12345)
    for trial in range(300):
        n = rng.randint(0, 7)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in possible if rng.random() < 0.4]
        instance = {"n": n, "edges": edges}
        run_case(instance, f"random trial={trial} n={n}")


def test_reduction_shape() -> None:
    # A graph with n vertices should use exactly 3n variables.
    instance = {"n": 4, "edges": [[0, 1], [2, 3]]}
    reduced = reduce(instance)
    check("num_vars == 3n", reduced["num_vars"] == 12)
    # n=0 gives an empty, satisfiable formula.
    empty = reduce({"n": 0, "edges": []})
    check("n=0 empty formula", empty == {"num_vars": 0, "clauses": []})
    check("n=0 formula satisfiable", solve_sat(empty) is True)


def main() -> None:
    test_exhaustive_small_graphs()
    test_edge_cases()
    test_structured_graphs()
    test_random_graphs()
    test_reduction_shape()

    print(f"tests_run={_tests_run} tests_passed={_tests_passed}")
    assert _tests_run == _tests_passed, "some tests failed"

    import json
    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": True, "tests_run": _tests_run, "tests_passed": _tests_passed},
            fh,
        )
    print("verdict.json written")


if __name__ == "__main__":
    main()
