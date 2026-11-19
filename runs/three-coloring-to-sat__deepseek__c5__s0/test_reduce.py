"""Independent tests for reduce.py (3-Coloring -> SAT).

We implement our own brute-force solvers from the problem definitions and
compare their answers on many small source instances against the answers of
the reduced SAT instances.
"""

from __future__ import annotations

import itertools
import random

from problems import ThreeColoring, Sat
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions (no brute force in reduce)
# ----------------------------------------------------------------------

def solve_three_coloring(instance: dict) -> bool:
    """Yes iff a proper 3-colouring exists. Try all 3^n colourings."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def solve_sat(instance: dict) -> bool:
    """Yes iff some assignment satisfies every clause. Try all 2^m."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=num_vars):
        satisfied = True
        for clause in clauses:
            clause_ok = False
            for literal in clause:
                value = bits[abs(literal) - 1]
                if literal < 0:
                    value = not value
                if value:
                    clause_ok = True
                    break
            if not clause_ok:
                satisfied = False
                break
        if satisfied:
            return True
    return False


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance: dict, label: str = "") -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    # The source instance must be valid.
    ThreeColoring.validate(instance)
    reduced = reduce(instance)
    # The reduction must produce a valid SAT instance.
    Sat.validate(reduced)
    expected = solve_three_coloring(instance)
    got = solve_sat(reduced)
    if expected == got:
        TESTS_PASSED += 1
    else:
        print(f"FAIL {label}: instance={instance!r}")
        print(f"  source answer={expected}, reduced answer={got}")
        print(f"  reduced={reduced!r}")


def all_graphs(n: int):
    """All simple graphs on n labelled vertices."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def main() -> None:
    random.seed(12345)

    # 1. Exhaustive over all graphs on 0..4 vertices (all 1+1+2+8+64 graphs).
    for n in range(0, 5):
        for graph in all_graphs(n):
            check(graph, f"exhaustive n={n}")

    # 2. Random graphs on 5..6 vertices (SAT brute force is 2^(3n)).
    for _ in range(300):
        n = random.randint(5, 6)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in possible if random.random() < 0.5]
        check({"n": n, "edges": edges}, "random")

    # 3. Specific edge cases from the definitions.
    check({"n": 0, "edges": []}, "n=0")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, "K3")
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, "K4")
    check({"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]}, "C5")
    check({"n": 6, "edges": [[0, 1], [2, 3], [4, 5]]}, "disjoint edges")

    # 4. Known no-instances (odd cycles, K4 subgraphs).
    check({"n": 7, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 0]]}, "C7")
    check({"n": 6, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, "K4 + isolated")

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED, "some tests failed"


if __name__ == "__main__":
    main()
