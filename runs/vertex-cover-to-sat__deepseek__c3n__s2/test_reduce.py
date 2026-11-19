"""Tests for the Vertex Cover -> SAT reduction."""

from __future__ import annotations

import random

from problems import Sat, VertexCover
from reduce import reduce
from solvers import solve_sat, solve_sat_bruteforce, solve_vertex_cover

TESTS_RUN = 0
TESTS_PASSED = 0


def check(instance: dict) -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    VertexCover.validate(instance)
    target = reduce(instance)
    Sat.validate(target)
    expected = solve_vertex_cover(instance)
    got = solve_sat(target)
    assert got == expected, (
        f"mismatch: source={instance} expected={expected} got={got} target={target}"
    )
    TESTS_PASSED += 1


def all_graphs(n: int):
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        yield [list(e) for i, e in enumerate(possible) if mask >> i & 1]


def test_sat_solver_agreement() -> None:
    """Validate the DPLL solver against exhaustive enumeration on small formulas."""
    global TESTS_RUN, TESTS_PASSED
    rng = random.Random(999)
    for _ in range(400):
        m = rng.randint(0, 6)
        clauses = []
        for _ in range(rng.randint(0, 5)):
            clause = []
            for _ in range(rng.randint(0, 4)):
                if m == 0:
                    break
                v = rng.randint(1, m)
                clause.append(v if rng.random() < 0.5 else -v)
            clauses.append(clause)
        inst = {"num_vars": m, "clauses": clauses}
        TESTS_RUN += 1
        assert solve_sat(inst) == solve_sat_bruteforce(inst), inst
        TESTS_PASSED += 1


def main() -> None:
    test_sat_solver_agreement()

    # Exhaustive: all graphs up to 4 vertices, all k in a wide range.
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                check({"n": n, "edges": edges, "k": k})

    # Random structured cases with more vertices.
    rng = random.Random(12345)
    for _ in range(500):
        n = rng.randint(0, 9)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in possible if rng.random() < 0.4]
        k = rng.randint(-2, n + 2)
        check({"n": n, "edges": edges, "k": k})

    # Explicit edge cases.
    check({"n": 0, "edges": [], "k": 0})
    check({"n": 0, "edges": [], "k": -1})
    check({"n": 5, "edges": [], "k": 0})
    check({"n": 5, "edges": [], "k": -1})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": 1})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": 2})
    check({"n": 3, "edges": [[0, 1], [1, 2]], "k": 3})

    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    assert TESTS_RUN == TESTS_PASSED


if __name__ == "__main__":
    main()
